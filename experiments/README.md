# Experiments Folder

This folder contains experimental implementations, alternative approaches, and legacy code that has been moved out of the main codebase to keep it clean and focused.

## Structure

### 📁 refactored_implementations/
Contains experimental refactored versions following the Intentional Disclosure Principle:
- **pattern_translator_refactored.py** - Pattern translator with all 4 craftsmanship rules
- **manager_refactored.py** - Translation manager with clean orchestration
- **auth_refactored.py** - Authentication API with explicit async naming
- **config_refactored.py** - Configuration with domain types
- **pattern_loader_refactored.py** - Pattern loader with repository pattern
- Test files for each refactored implementation

These implementations demonstrate:
- Rule 1: Explicit async naming for I/O operations
- Rule 2: Orchestrator pattern for public methods
- Rule 3: Rich domain types instead of primitives
- Rule 4: Clean separation of infrastructure from core logic

### 📁 ui_implementations/
Different desktop UI implementations for comparison:
- **tau_translator_desktop_qt.py** - PyQt6 version (most feature-rich)
- **tau_translator_desktop_tkinter.py** - Tkinter professional version
- **tau_translator_desktop_modern.py** - Tkinter with modern design
- **tau_translator_desktop_legacy.py** - Basic Tkinter implementation
- **gui_comparison.py** - Tool to compare UI implementations
- **comprehensive_qt_integration_test.py** - Qt integration testing

### 📁 fsa_variants/
Different Finite State Automaton engine implementations:
- **fsa_engine_fast.py** - Optimized for speed
- **fsa_engine_hybrid.py** - Hybrid approach balancing features
- **fsa_engine_optimized.py** - Memory-optimized version

### 📁 old_security_implementations/
Legacy security and API key management code:
- Multiple implementations with varying security levels
- Now integrated into `backend/unified/core/auth.py`

### 📁 old_core_engine/
The original tau_translator_omega core engine:
- Legacy implementation before unified backend
- Contains old parser, semantic analyzer, and translation logic
- Superseded by `backend/unified/`

## Purpose

This folder serves as:
1. **Reference** - See how different approaches were implemented
2. **Learning** - Understand the evolution of the codebase
3. **Experimentation** - Test new ideas without cluttering main code
4. **Comparison** - Evaluate different implementation strategies

## Usage

- These files are NOT part of the active codebase
- They are NOT imported by any production code
- They serve as examples and experiments
- Feel free to study, modify, or test these implementations

## Future

As new experiments are conducted:
- Move experimental code here instead of deleting
- Document what each experiment was testing
- Keep the most promising approaches for potential future integration

---
Generated: 2025-01-06
Copyright: DarkLightX/Dana Edwards