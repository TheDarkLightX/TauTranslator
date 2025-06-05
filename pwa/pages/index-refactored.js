/**
 * Refactored Editor Page
 * =====================
 * Cleaner implementation using modular components
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
import { useTranslation } from '../hooks/useTranslation';
import { useAuth } from '../hooks/useAuth';

export default function RefactoredEditorPage() {
  // State
  const [leftText, setLeftText] = useState('');
  const [rightText, setRightText] = useState('');
  const [leftLanguage, setLeftLanguage] = useState('PLAIN_ENGLISH');
  const [rightLanguage, setRightLanguage] = useState('TAU');
  const [showAuthModal, setShowAuthModal] = useState(false);

  // Hooks
  const { isAuthenticated } = useAuth();
  const { translate, isLoading, error, clearError } = useTranslation();

  // Handlers
  const handleSwapLanguages = () => {
    setLeftLanguage(rightLanguage);
    setRightLanguage(leftLanguage);
    setLeftText(rightText);
    setRightText(leftText);
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
          onClick={handleSwapLanguages} 
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