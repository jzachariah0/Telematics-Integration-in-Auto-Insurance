# State Insurance Department Filing Brief
## Telematics-Based Rating Factor Implementation

**Filing Date**: September 12, 2025  
**Company**: InsurityAI Demonstration  
**Product**: Personal Auto Insurance - Telematics Enhancement  
**Effective Date**: [Pending Regulatory Approval]  
**Filing Type**: New Rating Factor Implementation

---

## Telematics Rating Factor Definition

### Factor Construction
The telematics rating factor is defined as the **ratio of individual expected loss cost to book average expected loss cost**, derived from behavioral driving data collected via smartphone sensors. The factor represents the relative risk adjustment applied to base premium rates.

**Mathematical Definition**:
```
Telematics Factor = (Individual Expected Loss Cost) / (Book Average Expected Loss Cost)
```

**Base Calculation**:
- Individual expected loss cost determined through machine learning models trained on driving behavior features
- Book average represents the portfolio-wide expected loss cost for the rating class
- Resulting factor applied multiplicatively to manual premium before other adjustments

### Smoothing Methodology
To ensure rating stability and prevent volatile premium swings, the telematics factor incorporates **Exponentially Weighted Moving Average (EWMA) smoothing**:

- **Smoothing Parameter (α)**: 0.3 weighting on current period observations
- **Historical Weight**: 0.7 weighting on prior smoothed factor
- **Minimum Observation Period**: 90 days of driving data required before factor application
- **Cold Start**: New customers receive neutral factor (1.00) until sufficient data available

### Risk Concentration Caps
- **Monthly Cap**: ±10% maximum change in telematics factor per month
- **Quarterly Cap**: ±25% maximum change in telematics factor per quarter
- **Annual Floor/Ceiling**: Factor constrained between 0.75 and 1.25 (±25% of neutral)
- **Grace Period**: 30-day advance notice before adverse rating changes take effect

---

## Update Cadence and Implementation

### Calculation Frequency
- **Model Scoring**: Real-time behavioral feature updates as driving data received
- **Factor Recalculation**: Monthly on policy anniversary date
- **Premium Application**: Next renewal cycle following factor update
- **Emergency Adjustments**: Quarterly for significant risk profile changes

### Implementation Timeline
- **Data Collection Period**: Minimum 90 days of qualifying trips (≥1 mile, ≥5 minutes)
- **Factor Stabilization**: 6-month observation period for reliable factor determination
- **Renewal Integration**: Telematics factor applied at policy renewal alongside other rating variables

---

## Models and Governance Framework

### Primary Model Architecture

**Baseline Model: Generalized Linear Model (GLM)**
- **Distribution**: Tweedie (compound Poisson-Gamma) for insurance loss modeling
- **Link Function**: Log link ensuring positive predictions
- **Features**: 14 behavioral driving metrics aggregated monthly
- **Training Data**: Historical loss experience correlated with telematics features
- **Validation**: Out-of-time testing with 80/20 train/validation split

**Monitoring Model: LightGBM Gradient Boosting**
- **Purpose**: Secondary validation and model performance monitoring
- **Constraints**: Monotonic constraints ensuring logical feature relationships
- **Ensemble Approach**: GLM primary for pricing, LightGBM for validation and drift detection
- **Performance Comparison**: Monthly comparison between GLM and LightGBM predictions

### Model Governance and Validation

**Documentation Requirements**:
- **Model Development Documentation**: Comprehensive model development reports with feature engineering, selection methodology, and performance validation
- **Model Card**: Standardized documentation including intended use, training data, performance metrics, fairness considerations, and limitations
- **Version Control**: Git-based versioning for all model code, data processing pipelines, and documentation

**Ongoing Monitoring**:
- **Performance Monitoring**: Monthly tracking of prediction accuracy, calibration, and discrimination
- **Population Stability**: Quarterly assessment of feature distributions and model population stability index
- **Bias Testing**: Semi-annual fairness assessments across protected characteristics where data available
- **Model Refresh**: Annual model retraining with updated loss experience and feature optimization

**Validation Standards**:
- **Independent Validation**: Third-party actuarial review of model development and implementation
- **Backtesting**: Historical performance validation across multiple time periods
- **Stress Testing**: Model performance under extreme scenarios and edge cases

---

## Consumer Transparency and Protections

### In-Application Transparency

**Real-Time Feedback**:
- **Driving Score Display**: Monthly behavioral scores with trend indicators
- **Factor Explanation**: Clear presentation of current telematics factor and impact on premium
- **Feature Contributions**: SHAP (SHapley Additive exPlanations) values showing individual behavioral factor contributions to risk score

**Reason Code System**:
- **Primary Reason Codes**: Top 3 behavioral factors contributing to risk adjustment (e.g., "Speed", "Hard Braking", "Night Driving")
- **Directional Impact**: Clear indication whether each factor increases or decreases risk assessment
- **Improvement Guidance**: Specific recommendations for driving behavior modifications to improve factor

### Consumer Rights and Dispute Resolution

**Data Access Rights**:
- **Trip Data Access**: Customers can view and download all collected driving data through mobile application
- **Factor History**: Historical telematics factors and premium impacts available for 24-month period
- **Data Correction**: Process for customers to dispute and correct erroneous trip classifications

**Dispute and Appeal Workflow** *(Production Implementation Pending)*:
- **Level 1 - Automated Review**: Algorithm-based review of disputed trips with potential automatic correction
- **Level 2 - Manual Review**: Human underwriter review of complex disputes with supporting documentation
- **Level 3 - Independent Appeal**: Third-party arbitration for unresolved disputes over rating decisions
- **Timeline**: 30-day initial response, 60-day resolution target for complex cases

**Consumer Protections**:
- **Opt-Out Option**: Customers may discontinue telematics participation with 30-day notice (return to manual rates)
- **Data Deletion**: Complete removal of telematics data upon opt-out or policy cancellation
- **Rate Stability**: Grace period protections preventing sudden premium increases due to short-term driving pattern changes

---

## Technical Implementation and Compliance

### Data Collection and Privacy
- **Consent Framework**: Explicit opt-in consent required for telematics data collection and processing
- **Data Minimization**: Collection limited to driving behavior metrics essential for risk assessment
- **Geographic Privacy**: GPS coordinates processed to coarse geographic regions (≥1km grid cells)
- **Retention Limits**: Raw driving data retained maximum 90 days; aggregated behavioral features retained 24 months

### Regulatory Compliance
- **Rate Filing Compliance**: All telematics factors subject to standard rate filing and approval processes
- **Discrimination Testing**: Regular analysis ensuring telematics factors do not serve as proxies for prohibited rating characteristics
- **Audit Trail**: Complete documentation of factor calculations, model decisions, and premium applications for regulatory examination
- **Emergency Procedures**: Defined processes for immediate model suspension in case of systematic errors or bias detection

---

## Filing Summary and Regulatory Request

This filing requests approval for implementation of telematics-based rating factors that enhance risk assessment accuracy while maintaining strong consumer protections and transparency. The proposed methodology balances actuarial soundness with rate stability through conservative smoothing and capping mechanisms.

**Key Filing Elements**:
- ✓ Actuarially sound factor definition with demonstrated loss correlation
- ✓ Conservative update cadence with robust stability mechanisms  
- ✓ Comprehensive model governance with independent validation
- ✓ Strong consumer transparency and dispute resolution framework
- ✓ Privacy-by-design data handling with regulatory compliance

**Regulatory Review Period**: 90 days requested for comprehensive review and approval  
**Anticipated Effective Date**: January 1, 2026 (following approval)  
**Supporting Documentation**: Model development reports, validation studies, and consumer testing results available upon request

---

*This filing brief provides a summary of the telematics rating factor implementation. Complete technical documentation, actuarial analyses, and consumer impact studies are available for detailed regulatory review.*