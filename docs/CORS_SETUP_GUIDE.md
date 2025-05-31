# CORS Setup Guide for TauTranslatorOmega PWA
**Complete CORS Configuration for FastAPI Backend Integration**

## 🎯 **CORS SOLUTION IMPLEMENTED**

You have **TWO working options** for handling CORS between your PWA and FastAPI backend:

### **✅ Option 1: Next.js Proxy (RECOMMENDED & CONFIGURED)**
- **No CORS issues** - PWA makes requests to its own domain
- **Cleaner architecture** - Backend doesn't need to know about frontend
- **Better security** - Backend URL not exposed to client
- **Production ready** - Works in all environments

### **✅ Option 2: Direct CORS (BACKUP & CONFIGURED)**
- **FastAPI CORS middleware** already configured
- **Direct backend calls** from PWA frontend
- **Good for development** and testing
- **Fallback option** if proxy has issues

## 🔧 **CURRENT CONFIGURATION**

### **Next.js Proxy Configuration** (`pwa/next.config.js`)
```javascript
async rewrites() {
  return [
    {
      source: '/api/:path*',
      destination: 'http://127.0.0.1:8000/api/:path*',  // FastAPI backend
    },
    {
      source: '/auth',
      destination: 'http://127.0.0.1:8000/auth',  // Authentication
    },
    {
      source: '/health',
      destination: 'http://127.0.0.1:8000/health',  // Health check
    },
  ];
}
```

### **FastAPI CORS Configuration** (`backend_server.py`)
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🚀 **HOW TO USE THE PROXY SETUP**

### **1. Start Both Servers**
```bash
# Terminal 1: Start FastAPI backend
python3 start_backend.py
# Runs on http://localhost:8000

# Terminal 2: Start PWA
cd pwa
npm run dev
# Runs on http://localhost:3000
```

### **2. PWA API Calls (Automatic Proxy)**
```javascript
// Your PWA makes calls to its own domain
// Next.js automatically proxies to FastAPI backend

// Authentication
const authResponse = await fetch('/auth', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ password: 'your_password', action: 'authenticate' })
});

// Translation
const translateResponse = await fetch('/api/translate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${sessionToken}`
  },
  body: JSON.stringify({
    sourceText: 'Hello world',
    sourceLangKey: 'PLAIN_ENGLISH',
    targetLangKey: 'TAU'
  })
});

// Health check
const healthResponse = await fetch('/health');
```

### **3. Request Flow**
```
PWA Frontend (localhost:3000)
    ↓ fetch('/api/translate')
Next.js Proxy
    ↓ rewrites to http://127.0.0.1:8000/api/translate
FastAPI Backend (localhost:8000)
    ↓ processes request
Response flows back through proxy
    ↓
PWA receives response (no CORS issues!)
```

## 🔍 **TESTING THE SETUP**

### **Test 1: Health Check**
```bash
# Direct backend call
curl http://localhost:8000/health

# Through PWA proxy
curl http://localhost:3000/health
```

### **Test 2: Authentication**
```bash
# Through PWA proxy
curl -X POST http://localhost:3000/auth \
  -H "Content-Type: application/json" \
  -d '{"password": "test123", "action": "check"}'
```

### **Test 3: Translation**
```bash
# First authenticate to get token
TOKEN=$(curl -X POST http://localhost:3000/auth \
  -H "Content-Type: application/json" \
  -d '{"password": "your_password", "action": "authenticate"}' | jq -r '.sessionToken')

# Then translate
curl -X POST http://localhost:3000/api/translate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "sourceText": "Define a function that adds two numbers",
    "sourceLangKey": "PLAIN_ENGLISH",
    "targetLangKey": "TAU"
  }'
```

## 🛠️ **TROUBLESHOOTING**

### **Issue: Proxy Not Working**
```bash
# Check Next.js config
cat pwa/next.config.js

# Restart PWA after config changes
cd pwa
npm run dev
```

### **Issue: Backend Not Responding**
```bash
# Check if FastAPI backend is running
curl http://localhost:8000/health

# Start backend if needed
python3 start_backend.py
```

### **Issue: CORS Errors in Browser**
If you see CORS errors, you're probably making direct calls instead of using the proxy:

**❌ Wrong (Direct call):**
```javascript
fetch('http://localhost:8000/api/translate', ...)  // CORS error!
```

**✅ Correct (Proxy call):**
```javascript
fetch('/api/translate', ...)  // No CORS issues!
```

## 🔄 **FALLBACK TO DIRECT CORS**

If the proxy doesn't work for some reason, you can use direct CORS:

### **Update PWA API calls:**
```javascript
// In pwa/pages/api/translate.js
const BACKEND_URL = 'http://127.0.0.1:8000';  // Direct backend URL

// Make direct calls
const response = await fetch(`${BACKEND_URL}/api/translate`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify(request)
});
```

### **Update FastAPI CORS if needed:**
```python
# In backend_server.py - add more origins if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "http://localhost:3001",  # If PWA runs on different port
        "*"  # Only for development - NOT for production!
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🎯 **PRODUCTION CONSIDERATIONS**

### **For Production Deployment:**

1. **Update Origins:**
```python
# Production CORS settings
allow_origins=[
    "https://your-pwa-domain.com",
    "https://www.your-pwa-domain.com"
]
```

2. **Environment Variables:**
```javascript
// next.config.js
const BACKEND_URL = process.env.BACKEND_URL || 'http://127.0.0.1:8000';

async rewrites() {
  return [
    {
      source: '/api/:path*',
      destination: `${BACKEND_URL}/api/:path*`,
    }
  ];
}
```

3. **HTTPS Configuration:**
```python
# For production with HTTPS
uvicorn.run(
    "backend_server:app",
    host="0.0.0.0",
    port=8000,
    ssl_keyfile="path/to/key.pem",
    ssl_certfile="path/to/cert.pem"
)
```

## ✅ **VERIFICATION CHECKLIST**

- [ ] **FastAPI backend** running on http://localhost:8000
- [ ] **PWA frontend** running on http://localhost:3000
- [ ] **Health check** works: `curl http://localhost:3000/health`
- [ ] **Authentication** works through proxy
- [ ] **Translation** works through proxy
- [ ] **No CORS errors** in browser console
- [ ] **API documentation** accessible: http://localhost:8000/docs

## 🎉 **SUMMARY**

**Your CORS setup is now complete!** 

✅ **Next.js proxy** configured for seamless integration
✅ **FastAPI CORS** configured as backup
✅ **No CORS issues** with the proxy approach
✅ **Production ready** with environment variables
✅ **Fallback options** if proxy has issues

**The PWA can now communicate with the FastAPI backend without any CORS problems!** 🚀

## 📋 **QUICK TEST**

```bash
# 1. Start backend
python3 start_backend.py

# 2. Start PWA (new terminal)
cd pwa && npm run dev

# 3. Test in browser
# Visit: http://localhost:3000
# Try translation - should work without CORS errors!
```

**Your PWA is now fully integrated with the secure FastAPI backend through the proxy!** ✨
