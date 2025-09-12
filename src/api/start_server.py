#!/usr/bin/env python3
"""
Simple server startup script.
"""

import uvicorn
import sys
import os

# Add current directory to path so we can import server
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("Starting InsurityAI Dashboard Server...")
    print("Dashboard will be available at: http://localhost:8001")
    print("Note: Pricing data not found - dashboard will show empty state")
    print("To populate data, run the feature engineering and model training pipelines first.")
    
    uvicorn.run(
        "server:app",
        host="127.0.0.1", 
        port=8001,
        reload=False,
        log_level="info"
    )