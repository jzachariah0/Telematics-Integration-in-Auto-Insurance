#!/usr/bin/env python3def main():

"""    print("Feature building started...")

Feature engineering pipeline for InsurityAI project.    print("✅ Features built (placeholder).")



Reads raw trip data and creates monthly per-user features for risk modeling,if __name__ == "__main__":

including synthetic ground-truth targets for claims modeling.    main()

"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set random seed for reproducibility
np.random.seed(42)


def ensure_directories_exist(output_path: str) -> None:
    """Ensure output directory structure exists."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path("./docs").mkdir(parents=True, exist_ok=True)


def load_trip_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load and validate trip data files."""
    trips_path = "./data/raw/trips.parquet"
    trips_meta_path = "./data/raw/trips_meta.parquet"
    
    if not os.path.exists(trips_path):
        raise FileNotFoundError(f"Required file not found: {trips_path}")
    if not os.path.exists(trips_meta_path):
        raise FileNotFoundError(f"Required file not found: {trips_meta_path}")
    
    logger.info(f"Loading trips data from {trips_path}")
    trips = pd.read_parquet(trips_path)
    
    logger.info(f"Loading trips metadata from {trips_meta_path}")
    trips_meta = pd.read_parquet(trips_meta_path)
    
    logger.info(f"Loaded {len(trips):,} trips and {len(trips_meta):,} metadata records")
    return trips, trips_meta


def engineer_features(trips: pd.DataFrame, trips_meta: pd.DataFrame) -> pd.DataFrame:
    """
    Engineer monthly per-user features from trip data.
    
    Returns:
        DataFrame with columns: user_id, month, features...
    """
    logger.info("Starting feature engineering...")
    
    # Merge trips with metadata
    df = trips.merge(trips_meta, on='trip_id', how='left')
    
    # Convert timestamp to datetime and extract month
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['month'] = df['timestamp'].dt.to_period('M')
    
    # Convert km to miles (1 km = 0.621371 miles)
    df['miles'] = df['distance_km'] * 0.621371
    
    # Calculate rates per 100 miles
    df['harsh_brake_rate_per_100mi'] = np.where(
        df['miles'] > 0, 
        (df['harsh_brake_count'] / df['miles']) * 100, 
        0
    )
    df['harsh_accel_rate_per_100mi'] = np.where(
        df['miles'] > 0, 
        (df['harsh_accel_count'] / df['miles']) * 100, 
        0
    )
    df['harsh_lateral_rate_per_100mi'] = np.where(
        df['miles'] > 0, 
        (df['harsh_lateral_count'] / df['miles']) * 100, 
        0
    )
    
    # Calculate speeding percentages (assuming speed and speed_limit are in m/s)
    df['speed_over_limit'] = df['avg_speed_mps'] - df['speed_limit_mps']
    df['speeding_5'] = df['speed_over_limit'] > 5
    df['speeding_10'] = df['speed_over_limit'] > 10
    df['speeding_15'] = df['speed_over_limit'] > 15
    
    # Calculate night and wet percentages
    df['is_night'] = df['night_driving_pct'] > 0.5  # Simplification
    df['is_wet'] = df['wet_weather_pct'] > 0.5      # Simplification
    
    # Group by user and month to create monthly features
    monthly_features = df.groupby(['user_id', 'month']).agg({
        'miles': 'sum',
        'trip_id': 'count',  # trip_count
        'harsh_brake_rate_per_100mi': 'mean',
        'harsh_accel_rate_per_100mi': 'mean', 
        'harsh_lateral_rate_per_100mi': 'mean',
        'speeding_5': 'mean',  # speeding_pct_over_5
        'speeding_10': 'mean', # speeding_pct_over_10
        'speeding_15': 'mean', # speeding_pct_over_15
        'night_driving_pct': 'mean',  # night_pct
        'wet_weather_pct': 'mean',    # wet_pct
        'jerk_p95': 'mean',           # volatility_jerk_p95
        'highway_pct': 'mean',        # pct_highway
        'arterial_pct': 'mean',       # pct_arterial
        'local_pct': 'mean'           # pct_local
    }).reset_index()
    
    # Rename columns for clarity
    monthly_features.rename(columns={
        'trip_id': 'trip_count',
        'speeding_5': 'speeding_pct_over_5',
        'speeding_10': 'speeding_pct_over_10', 
        'speeding_15': 'speeding_pct_over_15',
        'night_driving_pct': 'night_pct',
        'wet_weather_pct': 'wet_pct',
        'jerk_p95': 'volatility_jerk_p95',
        'highway_pct': 'pct_highway',
        'arterial_pct': 'pct_arterial',
        'local_pct': 'pct_local'
    }, inplace=True)
    
    # Convert month back to string for output
    monthly_features['month'] = monthly_features['month'].astype(str)
    
    logger.info(f"Generated features for {len(monthly_features):,} user-months")
    return monthly_features


def generate_synthetic_targets(features: pd.DataFrame) -> pd.DataFrame:
    """
    Generate synthetic ground-truth targets for claims modeling.
    
    Creates frequency and severity targets based on engineered risk index.
    """
    logger.info("Generating synthetic targets...")
    
    df = features.copy()
    
    # Scale and clip features to reasonable ranges for risk modeling
    df['speeding_scaled'] = np.clip(df['speeding_pct_over_10'], 0, 1)
    df['night_scaled'] = np.clip(df['night_pct'], 0, 1)
    df['harsh_brake_scaled'] = np.clip(df['harsh_brake_rate_per_100mi'] / 5, 0, 1)
    df['wet_scaled'] = np.clip(df['wet_pct'], 0, 1)
    df['jerk_scaled'] = np.clip(df['volatility_jerk_p95'] / 5, 0, 1)
    
    # Calculate risk index as weighted combination
    risk_index = (
        0.8 * df['speeding_scaled'] +
        0.5 * df['night_scaled'] +
        0.4 * df['harsh_brake_scaled'] +
        0.3 * df['wet_scaled'] +
        0.2 * df['jerk_scaled']
    )
    
    # Generate frequency from Poisson distribution
    lambda_freq = np.exp(risk_index - 2)  # Shift down to get reasonable frequencies
    lambda_freq = np.clip(lambda_freq, 0.01, 2.0)  # Reasonable range
    df['frequency'] = np.random.poisson(lambda_freq)
    
    # Generate severity for positive claims from Gamma distribution
    # Shape and scale parameters for reasonable severity distribution
    shape = 2.0
    scale = 5000  # Base severity around $10k
    
    # Adjust severity based on risk (higher risk = higher severity)
    severity_scale = scale * (1 + risk_index)
    df['severity_mean'] = np.where(
        df['frequency'] > 0,
        np.random.gamma(shape, severity_scale),
        0
    )
    
    # Calculate loss cost
    df['loss_cost'] = df['frequency'] * df['severity_mean']
    
    # Clean up temporary columns
    df.drop(columns=[
        'speeding_scaled', 'night_scaled', 'harsh_brake_scaled', 
        'wet_scaled', 'jerk_scaled'
    ], inplace=True)
    
    # Add some claims have zero severity for realism
    zero_sev_mask = (df['frequency'] > 0) & (np.random.random(len(df)) < 0.1)
    df.loc[zero_sev_mask, 'severity_mean'] = 0
    df.loc[zero_sev_mask, 'loss_cost'] = 0
    
    logger.info(f"Generated targets: {df['frequency'].sum():,.0f} total claims, "
               f"${df['loss_cost'].sum():,.0f} total loss cost")
    
    return df


def create_data_dictionary() -> None:
    """Create documentation for the features and targets."""
    logger.info("Creating data dictionary...")
    
    dictionary_content = """# Data Dictionary - InsurityAI Features

## Feature Definitions

### Identifiers
- **user_id**: Unique identifier for each driver
- **month**: Month in YYYY-MM format for aggregation period

### Basic Metrics
- **miles**: Total miles driven in the month (converted from km)
- **trip_count**: Total number of trips taken in the month

### Harsh Driving Behaviors (per 100 miles)
- **harsh_brake_rate_per_100mi**: Rate of harsh braking events per 100 miles
- **harsh_accel_rate_per_100mi**: Rate of harsh acceleration events per 100 miles  
- **harsh_lateral_rate_per_100mi**: Rate of harsh lateral movement events per 100 miles

### Speeding Metrics
- **speeding_pct_over_5**: Percentage of driving time speeding >5 mph over limit
- **speeding_pct_over_10**: Percentage of driving time speeding >10 mph over limit
- **speeding_pct_over_15**: Percentage of driving time speeding >15 mph over limit

### Environmental Conditions
- **night_pct**: Percentage of driving during nighttime hours
- **wet_pct**: Percentage of driving in wet weather conditions

### Driving Style
- **volatility_jerk_p95**: 95th percentile of jerk (rate of acceleration change)

### Road Type Exposure
- **pct_highway**: Percentage of miles driven on highways
- **pct_arterial**: Percentage of miles driven on arterial roads
- **pct_local**: Percentage of miles driven on local roads

## Target Variables (Synthetic)

### Claims Frequency and Severity
- **frequency**: Number of claims in the month (Poisson distributed)
- **severity_mean**: Average claim severity for the month (Gamma distributed, $USD)
- **loss_cost**: Total loss cost (frequency × severity_mean)

### Risk Model
The synthetic targets are generated using a risk index:
```
risk = 0.8×speeding_pct_over_10 + 0.5×night_pct + 0.4×harsh_brake_rate_per_100mi/5 + 0.3×wet_pct + 0.2×volatility_jerk_p95/5
```

Higher risk drivers have higher expected frequency and severity of claims.
"""
    
    with open("./docs/data_dictionary.md", "w") as f:
        f.write(dictionary_content)
    
    logger.info("Data dictionary written to ./docs/data_dictionary.md")


def print_summary(df: pd.DataFrame) -> None:
    """Print summary statistics for the output dataset."""
    logger.info("Dataset Summary:")
    logger.info(f"  Rows: {len(df):,}")
    logger.info(f"  Columns: {len(df.columns)}")
    logger.info(f"  Unique users: {df['user_id'].nunique():,}")
    logger.info(f"  Unique months: {df['month'].nunique():,}")
    logger.info(f"  Null values: {df.isnull().sum().sum():,}")
    logger.info(f"  Total miles: {df['miles'].sum():,.1f}")
    logger.info(f"  Total claims: {df['frequency'].sum():,.0f}")
    logger.info(f"  Total loss cost: ${df['loss_cost'].sum():,.0f}")


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description="Build features for InsurityAI")
    parser.add_argument("--input_db", help="Input database path (ignored if missing)")
    parser.add_argument("--output", default="./data/features.parquet", 
                       help="Output path for features")
    
    args = parser.parse_args()
    
    try:
        # Ensure output directories exist
        ensure_directories_exist(args.output)
        
        # Load data
        trips, trips_meta = load_trip_data()
        
        # Engineer features
        features = engineer_features(trips, trips_meta)
        
        # Generate synthetic targets
        final_dataset = generate_synthetic_targets(features)
        
        # Save output
        logger.info(f"Saving features to {args.output}")
        final_dataset.to_parquet(args.output, index=False)
        
        # Create documentation
        create_data_dictionary()
        
        # Print summary
        print_summary(final_dataset)
        
        logger.info("Feature engineering completed successfully!")
        
    except Exception as e:
        logger.error(f"Feature engineering failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()