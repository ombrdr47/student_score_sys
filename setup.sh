#!/bin/bash

# Communication Skills Scoring Tool - Setup Script
# This script automates the local setup process

echo "🚀 Communication Skills Scoring Tool - Setup Script"
echo "=================================================="

# Check Python version
echo ""
echo "1️⃣  Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✅ $PYTHON_VERSION found"
else
    echo "❌ Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

# Check Java (for LanguageTool)
echo ""
echo "2️⃣  Checking Java installation..."
if command -v java &> /dev/null; then
    JAVA_VERSION=$(java -version 2>&1 | head -n 1)
    echo "✅ Java found: $JAVA_VERSION"
else
    echo "⚠️  Java not found. LanguageTool grammar checking may not work."
    echo "   Install Java: brew install openjdk@11 (macOS) or sudo apt install openjdk-11-jre (Ubuntu)"
fi

# Create virtual environment
echo ""
echo "3️⃣  Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "ℹ️  Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "4️⃣  Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"

# Upgrade pip
echo ""
echo "5️⃣  Upgrading pip..."
pip install --upgrade pip --quiet
echo "✅ pip upgraded"

# Install dependencies
echo ""
echo "6️⃣  Installing dependencies (this may take 5-10 minutes)..."
echo "   Downloading NLP models and libraries..."
pip install -r requirements.txt
echo "✅ Dependencies installed"

# Verify installation
echo ""
echo "7️⃣  Verifying installation..."
python -c "import flask; import sentence_transformers; import language_tool_python; import vaderSentiment; print('✅ All packages imported successfully')"

# Create test results directory
mkdir -p test_results

echo ""
echo "=================================================="
echo "✅ Setup Complete!"
echo "=================================================="
echo ""
echo "Next steps:"
echo "  1. Activate environment: source venv/bin/activate"
echo "  2. Run application: python app.py"
echo "  3. Open browser: http://localhost:5000"
echo "  4. Run tests: python test_scorer.py"
echo ""
echo "For deployment instructions, see DEPLOYMENT.md"
echo ""
