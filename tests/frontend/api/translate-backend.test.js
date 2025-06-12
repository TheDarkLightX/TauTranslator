/**
 * Unit Tests for Translate Backend API (including Autocomplete)
 * =============================================================
 * Following FIRST principles and BDD approach
 * 
 * Copyright: DarkLightX/Dana Edwards
 */

import handler, { _handle_autocomplete_request_async, _generate_basic_suggestions_fallback } from '../../pages/api/translate-backend';
import { createMocks } from 'node-mocks-http';

// Mock global fetch
global.fetch = jest.fn();

// Test Data Builders
class AutoCompleteRequestBuilder {
  constructor() {
    this.text = 'for';
    this.position = null;
    this.context = null;
  }
  
  withText(text) {
    this.text = text;
    return this;
  }
  
  withPosition(position) {
    this.position = position;
    return this;
  }
  
  withContext(context) {
    this.context = context;
    return this;
  }
  
  build() {
    return {
      endpoint: '/autocomplete',
      data: {
        text: this.text,
        position: this.position,
        context: this.context
      }
    };
  }
}

class BackendResponseBuilder {
  constructor() {
    this.success = true;
    this.data = {
      suggestions: [],
      source: 'nlp'
    };
  }
  
  withSuggestions(suggestions) {
    this.data.suggestions = suggestions;
    return this;
  }
  
  withError() {
    this.success = false;
    return this;
  }
  
  build() {
    return {
      success: this.success,
      data: this.data
    };
  }
}

describe('Translate Backend API - Autocomplete Endpoint', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });
  
  describe('Autocomplete Request Handling', () => {
    // Test: AutoComplete_ValidRequest_ReturnsSuccess
    test('given_valid_autocomplete_request_when_backend_available_then_returns_suggestions', async () => {
      // Given: Backend returns suggestions
      const mockSuggestions = [
        { text: 'forall', type: 'quantifier', description: 'Universal quantification' }
      ];
      
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => new BackendResponseBuilder()
          .withSuggestions(mockSuggestions)
          .build()
      });
      
      const { req, res } = createMocks({
        method: 'POST',
        body: new AutoCompleteRequestBuilder().build()
      });
      
      // When: Handling the request
      await handler(req, res);
      
      // Then: Returns success with suggestions
      expect(res._getStatusCode()).toBe(200);
      const response = JSON.parse(res._getData());
      expect(response.success).toBe(true);
      expect(response.data.suggestions).toHaveLength(1);
      expect(response.data.suggestions[0].text).toBe('forall');
    });
    
    // Test: AutoComplete_MissingText_ReturnsBadRequest
    test('given_missing_text_when_requesting_autocomplete_then_returns_400_error', async () => {
      // Given: Request without text
      const { req, res } = createMocks({
        method: 'POST',
        body: {
          endpoint: '/autocomplete',
          data: {
            text: null,
            position: null,
            context: null
          }
        }
      });
      
      // When: Handling the request
      await handler(req, res);
      
      // Then: Returns 400 error
      expect(res._getStatusCode()).toBe(400);
      const response = JSON.parse(res._getData());
      expect(response.success).toBe(false);
      expect(response.error).toBe('Missing text for autocomplete');
    });
    
    // Test: AutoComplete_BackendUnavailable_ReturnsFallback
    test('given_all_backends_unavailable_when_requesting_then_returns_fallback_suggestions', async () => {
      // Given: All backends fail
      fetch.mockRejectedValue(new Error('Connection refused'));
      
      const { req, res } = createMocks({
        method: 'POST',
        body: new AutoCompleteRequestBuilder()
          .withText('def')
          .build()
      });
      
      // When: Handling the request
      await handler(req, res);
      
      // Then: Returns fallback suggestions
      expect(res._getStatusCode()).toBe(200);
      const response = JSON.parse(res._getData());
      expect(response.success).toBe(true);
      expect(response.data.source).toBe('fallback');
      expect(response.data.suggestions.length).toBeGreaterThan(0);
      expect(response.data.suggestions.some(s => s.text === 'DEFINE')).toBe(true);
    });
    
    // Test: AutoComplete_WithAuthorization_PassesHeader
    test('given_authorization_header_when_requesting_then_forwards_to_backend', async () => {
      // Given: Request with auth header
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => new BackendResponseBuilder().build()
      });
      
      const { req, res } = createMocks({
        method: 'POST',
        headers: {
          authorization: 'Bearer test-token'
        },
        body: new AutoCompleteRequestBuilder().build()
      });
      
      // When: Handling the request
      await handler(req, res);
      
      // Then: Auth header is forwarded
      expect(fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Authorization': 'Bearer test-token'
          })
        })
      );
    });
  });
  
  describe('Fallback Suggestion Generation', () => {
    // Test: FallbackSuggestions_EmptyInput_ReturnsAllBasicSuggestions
    test('given_empty_input_when_generating_fallback_then_returns_all_suggestions', () => {
      // Given: Empty input
      const text = '';
      
      // When: Generating fallback suggestions
      const suggestions = _generate_basic_suggestions_fallback(text);
      
      // Then: Returns limited set of all suggestions
      expect(suggestions.length).toBe(10);
      expect(suggestions.some(s => s.type === 'keyword')).toBe(true);
      expect(suggestions.some(s => s.type === 'operator')).toBe(true);
      expect(suggestions.some(s => s.type === 'temporal')).toBe(true);
      expect(suggestions.some(s => s.type === 'quantifier')).toBe(true);
    });
    
    // Test: FallbackSuggestions_PartialMatch_FiltersResults
    test('given_partial_text_when_generating_fallback_then_filters_matching_suggestions', () => {
      // Given: Partial text 'for'
      const text = 'for';
      
      // When: Generating fallback suggestions
      const suggestions = _generate_basic_suggestions_fallback(text);
      
      // Then: Only returns suggestions containing 'for'
      suggestions.forEach(suggestion => {
        expect(suggestion.text.toLowerCase()).toContain('for');
      });
      expect(suggestions.some(s => s.text === 'forall')).toBe(true);
    });
    
    // Test: FallbackSuggestions_NoMatch_ReturnsEmpty
    test('given_non_matching_text_when_generating_fallback_then_returns_empty', () => {
      // Given: Text that doesn't match any suggestions
      const text = 'xyz';
      
      // When: Generating fallback suggestions
      const suggestions = _generate_basic_suggestions_fallback(text);
      
      // Then: Returns empty array
      expect(suggestions).toEqual([]);
    });
    
    // Test: FallbackSuggestions_CaseInsensitive_MatchesRegardlessOfCase
    test('given_uppercase_input_when_generating_fallback_then_matches_case_insensitive', () => {
      // Given: Uppercase input
      const text = 'FOR';
      
      // When: Generating fallback suggestions
      const suggestions = _generate_basic_suggestions_fallback(text);
      
      // Then: Matches suggestions case-insensitively
      expect(suggestions.some(s => s.text === 'forall')).toBe(true);
    });
  });
  
  describe('Backend Failover Logic', () => {
    // Test: Failover_FirstBackendSucceeds_DoesNotTryOthers
    test('given_first_backend_succeeds_when_requesting_then_stops_trying_others', async () => {
      // Given: First backend succeeds
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => new BackendResponseBuilder().build()
      });
      
      const { req, res } = createMocks({
        method: 'POST',
        body: new AutoCompleteRequestBuilder().build()
      });
      
      // When: Handling the request
      await handler(req, res);
      
      // Then: Only tries first backend
      expect(fetch).toHaveBeenCalledTimes(1);
      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/nlp/autocomplete',
        expect.any(Object)
      );
    });
    
    // Test: Failover_FirstBackendFails_TriesNext
    test('given_first_backend_fails_when_requesting_then_tries_next_backend', async () => {
      // Given: First backend fails, second succeeds
      fetch
        .mockRejectedValueOnce(new Error('Connection refused'))
        .mockResolvedValueOnce({
          ok: true,
          json: async () => new BackendResponseBuilder().build()
        });
      
      const { req, res } = createMocks({
        method: 'POST',
        body: new AutoCompleteRequestBuilder().build()
      });
      
      // When: Handling the request
      await handler(req, res);
      
      // Then: Tries both backends
      expect(fetch).toHaveBeenCalledTimes(2);
      expect(fetch).toHaveBeenNthCalledWith(1,
        'http://localhost:8000/api/nlp/autocomplete',
        expect.any(Object)
      );
      expect(fetch).toHaveBeenNthCalledWith(2,
        'http://localhost:8001/api/nlp/autocomplete',
        expect.any(Object)
      );
    });
  });
  
  describe('Error Handling', () => {
    // Test: ErrorHandling_NetworkError_HandlesGracefully
    test('given_network_error_when_requesting_then_returns_fallback_without_crashing', async () => {
      // Given: Network error
      fetch.mockImplementationOnce(() => {
        throw new Error('Network error');
      });
      
      const { req, res } = createMocks({
        method: 'POST',
        body: new AutoCompleteRequestBuilder().build()
      });
      
      // When: Handling the request
      await handler(req, res);
      
      // Then: Returns fallback response
      expect(res._getStatusCode()).toBe(200);
      const response = JSON.parse(res._getData());
      expect(response.success).toBe(true);
      expect(response.data.source).toBe('fallback');
    });
    
    // Test: ErrorHandling_InvalidJSON_HandlesGracefully
    test('given_invalid_json_response_when_backend_responds_then_returns_fallback', async () => {
      // Given: Backend returns invalid JSON
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => {
          throw new Error('Invalid JSON');
        }
      });
      
      const { req, res } = createMocks({
        method: 'POST',
        body: new AutoCompleteRequestBuilder().build()
      });
      
      // When: Handling the request
      await handler(req, res);
      
      // Then: Returns fallback response
      expect(res._getStatusCode()).toBe(200);
      const response = JSON.parse(res._getData());
      expect(response.success).toBe(true);
      expect(response.data.source).toBe('fallback');
    });
  });
  
  describe('Performance Considerations', () => {
    // Test: Performance_LongText_HandlesEfficiently
    test('given_long_input_text_when_generating_suggestions_then_completes_quickly', () => {
      // Given: Long input text
      const longText = 'a'.repeat(1000);
      
      // When: Measuring performance
      const startTime = Date.now();
      const suggestions = _generate_basic_suggestions_fallback(longText);
      const endTime = Date.now();
      
      // Then: Completes in reasonable time
      expect(endTime - startTime).toBeLessThan(100); // Should complete in < 100ms
      expect(suggestions).toEqual([]); // No matches expected
    });
  });
});