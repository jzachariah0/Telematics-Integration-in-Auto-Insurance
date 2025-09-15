#!/usr/bin/env python3
"""
FastAPI server for InsurityAI pricing dashboard.

Provides REST API endpoints and an interactive web dashboard
for exploring pricing results and risk factors.
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
import uvicorn
import io
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="InsurityAI Pricing Dashboard", version="1.0.0")

# Global data storage
pricing_data = []
pricing_by_user = {}


def get_feature_mapping():
    """Return mapping of technical features to plain English explanations."""
    return {
        # Handle both underscore and space versions of feature names
        'night_pct': {
            'plain': 'You drive a lot at night, which increases risk due to reduced visibility',
            'technical': 'Percentage of driving during nighttime hours'
        },
        'night pct': {
            'plain': 'You drive a lot at night, which increases risk due to reduced visibility',
            'technical': 'Percentage of driving during nighttime hours'
        },
        'pct_highway': {
            'plain': 'Most of your driving is on highways, which reduces risk compared to city traffic',
            'technical': 'Percentage of miles driven on highways'
        },
        'pct highway': {
            'plain': 'Most of your driving is on highways, which reduces risk compared to city traffic',
            'technical': 'Percentage of miles driven on highways'
        },
        'wet_pct': {
            'plain': 'You drive in rain or wet conditions more often, which increases crash risk',
            'technical': 'Percentage of driving in wet weather conditions'
        },
        'wet pct': {
            'plain': 'You drive in rain or wet conditions more often, which increases crash risk',
            'technical': 'Percentage of driving in wet weather conditions'
        },
        'hard_accel_rate_per_100mi': {
            'plain': 'You accelerate aggressively more often, which increases accident risk',
            'technical': 'Rate of hard acceleration events per 100 miles'
        },
        'hard accel rate per 100mi': {
            'plain': 'You accelerate aggressively more often, which increases accident risk',
            'technical': 'Rate of hard acceleration events per 100 miles'
        },
        'harsh_lateral_rate_per_100mi': {
            'plain': 'You make sharp turns or lane changes often, which increases risk',
            'technical': 'Rate of harsh lateral movement events per 100 miles'
        },
        'harsh lateral rate per 100mi': {
            'plain': 'You make sharp turns or lane changes often, which increases risk',
            'technical': 'Rate of harsh lateral movement events per 100 miles'
        },
        'hard_brake_rate_per_100mi': {
            'plain': 'You brake hard more often, which may indicate following too closely',
            'technical': 'Rate of hard braking events per 100 miles'
        },
        'hard brake rate per 100mi': {
            'plain': 'You brake hard more often, which may indicate following too closely',
            'technical': 'Rate of hard braking events per 100 miles'
        },
        'speeding_pct_over_5': {
            'plain': 'You drive slightly over the speed limit (5+ mph) regularly',
            'technical': 'Percentage of time speeding >5 mph over limit'
        },
        'speeding pct over 5': {
            'plain': 'You drive slightly over the speed limit (5+ mph) regularly',
            'technical': 'Percentage of time speeding >5 mph over limit'
        },
        'speeding_pct_over_10': {
            'plain': 'You drive well over the speed limit (10+ mph) more often',
            'technical': 'Percentage of time speeding >10 mph over limit'
        },
        'speeding pct over 10': {
            'plain': 'You drive well over the speed limit (10+ mph) more often',
            'technical': 'Percentage of time speeding >10 mph over limit'
        },
        'speeding_pct_over_15': {
            'plain': 'You drive far above the speed limit (15+ mph) frequently',
            'technical': 'Percentage of time speeding >15 mph over limit'
        },
        'speeding pct over 15': {
            'plain': 'You drive far above the speed limit (15+ mph) frequently',
            'technical': 'Percentage of time speeding >15 mph over limit'
        },
        'volatility_jerk_p95': {
            'plain': 'Your driving style is more "jerky" with sudden speed changes',
            'technical': '95th percentile of jerk (rate of acceleration change)'
        },
        'volatility jerk p95': {
            'plain': 'Your driving style is more "jerky" with sudden speed changes',
            'technical': '95th percentile of jerk (rate of acceleration change)'
        },
        'pct_arterial': {
            'plain': 'You drive frequently on busy arterial roads with traffic lights and intersections',
            'technical': 'Percentage of miles driven on arterial roads'
        },
        'pct arterial': {
            'plain': 'You drive frequently on busy arterial roads with traffic lights and intersections',
            'technical': 'Percentage of miles driven on arterial roads'
        },
        'pct_local': {
            'plain': 'You do more neighborhood driving with pedestrians and stop signs',
            'technical': 'Percentage of miles driven on local roads'
        },
        'pct local': {
            'plain': 'You do more neighborhood driving with pedestrians and stop signs',
            'technical': 'Percentage of miles driven on local roads'
        },
        'crash_density_index': {
            'plain': 'You drive in areas with higher crash rates than average',
            'technical': 'External crash risk index based on road class and location'
        },
        'crash density index': {
            'plain': 'You drive in areas with higher crash rates than average',
            'technical': 'External crash risk index based on road class and location'
        },
        'theft_risk_index': {
            'plain': 'You often drive in higher-crime areas, which increases theft risk',
            'technical': 'External theft risk index based on geographic area'
        },
        'theft risk index': {
            'plain': 'You often drive in higher-crime areas, which increases theft risk',
            'technical': 'External theft risk index based on geographic area'
        },
        'miles': {
            'plain': 'Your total driving distance affects your exposure to potential accidents',
            'technical': 'Total miles driven in the month'
        },
        'trip_count': {
            'plain': 'You take many short trips, which can be riskier than fewer long trips',
            'technical': 'Total number of trips taken in the month'
        },
        'trip count': {
            'plain': 'You take many short trips, which can be riskier than fewer long trips',
            'technical': 'Total number of trips taken in the month'
        }
    }


def parse_reason_string(reason_str):
    """
    Parse a reason string like 'night_pct (+2453.276)' into components.
    Returns: (feature_name, shap_value, increases_risk)
    """
    import re
    
    # Extract feature name and SHAP value using regex
    match = re.match(r'^([^(]+)\s*\(([+-]?\d+\.?\d*)\)', reason_str.strip())
    
    if match:
        feature_name = match.group(1).strip()
        shap_value = float(match.group(2))
        increases_risk = shap_value > 0
        return feature_name, shap_value, increases_risk
    else:
        # Fallback for malformed strings
        return reason_str.strip(), 0.0, False


def create_templates_directory():
    """Create templates directory and HTML template."""
    templates_dir = Path("src/api/templates")
    templates_dir.mkdir(parents=True, exist_ok=True)
    
    template_path = templates_dir / "index.html"
    
    if not template_path.exists():
        html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>InsurityAI Pricing Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        
        .dashboard-header {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 20px 0;
            box-shadow: 0 2px 20px rgba(0,0,0,0.1);
            position: sticky;
            top: 0;
            z-index: 100;
        }
        
        .header-content {
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        h1 {
            color: #2c3e50;
            font-size: 28px;
            font-weight: 600;
            letter-spacing: -0.5px;
        }
        
        .company-info {
            color: #7f8c8d;
            font-size: 14px;
        }
        
        .main-container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 30px 20px;
        }
        
        .controls-section {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }
        
        .controls-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
        }
        
        .form-group {
            position: relative;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            color: #2c3e50;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .form-group select {
            width: 100%;
            padding: 12px 16px;
            border: 2px solid #e1e8ed;
            border-radius: 8px;
            font-size: 16px;
            background: white;
            transition: all 0.3s ease;
            appearance: none;
            background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e");
            background-position: right 12px center;
            background-repeat: no-repeat;
            background-size: 16px;
            padding-right: 40px;
        }
        
        .form-group select:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .metrics-overview {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .metric-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 24px;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 40px rgba(0,0,0,0.15);
        }
        
        .metric-card h3 {
            color: #7f8c8d;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
        }
        
        .metric-value {
            font-size: 32px;
            font-weight: 700;
            color: #2c3e50;
            margin: 8px 0;
            line-height: 1;
        }
        
        .metric-comparison {
            font-size: 14px;
            color: #7f8c8d;
            font-weight: 500;
        }
        
        .content-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }
        
        .content-section {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }
        
        .section-header {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 20px 24px;
            font-size: 18px;
            font-weight: 600;
            letter-spacing: -0.3px;
        }
        
        .section-content {
            padding: 24px;
        }
        
        .data-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }
        
        .data-table th {
            background: #f8f9fa;
            color: #2c3e50;
            font-weight: 600;
            padding: 16px 12px;
            text-align: left;
            border-bottom: 2px solid #e9ecef;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .data-table td {
            padding: 16px 12px;
            border-bottom: 1px solid #f1f3f4;
            color: #2c3e50;
        }
        
        .data-table tr:hover {
            background: #f8f9fa;
        }
        
        .data-table tr:last-child td {
            border-bottom: none;
        }
        
        .chart-section {
            grid-column: 1 / -1;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }
        
        .chart-content {
            padding: 24px;
            text-align: center;
        }
        
        .chart-content img {
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        }
        
        .status-message {
            text-align: center;
            padding: 60px 20px;
            color: #7f8c8d;
            font-size: 16px;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }
        
        .error-message {
            background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
            color: white;
            padding: 20px 24px;
            border-radius: 12px;
            margin: 20px 0;
            text-align: center;
            font-weight: 500;
            box-shadow: 0 4px 16px rgba(231, 76, 60, 0.3);
        }
        
        .loading-indicator {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-right: 10px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        @media (max-width: 1024px) {
            .content-grid {
                grid-template-columns: 1fr;
            }
            .metrics-overview {
                grid-template-columns: repeat(2, 1fr);
            }
        }
        
        @media (max-width: 768px) {
            .controls-grid {
                grid-template-columns: 1fr;
            }
            .metrics-overview {
                grid-template-columns: 1fr;
            }
            .header-content {
                flex-direction: column;
                gap: 10px;
                text-align: center;
            }
        }
    </style>
    <script>
        async function loadUserData() {
            const userSelect = document.getElementById('userSelect');
            const monthSelect = document.getElementById('monthSelect');
            
            // Show loading state
            userSelect.innerHTML = '<option value="">Loading users...</option>';
            
            try {
                const response = await fetch('/api/pricing');
                const data = await response.json();
                
                // Populate user dropdown
                const users = [...new Set(data.map(item => item.user_id))].sort((a, b) => parseInt(a) - parseInt(b));
                userSelect.innerHTML = '<option value="">Select a user...</option>';
                users.forEach(user => {
                    const option = document.createElement('option');
                    option.value = user;
                    option.textContent = `User ${user}`;
                    userSelect.appendChild(option);
                });
                
                // Store data globally for filtering
                window.pricingData = data;
                
            } catch (error) {
                console.error('Error loading data:', error);
                document.getElementById('content').innerHTML = 
                    '<div class="error-message">Unable to load pricing data. Please check that the server is running and data files are available.</div>';
            }
        }
        
        function onUserChange() {
            const userSelect = document.getElementById('userSelect');
            const monthSelect = document.getElementById('monthSelect');
            const selectedUser = userSelect.value;
            
            if (!selectedUser || !window.pricingData) {
                monthSelect.innerHTML = '<option value="">Select month...</option>';
                clearDashboard();
                return;
            }
            
            // Filter data for selected user
            const userData = window.pricingData.filter(item => item.user_id === selectedUser);
            
            // Populate month dropdown
            monthSelect.innerHTML = '<option value="">Select month...</option>';
            userData.forEach(item => {
                const option = document.createElement('option');
                option.value = item.month;
                option.textContent = item.month;
                monthSelect.appendChild(option);
            });
            
            // If only one month, auto-select it
            if (userData.length === 1) {
                monthSelect.value = userData[0].month;
                onMonthChange();
            } else {
                clearDashboard();
            }
        }
        
        function onMonthChange() {
            const userSelect = document.getElementById('userSelect');
            const monthSelect = document.getElementById('monthSelect');
            const selectedUser = userSelect.value;
            const selectedMonth = monthSelect.value;
            
            if (!selectedUser || !selectedMonth || !window.pricingData) {
                clearDashboard();
                return;
            }
            
            const selectedData = window.pricingData.find(
                item => item.user_id === selectedUser && item.month === selectedMonth
            );
            
            if (selectedData) {
                updateDashboard(selectedData);
                updateChart(selectedUser);
            }
        }
        
        function updateDashboard(data) {
            // Update metrics cards
            document.getElementById('riskIndex').textContent = data.risk_index.toFixed(3);
            document.getElementById('telematicsFactorCapped').textContent = data.telematics_factor_capped.toFixed(3);
            document.getElementById('finalPremium').textContent = `$${data.final_premium.toFixed(2)}`;
            document.getElementById('basePremium').textContent = `$${data.base_premium.toFixed(2)}`;
            
            // Update reason codes table
            const reasonsBody = document.getElementById('reasonsTableBody');
            reasonsBody.innerHTML = '';
            
            if (data.top_reasons && data.top_reasons.length > 0) {
                data.top_reasons.slice(0, 5).forEach((reason, index) => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${index + 1}</td>
                        <td>${reason}</td>
                    `;
                    reasonsBody.appendChild(row);
                });
            } else {
                reasonsBody.innerHTML = '<tr><td colspan="2" style="text-align: center; color: #7f8c8d; font-style: italic;">No reason codes available</td></tr>';
            }
            
            // Show capping indicators
            const indicators = [];
            if (data.is_first_month) indicators.push('First Month (Grace Period)');
            if (data.monthly_capped) indicators.push('Monthly Capped');
            if (data.quarterly_capped) indicators.push('Quarterly Capped');
            
            document.getElementById('cappingIndicators').innerHTML = 
                indicators.length > 0 ? indicators.join(' • ') : 'No caps applied';
        }
        
        async function updateChart(userId) {
            try {
                const response = await fetch(`/api/chart/${userId}`);
                if (response.ok) {
                    const blob = await response.blob();
                    const imageUrl = URL.createObjectURL(blob);
                    document.getElementById('chartImage').src = imageUrl;
                    document.getElementById('chartImage').style.display = 'block';
                    document.getElementById('noChartMessage').style.display = 'none';
                } else {
                    document.getElementById('chartImage').style.display = 'none';
                    document.getElementById('noChartMessage').style.display = 'block';
                }
            } catch (error) {
                console.error('Error loading chart:', error);
                document.getElementById('chartImage').style.display = 'none';
                document.getElementById('noChartMessage').style.display = 'block';
            }
        }
        
        function clearDashboard() {
            document.getElementById('riskIndex').textContent = '---';
            document.getElementById('telematicsFactorCapped').textContent = '---';
            document.getElementById('finalPremium').textContent = '---';
            document.getElementById('basePremium').textContent = '---';
            document.getElementById('reasonsTableBody').innerHTML = '<tr><td colspan="2" style="text-align: center; color: #7f8c8d; font-style: italic;">Select a user and month to view analysis</td></tr>';
            document.getElementById('cappingIndicators').innerHTML = '---';
            document.getElementById('chartImage').style.display = 'none';
            document.getElementById('noChartMessage').style.display = 'block';
        }
        
        // Load data when page loads
        document.addEventListener('DOMContentLoaded', loadUserData);
    </script>
</head>
<body>
    <header class="dashboard-header">
        <div class="header-content">
            <h1>InsurityAI Pricing Dashboard</h1>
            <div class="company-info">
                Telematics-Based Risk Assessment System
            </div>
        </div>
    </header>
    
    <div class="main-container">
        <section class="controls-section">
            <div class="controls-grid">
                <div class="form-group">
                    <label for="userSelect">User Selection</label>
                    <select id="userSelect" onchange="onUserChange()">
                        <option value="">Loading users...</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="monthSelect">Reporting Period</label>
                    <select id="monthSelect" onchange="onMonthChange()">
                        <option value="">Select month...</option>
                    </select>
                </div>
            </div>
        </section>
        
        <div id="content">
            <div class="metrics-overview">
                <div class="metric-card">
                    <h3>Risk Index</h3>
                    <div class="metric-value" id="riskIndex">---</div>
                    <div class="metric-comparison">vs Book Average</div>
                </div>
                <div class="metric-card">
                    <h3>Telematics Factor</h3>
                    <div class="metric-value" id="telematicsFactorCapped">---</div>
                    <div class="metric-comparison">After Caps & Smoothing</div>
                </div>
                <div class="metric-card">
                    <h3>Final Premium</h3>
                    <div class="metric-value" id="finalPremium">---</div>
                    <div class="metric-comparison">Base: <span id="basePremium">---</span></div>
                </div>
            </div>
            
            <div class="content-grid">
                <div class="content-section">
                    <h2 class="section-header">Primary Risk Factors</h2>
                    <div class="section-content">
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>Rank</th>
                                    <th>Risk Factor</th>
                                </tr>
                            </thead>
                            <tbody id="reasonsTableBody">
                                <tr><td colspan="2" class="status-message">Select a user and month to view analysis</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <div class="content-section">
                    <h2 class="section-header">Policy Status</h2>
                    <div class="section-content">
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>Status Type</th>
                                    <th>Details</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>Pricing Adjustments</td>
                                    <td><span id="cappingIndicators">---</span></td>
                                </tr>
                                <tr>
                                    <td>Data Quality</td>
                                    <td>Sufficient driving data available</td>
                                </tr>
                                <tr>
                                    <td>Model Version</td>
                                    <td>GLM v1.0 (Regulatory Approved)</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <div class="chart-section">
                    <h2 class="section-header">Risk Trend Analysis</h2>
                    <div class="chart-content">
                        <img id="chartImage" style="display: none;" alt="Risk Index Chart">
                        <div id="noChartMessage" class="status-message">
                            Select a user to view risk trend visualization
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>'''
        
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(html_template)
        
        logger.info(f"Created template at {template_path}")
    
    return Jinja2Templates(directory=str(templates_dir))


def load_pricing_data():
    """Load pricing results from JSON file."""
    global pricing_data, pricing_by_user
    
    # Try multiple possible paths
    possible_paths = [
        "../../data/pricing_results.json",
        "./data/pricing_results.json", 
        "data/pricing_results.json"
    ]
    
    pricing_file = None
    for path in possible_paths:
        if os.path.exists(path):
            pricing_file = path
            break
    
    if pricing_file is None:
        logger.warning(f"Pricing results file not found in any of: {possible_paths}")
        return False
    
    try:
        with open(pricing_file, 'r') as f:
            pricing_data = json.load(f)
        
        # Organize data by user for easy lookup
        pricing_by_user = {}
        for item in pricing_data:
            user_id = item['user_id']
            if user_id not in pricing_by_user:
                pricing_by_user[user_id] = []
            pricing_by_user[user_id].append(item)
        
        # Sort each user's data by month
        for user_id in pricing_by_user:
            pricing_by_user[user_id].sort(key=lambda x: x['month'])
        
        logger.info(f"Loaded {len(pricing_data)} pricing records for {len(pricing_by_user)} users")
        return True
        
    except Exception as e:
        logger.error(f"Error loading pricing data: {e}")
        return False


def create_risk_chart(user_id: str) -> Optional[bytes]:
    """Create a line chart of risk index over time for a user."""
    
    if user_id not in pricing_by_user:
        return None
    
    user_data = pricing_by_user[user_id]
    
    if len(user_data) < 2:
        return None
    
    # Extract data for plotting
    months = [item['month'] for item in user_data]
    risk_indices = [item['risk_index'] for item in user_data]
    ewma_indices = [item['ewma_index'] for item in user_data]
    
    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(months, risk_indices, marker='o', linewidth=2, label='Raw Risk Index', color='#e74c3c')
    plt.plot(months, ewma_indices, marker='s', linewidth=2, label='EWMA Smoothed', color='#3498db')
    
    # Add horizontal reference line at 1.0
    plt.axhline(y=1.0, color='gray', linestyle='--', alpha=0.7, label='Book Average')
    
    plt.title(f'Risk Index Trend - User {user_id}', fontsize=16, fontweight='bold')
    plt.xlabel('Month', fontsize=12)
    plt.ylabel('Risk Index', fontsize=12)
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # Convert to bytes
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
    img_buffer.seek(0)
    plt.close()
    
    return img_buffer.getvalue()


# Initialize templates and load data on startup
templates = create_templates_directory()
load_pricing_data()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"ok": True}


@app.get("/api/pricing")
async def get_pricing_data():
    """Return all pricing results."""
    if not pricing_data:
        raise HTTPException(status_code=404, detail="Pricing data not found")
    return pricing_data


@app.get("/api/chart/{user_id}")
async def get_user_chart(user_id: str):
    """Generate and return a risk chart for a specific user."""
    chart_data = create_risk_chart(user_id)
    
    if chart_data is None:
        raise HTTPException(status_code=404, detail="Chart data not available for this user")
    
    return StreamingResponse(
        io.BytesIO(chart_data),
        media_type="image/png",
        headers={"Cache-Control": "no-cache"}
    )


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Serve the main dashboard page."""
    feature_mapping = get_feature_mapping()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "feature_mapping": feature_mapping
    })


if __name__ == "__main__":
    # Ensure data is loaded
    if not load_pricing_data():
        logger.warning("No pricing data available - dashboard will show empty state")
    
    # Run the server
    logger.info("Starting InsurityAI Pricing Dashboard...")
    logger.info("Dashboard available at: http://localhost:8000")
    logger.info("API endpoints:")
    logger.info("  GET /health - Health check")
    logger.info("  GET /api/pricing - Pricing data")
    logger.info("  GET /api/chart/{user_id} - Risk charts")
    
    uvicorn.run(
        "server:app",  # Assuming this file is named server.py
        host="0.0.0.0",
        port=8001,
        reload=False,
        log_level="info"
    )


