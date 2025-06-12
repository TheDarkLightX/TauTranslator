#!/bin/bash
# Quick cleanup script for TauTranslator repository
# Removes build artifacts and caches

echo "🧹 TauTranslator Quick Cleanup"
echo "=============================="

# Remove Python caches
echo "Removing Python caches..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
find . -type f -name "*.pyo" -delete 2>/dev/null

# Remove build artifacts
echo "Removing build artifacts..."
rm -rf build/ dist/ *.egg-info/ 2>/dev/null

# Remove coverage reports
echo "Removing coverage reports..."
rm -rf htmlcov/ .coverage 2>/dev/null

# Remove temporary files
echo "Removing temporary files..."
find . -type f -name ".DS_Store" -delete 2>/dev/null
find . -type f -name "*~" -delete 2>/dev/null
find . -type f -name "*.swp" -delete 2>/dev/null

# Count remaining Python files
echo ""
echo "📊 Repository Statistics:"
echo "Python files: $(find . -name "*.py" -type f | grep -v __pycache__ | wc -l)"
echo "Test files: $(find . -name "test_*.py" -type f | wc -l)"
echo "UI files: $(find ui/ -name "*.py" -type f 2>/dev/null | wc -l)"

echo ""
echo "✅ Quick cleanup complete!"
echo ""
echo "For full reorganization, run:"
echo "  python reorganize_repository.py --execute"