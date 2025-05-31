/**
 * Direct Translation API - No Authentication Required
 * =================================================
 * 
 * This endpoint directly uses the LMQL translator without requiring
 * authentication or external API keys. Perfect for pattern-based translation.
 */

import { spawn } from 'child_process';
import path from 'path';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', ['POST']);
    return res.status(405).end(`Method ${req.method} Not Allowed`);
  }

  const { sourceText, sourceLangKey, targetLangKey } = req.body;

  if (!sourceText) {
    return res.status(400).json({
      error: 'Missing source text',
      message: 'sourceText is required'
    });
  }

  try {
    // Use the LMQL translator directly via Python
    const projectRoot = path.join(process.cwd(), '..');
    const pythonScript = `
import sys
sys.path.insert(0, '${projectRoot}')

from src.tau_translator_omega.lmql_engine.bidirectional_translator import LMQLBidirectionalTranslator

translator = LMQLBidirectionalTranslator()
source_text = """${sourceText.replace(/"/g, '\\"')}"""
source_lang = "${sourceLangKey}"
target_lang = "${targetLangKey}"

try:
    if source_lang == 'PLAIN_ENGLISH' and target_lang == 'TAU':
        result = translator.translate_tce_to_tau(source_text)
        print(f"SUCCESS:{result.output}")
    elif source_lang == 'TAU' and target_lang == 'PLAIN_ENGLISH':
        result = translator.translate_tau_to_tce(source_text)
        print(f"SUCCESS:{result.output}")
    else:
        print(f"SUCCESS:{source_text}")
except Exception as e:
    print(f"ERROR:{str(e)}")
`;

    const python = spawn('python3', ['-c', pythonScript], {
      cwd: projectRoot,
      env: { ...process.env, PYTHONPATH: projectRoot }
    });

    let output = '';
    let error = '';

    python.stdout.on('data', (data) => {
      output += data.toString();
    });

    python.stderr.on('data', (data) => {
      error += data.toString();
    });

    python.on('close', (code) => {
      if (code !== 0) {
        console.error('Python script error:', error);
        return res.status(500).json({
          error: 'Translation failed',
          message: error || 'Unknown error occurred',
          fallback: `${targetLangKey}: ${sourceText}`
        });
      }

      const lines = output.trim().split('\n');
      const lastLine = lines[lines.length - 1];

      if (lastLine.startsWith('SUCCESS:')) {
        const translatedText = lastLine.substring(8); // Remove "SUCCESS:"
        
        return res.status(200).json({
          translatedText: translatedText,
          provider: 'LMQL Pattern Translator',
          model: 'pattern-based',
          secure: true,
          mock: false,
          processingTime: 0.1
        });
      } else if (lastLine.startsWith('ERROR:')) {
        const errorMessage = lastLine.substring(6); // Remove "ERROR:"
        
        return res.status(500).json({
          error: 'Translation error',
          message: errorMessage,
          fallback: `${targetLangKey}: ${sourceText}`
        });
      } else {
        // Fallback
        return res.status(200).json({
          translatedText: `${targetLangKey}: ${sourceText}`,
          provider: 'Fallback',
          model: 'pattern-fallback',
          secure: true,
          mock: true,
          processingTime: 0.1
        });
      }
    });

  } catch (error) {
    console.error('Direct translation error:', error);
    
    return res.status(500).json({
      error: 'Translation failed',
      message: error.message,
      fallback: `${targetLangKey}: ${sourceText}`
    });
  }
}