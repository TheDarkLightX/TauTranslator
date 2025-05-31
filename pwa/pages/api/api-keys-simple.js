/**
 * Simple API Keys Management (Plain Text for Testing)
 * ==================================================
 * 
 * Temporary simple storage for debugging API key issues.
 * WARNING: This stores keys in plain text - use only for testing!
 */

import fs from 'fs';
import path from 'path';

const CONFIG_DIR = path.join(process.cwd(), '.tau_config');
const KEYS_FILE = path.join(CONFIG_DIR, 'api_keys.json');

// Ensure config directory exists
if (!fs.existsSync(CONFIG_DIR)) {
  fs.mkdirSync(CONFIG_DIR, { recursive: true });
}

// Supported providers
const SUPPORTED_PROVIDERS = {
  openrouter: {
    name: "OpenRouter",
    description: "Access to multiple AI models via one API",
    url: "https://openrouter.ai/keys",
    models: [
      "anthropic/claude-3.5-sonnet",
      "openai/gpt-4o",
      "openai/gpt-4-turbo",
      "google/gemini-pro-1.5",
      "meta-llama/llama-3.1-405b-instruct",
      "anthropic/claude-3-haiku"
    ]
  },
  openai: {
    name: "OpenAI",
    description: "GPT-4, GPT-3.5-turbo, etc.",
    url: "https://platform.openai.com/api-keys",
    models: ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]
  },
  anthropic: {
    name: "Anthropic", 
    description: "Claude 3.5 Sonnet, Claude 3 Haiku, etc.",
    url: "https://console.anthropic.com/",
    models: ["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"]
  },
  google: {
    name: "Google AI",
    description: "Gemini Pro, Gemini Flash, etc.", 
    url: "https://aistudio.google.com/app/apikey",
    models: ["gemini-pro", "gemini-pro-vision", "gemini-1.5-flash"]
  }
};

// Simple storage functions
function loadApiKeys() {
  if (!fs.existsSync(KEYS_FILE)) {
    return {};
  }
  
  try {
    const data = fs.readFileSync(KEYS_FILE, 'utf8');
    return JSON.parse(data);
  } catch (error) {
    console.error('Failed to load API keys:', error);
    return {};
  }
}

function saveApiKeys(apiKeys) {
  try {
    fs.writeFileSync(KEYS_FILE, JSON.stringify(apiKeys, null, 2));
    return true;
  } catch (error) {
    console.error('Failed to save API keys:', error);
    return false;
  }
}

// Test API key function
async function testApiKey(provider, apiKey) {
  try {
    let testUrl, headers;
    
    if (provider === 'openrouter') {
      testUrl = 'https://openrouter.ai/api/v1/models';
      headers = {
        'Authorization': `Bearer ${apiKey}`,
        'HTTP-Referer': 'https://localhost:3000',
        'X-Title': 'TauTranslator'
      };
    } else if (provider === 'openai') {
      testUrl = 'https://api.openai.com/v1/models';
      headers = {
        'Authorization': `Bearer ${apiKey}`
      };
    } else if (provider === 'anthropic') {
      testUrl = 'https://api.anthropic.com/v1/messages';
      headers = {
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01'
      };
    } else {
      return { success: false, error: 'Unsupported provider for testing' };
    }

    const response = await fetch(testUrl, {
      method: 'GET',
      headers,
      timeout: 10000
    });

    // For most APIs, 200 means success, 401 means invalid key, 403 means valid key but no permission
    if (response.status === 200 || response.status === 403) {
      return { success: true, message: 'API key is valid' };
    } else if (response.status === 401) {
      return { success: false, error: 'Invalid API key' };
    } else {
      return { success: false, error: `HTTP ${response.status}: ${response.statusText}` };
    }
  } catch (error) {
    return { success: false, error: error.message };
  }
}

export default async function handler(req, res) {
  console.log(`API Keys endpoint: ${req.method} ${req.url}`);
  
  if (req.method === 'GET') {
    // Get provider info and status
    try {
      const apiKeys = loadApiKeys();
      console.log('Loaded API keys for providers:', Object.keys(apiKeys));
      
      const providers = Object.entries(SUPPORTED_PROVIDERS).map(([id, info]) => ({
        id,
        ...info,
        hasKey: !!apiKeys[id],
        keyPreview: apiKeys[id] ? `${apiKeys[id].substring(0, 8)}...` : null
      }));
      
      res.status(200).json({
        success: true,
        providers
      });
    } catch (error) {
      console.error('Error in GET:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to load API keys',
        message: error.message
      });
    }
  } 
  else if (req.method === 'POST') {
    // Set API key
    try {
      const { provider, apiKey, testConnection } = req.body;
      console.log(`Setting API key for provider: ${provider}, testConnection: ${testConnection}`);
      
      if (!provider || !apiKey) {
        return res.status(400).json({
          success: false,
          error: 'Provider and API key are required'
        });
      }
      
      if (!SUPPORTED_PROVIDERS[provider]) {
        return res.status(400).json({
          success: false,
          error: 'Unsupported provider',
          supportedProviders: Object.keys(SUPPORTED_PROVIDERS)
        });
      }
      
      // Test the API key if requested
      if (testConnection) {
        console.log(`Testing API key for ${provider}...`);
        const testResult = await testApiKey(provider, apiKey);
        if (!testResult.success) {
          return res.status(400).json({
            success: false,
            error: 'API key test failed',
            details: testResult.error
          });
        }
        console.log(`API key test successful for ${provider}`);
      }
      
      const apiKeys = loadApiKeys();
      apiKeys[provider] = apiKey;
      
      const saved = saveApiKeys(apiKeys);
      if (!saved) {
        return res.status(500).json({
          success: false,
          error: 'Failed to save API key to disk'
        });
      }
      
      console.log(`API key saved successfully for ${provider}`);
      res.status(200).json({
        success: true,
        message: `API key for ${SUPPORTED_PROVIDERS[provider].name} saved successfully`,
        tested: !!testConnection
      });
    } catch (error) {
      console.error('Error in POST:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to save API key',
        message: error.message
      });
    }
  }
  else if (req.method === 'DELETE') {
    // Remove API key
    try {
      const { provider } = req.body;
      console.log(`Removing API key for provider: ${provider}`);
      
      if (!provider) {
        return res.status(400).json({
          success: false,
          error: 'Provider is required'
        });
      }
      
      const apiKeys = loadApiKeys();
      delete apiKeys[provider];
      
      const saved = saveApiKeys(apiKeys);
      if (!saved) {
        return res.status(500).json({
          success: false,
          error: 'Failed to save changes to disk'
        });
      }
      
      console.log(`API key removed successfully for ${provider}`);
      res.status(200).json({
        success: true,
        message: `API key for ${SUPPORTED_PROVIDERS[provider]?.name || provider} removed`
      });
    } catch (error) {
      console.error('Error in DELETE:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to remove API key',
        message: error.message
      });
    }
  }
  else {
    res.setHeader('Allow', ['GET', 'POST', 'DELETE']);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}