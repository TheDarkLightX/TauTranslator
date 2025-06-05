# Using the Unified Backend
==========================

The Tau Translator now has a unified backend architecture that consolidates all translation functionality into a single, well-organized FastAPI application.

## Quick Start

1. **Start the unified backend**:
   ```bash
   python3 backend/unified/server.py
   ```
   This runs on port 8000 by default

2. **Access the API documentation**:
   - Open http://localhost:8000/docs for interactive Swagger UI
   - Open http://localhost:8000/redoc for ReDoc documentation

3. **Start the frontend** (in another terminal):
   ```bash
   cd pwa && npm run dev
   ```
   Access at http://localhost:3000

## What Works

### ✅ Pattern-Based Translation
- Basic TCE ↔ Tau conversion
- Common logical operators: `and`, `or`, `not`, `implies`
- Temporal keywords: `always`, `sometimes`, `eventually`
- Simple comparisons: `greater than`, `less than`, `equals`

### ✅ LMQL Translation Engine
- AI-powered bidirectional translation
- Caching for improved performance
- Fallback to pattern matching
- Confidence scoring

### ✅ API Features
- RESTful endpoints with JSON responses
- Health monitoring at `/health/`
- Authentication with session management
- Comprehensive error handling
- CORS enabled for PWA integration

### ✅ Supported Translation Patterns

#### Simple Boolean Logic
```
TCE: "always x and y"        → Tau: "always (x & y)"
TCE: "not x or y"           → Tau: "x' | y"
TCE: "x implies y"          → Tau: "x -> y"
```

#### Temporal Logic
```
TCE: "x at time t"          → Tau: "x[t]"
TCE: "eventually x"         → Tau: "eventually x"
TCE: "always not error"     → Tau: "always error'"
```

#### Stream Operations
```
Tau: "r o1[t] = i1[t] & i2[t]"  → TCE: "Rule: output 1 at time t equals input 1 at time t AND input 2 at time t"
```

## API Endpoints

### Translation
```bash
# Main translation endpoint
curl -X POST http://localhost:8000/api/translate/ \
  -H "Content-Type: application/json" \
  -d '{
    "sourceText": "always x and y",
    "direction": "to_tau"
  }'

# Response:
{
  "success": true,
  "data": {
    "translated_text": "always (x & y)",
    "confidence": 0.85,
    "translation_method": "pattern"
  }
}
```

### Health Check
```bash
# Basic health
curl http://localhost:8000/health/

# Detailed health with metrics
curl http://localhost:8000/health/detailed

# Engine status
curl http://localhost:8000/health/engines
```

### Authentication (Optional)
```bash
# Login with master password
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"password": "your_master_password"}'
```

## Configuration

### Environment Variables
```bash
# Server settings
export TAU_HOST=0.0.0.0
export TAU_PORT=8000
export TAU_DEBUG=true

# Enable specific engines
export TAU_ENABLE_LMQL=true
export TAU_ENABLE_GRAMMAR=false
export TAU_ENABLE_NLP=false

# Security (optional)
export TAU_MASTER_PASSWORD=your_password
```

### Using .env File
Create a `.env` file in the project root:
```ini
TAU_HOST=localhost
TAU_PORT=8000
TAU_DEBUG=true
TAU_ENABLE_LMQL=true
```

## Architecture

The unified backend consolidates:
- **6 separate backend files** → **1 organized structure**
- **Duplicate code** → **Reusable components**
- **Inconsistent APIs** → **Standardized endpoints**
- **Multiple processes** → **Single service**

### Translation Engines
1. **Pattern Engine** (✅ Working): Fast regex-based translation
2. **LMQL Engine** (✅ Working): AI-powered with caching
3. **Grammar Engine** (🚧 Stub): Lark parser integration
4. **NLP Engine** (🚧 Stub): Advanced language features

## Testing

```bash
# Run test suite
python backend/test_unified_backend.py

# Test with custom URL
python backend/test_unified_backend.py --url http://localhost:8001

# Save results
python backend/test_unified_backend.py --save-results results.json
```

## Limitations

- Complex Tau constructs not fully supported
- Grammar integration incomplete
- NLP features stubbed
- Some temporal patterns need work
- LLM integration requires API keys

## Migration from Old Backends

If you were using:
- `simple_backend.py` → Use unified backend on port 8000
- `backend_server.py` → Use unified backend with auth
- `working_backend.py` → Use unified backend (same patterns work)
- `integrated_nlp_backend.py` → NLP features coming soon

The unified backend maintains compatibility with existing frontend code while providing a cleaner, more maintainable architecture.

---

**Note**: This is the recommended backend for all Tau Translator deployments. The old separate backend files are deprecated.