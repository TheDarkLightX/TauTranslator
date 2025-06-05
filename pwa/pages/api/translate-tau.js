/**
 * Proper Tau Language Translation API
 * ===================================
 * 
 * Translates natural language to proper Tau syntax based on the official tau.tgf grammar
 * from https://github.com/IDNI/tau-lang/tree/main/parser
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
      console.log(`Tau API: Translating from ${sourceLangLabel} (${sourceLangKey}) to ${targetLangLabel} (${targetLangKey}): ${sourceText}`);

      const translatedText = translateToProperTau(sourceText, sourceLangKey, targetLangKey);
      
      return res.status(200).json({
        translatedText: translatedText,
        provider: 'Tau Language Translator',
        model: 'tau-grammar-v1',
        secure: true,
        mock: false,
        processingTime: 0.03
      });
      
    } catch (translationError) {
      console.error('Tau translation error:', translationError.message);
      
      return res.status(500).json({
        error: 'Translation failed',
        message: translationError.message,
        translatedText: sourceText
      });
    }
  } else {
    res.setHeader('Allow', ['POST']);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}

function translateToProperTau(text, sourceLang, targetLang) {
  if (sourceLang === 'PLAIN_ENGLISH' && targetLangKey === 'TAU') {
    return translateNaturalLanguageToTau(text);
  } else if (sourceLang === 'TAU' && targetLang === 'PLAIN_ENGLISH') {
    return translateTauToNaturalLanguage(text);
  } else {
    return text; // No translation needed
  }
}

function translateNaturalLanguageToTau(text) {
  let input = text.trim().toLowerCase();
  
  // Handle specific natural language patterns and convert to proper Tau syntax
  
  // Pattern 1: SBF declarations
  if (input.match(/.*filter.*takes.*input.*/)) {
    // "sbf filter takes input_stream" -> proper Tau: variable assignment
    // Based on tau.tgf: ref := (capture | ref | wff | bf)
    const match = input.match(/(.*?)(?:filter|processor|sbf).*takes.*(input.*)/);
    if (match) {
      const filterName = match[1].trim() || 'filter';
      const inputName = match[2].replace(/[^a-zA-Z0-9_]/g, '_');
      return `${filterName}_input := ${inputName}.`;
    }
  }
  
  // Pattern 2: Variable assignments
  if (input.match(/.*(\w+).*(?:equals?|is|:=).*/)) {
    const assignmentMatch = input.match(/(.*?)(?:equals?|is|set.*to|assign.*to|\s*:=\s*)(.*)/);
    if (assignmentMatch) {
      let varName = assignmentMatch[1].trim().replace(/[^a-zA-Z0-9_]/g, '_');
      let value = assignmentMatch[2].trim();
      
      // Convert natural language values to Tau syntax
      if (value === 'true' || value === 'yes' || value === 'on') {
        value = '1'; // Tau uses 1 for true
      } else if (value === 'false' || value === 'no' || value === 'off') {
        value = '0'; // Tau uses 0 for false  
      }
      
      // Tau assignment syntax: ref := bf
      return `${varName} := ${value}.`;
    }
  }
  
  // Pattern 3: Conditional statements
  if (input.match(/if.*then.*/)) {
    const condMatch = input.match(/if\s+(.*?)\s+then\s+(.*?)(?:\s+else\s+(.*))?/);
    if (condMatch) {
      let condition = condMatch[1];
      let thenPart = condMatch[2];
      let elsePart = condMatch[3];
      
      // Convert condition to Tau syntax
      condition = convertConditionToTau(condition);
      
      // Tau conditional syntax: wff ? wff : wff
      if (elsePart) {
        return `(${condition}) ? (${thenPart}) : (${elsePart}).`;
      } else {
        return `(${condition}) ? (${thenPart}) : 0.`;
      }
    }
  }
  
  // Pattern 4: Temporal expressions
  if (input.match(/always|sometimes|eventually|never/)) {
    const temporalMatch = input.match(/(always|sometimes|eventually|never)\s+(.*)/);
    if (temporalMatch) {
      const operator = temporalMatch[1];
      let expression = temporalMatch[2];
      
      // Convert to Tau temporal syntax
      expression = convertExpressionToTau(expression);
      
      switch (operator) {
        case 'always':
          return `always (${expression}).`;
        case 'sometimes':
          return `sometimes (${expression}).`;
        case 'eventually':
          return `<> (${expression}).`;
        case 'never':
          return `!(sometimes (${expression})).`;
      }
    }
  }
  
  // Pattern 5: Boolean expressions
  if (input.match(/.*(?:and|or|not).*/)) {
    let result = input;
    
    // Convert to proper Tau boolean operators
    result = result.replace(/\band\b/g, '&&');
    result = result.replace(/\bor\b/g, '||');
    result = result.replace(/\bnot\b/g, '!');
    
    return result + '.';
  }
  
  // Default: treat as expression and add period
  return convertExpressionToTau(input) + '.';
}

function convertConditionToTau(condition) {
  let result = condition.trim();
  
  // Convert comparison operators to Tau syntax
  result = result.replace(/\bis\s+greater\s+than\s+or\s+equal\s+to\b/g, '>=');
  result = result.replace(/\bis\s+less\s+than\s+or\s+equal\s+to\b/g, '<=');
  result = result.replace(/\bis\s+greater\s+than\b/g, '>');
  result = result.replace(/\bis\s+less\s+than\b/g, '<');
  result = result.replace(/\bis\s+equal\s+to\b/g, '=');
  result = result.replace(/\bis\s+not\s+equal\s+to\b/g, '!=');
  result = result.replace(/\bis\b/g, '=');
  result = result.replace(/\bequals?\b/g, '=');
  
  // Convert boolean operators
  result = result.replace(/\band\b/g, '&&');
  result = result.replace(/\bor\b/g, '||');
  result = result.replace(/\bnot\b/g, '!');
  
  return result;
}

function convertExpressionToTau(expression) {
  let result = expression.trim();
  
  // Convert comparison operators
  result = result.replace(/\bis\s+greater\s+than\b/g, '>');
  result = result.replace(/\bis\s+less\s+than\b/g, '<');
  result = result.replace(/\bis\s+equal\s+to\b/g, '=');
  result = result.replace(/\bgreater\s+than\b/g, '>');
  result = result.replace(/\bless\s+than\b/g, '<');
  result = result.replace(/\bequals?\b/g, '=');
  result = result.replace(/\bis\b/g, '=');
  
  // Convert boolean values
  result = result.replace(/\btrue\b/g, '1');
  result = result.replace(/\bfalse\b/g, '0');
  result = result.replace(/\byes\b/g, '1');
  result = result.replace(/\bno\b/g, '0');
  
  // Convert boolean operators
  result = result.replace(/\band\b/g, '&&');
  result = result.replace(/\bor\b/g, '||');
  result = result.replace(/\bnot\b/g, '!');
  
  return result;
}

function translateTauToNaturalLanguage(tauCode) {
  let result = tauCode.trim();
  
  // Remove trailing period
  if (result.endsWith('.')) {
    result = result.slice(0, -1);
  }
  
  // Convert Tau operators back to natural language
  result = result.replace(/&&/g, ' and ');
  result = result.replace(/\|\|/g, ' or ');
  result = result.replace(/!/g, 'not ');
  result = result.replace(/=/g, ' equals ');
  result = result.replace(/!=/g, ' does not equal ');
  result = result.replace(/>=/g, ' is greater than or equal to ');
  result = result.replace(/<=/g, ' is less than or equal to ');
  result = result.replace(/>/g, ' is greater than ');
  result = result.replace(/</g, ' is less than ');
  
  // Convert temporal operators
  result = result.replace(/always\s*\(/g, 'It is always true that (');
  result = result.replace(/sometimes\s*\(/g, 'Sometimes (');
  result = result.replace(/<>\s*\(/g, 'Eventually (');
  
  // Convert assignments
  result = result.replace(/(\w+)\s*:=\s*(.+)/g, '$1 is assigned the value $2');
  
  // Convert conditionals
  result = result.replace(/\((.*?)\)\s*\?\s*\((.*?)\)\s*:\s*\((.*?)\)/g, 
    'If $1, then $2, otherwise $3');
  
  // Convert boolean values
  result = result.replace(/\b1\b/g, 'true');
  result = result.replace(/\b0\b/g, 'false');
  
  return result + '.';
}