#!/bin/bash
# TauTranslator Production Startup Script
# ======================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}TauTranslator Production Startup${NC}"
echo "=================================="

# Check Python version
echo -n "Checking Python version... "
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then 
    echo -e "${GREEN}✓ Python $PYTHON_VERSION${NC}"
else
    echo -e "${RED}✗ Python $PYTHON_VERSION (need >= $REQUIRED_VERSION)${NC}"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo -e "${YELLOW}Installing production dependencies...${NC}"
pip install --upgrade pip setuptools wheel
pip install -r production_requirements.txt

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p logs
mkdir -p data
mkdir -p ~/.tau_translator

# Set environment variables
export TAU_LOG_LEVEL="${TAU_LOG_LEVEL:-INFO}"
export TAU_DEFAULT_MODEL="${TAU_DEFAULT_MODEL:-gpt-3.5-turbo}"
export PYTHONUNBUFFERED=1

# Check which mode to start
MODE="${1:-all}"

case $MODE in
    api)
        echo -e "${GREEN}Starting API server...${NC}"
        python production_translator.py --api
        ;;
    web)
        echo -e "${GREEN}Starting web interface...${NC}"
        python production_translator.py --web
        ;;
    docker)
        echo -e "${GREEN}Starting with Docker Compose...${NC}"
        docker-compose up -d
        ;;
    all)
        echo -e "${GREEN}Starting all services...${NC}"
        # Start API server in background
        python production_translator.py --api &
        API_PID=$!
        
        # Wait a bit for API to start
        sleep 3
        
        # Start web interface
        python production_translator.py --web &
        WEB_PID=$!
        
        echo -e "${GREEN}Services started:${NC}"
        echo "- API Server: http://localhost:8000 (PID: $API_PID)"
        echo "- Web Interface: http://localhost:5000 (PID: $WEB_PID)"
        echo ""
        echo "Press Ctrl+C to stop all services"
        
        # Wait for interrupt
        trap "kill $API_PID $WEB_PID; exit" INT
        wait
        ;;
    test)
        echo -e "${GREEN}Running production tests...${NC}"
        python -m pytest tests/ -v
        ;;
    *)
        echo "Usage: $0 [api|web|docker|all|test]"
        echo "  api    - Start only the API server"
        echo "  web    - Start only the web interface"
        echo "  docker - Start with Docker Compose"
        echo "  all    - Start both API and web (default)"
        echo "  test   - Run production tests"
        exit 1
        ;;
esac