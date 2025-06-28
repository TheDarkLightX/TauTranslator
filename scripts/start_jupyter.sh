#!/bin/bash
# Start Jupyter Lab with TauTranslator environment
# ================================================

set -e

# Determine the project root directory dynamically
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=$(dirname "$SCRIPT_DIR")

# Change to the project root directory
cd "$PROJECT_ROOT"
source venv/bin/activate

echo "🚀 Starting Jupyter Lab for TauTranslator Development"
echo "=" * 60

# Set environment variables for debugging
export PYTHONPATH="${PWD}:${PWD}/src:${PYTHONPATH}"
export TAU_DEBUG=1
export TAU_LOG_LEVEL=DEBUG

# Install Jupyter extensions if not already present
echo "📦 Checking Jupyter extensions..."
pip install -q jupyterlab-lsp python-lsp-server[all] 2>/dev/null || echo "Extensions already installed"

# Create notebooks directory if it doesn't exist
mkdir -p notebooks

# Start Jupyter Lab
echo "🔬 Launching Jupyter Lab..."
echo "   - Project root: ${PWD}"
echo "   - Python path: ${PYTHONPATH}"
echo "   - Virtual env: $(which python)"
echo ""
echo "Access at: http://localhost:8888"
echo "Press Ctrl+C to stop"

jupyter lab --notebook-dir=. --ip=0.0.0.0 --port=8888 --no-browser --allow-root