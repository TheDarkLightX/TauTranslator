/**
 * Unified Authentication Modal
 * ===========================
 * Single auth modal component with clean design
 * 
 * Author: DarkLightX/Dana Edwards
 */

import { useState } from 'react';
import authService from '../services/authService';
import styles from '../styles/AuthModal.module.css';

export default function UnifiedAuthModal({ isOpen, onSuccess, onClose }) {
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!password.trim()) {
      setError('Please enter your master password');
      return;
    }

    setIsLoading(true);

    try {
      const { token } = await authService.authenticate(password);
      
      // Clear form
      setPassword('');
      setError('');
      
      // Notify parent
      onSuccess(token);
      
    } catch (error) {
      setError(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClose = () => {
    setPassword('');
    setError('');
    onClose();
  };

  return (
    <div className={styles.modalOverlay} onClick={handleClose}>
      <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
        <div className={styles.modalHeader}>
          <h2>Authentication Required</h2>
          <button 
            className={styles.closeButton} 
            onClick={handleClose}
            aria-label="Close"
          >
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.inputGroup}>
            <label htmlFor="password">Master Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your master password"
              autoFocus
              disabled={isLoading}
              className={styles.input}
            />
          </div>

          {error && (
            <div className={styles.error} role="alert">
              {error}
            </div>
          )}

          <div className={styles.actions}>
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
              className={styles.submitButton}
            >
              {isLoading ? 'Authenticating...' : 'Authenticate'}
            </button>
          </div>
        </form>

        <div className={styles.help}>
          <p>Enter your master password to access translation features.</p>
        </div>
      </div>
    </div>
  );
}