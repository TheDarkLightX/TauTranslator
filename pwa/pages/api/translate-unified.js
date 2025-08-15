/**
 * Unified Translation Gateway API
 * ===============================
 * 
 * Single entry point for all translation requests
 * Routes to appropriate translator based on availability and request type
 * 
 * Priority order:
 * 1. Python backend (if available and not forcing local)
 * 2. LMQL translator (for advanced features)
 * 3. ILR translator (for ILR-specific requests)
 * 4. Pattern-based translator (fallback)
 * 
 * Author: DarkLightX / Dana Edwards
 */

import axios from 'axios';

// Backend URLs to try in order
const BACKEND_URLS = [
  'http://localhost:8000',
  'http://localhost:8001',
  'http://localhost:8003'
];

// Cache backend availability for 30 seconds
let backendCache = {
  available: false,
  lastCheck: 0,
  url: null
};

const CACHE_DURATION = 30000; // 30 seconds

export default async function handler(req, res) {
  if (req.method === 'POST') {
    const { 
      sourceText, 
      sourceLangKey, 
      targetLangKey, 
      sourceLangLabel, 
      targetLangLabel,
      forceLocal = false,
      preferredTranslator = null
    } = req.body;
    
    if (!sourceText) {
      return res.status(400).json({
        error: 'Missing source text',
        message: 'sourceText is required'
      });
    }

    try {
      console.log(`Unified Translator: ${sourceLangLabel} (${sourceLangKey}) → ${targetLangLabel} (${targetLangKey})`);
      console.log(`Options: forceLocal=${forceLocal}, preferred=${preferredTranslator}`);

      // Check if we should use a specific translator
      if (preferredTranslator) {
        return await routeToSpecificTranslator(req, res, preferredTranslator);
      }

      // Route based on language and availability
      let result = null;

      // 1. Try backend first (unless forcing local)
      if (!forceLocal) {
        result = await tryBackendTranslation(req.body);
        if (result && result.success) {
          return res.status(200).json(result.data);
        }
      }

      // 2. Check if this is an ILR-specific request
      if (sourceLangKey === 'ILR' || targetLangKey === 'ILR') {
        result = await tryILRTranslation(req.body);
        if (result && result.success) {
          return res.status(200).json(result.data);
        }
      }

      // 3. Try LMQL translator for advanced features
      if (shouldUseLMQL(sourceText, sourceLangKey, targetLangKey)) {
        result = await tryLMQLTranslation(req.body);
        if (result && result.success) {
          return res.status(200).json(result.data);
        }
      }

      // 4. Fall back to pattern-based translator
      result = await tryPatternTranslation(req.body);
      if (result && result.success) {
        return res.status(200).json(result.data);
      }

      // If all translators fail, return error
      return res.status(500).json({
        error: 'Translation failed',
        message: 'All translation methods failed',
        translatedText: sourceText,
        provider: 'None',
        fallback: true
      });

    } catch (error) {
      console.error('Unified translation error:', error);
      
      return res.status(500).json({
        error: 'Translation system error',
        message: error.message,
        translatedText: sourceText
      });
    }
  } else {
    res.setHeader('Allow', ['POST']);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}

// Check if backend is available (with caching)
async function isBackendAvailable() {
  const now = Date.now();
  
  // Use cached result if still valid
  if (now - backendCache.lastCheck < CACHE_DURATION) {
    return backendCache;
  }

  // Check backend availability
  for (const url of BACKEND_URLS) {
    try {
      const response = await axios.get(`${url}/health`, { timeout: 1000 });
      if (response.status === 200) {
        backendCache = {
          available: true,
          lastCheck: now,
          url: url
        };
        return backendCache;
      }
    } catch (error) {
      // Continue to next URL
    }
  }

  // No backend available
  backendCache = {
    available: false,
    lastCheck: now,
    url: null
  };
  return backendCache;
}

// Try translation via Python backend
async function tryBackendTranslation(requestBody) {
  const backend = await isBackendAvailable();
  
  if (!backend.available) {
    return { success: false, error: 'Backend not available' };
  }

  try {
    // First try authenticated endpoint
    if (requestBody.apiKey) {
      try {
        const response = await axios.post(
          `${backend.url}/translate/secure`,
          requestBody,
          { 
            timeout: 5000,
            headers: {
              'Authorization': `Bearer ${requestBody.apiKey}`,
              'Content-Type': 'application/json'
            }
          }
        );
        
        return {
          success: true,
          data: {
            ...response.data,
            provider: response.data.provider || 'Python Backend (Secure)',
            backendUrl: backend.url
          }
        };
      } catch (authError) {
        console.log('Authenticated endpoint failed, trying public endpoint');
      }
    }

    // Choose endpoint based on advanced parameters
    const needsV2 = Boolean(requestBody.grammarFilename) || (requestBody.engineKey && requestBody.engineKey !== 'auto');
    const path = needsV2 ? '/v2/translate' : '/translate';

    const response = await axios.post(
      `${backend.url}${path}`,
      requestBody,
      { 
        timeout: 5000,
        headers: { 'Content-Type': 'application/json' }
      }
    );

    return {
      success: true,
      data: {
        ...response.data,
        provider: response.data.provider || 'Python Backend',
        backendUrl: backend.url
      }
    };

  } catch (error) {
    console.error('Backend translation error:', error.message);
    return { success: false, error: error.message };
  }
}

// Try translation via LMQL translator
async function tryLMQLTranslation(requestBody) {
  try {
    const response = await fetch('/api/translate-direct', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestBody)
    });

    if (response.ok) {
      const data = await response.json();
      return {
        success: true,
        data: {
          ...data,
          provider: data.provider || 'LMQL Translator'
        }
      };
    }

    return { success: false, error: 'LMQL translation failed' };
  } catch (error) {
    console.error('LMQL translation error:', error.message);
    return { success: false, error: error.message };
  }
}

// Try translation via ILR translator
async function tryILRTranslation(requestBody) {
  try {
    const response = await fetch('/api/translate-ilr', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestBody)
    });

    if (response.ok) {
      const data = await response.json();
      return {
        success: true,
        data: {
          ...data,
          provider: data.provider || 'ILR Translator'
        }
      };
    }

    return { success: false, error: 'ILR translation failed' };
  } catch (error) {
    console.error('ILR translation error:', error.message);
    return { success: false, error: error.message };
  }
}

// Try translation via pattern-based translator
async function tryPatternTranslation(requestBody) {
  try {
    const response = await fetch('/api/translate-patterns', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestBody)
    });

    if (response.ok) {
      const data = await response.json();
      return {
        success: true,
        data: {
          ...data,
          provider: data.provider || 'Pattern Translator',
          fallback: true
        }
      };
    }

    return { success: false, error: 'Pattern translation failed' };
  } catch (error) {
    console.error('Pattern translation error:', error.message);
    return { success: false, error: error.message };
  }
}

// Route to a specific translator
async function routeToSpecificTranslator(req, res, translator) {
  const translatorMap = {
    'backend': '/api/translate-backend',
    'lmql': '/api/translate-direct',
    'ilr': '/api/translate-ilr',
    'patterns': '/api/translate-patterns',
    'simple': '/api/translate-simple',
    'tau': '/api/translate-tau'
  };

  const endpoint = translatorMap[translator];
  if (!endpoint) {
    return res.status(400).json({
      error: 'Invalid translator',
      message: `Unknown translator: ${translator}`,
      available: Object.keys(translatorMap)
    });
  }

  try {
    const response = await fetch(`http://localhost:3000${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req.body)
    });

    const data = await response.json();
    return res.status(response.status).json(data);
  } catch (error) {
    return res.status(500).json({
      error: 'Routing error',
      message: error.message,
      translator: translator
    });
  }
}

// Determine if LMQL should be used based on complexity
function shouldUseLMQL(text, sourceLang, targetLang) {
  // Use LMQL for complex patterns
  const complexPatterns = [
    /solve\s*{.*}/,
    /\bforall\b|\bexists\b/,
    /always|sometimes|eventually/,
    /\[t-\d+\]|\[t\+\d+\]/,
    /:=/
  ];

  // Check if text contains complex patterns
  return complexPatterns.some(pattern => pattern.test(text));
}

// Export helper functions for testing
export { isBackendAvailable, shouldUseLMQL };