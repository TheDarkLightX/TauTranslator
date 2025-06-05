# Tau Translator Alpha 🚀

**A comprehensive natural language interface to the IDNI Tau Language ecosystem.**

[![Status](https://img.shields.io/badge/Status-Alpha%20Ready-yellow)](#-current-status)
[![Translation Tests](https://img.shields.io/badge/Translation%20Tests-Working-green)](#-testing-results)
[![Backend](https://img.shields.io/badge/Backend-Multiple%20Options-blue)](#-backend-integration)
[![GUI](https://img.shields.io/badge/GUI-PWA%20%2B%20Qt%20%2B%20Desktop-orange)](#-available-interfaces)

## ⚡ **Current Status: ALPHA READY**

**Current Development Status:**
- ✅ **Translation Engine**: Pattern-based translation with LMQL fallback working
- ✅ **Unified Backend**: FastAPI-based unified backend with modular translators
- ✅ **Frontend Integration**: PWA web interface with working translation
- ✅ **Organized Codebase**: Clean project structure with proper separation
- ✅ **Testing Suite**: Comprehensive tests across all components
- ✅ **Documentation**: Complete docs in organized structure

### 🖥️ **Available Interfaces**
1. **PWA Web Interface**: `http://localhost:3000` (Next.js + React)
2. **PyQt6 Desktop GUI**: `ui/tau_translator_desktop_qt.py` - **Recommended**
3. **Tkinter Desktop GUI**: `ui/tau_translator_desktop_tkinter.py` - Lightweight option
4. **Unified Backend API**: `backend/unified/server.py` - FastAPI backend

### 🔧 **Quick Start Commands**
```bash
# Start the unified backend
python3 backend/unified/server.py

# Start PWA (in another terminal)
cd pwa && npm run dev

# Or run the desktop GUI (PyQt6)
python3 ui/tau_translator_desktop_qt.py

# Run tests
pytest tests/ -v
```

## 🎯 Overview

Tau Translator Alpha provides **TCE (Tau Controlled English)** - a natural language interface that translates to the formal Tau Language. The system includes multiple translation engines, comprehensive testing, and both web and desktop interfaces.

## 🔑 Key Features

### **Complete Translation System**
- **Bidirectional Translation**: TCE ↔ Tau Language with pattern recognition
- **LMQL Integration**: Advanced translation using language models
- **Fallback Mechanisms**: Multiple translation strategies for reliability
- **Real-time Translation**: Working web interface with live translation

### **Unified Backend Architecture**
- **Unified Backend** (`backend/unified/server.py`): Production-ready FastAPI server with modular translator system
- **Pattern Translator**: Fast pattern-based translation for common constructs
- **Grammar Translator**: Grammar-aware translation with Lark parser integration
- **NLP Translator**: Advanced natural language processing capabilities
- **LMQL Translator**: AI-powered translation with Language Model Query Language

### **Comprehensive Architecture**
- **Organized Structure**: Clean separation of concerns in organized directories
- **Security Layer**: Complete API key management and secure storage
- **Testing Suite**: Unit, integration, and behavioral tests
- **Development Tools**: Code quality analysis and development utilities

## 🏗️ Project Structure

```
TauTranslator/
├── backend/unified/         # Unified FastAPI backend
│   ├── server.py           # Main server application
│   ├── api/                # API endpoints (auth, translate, grammar, nlp)
│   ├── core/               # Core functionality (config, auth, responses)
│   └── translators/        # Modular translator implementations
├── pwa/                     # Progressive Web App (Next.js)
├── src/tau_translator_omega/ # Core translation engine
│   ├── core_engine/         # CNL parser, semantic analyzer, AST
│   ├── lmql_engine/         # LMQL-based translation
│   └── llm_services/        # LLM integration services
├── scripts/                 # Startup and utility scripts
├── security/                # API key management and security
├── tests/                   # Comprehensive test suite
├── docs/                    # Complete documentation
├── tools/                   # Development and analysis tools
├── examples/                # Usage examples and demos
├── translators/             # Legacy translator implementations
└── ui/                      # Desktop GUI applications
    ├── tau_translator_desktop_qt.py     # PyQt6 interface
    ├── tau_translator_desktop_tkinter.py # Tkinter interface
    └── tau_translator_desktop_modern.py  # Modern UI concept
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
# Start the unified backend and web interface
python3 backend/unified/server.py &
cd pwa && npm run dev

# Access the web interface at http://localhost:3000
# API documentation available at http://localhost:8000/docs
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
- **[docs/PRODUCTION_READY_SUMMARY.md](docs/PRODUCTION_READY_SUMMARY.md)**: Production deployment guide
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

### **Current: Alpha Release**
- ✅ Unified backend architecture
- ✅ Production-ready PWA interface
- ✅ Comprehensive testing suite
- ✅ Complete documentation
- ✅ Multiple desktop GUI options (PyQt6, Tkinter)

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

## 🛡️ Security & Privacy

- **Local-first**: All core translation runs locally
- **API Key Management**: Secure storage for LLM providers
- **No telemetry**: Your code stays private
- **Open source**: Full transparency

## 🙏 Acknowledgments

- **IDNI Team**: For the innovative Tau Language
- **Tau Community**: For real-world demos and feedback
- **Open Source Community**: For the tools and frameworks used

---

**Author: DarkLightX / Dana Edwards**

**Tau Translator Alpha: An alpha-ready bridge between natural language and formal Tau Language specifications.**