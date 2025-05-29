/**
 * Authentication API Route - Proxied to FastAPI Backend
 * ====================================================
 *
 * Handles authentication with the secure backend using master password.
 * Uses Next.js proxy to avoid CORS issues.
 */

// Use Next.js proxy instead of direct backend calls to avoid CORS
const BACKEND_URL = process.env.BACKEND_URL || 'http://127.0.0.1:8000';

export default async function handler(req, res) {
  if (req.method === 'POST') {
    const { password, action } = req.body;

    try {
      if (action === 'authenticate') {
        // TEMPORARY: Mock authentication when backend is unavailable
        if (!password || password.trim().length === 0) {
          return res.status(400).json({
            error: 'Invalid password',
            message: 'Please enter a password'
          });
        }

        // Try to authenticate with backend first
        try {
          const backendResponse = await fetch(`${BACKEND_URL}/auth`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({ password })
          });

        if (!backendResponse.ok) {
          const errorData = await backendResponse.json().catch(() => ({}));
          
          if (backendResponse.status === 401) {
            return res.status(401).json({
              error: 'Authentication failed',
              message: 'Incorrect master password'
            });
          }

          throw new Error(`Backend error: ${backendResponse.status} - ${errorData.detail || 'Unknown error'}`);
        }

        const authResult = await backendResponse.json();
        
        return res.status(200).json({
          authenticated: authResult.authenticated,
          sessionToken: authResult.sessionToken,
          message: 'Authentication successful'
        });

        } catch (backendError) {
          // Backend is unavailable, return error instead of mock
          console.error('Backend unavailable:', backendError.message);

          return res.status(503).json({
            error: 'Backend unavailable',
            message: 'Authentication backend is not running. Please start the backend server.',
            backendAvailable: false
          });
        }

      } else if (action === 'check') {
        // Check backend health and authentication status
        const healthResponse = await fetch(`${BACKEND_URL}/health`);
        
        if (!healthResponse.ok) {
          throw new Error('Backend unavailable');
        }

        const healthData = await healthResponse.json();
        
        return res.status(200).json({
          backendAvailable: true,
          secureStorageAvailable: healthData.secureStorageAvailable,
          cryptoAvailable: healthData.cryptoAvailable,
          configuredProviders: healthData.configuredProviders
        });

      } else {
        return res.status(400).json({
          error: 'Invalid action',
          message: 'Action must be "authenticate" or "check"'
        });
      }

    } catch (error) {
      console.error('Authentication API error:', error);
      
      // Check if backend is unavailable
      if (error.code === 'ECONNREFUSED' || error.message.includes('fetch')) {
        return res.status(503).json({
          error: 'Backend unavailable',
          message: 'Secure backend is not running. Please start the backend server.',
          backendAvailable: false
        });
      }

      return res.status(500).json({
        error: 'Authentication failed',
        message: error.message
      });
    }

  } else {
    res.setHeader('Allow', ['POST']);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}
