#!/usr/bin/env node

/**
 * Test Script: User Grammar Input Capability
 * ===========================================
 * 
 * This script tests the ability for users to:
 * 1. Upload their own grammar files
 * 2. Set custom grammars as active
 * 3. Use custom grammars for translation validation
 * 4. Manage multiple grammar files
 */

const fs = require('fs');
const path = require('path');
const FormData = require('form-data');

const API_BASE = 'http://localhost:3000/api';

// Test grammar files to upload (based on real Tau language specifications)
const TEST_GRAMMARS = {
  'tau_logic.tgf': `
# Tau Logic Grammar - Based on official Tau language specification
# Supports logical formulas, constraints, and temporal operators

@directive: trim_terminals.
@directive: inline_char_classes.

# Main entry points
main       => wff | tau_rec | constraint .
wff        => wff_equiv .
wff_equiv  => wff_impl ( '<->' wff_impl )* .
wff_impl   => wff_or ( '->' wff_or )* .
wff_or     => wff_and ( '||' wff_and )* .
wff_and    => wff_neg ( '&&' wff_neg )* .
wff_neg    => '!' wff_neg | wff_factor .
wff_factor => '(' wff ')' | 'always' wff | 'sometimes' wff | 'ex' variable ',' wff | 'all' variable ',' wff | constraint .

# Constraints and comparisons
constraint => expr rel_op expr .
rel_op     => '=' | '!=' | '<' | '<=' | '>' | '>=' .
expr       => expr '+' term | expr '-' term | term .
term       => term '*' factor | term '/' factor | factor .
factor     => '(' expr ')' | variable | constant .

# Variables and constants
variable   => alpha (alnum | '_')* .
constant   => digit+ .
tau_rec    => variable '(' tau_rec_args ')' ':-' wff .
tau_rec_args => variable (',' variable)* | null .

# Character classes
alpha      => [a-zA-Z] .
digit      => [0-9] .
alnum      => [a-zA-Z0-9] .
`,
  
  'sbf_formula.tgf': `
# SBF (Satisfiability Bit Formula) Grammar
# For parsing boolean formulas with bit-level operations

@directive: trim_terminals.

start      => wff | '1' | '0' .
wff        => wff '|' wff | wff '^' wff | wff '+' wff | wff '&' wff | wff wff | '\'' wff | '(' wff ')' | variable .
variable   => (alpha (alnum | '_')*) | (alpha digit*) .

# Character classes
alpha      => [a-zA-Z] .
digit      => [0-9] .
alnum      => [a-zA-Z0-9] .
`,

  'temporal_cnl.ebnf': `
(* Extended Backus-Naur Form for Temporal CNL *)
(* Based on common temporal logic patterns *)

temporal_statement ::= temporal_expr "."
temporal_expr      ::= always_expr | eventually_expr | until_expr | logical_expr

always_expr        ::= "always" "(" logical_expr ")"
eventually_expr    ::= "eventually" "(" logical_expr ")"
until_expr         ::= logical_expr "until" logical_expr

logical_expr       ::= conjunction | disjunction | negation | atomic_expr
conjunction        ::= logical_expr "and" logical_expr
disjunction        ::= logical_expr "or" logical_expr  
negation          ::= "not" logical_expr
atomic_expr       ::= comparison | predicate | "(" logical_expr ")"

comparison        ::= term comparison_op term
comparison_op     ::= "equals" | "is greater than" | "is less than" | 
                      "is greater than or equal to" | "is less than or equal to"

predicate         ::= identifier "(" term_list? ")"
term_list         ::= term ("," term)*
term              ::= identifier | number | string
identifier        ::= letter (letter | digit | "_")*
number            ::= digit+
string            ::= '"' character* '"'
letter            ::= "a" | "b" | "c" | "d" | "e" | "f" | "g" | "h" | "i" | "j" | 
                      "k" | "l" | "m" | "n" | "o" | "p" | "q" | "r" | "s" | "t" |
                      "u" | "v" | "w" | "x" | "y" | "z" | "A" | "B" | "C" | "D" |
                      "E" | "F" | "G" | "H" | "I" | "J" | "K" | "L" | "M" | "N" |
                      "O" | "P" | "Q" | "R" | "S" | "T" | "U" | "V" | "W" | "X" |
                      "Y" | "Z"
digit             ::= "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"
character         ::= letter | digit | " " | "!" | "@" | "#" | "$" | "%" | "^" | 
                      "&" | "*" | "(" | ")" | "-" | "+" | "=" | "[" | "]" | "{" | 
                      "}" | "|" | "\\" | ":" | ";" | "'" | "<" | ">" | "," | "." | 
                      "/" | "?"
`,

  'user_grammar_sample.json': `{
  "name": "User Custom Grammar",
  "version": "1.0",
  "description": "Sample user-defined grammar for domain-specific language",
  "format": "tau_compatible",
  "rules": {
    "entry_point": "system_spec",
    "system_spec": ["component_def+"],
    "component_def": ["'component' identifier '{' property_list '}'"],
    "property_list": ["property*"],
    "property": ["identifier ':' value ';'"],
    "value": ["string | number | boolean"],
    "string": ["'\"' character* '\"'"],
    "number": ["digit+ ('.' digit+)?"],
    "boolean": ["'true' | 'false'"],
    "identifier": ["letter (letter | digit | '_')*"]
  },
  "terminals": {
    "letter": "[a-zA-Z]",
    "digit": "[0-9]",
    "character": "[^\"\\\\n]"
  }
}`
};

class GrammarInputTester {
  constructor() {
    this.testResults = [];
    this.uploadedFiles = [];
  }

  log(message, level = 'INFO') {
    const timestamp = new Date().toISOString();
    const logMessage = `[${timestamp}] ${level}: ${message}`;
    console.log(logMessage);
    this.testResults.push({ timestamp, level, message });
  }

  async makeRequest(url, options = {}) {
    try {
      const fetch = (await import('node-fetch')).default;
      const response = await fetch(url, options);
      const data = await response.json();
      return { success: response.ok, status: response.status, data };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  async createTestGrammarFiles() {
    this.log('Creating test grammar files...');
    const tempDir = path.join(__dirname, 'test_grammars');
    
    if (!fs.existsSync(tempDir)) {
      fs.mkdirSync(tempDir, { recursive: true });
    }

    const createdFiles = [];
    for (const [filename, content] of Object.entries(TEST_GRAMMARS)) {
      const filePath = path.join(tempDir, filename);
      fs.writeFileSync(filePath, content);
      createdFiles.push(filePath);
      this.log(`Created test file: ${filename}`);
    }

    return createdFiles;
  }

  async testGrammarFileUpload() {
    this.log('=== Testing Grammar File Upload ===');
    
    const testFiles = await this.createTestGrammarFiles();
    let uploadSuccessCount = 0;

    for (const filePath of testFiles) {
      const filename = path.basename(filePath);
      this.log(`Uploading ${filename}...`);

      try {
        const formData = new FormData();
        formData.append('files', fs.createReadStream(filePath), filename);
        
        const result = await this.makeRequest(`${API_BASE}/grammar-files`, {
          method: 'POST',
          body: formData,
          headers: formData.getHeaders()
        });

        if (result.success) {
          this.log(`✅ Successfully uploaded ${filename}`, 'SUCCESS');
          uploadSuccessCount++;
          if (result.data.files) {
            this.uploadedFiles.push(...result.data.files);
          }
        } else {
          this.log(`❌ Failed to upload ${filename}: ${result.data?.message || result.error}`, 'ERROR');
        }
      } catch (error) {
        this.log(`❌ Exception uploading ${filename}: ${error.message}`, 'ERROR');
      }
    }

    this.log(`Upload test completed: ${uploadSuccessCount}/${testFiles.length} files uploaded successfully`);
    return uploadSuccessCount === testFiles.length;
  }

  async testGrammarFileList() {
    this.log('=== Testing Grammar File Listing ===');
    
    const result = await this.makeRequest(`${API_BASE}/grammar-files`);
    
    if (result.success) {
      const files = result.data;
      this.log(`✅ Retrieved ${files.length} grammar files`, 'SUCCESS');
      
      files.forEach(file => {
        this.log(`  - ${file.originalName} (${file.type}) - ${file.exists ? 'Available' : 'Missing'}`);
      });
      
      return files.length > 0;
    } else {
      this.log(`❌ Failed to list grammar files: ${result.data?.message || result.error}`, 'ERROR');
      return false;
    }
  }

  async testSetActiveGrammar() {
    this.log('=== Testing Set Active Grammar ===');
    
    if (this.uploadedFiles.length === 0) {
      this.log('❌ No uploaded files to test with', 'ERROR');
      return false;
    }

    const testFile = this.uploadedFiles[0];
    this.log(`Setting ${testFile.originalName} as active grammar...`);

    const result = await this.makeRequest(`${API_BASE}/grammar-files?id=${testFile.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ isActive: true })
    });

    if (result.success) {
      this.log(`✅ Successfully set ${testFile.originalName} as active`, 'SUCCESS');
      return true;
    } else {
      this.log(`❌ Failed to set active grammar: ${result.data?.message || result.error}`, 'ERROR');
      return false;
    }
  }

  async testGrammarIntegration() {
    this.log('=== Testing Grammar Integration ===');
    
    // Test getting active grammar info
    const grammarResult = await this.makeRequest(`${API_BASE}/grammar-integration`);
    
    if (grammarResult.success && grammarResult.data.hasActiveGrammar) {
      const grammar = grammarResult.data.grammar;
      this.log(`✅ Active grammar found: ${grammar.originalName} (${grammar.type})`, 'SUCCESS');
      
      // Test input validation against the grammar (Tau-specific examples)
      const testInputs = [
        'always (x > y)',
        'ex x, (x = 5) && (x < 10)',
        'all x, x != 0 -> (y / x) > 0',
        'sometimes (temperature > 25)',
        'p(x) :- (x > 0) && (x < 100)',
        'x | y & !z',
        'component MySystem { name: "test"; active: true; }'
      ];

      for (const input of testInputs) {
        this.log(`Testing validation for: "${input}"`);
        
        const validationResult = await this.makeRequest(`${API_BASE}/grammar-integration`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ input })
        });

        if (validationResult.success) {
          const validation = validationResult.data.validation;
          this.log(`  ${validation.valid ? '✅' : '❌'} ${validation.message}`);
        } else {
          this.log(`  ❌ Validation failed: ${validationResult.error}`, 'ERROR');
        }
      }
      
      return true;
    } else {
      this.log(`❌ No active grammar found or error: ${grammarResult.data?.message || grammarResult.error}`, 'ERROR');
      return false;
    }
  }

  async testGrammarFileManagement() {
    this.log('=== Testing Grammar File Management ===');
    
    if (this.uploadedFiles.length === 0) {
      this.log('❌ No uploaded files to manage', 'ERROR');
      return false;
    }

    // Test updating file description
    const testFile = this.uploadedFiles[0];
    const updateResult = await this.makeRequest(`${API_BASE}/grammar-files?id=${testFile.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        description: 'Test grammar file for automated testing' 
      })
    });

    if (updateResult.success) {
      this.log(`✅ Successfully updated file description`, 'SUCCESS');
    } else {
      this.log(`❌ Failed to update file: ${updateResult.data?.message || updateResult.error}`, 'ERROR');
      return false;
    }

    return true;
  }

  async testTranslationWithCustomGrammar() {
    this.log('=== Testing Translation with Custom Grammar ===');
    
    const testTranslations = [
      {
        sourceText: 'x is always greater than y',
        sourceLangKey: 'PLAIN_ENGLISH',
        targetLangKey: 'TAU',
        sourceLangLabel: 'Plain English',
        targetLangLabel: 'Tau Language Code'
      },
      {
        sourceText: 'always (temperature > 25)',
        sourceLangKey: 'TAU',
        targetLangKey: 'PLAIN_ENGLISH',
        sourceLangLabel: 'Tau Language Code',
        targetLangLabel: 'Plain English'
      }
    ];

    let successCount = 0;
    for (const translation of testTranslations) {
      this.log(`Testing translation: "${translation.sourceText}" (${translation.sourceLangKey} → ${translation.targetLangKey})`);
      
      const result = await this.makeRequest(`${API_BASE}/translate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(translation)
      });

      if (result.success) {
        const translated = result.data.translatedText;
        this.log(`  ✅ Translation result: "${translated}"`, 'SUCCESS');
        successCount++;
      } else {
        this.log(`  ❌ Translation failed: ${result.data?.message || result.error}`, 'ERROR');
      }
    }

    return successCount === testTranslations.length;
  }

  async cleanup() {
    this.log('=== Cleaning Up ===');
    
    // Clean up uploaded files
    for (const file of this.uploadedFiles) {
      try {
        const result = await this.makeRequest(`${API_BASE}/grammar-files?id=${file.id}`, {
          method: 'DELETE'
        });
        
        if (result.success) {
          this.log(`✅ Deleted ${file.originalName}`, 'SUCCESS');
        } else {
          this.log(`❌ Failed to delete ${file.originalName}`, 'ERROR');
        }
      } catch (error) {
        this.log(`❌ Exception deleting ${file.originalName}: ${error.message}`, 'ERROR');
      }
    }

    // Clean up test files
    const tempDir = path.join(__dirname, 'test_grammars');
    if (fs.existsSync(tempDir)) {
      fs.rmSync(tempDir, { recursive: true, force: true });
      this.log('Removed temporary test files');
    }
  }

  async runAllTests() {
    this.log('🚀 Starting Grammar Input Capability Tests');
    
    const testResults = {};
    
    try {
      testResults.upload = await this.testGrammarFileUpload();
      testResults.list = await this.testGrammarFileList();
      testResults.setActive = await this.testSetActiveGrammar();
      testResults.integration = await this.testGrammarIntegration();
      testResults.management = await this.testGrammarFileManagement();
      testResults.translation = await this.testTranslationWithCustomGrammar();
      
      // Generate test report
      this.generateTestReport(testResults);
      
    } catch (error) {
      this.log(`❌ Test suite failed with exception: ${error.message}`, 'ERROR');
    } finally {
      await this.cleanup();
    }
  }

  generateTestReport(testResults) {
    this.log('=== TEST REPORT ===');
    
    const totalTests = Object.keys(testResults).length;
    const passedTests = Object.values(testResults).filter(result => result === true).length;
    
    this.log(`Tests Passed: ${passedTests}/${totalTests}`);
    this.log('');
    
    Object.entries(testResults).forEach(([testName, passed]) => {
      this.log(`${passed ? '✅' : '❌'} ${testName.toUpperCase()}: ${passed ? 'PASSED' : 'FAILED'}`);
    });
    
    this.log('');
    
    if (passedTests === totalTests) {
      this.log('🎉 ALL TESTS PASSED! User grammar input capability is working correctly.', 'SUCCESS');
    } else {
      this.log(`⚠️  ${totalTests - passedTests} test(s) failed. Grammar input capability may have issues.`, 'WARNING');
    }

    // Save detailed report
    const reportPath = path.join(__dirname, 'grammar_input_test_report.json');
    fs.writeFileSync(reportPath, JSON.stringify({
      timestamp: new Date().toISOString(),
      summary: {
        totalTests,
        passedTests,
        failedTests: totalTests - passedTests,
        success: passedTests === totalTests
      },
      results: testResults,
      logs: this.testResults
    }, null, 2));
    
    this.log(`📄 Detailed report saved to: ${reportPath}`);
  }
}

// Check if PWA server is running before starting tests
async function checkServerStatus() {
  try {
    const fetch = (await import('node-fetch')).default;
    const response = await fetch(`${API_BASE}/grammar-files`);
    return response.status === 200 || response.status === 404; // Either working or just no files yet
  } catch (error) {
    return false;
  }
}

// Main execution
async function main() {
  console.log('🔍 Checking if PWA server is running...');
  
  const serverRunning = await checkServerStatus();
  if (!serverRunning) {
    console.log('❌ PWA server is not running on localhost:3000');
    console.log('Please start the server with: npm run dev');
    process.exit(1);
  }
  
  console.log('✅ PWA server detected');
  
  const tester = new GrammarInputTester();
  await tester.runAllTests();
}

if (require.main === module) {
  main().catch(console.error);
}