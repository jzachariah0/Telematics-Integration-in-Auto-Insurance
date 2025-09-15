#!/bin/bash
# InsurityAI Setup Script
# Sets up Python virtual environment and installs dependencies

set -e

echo "🚀 Setting up InsurityAI environment..."

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.8+ first."
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python -m venv .venv

# Activate virtual environment (cross-platform)
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source .venv/Scripts/activate
else
    source .venv/bin/activate
fi

# Upgrade pip
echo "🔄 Upgrading pip..."
python -m pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

echo "✅ Environment setup complete!"
echo ""
echo "To activate the environment manually:"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "  .venv\\Scripts\\activate"
else
    echo "  source .venv/bin/activate"
fi
echo ""
echo "Next steps:"
echo "  ./bin/train.sh    # Train models"
echo "  ./bin/serve.sh    # Start dashboard"