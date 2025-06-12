# TauTranslator Scripts Directory
================================

This directory contains utility scripts, demos, and tools for the TauTranslator project.

## Directory Structure

```
scripts/
├── demos/                      # Demo scripts
│   ├── run_all_demos.py       # Master demo runner
│   ├── nlp_gui_demo.py        # NLP GUI demonstration
│   └── start_nlp_demo.py      # NLP demo launcher
├── setup/                      # Setup and installation scripts
│   └── recommended_local_models.py
├── analysis/                   # Analysis and quality tools
│   └── run_project_wide_mutation_analysis.py
├── test_pyqt_gui.py           # PyQt GUI test runner
├── demo_pyqt_autocomplete.py  # AutoComplete GUI demo
├── PYQT_GUI_TESTING.md        # PyQt testing guide
└── [various utility scripts]
```

## Quick Start Demos

### 1. Run All Demos
```bash
python scripts/demos/run_all_demos.py
```
Interactive menu to run any or all demos.

### 2. PyQt GUI with AutoComplete
```bash
python scripts/demo_pyqt_autocomplete.py
```
Tests the desktop GUI with autocomplete functionality.

### 3. Test PyQt Installation
```bash
python scripts/test_pyqt_gui.py
```
Checks dependencies and allows running GUI or tests.

## Utility Scripts

### Backend Management
- `start_backend.py` - Start the unified backend server
- `start_all_backends.py` - Start all backend services
- `start_production.sh` - Production startup script

### Build and Setup
- `build_desktop_app.py` - Build desktop application
- `build_executable_ubuntu.py` - Create Ubuntu executable
- `setup_complete_system.py` - Complete system setup
- `setup_gemma_model.py` - Setup Gemma language models

### Migration and Cleanup
- `migrate_*.py` - Various migration scripts
- `cleanup_duplicates.py` - Remove duplicate files
- `update_imports_*.py` - Update import statements

### Testing and Analysis
- `benchmark_simd_performance.py` - Test SIMD optimizations
- `quick_quality_check.py` - Run quality checks

## Running Scripts

Most scripts can be run directly:
```bash
python scripts/script_name.py
```

Some scripts may require additional arguments or environment setup. Check the script's docstring or run with `--help` if available.

## Adding New Scripts

When adding new scripts:
1. Include a clear docstring explaining purpose
2. Add shebang line: `#!/usr/bin/env python3`
3. Make executable: `chmod +x script_name.py`
4. Update this README if it's a user-facing script
5. Consider adding to `run_all_demos.py` if it's a demo

## Dependencies

Different scripts have different requirements:
- **PyQt demos**: Require PyQt6 or PyQt5
- **NLP demos**: May require language models
- **Backend scripts**: Require FastAPI and uvicorn
- **Analysis scripts**: May require pytest, mutmut, etc.

Check individual script requirements or run dependency checks.