/**
 * AutoComplete Textarea Component
 * ==============================
 * Following Intentional Disclosure Principle
 * 
 * Rule 1: Names reveal consequence and async operations
 * Rule 2: Public methods orchestrate, private methods implement
 * Rule 3: Types maximize disclosure
 * Rule 4: I/O isolated in service layer
 * 
 * Copyright: DarkLightX/Dana Edwards
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import styles from '../styles/Editor.module.css';

// Domain Types (Rule 3: Maximize Disclosure via Type System)
const SuggestionType = {
  KEYWORD: 'keyword',
  OPERATOR: 'operator',
  TEMPORAL: 'temporal',
  QUANTIFIER: 'quantifier',
  IDENTIFIER: 'identifier',
  CONTINUATION: 'continuation',
  COMPLETION: 'completion'
};

const AutoCompleteState = {
  IDLE: 'idle',
  FETCHING: 'fetching',
  SHOWING: 'showing',
  ERROR: 'error'
};

// Infrastructure Layer (Rule 4: Isolate Impurity)
class AutoCompleteSuggestionService {
  static async fetch_suggestions_from_api_async(text, position = null, context = null) {
    try {
      const response = await fetch('/api/translate-backend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          endpoint: '/autocomplete',
          data: { text, position, context }
        })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const result = await response.json();
      return result.success ? result.data : { suggestions: [], source: 'error' };
    } catch (error) {
      console.error('AutoComplete API error:', error);
      return { suggestions: [], source: 'error', error: error.message };
    }
  }
}

// Core Business Logic (Pure Functions)
class SuggestionMatcher {
  static filter_relevant_suggestions_by_prefix(suggestions, currentWord) {
    if (!currentWord) return suggestions;
    
    const prefix = currentWord.toLowerCase();
    return suggestions.filter(suggestion => 
      suggestion.text.toLowerCase().includes(prefix)
    );
  }
  
  static calculate_suggestion_position_from_cursor(textareaRef, cursorPosition) {
    if (!textareaRef.current) return { top: 0, left: 0 };
    
    const textarea = textareaRef.current;
    const { scrollTop, scrollLeft } = textarea;
    
    // Create temporary element to measure text
    const temp = document.createElement('div');
    const computedStyle = window.getComputedStyle(textarea);
    
    temp.style.position = 'absolute';
    temp.style.visibility = 'hidden';
    temp.style.font = computedStyle.font;
    temp.style.padding = computedStyle.padding;
    temp.style.border = computedStyle.border;
    temp.style.whiteSpace = 'pre-wrap';
    temp.style.wordWrap = 'break-word';
    temp.style.width = textarea.clientWidth + 'px';
    
    const textBeforeCursor = textarea.value.substring(0, cursorPosition);
    temp.textContent = textBeforeCursor;
    
    document.body.appendChild(temp);
    
    const rect = textarea.getBoundingClientRect();
    const tempRect = temp.getBoundingClientRect();
    
    document.body.removeChild(temp);
    
    return {
      top: rect.top + tempRect.height - scrollTop + 20,
      left: rect.left + (tempRect.width % textarea.clientWidth) - scrollLeft
    };
  }
  
  static extract_current_word_at_cursor(text, cursorPosition) {
    const beforeCursor = text.substring(0, cursorPosition);
    const afterCursor = text.substring(cursorPosition);
    
    const wordBoundary = /[\s,()[\]{}]/;
    
    let wordStart = cursorPosition;
    while (wordStart > 0 && !wordBoundary.test(beforeCursor[wordStart - 1])) {
      wordStart--;
    }
    
    let wordEnd = cursorPosition;
    while (wordEnd < text.length && !wordBoundary.test(afterCursor[wordEnd - cursorPosition])) {
      wordEnd++;
    }
    
    return {
      word: text.substring(wordStart, wordEnd),
      start: wordStart,
      end: wordEnd
    };
  }
}

// Component (Rule 2: Orchestrator Methods)
export default function AutoCompleteTextarea({
  label,
  value,
  onChange,
  placeholder,
  readOnly = false,
  disabled = false,
  enableAutoComplete = true
}) {
  // State Management
  const [suggestions, setSuggestions] = useState([]);
  const [autoCompleteState, setAutoCompleteState] = useState(AutoCompleteState.IDLE);
  const [selectedSuggestionIndex, setSelectedSuggestionIndex] = useState(0);
  const [suggestionPosition, setSuggestionPosition] = useState({ top: 0, left: 0 });
  const [currentWord, setCurrentWord] = useState({ word: '', start: 0, end: 0 });
  
  const textareaRef = useRef(null);
  const suggestionTimeoutRef = useRef(null);
  
  // Rule 2: Public orchestrator method
  const handle_text_change_with_autocomplete = useCallback(async (newValue) => {
    onChange(newValue);
    
    if (!enableAutoComplete || readOnly || disabled) {
      _hide_suggestions();
      return;
    }
    
    const cursorPosition = textareaRef.current?.selectionStart || 0;
    const wordInfo = SuggestionMatcher.extract_current_word_at_cursor(newValue, cursorPosition);
    
    setCurrentWord(wordInfo);
    
    if (wordInfo.word.length >= 1) {
      await _fetch_and_show_suggestions_async(newValue, cursorPosition, wordInfo);
    } else {
      _hide_suggestions();
    }
  }, [onChange, enableAutoComplete, readOnly, disabled]);
  
  // Rule 2: Public orchestrator method
  const handle_key_navigation_in_suggestions = useCallback((event) => {
    if (autoCompleteState !== AutoCompleteState.SHOWING || suggestions.length === 0) {
      return;
    }
    
    switch (event.key) {
      case 'ArrowDown':
        event.preventDefault();
        _move_selection_down();
        break;
      case 'ArrowUp':
        event.preventDefault();
        _move_selection_up();
        break;
      case 'Tab':
      case 'Enter':
        event.preventDefault();
        _apply_selected_suggestion();
        break;
      case 'Escape':
        event.preventDefault();
        _hide_suggestions();
        break;
    }
  }, [autoCompleteState, suggestions, selectedSuggestionIndex, currentWord, value]);
  
  // Rule 2: Public orchestrator method
  const handle_suggestion_click_selection = useCallback((suggestionIndex) => {
    setSelectedSuggestionIndex(suggestionIndex);
    _apply_selected_suggestion();
  }, [suggestions, currentWord, value]);
  
  // Private Implementation Methods (Rule 2)
  const _fetch_and_show_suggestions_async = async (text, cursorPosition, wordInfo) => {
    // Clear existing timeout
    if (suggestionTimeoutRef.current) {
      clearTimeout(suggestionTimeoutRef.current);
    }
    
    // Debounce suggestions
    suggestionTimeoutRef.current = setTimeout(async () => {
      setAutoCompleteState(AutoCompleteState.FETCHING);
      
      const result = await AutoCompleteSuggestionService.fetch_suggestions_from_api_async(
        text, cursorPosition, wordInfo.word
      );
      
      if (result.suggestions && result.suggestions.length > 0) {
        const filteredSuggestions = SuggestionMatcher.filter_relevant_suggestions_by_prefix(
          result.suggestions, wordInfo.word
        );
        
        setSuggestions(filteredSuggestions);
        setSelectedSuggestionIndex(0);
        
        const position = SuggestionMatcher.calculate_suggestion_position_from_cursor(
          textareaRef, cursorPosition
        );
        setSuggestionPosition(position);
        
        setAutoCompleteState(AutoCompleteState.SHOWING);
      } else {
        _hide_suggestions();
      }
    }, 300); // 300ms debounce
  };
  
  const _hide_suggestions = () => {
    setSuggestions([]);
    setAutoCompleteState(AutoCompleteState.IDLE);
    setSelectedSuggestionIndex(0);
  };
  
  const _move_selection_down = () => {
    setSelectedSuggestionIndex(prev => 
      prev < suggestions.length - 1 ? prev + 1 : 0
    );
  };
  
  const _move_selection_up = () => {
    setSelectedSuggestionIndex(prev => 
      prev > 0 ? prev - 1 : suggestions.length - 1
    );
  };
  
  const _apply_selected_suggestion = () => {
    if (suggestions.length === 0) return;
    
    const selectedSuggestion = suggestions[selectedSuggestionIndex];
    if (!selectedSuggestion) return;
    
    const beforeWord = value.substring(0, currentWord.start);
    const afterWord = value.substring(currentWord.end);
    const newValue = beforeWord + selectedSuggestion.text + afterWord;
    
    onChange(newValue);
    _hide_suggestions();
    
    // Set cursor position after suggestion
    setTimeout(() => {
      if (textareaRef.current) {
        const newCursorPos = currentWord.start + selectedSuggestion.text.length;
        textareaRef.current.selectionStart = newCursorPos;
        textareaRef.current.selectionEnd = newCursorPos;
        textareaRef.current.focus();
      }
    }, 0);
  };
  
  // Cleanup effect
  useEffect(() => {
    return () => {
      if (suggestionTimeoutRef.current) {
        clearTimeout(suggestionTimeoutRef.current);
      }
    };
  }, []);
  
  return (
    <div className={styles.editorPanel}>
      <div className={styles.panelHeader}>{label}</div>
      <div style={{ position: 'relative' }}>
        <textarea 
          ref={textareaRef}
          className={styles.textarea}
          value={value}
          onChange={(e) => handle_text_change_with_autocomplete(e.target.value)}
          onKeyDown={handle_key_navigation_in_suggestions}
          placeholder={placeholder || `Enter ${label} here...`}
          readOnly={readOnly || disabled}
          disabled={disabled}
        />
        
        {/* Suggestion Dropdown */}
        {autoCompleteState === AutoCompleteState.SHOWING && suggestions.length > 0 && (
          <div 
            className={styles.suggestionDropdown}
            style={{
              position: 'fixed',
              top: suggestionPosition.top,
              left: suggestionPosition.left,
              zIndex: 1000
            }}
          >
            {suggestions.map((suggestion, index) => (
              <div
                key={index}
                className={`${styles.suggestionItem} ${
                  index === selectedSuggestionIndex ? styles.suggestionSelected : ''
                }`}
                onClick={() => handle_suggestion_click_selection(index)}
                onMouseEnter={() => setSelectedSuggestionIndex(index)}
              >
                <div className={styles.suggestionText}>{suggestion.text}</div>
                <div className={styles.suggestionType}>{suggestion.type}</div>
                {suggestion.description && (
                  <div className={styles.suggestionDescription}>{suggestion.description}</div>
                )}
              </div>
            ))}
          </div>
        )}
        
        {/* Loading Indicator */}
        {autoCompleteState === AutoCompleteState.FETCHING && (
          <div className={styles.loadingIndicator}>
            Fetching suggestions...
          </div>
        )}
      </div>
    </div>
  );
}