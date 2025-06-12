# Test Organization Guide
========================

This document describes the organization of tests in the TauTranslator project.

## Directory Structure

```
tests/
├── unit/                      # Unit tests for individual components
│   ├── test_*.py             # Python unit tests
│   └── ...
├── integration/              # Integration tests
│   ├── test_nlp_autocomplete_api.py  # Backend API integration tests
│   └── ...
├── frontend/                 # Frontend tests (React/PWA)
│   ├── components/          # React component tests
│   │   └── AutoCompleteTextarea.test.js
│   └── api/                 # Frontend API tests
│       └── translate-backend.test.js
├── ui/                      # Desktop UI tests (PyQt)
│   └── test_tau_translator_qt_autocomplete.py
├── features/                # BDD feature tests
│   ├── api/                # API behavior tests
│   ├── translation/        # Translation behavior tests
│   └── ...
├── performance/            # Performance tests
├── fixtures/               # Test fixtures and data
└── ...
```

## Test Categories

### 1. Unit Tests (`tests/unit/`)
- Individual component tests
- No external dependencies
- Fast execution
- Follow FIRST principles

### 2. Integration Tests (`tests/integration/`)
- Test component interactions
- May use mocked external services
- Backend API tests
- Service integration tests

### 3. Frontend Tests (`tests/frontend/`)
- React component tests using Jest/Testing Library
- API client tests
- UI interaction tests
- Autocomplete functionality tests

### 4. UI Tests (`tests/ui/`)
- PyQt desktop application tests
- GUI interaction tests
- Theme switching tests
- Keyboard shortcut tests

### 5. Feature Tests (`tests/features/`)
- BDD-style tests using Gherkin syntax
- End-to-end scenarios
- User story validation

## Running Tests

### Python Tests
```bash
# Run all Python tests
pytest

# Run specific test category
pytest tests/unit/
pytest tests/integration/
pytest tests/ui/

# Run with coverage
pytest --cov=src tests/
```

### JavaScript Tests
```bash
# Run frontend tests
cd pwa && npm test

# Or from root
npm --prefix pwa test

# Run specific test file
npm --prefix pwa test -- tests/frontend/components/AutoCompleteTextarea.test.js
```

### BDD Tests
```bash
# Run feature tests
pytest tests/features/

# Run specific feature
pytest tests/features/translation/
```

## Test Naming Conventions

### Python Tests
- Test files: `test_*.py`
- Test classes: `Test*`
- Test methods: `test_given_*_when_*_then_*` (BDD style)

### JavaScript Tests
- Test files: `*.test.js`
- Test suites: `describe('Component/Feature', () => {})`
- Test cases: `test('given_*_when_*_then_*', () => {})`

## Best Practices

1. **Follow FIRST Principles**
   - Fast
   - Independent/Isolated
   - Repeatable
   - Self-Validating
   - Timely

2. **Use Test Builders**
   - Create builder classes for complex test data
   - Improves test readability
   - Reduces duplication

3. **Mock External Dependencies**
   - Mock API calls
   - Mock file system operations
   - Mock database connections

4. **Test Edge Cases**
   - Boundary values
   - Error conditions
   - Empty/null inputs
   - Large data sets

5. **Maintain Test Quality**
   - Refactor tests like production code
   - Remove duplication
   - Keep tests simple and focused

## AutoComplete Test Coverage

The autocomplete functionality is tested at multiple levels:

1. **Component Tests** (`tests/frontend/components/AutoCompleteTextarea.test.js`)
   - UI behavior
   - Keyboard navigation
   - Mouse interactions
   - Debouncing

2. **API Tests** (`tests/frontend/api/translate-backend.test.js`)
   - Request handling
   - Error handling
   - Fallback behavior
   - Backend failover

3. **Backend Integration** (`tests/integration/test_nlp_autocomplete_api.py`)
   - NLP service integration
   - Suggestion generation
   - Validation
   - Performance

4. **Desktop UI** (`tests/ui/test_tau_translator_qt_autocomplete.py`)
   - PyQt integration
   - Completer widget
   - Theme compatibility
   - Keyboard shortcuts

## Continuous Integration

Tests are automatically run on:
- Every commit (pre-commit hooks)
- Pull requests
- Main branch merges

Failed tests block deployment to ensure quality.