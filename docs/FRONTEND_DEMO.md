# TauTranslator Frontend Demo
============================

## 🎨 Live Frontend Interface

**Access URL**: http://localhost:3000

## Interface Layout

```
┌─────────────────────────────────────────────────────────────────┐
│                   Tau Language Translator                       │
│                                                                 │
│  [💼 Professional UI] [⚙️ Settings]     🔓 Authenticated [Logout] │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Plain English    ⇄    [Tau Language Code ▼]    [Translate]   │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ ┌─ Plain English ─────────┐ ┌─ Tau Language Code ─────────┐    │
│ │                         │ │                             │    │
│ │ Enter Plain English     │ │ Translation appears here... │    │
│ │ here...                 │ │                             │    │
│ │                         │ │                             │    │
│ │                         │ │                             │    │
│ │                         │ │                             │    │
│ │                         │ │                             │    │
│ │                         │ │                             │    │
│ └─────────────────────────┘ └─────────────────────────────┘    │
│                                                                 │
│ Backend Status: ✅ Connected                                    │
└─────────────────────────────────────────────────────────────────┘
```

## How to Use the Frontend

### 1. **Basic Translation**
1. Open http://localhost:3000
2. Type in left panel: `"Always x and y."`
3. Select "Tau Language Code" in dropdown
4. Click "Translate"
5. See result in right panel: `"always (x & y)"`

### 2. **Authentication**
- Click "Login" if not authenticated
- Enter password: `test123`
- System remembers authentication

### 3. **Language Swapping**
- Click the ⇄ button to reverse translation direction
- Left panel becomes Tau input
- Right panel becomes Plain English output

### 4. **Settings Page**
- Click "⚙️ Settings" to access configuration
- Manage grammar files
- Configure AI providers
- View system status

### 5. **Professional Mode**
- Click "💼 Professional UI" for advanced features
- Multiple panes
- Enhanced workflow
- Grammar visualization

## Example Translations You Can Try

### Simple Boolean Logic
```
Input:  "x and y or z"
Output: "(x & y | z)"
```

### Temporal Logic
```
Input:  "Always x implies sometimes y"
Output: "always x -> sometimes y"
```

### Natural Language Comparisons
```
Input:  "x greater than 0 and y less than 10"
Output: "x > 0 & y < 10"
```

### Quantifiers
```
Input:  "For all x such that P(x)"
Output: "forall x : P(x)"
```

### Complex Expressions
```
Input:  "For all x such that x greater than 0 implies f(x) equals 1"
Output: "forall x : x > 0 -> f(x) = 1"
```

## Backend Connection Status

The frontend automatically detects and connects to available backends:

- **✅ Working Backend**: Port 8003 (recommended)
- **⚠️ Simple Backend**: Port 8000 (basic)
- **❌ No Backend**: Shows connection error

## Visual Features

### Theme Support
- **Light Mode**: Clean, professional appearance
- **Dark Mode**: Easy on the eyes for extended use
- Toggle in View menu

### Responsive Design
- Works on desktop browsers
- Adapts to different window sizes
- Mobile-friendly layout

### Real-time Feedback
- Loading indicators during translation
- Error messages for failed translations
- Success indicators for completed translations

### Authentication Status
- 🔓 Green indicator when authenticated
- 🔒 Red indicator when not authenticated
- Clear login/logout controls

## Advanced Features

### Settings Page (`/settings`)
- **LLM Configuration**: Set up AI providers
- **Grammar Files**: Upload and manage .tgf files
- **API Keys**: Secure credential management
- **Model Selection**: Choose translation models

### Professional Mode (`/professional`)
- Multi-pane interface
- Side-by-side comparisons
- Grammar file visualization
- Advanced translation options

## Testing the Interface

1. **Open your browser** to http://localhost:3000
2. **Try basic translation**: Type simple sentences and see immediate results
3. **Test complex examples**: Use the examples above
4. **Explore settings**: Check grammar file management
5. **Try professional mode**: See advanced features

The frontend provides a clean, user-friendly interface for the powerful translation engine running in the backend!