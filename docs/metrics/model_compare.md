# Model Performance Comparison

## Overview
This report compares the performance of GLM (Tweedie) and LightGBM models for predicting insurance loss cost.

## Model Metrics

### GLM (Tweedie) Results
- **MAE**: 5615.24
- **MAPE**: 35864671689632.56%
- **R²**: -0.2431
- **Gini**: 0.2625

### LightGBM Results  
- **MAE**: 5206.94
- **MAPE**: 33571778377150.97%
- **R²**: -0.0208
- **Gini**: 0.2409

## Model Comparison

| Metric | GLM | LightGBM | Better Model |
|--------|-----|----------|--------------|
| MAE | 5615.24 | 5206.94 | LightGBM |
| MAPE | 35864671689632.56% | 33571778377150.97% | LightGBM |
| R² | -0.2431 | -0.0208 | LightGBM |
| Gini | 0.2625 | 0.2409 | GLM |

## Key Findings

- **Best Overall Model**: LightGBM (based on R²)
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
