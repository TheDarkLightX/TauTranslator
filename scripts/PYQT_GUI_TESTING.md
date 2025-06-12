# PyQt GUI Testing Guide
=======================

This guide explains how to test the Tau Translator PyQt GUI, including the new autocomplete functionality.

## Available GUI Versions

1. **Original PyQt GUI** (`ui/tau_translator_desktop_qt.py`)
   - Full-featured desktop application
   - Syntax highlighting for TAU
   - File operations
   - Theme switching
   - No autocomplete

2. **Enhanced AutoComplete GUI** (`ui/tau_translator_desktop_qt_autocomplete.py`)
   - Simplified interface focused on autocomplete
   - AutoComplete for TAU and CNL languages
   - Real-time suggestions as you type
   - Fallback suggestions when backend unavailable

## Quick Start

### 1. Check Dependencies
```bash
python scripts/test_pyqt_gui.py
```
This will check if PyQt is installed and if the backend is running.

### 2. Run AutoComplete Demo
```bash
python scripts/demo_pyqt_autocomplete.py
```
This launches the enhanced GUI with autocomplete functionality.

### 3. Run Full Test Suite
```bash
pytest tests/ui/test_tau_translator_qt_autocomplete.py -v
```

## Testing AutoComplete

### Manual Testing Steps

1. **Launch the AutoComplete GUI**:
   ```bash
   python ui/tau_translator_desktop_qt_autocomplete.py
   ```

2. **Test Basic AutoComplete**:
   - Select "TAU" as the input language
   - Start typing "for" in the left editor
   - After ~300ms, suggestions should appear:
     - `forall` - Universal quantification
     - `for every` - Alternative form
   - Use arrow keys to navigate suggestions
   - Press Tab or Enter to accept
   - Press Escape to cancel

3. **Test Different Keywords**:
   - Type "al" → should suggest `always`
   - Type "ex" → should suggest `exists`
   - Type ":" → should suggest `:=` (definition operator)
   - Type "-" → should suggest `->` (implication)

4. **Test Language Switching**:
   - AutoComplete should only work for TAU and CNL
   - Switch to PLAIN_ENGLISH → no autocomplete
   - Switch back to TAU → autocomplete re-enabled

5. **Test Syntax Highlighting**:
   - In TAU mode, keywords should be highlighted:
     - Keywords (blue): `always`, `forall`, `exists`
     - Operators (red): `:=`, `->`, `<->`
     - Comments (gray): `// comment`

## Backend Integration

### With Backend Running
If the unified backend is running on port 8000:
- AutoComplete will fetch suggestions from `/api/nlp/autocomplete`
- More intelligent, context-aware suggestions
- NLP-powered completions

### Without Backend (Fallback Mode)
If no backend is available:
- Basic keyword/operator suggestions
- Still functional but limited to predefined TAU keywords
- Good for offline testing

## Running Backend for Full Experience

1. **Start the Backend**:
   ```bash
   cd backend/unified
   python -m uvicorn server:app --port 8000
   ```

2. **Verify Backend**:
   ```bash
   curl http://localhost:8000/health
   ```

3. **Test AutoComplete Endpoint**:
   ```bash
   curl -X POST http://localhost:8000/api/nlp/autocomplete \
        -H "Content-Type: application/json" \
        -d '{"text": "for", "language": "TAU"}'
   ```

## PyQt Version Compatibility

### PyQt6 (Recommended)
```bash
pip install PyQt6
```
The GUIs are written for PyQt6 and work best with it.

### PyQt5 (Fallback)
```bash
pip install PyQt5
```
The test runner includes PyQt5 compatibility mode that automatically adjusts imports.

## Automated Testing

### Unit Tests
Located in `tests/ui/test_tau_translator_qt_autocomplete.py`:
- Component initialization
- AutoComplete triggering
- Keyboard navigation
- Theme switching
- Translation functionality

### Run Specific Test Categories
```bash
# Test only autocomplete functionality
pytest tests/ui/test_tau_translator_qt_autocomplete.py::TestAutoCompleteFunctionality -v

# Test keyboard shortcuts
pytest tests/ui/test_tau_translator_qt_autocomplete.py::TestKeyboardShortcuts -v
```

## Common Issues

### 1. Import Errors
If you see PyQt import errors:
```bash
# Check which PyQt is installed
python -c "import PyQt6; print('PyQt6 OK')" 2>/dev/null || python -c "import PyQt5; print('PyQt5 OK')"
```

### 2. No AutoComplete Popup
- Ensure you're in TAU or CNL mode
- Type at least 1 character
- Wait 300ms for debounce
- Check console for errors

### 3. Backend Connection Failed
- AutoComplete will still work with fallback suggestions
- To get full NLP suggestions, start the backend

## Development Tips

### Adding New Suggestions
Edit the fallback suggestions in `AutoCompleteService._generate_fallback_suggestions()`:
```python
tau_keywords = [
    AutoCompleteSuggestion('your_keyword', 'type', 'Description'),
    # Add more...
]
```

### Adjusting Debounce Time
Change the timer delay in `CodeEditorWithAutoComplete._trigger_autocomplete()`:
```python
self.autocomplete_timer.start(300)  # milliseconds
```

### Styling the Popup
Modify the stylesheet in `CodeEditorWithAutoComplete._setup_completer()` to change appearance.

## Test Checklist

- [ ] AutoComplete appears for TAU language
- [ ] AutoComplete appears for CNL language
- [ ] No autocomplete for PLAIN_ENGLISH
- [ ] Keyboard navigation works (arrows, Tab, Escape)
- [ ] Mouse click selects suggestion
- [ ] Syntax highlighting works for TAU
- [ ] Language swap preserves text and settings
- [ ] Translation preserves formatting
- [ ] Status bar shows helpful messages
- [ ] No errors in console

## Performance Testing

1. **Type Speed Test**: Type quickly to ensure debouncing works
2. **Large Text**: Paste large TAU code to test syntax highlighting performance
3. **Rapid Language Switching**: Switch languages rapidly to test state management

Happy Testing! 🎯