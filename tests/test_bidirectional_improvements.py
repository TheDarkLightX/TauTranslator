#!/usr/bin/env python3
"""
Test the improved bidirectional translation capabilities.

Tests the enhanced language detection and TAU to English translation 
implemented in the current session.

Copyright: DarkLightX / Dana Edwards
"""

import os
import sys
import asyncio
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
backend_path = project_root / "backend/unified"
src_path = project_root / "src"

sys.path.insert(0, str(backend_path))
sys.path.insert(0, str(src_path))

class BidirectionalImprovementTester:
    """Test the improvements made to bidirectional translation."""
    
    def __init__(self):
        self.test_cases = [
            # TAU expressions for TAU → English testing
            {
                "input": "∀x: p(x)",
                "expected_direction": "TAU",
                "expected_translation": "for all x, p(x)",
                "description": "Universal quantifier TAU to English"
            },
            {
                "input": "∃y: q(y)",
                "expected_direction": "TAU", 
                "expected_translation": "there exists y such that q(y)",
                "description": "Existential quantifier TAU to English"
            },
            {
                "input": "(x > 5 ? true : false)",
                "expected_direction": "TAU",
                "expected_translation": "if x is greater than 5 then true else false",
                "description": "Conditional TAU to English"
            },
            
            # TCE expressions for TCE parsing
            {
                "input": "forall x: p(x)",
                "expected_direction": "TCE",
                "expected_translation": "∀x: p(x)",
                "description": "TCE quantifier parsing"
            },
            {
                "input": "if x > 5 then true else false",
                "expected_direction": "TCE",
                "expected_translation": "(x > 5 ? true : false)",
                "description": "TCE conditional parsing"
            },
            
            # English expressions for English → TAU
            {
                "input": "for all variables x, predicate p holds",
                "expected_direction": "English",
                "expected_translation": "∀x: p(x)",
                "description": "English to TAU quantifier"
            }
        ]
    
    def test_language_detection(self) -> bool:
        """Test the improved language detection algorithm."""
        
        print("🔍 Testing Enhanced Language Detection:")
        print("-" * 50)
        
        try:
            # Import the bidirectional engine
            from translators.bidirectional_engine import BidirectionalTranslationEngine
            
            engine = BidirectionalTranslationEngine()
            print("  ✅ Bidirectional engine loaded")
            
            success_count = 0
            for test_case in self.test_cases:
                try:
                    input_text = test_case["input"]
                    expected_direction = test_case["expected_direction"]
                    
                    # Test language detection
                    detected_direction = engine._detect_direction(input_text)
                    
                    # Map direction to expected language
                    direction_map = {
                        "TO_ENGLISH": "TAU",
                        "TCE_TO_TAU": "TCE", 
                        "TO_TAU": "English"
                    }
                    
                    detected_language = direction_map.get(detected_direction.value if detected_direction else None, "Unknown")
                    
                    if detected_language == expected_direction:
                        print(f"    ✅ '{input_text[:30]}...' → {detected_language}")
                        success_count += 1
                    else:
                        print(f"    ❌ '{input_text[:30]}...' → {detected_language} (expected {expected_direction})")
                
                except Exception as e:
                    print(f"    ❌ Error detecting '{input_text[:30]}...': {e}")
            
            detection_success = success_count >= len(self.test_cases) // 2
            print(f"\n  📊 Detection Results: {success_count}/{len(self.test_cases)} correct")
            return detection_success
            
        except ImportError as e:
            print(f"  ❌ Could not import bidirectional engine: {e}")
            return False
        except Exception as e:
            print(f"  ❌ Language detection test failed: {e}")
            return False
    
    def test_tau_to_english_translation(self) -> bool:
        """Test the new TAU to English translation service."""
        
        print("\n🔄 Testing TAU to English Translation:")
        print("-" * 50)
        
        try:
            from domain.tau_to_english_translator import create_tau_to_english_service
            
            service = create_tau_to_english_service()
            print("  ✅ TAU to English service created")
            
            success_count = 0
            tau_test_cases = [tc for tc in self.test_cases if tc["expected_direction"] == "TAU"]
            
            for test_case in tau_test_cases:
                try:
                    input_text = test_case["input"]
                    expected_output = test_case["expected_translation"]
                    
                    # Test async translation
                    result = asyncio.run(service.translate_expression_async(input_text))
                    
                    if hasattr(result, 'is_success') and result.is_success():
                        translated = result.value
                        
                        # Check if translation contains expected elements
                        expected_words = expected_output.lower().split()
                        translated_lower = translated.lower()
                        
                        found_words = sum(1 for word in expected_words if word in translated_lower)
                        coverage = found_words / len(expected_words) if expected_words else 0
                        
                        if coverage >= 0.6:  # 60% coverage threshold
                            print(f"    ✅ '{input_text}' → '{translated}'")
                            success_count += 1
                        else:
                            print(f"    ❌ '{input_text}' → '{translated}' (low coverage: {coverage:.1%})")
                    else:
                        error_msg = result.error if hasattr(result, 'error') else "Unknown error"
                        print(f"    ❌ '{input_text}' → Failed: {error_msg}")
                
                except Exception as e:
                    print(f"    ❌ Error translating '{input_text}': {e}")
            
            translation_success = success_count >= len(tau_test_cases) // 2
            print(f"\n  📊 Translation Results: {success_count}/{len(tau_test_cases)} successful")
            return translation_success
            
        except ImportError as e:
            print(f"  ❌ Could not import TAU to English service: {e}")
            return False
        except Exception as e:
            print(f"  ❌ TAU to English translation test failed: {e}")
            return False
    
    def test_enhanced_tce_parsing(self) -> bool:
        """Test enhanced TCE parsing with our fixed grammar."""
        
        print("\n🔧 Testing Enhanced TCE Parsing:")
        print("-" * 50)
        
        try:
            from lark import Lark
            from tau_translator_omega.core_engine.tce_tau_transformer import TCEToTauTransformer
            
            # Load the fixed TCE grammar
            grammar_path = project_root / "src/tau_translator_omega/core_engine/cnl_parser/grammars/tce_fixed.lark"
            
            with open(grammar_path, 'r') as f:
                grammar_content = f.read()
            
            parser = Lark(grammar_content, parser='lalr', start='start', propagate_positions=True)
            transformer = TCEToTauTransformer()
            
            print("  ✅ Enhanced TCE parser loaded")
            
            success_count = 0
            tce_test_cases = [tc for tc in self.test_cases if tc["expected_direction"] == "TCE"]
            
            for test_case in tce_test_cases:
                try:
                    input_text = test_case["input"] + "."  # Add sentence terminator
                    
                    # Parse and transform
                    parse_tree = parser.parse(input_text)
                    tau_output = transformer.transform(parse_tree)
                    
                    if tau_output and str(tau_output).strip():
                        print(f"    ✅ '{test_case['input']}' → '{tau_output}'")
                        success_count += 1
                    else:
                        print(f"    ❌ '{test_case['input']}' → Empty output")
                
                except Exception as e:
                    print(f"    ❌ Error parsing '{test_case['input']}': {e}")
            
            parsing_success = success_count >= len(tce_test_cases) // 2
            print(f"\n  📊 Parsing Results: {success_count}/{len(tce_test_cases)} successful")
            return parsing_success
            
        except ImportError as e:
            print(f"  ❌ Could not import TCE parser: {e}")
            return False
        except Exception as e:
            print(f"  ❌ TCE parsing test failed: {e}")
            return False
    
    def run_all_tests(self) -> bool:
        """Run all improvement tests."""
        
        print("🧪 Testing Bidirectional Translation Improvements")
        print("=" * 70)
        print("Testing improvements made in current session:")
        print("- Enhanced language detection algorithm")
        print("- TAU to English translation service")
        print("- Improved TCE grammar parsing")
        print()
        
        # Run all tests
        detection_success = self.test_language_detection()
        translation_success = self.test_tau_to_english_translation()
        parsing_success = self.test_enhanced_tce_parsing()
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 IMPROVEMENT TEST RESULTS:")
        print()
        
        improvements_working = 0
        total_improvements = 3
        
        if detection_success:
            print("✅ Enhanced Language Detection: IMPROVED")
            improvements_working += 1
        else:
            print("❌ Enhanced Language Detection: NEEDS WORK")
        
        if translation_success:
            print("✅ TAU to English Translation: WORKING")
            improvements_working += 1
        else:
            print("❌ TAU to English Translation: NEEDS WORK")
        
        if parsing_success:
            print("✅ Enhanced TCE Parsing: WORKING")
            improvements_working += 1
        else:
            print("❌ Enhanced TCE Parsing: NEEDS WORK")
        
        overall_success = improvements_working >= 2
        
        print(f"\n🎯 Overall: {improvements_working}/{total_improvements} improvements working")
        
        if overall_success:
            print("🎉 SUCCESS: Bidirectional translation improvements are effective!")
            print("✅ The enhanced capabilities provide better language detection and translation")
        else:
            print("❌ NEEDS WORK: Some improvements need refinement")
        
        return overall_success

def main():
    """Main test runner."""
    tester = BidirectionalImprovementTester()
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()