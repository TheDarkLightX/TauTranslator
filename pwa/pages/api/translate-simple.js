/**
 * Simple Pattern-Based Translation API
 * ===================================
 * 
 * Direct pattern-based translation without external dependencies.
 * Uses the same logic as the LMQL translator but implemented in JavaScript.
 */

export default function handler(req, res) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', ['POST']);
    return res.status(405).end(`Method ${req.method} Not Allowed`);
  }

  const { sourceText, sourceLangKey, targetLangKey, sourceLangLabel, targetLangLabel } = req.body;

  if (!sourceText) {
    return res.status(400).json({
      error: 'Missing source text',
      message: 'sourceText is required'
    });
  }

  try {
    console.log(`Simple API: Translating "${sourceText}" from ${sourceLangKey} to ${targetLangKey}`);
    
    const translatedText = translateText(sourceText, sourceLangKey, targetLangKey);
    
    return res.status(200).json({
      translatedText: translatedText,
      provider: 'Pattern Translator',
      model: 'javascript-patterns',
      secure: true,
      mock: false,
      processingTime: 0.05,
      direction: `${sourceLangKey}_to_${targetLangKey}`
    });

  } catch (error) {
    console.error('Simple translation error:', error);
    
    return res.status(200).json({
      translatedText: `${targetLangKey}: ${sourceText}`,
      provider: 'Fallback',
      model: 'passthrough',
      secure: true,
      mock: true,
      processingTime: 0.01,
      error: error.message
    });
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
  
  // Other language pairs - simple formatting
  if (targetLang === 'CNL') {
    return `CNL: ${result}`;
  } else if (targetLang === 'ILR') {
    return `ILR(${result})`;
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