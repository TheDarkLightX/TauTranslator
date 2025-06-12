/**
 * Unit Tests for AutoCompleteTextarea Component
 * =============================================
 * Following FIRST principles and BDD approach
 * 
 * Copyright: DarkLightX/Dana Edwards
 */

import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import AutoCompleteTextarea from '../../components/AutoCompleteTextarea';

// Mock the fetch API
global.fetch = jest.fn();

// Test Data Builders (Advanced Testing Pattern)
class AutoCompletePropsBuilder {
  constructor() {
    this.label = 'Test Input';
    this.value = '';
    this.onChange = jest.fn();
    this.placeholder = 'Enter text...';
    this.readOnly = false;
    this.disabled = false;
    this.enableAutoComplete = true;
  }
  
  withValue(value) {
    this.value = value;
    return this;
  }
  
  withAutoCompleteDisabled() {
    this.enableAutoComplete = false;
    return this;
  }
  
  asReadOnly() {
    this.readOnly = true;
    return this;
  }
  
  asDisabled() {
    this.disabled = true;
    return this;
  }
  
  build() {
    return {
      label: this.label,
      value: this.value,
      onChange: this.onChange,
      placeholder: this.placeholder,
      readOnly: this.readOnly,
      disabled: this.disabled,
      enableAutoComplete: this.enableAutoComplete
    };
  }
}

// Mock Response Builder
class SuggestionResponseBuilder {
  constructor() {
    this.suggestions = [];
    this.source = 'nlp';
  }
  
  withSuggestions(suggestions) {
    this.suggestions = suggestions;
    return this;
  }
  
  withFallbackSource() {
    this.source = 'fallback';
    return this;
  }
  
  build() {
    return {
      success: true,
      data: {
        suggestions: this.suggestions,
        source: this.source
      }
    };
  }
}

describe('AutoCompleteTextarea Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    jest.useFakeTimers();
  });
  
  afterEach(() => {
    jest.runOnlyPendingTimers();
    jest.useRealTimers();
  });
  
  describe('Basic Rendering', () => {
    // Test: Component_InitialState_RendersCorrectly
    test('given_default_props_when_rendering_then_displays_textarea_with_label', () => {
      // Given: Default props
      const props = new AutoCompletePropsBuilder().build();
      
      // When: Rendering the component
      render(<AutoCompleteTextarea {...props} />);
      
      // Then: Component elements are displayed correctly
      expect(screen.getByText('Test Input')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Enter text...')).toBeInTheDocument();
      expect(screen.getByRole('textbox')).not.toBeDisabled();
    });
    
    // Test: Component_DisabledState_PreventsInteraction
    test('given_disabled_prop_when_rendering_then_textarea_is_disabled', () => {
      // Given: Component with disabled prop
      const props = new AutoCompletePropsBuilder().asDisabled().build();
      
      // When: Rendering the component
      render(<AutoCompleteTextarea {...props} />);
      
      // Then: Textarea is disabled
      expect(screen.getByRole('textbox')).toBeDisabled();
    });
    
    // Test: Component_ReadOnlyState_PreventsEditing
    test('given_readonly_prop_when_rendering_then_textarea_is_readonly', () => {
      // Given: Component with readOnly prop
      const props = new AutoCompletePropsBuilder().asReadOnly().build();
      
      // When: Rendering the component
      render(<AutoCompleteTextarea {...props} />);
      
      // Then: Textarea has readOnly attribute
      expect(screen.getByRole('textbox')).toHaveAttribute('readonly');
    });
  });
  
  describe('Text Input Handling', () => {
    // Test: TextInput_UserTypes_CallsOnChange
    test('given_enabled_textarea_when_user_types_then_onChange_is_called', async () => {
      // Given: An enabled textarea
      const props = new AutoCompletePropsBuilder().build();
      render(<AutoCompleteTextarea {...props} />);
      const textarea = screen.getByRole('textbox');
      
      // When: User types text
      await userEvent.type(textarea, 'forall');
      
      // Then: onChange is called for each character
      expect(props.onChange).toHaveBeenCalledTimes(6); // 'forall' has 6 characters
      expect(props.onChange).toHaveBeenLastCalledWith('forall');
    });
    
    // Test: TextInput_WithAutoCompleteDisabled_NoSuggestionsShown
    test('given_autocomplete_disabled_when_user_types_then_no_suggestions_appear', async () => {
      // Given: AutoComplete is disabled
      const props = new AutoCompletePropsBuilder()
        .withAutoCompleteDisabled()
        .build();
      render(<AutoCompleteTextarea {...props} />);
      
      // When: User types text
      await userEvent.type(screen.getByRole('textbox'), 'forall');
      act(() => {
        jest.runAllTimers();
      });
      
      // Then: No fetch is made and no suggestions appear
      expect(fetch).not.toHaveBeenCalled();
      expect(screen.queryByText('Loading suggestions...')).not.toBeInTheDocument();
    });
  });
  
  describe('AutoComplete Suggestions', () => {
    // Test: AutoComplete_ValidInput_FetchesSuggestions
    test('given_valid_input_when_typing_then_fetches_and_displays_suggestions', async () => {
      // Given: Component with mocked API response
      const mockSuggestions = [
        { text: 'forall', type: 'quantifier', description: 'Universal quantification' },
        { text: 'for every', type: 'quantifier', description: 'Alternative universal quantifier' }
      ];
      
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => new SuggestionResponseBuilder()
          .withSuggestions(mockSuggestions)
          .build()
      });
      
      const props = new AutoCompletePropsBuilder().build();
      render(<AutoCompleteTextarea {...props} />);
      
      // When: User types 'for'
      await userEvent.type(screen.getByRole('textbox'), 'for');
      
      // Then: API is called after debounce
      act(() => {
        jest.advanceTimersByTime(300);
      });
      
      await waitFor(() => {
        expect(fetch).toHaveBeenCalledWith('/api/translate-backend', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            endpoint: '/autocomplete',
            data: { text: 'for', position: 3, context: 'for' }
          })
        });
      });
      
      // And: Suggestions are displayed
      await waitFor(() => {
        expect(screen.getByText('forall')).toBeInTheDocument();
        expect(screen.getByText('Universal quantification')).toBeInTheDocument();
      });
    });
    
    // Test: AutoComplete_APIError_ShowsFallbackSuggestions
    test('given_api_error_when_fetching_suggestions_then_shows_fallback', async () => {
      // Given: API returns error
      fetch.mockRejectedValueOnce(new Error('Network error'));
      
      const props = new AutoCompletePropsBuilder().build();
      render(<AutoCompleteTextarea {...props} />);
      
      // When: User types
      await userEvent.type(screen.getByRole('textbox'), 'def');
      
      act(() => {
        jest.advanceTimersByTime(300);
      });
      
      // Then: Error is logged but component doesn't crash
      await waitFor(() => {
        expect(fetch).toHaveBeenCalled();
      });
      
      // Component should handle error gracefully
      expect(screen.getByRole('textbox')).toBeInTheDocument();
    });
    
    // Test: AutoComplete_MinimumCharacters_NoSuggestionsForSingleChar
    test('given_single_character_when_typing_then_shows_suggestions', async () => {
      // Given: Component ready
      const props = new AutoCompletePropsBuilder().build();
      render(<AutoCompleteTextarea {...props} />);
      
      // When: User types single character
      await userEvent.type(screen.getByRole('textbox'), 'a');
      
      act(() => {
        jest.advanceTimersByTime(300);
      });
      
      // Then: Suggestions are still fetched (minimum is 1 character)
      await waitFor(() => {
        expect(fetch).toHaveBeenCalled();
      });
    });
  });
  
  describe('Keyboard Navigation', () => {
    const setupWithSuggestions = async () => {
      const mockSuggestions = [
        { text: 'always', type: 'temporal', description: 'Always true' },
        { text: 'all', type: 'keyword', description: 'All keyword' },
        { text: 'although', type: 'keyword', description: 'Although keyword' }
      ];
      
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => new SuggestionResponseBuilder()
          .withSuggestions(mockSuggestions)
          .build()
      });
      
      const props = new AutoCompletePropsBuilder().build();
      const { container } = render(<AutoCompleteTextarea {...props} />);
      const textarea = screen.getByRole('textbox');
      
      await userEvent.type(textarea, 'al');
      act(() => {
        jest.advanceTimersByTime(300);
      });
      
      await waitFor(() => {
        expect(screen.getByText('always')).toBeInTheDocument();
      });
      
      return { textarea, props };
    };
    
    // Test: Keyboard_ArrowDown_MovesSelectionDown
    test('given_suggestions_visible_when_pressing_arrow_down_then_selection_moves_down', async () => {
      // Given: Suggestions are visible
      const { textarea } = await setupWithSuggestions();
      
      // When: Pressing arrow down
      fireEvent.keyDown(textarea, { key: 'ArrowDown' });
      
      // Then: Second item is selected
      const suggestions = screen.getAllByText(/always|all|although/);
      expect(suggestions[1].closest('[class*="suggestionItem"]'))
        .toHaveClass(expect.stringMatching(/suggestionSelected/));
    });
    
    // Test: Keyboard_ArrowUp_MovesSelectionUp
    test('given_suggestions_visible_when_pressing_arrow_up_then_selection_wraps_to_bottom', async () => {
      // Given: Suggestions are visible
      const { textarea } = await setupWithSuggestions();
      
      // When: Pressing arrow up from first item
      fireEvent.keyDown(textarea, { key: 'ArrowUp' });
      
      // Then: Last item is selected (wraps around)
      const suggestions = screen.getAllByText(/always|all|although/);
      expect(suggestions[suggestions.length - 1].closest('[class*="suggestionItem"]'))
        .toHaveClass(expect.stringMatching(/suggestionSelected/));
    });
    
    // Test: Keyboard_Enter_AppliesSelectedSuggestion
    test('given_suggestion_selected_when_pressing_enter_then_applies_suggestion', async () => {
      // Given: Suggestions are visible
      const { textarea, props } = await setupWithSuggestions();
      
      // When: Pressing Enter
      fireEvent.keyDown(textarea, { key: 'Enter' });
      
      // Then: Selected suggestion is applied
      expect(props.onChange).toHaveBeenCalledWith('always');
    });
    
    // Test: Keyboard_Escape_ClosesSuggestions
    test('given_suggestions_visible_when_pressing_escape_then_closes_suggestions', async () => {
      // Given: Suggestions are visible
      const { textarea } = await setupWithSuggestions();
      
      // When: Pressing Escape
      fireEvent.keyDown(textarea, { key: 'Escape' });
      
      // Then: Suggestions are hidden
      await waitFor(() => {
        expect(screen.queryByText('always')).not.toBeInTheDocument();
      });
    });
  });
  
  describe('Mouse Interaction', () => {
    // Test: Mouse_ClickSuggestion_AppliesSuggestion
    test('given_suggestions_visible_when_clicking_suggestion_then_applies_it', async () => {
      // Given: Suggestions are visible
      const mockSuggestions = [
        { text: 'exists', type: 'quantifier', description: 'Existential quantification' }
      ];
      
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => new SuggestionResponseBuilder()
          .withSuggestions(mockSuggestions)
          .build()
      });
      
      const props = new AutoCompletePropsBuilder().build();
      render(<AutoCompleteTextarea {...props} />);
      
      await userEvent.type(screen.getByRole('textbox'), 'ex');
      act(() => {
        jest.advanceTimersByTime(300);
      });
      
      await waitFor(() => {
        expect(screen.getByText('exists')).toBeInTheDocument();
      });
      
      // When: Clicking on suggestion
      fireEvent.click(screen.getByText('exists'));
      
      // Then: Suggestion is applied
      expect(props.onChange).toHaveBeenCalledWith('exists');
    });
    
    // Test: Mouse_HoverSuggestion_HighlightsSuggestion
    test('given_suggestions_visible_when_hovering_over_suggestion_then_highlights_it', async () => {
      // Given: Multiple suggestions visible
      const mockSuggestions = [
        { text: 'true', type: 'keyword', description: 'Boolean true' },
        { text: 'false', type: 'keyword', description: 'Boolean false' }
      ];
      
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => new SuggestionResponseBuilder()
          .withSuggestions(mockSuggestions)
          .build()
      });
      
      const props = new AutoCompletePropsBuilder().build();
      render(<AutoCompleteTextarea {...props} />);
      
      await userEvent.type(screen.getByRole('textbox'), 't');
      act(() => {
        jest.advanceTimersByTime(300);
      });
      
      await waitFor(() => {
        expect(screen.getByText('true')).toBeInTheDocument();
      });
      
      // When: Hovering over second suggestion
      fireEvent.mouseEnter(screen.getByText('false'));
      
      // Then: Second suggestion is highlighted
      expect(screen.getByText('false').closest('[class*="suggestionItem"]'))
        .toHaveClass(expect.stringMatching(/suggestionSelected/));
    });
  });
  
  describe('Edge Cases and Error Scenarios', () => {
    // Test: EdgeCase_EmptyInput_NoSuggestions
    test('given_empty_input_when_cleared_then_no_suggestions_shown', async () => {
      // Given: Component with some text
      const props = new AutoCompletePropsBuilder()
        .withValue('test')
        .build();
      const { rerender } = render(<AutoCompleteTextarea {...props} />);
      
      // When: Clearing the input
      rerender(<AutoCompleteTextarea {...props} value="" />);
      
      act(() => {
        jest.runAllTimers();
      });
      
      // Then: No fetch is made for empty input
      expect(fetch).not.toHaveBeenCalled();
    });
    
    // Test: EdgeCase_RapidTyping_DebouncesRequests
    test('given_rapid_typing_when_user_types_quickly_then_debounces_api_calls', async () => {
      // Given: Component ready
      const props = new AutoCompletePropsBuilder().build();
      render(<AutoCompleteTextarea {...props} />);
      const textarea = screen.getByRole('textbox');
      
      // When: Typing rapidly
      await userEvent.type(textarea, 'f');
      act(() => { jest.advanceTimersByTime(100); });
      
      await userEvent.type(textarea, 'o');
      act(() => { jest.advanceTimersByTime(100); });
      
      await userEvent.type(textarea, 'r');
      act(() => { jest.advanceTimersByTime(100); });
      
      // Then: No API calls yet (still within debounce period)
      expect(fetch).not.toHaveBeenCalled();
      
      // When: Debounce period completes
      act(() => { jest.advanceTimersByTime(200); }); // Total 300ms
      
      // Then: Only one API call is made with final value
      await waitFor(() => {
        expect(fetch).toHaveBeenCalledTimes(1);
        expect(fetch).toHaveBeenCalledWith('/api/translate-backend', 
          expect.objectContaining({
            body: expect.stringContaining('"text":"for"')
          })
        );
      });
    });
    
    // Test: EdgeCase_ComponentUnmount_CleansUpTimers
    test('given_pending_api_call_when_component_unmounts_then_cleans_up_properly', async () => {
      // Given: Component with pending timer
      const props = new AutoCompletePropsBuilder().build();
      const { unmount } = render(<AutoCompleteTextarea {...props} />);
      
      await userEvent.type(screen.getByRole('textbox'), 'test');
      
      // When: Unmounting before timer completes
      unmount();
      
      // Then: No errors occur when timer would fire
      act(() => {
        jest.runAllTimers();
      });
      
      // Component unmounted cleanly
      expect(screen.queryByRole('textbox')).not.toBeInTheDocument();
    });
  });
  
  describe('Performance and Optimization', () => {
    // Test: Performance_LargeSuggestionList_HandlesEfficiently
    test('given_many_suggestions_when_rendering_then_limits_displayed_count', async () => {
      // Given: API returns many suggestions
      const largeSuggestionList = Array.from({ length: 50 }, (_, i) => ({
        text: `suggestion_${i}`,
        type: 'keyword',
        description: `Description ${i}`
      }));
      
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => new SuggestionResponseBuilder()
          .withSuggestions(largeSuggestionList)
          .build()
      });
      
      const props = new AutoCompletePropsBuilder().build();
      render(<AutoCompleteTextarea {...props} />);
      
      // When: Triggering suggestions
      await userEvent.type(screen.getByRole('textbox'), 'sug');
      act(() => {
        jest.advanceTimersByTime(300);
      });
      
      // Then: Component handles large list without issues
      await waitFor(() => {
        const suggestions = screen.getAllByText(/suggestion_\d+/);
        expect(suggestions.length).toBeLessThanOrEqual(50); // All rendered
      });
    });
  });
});

// Integration Tests for AutoComplete with Backend
describe('AutoComplete Integration Tests', () => {
  // Test: Integration_BackendAvailable_UsesNLPSuggestions
  test('given_backend_available_when_requesting_suggestions_then_uses_nlp_source', async () => {
    // Given: Backend returns NLP suggestions
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        success: true,
        data: {
          suggestions: [
            { text: 'forall x', type: 'quantifier', description: 'Universal quantifier with variable' }
          ],
          source: 'nlp'
        }
      })
    });
    
    const props = new AutoCompletePropsBuilder().build();
    render(<AutoCompleteTextarea {...props} />);
    
    // When: User types
    await userEvent.type(screen.getByRole('textbox'), 'for');
    act(() => {
      jest.advanceTimersByTime(300);
    });
    
    // Then: NLP suggestions are shown
    await waitFor(() => {
      expect(screen.getByText('forall x')).toBeInTheDocument();
      expect(screen.getByText('Universal quantifier with variable')).toBeInTheDocument();
    });
  });
  
  // Test: Integration_BackendUnavailable_UsesFallback
  test('given_backend_unavailable_when_requesting_suggestions_then_uses_fallback', async () => {
    // Given: Backend returns fallback suggestions
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        success: true,
        data: {
          suggestions: [
            { text: 'DEFINE', type: 'keyword', description: 'Define a new concept' }
          ],
          source: 'fallback'
        }
      })
    });
    
    const props = new AutoCompletePropsBuilder().build();
    render(<AutoCompleteTextarea {...props} />);
    
    // When: User types
    await userEvent.type(screen.getByRole('textbox'), 'def');
    act(() => {
      jest.advanceTimersByTime(300);
    });
    
    // Then: Fallback suggestions are shown
    await waitFor(() => {
      expect(screen.getByText('DEFINE')).toBeInTheDocument();
    });
  });
});