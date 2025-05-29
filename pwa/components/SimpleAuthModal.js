import { useState } from 'react';

export default function SimpleAuthModal({ isOpen, onAuthenticate, onClose }) {
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!password.trim()) {
      setError('Please enter your master password');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      console.log('Attempting authentication...');

      const response = await fetch('/auth', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          password: password,
          action: 'authenticate'
        }),
      });

      console.log('Response status:', response.status);
      console.log('Response headers:', response.headers.get('content-type'));

      if (!response.ok) {
        // Check if response is JSON
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
          const errorData = await response.json();
          throw new Error(errorData.message || `HTTP ${response.status}: Authentication failed`);
        } else {
          // Non-JSON response (probably HTML error page)
          const errorText = await response.text();
          console.log('Non-JSON error response:', errorText.substring(0, 200));

          if (response.status === 404) {
            throw new Error('Backend not available. Please start the FastAPI backend first.');
          } else if (response.status === 500) {
            throw new Error('Backend server error. Check if the backend is running properly.');
          } else {
            throw new Error(`Backend error (${response.status}). Check if FastAPI backend is running.`);
          }
        }
      }

      // Check if response is JSON
      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        const responseText = await response.text();
        console.log('Non-JSON success response:', responseText.substring(0, 200));
        throw new Error('Backend returned non-JSON response. Check if FastAPI backend is running.');
      }

      const data = await response.json();
      console.log('Authentication response:', data);
      
      if (data.authenticated && data.sessionToken) {
        localStorage.setItem('sessionToken', data.sessionToken);
        localStorage.setItem('authenticated', 'true');
        
        setPassword('');
        setError('');
        onAuthenticate(data.sessionToken);
      } else {
        throw new Error('Authentication failed - invalid response');
      }

    } catch (error) {
      console.error('Authentication error:', error);
      setError(error.message || 'Authentication failed');
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.7)',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      zIndex: 10000
    }}>
      <div style={{
        backgroundColor: 'white',
        padding: '30px',
        borderRadius: '10px',
        maxWidth: '400px',
        width: '90%',
        boxShadow: '0 10px 30px rgba(0,0,0,0.3)'
      }}>
        <h2 style={{ marginTop: 0, textAlign: 'center' }}>🔐 Authentication Required</h2>
        
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
              Master Password:
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your master password"
              disabled={isLoading}
              autoFocus
              style={{
                width: '100%',
                padding: '12px',
                border: '2px solid #ddd',
                borderRadius: '6px',
                fontSize: '16px',
                boxSizing: 'border-box'
              }}
            />
          </div>
          
          {error && (
            <div style={{
              backgroundColor: '#fee',
              border: '1px solid #fcc',
              color: '#c33',
              padding: '10px',
              borderRadius: '4px',
              marginBottom: '15px'
            }}>
              ❌ {error}
            </div>
          )}
          
          <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
            <button
              type="button"
              onClick={() => {
                setPassword('');
                setError('');
                onClose();
              }}
              disabled={isLoading}
              style={{
                padding: '10px 20px',
                border: '2px solid #ddd',
                backgroundColor: 'transparent',
                borderRadius: '6px',
                cursor: 'pointer'
              }}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading || !password.trim()}
              style={{
                padding: '10px 20px',
                border: 'none',
                backgroundColor: '#007bff',
                color: 'white',
                borderRadius: '6px',
                cursor: 'pointer',
                opacity: (isLoading || !password.trim()) ? 0.6 : 1
              }}
            >
              {isLoading ? '🔄 Authenticating...' : '🔓 Authenticate'}
            </button>
          </div>
        </form>
        
        <div style={{ marginTop: '20px', fontSize: '14px', color: '#666' }}>
          <p><strong>First time?</strong> Enter any password to create your secure storage.</p>
          <p><strong>Returning user?</strong> Enter your existing master password.</p>
        </div>
      </div>
    </div>
  );
}
