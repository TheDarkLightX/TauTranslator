"""
Global pytest configuration for TauTranslator test suite.
Sets up Python path and common fixtures.
"""
import sys
import os
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Add project root for relative imports
sys.path.insert(0, str(project_root))

# Configure test markers
pytest_plugins = []