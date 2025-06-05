/**
 * Unified Translation API v1
 * =========================
 * Single endpoint for all translation needs
 * 
 * Author: DarkLightX/Dana Edwards
 */

import translationService from '../../../services/translationService';

export default async function handler(req, res) {
  // Only allow POST
  if (req.method !== 'POST') {
    res.setHeader('Allow', ['POST']);
    return res.status(405).json({ 
      error: 'Method not allowed',
      message: `Method ${req.method} not allowed. Use POST.`
    });
  }

  // Validate request body
  const { sourceText, sourceLang, targetLang, options = {} } = req.body;

  if (!sourceText) {
    return res.status(400).json({
      error: 'Bad request',
      message: 'sourceText is required'
    });
  }

  if (!sourceLang || !targetLang) {
    return res.status(400).json({
      error: 'Bad request',
      message: 'sourceLang and targetLang are required'
    });
  }

  // Extract API key from Authorization header if present
  const authHeader = req.headers.authorization;
  if (authHeader && authHeader.startsWith('Bearer ')) {
    options.apiKey = authHeader.substring(7);
  }

  try {
    // Perform translation
    const result = await translationService.translate({
      sourceText,
      sourceLang,
      targetLang,
      options
    });

    // Return successful response
    return res.status(200).json({
      success: true,
      ...result,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('Translation error:', error);

    // Handle specific error types
    if (error.message === 'Source text is required') {
      return res.status(400).json({
        error: 'Bad request',
        message: error.message
      });
    }

    // Generic error response
    return res.status(500).json({
      error: 'Translation failed',
      message: error.message || 'An unexpected error occurred',
      translatedText: sourceText, // Return source as fallback
      provider: 'Error fallback'
    });
  }
}

// Export config for Next.js
export const config = {
  api: {
    bodyParser: {
      sizeLimit: '1mb',
    },
  },
};