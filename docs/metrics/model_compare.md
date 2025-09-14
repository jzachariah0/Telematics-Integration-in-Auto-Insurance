# Model Performance Comparison

## Overview
This report compares the performance of GLM (Tweedie) and LightGBM models for predicting insurance loss cost.

## Model Metrics

### GLM (Tweedie) Results
- **MAE**: 6533.90
- **MAPE**: 27494356971125.96%
- **R²**: 0.0279
- **Gini**: 0.3019

### LightGBM Results  
- **MAE**: 6908.88
- **MAPE**: 31905770259812.51%
- **R²**: 0.0313
- **Gini**: 0.3059

## Model Comparison

| Metric | GLM | LightGBM | Better Model |
|--------|-----|----------|--------------|
| MAE | 6533.90 | 6908.88 | GLM |
| MAPE | 27494356971125.96% | 31905770259812.51% | GLM |
| R² | 0.0279 | 0.0313 | LightGBM |
| Gini | 0.3019 | 0.3059 | LightGBM |

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
