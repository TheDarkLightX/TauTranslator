import fs from 'fs';
import path from 'path';

const MODELS_DIR = path.join(process.cwd(), '../models');
const GEMMA_MODELS_FILE = path.join(process.cwd(), '../config/gemma-models.json');

// Available Gemma models for download
const AVAILABLE_MODELS = {
  'google/gemma-2-2b-it': {
    id: 'google/gemma-2-2b-it',
    name: 'Gemma 2 2B Instruct',
    size: '~5GB',
    description: 'Compact instruction-tuned model, good for basic tasks',
    type: 'instruct',
    parameters: '2B'
  },
  'google/gemma-2-9b-it': {
    id: 'google/gemma-2-9b-it', 
    name: 'Gemma 2 9B Instruct',
    size: '~18GB',
    description: 'High-quality instruction-tuned model for complex tasks',
    type: 'instruct',
    parameters: '9B'
  },
  'google/gemma-2-27b-it': {
    id: 'google/gemma-2-27b-it',
    name: 'Gemma 2 27B Instruct', 
    size: '~54GB',
    description: 'Large instruction-tuned model for advanced applications',
    type: 'instruct',
    parameters: '27B'
  }
};

// Ensure directories exist
const ensureDirs = () => {
  const configDir = path.dirname(GEMMA_MODELS_FILE);
  if (!fs.existsSync(configDir)) {
    fs.mkdirSync(configDir, { recursive: true });
  }
  if (!fs.existsSync(MODELS_DIR)) {
    fs.mkdirSync(MODELS_DIR, { recursive: true });
  }
};

// Load downloaded models info
const loadDownloadedModels = () => {
  try {
    if (fs.existsSync(GEMMA_MODELS_FILE)) {
      const data = fs.readFileSync(GEMMA_MODELS_FILE, 'utf8');
      return JSON.parse(data);
    }
    return [];
  } catch (error) {
    console.error('Error loading downloaded models:', error);
    return [];
  }
};

// Save downloaded models info  
const saveDownloadedModels = (models) => {
  try {
    ensureDirs();
    fs.writeFileSync(GEMMA_MODELS_FILE, JSON.stringify(models, null, 2));
    return true;
  } catch (error) {
    console.error('Error saving downloaded models:', error);
    return false;
  }
};

// Check if model exists on disk
const checkModelExists = (modelId) => {
  const modelPath = path.join(MODELS_DIR, modelId.replace('/', '_'));
  return fs.existsSync(modelPath);
};

// Get model size on disk
const getModelSize = (modelId) => {
  try {
    const modelPath = path.join(MODELS_DIR, modelId.replace('/', '_'));
    if (!fs.existsSync(modelPath)) return 0;
    
    const getDirectorySize = (dirPath) => {
      let totalSize = 0;
      const files = fs.readdirSync(dirPath);
      
      for (const file of files) {
        const filePath = path.join(dirPath, file);
        const stats = fs.statSync(filePath);
        
        if (stats.isDirectory()) {
          totalSize += getDirectorySize(filePath);
        } else {
          totalSize += stats.size;
        }
      }
      
      return totalSize;
    };

    return getDirectorySize(modelPath);
  } catch (error) {
    return 0;
  }
};

export default async function handler(req, res) {
  const { method } = req;

  try {
    switch (method) {
      case 'GET':
        // Get all available and downloaded models
        const existingModels = loadDownloadedModels();
        
        const allModels = Object.values(AVAILABLE_MODELS).map(model => {
          const downloaded = existingModels.find(d => d.id === model.id);
          const exists = checkModelExists(model.id);
          const diskSize = exists ? getModelSize(model.id) : 0;
          
          return {
            ...model,
            downloaded: !!downloaded,
            downloadedAt: downloaded?.downloadedAt || null,
            status: downloaded?.status || 'available',
            diskSize: diskSize,
            diskSizeFormatted: diskSize > 0 ? `${Math.round(diskSize / 1024 / 1024 / 1024 * 100) / 100}GB` : '0GB',
            exists
          };
        });

        res.status(200).json(allModels);
        break;

      case 'POST':
        // Download a model (simulate download process)
        const { model_id, hf_token } = req.body;
        
        if (!model_id || !AVAILABLE_MODELS[model_id]) {
          return res.status(400).json({ message: 'Invalid model ID' });
        }

        const currentModels = loadDownloadedModels();
        const existingModel = currentModels.find(m => m.id === model_id);
        
        if (existingModel) {
          return res.status(400).json({ message: 'Model already downloaded' });
        }

        // Simulate download process
        const newDownload = {
          id: model_id,
          status: 'downloaded',
          downloadedAt: new Date().toISOString(),
          hfToken: hf_token ? 'provided' : 'not_provided'
        };

        currentModels.push(newDownload);
        
        // Create model directory (simulated)
        const downloadPath = path.join(MODELS_DIR, model_id.replace('/', '_'));
        if (!fs.existsSync(downloadPath)) {
          fs.mkdirSync(downloadPath, { recursive: true });
          
          // Create a dummy config file to simulate model presence
          const configPath = path.join(downloadPath, 'config.json');
          const dummyConfig = {
            model_id,
            downloaded_at: new Date().toISOString(),
            status: 'ready',
            ...AVAILABLE_MODELS[model_id]
          };
          fs.writeFileSync(configPath, JSON.stringify(dummyConfig, null, 2));
        }

        if (saveDownloadedModels(currentModels)) {
          res.status(200).json({ 
            message: 'Model download completed',
            model: newDownload 
          });
        } else {
          res.status(500).json({ message: 'Failed to save download info' });
        }
        break;

      case 'DELETE':
        // Delete a downloaded model
        const { id } = req.query;
        
        if (!id || !AVAILABLE_MODELS[id]) {
          return res.status(400).json({ message: 'Invalid model ID' });
        }

        const allDownloadedModels = loadDownloadedModels();
        const filteredModels = allDownloadedModels.filter(m => m.id !== id);
        
        if (filteredModels.length === allDownloadedModels.length) {
          return res.status(404).json({ message: 'Model not found' });
        }

        // Remove model directory
        const deletePath = path.join(MODELS_DIR, id.replace('/', '_'));
        if (fs.existsSync(deletePath)) {
          fs.rmSync(deletePath, { recursive: true, force: true });
        }

        if (saveDownloadedModels(filteredModels)) {
          res.status(200).json({ message: 'Model deleted successfully' });
        } else {
          res.status(500).json({ message: 'Failed to save changes' });
        }
        break;

      default:
        res.setHeader('Allow', ['GET', 'POST', 'DELETE']);
        res.status(405).end(`Method ${method} Not Allowed`);
    }
  } catch (error) {
    console.error('Gemma models API error:', error);
    res.status(500).json({ 
      error: 'Internal server error',
      message: error.message 
    });
  }
}