# InsurityAI – Telematics Dashboard for Auto Insurance

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive telematics-based insurance platform that uses driving behavior data to assess risk and calculate personalized premiums. Built with modern machine learning techniques and regulatory compliance in mind.

**Licensed under MIT License** - See LICENSE file for details.

## Features

- **Advanced Risk Assessment**: 16 sophisticated risk features including contextual factors
- **Real-time Dashboard**: Interactive web interface for premium calculation and risk analysis
- **SHAP Explanations**: Transparent AI with clear explanations for risk factors
- **Regulatory Compliance**: Built following insurance industry standards
- **Contextual Risk Factors**: External data integration for crash density and theft risk
- **Multiple ML Models**: GLM and LightGBM ensemble for robust predictions

## Dashboard Preview

The platform provides an intuitive dashboard showing:
- Risk index and telematics factor calculations
- Top 5 risk factors with technical and plain English explanations
- Premium calculations (base vs. final)
- Risk trend visualization charts
- Regulatory compliance indicators

## Architecture

```
InsurityAI-Project/
├── bin/                       # Build and deployment scripts
│   ├── setup.sh              # Environment setup automation
│   ├── train.sh              # Complete ML pipeline
│   ├── serve.sh              # Dashboard server
│   ├── test.sh               # Test suite runner
│   └── quality.sh            # Code quality and linting checks
├── src/
│   ├── api/                  # FastAPI web server
│   │   ├── server.py         # Main API server
│   │   └── templates/        # Dashboard HTML templates
│   ├── features/             # Feature engineering pipeline
│   │   └── build_features.py # Enhanced 16-feature extraction
│   ├── models/               # ML model training and inference
│   │   └── train.py         # GLM + LightGBM ensemble training
│   └── pricing/              # Premium calculation engine
│       └── run_pricing.py   # Risk-based pricing with SHAP
├── data/
│   ├── raw/                  # Original telematics data
│   ├── features.parquet      # Engineered features (16 total)
│   ├── pricing_results.json  # Final premium calculations
│   └── reason_codes.jsonl   # SHAP explanations
├── models/                   # Trained model artifacts
│   ├── glm.pkl              # Generalized Linear Model
│   └── lgbm.pkl             # LightGBM Ensemble
├── docs/                     # Comprehensive documentation
│   ├── data_dictionary.md   # Feature definitions
│   ├── model_card.md        # Model documentation
│   ├── dpia.md              # Privacy impact assessment
│   └── metrics/             # Performance visualizations
├── tests/                    # Unit test suite
│   ├── test_pipeline.py     # Comprehensive pipeline tests
│   └── __init__.py          # Test runner
├── requirements.txt          # Pinned dependencies
├── .env.example             # Environment configuration template
└── CHANGELOG.md             # Release notes and version history
```

## Build Process

InsurityAI uses a standardized build process with automated scripts:

### `/bin/setup.sh` - Environment Setup
- Creates Python virtual environment
- Installs dependencies with version pinning
- Cross-platform compatibility (Windows/macOS/Linux)
- Dependency verification

### `/bin/train.sh` - ML Pipeline
- Feature engineering (16 sophisticated risk factors)
- Model training (GLM + LightGBM ensemble)
- Premium calculation with SHAP explanations
- Model validation and metrics generation

### `/bin/serve.sh` - Production Server
- Validates trained models exist
- Starts FastAPI dashboard on port 8001
- Background process management
- Health check endpoints

### `/bin/test.sh` - Quality Assurance
- Import validation for all modules
- Data structure integrity checks
- Pipeline parameter validation
- Model artifact verification

### `/bin/quality.sh` - Code Quality
- Code linting with flake8
- Import sorting validation
- Code formatting checks with black
- Type checking with mypy

## Installation & Setup

### Prerequisites

- Python 3.8 or higher
- pip package manager
- 4GB+ RAM (for model training)
- Git (for repository cloning)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/InsurityAI-Project.git
   cd InsurityAI-Project
   ```

2. **Environment Setup** (Automated)
   ```bash
   ./bin/setup.sh
   ```
   This script will:
   - Create a Python virtual environment
   - Install all dependencies with pinned versions
   - Verify the installation

3. **Train Models** (Complete Pipeline)
   ```bash
   ./bin/train.sh
   ```
   This runs the full ML pipeline:
   - Feature engineering (16 risk factors)
   - Model training (GLM + LightGBM)
   - Premium calculation with SHAP explanations

4. **Start Dashboard** (Production Server)
   ```bash
   ./bin/serve.sh
   ```
   
5. **Access the Dashboard**
   - **Main Interface**: `http://localhost:8001`
   - **API Documentation**: `http://localhost:8001/docs`
   - **Health Check**: `http://localhost:8001/health`

### Alternative: Manual Setup

If you prefer manual installation:

```bash
# Create virtual environment
python -m venv .venv

# Activate environment (Windows)
.venv\Scripts\activate
# Activate environment (macOS/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run pipeline manually
python src/features/build_features.py
python src/models/train.py
python src/pricing/run_pricing.py
python src/api/server.py
```

### Verification

Run the test suite to verify everything is working:

```bash
./bin/test.sh
```

This validates:
- All modules import correctly
- Required data files exist
- Models are properly trained
- API endpoints respond correctly

## Risk Features

The platform analyzes **16 comprehensive risk factors**:

### Core Driving Behaviors
- **Harsh Events**: Braking, acceleration, and lateral movement rates per 100 miles
- **Speeding**: Percentage of time speeding >5, >10, >15 mph over limit
- **Driving Volatility**: 95th percentile jerk measurements

### Environmental Factors
- **Night Driving**: Percentage of nighttime driving (higher risk)
- **Wet Weather**: Percentage of driving in wet conditions
- **Road Types**: Highway vs. arterial vs. local road exposure

### Contextual Risk Factors 
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

## Pricing Engine

The pricing system implements industry-standard practices:

1. **Base Premium**: $100/month starting point
2. **Risk Index**: Calculated from 16 features using trained models
3. **Telematics Factor**: Risk-based multiplier (0.7x - 1.3x range)
4. **Regulatory Caps**: 
   - Monthly: ±10% adjustment limit
   - Quarterly: ±25% adjustment limit
   - First Month: Grace period with minimal adjustment

### Formula
```
Final Premium = Base Premium × min(Telematics Factor, Regulatory Caps)
```

## API Endpoints

- `GET /` - Interactive dashboard
- `GET /health` - System health check
- `GET /api/pricing` - Pricing data for all users
- `GET /api/chart/{user_id}` - Risk trend visualization

## Data Pipeline

1. **Raw Data**: Simulated telematics trips with GPS, speed, and behavior events
2. **Feature Engineering**: 16 features extracted per user per month
3. **External Data**: Crash density and theft risk indices added
4. **Model Training**: GLM + LightGBM ensemble on historical data
5. **SHAP Analysis**: Reason codes generated for every prediction
6. **Pricing**: Risk-based premiums with regulatory compliance
7. **Dashboard**: Real-time visualization and explanations

## Regulatory Compliance

- **Transparency**: SHAP explanations for every risk assessment
- **Rate Caps**: Regulatory limits on premium adjustments
- **Fair Pricing**: Equal treatment with explainable risk factors
- **Data Privacy**: Anonymized user identifiers
- **Audit Trail**: Complete lineage from raw data to final premium

## Development

### Development Workflow

1. **Environment Setup**
   ```bash
   ./bin/setup.sh              # One-time setup
   source .venv/bin/activate   # Activate environment
   ```

2. **Development Cycle**
   ```bash
   # Make changes to code
   ./bin/test.sh               # Run tests
   ./bin/train.sh              # Retrain if needed
   ./bin/serve.sh              # Test dashboard
   ```

3. **Quality Assurance**
   ```bash
   ./bin/test.sh               # Full test suite
   python -m pytest tests/     # Alternative test runner
   ```

### Adding New Features

1. **Risk Features**: Update `src/features/build_features.py`
   - Add new feature extraction logic
   - Update feature documentation
   - Retrain models with `./bin/train.sh`

2. **Model Improvements**: Modify `src/models/train.py`
   - Hyperparameter optimization
   - New model architectures
   - Cross-validation enhancements

3. **Dashboard Updates**: Edit `src/api/templates/index.html`
   - UI/UX improvements
   - New visualization types
   - Feature explanation updates

### Testing Strategy

- **Unit Tests**: Import validation, parameter checks
- **Integration Tests**: End-to-end pipeline validation
- **Data Tests**: Feature engineering correctness
- **API Tests**: Endpoint functionality and performance

### Environment Configuration

Copy `.env.example` to `.env` and customize:

```bash
cp .env.example .env
# Edit .env with your specific configuration
```

Key configuration options:
- API settings (host, port, debug mode)
- Model hyperparameters
- Rate caps and regulatory settings
- Logging and monitoring

## Documentation

- **Data Dictionary**: `docs/data_dictionary.md` - Complete feature definitions
- **API Docs**: Available at `http://localhost:8001/docs` when server is running
- **Model Cards**: Detailed documentation of model performance and limitations

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Acknowledgments

- **SHAP**: For model explainability framework
- **LightGBM**: For gradient boosting capabilities
- **FastAPI**: For modern web API framework
- **Insurance Industry**: For regulatory guidance and best practices

## Support

For questions, issues, or contributions:
- Create an issue on GitHub
- Review the documentation in `/docs`
- Check the API documentation at `/docs` endpoint

**Contact:** Joshua Zachariah  
**Email:** joshuaszachariah@gmail.com  
**Phone:** 469-858-5532

---

**Built with ❤️ for transparent, fair, and data-driven insurance pricing**

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Copyright (c) 2025 Joshua Zachariah

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
