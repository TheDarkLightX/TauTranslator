#!/usr/bin/env python3
"""
Integrated English to Tau Translator
Copyright: DarkLightX/Dana Edwards

Uses the TDD-developed NL to TCE translator with existing TCE to Tau translator.
"""

import sys
from pathlib import Path
from typing import Tuple
import logging

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.unified.domain.nl_to_tce_translator import NaturalLanguageToTCETranslator
from src.tau_translator_omega.core_engine.parsers.cnl_parser.parser import CNLParser
from backend.unified.tce_to_tau_wrapper import TCEToTauWrapper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntegratedEnglishToTauTranslator:
    """Integrated translator using all components."""
    
    def __init__(self):
        self.nl_to_tce = NaturalLanguageToTCETranslator()
        self.tce_parser = CNLParser()
        self.tce_to_tau = TCEToTauWrapper()
    
    def translate(self, english: str) -> Tuple[bool, str, str]:
        """
        Translate English to Tau.
        Returns: (success, tau_code, tce_intermediate)
        """
        # Step 1: English to TCE
        tce = self.nl_to_tce.translate_to_tce(english)
        logger.info(f"TCE: {tce}")
        
        # Step 2: Parse TCE to AST
        try:
            ast = self.tce_parser.parse(tce)
            if not ast:
                logger.error("Failed to parse TCE")
                return False, "", tce
        except Exception as e:
            logger.error(f"Parse error: {e}")
            # Try fallback
            return self._try_direct_translation(english, tce)
        
        # Step 3: AST to Tau
        try:
            result = self.tce_to_tau.translate(ast)
            if result.errors:
                logger.error(f"Translation errors: {result.errors}")
                return False, "", tce
            
            return True, result.tau_code, tce
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return False, "", tce
    
    def _try_direct_translation(self, english: str, tce: str) -> Tuple[bool, str, str]:
        """Fallback for simple cases."""
        # Remove trailing period from TCE for direct translation
        tce_clean = tce.rstrip('.')
        
        # Map common TCE patterns to Tau (order matters!)
        tau = tce_clean
        
        # Handle inequalities FIRST (before 'not' removal)
        tau = tau.replace(' not = ', ' != ')
        tau = tau.replace('not = ', '!= ')
        tau = tau.replace('not equals', '!=')
        
        # Handle other patterns
        tau = tau.replace(' and ', ' & ')
        tau = tau.replace(' or ', ' | ')
        tau = tau.replace('xor', '^')
        tau = tau.replace(' = ', ' = ')
        tau = tau.replace(' > ', ' > ')
        tau = tau.replace(' < ', ' < ')
        tau = tau.replace(' >= ', ' >= ')
        tau = tau.replace(' <= ', ' <= ')
        
        # Handle complement (NOT) operator with prime notation
        import re
        # Pattern: "not x" -> "x'" (handle standalone not)
        tau = re.sub(r'\bnot\s+(\w+)\b', r"\1'", tau)
        # Pattern: "x complement" -> "x'"
        tau = re.sub(r'(\w+)\s+complement\b', r"\1'", tau)
        # Handle remaining "not" without following word
        tau = tau.replace('not', "'")
        
        # Handle function definitions
        tau = re.sub(r'(\w+)\s+of\s+([^=]+)\s*=\s*defined\s+as\s+(.+)', r'\1(\2) := \3', tau)
        
        # Handle temporal indexing: "at time t" -> "[t]"
        tau = re.sub(r'(\w+)\s+at\s+time\s+(\w+)', r'\1[\2]', tau)
        
        # Handle solver commands
        if tau.startswith('solve '):
            # "solve x = 0 and y = 0" -> "solve x = 0 && y = 0"
            tau = tau.replace(' and ', ' && ')
        
        # Handle stream processing rules
        if tau.startswith('rule '):
            # "rule o1[t] = x" -> "r o1[t] = x"
            tau = tau.replace('rule ', 'r ', 1)
        
        # Handle quantifiers BEFORE other temporal processing
        tau = re.sub(r'for\s+all\s+(\w+),\s*(.+)', r'all \1 (\2)', tau)
        tau = re.sub(r'exists\s+(\w+)\s+such\s+that\s+(.+)', r'ex \1 (\2)', tau)
        
        # Also handle simple quantifiers without comma
        tau = re.sub(r'for\s+all\s+(\w+)\s+(.+)', r'all \1 (\2)', tau)
        
        # Handle implications: "implies" -> "->"
        tau = tau.replace(' implies ', ' -> ')
        
        # Handle equivalence: "if and only if" -> "<->"
        tau = tau.replace(' if  only if ', ' <-> ')
        
        # Handle temporal logic with better syntax
        if tau.startswith('always ') and '[t]' in tau:
            # "always x[t]" format - keep as is
            pass
        elif tau.startswith('always '):
            # "always x at time t" -> "always x[t]" 
            tau = re.sub(r'always\s+(\w+)', r'always \1[t]', tau)
        
        if tau.startswith('sometimes ') and '[t]' in tau:
            # "sometimes y[t]" format - keep as is
            pass
        elif tau.startswith('sometimes '):
            # "sometimes y at time t" -> "sometimes y[t]"
            tau = re.sub(r'sometimes\s+(\w+)', r'sometimes \1[t]', tau)
        
        # Handle arithmetic operations in temporal context
        tau = re.sub(r'(\w+)\[(\w+)\]\s*-\s*(\d+)', r'\1[\2-\3]', tau)
        
        # Add parentheses for simple expressions
        if ' & ' in tau or ' | ' in tau:
            tau = f"({tau})"
        
        return True, tau, tce


def main():
    """Interactive translator."""
    translator = IntegratedEnglishToTauTranslator()
    
    print("=== English to Tau Translator (Integrated) ===")
    print("Type 'help' for examples or 'quit' to exit.\n")
    
    examples = [
        "x equals 5",
        "temperature is 25",
        "x and y",
        "not p",
        "x is greater than 10",
        "if x then y",
        "for all x, x equals x",
        "there exists x such that x is prime",
        "always system is secure",
        "all users must have valid passwords",
    ]
    
    while True:
        text = input("English> ").strip()
        
        if text.lower() == 'quit':
            break
        elif text.lower() == 'help':
            print("\nExamples:")
            for ex in examples:
                print(f"  {ex}")
            print()
            continue
        elif not text:
            continue
        
        success, tau, tce = translator.translate(text)
        
        print(f"TCE: {tce}")
        if success:
            print(f"Tau: {tau}")
        else:
            print("Tau: [Translation failed]")
        print()


if __name__ == "__main__":
    # Test with examples
    translator = IntegratedEnglishToTauTranslator()
    
    test_cases = [
        "x equals 5",
        "x and y",
        "not p",
        "x is greater than 10",
        "for all x, x equals x",
        "if temperature is greater than 30 then cooling is on",
    ]
    
    print("=== Test Cases ===\n")
    success_count = 0
    
    for english in test_cases:
        print(f"English: {english}")
        success, tau, tce = translator.translate(english)
        print(f"TCE:     {tce}")
        print(f"Tau:     {tau if success else '[Failed]'}")
        if success:
            success_count += 1
        print()
    
    print(f"Success rate: {success_count}/{len(test_cases)}")
    print("\n" + "="*50 + "\n")
    
    # Run interactive mode
    main()