#!/usr/bin/env python3
"""
Debug ILR Pipeline Integration
Copyright: DarkLightX/Dana Edwards
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.unified.domain.text_to_ilr_service import TextToILRService
from backend.unified.domain.nlp_types import NaturalLanguageText
from backend.unified.domain.nlp_translation_service import NLPTranslationService
from backend.unified.domain.ilr_to_tce_transformer import ILRToTCETransformer
from backend.unified.tce_to_tau_wrapper import TCEToTauWrapper
from tau_translator_omega.core_engine.cnl_parser.cnl_parser import CNLParser

def debug_step_by_step():
    """Debug each step of the ILR pipeline."""
    
    # Test input
    text = "x equals 5"
    print(f"Input: {text}")
    
    # Step 1: Test NLP service
    print("\n=== Step 1: NLP Service ===")
    try:
        nlp_service = NLPTranslationService()
        nl_text = NaturalLanguageText(text)
        nlp_result = nlp_service.translate_nl_to_tce(nl_text)
        
        print(f"NLP Success: {nlp_result.success}")
        print(f"NLP Output: {nlp_result.output_text}")
        print(f"NLP Error: {nlp_result.error_message}")
        
        if not nlp_result.success:
            return
            
    except Exception as e:
        print(f"NLP Error: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 2: Test ILR generation
    print("\n=== Step 2: ILR Generation ===")
    try:
        ilr_service = TextToILRService()
        ilr_result = ilr_service.convert_text_to_ilr(nlp_result.output_text or "")
        
        print(f"ILR Result type: {type(ilr_result)}")
        print(f"ILR Result: {ilr_result}")
        
        from returns.result import Success, Failure
        if isinstance(ilr_result, Success):
            ilr_node = ilr_result.unwrap()
            print(f"ILR Success: {ilr_node}")
            print(f"ILR Node Type: {type(ilr_node)}")
        elif isinstance(ilr_result, Failure):
            print(f"ILR Failure: {ilr_result.failure()}")
            return
        else:
            print(f"Unknown ILR result format")
            return
            
    except Exception as e:
        print(f"ILR Error: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 3: Test ILR to TCE transformation
    print("\n=== Step 3: ILR to TCE Transformation ===")
    try:
        transformer = ILRToTCETransformer()
        tce_result = transformer.transform_ilr_to_tce_async(ilr_node)
        
        print(f"TCE Result type: {type(tce_result)}")
        if isinstance(tce_result, Success):
            tce_statements = tce_result.unwrap()
            print(f"TCE Success: {tce_statements}")
            print(f"TCE Count: {len(tce_statements)}")
            for i, stmt in enumerate(tce_statements):
                print(f"  Statement {i}: {stmt}")
        elif isinstance(tce_result, Failure):
            print(f"TCE Failure: {tce_result.failure()}")
            return
            
    except Exception as e:
        print(f"TCE Error: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 4: Test TCE to Tau translation
    print("\n=== Step 4: TCE to Tau Translation ===")
    try:
        # Format TCE statements as text
        tce_text = tce_statements[0].pattern
        if not tce_text.endswith('.'):
            tce_text += '.'
        print(f"TCE Text for parsing: '{tce_text}'")
        
        # Parse and translate to Tau
        parser = CNLParser()
        tau_wrapper = TCEToTauWrapper()
        
        ast = parser.parse(tce_text)
        print(f"AST type: {type(ast).__name__}")
        
        tau_result = tau_wrapper.translate(ast)
        print(f"Tau Success: {not tau_result.errors}")
        print(f"Tau Code: '{tau_result.tau_code}'")
        print(f"Tau Errors: {tau_result.errors}")
        
    except Exception as e:
        print(f"Tau Error: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Summary
    print("\n=== COMPLETE PIPELINE SUMMARY ===")
    print(f"Natural Language: '{text}'")
    print(f"ILR Semantic:     {type(ilr_node).__name__}({ilr_node.operator.value})")
    print(f"TCE Statement:    '{tce_text}'")
    print(f"Tau Code:         '{tau_result.tau_code}'")
    print(f"Pipeline Success: {not tau_result.errors}")

if __name__ == "__main__":
    debug_step_by_step()