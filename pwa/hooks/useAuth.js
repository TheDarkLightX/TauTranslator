/**
 * Authentication Hook
 * ==================
 * Custom React hook for authentication state management
 * 
 * Author: DarkLightX/Dana Edwards
 */

import { useState, useEffect, useCallback } from 'react';
import authService from '../services/authService';

export function useAuth() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Check auth status on mount
  useEffect(() => {
    const checkAuth = () => {
      const authenticated = authService.isAuthenticated();
      setIsAuthenticated(authenticated);
      setIsLoading(false);
    };

    checkAuth();

    // Listen for storage changes (logout in other tabs)
    const handleStorageChange = (e) => {
      if (e.key === 'sessionToken' || e.key === 'authenticated') {
        checkAuth();
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  const login = useCallback(async (password) => {
    try {
      const result = await authService.authenticate(password);
      setIsAuthenticated(true);
      return result;
    } catch (error) {
      throw error;
    }
  }, []);

  const logout = useCallback(() => {
    authService.logout();
    setIsAuthenticated(false);
  }, []);

  return {
    isAuthenticated,
    isLoading,
    login,
    logout
  };
}