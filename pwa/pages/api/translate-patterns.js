/**
 * Consolidated Pattern-Based Translation API
 * ==========================================
 * 
 * Merges functionality from translate.js, translate-simple.js, and translate-tau.js
 * Provides comprehensive pattern-based translation between TCE, TAU, CNL, and ILR
 * 
 * Author: DarkLightX / Dana Edwards
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
      console.log(`Pattern Translator: ${sourceLangLabel} (${sourceLangKey}) → ${targetLangLabel} (${targetLangKey}): ${sourceText}`);

      const translatedText = translateText(sourceText, sourceLangKey, targetLangKey);
      
      return res.status(200).json({
        translatedText: translatedText,
        provider: 'Pattern-Based Translator',
        model: 'patterns-v2',
        secure: true,
        mock: false,
        processingTime: 0.02
      });
      
    } catch (error) {
      console.error('Pattern translation error:', error.message);
      
      return res.status(500).json({
        error: 'Translation failed',
        message: error.message,
        translatedText: sourceText
      });
    }
  } else {
    res.setHeader('Allow', ['POST']);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}

function translateText(text, sourceLang, targetLang) {
  // Direct pass-through for same language
  if (sourceLang === targetLang) {
    return text;
  }
  
  // Handle all translation paths
  if (sourceLang === 'PLAIN_ENGLISH' || sourceLang === 'TCE') {
    if (targetLang === 'TAU') {
      return translateNaturalLanguageToTau(text);
    } else if (targetLang === 'CNL') {
      return translateToCNL(text);
    } else if (targetLang === 'ILR') {
      return translateToILR(text);
    }
  } else if (sourceLang === 'TAU') {
    if (targetLang === 'PLAIN_ENGLISH' || targetLang === 'TCE') {
      return translateTauToNaturalLanguage(text);
    } else if (targetLang === 'CNL') {
      return translateTauToCNL(text);
    } else if (targetLang === 'ILR') {
      return translateTauToILR(text);
    }
  } else if (sourceLang === 'CNL') {
    if (targetLang === 'TAU') {
      return translateCNLToTau(text);
    } else if (targetLang === 'PLAIN_ENGLISH' || targetLang === 'TCE') {
      return translateCNLToNaturalLanguage(text);
    } else if (targetLang === 'ILR') {
      return translateCNLToILR(text);
    }
  } else if (sourceLang === 'ILR') {
    if (targetLang === 'TAU') {
      return translateILRToTau(text);
    } else if (targetLang === 'PLAIN_ENGLISH' || targetLang === 'TCE') {
      return translateILRToNaturalLanguage(text);
    } else if (targetLang === 'CNL') {
      return translateILRToCNL(text);
    }
  }
  
  // Fallback: prefix with target language
  return `[${targetLang}] ${text}`;
}

// ===== Natural Language to Tau Translation =====

function translateNaturalLanguageToTau(text) {
  let input = text.trim().toLowerCase();
  
  // Enhanced patterns from translate-tau.js
  
  // Pattern 1: Solve commands
  if (input.match(/solve\s+for/)) {
    const match = input.match(/solve\s+for\s+(.*?)(?:\s+(?:such\s+)?that\s+(.*))?$/);
    if (match) {
      const variable = match[1].trim();
      const constraint = match[2]?.trim();
      if (constraint) {
        return `solve { ${variable} : ${convertConditionToTau(constraint)} }.`;
      }
      return `solve { ${variable} }.`;
    }
  }
  
  // Pattern 2: SBF/Type declarations
  if (input.match(/declare|define.*as.*sbf|stream/)) {
    const match = input.match(/(?:declare|define)\s+(.*?)\s+as\s+(sbf|stream|filter)/);
    if (match) {
      const varName = match[1].trim();
      return `{ ${varName} } : sbf.`;
    }
  }
  
  // Pattern 3: Stream operations with time
  if (input.match(/at\s+time\s+\d+|at\s+t/)) {
    const streamMatch = input.match(/(.*?)\s+at\s+time\s+(\d+|t(?:-\d+)?)\s+(?:equals?|is)\s+(.*)/);
    if (streamMatch) {
      const streamName = streamMatch[1].trim().replace(/\s+/g, '_');
      const time = streamMatch[2];
      const value = convertExpressionToTau(streamMatch[3]);
      return `${streamName}[${time}] := ${value}.`;
    }
  }
  
  // Pattern 4: Variable assignments
  if (input.match(/.*(?:equals?|is|:=).*/)) {
    const assignmentMatch = input.match(/(.*?)(?:equals?|is|set.*to|assign.*to|\s*:=\s*)(.*)/);
    if (assignmentMatch) {
      let varName = assignmentMatch[1].trim().replace(/[^a-zA-Z0-9_]/g, '_');
      let value = assignmentMatch[2].trim();
      
      // Convert boolean values to Tau syntax
      value = convertBooleanValues(value);
      
      return `${varName} := ${value}.`;
    }
  }
  
  // Pattern 5: Conditional statements
  if (input.match(/if.*then.*/)) {
    const condMatch = input.match(/if\s+(.*?)\s+then\s+(.*?)(?:\s+(?:else|otherwise)\s+(.*))?/);
    if (condMatch) {
      let condition = convertConditionToTau(condMatch[1]);
      let thenPart = convertExpressionToTau(condMatch[2]);
      let elsePart = condMatch[3] ? convertExpressionToTau(condMatch[3]) : '0';
      
      return `(${condition}) ? (${thenPart}) : (${elsePart}).`;
    }
  }
  
  // Pattern 6: Temporal expressions
  if (input.match(/always|sometimes|eventually|never|next/)) {
    const temporalMatch = input.match(/(always|sometimes|eventually|never|next)\s+(.*)/);
    if (temporalMatch) {
      const operator = temporalMatch[1];
      let expression = convertExpressionToTau(temporalMatch[2]);
      
      switch (operator) {
        case 'always':
          return `always (${expression}).`;
        case 'sometimes':
          return `sometimes (${expression}).`;
        case 'eventually':
          return `<> (${expression}).`;
        case 'never':
          return `!(sometimes (${expression})).`;
        case 'next':
          return `X (${expression}).`;
      }
    }
  }
  
  // Pattern 7: Quantifiers
  if (input.match(/for\s+all|there\s+exists?|exist/)) {
    const quantMatch = input.match(/(for\s+all|there\s+exists?)\s+(.*?)\s+(?:such\s+)?that\s+(.*)/);
    if (quantMatch) {
      const quantType = quantMatch[1].includes('all') ? 'all' : 'ex';
      const variable = quantMatch[2].trim();
      const condition = convertConditionToTau(quantMatch[3]);
      return `{ ${quantType} ${variable} : ${condition} }.`;
    }
  }
  
  // Pattern 8: Rules with time notation
  if (input.match(/rule\s+\w+.*at\s+time/)) {
    const ruleMatch = input.match(/rule\s+(\w+)\s+at\s+time\s+(\d+|t)\s+(?:equals?|is)\s+(.*)/);
    if (ruleMatch) {
      const ruleName = ruleMatch[1];
      const time = ruleMatch[2];
      const expression = convertExpressionToTau(ruleMatch[3]);
      return `r ${ruleName}[${time}] = ${expression}.`;
    }
  }
  
  // Pattern 9: Boolean expressions
  if (input.match(/.*(?:and|or|not|implies).*/)) {
    let result = convertBooleanExpression(input);
    return result + '.';
  }
  
  // Default: treat as expression and add period
  return convertExpressionToTau(input) + '.';
}

// ===== Tau to Natural Language Translation =====

function translateTauToNaturalLanguage(tauCode) {
  let result = tauCode.trim();
  
  // Remove trailing period
  if (result.endsWith('.')) {
    result = result.slice(0, -1);
  }
  
  // Handle solve statements
  if (result.match(/^solve\s*{/)) {
    const solveMatch = result.match(/solve\s*{\s*([^:}]+)(?:\s*:\s*([^}]+))?\s*}/);
    if (solveMatch) {
      const variable = solveMatch[1].trim();
      const constraint = solveMatch[2]?.trim();
      if (constraint) {
        return `Solve for ${variable} such that ${convertTauConditionToNL(constraint)}.`;
      }
      return `Solve for ${variable}.`;
    }
  }
  
  // Handle type declarations
  if (result.match(/{\s*\w+\s*}\s*:\s*sbf/)) {
    const typeMatch = result.match(/{\s*(\w+)\s*}\s*:\s*sbf/);
    if (typeMatch) {
      return `Declare ${typeMatch[1]} as a stream boolean function.`;
    }
  }
  
  // Handle stream assignments
  if (result.match(/\w+\[.*?\]\s*:=/)) {
    const streamMatch = result.match(/(\w+)\[(.*?)\]\s*:=\s*(.*)/);
    if (streamMatch) {
      const streamName = streamMatch[1];
      const time = streamMatch[2];
      const value = convertTauExpressionToNL(streamMatch[3]);
      return `${streamName} at time ${time} equals ${value}.`;
    }
  }
  
  // Handle conditionals
  result = result.replace(/\((.*?)\)\s*\?\s*\((.*?)\)\s*:\s*\((.*?)\)/g, 
    (match, cond, then, else_) => {
      return `If ${convertTauConditionToNL(cond)}, then ${convertTauExpressionToNL(then)}, otherwise ${convertTauExpressionToNL(else_)}`;
    });
  
  // Handle temporal operators
  result = result.replace(/always\s*\((.*?)\)/g, 'It is always true that $1');
  result = result.replace(/sometimes\s*\((.*?)\)/g, 'Sometimes $1');
  result = result.replace(/<>\s*\((.*?)\)/g, 'Eventually $1');
  result = result.replace(/X\s*\((.*?)\)/g, 'In the next time step, $1');
  
  // Handle quantifiers
  result = result.replace(/{\s*all\s+(\w+)\s*:\s*(.*?)\s*}/g, 'For all $1 such that $2');
  result = result.replace(/{\s*ex\s+(\w+)\s*:\s*(.*?)\s*}/g, 'There exists $1 such that $2');
  
  // Convert operators
  result = convertTauOperatorsToNL(result);
  
  return result + '.';
}

// ===== CNL Translation Functions =====

function translateToCNL(text) {
  let input = text.toLowerCase().trim();
  
  // CNL uses more structured English
  if (input.includes('if') && input.includes('then')) {
    return `WHEN ${input.replace('if', '').replace('then', 'THEN')}`;
  }
  
  if (input.includes('equals') || input.includes('is')) {
    return input.replace(/equals?|is/g, 'IS DEFINED AS');
  }
  
  return `DEFINE: ${text}`;
}

function translateCNLToTau(cnl) {
  let result = cnl.trim();
  
  // Convert CNL keywords to Tau
  result = result.replace(/WHEN\s+(.*?)\s+THEN\s+(.*)/i, '($1) ? ($2) : 0');
  result = result.replace(/IS DEFINED AS/gi, ':=');
  result = result.replace(/DEFINE:\s*/i, '');
  
  return result + '.';
}

function translateTauToCNL(tau) {
  let result = tau.trim();
  if (result.endsWith('.')) result = result.slice(0, -1);
  
  // Convert Tau conditionals to CNL
  result = result.replace(/\((.*?)\)\s*\?\s*\((.*?)\)\s*:\s*\((.*?)\)/g, 
    'WHEN $1 THEN $2 OTHERWISE $3');
  
  // Convert assignments
  result = result.replace(/:=/g, 'IS DEFINED AS');
  
  return result;
}

function translateCNLToNaturalLanguage(cnl) {
  let result = cnl.trim();
  
  result = result.replace(/WHEN\s+(.*?)\s+THEN\s+(.*?)(?:\s+OTHERWISE\s+(.*))?/gi, 
    (match, cond, then, else_) => {
      if (else_) {
        return `If ${cond.toLowerCase()}, then ${then.toLowerCase()}, otherwise ${else_.toLowerCase()}`;
      }
      return `If ${cond.toLowerCase()}, then ${then.toLowerCase()}`;
    });
  
  result = result.replace(/IS DEFINED AS/gi, 'equals');
  result = result.replace(/DEFINE:\s*/gi, '');
  
  return result;
}

// ===== ILR Translation Functions =====

function translateToILR(text) {
  const input = text.toLowerCase().trim();
  
  // Create ILR structure
  const ilr = {
    type: 'statement',
    content: text,
    components: []
  };
  
  // Detect components
  if (input.includes('if') && input.includes('then')) {
    ilr.type = 'conditional';
    const match = input.match(/if\s+(.*?)\s+then\s+(.*?)(?:\s+else\s+(.*))?/);
    if (match) {
      ilr.components = [
        { type: 'condition', value: match[1] },
        { type: 'then', value: match[2] },
        { type: 'else', value: match[3] || 'null' }
      ];
    }
  } else if (input.match(/equals?|is|:=/)) {
    ilr.type = 'assignment';
    const match = input.match(/(.*?)(?:equals?|is|:=)(.*)/);
    if (match) {
      ilr.components = [
        { type: 'variable', value: match[1].trim() },
        { type: 'value', value: match[2].trim() }
      ];
    }
  }
  
  return JSON.stringify(ilr, null, 2);
}

function translateILRToTau(ilrJson) {
  try {
    const ilr = JSON.parse(ilrJson);
    
    if (ilr.type === 'conditional') {
      const condition = ilr.components.find(c => c.type === 'condition')?.value || '';
      const thenPart = ilr.components.find(c => c.type === 'then')?.value || '';
      const elsePart = ilr.components.find(c => c.type === 'else')?.value || '0';
      
      return `(${condition}) ? (${thenPart}) : (${elsePart}).`;
    } else if (ilr.type === 'assignment') {
      const variable = ilr.components.find(c => c.type === 'variable')?.value || '';
      const value = ilr.components.find(c => c.type === 'value')?.value || '';
      
      return `${variable} := ${value}.`;
    }
    
    return ilr.content + '.';
  } catch (e) {
    return ilrJson; // Return as-is if not valid JSON
  }
}

function translateTauToILR(tau) {
  const ilr = {
    type: 'tau_statement',
    original: tau,
    components: []
  };
  
  // Parse Tau syntax
  if (tau.match(/\((.*?)\)\s*\?\s*\((.*?)\)\s*:\s*\((.*?)\)/)) {
    ilr.type = 'conditional';
    const match = tau.match(/\((.*?)\)\s*\?\s*\((.*?)\)\s*:\s*\((.*?)\)/);
    ilr.components = [
      { type: 'condition', value: match[1] },
      { type: 'then', value: match[2] },
      { type: 'else', value: match[3] }
    ];
  } else if (tau.includes(':=')) {
    ilr.type = 'assignment';
    const parts = tau.split(':=');
    ilr.components = [
      { type: 'variable', value: parts[0].trim() },
      { type: 'value', value: parts[1].trim().replace('.', '') }
    ];
  }
  
  return JSON.stringify(ilr, null, 2);
}

function translateILRToNaturalLanguage(ilrJson) {
  try {
    const ilr = JSON.parse(ilrJson);
    
    if (ilr.type === 'conditional') {
      const condition = ilr.components.find(c => c.type === 'condition')?.value || '';
      const thenPart = ilr.components.find(c => c.type === 'then')?.value || '';
      const elsePart = ilr.components.find(c => c.type === 'else')?.value;
      
      if (elsePart && elsePart !== 'null') {
        return `If ${condition}, then ${thenPart}, else ${elsePart}.`;
      }
      return `If ${condition}, then ${thenPart}.`;
    } else if (ilr.type === 'assignment') {
      const variable = ilr.components.find(c => c.type === 'variable')?.value || '';
      const value = ilr.components.find(c => c.type === 'value')?.value || '';
      
      return `${variable} equals ${value}.`;
    }
    
    return ilr.content || ilr.original || ilrJson;
  } catch (e) {
    return ilrJson; // Return as-is if not valid JSON
  }
}

function translateCNLToILR(cnl) {
  return translateToILR(translateCNLToNaturalLanguage(cnl));
}

function translateILRToCNL(ilr) {
  return translateToCNL(translateILRToNaturalLanguage(ilr));
}

// ===== Helper Functions =====

function convertConditionToTau(condition) {
  let result = condition.trim();
  
  // Convert comparison operators to Tau syntax
  result = result.replace(/\bis\s+greater\s+than\s+or\s+equal\s+to\b/g, '>=');
  result = result.replace(/\bis\s+less\s+than\s+or\s+equal\s+to\b/g, '<=');
  result = result.replace(/\bis\s+greater\s+than\b/g, '>');
  result = result.replace(/\bis\s+less\s+than\b/g, '<');
  result = result.replace(/\bis\s+equal\s+to\b/g, '=');
  result = result.replace(/\bis\s+not\s+equal\s+to\b/g, '!=');
  result = result.replace(/\bdoes\s+not\s+equal\b/g, '!=');
  result = result.replace(/\bis\s+not\b/g, '!=');
  result = result.replace(/\bis\b/g, '=');
  result = result.replace(/\bequals?\b/g, '=');
  
  // Convert boolean operators
  result = convertBooleanOperators(result);
  
  return result;
}

function convertExpressionToTau(expression) {
  let result = expression.trim();
  
  // Convert comparisons
  result = convertConditionToTau(result);
  
  // Convert boolean values
  result = convertBooleanValues(result);
  
  // Convert special values
  result = result.replace(/\bnull\b/g, '0');
  result = result.replace(/\bempty\b/g, '0');
  result = result.replace(/\bundefined\b/g, '0');
  
  return result;
}

function convertBooleanValues(text) {
  let result = text;
  result = result.replace(/\btrue\b/g, '1');
  result = result.replace(/\bfalse\b/g, '0');
  result = result.replace(/\byes\b/g, '1');
  result = result.replace(/\bno\b/g, '0');
  result = result.replace(/\bon\b/g, '1');
  result = result.replace(/\boff\b/g, '0');
  return result;
}

function convertBooleanOperators(text) {
  let result = text;
  result = result.replace(/\band\b/g, '&&');
  result = result.replace(/\bor\b/g, '||');
  result = result.replace(/\bnot\b/g, '!');
  result = result.replace(/\bimplies\b/g, '=>');
  return result;
}

function convertBooleanExpression(text) {
  let result = text;
  
  // Handle implies specially
  if (result.includes('implies')) {
    result = result.replace(/\bimplies\b/g, '=>');
  }
  
  // Convert other boolean operators
  result = convertBooleanOperators(result);
  
  // Convert boolean values
  result = convertBooleanValues(result);
  
  return result;
}

function convertTauConditionToNL(condition) {
  let result = condition;
  
  // Convert operators back to natural language
  result = result.replace(/>=/g, ' is greater than or equal to ');
  result = result.replace(/<=/g, ' is less than or equal to ');
  result = result.replace(/>/g, ' is greater than ');
  result = result.replace(/</g, ' is less than ');
  result = result.replace(/!=/g, ' does not equal ');
  result = result.replace(/=/g, ' equals ');
  
  // Convert boolean operators
  result = convertTauOperatorsToNL(result);
  
  return result;
}

function convertTauExpressionToNL(expression) {
  let result = expression;
  
  // Convert boolean values
  result = result.replace(/\b1\b/g, 'true');
  result = result.replace(/\b0\b/g, 'false');
  
  // Convert operators
  result = convertTauOperatorsToNL(result);
  
  return result;
}

function convertTauOperatorsToNL(text) {
  let result = text;
  
  // Convert boolean operators
  result = result.replace(/&&/g, ' and ');
  result = result.replace(/\|\|/g, ' or ');
  result = result.replace(/!/g, 'not ');
  result = result.replace(/=>/g, ' implies ');
  
  // Convert complement operator
  result = result.replace(/(\w+)'/g, 'complement of $1');
  
  return result;
}