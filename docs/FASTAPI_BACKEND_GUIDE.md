# FastAPI Unified Backend Guide
**Production-Ready Backend for Tau Translator**

## 🎯 **UNIFIED BACKEND ARCHITECTURE**

The Tau Translator uses a unified FastAPI backend that consolidates all translation functionality into a single, well-organized application located at `backend/unified/server.py`.

### **✅ Why FastAPI?**
- **Automatic API Documentation** - Interactive Swagger UI at `/docs`
- **Type Safety** - Pydantic models with automatic validation
- **High Performance** - Async/await support for AI operations
- **Modern Python** - Full type hints and async support
- **Production Ready** - Built on Starlette and Uvicorn
- **Easy Integration** - CORS support for PWA and desktop apps

### **✅ Unified Architecture Benefits**
- **Single Service** - One backend instead of 6 separate files
- **Consistent APIs** - Standardized request/response formats
- **Modular Design** - Pluggable translation engines
- **Better Testing** - Comprehensive test coverage
- **Easy Deployment** - Single process to manage

## 🚀 **BACKEND FEATURES**

### **Core Components**
```
backend/unified/
├── server.py              # Main FastAPI application
├── core/
│   ├── config.py         # Environment-based configuration
│   ├── auth.py           # Authentication and sessions
│   └── responses.py      # Standardized API responses
├── api/
│   ├── translate.py      # Translation endpoints
│   ├── health.py         # Health monitoring
│   ├── auth.py           # Authentication endpoints
│   ├── grammar.py        # Grammar management
│   └── nlp.py           # NLP features
└── translators/
    ├── manager.py        # Translation orchestration
    ├── pattern_translator.py  # Pattern-based engine
    ├── lmql_translator.py     # AI-powered engine
    ├── grammar_translator.py  # Grammar-aware engine
    └── nlp_translator.py      # NLP engine
```

### **API Endpoints**

#### Translation
```python
@app.post("/api/translate/", response_model=TranslationResponse)
async def translate(request: TranslationRequest):
    """Main translation endpoint with intelligent engine selection."""
    
# Request:
{
    "sourceText": "always x and y",
    "direction": "to_tau",  # or "to_tce"
    "options": {
        "useCache": true,
        "preferredEngine": "auto"
    }
}

# Response:
{
    "success": true,
    "data": {
        "translated_text": "always (x & y)",
        "confidence": 0.85,
        "translation_method": "pattern",
        "patterns_detected": ["temporal_always", "logical_and"]
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

#### Health Monitoring
```python
# Basic health check
GET /health/

# Detailed metrics
GET /health/detailed

# Translation engine status
GET /health/engines
```

#### Authentication (Optional)
```python
# Login
POST /auth/login
{
    "password": "master_password"
}

# Get current user
GET /auth/me

# Manage API keys
POST /auth/api-keys
GET /auth/api-keys/{provider}
```

### **Translation Engines**

1. **Pattern Engine** ✅
   - Fast regex-based translation
   - Handles common TCE ↔ Tau patterns
   - No external dependencies
   - 60-95% confidence

2. **LMQL Engine** ✅
   - AI-powered translation
   - Bidirectional with caching
   - Fallback mechanisms
   - 85%+ confidence

3. **Grammar Engine** 🚧
   - Lark parser integration
   - TGF/EBNF grammar support
   - Currently stubbed

4. **NLP Engine** 🚧
   - Advanced language features
   - Autocomplete and validation
   - Currently stubbed

## 🔧 **CONFIGURATION**

### **Environment Variables**
```bash
# Server Configuration
TAU_HOST=0.0.0.0            # Bind address
TAU_PORT=8000               # Port number
TAU_DEBUG=true              # Debug mode (enables /docs)

# Security
TAU_MASTER_PASSWORD=secret  # Optional auth
TAU_SECRET_KEY=random_key   # Session encryption
TAU_SESSION_EXPIRE_HOURS=24 # Session timeout

# Feature Flags
TAU_ENABLE_LMQL=true       # Enable LMQL engine
TAU_ENABLE_GRAMMAR=true    # Enable grammar features
TAU_ENABLE_NLP=true        # Enable NLP features

# Paths
TAU_GRAMMAR_DIR=./grammars      # Grammar files
TAU_SESSIONS_DIR=./sessions     # Session storage
TAU_CACHE_DIR=./cache          # Translation cache
```

### **Using .env File**
```ini
# backend/unified/.env
TAU_HOST=localhost
TAU_PORT=8000
TAU_DEBUG=true
TAU_ENABLE_LMQL=true
TAU_MASTER_PASSWORD=development
```

## 🚀 **QUICK START**

### **1. Install Dependencies**
```bash
cd backend/unified
pip install -r requirements.txt
```

### **2. Start the Server**
```bash
# Development mode
python server.py

# Production mode
uvicorn backend.unified.server:app --host 0.0.0.0 --port 8000
```

### **3. Access Documentation**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health: http://localhost:8000/health/

### **4. Test Translation**
```bash
curl -X POST http://localhost:8000/api/translate/ \
  -H "Content-Type: application/json" \
  -d '{"sourceText": "always x and y", "direction": "to_tau"}'
```

## 🔒 **SECURITY FEATURES**

### **API Key Management**
- Encrypted storage using Fernet
- Provider-specific keys (OpenRouter, HuggingFace, etc.)
- Secure retrieval through authenticated endpoints

### **Session Management**
- Optional master password protection
- JWT-like session tokens
- Configurable expiration
- Secure cookie handling

### **Input Validation**
- Pydantic models for all requests
- Automatic validation and sanitization
- Clear error messages
- SQL injection protection

### **CORS Configuration**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # PWA origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📊 **MONITORING & DEBUGGING**

### **Logging**
```python
# Structured logging with context
logger.info("Translation request", extra={
    "source_text_length": len(source_text),
    "direction": direction,
    "engine": engine_name
})
```

### **Metrics**
- Request count and latency
- Translation success/failure rates
- Engine performance comparison
- Cache hit rates

### **Debug Mode**
When `TAU_DEBUG=true`:
- Swagger UI enabled
- Detailed error messages
- Request/response logging
- Performance profiling

## 🚢 **DEPLOYMENT**

### **Docker**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY backend/unified/ ./backend/unified/
RUN pip install -r backend/unified/requirements.txt
EXPOSE 8000
CMD ["uvicorn", "backend.unified.server:app", "--host", "0.0.0.0"]
```

### **Production Settings**
```bash
# Use production ASGI server
gunicorn backend.unified.server:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000

# Enable HTTPS (reverse proxy recommended)
# Use environment variables for secrets
# Set TAU_DEBUG=false
# Configure proper CORS origins
```

### **Health Checks**
```yaml
# Kubernetes example
livenessProbe:
  httpGet:
    path: /health/live
    port: 8000
readinessProbe:
  httpGet:
    path: /health/ready
    port: 8000
```

## 🧪 **TESTING**

### **Run Test Suite**
```bash
python backend/test_unified_backend.py
```

### **Test Coverage**
- ✅ Health endpoints
- ✅ Basic translation
- ✅ Pattern engine
- ✅ LMQL engine
- ✅ Error handling
- ✅ Authentication
- 🚧 Grammar features
- 🚧 NLP features

### **Performance Testing**
```bash
# Load testing with locust
locust -f tests/load_test.py --host http://localhost:8000
```

## 📝 **API EXAMPLES**

### **Basic Translation**
```javascript
// JavaScript/React example
const response = await fetch('http://localhost:8000/api/translate/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        sourceText: 'always x and y',
        direction: 'to_tau'
    })
});
const result = await response.json();
console.log(result.data.translated_text); // "always (x & y)"
```

### **With Authentication**
```javascript
// Login first
const authResponse = await fetch('http://localhost:8000/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ password: 'master_password' })
});
const { session_token } = await authResponse.json();

// Use token for subsequent requests
const response = await fetch('http://localhost:8000/api/translate/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${session_token}`
    },
    body: JSON.stringify({ sourceText: 'x or y', direction: 'to_tau' })
});
```

### **Batch Translation**
```javascript
// Coming soon - translate multiple texts
const response = await fetch('http://localhost:8000/api/translate/batch', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        texts: ['always x', 'sometimes y', 'never z'],
        direction: 'to_tau'
    })
});
```

## 🔄 **MIGRATION GUIDE**

### **From Old Backends**
- `simple_backend.py` → Use unified backend
- `backend_server.py` → Same auth concepts
- `integrated_backend.py` → Grammar features coming
- `working_backend.py` → Pattern engine included

### **Frontend Updates**
```javascript
// Old: Multiple backend URLs
const BACKEND_URL = 'http://localhost:8000';
const GRAMMAR_URL = 'http://localhost:8001';

// New: Single unified backend
const API_URL = 'http://localhost:8000/api';
```

## 📚 **ADDITIONAL RESOURCES**

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Backend README](../backend/unified/README.md)
- [API Test Suite](../backend/test_unified_backend.py)

---

**The unified FastAPI backend provides a solid foundation for the Tau Translator system, with room for growth as new features are implemented.**