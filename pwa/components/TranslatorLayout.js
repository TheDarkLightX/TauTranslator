/**
 * Translator Layout Component
 * ==========================
 * Common layout for translator pages
 * 
 * Author: DarkLightX/Dana Edwards
 */

import Link from 'next/link';
import styles from '../styles/Editor.module.css';
import { useAuth } from '../hooks/useAuth';

export default function TranslatorLayout({ 
  children, 
  title = 'Tau Language Translator',
  showSettings = true,
  showAuth = true 
}) {
  const { isAuthenticated, logout } = useAuth();

  return (
    <div className={styles.editorContainer}>
      <div className={styles.header}>
        <h1 className={styles.title}>{title}</h1>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          {showSettings && (
            <Link href="/settings">
              <button style={{
                padding: '8px 12px',
                border: '1px solid #6c757d',
                background: '#6c757d',
                color: 'white',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '14px'
              }}>
                ⚙️ Settings
              </button>
            </Link>
          )}
        </div>

        {showAuth && (
          <div className={styles.authStatus}>
            {isAuthenticated ? (
              <div className={styles.authenticatedStatus}>
                <span className={styles.authIndicator}>🔓 Authenticated</span>
                <button onClick={logout} className={styles.logoutButton}>
                  Logout
                </button>
              </div>
            ) : (
              <div className={styles.unauthenticatedStatus}>
                <span className={styles.authIndicator}>🔒 Not Authenticated</span>
              </div>
            )}
          </div>
        )}
      </div>

      {children}
    </div>
  );
}