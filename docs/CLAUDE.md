# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TauTranslatorOmega is a comprehensive natural language interface to the IDNI Tau Language ecosystem. It translates between TCE (Tau Controlled English) and formal Tau Language specifications, making formal methods accessible to non-experts.

## Memories

- When adding the author of any file, it's DarklightX or Dana Edwards. This name must be the author of all documents we create.

## Architecture

The project consists of:

1. **Core Translation Engine** (`src/tau_translator_omega/core_engine/`)
   - CNL Parser with AST nodes for natural language processing
   - Semantic Analyzer with type checking and inference
   - Enhanced NLP Module with AMR semantic analysis
   - Incremental Parser with intelligent caching
   - TCE-to-Tau translator with bidirectional translation support
   - Plugin system for extensibility
   - Grammar processing with Lark parser

2. **Multiple User Interfaces**
   - Qt Desktop GUI: `src/tau_translator_omega/desktop_gui/main_window.py`
   - PWA Web Interface: `pwa/` (Next.js/React)
   - Tkinter desktop apps: Various `*_tau_translator.py` files

3. **Backend Services**
   - Simple HTTP backend: `simple_backend.py`
   - FastAPI server: `backend_server.py`
   - LLM configuration service: `src/tau_translator_omega/llm_config_service/`

## Commands

### Testing
```bash
# Run all tests with verbose output
pytest tests/ -v

# Run tests with coverage report
python run_tests.py --mode unit

# Run all tests including integration
python run_tests.py --mode all

# Run comprehensive Qt integration tests
python comprehensive_qt_integration_test.py

# Run specific test file
pytest tests/core_engine/test_tce_tau_translator.py -v

# Run semantic analyzer tests
pytest tests/core_engine/test_analyzer_*.py -v

# Run semantic analyzer performance tests
pytest tests/core_engine/test_semantic_analyzer_performance.py -v

# Run advanced semantic analysis tests
pytest tests/core_engine/test_semantic_analyzer_advanced.py -v

# Run enhanced NLP tests
pytest tests/core_engine/test_nlp_enhanced.py -v
```

### Development
```bash
# Install in development mode
pip install -e .

# Start backend server
python simple_backend.py

# Start PWA development server (from pwa/ directory)
cd pwa && npm run dev

# Run Qt GUI
python src/tau_translator_omega/desktop_gui/main_window.py

# Lint code (max line length 88, Black-compatible)
flake8
```

### PWA Commands
```bash
# From pwa/ directory
npm run dev    # Development server on port 3000
npm run build  # Production build
npm run lint   # ESLint
```

## Key Translation Flow

1. TCE input → CNL Parser → AST
2. AST → Semantic Analyzer → Validated AST
3. Validated AST → TCE-to-Tau Translator → Tau output
4. Supports bidirectional translation (Tau → TCE)

## Important Files

- `grammars/tce_tau_accurate.ebnf` - Complete TCE grammar specification
- `examples/tce_tau_accurate_examples.tce` - Real-world TCE examples
- `docs/tce_specification.md` - TCE language specification
- `pytest.ini` - Test configuration with markers and coverage settings

## Test Markers

- `unit` - Unit tests for individual components
- `integration` - Integration tests
- `security` - Security-focused tests
- `performance` - Performance benchmarks
- `slow` - Long-running tests
- `crypto` - Tests requiring cryptography

## Semantic Analyzer

The semantic analyzer (`src/tau_translator_omega/core_engine/semantic_analyzer.py`) provides:

### Features
- **Type System**: Supports integer, string, boolean, real, and auto (inferred) types
- **Type Checking**: Validates type compatibility in assignments and expressions
- **Type Inference**: Automatically infers types for 'auto' declarations
- **Symbol Table**: Hierarchical scoping with O(1) lookup performance
- **Error Recovery**: Collects multiple errors for comprehensive reporting
- **Predicate/Function Validation**: Arity checking and signature validation

### Performance Characteristics
- **Symbol Lookup**: O(1) average case
- **Type Checking**: O(1) per operation
- **Full Analysis**: O(n) single-pass algorithm
- **Memory Usage**: < 100 bytes per symbol

### Type System Rules
```
integer → number
real → number
auto → accepts any type during assignment
```

### Future Optimization Opportunities
- Binary Decision Diagrams (BDDs) for complex type hierarchies
- Incremental analysis for real-time editing
- Parallel analysis for independent modules

## Enhanced NLP Module

The enhanced NLP module (`src/tau_translator_omega/core_engine/nlp_enhanced/`) provides state-of-the-art natural language processing:

### Features
- **AMR Semantic Analysis**: Abstract Meaning Representation for deep semantic understanding
- **Incremental Parsing**: O(log n) parsing for small edits with intelligent caching
- **Semantic Role Labeling**: Automatic predicate-argument structure detection
- **Coreference Resolution**: Cross-reference tracking for complex expressions
- **Real-time Error Recovery**: Graceful handling of partial and malformed input

### AMR Semantic Layer
```python
# Extract semantic roles from TCE
amr_analyzer = AMRSemanticAnalyzer()
amr_graph = amr_analyzer.analyze(ast_node)
roles = amr_analyzer.get_semantic_roles(amr_graph, "prime")
```

### Incremental Parser
```python
# Real-time parsing with caching
parser = IncrementalTCEParser()
ast, metadata = parser.parse(new_text, previous_text, previous_ast)
# metadata includes: parse_time, cache_hit, incremental flags
```

### Performance Characteristics
- **Cache Hit Rate**: 85%+ for typical editing patterns
- **Incremental Speedup**: 3-5x faster for small edits
- **Memory Usage**: LRU cache with configurable size limits
- **Parse Time**: Sub-millisecond for cached results

### Supported NLP Features
- Predicate-argument structure extraction
- Quantifier scope analysis
- Temporal and modal operator handling
- Cross-sentence coreference (planned)
- Contextual disambiguation (planned)

## Current Status

- Production ready (Phase 3 complete)
- 100% translation test success rate
- Sub-millisecond translation performance
- Comprehensive semantic analysis with type safety
- Multiple UI options available
- LMQL-powered solution integrated

## Personal Instructions

- Always create a todo list.