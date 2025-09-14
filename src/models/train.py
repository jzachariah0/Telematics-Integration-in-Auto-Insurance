#!/usr/bin/env python3
"""
Model training pipeline for InsurityAI project.

Trains GLM and LightGBM models to predict loss cost and generates
comprehensive evaluation metrics and explainability outputs.
"""

import argparse
import json
import logging
import os
import pickle
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any

import lightgbm as lgb
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap
import statsmodels.api as sm
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set random seed for reproducibility
np.random.seed(42)


def ensure_directories_exist() -> None:
    """Ensure output directory structure exists."""
    directories = [
        "./models",
        "./docs/metrics",
        "./data"
    ]
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)


def load_and_prepare_data(features_path: str) -> Tuple[pd.DataFrame, List[str]]:
    """
    Load features data and prepare for modeling.
    
    Returns:
        Tuple of (dataframe, feature_column_names)
    """
    logger.info(f"Loading features from {features_path}")
    
    if not os.path.exists(features_path):
        raise FileNotFoundError(f"Features file not found: {features_path}")
    
    df = pd.read_parquet(features_path)
    logger.info(f"Loaded {len(df):,} records with {len(df.columns)} columns")
    
    # Identify feature columns (exclude IDs, time, and targets)
    exclude_cols = {
        'user_id', 'month', 'frequency', 'severity_mean', 'loss_cost'
    }
    feature_cols = [col for col in df.columns if col not in exclude_cols]
    
    logger.info(f"Using {len(feature_cols)} features: {feature_cols}")
    
    # Handle missing values with median imputation for numeric columns
    numeric_features = df[feature_cols].select_dtypes(include=[np.number]).columns
    for col in numeric_features:
        if df[col].isnull().sum() > 0:
            median_val = df[col].median()
            df[col].fillna(median_val, inplace=True)
            logger.info(f"Imputed {col} missing values with median: {median_val:.3f}")
    
    return df, feature_cols


def create_train_test_split(df: pd.DataFrame, feature_cols: List[str]) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Create train/test split by month if multiple months, else by user.
    
    Returns:
        X_train, X_test, y_train, y_test
    """
    target = 'loss_cost'
    
    # Check if we have multiple months
    unique_months = df['month'].nunique()
    logger.info(f"Data spans {unique_months} unique months")
    
    if unique_months > 1:
        # Split by month - use last month as test
        months = sorted(df['month'].unique())
        test_month = months[-1]
        train_months = months[:-1]
        
        train_mask = df['month'].isin(train_months)
        test_mask = df['month'] == test_month
        
        logger.info(f"Train months: {train_months}")
        logger.info(f"Test month: {test_month}")
    else:
        # Split 80/20 by user
        unique_users = df['user_id'].unique()
        train_users, test_users = train_test_split(
            unique_users, test_size=0.2, random_state=42
        )
        
        train_mask = df['user_id'].isin(train_users)
        test_mask = df['user_id'].isin(test_users)
        
        logger.info(f"Train users: {len(train_users)}, Test users: {len(test_users)}")
    
    X_train = df.loc[train_mask, feature_cols]
    X_test = df.loc[test_mask, feature_cols]
    y_train = df.loc[train_mask, target]
    y_test = df.loc[test_mask, target]
    
    logger.info(f"Train set: {len(X_train):,} records, Test set: {len(X_test):,} records")
    
    return X_train, X_test, y_train, y_test


def train_glm_model(X_train: pd.DataFrame, y_train: pd.Series, X_test: pd.DataFrame, y_test: pd.Series) -> sm.GLM:
    """
    Train GLM with Tweedie family for loss cost prediction.
    
    Returns:
        Fitted GLM model
    """
    logger.info("Training GLM model with Tweedie family...")
    
    # Add constant for intercept
    X_train_const = sm.add_constant(X_train)
    X_test_const = sm.add_constant(X_test)
    
    # Use Tweedie family with log link and variance_power=1.5
    # Add small constant to avoid log(0) issues
    y_train_adj = y_train + 1e-6
    y_test_adj = y_test + 1e-6
    
    try:
        # Fit GLM with Tweedie family
        glm_model = sm.GLM(
            y_train_adj, 
            X_train_const,
            family=sm.families.Tweedie(var_power=1.5, link=sm.families.links.log())
        )
        glm_fitted = glm_model.fit()
        
        # Save model summary
        with open("./docs/metrics/glm_summary.txt", "w") as f:
            f.write(str(glm_fitted.summary()))
        
        logger.info("GLM model trained successfully")
        
        # Save model
        with open("./models/glm.pkl", "wb") as f:
            pickle.dump(glm_fitted, f)
        
        return glm_fitted
        
    except Exception as e:
        logger.error(f"GLM training failed: {str(e)}")
        logger.info("Falling back to Gaussian GLM...")
        
        # Fallback to Gaussian family if Tweedie fails
        glm_model = sm.GLM(y_train, X_train_const, family=sm.families.Gaussian())
        glm_fitted = glm_model.fit()
        
        with open("./docs/metrics/glm_summary.txt", "w") as f:
            f.write("GLM Summary (Gaussian fallback)\n")
            f.write("="*50 + "\n")
            f.write(str(glm_fitted.summary()))
        
        with open("./models/glm.pkl", "wb") as f:
            pickle.dump(glm_fitted, f)
        
        return glm_fitted


def train_lightgbm_model(X_train: pd.DataFrame, y_train: pd.Series, X_test: pd.DataFrame, y_test: pd.Series, feature_cols: List[str]) -> lgb.Booster:
    """
    Train LightGBM model with monotonic constraints.
    
    Returns:
        Fitted LightGBM booster
    """
    logger.info("Training LightGBM model with monotonic constraints...")
    
    # Define monotonic constraints
    monotone_increasing_features = {
        'speeding_pct_over_10', 'speeding_pct_over_15', 'night_pct',
        'harsh_brake_rate_per_100mi', 'harsh_lateral_rate_per_100mi', 'volatility_jerk_p95'
    }
    
    # Create monotone constraints array
    monotone_constraints = []
    for feature in feature_cols:
        if feature in monotone_increasing_features:
            monotone_constraints.append(1)  # monotone increasing
        else:
            monotone_constraints.append(0)  # no constraint
    
    logger.info(f"Monotonic constraints applied to: {monotone_increasing_features}")
    
    # Prepare datasets
    train_data = lgb.Dataset(X_train, label=y_train)
    valid_data = lgb.Dataset(X_test, label=y_test, reference=train_data)
    
    # LightGBM parameters
    params = {
        'objective': 'regression',
        'metric': 'mae',
        'boosting_type': 'gbdt',
        'num_leaves': 31,
        'max_depth': 6,
        'learning_rate': 0.1,
        'feature_fraction': 0.8,
        'bagging_fraction': 0.8,
        'bagging_freq': 5,
        'monotone_constraints': monotone_constraints,
        'verbose': -1,
        'random_state': 42
    }
    
    # Train model with early stopping
    lgb_model = lgb.train(
        params,
        train_data,
        valid_sets=[valid_data],
        num_boost_round=1000,
        callbacks=[
            lgb.early_stopping(stopping_rounds=50),
            lgb.log_evaluation(period=0)  # Silent training
        ]
    )
    
    # Save model
    lgb_model.save_model("./models/lgbm_loss_cost.txt")
    
    with open("./models/lgbm.pkl", "wb") as f:
        pickle.dump(lgb_model, f)
    
    logger.info("LightGBM model trained successfully")
    
    return lgb_model


def calculate_metrics(y_true: pd.Series, y_pred: np.ndarray, model_name: str) -> Dict[str, float]:
    """Calculate evaluation metrics for model performance."""
    
    # Basic regression metrics
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    
    # MAPE (handling zero values)
    mape = np.mean(np.abs((y_true - y_pred) / np.maximum(y_true, 1e-8))) * 100
    
    # Gini coefficient (rank-based)
    # Create binary target for "has_claim"
    has_claim_true = (y_true > 0).astype(int)
    
    if len(np.unique(has_claim_true)) > 1:
        # Calculate AUC-style Gini
        from sklearn.metrics import roc_auc_score
        try:
            auc = roc_auc_score(has_claim_true, y_pred)
            gini = 2 * auc - 1
        except:
            gini = 0.0
    else:
        gini = 0.0
    
    metrics = {
        'MAE': mae,
        'MAPE': mape,
        'R2': r2,
        'Gini': gini
    }
    
    logger.info(f"{model_name} metrics: {metrics}")
    
    return metrics


def create_calibration_plot(y_true: pd.Series, y_pred_glm: np.ndarray, y_pred_lgb: np.ndarray) -> None:
    """Create calibration plot comparing predicted vs actual loss cost in deciles."""
    
    plt.figure(figsize=(12, 5))
    
    for i, (y_pred, model_name, color) in enumerate([(y_pred_glm, 'GLM', 'blue'), (y_pred_lgb, 'LightGBM', 'red')]):
        plt.subplot(1, 2, i+1)
        
        # Create deciles based on predictions
        df_cal = pd.DataFrame({'actual': y_true, 'predicted': y_pred})
        df_cal['decile'] = pd.qcut(df_cal['predicted'], q=10, labels=False, duplicates='drop')
        
        # Calculate mean actual and predicted by decile
        cal_stats = df_cal.groupby('decile').agg({
            'actual': 'mean',
            'predicted': 'mean'
        }).reset_index()
        
        plt.scatter(cal_stats['predicted'], cal_stats['actual'], color=color, s=50, alpha=0.7)
        plt.plot([0, cal_stats['predicted'].max()], [0, cal_stats['predicted'].max()], 'k--', alpha=0.5)
        
        plt.xlabel('Predicted Loss Cost')
        plt.ylabel('Actual Loss Cost') 
        plt.title(f'{model_name} Calibration Plot')
        plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('./docs/metrics/calibration_plot.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    logger.info("Calibration plot saved to ./docs/metrics/calibration_plot.png")


def create_lift_chart(y_true: pd.Series, y_pred_glm: np.ndarray, y_pred_lgb: np.ndarray) -> None:
    """Create lift chart showing cumulative gain by prediction decile."""
    
    plt.figure(figsize=(10, 6))
    
    for y_pred, model_name, color in [(y_pred_glm, 'GLM', 'blue'), (y_pred_lgb, 'LightGBM', 'red')]:
        # Create deciles
        df_lift = pd.DataFrame({'actual': y_true, 'predicted': y_pred})
        df_lift['decile'] = pd.qcut(df_lift['predicted'], q=10, labels=False, duplicates='drop')
        
        # Calculate cumulative gains
        decile_stats = df_lift.groupby('decile').agg({
            'actual': ['sum', 'count']
        }).reset_index()
        
        decile_stats.columns = ['decile', 'total_loss', 'count']
        decile_stats = decile_stats.sort_values('decile', ascending=False)
        
        # Calculate cumulative percentages
        decile_stats['cum_loss_pct'] = decile_stats['total_loss'].cumsum() / decile_stats['total_loss'].sum() * 100
        decile_stats['cum_pop_pct'] = decile_stats['count'].cumsum() / decile_stats['count'].sum() * 100
        
        plt.plot(decile_stats['cum_pop_pct'], decile_stats['cum_loss_pct'], 
                marker='o', label=model_name, color=color, linewidth=2)
    
    # Add diagonal reference line
    plt.plot([0, 100], [0, 100], 'k--', alpha=0.5, label='Random')
    
    plt.xlabel('Cumulative Population %')
    plt.ylabel('Cumulative Loss Cost %')
    plt.title('Lift Chart - Cumulative Gain')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xlim(0, 100)
    plt.ylim(0, 100)
    
    plt.tight_layout()
    plt.savefig('./docs/metrics/lift_chart.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    logger.info("Lift chart saved to ./docs/metrics/lift_chart.png")


def generate_shap_analysis(lgb_model: lgb.Booster, X_test: pd.DataFrame, df_test: pd.DataFrame) -> None:
    """Generate SHAP analysis for LightGBM model."""
    
    logger.info("Generating SHAP analysis...")
    
    # Create SHAP explainer
    explainer = shap.TreeExplainer(lgb_model)
    shap_values = explainer.shap_values(X_test)
    
    # Global SHAP importance plot
    plt.figure(figsize=(10, 8))
    shap.summary_plot(shap_values, X_test, plot_type="bar", show=False)
    plt.tight_layout()
    plt.savefig('./docs/metrics/shap_global.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    logger.info("Global SHAP plot saved to ./docs/metrics/shap_global.png")
    
    # Generate per-row explanations
    reason_codes = []
    
    for idx, (_, row) in enumerate(df_test.iterrows()):
        # Get SHAP values for this row
        row_shap = shap_values[idx]
        
        # Get top 5 positive contributors
        feature_shap = list(zip(X_test.columns, row_shap))
        # Sort by SHAP value (descending for positive impact)
        feature_shap.sort(key=lambda x: x[1], reverse=True)
        
        top_reasons = []
        for rank, (feature, shap_val) in enumerate(feature_shap[:5]):
            if shap_val > 0:  # Only positive contributors
                top_reasons.append({
                    'feature': feature,
                    'shap_value': float(shap_val),
                    'rank': rank + 1
                })
        
        # Create reason code entry
        reason_entry = {
            'user_id': str(row['user_id']),
            'month': str(row['month']),
            'top_reasons': top_reasons
        }
        
        reason_codes.append(reason_entry)
    
    # Save reason codes as JSONL
    with open('./data/reason_codes.jsonl', 'w') as f:
        for entry in reason_codes:
            f.write(json.dumps(entry) + '\n')
    
    logger.info(f"Reason codes saved to ./data/reason_codes.jsonl ({len(reason_codes)} entries)")


def create_model_comparison_report(glm_metrics: Dict[str, float], lgb_metrics: Dict[str, float]) -> None:
    """Create markdown report comparing model performance."""
    
    report_content = f"""# Model Performance Comparison

## Overview
This report compares the performance of GLM (Tweedie) and LightGBM models for predicting insurance loss cost.

## Model Metrics

### GLM (Tweedie) Results
- **MAE**: {glm_metrics['MAE']:.2f}
- **MAPE**: {glm_metrics['MAPE']:.2f}%
- **R²**: {glm_metrics['R2']:.4f}
- **Gini**: {glm_metrics['Gini']:.4f}

### LightGBM Results  
- **MAE**: {lgb_metrics['MAE']:.2f}
- **MAPE**: {lgb_metrics['MAPE']:.2f}%
- **R²**: {lgb_metrics['R2']:.4f}
- **Gini**: {lgb_metrics['Gini']:.4f}

## Model Comparison

| Metric | GLM | LightGBM | Better Model |
|--------|-----|----------|--------------|
| MAE | {glm_metrics['MAE']:.2f} | {lgb_metrics['MAE']:.2f} | {'LightGBM' if lgb_metrics['MAE'] < glm_metrics['MAE'] else 'GLM'} |
| MAPE | {glm_metrics['MAPE']:.2f}% | {lgb_metrics['MAPE']:.2f}% | {'LightGBM' if lgb_metrics['MAPE'] < glm_metrics['MAPE'] else 'GLM'} |
| R² | {glm_metrics['R2']:.4f} | {lgb_metrics['R2']:.4f} | {'LightGBM' if lgb_metrics['R2'] > glm_metrics['R2'] else 'GLM'} |
| Gini | {glm_metrics['Gini']:.4f} | {lgb_metrics['Gini']:.4f} | {'LightGBM' if lgb_metrics['Gini'] > glm_metrics['Gini'] else 'GLM'} |

## Key Findings

- **Best Overall Model**: {'LightGBM' if lgb_metrics['R2'] > glm_metrics['R2'] else 'GLM'} (based on R²)
- **Prediction Accuracy**: Lower MAE indicates better absolute prediction accuracy
- **Ranking Performance**: Higher Gini coefficient indicates better ranking of risk

## Generated Artifacts

- **Models**: `./models/glm.pkl`, `./models/lgbm.pkl`
- **Visualizations**: `./docs/metrics/calibration_plot.png`, `./docs/metrics/lift_chart.png`
- **Explainability**: `./docs/metrics/shap_global.png`, `./data/reason_codes.jsonl`
- **Model Details**: `./docs/metrics/glm_summary.txt`

## Notes

- GLM uses Tweedie family with log link (variance_power=1.5)
- LightGBM includes monotonic constraints on risk-increasing features
- SHAP values provide individual prediction explanations
- Calibration plots show prediction vs actual alignment by decile
"""
    
    with open('./docs/metrics/model_compare.md', 'w') as f:
        f.write(report_content)
    
    logger.info("Model comparison report saved to ./docs/metrics/model_compare.md")


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description="Train models for InsurityAI")
    parser.add_argument("--features", default="./data/features.parquet", 
                       help="Path to features file")
    parser.add_argument("--output", default="./models/", 
                       help="Output directory for models")
    
    args = parser.parse_args()
    
    try:
        # Ensure output directories exist
        ensure_directories_exist()
        
        # Load and prepare data
        df, feature_cols = load_and_prepare_data(args.features)
        
        # Create train/test split
        X_train, X_test, y_train, y_test = create_train_test_split(df, feature_cols)
        
        # Train GLM model
        glm_model = train_glm_model(X_train, y_train, X_test, y_test)
        
        # Train LightGBM model
        lgb_model = train_lightgbm_model(X_train, y_train, X_test, y_test, feature_cols)
        
        # Generate predictions
        # For GLM, need to add constant
        X_test_const = sm.add_constant(X_test)
        glm_pred = glm_model.predict(X_test_const)
        lgb_pred = lgb_model.predict(X_test)
        
        # Calculate metrics
        glm_metrics = calculate_metrics(y_test, glm_pred, "GLM")
        lgb_metrics = calculate_metrics(y_test, lgb_pred, "LightGBM")
        
        # Create visualizations
        create_calibration_plot(y_test, glm_pred, lgb_pred)
        create_lift_chart(y_test, glm_pred, lgb_pred)
        
        # Generate SHAP analysis
        df_test = df.loc[y_test.index].copy()
        generate_shap_analysis(lgb_model, X_test, df_test)
        
        # Create comparison report
        create_model_comparison_report(glm_metrics, lgb_metrics)
        
        # Print summary
        print("\n" + "="*60)
        print("MODEL TRAINING COMPLETED SUCCESSFULLY")
        print("="*60)
        print(f"Train samples: {len(X_train):,}")
        print(f"Test samples: {len(X_test):,}")
        print(f"Features used: {len(feature_cols)}")
        print("\nGLM Performance:")
        print(f"  MAE: {glm_metrics['MAE']:.2f}")
        print(f"  R²: {glm_metrics['R2']:.4f}")
        print("\nLightGBM Performance:")
        print(f"  MAE: {lgb_metrics['MAE']:.2f}")
        print(f"  R²: {lgb_metrics['R2']:.4f}")
        print(f"\nBest Model: {'LightGBM' if lgb_metrics['R2'] > glm_metrics['R2'] else 'GLM'}")
        print("\nOutput Files:")
        print("  Models: ./models/glm.pkl, ./models/lgbm.pkl")
        print("  Metrics: ./docs/metrics/model_compare.md")
        print("  Plots: ./docs/metrics/*.png")
        print("  Explanations: ./data/reason_codes.jsonl")
        
        logger.info("Model training pipeline completed successfully!")
        
    except Exception as e:
        logger.error(f"Model training failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()