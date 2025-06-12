# TauTranslator Canonical Versions

This document identifies the canonical (official) implementation of each component.

## User Interfaces

### PyQt6 Desktop Applications
- **Main GUI**: `ui/tau_translator_qt_educational_complete.py`
  - Full-featured PyQt6 application
  - Educational autocomplete with examples
  - Achievement system and progress tracking
  - Learning levels (Beginner/Intermediate/Advanced)

- **Simple GUI**: `ui/tau_translator_desktop_qt.py`
  - Lightweight PyQt6 interface
  - Basic translation functionality
  - Syntax highlighting for TAU

### React Web Application
- **Location**: `pwa/`
- **Main Page**: `pages/professional.js`
- **Framework**: Next.js with React
- **Features**: Progressive Web App, responsive design

## Backend Services

### FastAPI Server
- **Location**: `backend/unified/server.py`
- **API Documentation**: Auto-generated at `/docs`
- **Endpoints**:
  - `/api/translate` - Translation service
  - `/api/nlp/autocomplete` - Autocomplete suggestions
  - `/api/educational/*` - Educational features
  - `/api/grammar/*` - Grammar operations

### Core Services
All in `backend/unified/`:
- **Translation**: `domain/nlp_translation_service.py`
- **Autocomplete**: `core/autocomplete/educational_autocomplete_service.py`
- **Grammar**: `domain/grammar_service.py`
- **Authentication**: `core/auth.py`

## Translation Engine

### Core Engine
- **Location**: `src/tau_translator_omega/core_engine/`
- **Parser**: `parser_refactored.py`
- **Translator**: `ilr_translator_refactored.py`
- **Semantic Analyzer**: `semantic_analyzer_refactored.py`

## Launch Points

### Unified Launcher
- **Script**: `tau_translator.py`
- **Command**: `tau-translator` (after installation)
- **Modes**: desktop, web, simple, cli, api

### Direct Launch
- PyQt6 GUI: `python ui/tau_translator_qt_educational_complete.py`
- API Server: `python backend/unified/server.py`
- Web Dev: `cd pwa && npm run dev`

## Deprecated/Archived

The following have been replaced and should not be used:
- All `*_gamified_*.py` files (functionality integrated into educational)
- Original backend implementations (replaced by unified)
- Multiple GUI attempts (consolidated to two PyQt6 versions)
- Scattered test files (moved to `tests/` directory)

## Technology Stack

- **Desktop GUI**: PyQt6 6.0+
- **Web Frontend**: React 18+, Next.js 13+
- **Backend API**: FastAPI 0.68+, Python 3.8+
- **Database**: SQLite (local), PostgreSQL (production ready)
- **Testing**: pytest, pytest-asyncio, pytest-bdd

---
Last Updated: 2025-01-11