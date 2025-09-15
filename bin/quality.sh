#!/bin/bash
# InsurityAI Code Quality Check
# Runs linting and formatting checks

set -e

echo "🔍 Running code quality checks..."

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

echo "📋 Installing quality tools..."
pip install -q flake8 black isort mypy pytest-cov

echo "📋 Running flake8 (linting)..."
flake8 src/ tests/ --statistics

echo "📋 Checking import sorting..."
isort --check-only src/ tests/

echo "📋 Checking code formatting..."
black --check src/ tests/

echo "📋 Running type checks..."
mypy src/ || echo "⚠️  Type checking has warnings (non-blocking)"

echo ""
echo "✅ Code quality checks completed!"
echo ""
echo "To fix formatting issues:"
echo "  black src/ tests/     # Auto-format code"
echo "  isort src/ tests/     # Sort imports"