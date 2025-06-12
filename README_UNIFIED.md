# TauTranslator - Unified Edition

## Quick Start

```bash
# Install (one-time setup)
python setup.py install

# Launch
tau-translator              # Interactive menu
tau-translator desktop      # PyQt6 desktop GUI
tau-translator web         # React web interface
tau-translator api         # FastAPI server only
```

## What is TauTranslator?

TauTranslator is an educational tool for learning formal specification languages:
- **TAU**: A temporal logic specification language
- **TCE**: Tau Controlled English (natural language interface to TAU)

## Features

### 📚 Educational System
- Interactive learning with progress tracking
- Achievement system for milestones
- Skill monitoring across different areas
- Daily challenges and goals

### 🤖 Intelligent Autocomplete
- Context-aware suggestions with explanations
- Examples for every keyword and pattern
- Difficulty-based learning progression
- Real-time syntax help

### 🖥️ Multiple Interfaces
- **PyQt6 Desktop GUI**: Full-featured desktop application with educational features
- **React Web App**: Modern Progressive Web App with Next.js
- **Command Line**: Terminal interface for quick translations
- **FastAPI Server**: REST API with automatic documentation

## Installation

### Option 1: System Install (Recommended)
```bash
git clone https://github.com/YourUsername/TauTranslator.git
cd TauTranslator
python setup.py install
```

### Option 2: Development Mode
```bash
pip install -e .  # Editable install
```

### Option 3: Direct Run
```bash
python tau_translator.py
```

## Repository Structure

```
TauTranslator/
├── tau_translator.py      # Unified launcher
├── setup.py              # Installation script
├── backend/unified/      # Core backend services
├── ui/                   # Desktop GUI implementations
├── pwa/                  # Web application
├── src/                  # Core translation engine
├── tests/                # Test suite
└── docs/                 # Documentation
```

## Usage Examples

### PyQt6 Desktop Application
```bash
tau-translator desktop
```
- Type TAU keywords to see educational suggestions
- Use intelligent autocomplete with examples
- Complete translations with instant feedback
- Track your learning progress with achievements

### Web Interface
```bash
tau-translator web
```
Opens at http://localhost:3000
- Modern web-based interface
- Same gamification features
- Works on mobile devices

### Command Line
```bash
echo "for all x such that x > 0" | tau-translator cli
# Output: forall x : x > 0
```

### API Server
```bash
tau-translator api
# Server runs at http://localhost:8000
# API docs at http://localhost:8000/docs
```

## Learning Path

1. **Start with Desktop GUI**
   - Launch with `tau-translator desktop`
   - Begin with simple keywords: always, exists, forall
   - Follow the autocomplete suggestions
   - Complete daily challenges

2. **Progress Through Levels**
   - Level 1-3: Basic keywords and operators
   - Level 4-6: Temporal logic and quantifiers
   - Level 7-9: Complex patterns and streams
   - Level 10: Master certification

3. **Practice with Examples**
   - Try temporal properties: `always (door_locked)`
   - Use quantifiers: `forall x : x > 0`
   - Solve constraints: `solve x = y + 2`

## Configuration

Settings are stored in:
- Linux: `~/.config/tau-translator/`
- macOS: `~/Library/Application Support/tau-translator/`
- Windows: `%APPDATA%\tau-translator\`

## Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### Backend server not starting
```bash
# Check if port 8000 is in use
lsof -i :8000  # Linux/macOS
netstat -ano | findstr :8000  # Windows
```

### Autocomplete not working
- Ensure you're in TAU or TCE mode
- Check backend is running: `tau-translator api`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Follow the Intentional Disclosure Principle (see `docs/IDP.md`)
4. Submit a pull request

## License

MIT License - See LICENSE file

## Acknowledgments

- TAU Language community
- Contributors and testers
- Educational gamification research

---

For detailed gamification features, see [GAMIFIED_EDITION_README.md](GAMIFIED_EDITION_README.md)

For development docs, see [docs/](docs/)