/**
 * Translation Store
 * ================
 * Global state management for translation features
 * 
 * Author: DarkLightX/Dana Edwards
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import translationService from '../services/translationService';
import authService from '../services/authService';

const useTranslationStore = create(
  persist(
    (set, get) => ({
      // Editor State
      leftText: '',
      rightText: '',
      leftLanguage: 'PLAIN_ENGLISH',
      rightLanguage: 'TAU',
      
      // UI State
      isLoading: false,
      error: null,
      
      // Translation History
      history: [],
      maxHistorySize: 50,
      
      // Actions
      setLeftText: (text) => set({ leftText: text }),
      setRightText: (text) => set({ rightText: text }),
      setLeftLanguage: (lang) => set({ leftLanguage: lang }),
      setRightLanguage: (lang) => set({ rightLanguage: lang }),
      setError: (error) => set({ error }),
      clearError: () => set({ error: null }),
      
      // Swap languages and text
      swapLanguages: () => {
        const state = get();
        set({
          leftLanguage: state.rightLanguage,
          rightLanguage: state.leftLanguage,
          leftText: state.rightText,
          rightText: state.leftText
        });
      },
      
      // Main translation function
      translate: async (options = {}) => {
        const state = get();
        const { leftText, leftLanguage, rightLanguage } = state;
        
        if (!leftText.trim()) {
          set({ error: 'Please enter text to translate' });
          return { success: false };
        }
        
        set({ isLoading: true, error: null });
        
        try {
          const result = await translationService.translate({
            sourceText: leftText,
            sourceLang: leftLanguage,
            targetLang: rightLanguage,
            options: {
              ...options,
              apiKey: authService.getToken()
            }
          });
          
          // Update state
          set({ 
            rightText: result.translatedText,
            isLoading: false
          });
          
          // Add to history
          get().addToHistory({
            sourceText: leftText,
            sourceLang: leftLanguage,
            targetLang: rightLanguage,
            translatedText: result.translatedText,
            provider: result.provider,
            timestamp: new Date().toISOString()
          });
          
          return { success: true, ...result };
          
        } catch (error) {
          set({ 
            error: error.message,
            isLoading: false
          });
          
          // Check if auth required
          if (error.message.includes('Authentication')) {
            return { success: false, requiresAuth: true };
          }
          
          return { success: false, error: error.message };
        }
      },
      
      // History management
      addToHistory: (entry) => {
        const state = get();
        const newHistory = [entry, ...state.history].slice(0, state.maxHistorySize);
        set({ history: newHistory });
      },
      
      clearHistory: () => set({ history: [] }),
      
      // Load from history
      loadFromHistory: (index) => {
        const state = get();
        const entry = state.history[index];
        if (entry) {
          set({
            leftText: entry.sourceText,
            rightText: entry.translatedText,
            leftLanguage: entry.sourceLang,
            rightLanguage: entry.targetLang
          });
        }
      }
    }),
    {
      name: 'translation-storage',
      partialize: (state) => ({
        leftLanguage: state.leftLanguage,
        rightLanguage: state.rightLanguage,
        history: state.history
      })
    }
  )
);

export default useTranslationStore;