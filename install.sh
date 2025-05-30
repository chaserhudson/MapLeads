#!/bin/bash

echo "🗺️ MapLeads Installation Script"
echo "================================"
echo ""

# Check if running on supported OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="Mac"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="Linux"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    OS="Windows"
    echo "❌ Windows users: Please use Windows Subsystem for Linux (WSL) or see manual installation guide"
    exit 1
else
    echo "❌ Unsupported operating system: $OSTYPE"
    exit 1
fi

echo "✅ Detected: $OS"
echo ""

# Check for Python 3
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    echo "✅ Python 3 found: $PYTHON_VERSION"
else
    echo "❌ Python 3 not found!"
    echo ""
    if [[ "$OS" == "Mac" ]]; then
        echo "To install Python 3 on Mac:"
        echo "1. Install Homebrew: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        echo "2. Install Python: brew install python3"
    elif [[ "$OS" == "Linux" ]]; then
        echo "To install Python 3 on Linux:"
        echo "Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-pip"
        echo "CentOS/RHEL: sudo yum install python3 python3-pip"
    fi
    exit 1
fi

# Check for pip
if command -v pip3 &> /dev/null; then
    echo "✅ pip3 found"
else
    echo "❌ pip3 not found!"
    echo "Please install pip3 and try again"
    exit 1
fi

# Check for git
if command -v git &> /dev/null; then
    echo "✅ git found"
else
    echo "❌ git not found!"
    echo ""
    if [[ "$OS" == "Mac" ]]; then
        echo "Install git on Mac: brew install git"
    elif [[ "$OS" == "Linux" ]]; then
        echo "Install git on Linux: sudo apt install git (Ubuntu/Debian) or sudo yum install git (CentOS/RHEL)"
    fi
    exit 1
fi

echo ""
echo "🔽 Installing MapLeads..."
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "❌ Failed to create virtual environment"
    exit 1
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📚 Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Make scripts executable
chmod +x run.sh
chmod +x install.sh

echo ""
echo "🎉 Installation Complete!"
echo ""
echo "🚀 Next Steps:"
echo "1. Run setup: ./run.sh setup"
echo "2. Start monitoring: ./run.sh"
echo ""
echo "💡 Tip: You can also run individual commands like:"
echo "   ./run.sh status    - Check statistics"
echo "   ./run.sh export    - Export your data"
echo "   ./run.sh test      - Run a test scan"
echo ""
echo "📖 For help: ./run.sh --help"
echo ""