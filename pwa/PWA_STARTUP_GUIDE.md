# TauTranslator PWA Startup Guide

## Current Status

The PWA development server is now running at: **http://localhost:3001**

### Backend Services Status:
- ✅ **Main Translation Backend** (Port 8000): Running
- ❌ **LLM Configuration Service** (Port 45311): Not running

## Starting the PWA

The PWA is already running. You can access it at: http://localhost:3001

To start it manually in the future:
```bash
cd ~/TauTranslator/pwa
npm run dev
```

## Testing the PWA

### 1. Basic Functionality Test
1. Open your browser and navigate to http://localhost:3001
2. The page should load with the TauTranslator interface
3. Check the Backend Status indicator in the top-right corner

### 2. Backend Connection Test
The PWA includes a BackendStatusChecker component that will show:
- Main Backend status (should show "Online" if port 8000 is running)
- LLM Service status (currently "Offline" - port 45311 not running)
- PWA Proxy status (should show "Working")

### 3. Translation Test
1. Enter some text in the input field
2. Select source and target languages
3. Click "Translate"
4. The translation should process through the backend

### 4. PWA Features Test
- **Responsive Design**: Resize browser window to test mobile/tablet views
- **Offline Capability**: PWA manifest is configured but service worker not fully implemented yet
- **Install Prompt**: On supported browsers, you may see an "Install App" option

## Starting All Backend Services

To start all required backend services:
```bash
cd ~/TauTranslator
python3 scripts/start_all_backends.py
```

This will start:
1. Main translation backend (port 8000)
2. LLM configuration service (port 45311)

## Available Routes in PWA

- `/` - Main translation interface
- `/professional` - Professional UI variant
- `/settings` - Application settings
- `/settings/llm` - LLM configuration
- `/files` - File explorer

## Development Commands

```bash
# Development server (already running)
npm run dev

# Build for production
npm run build

# Start production server
npm run start

# Run E2E tests
npm run test:e2e

# Run E2E tests with UI
npm run test:e2e:ui
```

## Troubleshooting

### If PWA doesn't load:
1. Check if port 3001 is accessible
2. Check browser console for errors
3. Verify Node.js version (v22.16.0 installed)

### If translations fail:
1. Check Backend Status indicator
2. Ensure main backend is running on port 8000
3. Check network tab in browser DevTools

### If LLM features don't work:
1. Start the LLM service: `python3 scripts/start_llm_config_service.py`
2. Check port 45311 is accessible

## Next Steps

1. Open http://localhost:3001 in your browser
2. Test the translation functionality
3. If needed, start the LLM service for full functionality
4. Check the Backend Status indicator to confirm all services are connected

The PWA is configured with Next.js rewrites to proxy API calls to the backend services, so CORS issues should be avoided.