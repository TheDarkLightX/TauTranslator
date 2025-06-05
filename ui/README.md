# TauTranslator Desktop User Interfaces

This directory contains the desktop GUI implementations for TauTranslator.

## Available Interfaces

### tau_translator_desktop_qt.py
- **Framework**: PyQt6
- **Features**: Professional IDE-quality interface with syntax highlighting, dockable panels, and native look
- **Recommended**: Yes - for production use
- **Size**: ~50MB (includes Qt runtime)

### tau_translator_desktop_tkinter.py
- **Framework**: Tkinter (built-in Python)
- **Features**: Basic interface with theme support
- **Recommended**: For lightweight deployments
- **Size**: ~5MB

### tau_translator_desktop_modern.py
- **Framework**: Tkinter with modern styling
- **Features**: Card-based design, theme toggle, three-column layout
- **Recommended**: Alternative lightweight option
- **Size**: ~5MB

### tau_translator_desktop_legacy.py
- **Framework**: Tkinter
- **Features**: Original interface with Gemma 3 integration
- **Status**: Legacy - kept for compatibility

## Supporting Files

- **splash_screen.py**: Loading screen with animations
- **gui_comparison.py**: Comparison tool for different GUI frameworks
- **comprehensive_qt_integration_test.py**: Qt integration tests

## Usage

To run a specific interface:
```bash
python3 tau_translator_desktop_qt.py        # Recommended
python3 tau_translator_desktop_tkinter.py   # Lightweight
```

## Building Executables

Use the build script with environment variable to choose interface:
```bash
USE_QT6=true python3 ../scripts/build_desktop_app.py   # Build with Qt
USE_QT6=false python3 ../scripts/build_desktop_app.py  # Build with tkinter
```