#!/usr/bin/env python3
"""
Complete ILR-Integrated Translation Pipeline
Copyright: DarkLightX/Dana Edwards

Natural Language → ILR → TCE → Tau using TDD-developed components.
Following craftsmanship principles with methods ≤10 lines.
"""

import sys
from pathlib import Path
from typing import Tuple
import logging
from ..core.result_enhanced import Success, Failure

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.unified.domain.text_to_ilr_service import TextToILRService
from backend.unified.domain.nlp_translation_service import NLPTranslationService
from backend.unified.domain.nlp_types import NaturalLanguageText
from backend.unified.domain.ilr_to_tce_transformer import ILRToTCETransformer
from backend.unified.tce_to_tau_wrapper import TCEToTauWrapper
from src.tau_translator_omega.core_engine.parsers.cnl_parser.parser import CNLParser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ILRIntegratedTranslator:
    """Complete NL→ILR→TCE→Tau pipeline with semantic structure."""
    
    def __init__(self):
        self._nlp_service = NLPTranslationService()
        self._ilr_generator = TextToILRService()
        self._ilr_to_tce = ILRToTCETransformer()
        self._tce_parser = CNLParser()
        self._tau_translator = TCEToTauWrapper()
    
    def translate(self, english: str) -> Tuple[bool, str, str, dict]:
        """Translate Natural Language to Tau via ILR."""
        metadata = self._create_metadata()
        
        pipeline_result = (self._execute_nl_step(english, metadata)
                          .flat_map(lambda nl: self._execute_ilr_step(nl, metadata))
                          .flat_map(lambda ilr: self._execute_tce_step(ilr, metadata))
                          .flat_map(lambda tce: self._execute_tau_step(tce, metadata)))
        
        return self._format_final_result(pipeline_result, metadata)
    
    def _process_natural_language(self, text: str) -> Tuple[bool, str, dict]:
        """Process natural language input."""
        try:
            nl_text = NaturalLanguageText(text)
            nlp_result = self._nlp_service.translate_nl_to_tce(nl_text)
            
            if nlp_result.success:
                return True, nlp_result.output_text or "", {
                    "step": "NL_Processing",
                    "input": text,
                    "output": nlp_result.output_text,
                    "success": True
                }
            else:
                return False, "", {
                    "step": "NL_Processing", 
                    "error": nlp_result.error_message,
                    "success": False
                }
        except Exception as e:
            return False, "", {"step": "NL_Processing", "error": str(e), "success": False}
    
    def _generate_ilr_structure(self, text: str) -> Tuple[bool, object, dict]:
        """Generate ILR semantic structure."""
        try:
            ilr_result = self._ilr_generator.convert_text_to_ilr(text)
            
            if isinstance(ilr_result, Success):
                ilr_node = ilr_result.unwrap()
                return True, ilr_node, {
                    "step": "ILR_Generation",
                    "input": text,
                    "ilr_type": type(ilr_node).__name__,
                    "semantic_structure": str(ilr_node),
                    "success": True
                }
            else:
                return False, None, {
                    "step": "ILR_Generation",
                    "error": ilr_result.failure(),
                    "success": False
                }
        except Exception as e:
            return False, None, {"step": "ILR_Generation", "error": str(e), "success": False}
    
    def _transform_to_tce(self, ilr_node) -> Tuple[bool, list, dict]:
        """Transform ILR to TCE statements."""
        try:
            tce_result = self._ilr_to_tce.transform_ilr_to_tce_async(ilr_node)
            
            if isinstance(tce_result, Success):
                tce_statements = tce_result.unwrap()
                return True, tce_statements, {
                    "step": "ILR_to_TCE",
                    "tce_count": len(tce_statements),
                    "tce_patterns": [stmt.pattern for stmt in tce_statements],
                    "success": True
                }
            else:
                return False, [], {
                    "step": "ILR_to_TCE",
                    "error": tce_result.failure(),
                    "success": False
                }
        except Exception as e:
            return False, [], {"step": "ILR_to_TCE", "error": str(e), "success": False}
    
    def _translate_to_tau(self, tce_statements: list) -> Tuple[bool, str, dict]:
        """Translate TCE to Tau code."""
        try:
            if not tce_statements:
                return False, "", {"step": "TCE_to_Tau", "error": "No TCE statements", "success": False}
            
            # Format first TCE statement for parsing
            tce_text = tce_statements[0].pattern
            if not tce_text.endswith('.'):
                tce_text += '.'
            
            # Parse and translate
            ast = self._tce_parser.parse(tce_text)
            tau_result = self._tau_translator.translate(ast)
            
            return not bool(tau_result.errors), tau_result.tau_code, {
                "step": "TCE_to_Tau",
                "tce_input": tce_text,
                "tau_output": tau_result.tau_code,
                "errors": tau_result.errors,
                "success": not bool(tau_result.errors)
            }
        except Exception as e:
            return False, "", {"step": "TCE_to_Tau", "error": str(e), "success": False}
    
    def _format_tce_for_display(self, tce_statements: list) -> str:
        """Format TCE statements for display."""
        if not tce_statements:
            return ""
        
        patterns = []
        for stmt in tce_statements:
            pattern = stmt.pattern
            if not pattern.endswith('.'):
                pattern += '.'
            patterns.append(pattern)
        
        return " ".join(patterns)


def main():
    """Interactive ILR-integrated translator."""
    translator = ILRIntegratedTranslator()
    
    print("=== ILR-Integrated English to Tau Translator ===")
    print("Pipeline: Natural Language → ILR → TCE → Tau")
    print("Type 'help' for examples or 'quit' to exit.\n")
    
    examples = [
        "x equals 5",
        "temperature is 25",
        "x and y", 
        "x is greater than 10",
        "if x then y",
        "for all x, x equals x",
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
        
        success, tau, tce, metadata = translator.translate(text)
        
        print(f"ILR:     {metadata['steps'][1]['ilr_type'] if len(metadata['steps']) > 1 else 'Failed'}")
        print(f"TCE:     {tce}")
        print(f"Tau:     {tau if success else '[Translation failed]'}")
        
        if not success:
            print("Errors:")
            for step in metadata['steps']:
                if not step.get('success', True):
                    print(f"  {step['step']}: {step.get('error', 'Unknown error')}")
        print()


if __name__ == "__main__":
    # Test with examples first
    translator = ILRIntegratedTranslator()
    
    test_cases = [
        "x equals 5",
        "x and y",
        "x is greater than 10",
        "temperature is 25",
    ]
    
    print("=== ILR Pipeline Test Cases ===\n")
    success_count = 0
    
    for english in test_cases:
        print(f"English: {english}")
        success, tau, tce, metadata = translator.translate(english)
        
        print(f"ILR:     {metadata['steps'][1]['ilr_type'] if len(metadata['steps']) > 1 else 'Failed'}")
        print(f"TCE:     {tce}")
        print(f"Tau:     {tau if success else '[Failed]'}")
        print(f"Success: {success}")
        
        if success:
            success_count += 1
        print()
    
    print(f"Success rate: {success_count}/{len(test_cases)}")
    print("=" * 50 + "\n")
    
    # Run interactive mode
    main()