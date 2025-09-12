#!/usr/bin/env python3def main():

"""    print("Ingest pipeline started...")

Data ingestion pipeline for InsurityAI project.    print("✅ Ingest complete (placeholder).")



Generates synthetic trip data for testing and development purposes.if __name__ == "__main__":

Creates realistic telematics data including driving behaviors, conditions, and metadata.    main()
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
    Path("./data/raw").mkdir(parents=True, exist_ok=True)


def generate_synthetic_trips(n_users: int = 100, months: int = 3) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Generate synthetic trip data for testing.
    
    Args:
        n_users: Number of unique users to generate
        months: Number of months of data to generate
        
    Returns:
        Tuple of (trips_df, trips_meta_df)
    """
    logger.info(f"Generating synthetic data for {n_users} users over {months} months")
    
    # Generate user IDs
    user_ids = [f"user_{i:04d}" for i in range(1, n_users + 1)]
    
    # Generate months
    months_list = [f"2024-{i:02d}" for i in range(1, months + 1)]
    
    trips_data = []
    trips_meta_data = []
    trip_id_counter = 1
    
    for user_id in user_ids:
        # User characteristics (some users are riskier than others)
        user_risk_factor = np.random.lognormal(0, 0.3)  # Most users around 1.0, some outliers
        
        for month in months_list:
            # Number of trips per user per month (Poisson distribution)
            n_trips = np.random.poisson(15) + 5  # 5-30 trips per month typically
            
            for _ in range(n_trips):
                trip_id = f"trip_{trip_id_counter:06d}"
                trip_id_counter += 1
                
                # Basic trip characteristics
                distance_km = np.random.exponential(25) + 2  # 2-100+ km trips
                duration_minutes = distance_km * np.random.normal(2.5, 0.5) + np.random.normal(0, 5)
                duration_minutes = max(5, duration_minutes)  # Minimum 5 minutes
                
                # Speed calculations
                avg_speed_kmh = distance_km / (duration_minutes / 60)
                avg_speed_mps = avg_speed_kmh / 3.6
                
                # Speed limit (varies by road type)
                road_type = np.random.choice(['highway', 'arterial', 'local'], p=[0.3, 0.4, 0.3])
                if road_type == 'highway':
                    speed_limit_kmh = np.random.choice([100, 110, 120], p=[0.5, 0.3, 0.2])
                elif road_type == 'arterial':
                    speed_limit_kmh = np.random.choice([50, 60, 70], p=[0.4, 0.4, 0.2])
                else:  # local
                    speed_limit_kmh = np.random.choice([30, 40, 50], p=[0.3, 0.4, 0.3])
                
                speed_limit_mps = speed_limit_kmh / 3.6
                
                # Harsh events (correlated with user risk factor)
                base_harsh_rate = user_risk_factor * 0.1  # events per km
                harsh_brake_count = np.random.poisson(distance_km * base_harsh_rate)
                harsh_accel_count = np.random.poisson(distance_km * base_harsh_rate * 0.8)
                harsh_lateral_count = np.random.poisson(distance_km * base_harsh_rate * 0.6)
                
                # Environmental conditions
                is_night = np.random.choice([True, False], p=[0.2, 0.8])
                is_wet = np.random.choice([True, False], p=[0.15, 0.85])
                
                night_driving_pct = 1.0 if is_night else 0.0
                wet_weather_pct = 1.0 if is_wet else 0.0
                
                # Road type percentages
                if road_type == 'highway':
                    highway_pct, arterial_pct, local_pct = 0.8, 0.15, 0.05
                elif road_type == 'arterial':
                    highway_pct, arterial_pct, local_pct = 0.1, 0.8, 0.1
                else:
                    highway_pct, arterial_pct, local_pct = 0.05, 0.25, 0.7
                
                # Jerk (smoothness measure) - higher for riskier drivers
                jerk_p95 = np.random.gamma(2, user_risk_factor * 2)
                
                # Trip data
                trip_data = {
                    'trip_id': trip_id,
                    'user_id': user_id,
                    'timestamp': f"{month}-15 12:00:00",  # Simplified timestamp
                    'distance_km': round(distance_km, 2),
                    'duration_minutes': round(duration_minutes, 1),
                    'avg_speed_mps': round(avg_speed_mps, 2),
                    'speed_limit_mps': round(speed_limit_mps, 2),
                    'harsh_brake_count': harsh_brake_count,
                    'harsh_accel_count': harsh_accel_count,
                    'harsh_lateral_count': harsh_lateral_count
                }
                
                # Trip metadata
                trip_meta_data_item = {
                    'trip_id': trip_id,
                    'night_driving_pct': night_driving_pct,
                    'wet_weather_pct': wet_weather_pct,
                    'highway_pct': highway_pct,
                    'arterial_pct': arterial_pct,
                    'local_pct': local_pct,
                    'jerk_p95': round(jerk_p95, 3)
                }
                
                trips_data.append(trip_data)
                trips_meta_data.append(trip_meta_data_item)
    
    trips_df = pd.DataFrame(trips_data)
    trips_meta_df = pd.DataFrame(trips_meta_data)
    
    logger.info(f"Generated {len(trips_df):,} trips with metadata")
    
    return trips_df, trips_meta_df


def save_data(trips_df: pd.DataFrame, trips_meta_df: pd.DataFrame, output_path: str) -> None:
    """Save the generated data to parquet files."""
    
    trips_file = "./data/raw/trips.parquet"
    trips_meta_file = "./data/raw/trips_meta.parquet"
    
    logger.info(f"Saving trips data to {trips_file}")
    trips_df.to_parquet(trips_file, index=False)
    
    logger.info(f"Saving trips metadata to {trips_meta_file}")
    trips_meta_df.to_parquet(trips_meta_file, index=False)
    
    # Print summary
    logger.info("Data generation summary:")
    logger.info(f"  Total trips: {len(trips_df):,}")
    logger.info(f"  Unique users: {trips_df['user_id'].nunique():,}")
    logger.info(f"  Date range: {trips_df['timestamp'].min()} to {trips_df['timestamp'].max()}")
    logger.info(f"  Avg distance per trip: {trips_df['distance_km'].mean():.1f} km")
    logger.info(f"  Total distance: {trips_df['distance_km'].sum():,.0f} km")


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description="Generate synthetic trip data for InsurityAI")
    parser.add_argument("--input", default="./data/synthetic_samples", 
                       help="Input directory (ignored - generates synthetic data)")
    parser.add_argument("--output", default="db", 
                       help="Output format (ignored - saves to parquet)")
    parser.add_argument("--users", type=int, default=100,
                       help="Number of users to generate")
    parser.add_argument("--months", type=int, default=3,
                       help="Number of months of data")
    
    args = parser.parse_args()
    
    try:
        # Ensure output directories exist
        ensure_directories_exist(args.output)
        
        # Generate synthetic data
        trips_df, trips_meta_df = generate_synthetic_trips(args.users, args.months)
        
        # Save data
        save_data(trips_df, trips_meta_df, args.output)
        
        logger.info("Data ingestion completed successfully!")
        
    except Exception as e:
        logger.error(f"Data ingestion failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()