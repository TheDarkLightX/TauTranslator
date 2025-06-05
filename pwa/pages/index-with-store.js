/**
 * Editor Page with Global State
 * ============================
 * Uses Zustand for state management
 * 
 * Author: DarkLightX/Dana Edwards
 */

import { useState } from 'react';
import styles from '../styles/Editor.module.css';
import TranslatorLayout from '../components/TranslatorLayout';
import TranslationPanel from '../components/TranslationPanel';
import LanguageSelector, { LANGUAGE_OPTIONS } from '../components/LanguageSelector';
import UnifiedAuthModal from '../components/UnifiedAuthModal';
import BackendStatusChecker from '../components/BackendStatusChecker';
import useTranslationStore from '../store/translationStore';

export default function EditorWithStore() {
  const [showAuthModal, setShowAuthModal] = useState(false);
  
  // Get state and actions from store
  const {
    leftText,
    rightText,
    leftLanguage,
    rightLanguage,
    isLoading,
    error,
    setLeftText,
    setRightText,
    setLeftLanguage,
    setRightLanguage,
    swapLanguages,
    translate,
    clearError
  } = useTranslationStore();

  const handleTranslate = async () => {
    const result = await translate();
    if (result.requiresAuth) {
      setShowAuthModal(true);
    }
  };

  const canTranslate = leftText.trim() && !isLoading;

  return (
    <TranslatorLayout>
      {/* Controls Bar */}
      <div className={styles.controlsBar}>
        <LanguageSelector 
          value={leftLanguage} 
          onChange={setLeftLanguage} 
          disabled={isLoading}
        />

        <button 
          onClick={swapLanguages} 
          className={styles.swapButton} 
          title="Swap Languages" 
          disabled={isLoading}
        >
          ↔
        </button>

        <LanguageSelector 
          value={rightLanguage} 
          onChange={setRightLanguage} 
          disabled={isLoading}
        />

        <button 
          onClick={handleTranslate} 
          className={styles.translateButton} 
          disabled={!canTranslate}
        >
          {isLoading ? 'Translating...' : 'Translate'}
        </button>
      </div>

      {/* Translation Panels */}
      <div className={styles.panelsContainer}>
        <TranslationPanel
          label={LANGUAGE_OPTIONS[leftLanguage]}
          value={leftText}
          onChange={setLeftText}
          disabled={isLoading}
        />
        
        <TranslationPanel
          label={LANGUAGE_OPTIONS[rightLanguage]}
          value={rightText}
          onChange={setRightText}
          disabled={isLoading}
        />
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

      {/* Auth Modal */}
      <UnifiedAuthModal
        isOpen={showAuthModal}
        onSuccess={() => setShowAuthModal(false)}
        onClose={() => setShowAuthModal(false)}
      />

      {/* Backend Status */}
      <BackendStatusChecker />
    </TranslatorLayout>
  );
}