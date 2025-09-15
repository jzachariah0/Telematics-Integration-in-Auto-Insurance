#!/bin/bash
# InsurityAI Dashboard Server
# Starts the FastAPI dashboard with real-time pricing

set -e

echo "🌐 Starting InsurityAI dashboard..."

# Activate virtual environment (cross-platform)
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source .venv/Scripts/activate
else
    source .venv/bin/activate
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Run ./bin/setup.sh first."
    exit 1
fi

# Check if models exist
if [ ! -f "models/glm.pkl" ] || [ ! -f "models/lgbm.pkl" ]; then
    echo "❌ Models not found. Run ./bin/train.sh first."
    exit 1
fi

# Check if pricing data exists
if [ ! -f "data/pricing_results.json" ]; then
    echo "❌ Pricing data not found. Run ./bin/train.sh first."
    exit 1
fi

echo "🚀 Starting dashboard server..."
echo "📍 Dashboard will be available at: http://localhost:8001"
echo "📚 API documentation at: http://localhost:8001/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the FastAPI server
python src/api/server.py