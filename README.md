# TauTranslator Professional 🚀

**A comprehensive natural language interface to the IDNI Tau Language ecosystem.**

[![Status](https://img.shields.io/badge/Status-Alpha%20Ready-yellow)](#-current-status)
[![Translation Tests](https://img.shields.io/badge/Translation%20Tests-Working-green)](#-testing-results)
[![Backend](https://img.shields.io/badge/Backend-Multiple%20Options-blue)](#-backend-integration)
[![GUI](https://img.shields.io/badge/GUI-PWA%20%2B%20Qt%20%2B%20Desktop-orange)](#-available-interfaces)

## ⚡ **Current Status: ALPHA READY**

**Current Development Status:**
- ✅ **Translation Engine**: Pattern-based translation with LMQL fallback working
- ✅ **Multiple Backend Options**: Simple, FastAPI, Grammar-aware, and NLP backends
- ✅ **Frontend Integration**: PWA web interface with working translation
- ✅ **Organized Codebase**: Clean project structure with proper separation
- ✅ **Testing Suite**: Comprehensive tests across all components
- ✅ **Documentation**: Complete docs in organized structure

### 🖥️ **Available Interfaces**
1. **PWA Web Interface**: `http://localhost:3000` (Next.js + React) - **Primary**
2. **Qt Desktop GUI**: `src/tau_translator_omega/desktop_gui/main_window.py`
3. **Multiple Backend APIs**: Choose from simple, FastAPI, or specialized backends

### 🔧 **Quick Start Commands**
```bash
# Start the working backend (recommended)
python3 backend/simple_backend.py

# Start PWA (in another terminal)
cd pwa && npm run dev

# Start all backends (comprehensive)
python3 scripts/start_all_backends.py

# Run tests
pytest tests/ -v
```

## 🎯 Overview

TauTranslatorOmega provides **TCE (Tau Controlled English)** - a natural language interface that translates to the formal Tau Language. The system includes multiple translation engines, comprehensive testing, and an alpha-ready web interface.

## 🔑 Key Features

### **Complete Translation System**
- **Bidirectional Translation**: TCE ↔ Tau Language with pattern recognition
- **LMQL Integration**: Advanced translation using language models
- **Fallback Mechanisms**: Multiple translation strategies for reliability
- **Real-time Translation**: Working web interface with live translation

### **Multiple Backend Options**
- **Simple Backend** (`backend/simple_backend.py`): Basic HTTP server - **Recommended for testing**
- **FastAPI Backend** (`backend/backend_server.py`): Full-featured production backend
- **Grammar-aware Backend** (`backend/grammar_aware_backend.py`): Grammar file integration
- **Integrated NLP Backend** (`backend/integrated_nlp_backend.py`): Advanced NLP features

### **Comprehensive Architecture**
- **Organized Structure**: Clean separation of concerns in organized directories
- **Security Layer**: Complete API key management and secure storage
- **Testing Suite**: Unit, integration, and behavioral tests
- **Development Tools**: Code quality analysis and development utilities

## 🏗️ Project Structure

```
TauTranslatorOmega/
├── backend/                  # Multiple backend server options
├── pwa/                     # Progressive Web App (Next.js)
├── src/tau_translator_omega/ # Core translation engine
│   ├── core_engine/         # CNL parser, semantic analyzer, translators
│   ├── lmql_engine/         # LMQL-based translation
│   └── gemma3/              # Gemma 3 model integration
├── scripts/                 # Startup and utility scripts
├── security/                # API key management and security
├── tests/                   # Comprehensive test suite
├── docs/                    # Complete documentation
├── tools/                   # Development and analysis tools
├── examples/                # Usage examples and demos
├── translators/             # Various translator implementations
└── ui/                      # Desktop GUI applications
```

## 🚀 Quick Start

### **Installation**
```bash
git clone https://github.com/your-org/TauTranslatorOmega.git
cd TauTranslatorOmega
pip install -r docs/requirements.txt
```

### **Start the System**
```bash
# Option 1: Simple setup (recommended for testing)
python3 backend/simple_backend.py &
cd pwa && npm run dev

# Option 2: Full production setup
python3 scripts/start_all_backends.py &
cd pwa && npm run dev

# Access the web interface at http://localhost:3000
```

### **Basic Usage**
```python
from src.tau_translator_omega.lmql_engine.bidirectional_translator import LMQLBidirectionalTranslator

# Create translator
translator = LMQLBidirectionalTranslator()

# Translate TCE to Tau
result = translator.translate_tce_to_tau("always x is greater than y")
print(result.output)  # Output: always (x > y)

# Translate Tau to TCE
result = translator.translate_tau_to_tce("r o1[t] = i1[t] & i2[t]")
print(result.output)  # Output: Rule: output 1 at time t equals input 1 at time t AND input 2 at time t
```

## 📊 Translation Examples

### **Working Translation Patterns**
```
TCE: "always x is greater than y"     → Tau: always (x > y)
TCE: "x and y"                        → Tau: x & y
TCE: "not x"                          → Tau: x'
TCE: "x or y"                         → Tau: x | y
Tau: "r o1[t] = i1[t] & i2[t]"       → TCE: "Rule: output 1 at time t equals input 1 at time t AND input 2 at time t"
```

### **Backend API Usage**
```bash
# Test translation endpoint
curl -X POST http://localhost:8000/api/translate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"sourceText": "always x > y", "sourceLangKey": "PLAIN_ENGLISH", "targetLangKey": "TAU"}'
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test categories
pytest tests/core_engine/ -v          # Core engine tests
pytest tests/integration/ -v          # Integration tests
pytest tests/nlp/ -v                  # NLP tests

# Run with coverage
pytest --cov=src tests/ --cov-report=html
```

## 📚 Documentation

### **Core Documents**
- **[docs/PROJECT_STATUS.md](docs/PROJECT_STATUS.md)**: Current project status
- **[docs/PRODUCTION_README.md](docs/PRODUCTION_README.md)**: Production deployment guide
- **[docs/TESTING_GUIDE.md](docs/TESTING_GUIDE.md)**: Comprehensive testing documentation
- **[docs/FASTAPI_BACKEND_GUIDE.md](docs/FASTAPI_BACKEND_GUIDE.md)**: Backend setup guide

### **Technical Specifications**
- **[docs/TRANSLATION_PIPELINE_EXPLAINED.md](docs/TRANSLATION_PIPELINE_EXPLAINED.md)**: Translation system architecture
- **[docs/SEMANTIC_ANALYSIS_ALGORITHMS_REPORT.md](docs/SEMANTIC_ANALYSIS_ALGORITHMS_REPORT.md)**: Semantic analysis details

## 🛠️ Development Tools

```bash
# Code quality analysis
python3 tools/code_quality_tool.py

# Debug utilities
python3 tools/debug_utilities.py

# Check backend status
python3 tools/check_backend_status.py
```

## 🔮 Roadmap

### **Current: Production Deployment**
- ✅ Multiple working backends
- ✅ Production-ready PWA interface
- ✅ Comprehensive testing suite
- ✅ Complete documentation

### **Next: Enhanced Features**
- LLM provider integration
- Advanced grammar file processing
- Real-time collaborative editing
- API ecosystem expansion

### **Future: Enterprise Features**
- IDE plugins and extensions
- Enterprise security features
- Industry-specific adaptations
- Advanced AI assistance

## 🤝 Contributing

We welcome contributions! The project has:
- Clean, organized codebase structure
- Comprehensive test coverage
- Detailed documentation
- Multiple development tools

Feel free to:
- Report bugs and request features
- Submit pull requests
- Improve documentation
- Add new test cases

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **IDNI Team**: For the innovative Tau Language
- **Tau Community**: For real-world demos and feedback
- **Open Source Community**: For the tools and frameworks used

---

**Author: DarkLightX / Dana Edwards**

**TauTranslatorOmega: An alpha-ready bridge between natural language and formal Tau Language specifications.**