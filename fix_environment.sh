#!/bin/bash

echo "🔧 MapLeads Environment Fix"
echo "============================"
echo ""

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Not in MapLeads directory!"
    echo "Please cd to the MapLeads directory first"
    exit 1
fi

echo "✅ In MapLeads directory"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "✅ Virtual environment exists"

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Check Python version
echo "🐍 Python version: $(python --version)"

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install Flask specifically
echo "📦 Installing Flask..."
pip install flask

# Test Flask installation
echo "🧪 Testing Flask installation..."
python -c "import flask; print(f'✅ Flask {flask.__version__} installed successfully')"

# Kill any process using port 5000
echo "🔌 Checking port 5000..."
lsof -ti:5000 | xargs kill -9 2>/dev/null || echo "Port 5000 is free"

echo ""
echo "🚀 Environment should be fixed!"
echo "Now run: python emergency_test.py"