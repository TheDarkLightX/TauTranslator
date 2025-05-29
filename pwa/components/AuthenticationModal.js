import { useState } from 'react';
import styles from '../styles/AuthModal.module.css';

export default function AuthenticationModal({ isOpen, onAuthenticate, onClose }) {
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

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Authentication failed');
      }

      const data = await response.json();
      
      if (data.authenticated && data.sessionToken) {
        // Store session token
        localStorage.setItem('sessionToken', data.sessionToken);
        localStorage.setItem('authenticated', 'true');
        
        // Clear form
        setPassword('');
        setError('');
        
        // Notify parent component
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

  const handleClose = () => {
    setPassword('');
    setError('');
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div
      className={styles.modalOverlay}
      onClick={(e) => {
        // Only close if clicking the overlay, not the modal content
        if (e.target === e.currentTarget) {
          handleClose();
        }
      }}
    >
      <div
        className={styles.modalContent}
        onClick={(e) => e.stopPropagation()} // Prevent closing when clicking inside modal
      >
        <div className={styles.modalHeader}>
          <h2>🔐 Authentication Required</h2>
          <button
            className={styles.closeButton}
            onClick={handleClose}
            disabled={isLoading}
            type="button"
          >
            ×
          </button>
        </div>

        <div className={styles.modalBody}>
          <p>Enter your master password to access secure translation features:</p>

          <form onSubmit={handleSubmit}>
            <div className={styles.inputGroup}>
              <label htmlFor="password">Master Password:</label>
              <input
                type="password"
                id="password"
                name="password"
                value={password}
                onChange={(e) => {
                  console.log('Password input changed:', e.target.value); // Debug log
                  setPassword(e.target.value);
                }}
                onFocus={() => console.log('Password input focused')} // Debug log
                placeholder="Enter your master password"
                disabled={isLoading}
                autoFocus
                autoComplete="current-password"
                className={styles.passwordInput}
                style={{
                  pointerEvents: 'auto',
                  userSelect: 'text',
                  WebkitUserSelect: 'text'
                }}
              />
            </div>

            {error && (
              <div className={styles.errorMessage}>
                ❌ {error}
              </div>
            )}

            <div className={styles.buttonGroup}>
              <button
                type="button"
                onClick={handleClose}
                disabled={isLoading}
                className={styles.cancelButton}
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isLoading || !password.trim()}
                className={styles.authenticateButton}
              >
                {isLoading ? '🔄 Authenticating...' : '🔓 Authenticate'}
              </button>
            </div>
          </form>

          <div className={styles.helpText}>
            <p><strong>First time?</strong> Enter any password to create your secure storage.</p>
            <p><strong>Returning user?</strong> Enter your existing master password.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
