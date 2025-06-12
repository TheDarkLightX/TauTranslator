#!/usr/bin/env python3
"""
English to Tau Translator - Gracefully handles multiple parsers
Copyright: DarkLightX/Dana Edwards

Translates plain English to Tau code using the best available parser.
"""

import sys
from pathlib import Path
from typing import Optional, Tuple
import logging

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.unified.translators.base import TranslationDirection
from src.tau_translator_omega.core_engine.cnl_parser.cnl_parser import CNLParser
from src.tau_translator_omega.core_engine.tce_tau_translator import TCETauTranslator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnglishToTauTranslator:
    """Translates plain English to Tau code."""
    
    def __init__(self):
        self.cnl_parser = CNLParser()
        self.tau_translator = TCETauTranslator()
    
    def translate_english_to_tau(self, english: str) -> Tuple[bool, str, str]:
        """
        Translate English to Tau code.
        
        Returns: (success, tau_code, intermediate_tce)
        """
        # Step 1: Convert English to TCE format
        tce_text = self._english_to_tce(english)
        
        # Step 2: Parse TCE to AST
        try:
            ast = self.cnl_parser.parse(tce_text)
            if not ast:
                return False, "", tce_text
        except Exception as e:
            logger.error(f"Parse error: {e}")
            # Try alternative parsing strategies
            return self._try_alternative_parsing(english, tce_text)
        
        # Step 3: Translate AST to Tau
        try:
            result = self.tau_translator.translate(ast)
            if result.errors:
                logger.error(f"Translation errors: {result.errors}")
                return False, "", tce_text
            
            return True, result.tau_code, tce_text
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return False, "", tce_text
    
    def _english_to_tce(self, english: str) -> str:
        """Convert English to TCE format."""
        # Normalize input
        text = english.strip().lower()
        
        # Simple mappings for common patterns
        mappings = {
            # Mathematical
            " plus ": " + ",
            " minus ": " - ",
            " times ": " * ",
            " divided by ": " / ",
            " mod ": " modulo ",
            
            # Comparisons
            " is greater than ": " > ",
            " is less than ": " < ",
            " is at least ": " >= ",
            " is at most ": " <= ",
            " equals ": " = ",
            " is equal to ": " = ",
            " is not equal to ": " != ",
            " is ": " = ",
            
            # Logical
            " and ": " and ",
            " or ": " or ",
            " not ": " not ",
            
            # Quantifiers
            "for all ": "for all ",
            "for every ": "for all ",
            "there exists ": "there exists ",
            "exists ": "there exists ",
            
            # Temporal
            "always ": "always ",
            "sometimes ": "sometimes ",
            "eventually ": "sometimes ",
        }
        
        # Apply mappings
        for eng, tce in mappings.items():
            text = text.replace(eng, tce)
        
        # Ensure ends with period
        if not text.endswith('.'):
            text += '.'
        
        return text
    
    def _try_alternative_parsing(self, english: str, tce_text: str) -> Tuple[bool, str, str]:
        """Try alternative parsing strategies when main parser fails."""
        
        # Strategy 1: Direct pattern matching for simple cases
        text = english.strip().lower()
        
        # Handle simple variable assignments
        if " equals " in text or " is " in text:
            parts = text.replace(" equals ", " = ").replace(" is ", " = ").split(" = ")
            if len(parts) == 2:
                var = parts[0].strip()
                val = parts[1].strip()
                return True, f"{var} = {val}", tce_text
        
        # Handle simple boolean operations
        if " and " in text:
            parts = text.split(" and ")
            if len(parts) == 2:
                return True, f"{parts[0].strip()} & {parts[1].strip()}", tce_text
        
        if " or " in text:
            parts = text.split(" or ")
            if len(parts) == 2:
                return True, f"{parts[0].strip()} | {parts[1].strip()}", tce_text
        
        if text.startswith("not "):
            operand = text[4:].strip()
            return True, f"~{operand}", tce_text
        
        # Handle comparisons
        comparison_ops = {
            " > ": " > ",
            " < ": " < ",
            " >= ": " >= ",
            " <= ": " <= ",
        }
        
        for op_text, op_symbol in comparison_ops.items():
            if op_text in text:
                parts = text.split(op_text)
                if len(parts) == 2:
                    return True, f"{parts[0].strip()} {op_symbol} {parts[1].strip()}", tce_text
        
        # Handle quantifiers
        if text.startswith("for all "):
            rest = text[8:].strip()
            if ", " in rest:
                var, condition = rest.split(", ", 1)
                return True, f"{{all {var}}} ({condition})", tce_text
        
        if text.startswith("there exists "):
            rest = text[13:].strip()
            if " such that " in rest:
                var, condition = rest.split(" such that ", 1)
                return True, f"{{ex {var}}} ({condition})", tce_text
        
        # If all else fails, return the original
        return False, "", tce_text


def main():
    """Interactive English to Tau translator."""
    translator = EnglishToTauTranslator()
    
    print("=== English to Tau Translator ===")
    print("Enter English sentences to translate to Tau.")
    print("Type 'quit' to exit.\n")
    
    while True:
        english = input("English> ").strip()
        
        if english.lower() in ['quit', 'exit', 'q']:
            break
        
        if not english:
            continue
        
        success, tau, tce = translator.translate_english_to_tau(english)
        
        print(f"TCE:     {tce}")
        if success:
            print(f"Tau:     {tau}")
        else:
            print("Tau:     [Translation failed]")
        print()


if __name__ == "__main__":
    # Run some test cases
    test_cases = [
        "x equals 5",
        "x and y",
        "not p",
        "x is greater than 10",
        "for all x, x equals x",
        "there exists y such that y is prime",
    ]
    
    translator = EnglishToTauTranslator()
    
    print("=== Test Cases ===\n")
    for english in test_cases:
        success, tau, tce = translator.translate_english_to_tau(english)
        print(f"English: {english}")
        print(f"TCE:     {tce}")
        print(f"Tau:     {tau if success else '[Failed]'}")
        print()
    
    print("\n" + "="*50 + "\n")
    
    # Run interactive mode
    main()