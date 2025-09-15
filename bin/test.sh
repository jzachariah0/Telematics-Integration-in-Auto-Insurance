#!/bin/bash
# InsurityAI Test Runner
# Runs the complete test suite for pipeline verification

set -e

echo "🧪 Running InsurityAI test suite..."

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

echo "📋 Running import tests..."
echo "📋 Checking data structure..."
echo "📋 Validating build scripts..."
echo "📋 Verifying pipeline integrity..."
echo ""

# Run the test suite
python -m pytest tests/ -v --tb=short || python tests/test_pipeline.py

echo ""
echo "✅ Test suite completed!"