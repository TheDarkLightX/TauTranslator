import { useState, useEffect } from 'react';
import styles from '../styles/Editor.module.css';
import AuthenticationModal from '../components/AuthenticationModal';
import SimpleAuthModal from '../components/SimpleAuthModal';
import BackendStatusChecker from '../components/BackendStatusChecker';

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
  const [leftIsPlainEnglish, setLeftIsPlainEnglish] = useState(true);
  const [machineFormat, setMachineFormat] = useState('ILR'); // Default machine format
  const [isLoading, setIsLoading] = useState(false);

  // Authentication state
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [sessionToken, setSessionToken] = useState(null);
  const [showAuthModal, setShowAuthModal] = useState(false);

  // Check for existing authentication on component mount
  useEffect(() => {
    const storedToken = localStorage.getItem('sessionToken');
    const storedAuth = localStorage.getItem('authenticated');

    if (storedToken && storedAuth === 'true') {
      setSessionToken(storedToken);
      setIsAuthenticated(true);
    }
  }, []);

  const handleAuthenticate = (token) => {
    setSessionToken(token);
    setIsAuthenticated(true);
    setShowAuthModal(false);
  };

  const handleLogout = () => {
    localStorage.removeItem('sessionToken');
    localStorage.removeItem('authenticated');
    setSessionToken(null);
    setIsAuthenticated(false);
  };

  const handleSwapLanguages = () => {
    setLeftIsPlainEnglish(prev => !prev);
    setLeftText(rightText); // Swap text content
    setRightText(leftText);
  };

  const handleTranslate = async () => {
    // Check if authentication is required for backend features
    if (!isAuthenticated) {
      setShowAuthModal(true);
      return;
    }

    setIsLoading(true);

    const currentSourceText = leftIsPlainEnglish ? leftText : rightText;
    const currentSourceLangKey = leftIsPlainEnglish ? 'PLAIN_ENGLISH' : machineFormat;
    const currentTargetLangKey = leftIsPlainEnglish ? machineFormat : 'PLAIN_ENGLISH';

    const sourceLangLabel = languageTypes[currentSourceLangKey];
    const targetLangLabel = languageTypes[currentTargetLangKey];

    try {
      const headers = {
        'Content-Type': 'application/json',
      };

      // Add authorization header if we have a session token
      if (sessionToken) {
        headers['Authorization'] = `Bearer ${sessionToken}`;
      }

      const response = await fetch('/api/translate', {
        method: 'POST',
        headers,
        body: JSON.stringify({
          sourceText: currentSourceText,
          sourceLangKey: currentSourceLangKey,
          targetLangKey: currentTargetLangKey,
          sourceLangLabel, // Sending labels for API's mock logic, not strictly needed by real backend
          targetLangLabel  // Same as above
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();

        // Handle authentication errors
        if (response.status === 401) {
          handleLogout(); // Clear invalid session
          setShowAuthModal(true);
          throw new Error('Authentication expired. Please log in again.');
        }

        throw new Error(errorData.message || `API Error: ${response.status}`);
      }

      const data = await response.json();
      const { translatedText } = data;

      if (leftIsPlainEnglish) {
        setRightText(translatedText);
      } else {
        setLeftText(translatedText);
      }
    } catch (error) {
      console.error('Translation API call failed:', error);

      // Handle authentication-related errors
      if (error.message.includes('authenticate') || error.message.includes('Authentication')) {
        setShowAuthModal(true);
      }

      // Display error message to the user
      const errorMessage = `Error: ${error.message}`;
      if (leftIsPlainEnglish) {
        setRightText(errorMessage);
      } else {
        setLeftText(errorMessage);
      }
    }
    setIsLoading(false);
  };
  
  const currentInputIsEmpty = () => {
    if (leftIsPlainEnglish) return !leftText;
    return !rightText;
  };

  // Determine panel configurations based on leftIsPlainEnglish state
  const leftPanelLangKey = leftIsPlainEnglish ? 'PLAIN_ENGLISH' : machineFormat;
  const rightPanelLangKey = leftIsPlainEnglish ? machineFormat : 'PLAIN_ENGLISH';

  const leftPanelLabel = languageTypes[leftPanelLangKey];
  const rightPanelLabel = languageTypes[rightPanelLangKey];

  return (
    <div className={styles.editorContainer}>
      <div className={styles.header}>
        <h1 className={styles.title}>Tau Language Translator</h1>
        <div className={styles.authStatus}>
          {isAuthenticated ? (
            <div className={styles.authenticatedStatus}>
              <span className={styles.authIndicator}>🔓 Authenticated</span>
              <button onClick={handleLogout} className={styles.logoutButton}>
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
        {/* Left Language Display - Always Plain English */} 
        <div className={styles.languageDisplay}>{languageTypes.PLAIN_ENGLISH}</div>

        <button onClick={handleSwapLanguages} className={styles.swapButton} title="Swap Languages" disabled={isLoading}>
          &#x21C4; {/* Unicode for arrows left right */}
        </button>

        {/* Right Language Selector - Always Machine Formats */} 
        <select 
          value={machineFormat} 
          onChange={(e) => setMachineFormat(e.target.value)} 
          className={styles.languageSelector}
          disabled={isLoading}
        >
          {Object.entries(outputFormats).map(([key, label]) => (
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

      {/* Authentication Modal - Using Simple Version for Testing */}
      <SimpleAuthModal
        isOpen={showAuthModal}
        onAuthenticate={handleAuthenticate}
        onClose={() => setShowAuthModal(false)}
      />

      {/* Backend Status Checker */}
      <BackendStatusChecker />
    </div>
  );
}
