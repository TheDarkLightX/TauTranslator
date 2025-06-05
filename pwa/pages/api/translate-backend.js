/**
 * Backend Translation API Route
 * =============================
 * 
 * This route actually calls the Python backend for real translation
 * instead of using fake pattern matching.
 */

export default async function handler(req, res) {
  if (req.method === 'POST') {
    const { sourceText, sourceLangKey, targetLangKey } = req.body;
    
    if (!sourceText) {
      return res.status(400).json({
        error: 'Missing source text',
        message: 'sourceText is required'
      });
    }

    try {
      // Backend endpoints
      const BACKEND_URLS = [
        'http://localhost:8000',  // Simple backend
        'http://localhost:8001',  // FastAPI backend
        'http://localhost:8003',  // Working backend
      ];
      
      // Try each backend until one works
      let response = null;
      let lastError = null;
      
      for (const backendUrl of BACKEND_URLS) {
        try {
          // First try without auth (some backends don't require it)
          const translateResponse = await fetch(`${backendUrl}/translate`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              sourceText,
              sourceLang: sourceLangKey,
              targetLang: targetLangKey
            })
          });
          
          if (translateResponse.ok) {
            response = await translateResponse.json();
            break;
          }
          
          // If auth required and we have a token, try the api/translate endpoint
          const authHeader = req.headers.authorization;
          if (authHeader) {
            const apiResponse = await fetch(`${backendUrl}/api/translate`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': authHeader
              },
              body: JSON.stringify({
                sourceText,
                sourceLang: sourceLangKey,
                targetLang: targetLangKey
              })
            });
            
            if (apiResponse.ok) {
              response = await apiResponse.json();
              break;
            }
          }
        } catch (error) {
          lastError = error;
          console.log(`Backend ${backendUrl} not available:`, error.message);
        }
      }
      
      if (response && response.translatedText) {
        return res.status(200).json({
          translatedText: response.translatedText,
          provider: response.provider || 'Backend Translator',
          model: response.model || 'backend-v1',
          secure: true,
          mock: false,
          processingTime: response.processingTime || 0.1
        });
      } else {
        throw new Error(lastError?.message || 'No backend available');
      }
      
    } catch (error) {
      console.error('Backend translation error:', error);
      
      return res.status(503).json({
        error: 'Translation service unavailable',
        message: 'The backend translation service is not running. Please ensure the Python backend is started.',
        details: {
          tried: BACKEND_URLS,
          lastError: error.message,
          suggestion: 'Run: python3 backend/simple_backend.py'
        },
        translatedText: null,
        provider: 'None',
        model: 'None',
        secure: false,
        mock: false
      });
    }
  } else {
    res.setHeader('Allow', ['POST']);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}