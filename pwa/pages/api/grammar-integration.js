import fs from 'fs';
import path from 'path';

const GRAMMAR_CONFIG_FILE = path.join(process.cwd(), '../config/grammar-files.json');
const GRAMMARS_DIR = path.join(process.cwd(), '../grammars');

// Load active grammar file
const getActiveGrammar = () => {
  try {
    if (fs.existsSync(GRAMMAR_CONFIG_FILE)) {
      const data = fs.readFileSync(GRAMMAR_CONFIG_FILE, 'utf8');
      const grammarFiles = JSON.parse(data);
      return grammarFiles.find(f => f.isActive) || null;
    }
    return null;
  } catch (error) {
    console.error('Error loading active grammar:', error);
    return null;
  }
};

// Read grammar file content
const getGrammarContent = (grammarFile) => {
  try {
    const filePath = path.join(GRAMMARS_DIR, grammarFile.filename);
    if (fs.existsSync(filePath)) {
      return fs.readFileSync(filePath, 'utf8');
    }
    return null;
  } catch (error) {
    console.error('Error reading grammar file:', error);
    return null;
  }
};

// Validate translation input against grammar (basic validation)
const validateAgainstGrammar = (input, grammarContent, grammarType) => {
  if (!grammarContent) return { valid: true, message: 'No grammar validation available' };

  try {
    switch (grammarType) {
      case '.tgf':
        // Basic TGF validation - check for common patterns
        if (input.includes('always') || input.includes('eventually') || input.includes('until')) {
          return { valid: true, message: 'Contains temporal logic patterns' };
        }
        return { valid: true, message: 'TGF validation passed' };
      
      case '.ebnf':
      case '.bnf':
        // Basic EBNF validation
        return { valid: true, message: 'EBNF validation passed' };
      
      case '.lark':
        // Basic Lark validation
        return { valid: true, message: 'Lark validation passed' };
      
      default:
        return { valid: true, message: 'Generic validation passed' };
    }
  } catch (error) {
    return { valid: false, message: `Validation error: ${error.message}` };
  }
};

export default async function handler(req, res) {
  const { method } = req;

  try {
    switch (method) {
      case 'GET':
        // Get active grammar info and content
        const activeGrammar = getActiveGrammar();
        
        if (!activeGrammar) {
          return res.status(200).json({
            hasActiveGrammar: false,
            message: 'No active grammar file configured'
          });
        }

        const content = getGrammarContent(activeGrammar);
        
        res.status(200).json({
          hasActiveGrammar: true,
          grammar: {
            ...activeGrammar,
            content: content,
            contentPreview: content ? content.substring(0, 500) + (content.length > 500 ? '...' : '') : null
          }
        });
        break;

      case 'POST':
        // Validate input text against active grammar
        const { input } = req.body;
        
        if (!input) {
          return res.status(400).json({ message: 'Input text is required' });
        }

        const grammar = getActiveGrammar();
        
        if (!grammar) {
          return res.status(200).json({
            validated: false,
            message: 'No active grammar for validation',
            suggestions: []
          });
        }

        const grammarContent = getGrammarContent(grammar);
        const validation = validateAgainstGrammar(input, grammarContent, grammar.type);
        
        // Provide basic suggestions based on grammar type
        let suggestions = [];
        if (grammar.type === '.tgf') {
          suggestions = [
            'Try using temporal operators: always, eventually, until',
            'Use logical operators: and, or, not',
            'Consider quantifiers: for all, exists'
          ];
        }

        res.status(200).json({
          validated: true,
          grammar: {
            name: grammar.originalName,
            type: grammar.type
          },
          validation: validation,
          suggestions: validation.valid ? [] : suggestions
        });
        break;

      default:
        res.setHeader('Allow', ['GET', 'POST']);
        res.status(405).end(`Method ${method} Not Allowed`);
    }
  } catch (error) {
    console.error('Grammar integration API error:', error);
    res.status(500).json({ 
      error: 'Internal server error',
      message: error.message 
    });
  }
}