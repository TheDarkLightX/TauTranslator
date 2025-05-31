import fs from 'fs';
import path from 'path';
import formidable from 'formidable';

const GRAMMARS_DIR = path.join(process.cwd(), '../grammars');
const GRAMMAR_CONFIG_FILE = path.join(process.cwd(), '../config/grammar-files.json');

// Ensure directories exist
const ensureDirs = () => {
  const configDir = path.dirname(GRAMMAR_CONFIG_FILE);
  if (!fs.existsSync(configDir)) {
    fs.mkdirSync(configDir, { recursive: true });
  }
  if (!fs.existsSync(GRAMMARS_DIR)) {
    fs.mkdirSync(GRAMMARS_DIR, { recursive: true });
  }
};

// Load grammar files info
const loadGrammarFiles = () => {
  try {
    if (fs.existsSync(GRAMMAR_CONFIG_FILE)) {
      const data = fs.readFileSync(GRAMMAR_CONFIG_FILE, 'utf8');
      return JSON.parse(data);
    }
    return [];
  } catch (error) {
    console.error('Error loading grammar files:', error);
    return [];
  }
};

// Save grammar files info
const saveGrammarFiles = (files) => {
  try {
    ensureDirs();
    fs.writeFileSync(GRAMMAR_CONFIG_FILE, JSON.stringify(files, null, 2));
    return true;
  } catch (error) {
    console.error('Error saving grammar files:', error);
    return false;
  }
};

// Get file size
const getFileSize = (filePath) => {
  try {
    const stats = fs.statSync(filePath);
    return stats.size;
  } catch (error) {
    return 0;
  }
};

// Validate grammar file format
const validateGrammarFile = (filePath, fileType) => {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    
    switch (fileType) {
      case '.ebnf':
      case '.bnf':
        // Basic EBNF validation - check for rule definitions
        return content.includes('::=') || content.includes('=');
      
      case '.lark':
        // Basic Lark validation - check for rule definitions
        return content.includes(':') && (content.includes('|') || content.includes('"'));
      
      case '.tgf':
        // TGF validation - check for TGF-specific syntax
        return content.includes('%%') || content.includes('@') || content.includes('::=');
      
      case '.cnl':
        // CNL validation - should be plain text
        return content.trim().length > 0;
      
      default:
        return true; // Allow other file types
    }
  } catch (error) {
    return false;
  }
};

// Parse formidable form
const parseForm = (req) => {
  const form = formidable({
    uploadDir: GRAMMARS_DIR,
    keepExtensions: true,
    maxFileSize: 10 * 1024 * 1024, // 10MB limit
  });

  return new Promise((resolve, reject) => {
    form.parse(req, (err, fields, files) => {
      if (err) reject(err);
      else resolve({ fields, files });
    });
  });
};

export const config = {
  api: {
    bodyParser: false, // Disable body parsing for file uploads
  },
};

export default async function handler(req, res) {
  const { method } = req;

  try {
    ensureDirs();

    switch (method) {
      case 'GET': {
        // Get all grammar files
        const grammarFiles = loadGrammarFiles();
        
        // Add current file status
        const filesWithStatus = grammarFiles.map(file => {
          const filePath = path.join(GRAMMARS_DIR, file.filename);
          const exists = fs.existsSync(filePath);
          const size = exists ? getFileSize(filePath) : 0;
          
          return {
            ...file,
            exists,
            size,
            sizeFormatted: size > 0 ? `${Math.round(size / 1024 * 100) / 100}KB` : '0KB'
          };
        });

        res.status(200).json(filesWithStatus);
        break;
      }

      case 'POST': {
        // Upload grammar files
        try {
          const { fields, files } = await parseForm(req);
          
          const uploadedFiles = [];
          const currentFiles = loadGrammarFiles();

          // Handle multiple files
          const fileArray = Array.isArray(files.files) ? files.files : [files.files].filter(Boolean);
          
          for (const file of fileArray) {
            if (!file) continue;

            const fileExt = path.extname(file.originalFilename || '').toLowerCase();
            const allowedExts = ['.ebnf', '.tgf', '.lark', '.bnf', '.cnl', '.cfg', '.json', '.txt'];
            
            if (!allowedExts.includes(fileExt)) {
              throw new Error(`File type ${fileExt} not supported. Allowed: ${allowedExts.join(', ')}`);
            }

            // Validate grammar file
            if (!validateGrammarFile(file.filepath, fileExt)) {
              throw new Error(`Invalid grammar file format: ${file.originalFilename}`);
            }

            const filename = `${Date.now()}_${file.originalFilename}`;
            const finalPath = path.join(GRAMMARS_DIR, filename);
            
            // Move file to final location
            fs.renameSync(file.filepath, finalPath);

            const fileInfo = {
              id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
              filename,
              originalName: file.originalFilename,
              type: fileExt,
              size: file.size,
              uploadedAt: new Date().toISOString(),
              description: fields.description?.[0] || '',
              isActive: currentFiles.length === 0, // First file becomes active
              path: finalPath
            };

            currentFiles.push(fileInfo);
            uploadedFiles.push(fileInfo);
          }

          if (saveGrammarFiles(currentFiles)) {
            res.status(200).json({ 
              message: 'Files uploaded successfully',
              files: uploadedFiles 
            });
          } else {
            res.status(500).json({ message: 'Failed to save file info' });
          }
        } catch (error) {
          console.error('Upload error:', error);
          res.status(500).json({ 
            message: 'Upload failed', 
            error: error.message 
          });
        }
        break;
      }

      case 'PUT': {
        // Update grammar file info (set active, description, etc.)
        const { id } = req.query;
        const { isActive, description, name } = req.body;
        
        if (!id) {
          return res.status(400).json({ message: 'File ID is required' });
        }

        const currentFiles = loadGrammarFiles();
        const fileIndex = currentFiles.findIndex(f => f.id === id);
        
        if (fileIndex === -1) {
          return res.status(404).json({ message: 'File not found' });
        }

        // If setting this file as active, deactivate others
        if (isActive) {
          currentFiles.forEach(file => {
            file.isActive = false;
          });
        }

        // Update file info
        currentFiles[fileIndex] = {
          ...currentFiles[fileIndex],
          isActive: isActive !== undefined ? isActive : currentFiles[fileIndex].isActive,
          description: description !== undefined ? description : currentFiles[fileIndex].description,
          name: name !== undefined ? name : currentFiles[fileIndex].name,
          updatedAt: new Date().toISOString()
        };

        if (saveGrammarFiles(currentFiles)) {
          res.status(200).json(currentFiles[fileIndex]);
        } else {
          res.status(500).json({ message: 'Failed to update file' });
        }
        break;
      }

      case 'DELETE': {
        // Delete grammar file
        const { id } = req.query;
        
        if (!id) {
          return res.status(400).json({ message: 'File ID is required' });
        }

        const currentFiles = loadGrammarFiles();
        const fileToDelete = currentFiles.find(f => f.id === id);
        
        if (!fileToDelete) {
          return res.status(404).json({ message: 'File not found' });
        }

        // Delete physical file
        const filePath = path.join(GRAMMARS_DIR, fileToDelete.filename);
        if (fs.existsSync(filePath)) {
          fs.unlinkSync(filePath);
        }

        // Remove from config
        const filteredFiles = currentFiles.filter(f => f.id !== id);

        if (saveGrammarFiles(filteredFiles)) {
          res.status(200).json({ message: 'File deleted successfully' });
        } else {
          res.status(500).json({ message: 'Failed to save changes' });
        }
        break;
      }

      default:
        res.setHeader('Allow', ['GET', 'POST', 'PUT', 'DELETE']);
        res.status(405).end(`Method ${method} Not Allowed`);
    }
  } catch (error) {
    console.error('Grammar files API error:', error);
    res.status(500).json({ 
      error: 'Internal server error',
      message: error.message 
    });
  }
}