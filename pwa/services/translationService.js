/**
 * Translation Service
 * ==================
 * Centralized translation logic with intelligent routing
 * 
 * Author: DarkLightX/Dana Edwards
 */

import axios from 'axios';

// Backend configuration
const BACKEND_URLS = [
  'http://localhost:8000',
  'http://localhost:8001',
  'http://localhost:8003'
];

// Cache backend availability
let backendCache = {
  available: false,
  lastCheck: 0,
  url: null
};

const CACHE_DURATION = 30000; // 30 seconds

class TranslationService {
  constructor() {
    // Translation cache
    this.cache = new Map();
    this.cacheTimeout = 5 * 60 * 1000; // 5 minutes
  }

  /**
   * Main translation method - routes to appropriate translator
   */
  async translate({ sourceText, sourceLang, targetLang, options = {} }) {
    if (!sourceText) {
      throw new Error('Source text is required');
    }

    const { forceLocal = false, apiKey = null, useCache = true } = options;

    // Check cache first
    if (useCache) {
      const cached = this.getCached(sourceText, sourceLang, targetLang);
      if (cached) {
        return { ...cached, fromCache: true };
      }
    }

    let result;

    // Try backend first (unless forcing local)
    if (!forceLocal) {
      const backendResult = await this.tryBackendTranslation({ 
        sourceText, 
        sourceLang, 
        targetLang, 
        apiKey 
      });
      if (backendResult.success) {
        result = backendResult.data;
      }
    }

    // Use pattern-based translator as fallback
    if (!result) {
      result = this.patternTranslate(sourceText, sourceLang, targetLang);
    }

    // Cache the result
    if (useCache) {
      this.setCache(sourceText, sourceLang, targetLang, result);
    }

    return result;
  }

  /**
   * Get cached translation
   */
  getCached(sourceText, sourceLang, targetLang) {
    const key = this.getCacheKey(sourceText, sourceLang, targetLang);
    const cached = this.cache.get(key);
    
    if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
      return cached.result;
    }
    
    // Remove expired entry
    if (cached) {
      this.cache.delete(key);
    }
    
    return null;
  }

  /**
   * Set cache entry
   */
  setCache(sourceText, sourceLang, targetLang, result) {
    const key = this.getCacheKey(sourceText, sourceLang, targetLang);
    this.cache.set(key, {
      result,
      timestamp: Date.now()
    });

    // Limit cache size
    if (this.cache.size > 100) {
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }
  }

  /**
   * Generate cache key
   */
  getCacheKey(sourceText, sourceLang, targetLang) {
    return `${sourceLang}:${targetLang}:${sourceText}`;
  }

  /**
   * Check backend availability with caching
   */
  async checkBackendAvailability() {
    const now = Date.now();
    
    // Use cached result if still valid
    if (now - backendCache.lastCheck < CACHE_DURATION) {
      return backendCache;
    }

    // Check each backend URL
    for (const url of BACKEND_URLS) {
      try {
        const response = await axios.get(`${url}/health`, { timeout: 1000 });
        if (response.status === 200) {
          backendCache = {
            available: true,
            lastCheck: now,
            url
          };
          return backendCache;
        }
      } catch (error) {
        // Continue to next URL
      }
    }

    // No backend available
    backendCache = {
      available: false,
      lastCheck: now,
      url: null
    };
    return backendCache;
  }

  /**
   * Try translation via Python backend
   */
  async tryBackendTranslation({
    sourceText,
    sourceLang,
    targetLang,
    apiKey = null,
    grammarFilename = null,
    engineKey = 'auto'
  }) {
    const backend = await this.checkBackendAvailability();
    
    if (!backend.available) {
      return { success: false, error: 'Backend not available' };
    }

    try {
      // Prefer new v2 endpoint when advanced features are requested
      const needsV2 = grammarFilename !== null || engineKey !== 'auto';
      const endpoint = needsV2 ? '/v2/translate' : apiKey ? '/translate/secure' : '/translate';
      const headers = {
        'Content-Type': 'application/json',
        ...(apiKey && { 'Authorization': `Bearer ${apiKey}` })
      };

      const response = await axios.post(
        `${backend.url}${endpoint}`,
        {
          sourceText,
          sourceLangKey: sourceLang,
          targetLangKey: targetLang,
          ...(grammarFilename && { grammarFilename }),
          ...(engineKey && { engineKey })
        },
        { headers, timeout: 5000 }
      );

      return {
        success: true,
        data: {
          translatedText: response.data.translatedText,
          provider: response.data.provider || 'Python Backend',
          backendUrl: backend.url,
          ...response.data
        }
      };
    } catch (error) {
      console.error('Backend translation error:', error.message);
      return { success: false, error: error.message };
    }
  }

  /**
   * Upload a grammar file to the backend and make it active (if desired).
   */
  async uploadGrammar(file, autoActivate = true) {
    const backend = await this.checkBackendAvailability();
    if (!backend.available) {
      throw new Error('Backend not available');
    }

    const formData = new FormData();
    formData.append('file', file);

    const response = await axios.post(`${backend.url}/v2/grammars`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });

    if (autoActivate && response.data?.filename) {
      // Activate via translate call with grammarFilename
      await this.tryBackendTranslation({
        sourceText: '',
        sourceLang: 'PLAIN_ENGLISH',
        targetLang: 'TAU',
        grammarFilename: response.data.filename
      });
    }

    return response.data;
  }

  /**
   * List currently loaded grammars from backend.
   */
  async listGrammars() {
    const backend = await this.checkBackendAvailability();
    if (!backend.available) {
      return { active: null, loaded: {} };
    }

    const response = await axios.get(`${backend.url}/v2/grammars`);
    return response.data;
  }

  /**
   * Pattern-based translation (fallback)
   */
  patternTranslate(text, sourceLang, targetLang) {
    // TCE to TAU
    if (sourceLang === 'PLAIN_ENGLISH' && targetLang === 'TAU') {
      return {
        translatedText: this.tceToTau(text),
        provider: 'Pattern Translator',
        model: 'tau-patterns-v1'
      };
    }

    // TAU to TCE
    if (sourceLang === 'TAU' && targetLang === 'PLAIN_ENGLISH') {
      return {
        translatedText: this.tauToTce(text),
        provider: 'Pattern Translator',
        model: 'tau-patterns-v1'
      };
    }

    // ILR translation
    if (targetLang === 'ILR') {
      return {
        translatedText: this.toILR(text, sourceLang),
        provider: 'Pattern Translator',
        model: 'ilr-v1'
      };
    }

    // CNL translation
    if (targetLang === 'CNL') {
      return {
        translatedText: this.toCNL(text, sourceLang),
        provider: 'Pattern Translator',
        model: 'cnl-v1'
      };
    }

    // Default passthrough
    return {
      translatedText: text,
      provider: 'Passthrough',
      model: 'none'
    };
  }

  /**
   * TCE to TAU pattern translation
   */
  tceToTau(text) {
    let result = text.toLowerCase().trim();
    
    // Remove trailing period
    if (result.endsWith('.')) {
      result = result.slice(0, -1);
    }
    
    // Apply grammar rules
    const rules = {
      // Temporal operators
      'always': 'always',
      'sometimes': 'sometimes',
      'eventually': '<>',
      'never': '!(<>',
      
      // Boolean operators
      ' and ': ' && ',
      ' or ': ' || ',
      ' not ': ' !',
      ' implies ': ' -> ',
      ' if and only if ': ' <-> ',
      ' iff ': ' <-> ',
      ' xor ': ' ^ ',
      
      // Comparison operators
      ' is always greater than or equal to ': ' >= ',
      ' is always less than or equal to ': ' <= ',
      ' is always greater than ': ' > ',
      ' is always less than ': ' < ',
      ' is always equal to ': ' = ',
      ' is always ': ' = ',
      ' greater than or equal to ': ' >= ',
      ' less than or equal to ': ' <= ',
      ' greater than ': ' > ',
      ' less than ': ' < ',
      ' equals ': ' = ',
      ' is equal to ': ' = ',
      ' is ': ' = ',
      ' does not equal ': ' != ',
      ' is not equal to ': ' != ',
      
      // Quantifiers
      'for all': 'forall',
      'there exists': 'exists',
      'such that': ':'
    };
    
    // Apply rules
    for (const [pattern, replacement] of Object.entries(rules)) {
      const regex = new RegExp(pattern.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi');
      result = result.replace(regex, replacement);
    }
    
    // Handle temporal wrapping
    if (result.includes(' > ') || result.includes(' < ') || 
        result.includes(' = ') || result.includes(' >= ') || 
        result.includes(' <= ') || result.includes(' != ')) {
      
      if (!result.match(/^(always|sometimes|eventually|never)\s/)) {
        if (text.toLowerCase().includes('always')) {
          result = `always (${result})`;
        }
      }
    }
    
    return result;
  }

  /**
   * TAU to TCE pattern translation
   */
  tauToTce(text) {
    let result = text.trim();
    
    // Reverse rules
    const reverseRules = {
      'always \\((.+?)\\)': 'The statement "$1" is always true',
      'sometimes \\((.+?)\\)': 'Sometimes "$1" holds',
      'eventually \\((.+?)\\)': 'Eventually "$1" will be true',
      'never \\((.+?)\\)': 'It is never the case that "$1"',
      ' && ': ' and ',
      ' \\|\\| ': ' or ',
      ' ! ': ' not ',
      ' -> ': ' implies ',
      ' <-> ': ' if and only if ',
      ' \\^ ': ' exclusive or ',
      ' >= ': ' is greater than or equal to ',
      ' <= ': ' is less than or equal to ',
      ' > ': ' is greater than ',
      ' < ': ' is less than ',
      ' = ': ' equals ',
      ' != ': ' does not equal '
    };
    
    // Apply reverse rules
    for (const [pattern, replacement] of Object.entries(reverseRules)) {
      result = result.replace(new RegExp(pattern, 'g'), replacement);
    }
    
    // Capitalize and add period
    if (result) {
      result = result.charAt(0).toUpperCase() + result.slice(1);
      if (!result.endsWith('.')) {
        result += '.';
      }
    }
    
    return result;
  }

  /**
   * Convert to ILR format
   */
  toILR(text, sourceLang) {
    let tauText = text;
    if (sourceLang === 'PLAIN_ENGLISH') {
      tauText = this.tceToTau(text);
    }

    const ilr = {
      type: "logical_expression",
      source: text,
      parsed: tauText,
      structure: this.parseLogicalStructure(tauText, text)
    };

    return JSON.stringify(ilr, null, 2);
  }

  /**
   * Convert to CNL format
   */
  toCNL(text, sourceLang) {
    let tauText = text;
    if (sourceLang === 'PLAIN_ENGLISH') {
      tauText = this.tceToTau(text);
    }

    // Handle temporal logic
    const temporalMatch = tauText.match(/^(always|sometimes|eventually|never)\s*\((.+)\)$/);
    if (temporalMatch) {
      const [, operator, expression] = temporalMatch;
      const cnlExpression = this.convertExpressionToCNL(expression);
      
      switch (operator) {
        case 'always':
          return `It is always the case that ${cnlExpression}`;
        case 'sometimes':
          return `Sometimes it is the case that ${cnlExpression}`;
        case 'eventually':
          return `Eventually it will be the case that ${cnlExpression}`;
        case 'never':
          return `It is never the case that ${cnlExpression}`;
      }
    }

    return this.convertExpressionToCNL(tauText);
  }

  /**
   * Parse logical structure for ILR
   */
  parseLogicalStructure(tauText, originalText) {
    // Temporal logic
    const temporalMatch = tauText.match(/^(always|sometimes|eventually|never)\s*\((.+)\)$/);
    if (temporalMatch) {
      const [, operator, expression] = temporalMatch;
      return {
        temporal_operator: operator,
        scope: this.parseInnerExpression(expression),
        semantics: `The property "${expression}" holds ${operator}`
      };
    }

    // Quantifiers
    const quantifierMatch = tauText.match(/^(forall|exists)\s+(\w+)\s*:\s*(.+)$/);
    if (quantifierMatch) {
      const [, quantifier, variable, expression] = quantifierMatch;
      return {
        quantifier,
        variable,
        scope: this.parseInnerExpression(expression),
        semantics: `${quantifier === 'forall' ? 'For all' : 'There exists'} ${variable}, ${expression}`
      };
    }

    // Comparisons
    const comparisonMatch = tauText.match(/(.+?)\s*(>=|<=|>|<|=|!=)\s*(.+)/);
    if (comparisonMatch) {
      const [, left, operator, right] = comparisonMatch;
      return {
        type: "comparison",
        left_operand: left.trim(),
        operator,
        right_operand: right.trim(),
        semantics: `${left.trim()} ${this.getOperatorDescription(operator)} ${right.trim()}`
      };
    }

    return {
      type: "atomic",
      expression: tauText,
      semantics: originalText
    };
  }

  /**
   * Parse inner expressions for ILR
   */
  parseInnerExpression(expression) {
    const comparisonMatch = expression.match(/(.+?)\s*(>=|<=|>|<|=|!=)\s*(.+)/);
    if (comparisonMatch) {
      const [, left, operator, right] = comparisonMatch;
      return {
        type: "comparison",
        left_operand: left.trim(),
        operator,
        right_operand: right.trim()
      };
    }

    if (expression.includes(' && ')) {
      return {
        type: "conjunction",
        operands: expression.split(' && ').map(p => p.trim())
      };
    }

    if (expression.includes(' || ')) {
      return {
        type: "disjunction", 
        operands: expression.split(' || ').map(p => p.trim())
      };
    }

    return {
      type: "atomic",
      value: expression
    };
  }

  /**
   * Convert expression to CNL
   */
  convertExpressionToCNL(expression) {
    let result = expression;
    
    const operatorMap = {
      ' >= ': ' is greater than or equal to ',
      ' <= ': ' is less than or equal to ',
      ' > ': ' is greater than ',
      ' < ': ' is less than ',
      ' = ': ' equals ',
      ' != ': ' does not equal ',
      ' && ': ' and ',
      ' || ': ' or ',
      ' ! ': ' not ',
      ' -> ': ' implies ',
      ' <-> ': ' if and only if '
    };
    
    for (const [symbol, phrase] of Object.entries(operatorMap)) {
      result = result.replace(new RegExp(symbol.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g'), phrase);
    }
    
    return result;
  }

  /**
   * Get operator description
   */
  getOperatorDescription(operator) {
    const descriptions = {
      '>': 'is greater than',
      '<': 'is less than',
      '>=': 'is greater than or equal to',
      '<=': 'is less than or equal to',
      '=': 'equals',
      '!=': 'does not equal'
    };
    return descriptions[operator] || operator;
  }
}

// Export singleton instance
export default new TranslationService();