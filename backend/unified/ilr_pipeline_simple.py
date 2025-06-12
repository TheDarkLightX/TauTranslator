#!/usr/bin/env python3
"""
ILR Pipeline (IDP Simple)
Copyright: DarkLightX/Dana Edwards

Follows IDP with ≤10 line methods while keeping the working pipeline logic.
"""

import sys
from pathlib import Path
from typing import Tuple, Dict, Any
from dataclasses import dataclass

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.unified.domain.text_to_ilr_service import TextToILRService
from backend.unified.domain.nlp_translation_service import NLPTranslationService
from backend.unified.domain.nlp_types import NaturalLanguageText
from backend.unified.domain.ilr_to_tce_transformer import ILRToTCETransformer
from backend.unified.tce_to_tau_wrapper import TCEToTauWrapper
from src.tau_translator_omega.core_engine.cnl_parser.cnl_parser import CNLParser
from returns.result import Success, Failure


@dataclass(frozen=True)
class TranslationResult:
    """IDP domain type for translation results."""
    success: bool
    tau_code: str
    tce_text: str
    ilr_type: str
    metadata: Dict[str, Any]


class ILRPipelineSimple:
    """ILR pipeline with IDP principles and ≤10 line methods."""
    
    def __init__(self):
        self._init_services()
    
    def _init_services(self):
        """Initialize translation services."""
        self._nlp_service = NLPTranslationService()
        self._ilr_generator = TextToILRService()
        self._ilr_to_tce = ILRToTCETransformer()
        self._tce_parser = CNLParser()
        self._tau_translator = TCEToTauWrapper()
    
    def translate(self, english: str) -> TranslationResult:
        """Main orchestrator method."""
        metadata = self._create_metadata()
        
        # Step 1: NL → Normalized Text
        nl_result = self._process_natural_language(english)
        if not nl_result[0]:
            return self._create_failure_result(nl_result[2], metadata)
        
        # Step 2: Text → ILR
        ilr_result = self._generate_ilr_structure(nl_result[1])
        if not ilr_result[0]:
            return self._create_failure_result(ilr_result[2], metadata)
        
        # Step 3: ILR → TCE
        tce_result = self._transform_to_tce_statements(ilr_result[1])
        if not tce_result[0]:
            return self._create_failure_result(tce_result[2], metadata)
        
        # Step 4: TCE → Tau
        tau_result = self._translate_to_tau_code(tce_result[1])
        
        return self._create_success_result(tau_result, tce_result, ilr_result, metadata)
    
    def _process_natural_language(self, text: str) -> Tuple[bool, str, str]:
        """Process natural language to normalized text."""
        try:
            nl_text = NaturalLanguageText(text)
            result = self._nlp_service.translate_nl_to_tce(nl_text)
            return result.success, result.output_text or "", result.error_message or ""
        except Exception as e:
            return False, "", str(e)
    
    def _generate_ilr_structure(self, text: str) -> Tuple[bool, Any, str]:
        """Generate ILR semantic structure from text."""
        try:
            ilr_result = self._ilr_generator.convert_text_to_ilr(text)
            if isinstance(ilr_result, Success):
                return True, ilr_result.unwrap(), ""
            else:
                return False, None, ilr_result.failure()
        except Exception as e:
            return False, None, str(e)
    
    def _transform_to_tce_statements(self, ilr_node) -> Tuple[bool, list, str]:
        """Transform ILR node to TCE statements."""
        try:
            tce_result = self._ilr_to_tce.transform_ilr_to_tce_async(ilr_node)
            if isinstance(tce_result, Success):
                return True, tce_result.unwrap(), ""
            else:
                return False, [], tce_result.failure()
        except Exception as e:
            return False, [], str(e)
    
    def _translate_to_tau_code(self, tce_statements: list) -> Tuple[bool, str, str]:
        """Translate TCE statements to Tau code."""
        try:
            if not tce_statements:
                return False, "", "No TCE statements to translate"
            
            tce_text = self._format_tce_for_parsing(tce_statements[0])
            ast = self._tce_parser.parse(tce_text)
            tau_result = self._tau_translator.translate(ast)
            
            success = not bool(tau_result.errors)
            error = str(tau_result.errors[0]) if tau_result.errors else ""
            return success, tau_result.tau_code, error
        except Exception as e:
            return False, "", str(e)
    
    def _format_tce_for_parsing(self, tce_statement) -> str:
        """Format TCE statement for CNL parser."""
        pattern = tce_statement.pattern
        return pattern + '.' if not pattern.endswith('.') else pattern
    
    def _create_metadata(self) -> Dict[str, Any]:
        """Create metadata structure."""
        return {"pipeline": "NL→ILR→TCE→Tau", "steps": []}
    
    def _create_failure_result(self, error: str, metadata: Dict[str, Any]) -> TranslationResult:
        """Create failure result."""
        return TranslationResult(False, "", "", "", {"error": error, **metadata})
    
    def _create_success_result(self, tau_result, tce_result, ilr_result, metadata) -> TranslationResult:
        """Create success result."""
        tce_text = self._format_tce_for_parsing(tce_result[1][0]) if tce_result[1] else ""
        ilr_type = type(ilr_result[1]).__name__ if ilr_result[1] else ""
        
        return TranslationResult(
            success=tau_result[0],
            tau_code=tau_result[1],
            tce_text=tce_text,
            ilr_type=ilr_type,
            metadata=metadata
        )


def test_ilr_pipeline_simple():
    """Test ILR pipeline with simple IDP implementation."""
    pipeline = ILRPipelineSimple()
    
    test_cases = [
        "x equals 5",
        "temperature is 25",
        "x and y", 
        "x is greater than 10"
    ]
    
    print("=== IDP-Simple ILR Pipeline Test ===\n")
    success_count = 0
    
    for english in test_cases:
        print(f"English: {english}")
        result = pipeline.translate(english)
        
        print(f"ILR:     {result.ilr_type}")
        print(f"TCE:     {result.tce_text}")
        print(f"Tau:     {result.tau_code}")
        print(f"Success: {result.success}")
        
        if result.success:
            success_count += 1
        elif 'error' in result.metadata:
            print(f"Error:   {result.metadata['error']}")
        print()
    
    print(f"Success rate: {success_count}/{len(test_cases)}")


if __name__ == "__main__":
    test_ilr_pipeline_simple()