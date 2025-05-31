import formidable from 'formidable';
import fs from 'fs';
import path from 'path';

export const config = {
  api: {
    bodyParser: false,
  },
};

const GRAMMAR_DIR = path.join(process.cwd(), '../grammars');
const MODELS_DIR = path.join(process.cwd(), '../models');
const EXAMPLES_DIR = path.join(process.cwd(), '../examples');

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', ['POST']);
    return res.status(405).end(`Method ${req.method} Not Allowed`);
  }

  try {
    const form = formidable({
      maxFileSize: 100 * 1024 * 1024, // 100MB max
      keepExtensions: true,
    });

    const [fields, files] = await form.parse(req);
    const uploadType = fields.type[0];
    const uploadedFile = files.file[0];

    if (!uploadedFile) {
      return res.status(400).json({ error: 'No file uploaded' });
    }

    let targetDir;
    let allowedExtensions;

    switch (uploadType) {
      case 'grammar':
        targetDir = GRAMMAR_DIR;
        allowedExtensions = ['.ebnf', '.lark', '.tgf', '.bnf'];
        break;
      case 'model':
        targetDir = MODELS_DIR;
        allowedExtensions = ['.bin', '.gguf', '.safetensors', '.ggml'];
        break;
      case 'examples':
        targetDir = EXAMPLES_DIR;
        allowedExtensions = ['.cnl', '.tau', '.tce', '.txt'];
        break;
      default:
        return res.status(400).json({ error: 'Invalid upload type' });
    }

    // Validate file extension
    const fileExt = path.extname(uploadedFile.originalFilename).toLowerCase();
    if (!allowedExtensions.includes(fileExt)) {
      return res.status(400).json({
        error: `Invalid file type. Allowed: ${allowedExtensions.join(', ')}`
      });
    }

    // Ensure target directory exists
    if (!fs.existsSync(targetDir)) {
      fs.mkdirSync(targetDir, { recursive: true });
    }

    // Move file to target directory
    const targetPath = path.join(targetDir, uploadedFile.originalFilename);
    fs.copyFileSync(uploadedFile.filepath, targetPath);
    fs.unlinkSync(uploadedFile.filepath); // Clean up temp file

    res.status(200).json({
      success: true,
      filename: uploadedFile.originalFilename,
      path: targetPath,
      type: uploadType
    });

  } catch (error) {
    console.error('Upload error:', error);
    res.status(500).json({ error: 'Upload failed' });
  }
}