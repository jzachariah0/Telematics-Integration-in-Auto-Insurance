# Key Performance Indicators (KPIs)
## InsurityAI Telematics-Based Risk Assessment System

**Version**: 1.0  
**Date**: September 12, 2025  
**Review Frequency**: Monthly  
**Owner**: Product Analytics Team

---

## Executive Summary

This document defines the key performance indicators (KPIs) for measuring the success of our telematics-based insurance risk assessment system. Metrics are organized into three primary categories: **Actuarial Performance**, **Customer Experience**, and **Data Integrity**. Each KPI includes measurement methodology, target thresholds appropriate for proof-of-concept deployment, and monitoring frequency.

---

## 1. Actuarial Performance Metrics

### 1.1 Loss Ratio Improvement

**Definition**: Improvement in loss ratio (claims cost / premium revenue) for telematics participants vs. control group.

**Measurement Methodology**:
```
Loss Ratio Improvement = (Control_Loss_Ratio - Telematics_Loss_Ratio) / Control_Loss_Ratio × 100%

Where:
- Control_Loss_Ratio = Traditional rating loss ratio
- Telematics_Loss_Ratio = Telematics-adjusted rating loss ratio
- Minimum 6 months of data for statistical significance
```

**Data Sources**:
- Policy administration system (premium data)
- Claims management system (loss data)
- Telematics platform (participation flags)

**POC Target Thresholds**:
- **Green (Excellent)**: ≥8% improvement
- **Yellow (Acceptable)**: 3-7% improvement  
- **Red (Concerning)**: <3% improvement

**Monitoring Frequency**: Monthly with quarterly statistical testing
**Sample Size**: Minimum 500 policies per cohort for 95% confidence

### 1.2 Claim Frequency Reduction

**Definition**: Reduction in claim frequency (claims per 100 policy years) for telematics participants.

**Measurement Methodology**:
```
Frequency Reduction = (Control_Frequency - Telematics_Frequency) / Control_Frequency × 100%

Claim Frequency = (Number of Claims / Policy Years) × 100

Segmentation:
- By claim type: Collision, Comprehensive, Liability
- By severity band: <$1K, $1K-$5K, $5K-$25K, >$25K
- By customer tenure: <6mo, 6-12mo, 12-24mo, >24mo
```

**Data Sources**:
- Claims system with FNOL (First Notice of Loss) timestamps
- Policy effective dates and coverage periods
- Telematics participation start dates

**POC Target Thresholds**:
- **Green (Excellent)**: ≥15% reduction in collision frequency
- **Yellow (Acceptable)**: 5-14% reduction in collision frequency
- **Red (Concerning)**: <5% reduction or frequency increase

**Monitoring Frequency**: Monthly trending with quarterly significance testing
**Minimum Observation Period**: 12 months for mature assessment

### 1.3 Model Calibration Stability

**Definition**: Consistency of model predictions vs. actual outcomes across risk deciles and time periods.

**Measurement Methodology**:
```
Calibration Error = Σ|Predicted_i - Actual_i| / n

Where:
- Predicted_i = Model predicted loss cost for decile i
- Actual_i = Observed loss cost for decile i  
- n = Number of deciles (typically 10)

Hosmer-Lemeshow Test: χ² test for goodness of fit
- H0: Model is well-calibrated
- Significance level: α = 0.05
```

**Model Drift Monitoring**:
```
Population Stability Index (PSI) = Σ(Actual% - Expected%) × ln(Actual% / Expected%)

Where:
- Expected% = Feature distribution in training data
- Actual% = Feature distribution in current scoring data
```

**Data Sources**:
- Model scoring outputs with timestamps
- Actual loss development from claims system
- Feature distributions from telematics platform

**POC Target Thresholds**:
- **Green (Stable)**: Calibration error <10%, PSI <0.1
- **Yellow (Monitoring)**: Calibration error 10-20%, PSI 0.1-0.25
- **Red (Recalibration Needed)**: Calibration error >20%, PSI >0.25

**Monitoring Frequency**: Weekly for drift detection, monthly for calibration assessment

---

## 2. Customer Experience Metrics

### 2.1 Customer Retention Rate

**Definition**: Percentage of telematics participants who renew their policies vs. control group.

**Measurement Methodology**:
```
Retention Rate = (Renewed Policies / Eligible for Renewal) × 100%

Retention Lift = Telematics_Retention_Rate - Control_Retention_Rate

Cohort Analysis:
- Time-based: 6mo, 12mo, 24mo retention curves
- Segment-based: Age, geography, prior claims, risk score
- Behavior-based: High/medium/low engagement with app
```

**Data Sources**:
- Policy administration system (renewal data)
- Telematics platform (participation metrics)
- Customer relationship management system

**POC Target Thresholds**:
- **Green (Excellent)**: ≥3 percentage points improvement vs. control
- **Yellow (Acceptable)**: 0-3 percentage points improvement
- **Red (Concerning)**: Negative retention impact

**Monitoring Frequency**: Monthly with quarterly cohort analysis
**Baseline Establishment**: 12 months pre-telematics historical data

### 2.2 Telematics Opt-In Rate

**Definition**: Percentage of eligible customers who enroll in telematics program when offered.

**Measurement Methodology**:
```
Opt-In Rate = (Telematics Enrollments / Telematics Offers) × 100%

Funnel Analysis:
1. Telematics Offer Presented
2. Customer Clicks/Engages with Offer  
3. App Download Initiated
4. App Installation Completed
5. Initial Trip Data Collected
6. 30-Day Active Participation

Conversion Rate = Stage_n / Stage_1 × 100%
```

**Segmentation Analysis**:
- Demographics: Age, gender, geography
- Policy characteristics: Coverage limits, deductibles, multi-policy
- Channel: Agent, direct, online, mobile
- Timing: New business vs. renewal offer

**Data Sources**:
- Marketing campaign management system
- Mobile app analytics platform
- Telematics platform enrollment data

**POC Target Thresholds**:
- **Green (Strong Adoption)**: ≥35% opt-in rate
- **Yellow (Moderate Adoption)**: 20-34% opt-in rate
- **Red (Low Adoption)**: <20% opt-in rate

**Monitoring Frequency**: Weekly for optimization, monthly for reporting

### 2.3 Customer Complaint Rate

**Definition**: Telematics-related customer complaints per 1,000 participants vs. overall complaint baseline.

**Measurement Methodology**:
```
Complaint Rate = (Telematics Complaints / Telematics Participants) × 1,000

Complaint Categories:
- Pricing/Rating: Premium increases, factor disputes
- Privacy/Data: Data collection concerns, opt-out requests  
- Technology: App issues, device problems, data accuracy
- Service: Customer service quality, resolution time

Severity Classification:
- Level 1: Inquiry/Information request
- Level 2: Service complaint requiring follow-up
- Level 3: Formal complaint requiring investigation
- Level 4: Regulatory complaint or legal escalation
```

**Data Sources**:
- Customer service ticketing system
- Regulatory complaint tracking
- Social media monitoring tools
- App store reviews and ratings

**POC Target Thresholds**:
- **Green (Low Complaints)**: <5 complaints per 1,000 participants
- **Yellow (Moderate Complaints)**: 5-15 complaints per 1,000 participants
- **Red (High Complaints)**: >15 complaints per 1,000 participants

**Monitoring Frequency**: Daily for escalation monitoring, weekly for trending

### 2.4 Net Promoter Score (NPS) Proxy

**Definition**: Customer satisfaction and advocacy measured through telematics-specific survey and behavioral proxies.

**Measurement Methodology**:
```
NPS = %Promoters - %Detractors

Where:
- Promoters: Survey score 9-10 (recommend telematics to friends)
- Passives: Survey score 7-8 (satisfied but not enthusiastic)
- Detractors: Survey score 0-6 (unlikely to recommend)

Behavioral Proxies:
- App engagement: Daily/weekly active users
- Feature usage: Dashboard views, trip reviews, coaching uptake
- Referral behavior: Friend/family enrollments from participant referrals
- Voluntary opt-in extensions: Renewal without prompting
```

**Survey Deployment**:
- Timing: 90 days post-enrollment, annually thereafter
- Sample size: 25% of participant base per quarter
- Channel: In-app survey, email follow-up, SMS option
- Incentive: Premium credit or gift card for completion

**Data Sources**:
- Customer satisfaction survey platform
- Mobile app analytics (engagement metrics)
- Referral tracking system
- Renewal behavior analysis

**POC Target Thresholds**:
- **Green (High Satisfaction)**: NPS ≥50
- **Yellow (Moderate Satisfaction)**: NPS 20-49
- **Red (Low Satisfaction)**: NPS <20

**Monitoring Frequency**: Quarterly survey deployment, monthly behavioral proxy tracking

---

## 3. Data Integrity and Security Metrics

### 3.1 Fraud and Tampering Detection

**Definition**: Identification and flagging of suspicious data patterns that may indicate fraudulent activity or device tampering.

**Detection Categories and Thresholds**:

#### **Device Spoofing Detection**
```
GPS Anomaly Score = Σ(Speed_Impossibility + Location_Jump + Altitude_Inconsistency)

Thresholds:
- Speed Impossibility: >150 mph sustained for >30 seconds
- Location Jump: >50 mile instantaneous position change
- Altitude Inconsistency: >1000 ft elevation change without highway gradient
```

#### **Behavioral Gaming Detection**
```
Gaming Risk Score = Weighted_Sum(Behavior_Consistency + Pattern_Anomaly + Timing_Manipulation)

Indicators:
- Perfect driving scores (>98th percentile) for >6 months
- Sudden dramatic behavior improvement (>3 standard deviations)
- Driving patterns inconsistent with claimed demographics
- Trip timing manipulation (start/stop gaming)
```

#### **Technical Tampering Detection**
```
Technical Anomaly Score = Device_Integrity + Data_Quality + Network_Consistency

Red Flags:
- Sensor readings outside physical possibility ranges
- Consistent perfect accelerometer readings (device not in vehicle)
- Network connectivity patterns inconsistent with claimed trips
- Multiple device IDs associated with single policy
```

**Data Sources**:
- Telematics platform raw sensor logs
- Device authentication and integrity checks
- Network connectivity and geolocation services
- Customer policy and demographic information

**POC Target Thresholds**:
- **Green (Low Risk)**: <2% of participants flagged for investigation
- **Yellow (Moderate Risk)**: 2-5% flagged, <0.5% confirmed fraud
- **Red (High Risk)**: >5% flagged or >0.5% confirmed fraud

**Response Protocols**:
- **Automated Flagging**: Immediate scoring suspension for high-risk scores
- **Human Review**: Weekly review of moderate-risk cases
- **Investigation Process**: 30-day investigation period with customer notification
- **Resolution**: Factor adjustment, account suspension, or fraud referral

**Monitoring Frequency**: Real-time for severe anomalies, daily for pattern detection

---

## 4. Operational Performance Metrics

### 4.1 Data Quality and Completeness

**Definition**: Percentage of telematics participants with sufficient, high-quality data for risk assessment.

**Measurement Methodology**:
```
Data Sufficiency Rate = (Participants with ≥20 trips/month) / Total Active Participants × 100%

Data Quality Score = Weighted_Average(GPS_Accuracy + Sensor_Reliability + Trip_Completeness)

Where:
- GPS_Accuracy: <10m average error, <5% missing coordinates
- Sensor_Reliability: <1% impossible readings, consistent device orientation
- Trip_Completeness: Start/end points captured, duration >2 minutes, distance >0.5 miles
```

**POC Target Thresholds**:
- **Green (High Quality)**: ≥85% participants with sufficient data quality
- **Yellow (Moderate Quality)**: 70-84% sufficient data quality
- **Red (Poor Quality)**: <70% sufficient data quality

### 4.2 System Availability and Performance

**Definition**: Uptime and response time metrics for telematics data collection and processing systems.

**Key Metrics**:
- **Data Collection Uptime**: ≥99.5% availability
- **Processing Latency**: <15 minutes from trip end to feature calculation
- **API Response Time**: <500ms for dashboard queries
- **Mobile App Crash Rate**: <0.1% of sessions

**POC Target Thresholds**:
- **Green (Excellent)**: All metrics within target
- **Yellow (Acceptable)**: 1-2 metrics slightly below target
- **Red (Unacceptable)**: ≥3 metrics below target or critical system failure

---

## 5. Business Impact Metrics

### 5.1 Revenue Impact

**Definition**: Additional premium revenue generated through improved risk selection and retention.

**Measurement Methodology**:
```
Revenue Lift = (Telematics_Premium_per_Policy - Control_Premium_per_Policy) × Policy_Count

Components:
- Risk-based pricing adjustments (good drivers get discounts)
- Retention value (reduced acquisition costs)
- Portfolio improvement (adverse selection reduction)
```

**POC Target Thresholds**:
- **Green (Positive Impact)**: ≥2% revenue increase per telematics policy
- **Yellow (Neutral Impact)**: ±2% revenue impact
- **Red (Negative Impact)**: >2% revenue decrease

### 5.2 Cost Efficiency

**Definition**: Cost per policy for telematics program vs. value generated.

**Cost Components**:
- Technology platform and development
- Customer acquisition and onboarding
- Data processing and storage
- Customer support and operations

**POC Target Thresholds**:
- **Green (Efficient)**: ROI ≥3:1 within 24 months
- **Yellow (Breakeven)**: ROI 1:1 to 3:1
- **Red (Inefficient)**: ROI <1:1

---

## 6. Monitoring Dashboard and Reporting

### 6.1 Executive Dashboard (Monthly)

**Red/Yellow/Green Status Indicators**:
- Overall program health score
- Key metric trends and targets
- Risk flags requiring attention
- Regulatory compliance status

### 6.2 Operational Dashboard (Weekly)

**Detailed Metrics**:
- Data quality and system performance
- Customer experience indicators
- Fraud detection alerts
- Model performance monitoring

### 6.3 Deep Dive Analytics (Quarterly)

**Comprehensive Analysis**:
- Cohort performance analysis
- Competitive benchmarking
- ROI and business case validation
- Strategic recommendations and roadmap updates

---

## 7. Alerting and Escalation Procedures

### 7.1 Automated Alerts

**Critical (Immediate Response)**:
- System downtime >30 minutes
- Data quality <50%
- Fraud rate >1%
- Customer complaint spike >5x baseline

**Warning (24-hour Response)**:
- KPI trending toward red threshold
- Model performance degradation
- Customer satisfaction decline
- Regulatory inquiry received

### 7.2 Escalation Matrix

| Severity | Response Time | Owner | Escalation |
|----------|---------------|--------|------------|
| Critical | 1 hour | On-call Engineer | CTO + CPO |
| High | 4 hours | Product Manager | VP Product |
| Medium | 24 hours | Analytics Team | Director Analytics |
| Low | 1 week | Data Analyst | Team Lead |

---

## 8. Success Criteria for POC Graduation

**Minimum Thresholds for Production Deployment**:

✅ **Actuarial Performance**: 
- Loss ratio improvement ≥5%
- Claim frequency reduction ≥10%
- Model calibration error <15%

✅ **Customer Experience**:
- Retention improvement ≥2 percentage points
- Opt-in rate ≥25%
- Complaint rate <10 per 1,000 participants
- NPS ≥30

✅ **Data Integrity**:
- Fraud detection rate <3%
- Data quality ≥80%
- System uptime ≥99%

✅ **Business Impact**:
- Revenue lift ≥1%
- ROI pathway to 2:1 within 36 months

**POC Duration**: 12-18 months with quarterly go/no-go reviews

---

*This KPI framework provides comprehensive measurement capabilities for demonstrating telematics program value while maintaining appropriate thresholds for proof-of-concept validation. Regular review and adjustment of targets based on actual performance and market conditions is recommended.*