#!/bin/bash
# TauTranslatorOmega Ubuntu Installation Script
# ============================================
# 
# Creates Ubuntu desktop integration and compilation options
# Designed by Claude 3.5 Sonnet

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# App info
APP_NAME="TauTranslatorOmega"
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERSION="3.0"

echo -e "${BLUE}🚀 $APP_NAME Ubuntu Installation${NC}"
echo -e "${BLUE}Designed by Claude 3.5 Sonnet${NC}"
echo "============================================"
echo ""

# Check if running on Ubuntu/Debian
if ! command -v apt &> /dev/null; then
    echo -e "${YELLOW}⚠️  This script is designed for Ubuntu/Debian systems${NC}"
    echo "   You can still run the Python script directly:"
    echo "   python3 tau_translator_app.py"
    exit 1
fi

# Function to check dependencies
check_dependencies() {
    echo -e "${CYAN}🔍 Checking dependencies...${NC}"
    
    # Check Python 3
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        echo -e "   ${GREEN}✅ Python 3: $PYTHON_VERSION${NC}"
    else
        echo -e "   ${RED}❌ Python 3 not found${NC}"
        echo "   Installing Python 3..."
        sudo apt update
        sudo apt install -y python3
    fi
    
    # Check tkinter
    if python3 -c "import tkinter" 2>/dev/null; then
        echo -e "   ${GREEN}✅ tkinter: Available${NC}"
    else
        echo -e "   ${YELLOW}⚠️  tkinter not found${NC}"
        echo "   Installing python3-tk..."
        sudo apt update
        sudo apt install -y python3-tk
    fi
    
    # Check pip
    if command -v pip3 &> /dev/null; then
        echo -e "   ${GREEN}✅ pip3: Available${NC}"
    else
        echo -e "   ${YELLOW}⚠️  pip3 not found${NC}"
        echo "   Installing python3-pip..."
        sudo apt update
        sudo apt install -y python3-pip
    fi
    
    echo ""
}

# Function to create desktop launcher
create_launcher() {
    echo -e "${CYAN}🖥️  Creating Ubuntu desktop launcher...${NC}"
    
    if python3 create_ubuntu_launcher.py; then
        echo -e "${GREEN}✅ Desktop launcher created successfully!${NC}"
        echo ""
        echo -e "${BLUE}🚀 How to launch:${NC}"
        echo "   1. Applications Menu → Development → TauTranslatorOmega"
        echo "   2. Desktop shortcut (if created)"
        echo "   3. Terminal: tau-translator-omega"
        echo "   4. Alt+F2 → tau-translator-omega"
        echo ""
        return 0
    else
        echo -e "${RED}❌ Desktop launcher creation failed${NC}"
        return 1
    fi
}

# Function to compile executable
compile_executable() {
    echo -e "${CYAN}🔨 Compiling standalone executable...${NC}"
    echo "   This may take several minutes..."
    echo ""
    
    if python3 compile_executable.py; then
        echo -e "${GREEN}✅ Compilation completed!${NC}"
        echo ""
        echo -e "${BLUE}📦 Check the 'dist' directory for:${NC}"
        echo "   • TauTranslatorOmega (single executable)"
        echo "   • TauTranslatorOmega_dir (directory distribution)"
        echo "   • tau-translator-omega_3.0-1_amd64.deb (Ubuntu package)"
        echo ""
        return 0
    else
        echo -e "${RED}❌ Compilation failed${NC}"
        return 1
    fi
}

# Function to test the application
test_application() {
    echo -e "${CYAN}🧪 Testing application...${NC}"
    
    if python3 -c "
import sys
sys.path.insert(0, 'src')
from tau_translator_omega.lmql_engine.bidirectional_translator import LMQLBidirectionalTranslator
translator = LMQLBidirectionalTranslator()
result = translator.translate_tau_to_tce('halfAdderSum(a, b) := a + b')
print('✅ Test successful:', result.output if result.success else 'Failed')
"; then
        echo -e "${GREEN}✅ Application test passed!${NC}"
        return 0
    else
        echo -e "${RED}❌ Application test failed${NC}"
        return 1
    fi
}

# Function to show installation menu
show_menu() {
    echo -e "${PURPLE}📋 Installation Options:${NC}"
    echo ""
    echo "1. 🖥️  Create Ubuntu Desktop Launcher (Recommended)"
    echo "2. 🔨 Compile Standalone Executable"
    echo "3. 🧪 Test Application"
    echo "4. 🚀 Run Application Now"
    echo "5. 📊 Show UI Features Demo"
    echo "6. ❌ Exit"
    echo ""
    read -p "Choose an option (1-6): " choice
    
    case $choice in
        1)
            create_launcher
            ;;
        2)
            compile_executable
            ;;
        3)
            test_application
            ;;
        4)
            echo -e "${CYAN}🚀 Launching TauTranslatorOmega...${NC}"
            python3 tau_translator_app.py
            ;;
        5)
            echo -e "${CYAN}🎨 Launching UI Features Demo...${NC}"
            python3 demo_ui_features.py
            ;;
        6)
            echo -e "${BLUE}👋 Goodbye!${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Invalid option${NC}"
            show_menu
            ;;
    esac
}

# Main installation process
main() {
    # Change to app directory
    cd "$APP_DIR"
    
    # Check dependencies
    check_dependencies
    
    # Show current status
    echo -e "${BLUE}📁 Application Directory: $APP_DIR${NC}"
    echo -e "${BLUE}🏷️  Version: $VERSION${NC}"
    echo ""
    
    # Show menu
    while true; do
        show_menu
        echo ""
        read -p "Would you like to do something else? (y/n): " continue_choice
        if [[ $continue_choice != "y" && $continue_choice != "Y" ]]; then
            break
        fi
        echo ""
    done
    
    echo ""
    echo -e "${GREEN}🎉 Thank you for using TauTranslatorOmega!${NC}"
    echo -e "${BLUE}Designed by Claude 3.5 Sonnet with professional UI/UX${NC}"
}

# Run main function
main
