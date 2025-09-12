#!/usr/bin/env python3def main():

"""    print("Pricing engine running...")

Pricing engine for InsurityAI project.    print("✅ Pricing complete (placeholder).")



Converts model predictions into monthly premiums with risk-based adjustments,if __name__ == "__main__":

smoothing, and business constraints.    main()
"""

import argparse
import json
import logging
import os
import pickle
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import statsmodels.api as sm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
BASE_PREMIUM = 100.0
EWMA_LAMBDA = 0.6
MONTHLY_CAP_PCT = 0.10  # ±10%
QUARTERLY_CAP_PCT = 0.25  # ±25%


def load_models(models_dir: str) -> Tuple[object, object]:
    """Load trained GLM and LightGBM models."""
    glm_path = os.path.join(models_dir, "glm.pkl")
    lgb_path = os.path.join(models_dir, "lgbm.pkl")
    
    if not os.path.exists(glm_path):
        raise FileNotFoundError(f"GLM model not found: {glm_path}")
    if not os.path.exists(lgb_path):
        raise FileNotFoundError(f"LightGBM model not found: {lgb_path}")
    
    logger.info(f"Loading GLM model from {glm_path}")
    with open(glm_path, "rb") as f:
        glm_model = pickle.load(f)
    
    logger.info(f"Loading LightGBM model from {lgb_path}")
    with open(lgb_path, "rb") as f:
        lgb_model = pickle.load(f)
    
    return glm_model, lgb_model


def load_reason_codes(reason_codes_path: str) -> Dict[Tuple[str, str], List[str]]:
    """
    Load reason codes from JSONL file.
    
    Returns:
        Dictionary mapping (user_id, month) to list of reason strings
    """
    reason_codes = {}
    
    if not os.path.exists(reason_codes_path):
        logger.warning(f"Reason codes file not found: {reason_codes_path}")
        return reason_codes
    
    logger.info(f"Loading reason codes from {reason_codes_path}")
    
    with open(reason_codes_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            try:
                entry = json.loads(line.strip())
                user_id = entry['user_id']
                month = entry['month']
                
                # Extract reason strings from top_reasons
                reason_strings = []
                for reason in entry.get('top_reasons', []):
                    feature = reason['feature']
                    shap_value = reason['shap_value']
                    reason_strings.append(f"{feature} (+{shap_value:.3f})")
                
                reason_codes[(user_id, month)] = reason_strings
                
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Error parsing reason codes line {line_num}: {e}")
                continue
    
    logger.info(f"Loaded reason codes for {len(reason_codes)} user-months")
    return reason_codes


def generate_predictions(features_df: pd.DataFrame, glm_model: object, lgb_model: object) -> pd.DataFrame:
    """Generate predictions from both models."""
    
    # Identify feature columns (exclude IDs, time, and targets)
    exclude_cols = {'user_id', 'month', 'frequency', 'severity_mean', 'loss_cost'}
    feature_cols = [col for col in features_df.columns if col not in exclude_cols]
    
    logger.info(f"Generating predictions using {len(feature_cols)} features")
    
    X = features_df[feature_cols]
    
    # Handle missing values (same as training)
    X_clean = X.copy()
    for col in X.select_dtypes(include=[np.number]).columns:
        if X_clean[col].isnull().sum() > 0:
            median_val = X_clean[col].median()
            X_clean[col].fillna(median_val, inplace=True)
    
    # GLM predictions (need to add constant)
    X_const = sm.add_constant(X_clean)
    try:
        glm_pred = glm_model.predict(X_const)
    except Exception as e:
        logger.warning(f"GLM prediction failed: {e}. Using zeros.")
        glm_pred = np.zeros(len(X_clean))
    
    # LightGBM predictions
    try:
        lgb_pred = lgb_model.predict(X_clean)
    except Exception as e:
        logger.error(f"LightGBM prediction failed: {e}")
        raise
    
    # Create results dataframe
    results_df = features_df[['user_id', 'month']].copy()
    results_df['glm_predicted_loss'] = glm_pred
    results_df['lgb_predicted_loss'] = lgb_pred
    
    logger.info(f"Generated predictions for {len(results_df)} user-months")
    
    return results_df


def calculate_book_averages(predictions_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate book average loss cost by month."""
    
    # Use LightGBM as primary prediction
    book_avg_by_month = predictions_df.groupby('month')['lgb_predicted_loss'].mean().reset_index()
    book_avg_by_month.rename(columns={'lgb_predicted_loss': 'book_avg'}, inplace=True)
    
    # Merge back to main dataframe
    predictions_df = predictions_df.merge(book_avg_by_month, on='month', how='left')
    
    logger.info("Calculated book averages by month")
    
    return predictions_df


def apply_ewma_smoothing(pricing_df: pd.DataFrame) -> pd.DataFrame:
    """Apply EWMA smoothing to risk indices using prior months."""
    
    logger.info("Applying EWMA smoothing to risk indices...")
    
    # Sort by user and month for proper time series processing
    pricing_df = pricing_df.sort_values(['user_id', 'month']).copy()
    
    # Calculate base risk index
    pricing_df['risk_index'] = pricing_df['lgb_predicted_loss'] / pricing_df['book_avg']
    
    # Initialize EWMA index as risk index
    pricing_df['ewma_index'] = pricing_df['risk_index'].copy()
    
    # Apply EWMA smoothing within each user
    for user_id in pricing_df['user_id'].unique():
        user_mask = pricing_df['user_id'] == user_id
        user_data = pricing_df.loc[user_mask].copy()
        
        if len(user_data) > 1:
            # Apply EWMA: new_value = lambda * current + (1-lambda) * previous
            ewma_values = [user_data.iloc[0]['risk_index']]  # First value unchanged
            
            for i in range(1, len(user_data)):
                current_risk = user_data.iloc[i]['risk_index']
                previous_ewma = ewma_values[i-1]
                
                ewma_value = EWMA_LAMBDA * current_risk + (1 - EWMA_LAMBDA) * previous_ewma
                ewma_values.append(ewma_value)
            
            # Update the main dataframe
            pricing_df.loc[user_mask, 'ewma_index'] = ewma_values
    
    logger.info("EWMA smoothing applied")
    
    return pricing_df


def apply_telematics_caps_and_grace(pricing_df: pd.DataFrame) -> pd.DataFrame:
    """Apply monthly and quarterly caps, plus grace period logic."""
    
    logger.info("Applying telematics caps and grace period...")
    
    pricing_df = pricing_df.sort_values(['user_id', 'month']).copy()
    
    # Initialize factor columns
    pricing_df['telematics_factor_uncapped'] = pricing_df['ewma_index'].copy()
    pricing_df['telematics_factor_capped'] = pricing_df['ewma_index'].copy()
    pricing_df['is_first_month'] = False
    pricing_df['monthly_capped'] = False
    pricing_df['quarterly_capped'] = False
    
    # Create a synthetic month index for quarterly capping
    # Convert month strings to numeric for proper ordering
    pricing_df['month_dt'] = pd.to_datetime(pricing_df['month'])
    pricing_df['month_index'] = pricing_df['month_dt'].rank(method='dense').astype(int)
    
    for user_id in pricing_df['user_id'].unique():
        user_mask = pricing_df['user_id'] == user_id
        user_data = pricing_df.loc[user_mask].copy()
        
        if len(user_data) == 0:
            continue
            
        # Sort by month to ensure proper time ordering
        user_data = user_data.sort_values('month')
        user_indices = user_data.index
        
        # Grace period: first month gets factor = 1.0
        pricing_df.loc[user_indices[0], 'is_first_month'] = True
        pricing_df.loc[user_indices[0], 'telematics_factor_capped'] = 1.0
        
        # Apply caps for subsequent months
        for i in range(1, len(user_indices)):
            current_idx = user_indices[i]
            previous_idx = user_indices[i-1]
            
            current_factor = pricing_df.loc[current_idx, 'ewma_index']
            previous_factor = pricing_df.loc[previous_idx, 'telematics_factor_capped']
            
            # Monthly cap: ±10% change
            max_monthly_factor = previous_factor * (1 + MONTHLY_CAP_PCT)
            min_monthly_factor = previous_factor * (1 - MONTHLY_CAP_PCT)
            
            monthly_capped_factor = np.clip(current_factor, min_monthly_factor, max_monthly_factor)
            
            # Check if monthly capping was applied
            if abs(monthly_capped_factor - current_factor) > 1e-6:
                pricing_df.loc[current_idx, 'monthly_capped'] = True
            
            # Quarterly cap: ±25% from 3 months ago (if available)
            quarterly_capped_factor = monthly_capped_factor
            if i >= 3:  # Have at least 3 previous months
                three_months_ago_idx = user_indices[i-3]
                three_months_ago_factor = pricing_df.loc[three_months_ago_idx, 'telematics_factor_capped']
                
                max_quarterly_factor = three_months_ago_factor * (1 + QUARTERLY_CAP_PCT)
                min_quarterly_factor = three_months_ago_factor * (1 - QUARTERLY_CAP_PCT)
                
                quarterly_capped_factor = np.clip(monthly_capped_factor, min_quarterly_factor, max_quarterly_factor)
                
                # Check if quarterly capping was applied
                if abs(quarterly_capped_factor - monthly_capped_factor) > 1e-6:
                    pricing_df.loc[current_idx, 'quarterly_capped'] = True
            
            pricing_df.loc[current_idx, 'telematics_factor_capped'] = quarterly_capped_factor
    
    # Calculate final premiums
    pricing_df['final_premium'] = BASE_PREMIUM * pricing_df['telematics_factor_capped']
    
    # Log capping statistics
    total_records = len(pricing_df)
    monthly_capped_count = pricing_df['monthly_capped'].sum()
    quarterly_capped_count = pricing_df['quarterly_capped'].sum()
    grace_period_count = pricing_df['is_first_month'].sum()
    
    logger.info(f"Capping applied: {monthly_capped_count}/{total_records} monthly, {quarterly_capped_count}/{total_records} quarterly")
    logger.info(f"Grace period: {grace_period_count}/{total_records} first-month users")
    
    return pricing_df


def create_pricing_output(pricing_df: pd.DataFrame, reason_codes: Dict[Tuple[str, str], List[str]]) -> List[Dict]:
    """Create final pricing output with reason codes."""
    
    logger.info("Creating pricing output...")
    
    pricing_results = []
    
    for _, row in pricing_df.iterrows():
        user_id = str(row['user_id'])
        month = str(row['month'])
        
        # Get reason codes for this user-month
        top_reasons = reason_codes.get((user_id, month), [])
        
        result = {
            'user_id': user_id,
            'month': month,
            'base_premium': BASE_PREMIUM,
            'predicted_loss': float(row['lgb_predicted_loss']),
            'book_avg': float(row['book_avg']),
            'risk_index': float(row['risk_index']),
            'ewma_index': float(row['ewma_index']),
            'telematics_factor_capped': float(row['telematics_factor_capped']),
            'final_premium': float(row['final_premium']),
            'top_reasons': top_reasons,
            'is_first_month': bool(row['is_first_month']),
            'monthly_capped': bool(row['monthly_capped']),
            'quarterly_capped': bool(row['quarterly_capped'])
        }
        
        pricing_results.append(result)
    
    logger.info(f"Created pricing output for {len(pricing_results)} user-months")
    
    return pricing_results


def print_pricing_summary(pricing_results: List[Dict]) -> None:
    """Print summary statistics of pricing results."""
    
    if not pricing_results:
        logger.warning("No pricing results to summarize")
        return
    
    factors = [r['telematics_factor_capped'] for r in pricing_results]
    monthly_capped = sum(1 for r in pricing_results if r['monthly_capped'])
    quarterly_capped = sum(1 for r in pricing_results if r['quarterly_capped'])
    grace_period = sum(1 for r in pricing_results if r['is_first_month'])
    
    total_count = len(pricing_results)
    avg_factor = np.mean(factors)
    median_factor = np.median(factors)
    min_factor = np.min(factors)
    max_factor = np.max(factors)
    
    print("\n" + "="*60)
    print("PRICING SUMMARY")
    print("="*60)
    print(f"Total user-months: {total_count:,}")
    print(f"Base premium: ${BASE_PREMIUM:.2f}")
    print("\nTelematics Factors:")
    print(f"  Average: {avg_factor:.3f}")
    print(f"  Median: {median_factor:.3f}")
    print(f"  Range: {min_factor:.3f} - {max_factor:.3f}")
    print("\nCapping Applied:")
    print(f"  Monthly capped: {monthly_capped:,} ({monthly_capped/total_count*100:.1f}%)")
    print(f"  Quarterly capped: {quarterly_capped:,} ({quarterly_capped/total_count*100:.1f}%)")
    print(f"  Grace period: {grace_period:,} ({grace_period/total_count*100:.1f}%)")
    print("\nFinal Premiums:")
    final_premiums = [r['final_premium'] for r in pricing_results]
    print(f"  Average: ${np.mean(final_premiums):.2f}")
    print(f"  Range: ${np.min(final_premiums):.2f} - ${np.max(final_premiums):.2f}")


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description="Run pricing for InsurityAI")
    parser.add_argument("--features", default="./data/features.parquet", 
                       help="Path to features file")
    parser.add_argument("--models", default="./models", 
                       help="Directory containing model files")
    parser.add_argument("--output", default="./data/pricing_results.json", 
                       help="Output path for pricing results")
    
    args = parser.parse_args()
    
    try:
        # Ensure output directory exists
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        
        # Load features data
        if not os.path.exists(args.features):
            raise FileNotFoundError(f"Features file not found: {args.features}")
        
        logger.info(f"Loading features from {args.features}")
        features_df = pd.read_parquet(args.features)
        
        # Load models
        glm_model, lgb_model = load_models(args.models)
        
        # Load reason codes
        reason_codes_path = "./data/reason_codes.jsonl"
        reason_codes = load_reason_codes(reason_codes_path)
        
        # Generate predictions
        predictions_df = generate_predictions(features_df, glm_model, lgb_model)
        
        # Calculate book averages
        pricing_df = calculate_book_averages(predictions_df)
        
        # Apply EWMA smoothing
        pricing_df = apply_ewma_smoothing(pricing_df)
        
        # Apply caps and grace period
        pricing_df = apply_telematics_caps_and_grace(pricing_df)
        
        # Create final output
        pricing_results = create_pricing_output(pricing_df, reason_codes)
        
        # Save results
        logger.info(f"Saving pricing results to {args.output}")
        with open(args.output, 'w') as f:
            json.dump(pricing_results, f, indent=2)
        
        # Print summary
        print_pricing_summary(pricing_results)
        
        logger.info("Pricing pipeline completed successfully!")
        
    except Exception as e:
        logger.error(f"Pricing pipeline failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()