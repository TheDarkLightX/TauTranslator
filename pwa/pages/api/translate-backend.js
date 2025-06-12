/**
 * Backend Translation API Route
 * =============================
 * 
 * This route calls the Python backend for translation and autocomplete
 * following the Intentional Disclosure Principle.
 */

// Infrastructure Layer (Rule 4: Isolate Impurity)
async function _handle_autocomplete_request_async(req, res, autocompleteData) {
  const { text, position, context } = autocompleteData;
  
  if (!text) {
    return res.status(400).json({
      success: false,
      error: 'Missing text for autocomplete'
    });
  }

  try {
    const BACKEND_URLS = [
      'http://localhost:8000',  // Simple backend
      'http://localhost:8001',  // FastAPI backend  
      'http://localhost:8003',  // Working backend
    ];
    
    let response = null;
    let lastError = null;
    
    for (const backendUrl of BACKEND_URLS) {
      try {
        const autocompleteResponse = await fetch(`${backendUrl}/api/nlp/autocomplete`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(req.headers.authorization && { 'Authorization': req.headers.authorization })
          },
          body: JSON.stringify({ text, position, context })
        });
        
        if (autocompleteResponse.ok) {
          response = await autocompleteResponse.json();
          break;
        }
      } catch (error) {
        lastError = error;
        console.log(`Backend ${backendUrl} autocomplete not available:`, error.message);
      }
    }
    
    if (response && response.success) {
      return res.status(200).json({
        success: true,
        data: response.data
      });
    } else {
      // Fallback to basic suggestions
      const basicSuggestions = _generate_basic_suggestions_fallback(text);
      return res.status(200).json({
        success: true,
        data: {
          suggestions: basicSuggestions,
          source: 'fallback'
        }
      });
    }
    
  } catch (error) {
    console.error('Autocomplete service error:', error);
    
    // Fallback to basic suggestions on error
    const basicSuggestions = _generate_basic_suggestions_fallback(text);
    return res.status(200).json({
      success: true,
      data: {
        suggestions: basicSuggestions,
        source: 'fallback'
      }
    });
  }
}

// Core Business Logic (Pure Functions)
function _generate_basic_suggestions_fallback(text) {
  const lowerText = text.toLowerCase();
  const basicSuggestions = [];
  
  // TAU Keywords
  const tauKeywords = [
    { text: 'DEFINE', type: 'keyword', description: 'Define a new concept' },
    { text: 'always', type: 'temporal', description: 'Temporal operator: always true' },
    { text: 'sometimes', type: 'temporal', description: 'Temporal operator: sometimes true' },
    { text: 'eventually', type: 'temporal', description: 'Temporal operator: eventually true' },
    { text: 'forall', type: 'quantifier', description: 'Universal quantification' },
    { text: 'exists', type: 'quantifier', description: 'Existential quantification' },
    { text: 'true', type: 'keyword', description: 'Boolean literal: true' },
    { text: 'false', type: 'keyword', description: 'Boolean literal: false' }
  ];
  
  // TAU Operators
  const tauOperators = [
    { text: ':=', type: 'operator', description: 'Definition operator' },
    { text: '->', type: 'operator', description: 'Implication operator' },
    { text: '<->', type: 'operator', description: 'Equivalence operator' },
    { text: '&&', type: 'operator', description: 'Logical AND' },
    { text: '||', type: 'operator', description: 'Logical OR' },
    { text: '!', type: 'operator', description: 'Logical NOT' }
  ];
  
  // Filter based on input
  [...tauKeywords, ...tauOperators].forEach(item => {
    if (item.text.toLowerCase().includes(lowerText) || lowerText.length === 0) {
      basicSuggestions.push(item);
    }
  });
  
  return basicSuggestions.slice(0, 10); // Limit to 10 suggestions
}

export default async function handler(req, res) {
  if (req.method === 'POST') {
    const { sourceText, sourceLangKey, targetLangKey, endpoint, data } = req.body;
    
    // Handle autocomplete requests
    if (endpoint === '/autocomplete') {
      return await _handle_autocomplete_request_async(req, res, data);
    }
    
    // Handle translation requests (existing logic)
    
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