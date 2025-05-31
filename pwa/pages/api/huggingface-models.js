import fs from 'fs';
import path from 'path';
import { spawn } from 'child_process';

const MODELS_DIR = path.join(process.cwd(), '../models');
const DOWNLOADS_FILE = path.join(process.cwd(), '../config/downloaded-models.json');

// Ensure directories exist
const ensureDirs = () => {
  const configDir = path.dirname(DOWNLOADS_FILE);
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
    if (fs.existsSync(DOWNLOADS_FILE)) {
      const data = fs.readFileSync(DOWNLOADS_FILE, 'utf8');
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
    fs.writeFileSync(DOWNLOADS_FILE, JSON.stringify(models, null, 2));
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

// Download model using huggingface-hub
const downloadModelFromHF = async (modelId, hfToken) => {
  return new Promise((resolve, reject) => {
    const modelPath = path.join(MODELS_DIR, modelId.replace('/', '_'));
    
    // Create model directory
    if (!fs.existsSync(modelPath)) {
      fs.mkdirSync(modelPath, { recursive: true });
    }

    // Use huggingface-hub to download the model
    const args = [
      '-m', 'huggingface_hub.commands.download',
      modelId,
      '--cache-dir', modelPath,
      '--local-dir', modelPath
    ];

    if (hfToken) {
      args.push('--token', hfToken);
    }

    const process = spawn('python3', args, {
      stdio: ['pipe', 'pipe', 'pipe'],
      env: { ...process.env, PYTHONUNBUFFERED: '1' }
    });

    let stdout = '';
    let stderr = '';

    process.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    process.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    process.on('close', (code) => {
      if (code === 0) {
        resolve({ stdout, stderr });
      } else {
        reject(new Error(`Download failed with code ${code}: ${stderr}`));
      }
    });

    process.on('error', (error) => {
      reject(new Error(`Process error: ${error.message}`));
    });
  });
};

// Get model info from Hugging Face API
const getModelInfo = async (modelId, hfToken) => {
  try {
    const headers = {
      'User-Agent': 'TauTranslator/1.0'
    };
    
    if (hfToken) {
      headers['Authorization'] = `Bearer ${hfToken}`;
    }

    const response = await fetch(`https://huggingface.co/api/models/${modelId}`, {
      headers
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch model info: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching model info:', error);
    return null;
  }
};

export default async function handler(req, res) {
  const { method } = req;

  try {
    switch (method) {
      case 'GET': {
        const { search } = req.query;
        
        if (search) {
          // Search Hugging Face models
          try {
            const searchUrl = `https://huggingface.co/api/models?search=${encodeURIComponent(search)}&limit=20`;
            const response = await fetch(searchUrl);
            
            if (response.ok) {
              const models = await response.json();
              res.status(200).json(models);
            } else {
              res.status(500).json({ message: 'Failed to search models' });
            }
          } catch (error) {
            res.status(500).json({ message: 'Search failed' });
          }
        } else {
          // Get downloaded models
          const downloadedModels = loadDownloadedModels();
          
          const modelsWithStatus = downloadedModels.map(model => ({
            ...model,
            exists: checkModelExists(model.id),
            diskSize: getModelSize(model.id),
            diskSizeFormatted: getModelSize(model.id) > 0 ? 
              `${Math.round(getModelSize(model.id) / 1024 / 1024 / 1024 * 100) / 100}GB` : '0GB'
          }));

          res.status(200).json(modelsWithStatus);
        }
        break;
      }

      case 'POST': {
        // Download a model
        const { model_id, hf_token } = req.body;
        
        if (!model_id) {
          return res.status(400).json({ message: 'Model ID is required' });
        }

        // Get model info first
        const modelInfo = await getModelInfo(model_id, hf_token);
        
        const currentModels = loadDownloadedModels();
        const existingModel = currentModels.find(m => m.id === model_id);
        
        if (existingModel && checkModelExists(model_id)) {
          return res.status(400).json({ message: 'Model already downloaded' });
        }

        try {
          // Start download
          await downloadModelFromHF(model_id, hf_token);

          const newDownload = {
            id: model_id,
            name: modelInfo?.modelId || model_id,
            description: modelInfo?.description || 'Downloaded from Hugging Face',
            type: modelInfo?.pipeline_tag || 'unknown',
            parameters: modelInfo?.safetensors?.total || 'unknown',
            status: 'downloaded',
            downloadedAt: new Date().toISOString(),
            hfToken: hf_token ? 'provided' : 'not_provided',
            modelInfo: modelInfo
          };

          if (existingModel) {
            // Update existing
            const index = currentModels.findIndex(m => m.id === model_id);
            currentModels[index] = newDownload;
          } else {
            // Add new
            currentModels.push(newDownload);
          }
          
          if (saveDownloadedModels(currentModels)) {
            res.status(200).json({ 
              message: 'Model download completed',
              model: newDownload 
            });
          } else {
            res.status(500).json({ message: 'Failed to save download info' });
          }
        } catch (error) {
          res.status(500).json({ 
            message: 'Download failed', 
            error: error.message 
          });
        }
        break;
      }

      case 'DELETE': {
        // Delete a downloaded model
        const { id } = req.query;
        
        if (!id) {
          return res.status(400).json({ message: 'Model ID is required' });
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
      }

      default:
        res.setHeader('Allow', ['GET', 'POST', 'DELETE']);
        res.status(405).end(`Method ${method} Not Allowed`);
    }
  } catch (error) {
    console.error('Hugging Face models API error:', error);
    res.status(500).json({ 
      error: 'Internal server error',
      message: error.message 
    });
  }
}