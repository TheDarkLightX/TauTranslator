/**
 * API Keys Management Endpoint
 * ============================
 * 
 * Secure API key management for AI providers.
 * Keys are encrypted and stored securely.
 */

import fs from 'fs';
import path from 'path';
import crypto from 'crypto';

const CONFIG_DIR = path.join(process.cwd(), '.tau_config');
const KEYS_FILE = path.join(CONFIG_DIR, 'api_keys.enc');
const SALT_FILE = path.join(CONFIG_DIR, 'salt.key');

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
    models: ["gpt-4", "gpt-3.5-turbo", "gpt-4-turbo"]
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
  },
  huggingface: {
    name: "Hugging Face",
    description: "Inference API for various models",
    url: "https://huggingface.co/settings/tokens", 
    models: ["microsoft/DialoGPT-medium", "facebook/blenderbot-400M-distill"]
  }
};

// Encryption utilities
function getOrCreateSalt() {
  if (fs.existsSync(SALT_FILE)) {
    return fs.readFileSync(SALT_FILE);
  } else {
    const salt = crypto.randomBytes(16);
    fs.writeFileSync(SALT_FILE, salt);
    return salt;
  }
}

function deriveKey(password) {
  const salt = getOrCreateSalt();
  return crypto.pbkdf2Sync(password, salt, 100000, 32, 'sha256');
}

function encrypt(text, password) {
  const key = deriveKey(password);
  const iv = crypto.randomBytes(16);
  const cipher = crypto.createCipheriv('aes-256-cbc', key, iv);
  
  let encrypted = cipher.update(text, 'utf8', 'hex');
  encrypted += cipher.final('hex');
  
  return iv.toString('hex') + ':' + encrypted;
}

function decrypt(encryptedText, password) {
  const key = deriveKey(password);
  const textParts = encryptedText.split(':');
  const iv = Buffer.from(textParts.shift(), 'hex');
  const encrypted = textParts.join(':');
  
  const decipher = crypto.createDecipheriv('aes-256-cbc', key, iv);
  let decrypted = decipher.update(encrypted, 'hex', 'utf8');
  decrypted += decipher.final('utf8');
  
  return decrypted;
}

// API key storage
function loadApiKeys(masterPassword) {
  if (!fs.existsSync(KEYS_FILE)) {
    return {};
  }
  
  try {
    const encryptedData = fs.readFileSync(KEYS_FILE, 'utf8');
    const decryptedData = decrypt(encryptedData, masterPassword);
    return JSON.parse(decryptedData);
  } catch (error) {
    console.error('Failed to decrypt API keys:', error);
    return {};
  }
}

function saveApiKeys(apiKeys, masterPassword) {
  const encryptedData = encrypt(JSON.stringify(apiKeys), masterPassword);
  fs.writeFileSync(KEYS_FILE, encryptedData);
}

export default function handler(req, res) {
  if (req.method === 'GET') {
    // Get provider info and status
    try {
      const masterPassword = req.headers['x-master-password'] || 'default-password';
      const apiKeys = loadApiKeys(masterPassword);
      
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
      const { provider, apiKey, masterPassword = 'default-password' } = req.body;
      
      if (!provider || !apiKey) {
        return res.status(400).json({
          success: false,
          error: 'Provider and API key are required'
        });
      }
      
      if (!SUPPORTED_PROVIDERS[provider]) {
        return res.status(400).json({
          success: false,
          error: 'Unsupported provider'
        });
      }
      
      const apiKeys = loadApiKeys(masterPassword);
      apiKeys[provider] = apiKey;
      saveApiKeys(apiKeys, masterPassword);
      
      res.status(200).json({
        success: true,
        message: `API key for ${SUPPORTED_PROVIDERS[provider].name} saved securely`
      });
    } catch (error) {
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
      const { provider, masterPassword = 'default-password' } = req.body;
      
      if (!provider) {
        return res.status(400).json({
          success: false,
          error: 'Provider is required'
        });
      }
      
      const apiKeys = loadApiKeys(masterPassword);
      delete apiKeys[provider];
      saveApiKeys(apiKeys, masterPassword);
      
      res.status(200).json({
        success: true,
        message: `API key for ${SUPPORTED_PROVIDERS[provider]?.name || provider} removed`
      });
    } catch (error) {
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