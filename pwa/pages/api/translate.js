/**
 * Translation API Route - Built-in Pattern Translation
 * ===================================================
 *
 * This route provides direct pattern-based translation without external dependencies.
 * No authentication or API keys required - works out of the box.
 */

export default async function handler(req, res) {
  if (req.method === 'POST') {
    const { sourceText, sourceLangKey, targetLangKey, sourceLangLabel, targetLangLabel } = req.body;
    
    if (!sourceText) {
      return res.status(400).json({
        error: 'Missing source text',
        message: 'sourceText is required'
      });
    }

    try {
      console.log(`API: Translating from ${sourceLangLabel} (${sourceLangKey}) to ${targetLangLabel} (${targetLangKey}): ${sourceText}`);

      // Use simple pattern-based translation (always works, no dependencies)
      const translatedText = translateText(sourceText, sourceLangKey, targetLangKey);
      
      return res.status(200).json({
        translatedText: translatedText,
        provider: 'Built-in Pattern Translator',
        model: 'tau-patterns-v1',
        secure: true,
        mock: false,
        processingTime: 0.02
      });
      
    } catch (translationError) {
      console.log('Pattern translation error:', translationError.message);
      
      // Absolute fallback
      return res.status(200).json({
        translatedText: `${targetLangKey}: ${sourceText}`,
        provider: 'Fallback',
        model: 'passthrough',
        secure: true,
        mock: true,
        processingTime: 0.01
      });
    }
  } else {
    res.setHeader('Allow', ['POST']);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}

function translateText(text, sourceLang, targetLang) {
  // Normalize input
  let result = text.trim();
  
  // Remove trailing period
  if (result.endsWith('.')) {
    result = result.slice(0, -1);
  }
  
  // TCE to TAU translation (Plain English to TAU)
  if (sourceLang === 'PLAIN_ENGLISH' && targetLang === 'TAU') {
    return translateTceToTau(result);
  }
  
  // TAU to TCE translation (TAU to Plain English)
  if (sourceLang === 'TAU' && targetLang === 'PLAIN_ENGLISH') {
    return translateTauToTce(result);
  }
  
  // Other language pairs
  if (targetLang === 'CNL') {
    return translateToControlledNaturalLanguage(result, sourceLang);
  } else if (targetLang === 'ILR') {
    return translateToIntermediateLogicRepresentation(result, sourceLang);
  } else {
    return result;
  }
}

function translateTceToTau(text) {
  let result = text.toLowerCase();
  
  // Grammar rules for TCE to TAU translation
  const rules = {
    // Temporal operators
    'always': 'always',
    'sometimes': 'sometimes',
    'eventually': 'eventually',
    'never': 'never',
    
    // Boolean operators
    ' and ': ' & ',
    ' or ': ' | ',
    ' not ': ' ! ',
    ' implies ': ' -> ',
    ' if and only if ': ' <-> ',
    ' iff ': ' <-> ',
    ' xor ': ' ^ ',
    
    // Comparison operators (order matters - longer first)
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
    'such that': ':',
    
    // Stream operators
    'at time': '@',
    'next': "'",
    'previous': 'prev',
    
    // Conditional
    'if': 'if',
    'then': 'then',
    'else': 'else'
  };
  
  // Apply grammar rules
  for (const [pattern, replacement] of Object.entries(rules)) {
    result = result.replace(new RegExp(pattern.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi'), replacement);
  }
  
  // Handle temporal expressions like "x is always greater than y"
  result = result.replace(/^(.+?)\s+is\s+always\s+(.+)$/, 'always ($1 $2)');
  
  // Handle expressions that should be wrapped in temporal operators
  if (result.includes(' > ') || result.includes(' < ') || result.includes(' = ') || 
      result.includes(' >= ') || result.includes(' <= ') || result.includes(' != ')) {
    
    // Check if it already has a temporal operator
    if (!result.match(/^(always|sometimes|eventually|never)\s/)) {
      // Check for "always" patterns in the original text
      if (text.toLowerCase().includes('always')) {
        result = `always (${result})`;
      } else if (text.toLowerCase().includes('sometimes')) {
        result = `sometimes (${result})`;
      } else if (text.toLowerCase().includes('never')) {
        result = `never (${result})`;
      }
    }
  }
  
  // Handle quantifiers
  result = result.replace(/forall\s+(\w+)\s+such that\s+(.+)/, 'forall $1 : $2');
  result = result.replace(/exists\s+(\w+)\s+such that\s+(.+)/, 'exists $1 : $2');
  
  // Handle function calls and variables properly
  result = result.replace(/the\s+(\w+)/g, '$1');
  
  return result;
}

function translateTauToTce(text) {
  let result = text.trim();
  
  // Reverse the TAU to TCE translation
  const reverseRules = {
    // Temporal operators
    'always \\((.+?)\\)': 'The statement "$1" is always true',
    'sometimes \\((.+?)\\)': 'Sometimes "$1" holds',
    'eventually \\((.+?)\\)': 'Eventually "$1" will be true',
    'never \\((.+?)\\)': 'It is never the case that "$1"',
    
    // Boolean operators
    ' & ': ' and ',
    ' \\| ': ' or ',
    ' ! ': ' not ',
    ' -> ': ' implies ',
    ' <-> ': ' if and only if ',
    ' \\^ ': ' exclusive or ',
    
    // Comparison operators
    ' >= ': ' is greater than or equal to ',
    ' <= ': ' is less than or equal to ',
    ' > ': ' is greater than ',
    ' < ': ' is less than ',
    ' = ': ' equals ',
    ' != ': ' does not equal ',
    
    // Quantifiers
    'forall (\\w+) : (.+)': 'For all $1, $2 holds',
    'exists (\\w+) : (.+)': 'There exists $1 such that $2',
  };
  
  // Apply reverse rules
  for (const [pattern, replacement] of Object.entries(reverseRules)) {
    result = result.replace(new RegExp(pattern, 'g'), replacement);
  }
  
  // Capitalize first letter and add period
  if (result) {
    result = result.charAt(0).toUpperCase() + result.slice(1);
    if (!result.endsWith('.')) {
      result += '.';
    }
  }
  
  return result;
}

function translateToIntermediateLogicRepresentation(text, sourceLang) {
  // Convert to TAU first if coming from Plain English
  let tauText = text;
  if (sourceLang === 'PLAIN_ENGLISH') {
    tauText = translateTceToTau(text);
  }
  
  // Create proper ILR JSON structure
  const ilr = {
    type: "logical_expression",
    source: text,
    parsed: tauText,
    structure: parseLogicalStructure(tauText, text)
  };
  
  return JSON.stringify(ilr, null, 2);
}

function parseLogicalStructure(tauText, originalText) {
  // Parse temporal logic patterns
  const temporalMatch = tauText.match(/^(always|sometimes|eventually|never)\s*\((.+)\)$/);
  if (temporalMatch) {
    const [, operator, expression] = temporalMatch;
    return {
      temporal_operator: operator,
      scope: parseInnerExpression(expression),
      semantics: `The property "${expression}" holds ${operator}`
    };
  }
  
  // Parse quantifier patterns
  const quantifierMatch = tauText.match(/^(forall|exists)\s+(\w+)\s*:\s*(.+)$/);
  if (quantifierMatch) {
    const [, quantifier, variable, expression] = quantifierMatch;
    return {
      quantifier: quantifier,
      variable: variable,
      scope: parseInnerExpression(expression),
      semantics: `${quantifier === 'forall' ? 'For all' : 'There exists'} ${variable}, ${expression}`
    };
  }
  
  // Parse simple comparison
  const comparisonMatch = tauText.match(/(.+?)\s*(>=|<=|>|<|=|!=)\s*(.+)/);
  if (comparisonMatch) {
    const [, left, operator, right] = comparisonMatch;
    return {
      type: "comparison",
      left_operand: left.trim(),
      operator: operator,
      right_operand: right.trim(),
      semantics: `${left.trim()} ${getOperatorDescription(operator)} ${right.trim()}`
    };
  }
  
  // Default structure
  return {
    type: "atomic",
    expression: tauText,
    semantics: originalText
  };
}

function parseInnerExpression(expression) {
  // Parse comparisons within the expression
  const comparisonMatch = expression.match(/(.+?)\s*(>=|<=|>|<|=|!=)\s*(.+)/);
  if (comparisonMatch) {
    const [, left, operator, right] = comparisonMatch;
    return {
      type: "comparison",
      left_operand: left.trim(),
      operator: operator,
      right_operand: right.trim()
    };
  }
  
  // Parse boolean operations
  if (expression.includes(' & ')) {
    const parts = expression.split(' & ');
    return {
      type: "conjunction",
      operands: parts.map(p => p.trim())
    };
  }
  
  if (expression.includes(' | ')) {
    const parts = expression.split(' | ');
    return {
      type: "disjunction", 
      operands: parts.map(p => p.trim())
    };
  }
  
  return {
    type: "atomic",
    value: expression
  };
}

function getOperatorDescription(operator) {
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

function translateToControlledNaturalLanguage(text, sourceLang) {
  // Convert to TAU first if coming from Plain English
  let tauText = text;
  if (sourceLang === 'PLAIN_ENGLISH') {
    tauText = translateTceToTau(text);
  }
  
  // Convert TAU to structured CNL
  return translateTauToStructuredCNL(tauText);
}

function translateTauToStructuredCNL(tauText) {
  // Handle temporal logic
  const temporalMatch = tauText.match(/^(always|sometimes|eventually|never)\s*\((.+)\)$/);
  if (temporalMatch) {
    const [, operator, expression] = temporalMatch;
    const cnlExpression = convertExpressionToCNL(expression);
    
    switch (operator) {
      case 'always':
        return `It is always the case that ${cnlExpression}`;
      case 'sometimes':
        return `Sometimes it is the case that ${cnlExpression}`;
      case 'eventually':
        return `Eventually it will be the case that ${cnlExpression}`;
      case 'never':
        return `It is never the case that ${cnlExpression}`;
      default:
        return `${cnlExpression}`;
    }
  }
  
  // Handle quantifiers
  const quantifierMatch = tauText.match(/^(forall|exists)\s+(\w+)\s*:\s*(.+)$/);
  if (quantifierMatch) {
    const [, quantifier, variable, expression] = quantifierMatch;
    const cnlExpression = convertExpressionToCNL(expression);
    
    if (quantifier === 'forall') {
      return `For every ${variable}, ${cnlExpression}`;
    } else {
      return `There exists a ${variable} such that ${cnlExpression}`;
    }
  }
  
  // Handle simple expressions
  return convertExpressionToCNL(tauText);
}

function convertExpressionToCNL(expression) {
  let result = expression;
  
  // Convert operators to natural language
  const operatorMap = {
    ' >= ': ' is greater than or equal to ',
    ' <= ': ' is less than or equal to ',
    ' > ': ' is greater than ',
    ' < ': ' is less than ',
    ' = ': ' equals ',
    ' != ': ' does not equal ',
    ' & ': ' and ',
    ' | ': ' or ',
    ' ! ': ' not ',
    ' -> ': ' implies ',
    ' <-> ': ' if and only if '
  };
  
  for (const [symbol, phrase] of Object.entries(operatorMap)) {
    result = result.replace(new RegExp(symbol.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g'), phrase);
  }
  
  return result;
}