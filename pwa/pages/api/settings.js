import fs from 'fs';
import path from 'path';

const SETTINGS_FILE = path.join(process.cwd(), '../config/settings.json');
const GRAMMAR_DIR = path.join(process.cwd(), '../grammars');
const MODELS_DIR = path.join(process.cwd(), '../models');

export default async function handler(req, res) {
  if (req.method === 'GET') {
    try {
      // Load current settings
      let settings = {};
      if (fs.existsSync(SETTINGS_FILE)) {
        settings = JSON.parse(fs.readFileSync(SETTINGS_FILE, 'utf8'));
      }

      // Scan for grammar files
      const grammarFiles = [];
      if (fs.existsSync(GRAMMAR_DIR)) {
        const files = fs.readdirSync(GRAMMAR_DIR);
        files.forEach(file => {
          const filePath = path.join(GRAMMAR_DIR, file);
          const stats = fs.statSync(filePath);
          const ext = path.extname(file).toLowerCase();
          
          if (['.ebnf', '.lark', '.tgf', '.bnf'].includes(ext)) {
            grammarFiles.push({
              name: file,
              type: ext.slice(1).toUpperCase(),
              size: `${Math.round(stats.size / 1024)}KB`,
              path: filePath
            });
          }
        });
      }

      // Scan for model files
      const models = [];
      if (fs.existsSync(MODELS_DIR)) {
        const scanDir = (dir, prefix = '') => {
          const files = fs.readdirSync(dir);
          files.forEach(file => {
            const filePath = path.join(dir, file);
            const stats = fs.statSync(filePath);
            
            if (stats.isDirectory()) {
              scanDir(filePath, `${prefix}${file}/`);
            } else {
              const ext = path.extname(file).toLowerCase();
              if (['.bin', '.gguf', '.safetensors', '.ggml'].includes(ext)) {
                models.push({
                  name: `${prefix}${file}`,
                  type: ext.slice(1).toUpperCase(),
                  status: 'available',
                  path: filePath
                });
              }
            }
          });
        };
        scanDir(MODELS_DIR);
      }

      // Check for Gemma 3
      const gemma3Config = path.join(MODELS_DIR, 'gemma3/config.json');
      if (fs.existsSync(gemma3Config)) {
        models.push({
          name: 'Gemma 3',
          type: 'Transformers',
          status: 'ready',
          path: path.dirname(gemma3Config)
        });
      }

      res.status(200).json({
        grammarFiles,
        models,
        selectedGrammar: settings.selectedGrammar || '',
        selectedModel: settings.selectedModel || ''
      });

    } catch (error) {
      console.error('Settings load error:', error);
      res.status(500).json({ error: 'Failed to load settings' });
    }

  } else if (req.method === 'POST') {
    try {
      const { selectedGrammar, selectedModel } = req.body;

      // Ensure config directory exists
      const configDir = path.dirname(SETTINGS_FILE);
      if (!fs.existsSync(configDir)) {
        fs.mkdirSync(configDir, { recursive: true });
      }

      // Save settings
      const settings = {
        selectedGrammar,
        selectedModel,
        lastUpdated: new Date().toISOString()
      };

      fs.writeFileSync(SETTINGS_FILE, JSON.stringify(settings, null, 2));

      res.status(200).json({ success: true });

    } catch (error) {
      console.error('Settings save error:', error);
      res.status(500).json({ error: 'Failed to save settings' });
    }

  } else {
    res.setHeader('Allow', ['GET', 'POST']);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}