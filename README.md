# InsurityAI - Telematics Insurance Platform

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive telematics-based insurance platform that uses driving behavior data to assess risk and calculate personalized premiums. Built with modern machine learning techniques and regulatory compliance in mind.

## 🚀 Features

- **Advanced Risk Assessment**: 16 sophisticated risk features including contextual factors
- **Real-time Dashboard**: Interactive web interface for premium calculation and risk analysis
- **SHAP Explanations**: Transparent AI with clear explanations for risk factors
- **Regulatory Compliance**: Built following insurance industry standards
- **Contextual Risk Factors**: External data integration for crash density and theft risk
- **Multiple ML Models**: GLM and LightGBM ensemble for robust predictions

## 📊 Dashboard Preview

The platform provides an intuitive dashboard showing:
- Risk index and telematics factor calculations
- Top 5 risk factors with technical and plain English explanations
- Premium calculations (base vs. final)
- Risk trend visualization charts
- Regulatory compliance indicators

## 🏗️ Architecture

```
InsurityAI-Project/
├── src/
│   ├── api/                    # FastAPI web server
│   │   ├── server.py          # Main API server
│   │   └── templates/         # Dashboard HTML templates
│   ├── features/              # Feature engineering pipeline
│   │   └── build_features.py  # Enhanced 16-feature extraction
│   ├── models/                # ML model training and inference
│   │   └── train.py          # GLM + LightGBM ensemble training
│   ├── pricing/               # Premium calculation engine
│   │   └── run_pricing.py    # Risk-based pricing with SHAP
│   └── dashboard/             # Legacy dashboard components
├── data/
│   ├── raw/                   # Original telematics data
│   ├── processed/             # Cleaned and processed data
│   └── features/              # Engineered features (16 total)
├── models/                    # Trained model artifacts
├── charts/                    # Generated risk visualization charts
├── docs/                      # Documentation and data dictionary
└── infra/                     # Infrastructure and deployment
```

## 🔧 Installation & Setup

### Prerequisites

- Python 3.8 or higher
- pip package manager
- 4GB+ RAM (for model training)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/InsurityAI-Project.git
   cd InsurityAI-Project
   ```

2. **Install dependencies**
   ```bash
   pip install pandas numpy scikit-learn lightgbm fastapi uvicorn jinja2 matplotlib seaborn shap
   ```

3. **Build features (synthetic data)**
   ```bash
   python src/features/build_features.py
   ```

4. **Train models**
   ```bash
   python src/models/train.py
   ```

5. **Generate pricing data**
   ```bash
   python src/pricing/run_pricing.py
   ```

6. **Start the dashboard**
   ```bash
   python src/api/server.py
   ```

7. **Access the dashboard**
   Open your browser to: `http://localhost:8001`

## 📈 Risk Features

The platform analyzes **16 comprehensive risk factors**:

### Core Driving Behaviors
- **Harsh Events**: Braking, acceleration, and lateral movement rates per 100 miles
- **Speeding**: Percentage of time speeding >5, >10, >15 mph over limit
- **Driving Volatility**: 95th percentile jerk measurements

### Environmental Factors
- **Night Driving**: Percentage of nighttime driving (higher risk)
- **Wet Weather**: Percentage of driving in wet conditions
- **Road Types**: Highway vs. arterial vs. local road exposure

### Contextual Risk Factors ⭐
- **Crash Density Index**: External crash frequency data by location and road type
- **Theft Risk Index**: Vehicle theft probability based on geographic area

### Usage Metrics
- **Miles Driven**: Total monthly mileage
- **Trip Count**: Number of individual trips

## 🤖 Machine Learning Models

### GLM (Generalized Linear Model)
- **Purpose**: Base risk modeling with interpretable coefficients
- **Features**: All 16 risk factors with polynomial transformations
- **Output**: Continuous risk scores for premium calculation

### LightGBM (Gradient Boosting)
- **Purpose**: Advanced pattern recognition and non-linear relationships
- **Features**: Enhanced feature engineering with interaction terms
- **Output**: Probability distributions for claims frequency/severity

### SHAP Integration
- **Explainability**: Every prediction includes top 5 risk factor explanations
- **Transparency**: Both technical and plain English descriptions
- **Regulatory**: Meets insurance transparency requirements

## 💰 Pricing Engine

The pricing system implements industry-standard practices:

1. **Base Premium**: $100/month starting point
2. **Risk Index**: Calculated from 16 features using trained models
3. **Telematics Factor**: Risk-based multiplier (0.7x - 1.3x range)
4. **Regulatory Caps**: 
   - Monthly: ±30% adjustment limit
   - Quarterly: ±40% adjustment limit
   - First Month: Grace period with minimal adjustment

### Formula
```
Final Premium = Base Premium × min(Telematics Factor, Regulatory Caps)
```

## 🔍 API Endpoints

- `GET /` - Interactive dashboard
- `GET /health` - System health check
- `GET /api/pricing` - Pricing data for all users
- `GET /api/chart/{user_id}` - Risk trend visualization

## 📊 Data Pipeline

1. **Raw Data**: Simulated telematics trips with GPS, speed, and behavior events
2. **Feature Engineering**: 16 features extracted per user per month
3. **External Data**: Crash density and theft risk indices added
4. **Model Training**: GLM + LightGBM ensemble on historical data
5. **SHAP Analysis**: Reason codes generated for every prediction
6. **Pricing**: Risk-based premiums with regulatory compliance
7. **Dashboard**: Real-time visualization and explanations

## 🏛️ Regulatory Compliance

- **Transparency**: SHAP explanations for every risk assessment
- **Rate Caps**: Regulatory limits on premium adjustments
- **Fair Pricing**: Equal treatment with explainable risk factors
- **Data Privacy**: Anonymized user identifiers
- **Audit Trail**: Complete lineage from raw data to final premium

## 🛠️ Development

### Adding New Features

1. Update `src/features/build_features.py` with new feature logic
2. Retrain models with `python src/models/train.py`
3. Update feature descriptions in the dashboard
4. Regenerate pricing data

### Customizing the Dashboard

- Templates: `src/api/templates/index.html`
- Feature descriptions: Built into JavaScript mapping
- Styling: Basic HTML/CSS for simplicity

### Model Improvements

- Hyperparameter tuning in `src/models/train.py`
- Cross-validation and performance metrics
- A/B testing framework for pricing strategies

## 📝 Documentation

- **Data Dictionary**: `docs/data_dictionary.md` - Complete feature definitions
- **API Docs**: Available at `http://localhost:8001/docs` when server is running
- **Model Cards**: Detailed documentation of model performance and limitations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **SHAP**: For model explainability framework
- **LightGBM**: For gradient boosting capabilities
- **FastAPI**: For modern web API framework
- **Insurance Industry**: For regulatory guidance and best practices

## 📞 Support

For questions, issues, or contributions:
- Create an issue on GitHub
- Review the documentation in `/docs`
- Check the API documentation at `/docs` endpoint

---

**Built with ❤️ for transparent, fair, and data-driven insurance pricing**