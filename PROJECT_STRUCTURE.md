# TauTranslator Project Structure

## Directory Organization

```
TauTranslator/
├── backend/                      # Backend services
│   ├── tau_translator_server.py  # Main backend server
│   └── unified/                  # Unified backend API
│       ├── api/                  # API endpoints
│       ├── core/                 # Core backend logic
│       └── translators/          # Translation implementations
│
├── docs/                         # Documentation
│   ├── API guides               # API documentation
│   ├── Frontend guides          # Frontend documentation
│   └── Technical specs          # Technical specifications
│
├── examples/                     # Example code and demos
│   ├── *.py                     # Python examples
│   └── *.tce                    # TCE examples
│
├── grammars/                     # Grammar files
│   ├── tau.tgf                  # Tau grammar
│   └── tce_tau_accurate.ebnf   # EBNF grammar
│
├── pwa/                         # Progressive Web App (Next.js)
│   ├── pages/                   # Next.js pages
│   ├── components/              # React components
│   └── styles/                  # CSS styles
│
├── reports/                     # Analysis and test reports
│   ├── quality reports          # Code quality analysis
│   ├── test results             # Test execution results
│   └── analysis documents       # Various analyses
│
├── scripts/                     # Utility scripts
│   ├── analysis/                # Analysis scripts
│   ├── demos/                   # Demo scripts
│   └── setup/                   # Setup scripts
│
├── src/tau_translator_omega/    # Main source code
│   ├── core_engine/             # Core translation engine
│   ├── lmql_engine/             # LMQL integration
│   ├── vocabulary/              # Domain vocabulary
│   └── llm_services/            # LLM service integrations
│
├── tests/                       # Test suite
│   ├── core_engine/             # Core engine tests
│   ├── integration/             # Integration tests
│   ├── features/                # BDD feature tests
│   └── mutation/                # Mutation testing
│
├── tools/                       # Development tools
│   ├── code_quality_analyzer.py # Code quality tool
│   └── deep_codebase_analyzer.py # Codebase analysis
│
├── translators/                 # Standalone translators
│   └── tau_language_translator.py # Production translator
│
└── ui/                         # Desktop user interfaces
    ├── tau_translator_desktop_qt.py      # PyQt6 interface (recommended)
    ├── tau_translator_desktop_tkinter.py # Tkinter interface
    └── splash_screen.py                  # Loading screen
```

## Key Files

### Production Components
- **Backend Server**: `backend/tau_translator_server.py`
- **Unified API**: `backend/unified/server.py`
- **Desktop GUI (Qt)**: `ui/tau_translator_desktop_qt.py`
- **Desktop GUI (Tkinter)**: `ui/tau_translator_desktop_tkinter.py`
- **Web Interface**: `pwa/pages/index.js`
- **Production Translator**: `translators/tau_language_translator.py`

### Configuration
- **Python Project**: `pyproject.toml`
- **Git Ignore**: `.gitignore`
- **PWA Config**: `pwa/package.json`

### Scripts
- **Build Desktop App**: `scripts/build_desktop_app.py`
- **Start All Backends**: `scripts/start_all_backends.py`
- **Setup Gemma Model**: `scripts/setup_gemma_model.py`

## Development Workflow

1. **Backend Development**: Work in `backend/` and `src/tau_translator_omega/`
2. **Frontend Development**: Work in `pwa/` for web, `ui/` for desktop
3. **Testing**: Run tests from `tests/` directory
4. **Analysis**: Use tools in `tools/` directory
5. **Documentation**: Update docs in `docs/` directory

## Naming Conventions

- **Python Files**: `snake_case.py`
- **Production Files**: Descriptive names (e.g., `tau_translator_server.py`)
- **Test Files**: `test_*.py`
- **Config Files**: Standard names (e.g., `pyproject.toml`)
- **Reports**: Include timestamps in filename when generated