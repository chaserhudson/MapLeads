#!/bin/bash

# MapLeads Easy Runner Script
# Makes it simple to run MapLeads without knowing Python commands

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment not found!${NC}"
    echo "Please run the installation script first: ./install.sh"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Function to show help
show_help() {
    echo -e "${BLUE}🗺️ MapLeads - Easy Business Lead Generator${NC}"
    echo ""
    echo "Usage: ./run.sh [command]"
    echo ""
    echo -e "${GREEN}Main Commands:${NC}"
    echo "  setup          - Set up MapLeads for the first time"
    echo "  ui             - Launch web interface (easiest for beginners)"
    echo "  (no command)   - Start monitoring for new businesses"
    echo "  stop           - Stop monitoring (Ctrl+C also works)"
    echo ""
    echo -e "${GREEN}Utilities:${NC}"
    echo "  status         - View statistics and recent discoveries"
    echo "  export         - Export your data to CSV file"
    echo "  test           - Run a quick test to verify everything works"
    echo "  categories     - See available business categories"
    echo ""
    echo -e "${GREEN}Configuration:${NC}"
    echo "  category [type] - Change business category to monitor"
    echo "  instances [num] - Change number of parallel browsers (1-5)"
    echo ""
    echo -e "${GREEN}Examples:${NC}"
    echo "  ./run.sh setup                    # First-time setup"
    echo "  ./run.sh ui                       # Launch web interface"
    echo "  ./run.sh                          # Start monitoring"
    echo "  ./run.sh category plumber         # Monitor plumbers"
    echo "  ./run.sh instances 3              # Use 3 parallel browsers"
    echo "  ./run.sh export                   # Export data to CSV"
    echo ""
}

# Function to check if setup is needed
check_setup() {
    if [ ! -f "config/config.json" ]; then
        echo -e "${YELLOW}⚠️ No configuration found!${NC}"
        echo "Please run setup first: ./run.sh setup"
        exit 1
    fi
}

# Main script logic
case "$1" in
    "setup")
        echo -e "${BLUE}🔧 Running MapLeads Setup...${NC}"
        python mapleads.py setup
        ;;
    "ui")
        echo -e "${BLUE}🌐 Launching MapLeads Web Interface...${NC}"
        echo -e "${YELLOW}💡 The web interface will open in your browser${NC}"
        echo -e "${YELLOW}💡 Use Ctrl+C to stop the web server${NC}"
        echo ""
        python launch_ui.py
        ;;
    "status")
        check_setup
        echo -e "${BLUE}📊 Checking MapLeads Status...${NC}"
        python mapleads.py status
        ;;
    "export")
        check_setup
        echo -e "${BLUE}💾 Exporting Data...${NC}"
        python mapleads.py export
        ;;
    "test")
        check_setup
        echo -e "${BLUE}🧪 Running Test Scan...${NC}"
        python mapleads.py test
        ;;
    "categories")
        echo -e "${BLUE}📋 Available Categories...${NC}"
        python mapleads.py categories
        ;;
    "category")
        check_setup
        if [ -z "$2" ]; then
            echo -e "${BLUE}🏷️ Current Category...${NC}"
            python mapleads.py category
        else
            echo -e "${BLUE}🏷️ Changing Category to: $2${NC}"
            python mapleads.py category "$2"
        fi
        ;;
    "instances")
        check_setup
        if [ -z "$2" ]; then
            echo -e "${BLUE}🔧 Browser Instances...${NC}"
            python mapleads.py instances
        else
            echo -e "${BLUE}🔧 Setting Browser Instances to: $2${NC}"
            python mapleads.py instances "$2"
        fi
        ;;
    "stop")
        echo -e "${YELLOW}⏹️ To stop MapLeads, press Ctrl+C in the monitoring window${NC}"
        ;;
    "help"|"--help"|"-h")
        show_help
        ;;
    "")
        check_setup
        echo -e "${GREEN}🚀 Starting MapLeads Monitoring...${NC}"
        echo -e "${YELLOW}💡 Press Ctrl+C to stop monitoring${NC}"
        echo ""
        python mapleads.py run
        ;;
    *)
        echo -e "${RED}❌ Unknown command: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac