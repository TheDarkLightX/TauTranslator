/**
 * Authentication Service
 * =====================
 * Centralized authentication logic
 * 
 * Author: DarkLightX/Dana Edwards
 */

class AuthService {
  constructor() {
    this.tokenKey = 'sessionToken';
    this.authKey = 'authenticated';
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated() {
    if (typeof window === 'undefined') return false;
    
    const token = localStorage.getItem(this.tokenKey);
    const authStatus = localStorage.getItem(this.authKey);
    
    return Boolean(token && authStatus === 'true');
  }

  /**
   * Get current session token
   */
  getToken() {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem(this.tokenKey);
  }

  /**
   * Authenticate with password
   */
  async authenticate(password) {
    if (!password || !password.trim()) {
      throw new Error('Password is required');
    }

    try {
      const response = await fetch('/api/auth', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          password,
          action: 'authenticate'
        }),
      });

      if (!response.ok) {
        // Handle different error types
        if (response.status === 404) {
          throw new Error('Authentication service not available');
        }
        
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
          const errorData = await response.json();
          throw new Error(errorData.message || 'Authentication failed');
        } else {
          throw new Error(`Authentication failed (${response.status})`);
        }
      }

      const data = await response.json();
      
      if (!data.authenticated || !data.sessionToken) {
        throw new Error('Invalid authentication response');
      }

      // Store authentication data
      this.setSession(data.sessionToken);
      
      return {
        success: true,
        token: data.sessionToken
      };

    } catch (error) {
      // Re-throw with cleaner error messages
      if (error.message.includes('fetch')) {
        throw new Error('Cannot connect to authentication service');
      }
      throw error;
    }
  }

  /**
   * Store session data
   */
  setSession(token) {
    if (typeof window === 'undefined') return;
    
    localStorage.setItem(this.tokenKey, token);
    localStorage.setItem(this.authKey, 'true');
  }

  /**
   * Clear session (logout)
   */
  logout() {
    if (typeof window === 'undefined') return;
    
    localStorage.removeItem(this.tokenKey);
    localStorage.removeItem(this.authKey);
  }

  /**
   * Get authorization headers
   */
  getAuthHeaders() {
    const token = this.getToken();
    if (!token) return {};
    
    return {
      'Authorization': `Bearer ${token}`
    };
  }

  /**
   * Make authenticated request
   */
  async authenticatedFetch(url, options = {}) {
    const authHeaders = this.getAuthHeaders();
    
    const response = await fetch(url, {
      ...options,
      headers: {
        ...options.headers,
        ...authHeaders
      }
    });

    // Handle auth errors
    if (response.status === 401) {
      this.logout();
      throw new Error('Authentication expired. Please log in again.');
    }

    return response;
  }
}

// Export singleton instance
export default new AuthService();