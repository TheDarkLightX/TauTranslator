# TauTranslator Frontend Guide
==============================

The TauTranslator has a modern Progressive Web App (PWA) frontend built with Next.js and React.

## Access the Frontend

1. **URL**: http://localhost:3000
2. **Alternative URL**: http://localhost:3002 (if multiple instances running)

## Main Interface Features

### 1. **Translation Interface** (Home Page)
- **Two text areas**:
  - Left: Source text input (TCE or Tau)
  - Right: Translation output
- **Language selectors**: Choose source and target languages
- **Translate button**: Performs the translation
- **Swap button**: Reverses translation direction

### 2. **Menu Bar**
- **File Menu**:
  - New: Clear translation
  - Open: Load saved translations
  - Save: Save current translation
  - Export: Export as different formats
  
- **Edit Menu**:
  - Copy/Paste operations
  - Clear all
  
- **View Menu**:
  - Theme toggle (Light/Dark mode)
  - Layout options
  
- **Tools Menu**:
  - Grammar file manager
  - Settings
  - Debug console

### 3. **Settings Page** (`/settings`)
- **LLM Configuration**: Configure AI providers
- **Grammar Files**: Load and manage .tgf grammar files
- **API Keys**: Secure key management
- **Model Selection**: Choose translation models

### 4. **Professional Mode** (`/professional`)
- Advanced translation features
- Multiple panes for complex workflows
- Grammar visualization
- AST tree view (when available)

## Key Pages to Visit

1. **Main Translation**: http://localhost:3000
2. **Settings**: http://localhost:3000/settings
3. **LLM Config**: http://localhost:3000/settings/llm
4. **Professional Mode**: http://localhost:3000/professional

## How to Use

### Basic Translation:
1. Open http://localhost:3000
2. Select "TCE" as source language
3. Select "Tau" as target language
4. Enter TCE text like: "Always x and y."
5. Click "Translate"
6. See result: "always (x & y)"

### Reverse Translation:
1. Click the swap button (⇄)
2. Enter Tau code: "forall x : x > 0"
3. Click "Translate"
4. See TCE result: "For all x such that x greater than 0."

### Grammar File Management:
1. Go to Settings → LLM Configuration
2. Click "Grammar Files" tab
3. Upload .tgf files
4. Select active grammar
5. Grammar affects translation behavior

## Frontend Technologies

- **Framework**: Next.js 14 (React)
- **Styling**: CSS Modules
- **State Management**: React Context API
- **API Communication**: Fetch API
- **UI Components**: Custom React components

## Visual Features

- **Dark/Light Theme**: Toggle in View menu
- **Responsive Design**: Works on desktop and mobile
- **Real-time Translation**: Fast response times
- **Error Handling**: Clear error messages
- **Loading States**: Visual feedback during translation

## Backend Connection

The frontend connects to:
- **Simple Backend**: Port 8000 (default)
- **Working Backend**: Port 8003 (enhanced)
- **API Endpoints**:
  - `/translate`: Main translation endpoint
  - `/health`: Backend status
  - `/grammar/*`: Grammar file operations

## Tips

1. **Use Natural Language**: Type comparisons as "greater than" not ">"
2. **Check Examples**: The backend provides example translations
3. **Test Bidirectional**: Try translating back and forth
4. **Save Your Work**: Use File → Save for important translations