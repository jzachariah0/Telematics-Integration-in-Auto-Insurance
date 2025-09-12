# Model Card: Telematics-Based Auto Insurance Pricing Models

**Version**: 1.0  
**Date**: September 2025  
**Authors**: InsurityAI Development Team  
**Model Type**: Insurance Loss Cost Prediction (GLM & LightGBM Ensemble)

---

## Purpose & Scope

### Intended Use
These models predict **expected loss cost per user-month** for auto insurance pricing, serving as a component in a broader pricing system. The models do **not** output final premiums but provide risk-adjusted loss estimates that feed into downstream pricing algorithms with business rules, regulatory caps, and profit margins.

### Primary Use Cases
- **Risk Assessment**: Monthly recalibration of driver risk profiles
- **Premium Adjustment**: Input to telematics-based insurance pricing
- **Portfolio Management**: Risk segmentation and exposure monitoring
- **Regulatory Reporting**: Actuarial justification for rate changes

### Out-of-Scope Applications
- ❌ Final premium determination (requires business rules/regulatory constraints)
- ❌ Claims frequency/severity modeling (models combined expected loss)
- ❌ Real-time driver scoring (models operate on monthly aggregations)
- ❌ Cross-selling or marketing applications

---

## Data Sources & Context

### Primary Data Source
**Synthetic Smartphone Telematics Data**
- **Collection Method**: Simulated driving behavior based on realistic distributions
- **Coverage**: 100 users over 3 months (300 user-months total)
- **Trip Volume**: ~5,900 individual trips with detailed telemetry

### Contextual Variables
- **Road Classification**: Highway (30%), Arterial (40%), Local (30%)
- **Environmental Conditions**: Night driving, wet weather exposure
- **Geographic Context**: Coarse-grained (regional level only)
- **Temporal Patterns**: Monthly aggregations, seasonal baseline

### Data Limitations
- **Synthetic Origin**: Generated data may not capture all real-world edge cases
- **Limited Geography**: Single regional context, limited transferability
- **Short Time Horizon**: 3-month window insufficient for long-term trends
- **No External Data**: Weather APIs, traffic patterns, or road quality not integrated

---

## Feature Engineering & Definitions

### Exposure Metrics
- **`miles`**: Total miles driven per month (converted from km)
- **`trip_count`**: Number of discrete trips completed

### Driving Behavior Features
- **`harsh_brake_rate_per_100mi`**: Rate of hard braking events per 100 miles
- **`harsh_accel_rate_per_100mi`**: Rate of hard acceleration events per 100 miles  
- **`harsh_lateral_rate_per_100mi`**: Rate of sharp turns/lane changes per 100 miles
- **`volatility_jerk_p95`**: 95th percentile of jerk (acceleration smoothness)

### Speed-Related Risk
- **`speeding_pct_over_5`**: Percentage of time driving >5 mph over speed limit
- **`speeding_pct_over_10`**: Percentage of time driving >10 mph over speed limit
- **`speeding_pct_over_15`**: Percentage of time driving >15 mph over speed limit

### Environmental Exposure
- **`night_pct`**: Percentage of driving during nighttime hours
- **`wet_pct`**: Percentage of driving in wet weather conditions

### Road Type Distribution
- **`pct_highway`**: Percentage of miles on highways/interstates
- **`pct_arterial`**: Percentage of miles on arterial roads
- **`pct_local`**: Percentage of miles on local/residential streets

---

## Model Architecture & Training

### Model Ensemble
Two complementary approaches trained on identical feature sets:

#### 1. Generalized Linear Model (GLM)
- **Family**: Tweedie distribution (variance_power=1.5)
- **Link Function**: Log link
- **Rationale**: Industry-standard actuarial approach, regulatory-friendly
- **Implementation**: statsmodels GLM with maximum likelihood estimation

#### 2. LightGBM Gradient Boosting
- **Objective**: Regression (MAE optimization)
- **Constraints**: Monotonic increasing on risk-driving features
- **Regularization**: Early stopping, max_depth=6, num_leaves=31
- **Rationale**: Captures non-linear relationships while preserving business logic

### Training Strategy
- **Data Split**: Temporal split using last month (2024-03) as holdout test set
- **Training Data**: First 2 months (200 user-months)
- **Test Data**: Final month (100 user-months)
- **Fallback**: 80/20 user-based split if insufficient temporal data

### Monotonic Constraints (LightGBM)
Risk-increasing features constrained to monotonic relationships:
- `speeding_pct_over_10` ↗️ (higher speeding → higher risk)
- `speeding_pct_over_15` ↗️ (excessive speeding → higher risk)  
- `night_pct` ↗️ (night driving → higher accident risk)
- `harsh_brake_rate_per_100mi` ↗️ (aggressive braking → higher risk)
- `harsh_lateral_rate_per_100mi` ↗️ (erratic steering → higher risk)
- `volatility_jerk_p95` ↗️ (poor smoothness → higher risk)

**Rationale**: Ensures model predictions align with actuarial knowledge and regulatory expectations, preventing counterintuitive relationships that could arise from data artifacts.

---

## Model Performance & Validation

### Primary Metrics
| Metric | GLM (Tweedie) | LightGBM | Winner |
|--------|---------------|----------|--------|
| **MAE** | $5,615.24 | $5,206.94 | LightGBM |
| **R²** | -0.2431 | -0.0208 | LightGBM |
| **Gini** | 0.2625 | 0.2409 | GLM |

### Detailed Evaluation

#### Prediction Accuracy
- **Mean Absolute Error**: LightGBM achieves 7% lower MAE than GLM
- **R² Performance**: Both models struggle with explained variance (negative R²)
- **MAPE**: Extremely high due to zero-inflation in loss costs

#### Ranking Performance  
- **Gini Coefficient**: GLM slightly better at rank-ordering risk (0.26 vs 0.24)
- **AUC Analysis**: Based on binary "has_claim" proxy (loss_cost > 0)

#### Calibration Analysis
- **Decile Plots**: Systematic over/under-prediction patterns identified
- **Lift Charts**: Both models provide meaningful risk concentration in top deciles
- **Business Impact**: Top 30% of predicted risk captures 60%+ of actual losses

### Model Limitations
- **Negative R²**: Models explain less variance than simple mean prediction
- **High MAPE**: Zero-inflation in target variable inflates percentage errors  
- **Limited Data**: 300 observations insufficient for complex pattern detection
- **Synthetic Bias**: Generated data may lack realistic correlations

---

## Explainability & Interpretability

### SHAP (SHapley Additive exPlanations) Framework
- **Global Importance**: Feature rankings across entire test set
- **Local Explanations**: Per-user-month risk factor decomposition
- **Output Format**: Top-5 positive risk contributors per prediction

### Reason Code Generation
Each prediction accompanied by human-readable explanations:
```json
{
  "user_id": "user_0042",
  "month": "2024-03", 
  "top_reasons": [
    "speeding_pct_over_10 (+0.234)",
    "night_pct (+0.156)",
    "harsh_brake_rate_per_100mi (+0.089)"
  ]
}
```

### Business Value
- **Customer Communication**: Transparent premium adjustment explanations
- **Regulatory Compliance**: Auditable decision-making process
- **Model Debugging**: Identification of unexpected feature importance

### Interpretability Constraints
- **Tree-Based SHAP**: Only available for LightGBM model
- **GLM Coefficients**: Linear model provides inherent coefficient interpretability
- **Feature Interactions**: SHAP captures complex feature interactions in LightGBM

---

## Bias, Fairness & Ethical Considerations

### Protected Attribute Exclusion
**Deliberately Excluded Variables**:
- Age, gender, race, ethnicity
- Precise geographic location (zip code level)
- Income proxies, education level
- Vehicle value, credit scores

### Fairness Safeguards
- **Coarse Geospatial**: Regional-level only to prevent redlining
- **Behavior-Focused**: Models only driving behavior, not demographic characteristics
- **Transparent Features**: All input variables directly related to driving risk

### Potential Bias Sources
- **Digital Divide**: Smartphone-based data may exclude certain populations
- **Telematics Opt-In**: Self-selection bias toward tech-savvy, privacy-comfortable users
- **Geographic Concentration**: Model trained on limited geographic diversity
- **Temporal Bias**: Short training window may not capture seasonal driving patterns

### Disparate Impact Monitoring
- **Regular Audits**: Monthly analysis of prediction distributions across demographic groups
- **Threshold Analysis**: Equal error rates across protected classes
- **Appeal Process**: Manual review mechanism for disputed risk assessments

---

## Model Monitoring & Maintenance

### Performance Drift Detection
- **Feature Drift**: Monthly distribution comparison using KS tests
- **Prediction Drift**: Target variable distribution stability monitoring
- **Concept Drift**: Model performance degradation alerts (MAE increase >10%)

### Seasonal Adjustments
- **Winter Driving**: Expected changes in harsh event rates, night exposure
- **Holiday Patterns**: Trip frequency variations during peak travel periods
- **Economic Cycles**: Potential changes in driving behavior during recessions

### Retraining Triggers
- **Performance Degradation**: MAE increase >15% sustained over 2 months
- **Data Volume**: Accumulation of 500+ new user-months
- **Feature Importance Shift**: Major changes in SHAP global rankings
- **Business Logic Changes**: New regulatory requirements or risk factors

### Model Versioning
- **Quarterly Reviews**: Performance assessment and improvement opportunities
- **A/B Testing**: Champion/challenger framework for model updates
- **Rollback Procedures**: Automated reversion if new model underperforms

### Regulatory Compliance
- **Actuarial Review**: Annual validation by qualified actuaries
- **Documentation**: Comprehensive model development and validation records
- **Audit Trail**: Complete lineage from raw data to final predictions

---

## Limitations & Known Issues

### Technical Limitations
1. **Limited Training Data**: 300 user-months insufficient for robust ML
2. **Synthetic Data Bias**: Generated patterns may not reflect real-world complexity
3. **Feature Engineering**: Manual feature selection without systematic validation
4. **Model Selection**: Limited hyperparameter optimization due to small dataset

### Business Limitations  
1. **Geographic Scope**: Single-region model limits national applicability
2. **Temporal Coverage**: 3-month window insufficient for seasonal patterns
3. **Vehicle Types**: No differentiation between car types, motorcycle, commercial vehicles
4. **Driver Experience**: No adjustment for years of driving experience

### Statistical Limitations
1. **Negative R²**: Models perform worse than baseline mean prediction
2. **Zero-Inflation**: High frequency of zero loss months complicates modeling
3. **Outlier Sensitivity**: Limited robust statistical techniques employed
4. **Cross-Validation**: Temporal split only, no k-fold validation performed

---

## Deployment & Integration

### Production Architecture
- **Batch Scoring**: Monthly prediction generation for entire portfolio
- **Real-Time API**: Individual user risk score on-demand
- **Model Ensemble**: Combined GLM/LightGBM predictions using weighted average

### Business Integration
- **Pricing Engine**: Risk scores feed into premium calculation with caps/floors
- **Underwriting**: High-risk flag generation for manual review
- **Customer Portal**: Risk score explanations and improvement recommendations

### Operational Requirements
- **Compute Resources**: Minimal (models train in <1 minute on laptop)
- **Storage**: <100MB for model artifacts and feature store
- **Latency**: Sub-second prediction response times required

---

## Appendix

### Model Artifacts
- **GLM Model**: `./models/glm.pkl` (statsmodels GLM object)
- **LightGBM Model**: `./models/lgbm.pkl` (LightGBM booster)
- **Feature Definitions**: `./docs/data_dictionary.md`
- **Performance Report**: `./docs/metrics/model_compare.md`

### Reproducibility
- **Random Seed**: 42 (fixed across all components)
- **Dependencies**: `requirements.txt` with pinned versions
- **Code Repository**: Complete pipeline in `src/` directory
- **Data Generation**: Deterministic synthetic data creation

### Contact Information
- **Model Owner**: InsurityAI Data Science Team
- **Business Stakeholder**: Pricing & Underwriting Department  
- **Technical Support**: [internal contact information]
- **Regulatory Contact**: Chief Actuary Office

---

*This model card follows ML documentation best practices and should be updated with each model version. For technical implementation details, see the complete codebase in the project repository.*