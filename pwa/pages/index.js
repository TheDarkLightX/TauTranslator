import { useState } from 'react';
import Link from 'next/link';
import styles from '../styles/Editor.module.css';
import UnifiedAuthModal from '../components/UnifiedAuthModal';
import BackendStatusChecker from '../components/BackendStatusChecker';
import { useTranslation } from '../hooks/useTranslation';
import { useAuth } from '../hooks/useAuth';

const outputFormats = {
  ILR: 'ILR (Intermediate Logic Representation)',
  CNL: 'CNL (Controlled Natural Language)',
  TAU: 'Tau Language Code',
};

const languageTypes = {
  PLAIN_ENGLISH: 'Plain English',
  ...outputFormats,
};

export default function EditorPage() {
  const [leftText, setLeftText] = useState('');
  const [rightText, setRightText] = useState('');
  const [leftLanguage, setLeftLanguage] = useState('PLAIN_ENGLISH');
  const [rightLanguage, setRightLanguage] = useState('TAU');
  const [showAuthModal, setShowAuthModal] = useState(false);

  // Use custom hooks
  const { isAuthenticated, logout } = useAuth();
  const { translate, isLoading, error, clearError } = useTranslation();

  const handleSwapLanguages = () => {
    // Swap languages
    const tempLang = leftLanguage;
    setLeftLanguage(rightLanguage);
    setRightLanguage(tempLang);
    
    // Swap text content
    const tempText = leftText;
    setLeftText(rightText);
    setRightText(tempText);
  };

  const handleTranslate = async () => {
    const result = await translate({
      sourceText: leftText,
      sourceLang: leftLanguage,
      targetLang: rightLanguage
    });

    if (result.success) {
      setRightText(result.translatedText);
    } else if (result.requiresAuth) {
      setShowAuthModal(true);
    }
  };
  
  const currentInputIsEmpty = () => {
    // Always check left panel since that's where user inputs
    return !leftText;
  };

  // Determine panel configurations based on language state
  const leftPanelLabel = languageTypes[leftLanguage];
  const rightPanelLabel = languageTypes[rightLanguage];

  return (
    <div className={styles.editorContainer}>
      <div className={styles.header}>
        <h1 className={styles.title}>Tau Language Translator</h1>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
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
        </div>
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
              <button onClick={() => setShowAuthModal(true)} className={styles.loginButton}>
                Login
              </button>
            </div>
          )}
        </div>
      </div>

      <div className={styles.controlsBar}>
        {/* Left Language Selector */} 
        <select 
          value={leftLanguage} 
          onChange={(e) => setLeftLanguage(e.target.value)} 
          className={styles.languageSelector}
          disabled={isLoading}
        >
          {Object.entries(languageTypes).map(([key, label]) => (
            <option key={key} value={key}>{label}</option>
          ))}
        </select>

        <button onClick={handleSwapLanguages} className={styles.swapButton} title="Swap Languages" disabled={isLoading}>
          &#x21C4; {/* Unicode for arrows left right */}
        </button>

        {/* Right Language Selector */} 
        <select 
          value={rightLanguage} 
          onChange={(e) => setRightLanguage(e.target.value)} 
          className={styles.languageSelector}
          disabled={isLoading}
        >
          {Object.entries(languageTypes).map(([key, label]) => (
            <option key={key} value={key}>{label}</option>
          ))}
        </select>

        <button 
          onClick={handleTranslate} 
          className={styles.translateButton} 
          disabled={isLoading || currentInputIsEmpty()}
        >
          {isLoading ? 'Translating...' : 'Translate'}
        </button>
      </div>

      <div className={styles.panelsContainer}>
        <div className={styles.editorPanel}>
          <div className={styles.panelHeader}>{leftPanelLabel}</div>
          <textarea 
            className={styles.textarea}
            value={leftText}
            onChange={(e) => setLeftText(e.target.value)}
            placeholder={`Enter ${leftPanelLabel} here...`}
            readOnly={isLoading} // Made editable, only readOnly during loading
            disabled={isLoading} // Overall disabled when loading
          />
        </div>
        <div className={styles.editorPanel}>
          <div className={styles.panelHeader}>{rightPanelLabel}</div>
          <textarea 
            className={styles.textarea}
            value={rightText}
            onChange={(e) => setRightText(e.target.value)}
            placeholder={`Enter ${rightPanelLabel} here...`}
            readOnly={isLoading} // Made editable, only readOnly during loading
            disabled={isLoading} // Overall disabled when loading
          />
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className={styles.errorBanner}>
          <span className={styles.errorText}>{error}</span>
          <button 
            className={styles.errorClose}
            onClick={clearError}
            aria-label="Close error"
          >
            ×
          </button>
        </div>
      )}

      {/* Authentication Modal */}
      <UnifiedAuthModal
        isOpen={showAuthModal}
        onSuccess={() => setShowAuthModal(false)}
        onClose={() => setShowAuthModal(false)}
      />

      {/* Backend Status Checker */}
      <BackendStatusChecker />
    </div>
  );
}
