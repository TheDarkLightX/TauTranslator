/**
 * Translation Hook
 * ================
 * Custom React hook for translation functionality
 * 
 * Author: DarkLightX/Dana Edwards
 */

import { useState, useCallback } from 'react';
import translationService from '../services/translationService';
import authService from '../services/authService';

export function useTranslation() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [lastTranslation, setLastTranslation] = useState(null);

  const translate = useCallback(async ({ sourceText, sourceLang, targetLang, options = {} }) => {
    // Clear previous error
    setError('');
    
    // Validate input
    if (!sourceText || !sourceText.trim()) {
      const err = 'Please enter text to translate';
      setError(err);
      return { success: false, error: err };
    }

    setIsLoading(true);

    try {
      // Add auth token if available
      const token = authService.getToken();
      if (token) {
        options.apiKey = token;
      }

      // Perform translation
      const result = await translationService.translate({
        sourceText,
        sourceLang,
        targetLang,
        options
      });

      // Store successful result
      setLastTranslation({
        sourceText,
        sourceLang,
        targetLang,
        translatedText: result.translatedText,
        provider: result.provider
      });

      return {
        success: true,
        ...result
      };

    } catch (err) {
      const errorMessage = err.message || 'Translation failed';
      setError(errorMessage);
      
      // Check if auth error
      if (errorMessage.includes('Authentication')) {
        return {
          success: false,
          error: errorMessage,
          requiresAuth: true
        };
      }

      return {
        success: false,
        error: errorMessage
      };

    } finally {
      setIsLoading(false);
    }
  }, []);

  const clearError = useCallback(() => {
    setError('');
  }, []);

  return {
    translate,
    isLoading,
    error,
    clearError,
    lastTranslation
  };
}