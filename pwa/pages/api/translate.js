/**
 * Translation API Route - Integrates with Secure Backend
 * =====================================================
 *
 * This route now connects to the secure Python backend for real AI translation
 * with encrypted API key management.
 */

// Use Next.js proxy instead of direct backend calls to avoid CORS
const BACKEND_URL = process.env.BACKEND_URL || 'http://127.0.0.1:8000';

export default async function handler(req, res) {
  if (req.method === 'POST') {
    const { sourceText, sourceLangKey, targetLangKey, sourceLangLabel, targetLangLabel } = req.body;

    try {
      // Get session token from headers
      const authHeader = req.headers.authorization;

      if (!authHeader) {
        return res.status(401).json({
          error: 'Authentication required',
          message: 'Please authenticate with your master password first'
        });
      }

      console.log(`API: Translating from ${sourceLangLabel} (${sourceLangKey}) to ${targetLangLabel} (${targetLangKey}):\n${sourceText}`);

      // Try to call secure backend
      const backendResponse = await fetch(`${BACKEND_URL}/api/translate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': authHeader
        },
        body: JSON.stringify({
          sourceText,
          sourceLangKey,
          targetLangKey,
          sourceLangLabel,
          targetLangLabel
        })
      });

      if (!backendResponse.ok) {
        const errorData = await backendResponse.json().catch(() => ({}));

        if (backendResponse.status === 401) {
          return res.status(401).json({
            error: 'Authentication failed',
            message: 'Please re-authenticate with your master password'
          });
        }

        if (backendResponse.status === 400) {
          return res.status(400).json({
            error: 'Configuration required',
            message: errorData.detail || 'Please configure AI provider API keys first'
          });
        }

        throw new Error(`Backend error: ${backendResponse.status} - ${errorData.detail || 'Unknown error'}`);
      }

      const translationResult = await backendResponse.json();

      // Return the secure backend response
      res.status(200).json({
        translatedText: translationResult.translatedText,
        provider: translationResult.provider,
        model: translationResult.model,
        processingTime: translationResult.processingTime,
        secure: true
      });

    } catch (error) {
      console.error('Translation API error:', error);

      // Check if backend is unavailable - fallback to mock
      if (error.code === 'ECONNREFUSED' || error.message.includes('fetch')) {
        console.log('Backend unavailable, using fallback mock translation');

        // Fallback mock response
        let fallbackTranslatedText = `[Fallback Mock]: Translated from ${sourceLangLabel} to ${targetLangLabel}:\n"${sourceText.substring(0, 50)}..."`;

        if (sourceText) {
          if (sourceLangKey === 'PLAIN_ENGLISH') {
            if (targetLangKey === 'CNL') {
              fallbackTranslatedText = `[Fallback CNL]: This is a controlled version of: "${sourceText.substring(0, 50)}..."`;
            } else if (targetLangKey === 'TAU') {
              fallbackTranslatedText = `// Fallback Tau Code for: "${sourceText.substring(0, 50)}..."\nDEFINE CONCEPT fallback_example AS ( ... );`;
            } else if (targetLangKey === 'ILR') {
              fallbackTranslatedText = `<ILR_Fallback>\n  <statement text="${sourceText.substring(0,50)}...">\n  </statement>\n</ILR_Fallback>`;
            }
          } else {
            fallbackTranslatedText = `[Fallback Plain English]: This represents: "${sourceText.substring(0, 50)}..." (from ${sourceLangLabel})`;
          }
        }

        return res.status(200).json({
          translatedText: fallbackTranslatedText,
          provider: 'fallback',
          model: 'mock',
          processingTime: 0.5,
          secure: false,
          warning: 'Using fallback translation - secure backend unavailable'
        });
      }

      // Other errors
      res.status(500).json({
        error: 'Translation failed',
        message: error.message,
        secure: false
      });
    }
  } else {
    res.setHeader('Allow', ['POST']);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}
