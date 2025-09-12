# Data Dictionary - InsurityAI Features

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
