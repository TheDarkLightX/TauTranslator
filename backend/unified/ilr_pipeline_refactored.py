#!/usr/bin/env python3
"""
ILR-Integrated Pipeline (IDP Refactored)
Copyright: DarkLightX/Dana Edwards

Following Intentional Disclosure Principle:
- All methods ≤10 lines
- Result monad for error handling  
- Domain types over primitives
- Pipeline pattern with clear data flow
"""

import sys
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass
from ..core.result_enhanced import Result, Success, Failure
from returns.pipeline import flow

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.unified.core.domain_types import SourceText, TargetText
from backend.unified.domain.text_to_ilr_service import TextToILRService
from backend.unified.domain.nlp_translation_service import NLPTranslationService
from backend.unified.domain.nlp_types import NaturalLanguageText
from backend.unified.domain.ilr_to_tce_transformer import ILRToTCETransformer
from backend.unified.tce_to_tau_wrapper import TCEToTauWrapper
from src.tau_translator_omega.core_engine.parsers.cnl_parser.parser import CNLParser

# Domain Types
NLText = str
ILRNode = Any
TCEStatements = List[Any]
TauCode = str
PipelineMetadata = Dict[str, Any]

@dataclass(frozen=True)
class TranslationStep:
    """Represents one step in the pipeline."""
    step_name: str
    input_data: Any
    output_data: Any
    success: bool
    error: str = ""

@dataclass(frozen=True)
class PipelineResult:
    """Final result of the translation pipeline."""
    success: bool
    tau_code: TauCode
    tce_text: str
    steps: List[TranslationStep]


class ILRPipelineRefactored:
    """ILR pipeline following IDP with ≤10 line methods."""
    
    def __init__(self):
        self._nlp_service = NLPTranslationService()
        self._ilr_generator = TextToILRService()
        self._ilr_to_tce = ILRToTCETransformer()
        self._tce_parser = CNLParser()
        self._tau_translator = TCEToTauWrapper()
        self._steps: List[TranslationStep] = []
    
    def translate_async(self, english: str) -> Result[PipelineResult]:
        """Main translation pipeline orchestrator."""
        source = SourceText(english)
        self._steps = []
        
        return flow(
            source,
            self._process_nl_to_text,
            self._generate_ilr_from_text,
            self._transform_ilr_to_tce,
            self._translate_tce_to_tau,
            self._create_pipeline_result
        )
    
    def _process_nl_to_text(self, source: SourceText) -> Result[NLText]:
        """Step 1: Process natural language."""
        try:
            nl_input = NaturalLanguageText(source)
            result = self._nlp_service.translate_nl_to_tce(nl_input)
            return self._record_step_and_return("NL_Processing", source, result.output_text, result.success, result.error_message)
        except Exception as e:
            return self._record_error_step("NL_Processing", source, str(e))
    
    def _generate_ilr_from_text(self, text: NLText) -> Result[ILRNode]:
        """Step 2: Generate ILR semantic structure."""
        try:
            ilr_result = self._ilr_generator.convert_text_to_ilr(text)
            if isinstance(ilr_result, Success):
                node = ilr_result.unwrap()
                return self._record_step_and_return("ILR_Generation", text, node, True)
            else:
                return self._record_error_step("ILR_Generation", text, ilr_result.failure())
        except Exception as e:
            return self._record_error_step("ILR_Generation", text, str(e))
    
    def _transform_ilr_to_tce(self, ilr_node: ILRNode) -> Result[TCEStatements]:
        """Step 3: Transform ILR to TCE statements."""
        try:
            tce_result = self._ilr_to_tce.transform_ilr_to_tce_async(ilr_node)
            if isinstance(tce_result, Success):
                statements = tce_result.unwrap()
                return self._record_step_and_return("ILR_to_TCE", ilr_node, statements, True)
            else:
                return self._record_error_step("ILR_to_TCE", ilr_node, tce_result.failure())
        except Exception as e:
            return self._record_error_step("ILR_to_TCE", ilr_node, str(e))
    
    def _translate_tce_to_tau(self, tce_statements: TCEStatements) -> Result[TauCode]:
        """Step 4: Translate TCE to Tau code."""
        try:
            if not tce_statements:
                return self._record_error_step("TCE_to_Tau", tce_statements, "No TCE statements")
            
            tce_text = self._format_tce_text(tce_statements[0])
            ast = self._tce_parser.parse(tce_text)
            tau_result = self._tau_translator.translate(ast)
            
            success = not bool(tau_result.errors)
            error = str(tau_result.errors) if tau_result.errors else ""
            return self._record_step_and_return("TCE_to_Tau", tce_text, tau_result.tau_code, success, error)
        except Exception as e:
            return self._record_error_step("TCE_to_Tau", tce_statements, str(e))
    
    def _create_pipeline_result(self, tau_code: TauCode) -> Result[PipelineResult]:
        """Create final pipeline result."""
        tce_text = self._extract_tce_from_steps()
        success = all(step.success for step in self._steps)
        
        result = PipelineResult(
            success=success,
            tau_code=tau_code,
            tce_text=tce_text,
            steps=self._steps
        )
        return Success(result)
    
    def _record_step_and_return(self, step_name: str, input_data: Any, output_data: Any, 
                               success: bool, error: str = "") -> Result[Any]:
        """Record pipeline step and return result."""
        step = TranslationStep(step_name, input_data, output_data, success, error)
        self._steps.append(step)
        
        if success:
            return Success(output_data)
        else:
            return Failure(error or f"{step_name} failed")
    
    def _record_error_step(self, step_name: str, input_data: Any, error: str) -> Result[Any]:
        """Record error step."""
        return self._record_step_and_return(step_name, input_data, None, False, error)
    
    def _format_tce_text(self, tce_statement) -> str:
        """Format TCE statement for parsing."""
        pattern = tce_statement.pattern
        return pattern + '.' if not pattern.endswith('.') else pattern
    
    def _extract_tce_from_steps(self) -> str:
        """Extract TCE text from recorded steps."""
        for step in self._steps:
            if step.step_name == "ILR_to_TCE" and step.success and step.output_data:
                return self._format_tce_text(step.output_data[0])
        return ""


def test_ilr_pipeline():
    """Test the ILR pipeline with examples."""
    pipeline = ILRPipelineRefactored()
    
    test_cases = [
        "x equals 5",
        "temperature is 25", 
        "x and y",
        "x is greater than 10"
    ]
    
    print("=== IDP-Refactored ILR Pipeline Test ===\n")
    success_count = 0
    
    for english in test_cases:
        print(f"English: {english}")
        result = pipeline.translate_async(english)
        
        if isinstance(result, Success):
            pipeline_result = result.unwrap()
            print(f"ILR:     {pipeline_result.steps[1].output_data.__class__.__name__ if len(pipeline_result.steps) > 1 else 'Failed'}")
            print(f"TCE:     {pipeline_result.tce_text}")
            print(f"Tau:     {pipeline_result.tau_code}")
            print(f"Success: {pipeline_result.success}")
            
            if pipeline_result.success:
                success_count += 1
        else:
            print(f"Pipeline Error: {result.failure()}")
        print()
    
    print(f"Success rate: {success_count}/{len(test_cases)}")


if __name__ == "__main__":
    test_ilr_pipeline()