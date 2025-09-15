#!/bin/bash
# InsurityAI Training Script
# Runs the complete ML training pipeline

set -e

echo "🤖 Training InsurityAI models..."

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

echo "📊 Step 1/3: Building features..."
python src/features/build_features.py

echo "🧠 Step 2/3: Training models..."
python src/models/train.py

echo "💰 Step 3/3: Running pricing engine..."
python src/pricing/run_pricing.py

echo "✅ Training pipeline completed successfully!"
echo ""
echo "Generated artifacts:"
echo "  📁 models/glm.pkl, models/lgbm.pkl"
echo "  📁 data/features.parquet"
echo "  📁 data/pricing_results.json"
echo "  📁 docs/metrics/*.png"
echo ""
echo "Next step: ./bin/serve.sh to start the dashboard"