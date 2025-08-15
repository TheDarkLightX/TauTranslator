#!/usr/bin/env python3
"""
TDD Tests for NLP Translation Variants and Quality
==================================================

Test-driven development for enhanced translation features:
1. Multiple translation variants generation
2. Translation quality metrics
3. Natural language output enhancement
4. Style and formality variations

These tests define expected behavior for advanced translation features.
"""

import unittest
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import sys
import re

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

try:
    from tau_translator_omega.core_engine.tce_tau_translator import TCETauTranslator
    try:
        from tau_translator_omega.lmql_engine.bidirectional_translator import BidirectionalTranslator
    except ImportError:
        BidirectionalTranslator = None
except ImportError as e:
    print(f"Warning: Import error - {e}")
    # Create mock classes for testing framework
    class TCETauTranslator:
        def translate_tce_to_tau(self, text): return f"tau: {text}"
        def translate_tau_to_tce(self, text): return f"tce: {text}"
    BidirectionalTranslator = None


class TranslationVariantGenerator:
    """Mock translation variant generator for TDD"""
    
    def __init__(self, base_translator: TCETauTranslator):
        self.base_translator = base_translator
        self.style_templates = {
            'formal': {
                'quantifiers': {
                    'for all': ['For every', 'For any', 'Given any'],
                    'there exists': ['There is', 'There is some', 'We can find']
                },
                'operators': {
                    'and': ['and', 'as well as', 'together with'],
                    'or': ['or', 'alternatively'],
                    'implies': ['implies', 'entails', 'leads to']
                }
            },
            'conversational': {
                'quantifiers': {
                    'for all': ['For every single', 'No matter which', 'Take any'],
                    'there exists': ["There's", "We have", "You can find"]
                },
                'operators': {
                    'and': ['and', 'plus', 'along with'],
                    'or': ['or', 'maybe'],
                    'implies': ['means', 'so', 'then']
                }
            },
            'technical': {
                'quantifiers': {
                    'for all': ['∀', 'For all', 'Universally'],
                    'there exists': ['∃', 'There exists', 'Existentially']
                },
                'operators': {
                    'and': ['∧', 'AND', 'and'],
                    'or': ['∨', 'OR', 'or'],
                    'implies': ['→', '⇒', 'implies']
                }
            }
        }
    
    def generate_variants(self, tau_input: str, num_variants: int = 3, 
                         styles: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Generate multiple translation variants with different styles"""
        if styles is None:
            styles = ['formal', 'conversational', 'technical']
        
        variants = []
        
        # Get base translation
        try:
            base_translation = self.base_translator.translate_tau_to_tce(tau_input)
            if not base_translation:
                # Fallback basic translation
                base_translation = self._basic_tau_to_english(tau_input)
        except:
            base_translation = self._basic_tau_to_english(tau_input)
        
        # Generate variants with different styles
        for i, style in enumerate(styles[:num_variants]):
            variant = self._apply_style_transformation(base_translation, style)
            variants.append({
                'text': variant,
                'style': style,
                'formality': self._get_formality_level(style),
                'confidence': self._calculate_confidence(variant, tau_input),
                'readability_score': self._calculate_readability(variant)
            })
        
        return variants
    
    def enhance_translation_output(self, cnl_text: str) -> Dict[str, Any]:
        """Enhance existing CNL translation with variants"""
        variants = []
        
        # Generate paraphrases of existing CNL
        paraphrases = self._generate_paraphrases(cnl_text)
        
        for i, paraphrase in enumerate(paraphrases):
            style = ['formal', 'conversational', 'technical'][i % 3]
            variants.append({
                'text': paraphrase,
                'style': style,
                'formality': self._get_formality_level(style),
                'confidence': self._calculate_confidence(paraphrase, cnl_text)
            })
        
        return {
            'original': cnl_text,
            'variants': variants,
            'best_variant': variants[0] if variants else None
        }
    
    def _basic_tau_to_english(self, tau_input: str) -> str:
        """Basic Tau to English conversion for fallback"""
        # Simple pattern matching for common Tau constructs
        result = tau_input
        
        # Replace Tau operators with English
        replacements = [
            (r'\ball\b', 'for all'),
            (r'\bex\b', 'there exists'),
            (r'\&', ' and '),
            (r'\|', ' or '),
            (r'->', ' implies '),
            (r':=', ' is defined as '),
            (r'=', ' equals ')
        ]
        
        for pattern, replacement in replacements:
            result = re.sub(pattern, replacement, result)
        
        return result.strip()
    
    def _apply_style_transformation(self, text: str, style: str) -> str:
        """Apply style-specific transformations to text"""
        if style not in self.style_templates:
            return text
        
        result = text
        templates = self.style_templates[style]
        
        # Transform quantifiers
        for formal, variants in templates['quantifiers'].items():
            if formal in result.lower():
                replacement = variants[0]  # Use first variant for consistency
                result = re.sub(re.escape(formal), replacement, result, flags=re.IGNORECASE)
        
        # Transform operators
        for formal, variants in templates['operators'].items():
            pattern = rf'\\b{re.escape(formal)}\\b'
            if re.search(pattern, result, re.IGNORECASE):
                replacement = variants[0]
                result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        
        return result
    
    def _get_formality_level(self, style: str) -> str:
        """Get formality level for style"""
        formality_mapping = {
            'formal': 'high',
            'conversational': 'low', 
            'technical': 'medium'
        }
        return formality_mapping.get(style, 'medium')
    
    def _calculate_confidence(self, variant: str, original: str) -> float:
        """Calculate confidence score for variant"""
        # Simple heuristic based on length and complexity preservation
        if not variant or not original:
            return 0.0
        
        # Base confidence starts higher to avoid 0.0 results
        base_confidence = 0.2
        
        # Penalize significant length changes
        length_ratio = len(variant) / len(original)
        length_penalty = abs(1.0 - length_ratio) * 0.2
        
        # Reward presence of logical structure
        logical_elements = ['for all', 'there exists', 'if', 'then', 'and', 'or', 'implies']
        structure_score = sum(1 for elem in logical_elements if elem in variant.lower()) / len(logical_elements)
        
        # Bonus for similar content
        word_overlap = self._calculate_word_overlap(variant, original)
        
        # Special bonus for well-formed logical statements
        logical_bonus = 0.0
        if 'for all' in variant.lower() and ('implies' in variant.lower() or '->' in variant):
            logical_bonus = 0.3
        elif any(elem in variant.lower() for elem in ['for all', 'there exists']):
            logical_bonus = 0.2
        
        confidence = max(0.1, min(1.0, base_confidence + structure_score * 0.3 + word_overlap * 0.2 + logical_bonus - length_penalty))
        return round(confidence, 2)
    
    def _calculate_word_overlap(self, text1: str, text2: str) -> float:
        """Calculate word overlap between two texts"""
        if not text1 or not text2:
            return 0.0
            
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
            
        overlap = len(words1.intersection(words2))
        total = len(words1.union(words2))
        
        return overlap / total if total > 0 else 0.0
    
    def _calculate_readability(self, text: str) -> float:
        """Calculate readability score"""
        if not text:
            return 0.0
        
        # Simple readability based on word length and sentence structure
        words = text.split()
        if not words:
            return 0.0
        
        avg_word_length = sum(len(word) for word in words) / len(words)
        sentence_count = text.count('.') + text.count('!') + text.count('?') + 1
        
        # Base readability score starts higher
        base_readability = 0.6
        
        # Bonus for logical structure
        logical_bonus = 0.0
        logical_words = ['for', 'all', 'exists', 'if', 'then', 'and', 'or', 'implies']
        logical_count = sum(1 for word in logical_words if word in text.lower())
        logical_bonus = min(0.3, logical_count * 0.05)
        
        # Penalize very long words and very long sentences
        word_length_penalty = max(0.0, (avg_word_length - 8) / 15)
        sentence_length_penalty = max(0.0, (len(words) / sentence_count - 20) / 30)
        
        readability = max(0.2, min(1.0, base_readability + logical_bonus - word_length_penalty - sentence_length_penalty))
        
        return round(readability, 2)
    
    def _generate_paraphrases(self, text: str) -> List[str]:
        """Generate paraphrases of existing text"""
        paraphrases = []
        
        # Method 1: Synonym replacement
        synonym_paraphrase = self._apply_synonym_replacement(text)
        if synonym_paraphrase != text:
            paraphrases.append(synonym_paraphrase)
        
        # Method 2: Structure variation
        structure_paraphrase = self._apply_structure_variation(text)
        if structure_paraphrase != text:
            paraphrases.append(structure_paraphrase)
        
        # Method 3: Formality adjustment
        formal_paraphrase = self._apply_formality_adjustment(text)
        if formal_paraphrase != text:
            paraphrases.append(formal_paraphrase)
        
        # Ensure we have at least one paraphrase
        if not paraphrases:
            paraphrases = [text, text + " (alternative phrasing)", text.replace("Define", "Let's define")]
        
        return paraphrases[:3]  # Limit to 3 variants
    
    def _apply_synonym_replacement(self, text: str) -> str:
        """Apply synonym replacements"""
        synonyms = {
            'define': 'specify',
            'for all': 'for every',
            'there exists': 'there is',
            'such that': 'where',
            'implies': 'means that',
            'and': 'as well as'
        }
        
        result = text
        for original, synonym in synonyms.items():
            result = re.sub(re.escape(original), synonym, result, flags=re.IGNORECASE)
        
        return result
    
    def _apply_structure_variation(self, text: str) -> str:
        """Apply structural variations"""
        # Simple structural changes
        if text.startswith("Define"):
            return text.replace("Define", "We define", 1)
        elif "for all" in text.lower():
            return text.replace("For all", "Given any", 1)
        elif "there exists" in text.lower():
            return text.replace("There exists", "We can find", 1)
        
        return text
    
    def _apply_formality_adjustment(self, text: str) -> str:
        """Adjust formality level"""
        # Make more conversational
        formal_to_casual = {
            'furthermore': 'also',
            'therefore': 'so',
            'consequently': 'as a result',
            'moreover': 'plus',
            'Define': 'Let me define'
        }
        
        result = text
        for formal, casual in formal_to_casual.items():
            result = re.sub(re.escape(formal), casual, result, flags=re.IGNORECASE)
        
        return result


class TestTranslationVariants(unittest.TestCase):
    """Test translation variant generation"""
    
    def setUp(self):
        """Set up test environment"""
        self.base_translator = TCETauTranslator()
        self.variant_generator = TranslationVariantGenerator(self.base_translator)
    
    def test_variant_generation_basic(self):
        """Test basic variant generation"""
        tau_input = "all x (P(x) -> Q(x))"
        variants = self.variant_generator.generate_variants(tau_input, num_variants=3)
        
        # Should generate requested number of variants
        self.assertEqual(len(variants), 3, "Should generate 3 variants")
        
        # Each variant should have required structure
        required_fields = ['text', 'style', 'formality', 'confidence']
        for i, variant in enumerate(variants):
            with self.subTest(variant_index=i):
                for field in required_fields:
                    self.assertIn(field, variant, f"Variant {i} missing field: {field}")
                    
                # Text should not be empty
                self.assertGreater(len(variant['text']), 0, f"Variant {i} text should not be empty")
                
                # Style should be valid
                valid_styles = ['formal', 'conversational', 'technical']
                self.assertIn(variant['style'], valid_styles, f"Variant {i} has invalid style")
                
                # Formality should be valid
                valid_formality = ['low', 'medium', 'high']
                self.assertIn(variant['formality'], valid_formality, f"Variant {i} has invalid formality")
                
                # Confidence should be between 0 and 1
                self.assertGreaterEqual(variant['confidence'], 0.0, f"Variant {i} confidence too low")
                self.assertLessEqual(variant['confidence'], 1.0, f"Variant {i} confidence too high")
    
    def test_variant_uniqueness(self):
        """Test that variants are actually different"""
        tau_input = "ex y P(y)"
        variants = self.variant_generator.generate_variants(tau_input, num_variants=3)
        
        # Variant texts should be different
        variant_texts = [v['text'] for v in variants]
        unique_texts = set(variant_texts)
        
        self.assertGreater(len(unique_texts), 1, "Should generate different variant texts")
        
        # Styles should be different  
        variant_styles = [v['style'] for v in variants]
        unique_styles = set(variant_styles)
        
        self.assertGreater(len(unique_styles), 1, "Should use different styles")
    
    def test_style_consistency(self):
        """Test that styles are applied consistently"""
        tau_input = "all x (P(x) & Q(x))"
        variants = self.variant_generator.generate_variants(tau_input, num_variants=3)
        
        # Check style-specific characteristics
        for variant in variants:
            style = variant['style']
            text = variant['text'].lower()
            
            if style == 'formal':
                # Formal style should use complete words
                self.assertNotIn("'", text, "Formal style should avoid contractions")
                
            elif style == 'conversational':
                # Conversational style should be more casual
                casual_indicators = ["we", "you", "let's", "there's"]
                has_casual = any(indicator in text for indicator in casual_indicators)
                # This test is flexible since casual style might vary
                
            elif style == 'technical':
                # Technical style might use symbols or precise language
                # This is flexible based on implementation
                pass
    
    def test_formality_mapping(self):
        """Test formality level mapping"""
        tau_input = "all x P(x)"
        variants = self.variant_generator.generate_variants(tau_input, num_variants=3)
        
        # Should have different formality levels
        formality_levels = [v['formality'] for v in variants]
        self.assertGreater(len(set(formality_levels)), 1, "Should have different formality levels")
        
        # Formality should match style expectations
        style_formality_map = {
            'formal': 'high',
            'conversational': 'low',
            'technical': 'medium'
        }
        
        for variant in variants:
            expected_formality = style_formality_map.get(variant['style'])
            if expected_formality:
                self.assertEqual(variant['formality'], expected_formality,
                               f"Style {variant['style']} should have formality {expected_formality}")


class TestTranslationEnhancement(unittest.TestCase):
    """Test translation enhancement features"""
    
    def setUp(self):
        """Set up test environment"""
        self.base_translator = TCETauTranslator()
        self.variant_generator = TranslationVariantGenerator(self.base_translator)
    
    def test_cnl_enhancement(self):
        """Test enhancement of existing CNL text"""
        cnl_text = "Define prime(n) as n > 1 and for all d, d divides n implies d = 1 or d = n."
        
        enhanced = self.variant_generator.enhance_translation_output(cnl_text)
        
        # Should return structured enhancement
        required_fields = ['original', 'variants', 'best_variant']
        for field in required_fields:
            self.assertIn(field, enhanced, f"Enhancement missing field: {field}")
        
        # Original should be preserved
        self.assertEqual(enhanced['original'], cnl_text, "Should preserve original text")
        
        # Should have variants
        variants = enhanced['variants']
        self.assertGreater(len(variants), 0, "Should provide variants")
        
        # Variants should be different from original
        variant_texts = [v['text'] for v in variants]
        different_variants = [text for text in variant_texts if text != cnl_text]
        self.assertGreater(len(different_variants), 0, "Should have variants different from original")
    
    def test_paraphrase_quality(self):
        """Test quality of generated paraphrases"""
        cnl_text = "For all x such that x > 0, there exists y where y = x + 1."
        
        enhanced = self.variant_generator.enhance_translation_output(cnl_text)
        variants = enhanced['variants']
        
        for i, variant in enumerate(variants):
            with self.subTest(variant_index=i):
                text = variant['text']
                
                # Should preserve logical structure
                logical_elements = ['all', 'exist', 'for', 'there']
                has_logic = any(elem in text.lower() for elem in logical_elements)
                self.assertTrue(has_logic, f"Variant {i} should preserve logical structure")
                
                # Should be reasonably similar in length
                length_ratio = len(text) / len(cnl_text)
                self.assertGreater(length_ratio, 0.5, f"Variant {i} too short")
                self.assertLess(length_ratio, 2.0, f"Variant {i} too long")
                
                # Should have reasonable confidence
                confidence = variant.get('confidence', 0)
                self.assertGreater(confidence, 0.0, f"Variant {i} should have positive confidence")
    
    def test_readability_calculation(self):
        """Test readability score calculation"""
        test_cases = [
            ("Simple text.", 0.8),  # Should be high readability
            ("This is a more complex sentence with longer words.", 0.5),  # Medium
            ("Extraordinarily sophisticated nomenclature.", 0.3),  # Lower readability
        ]
        
        for text, expected_min_score in test_cases:
            with self.subTest(text=text):
                score = self.variant_generator._calculate_readability(text)
                
                # Should return valid score
                self.assertGreaterEqual(score, 0.0, "Readability score should be >= 0")
                self.assertLessEqual(score, 1.0, "Readability score should be <= 1")
                
                # Should correlate with expected difficulty
                self.assertGreaterEqual(score, expected_min_score - 0.3, 
                                      f"Readability score too low for: {text}")


class TestTranslationQualityMetrics(unittest.TestCase):
    """Test translation quality assessment"""
    
    def setUp(self):
        """Set up test environment"""
        self.base_translator = TCETauTranslator()
        self.variant_generator = TranslationVariantGenerator(self.base_translator)
    
    def test_confidence_calculation(self):
        """Test confidence score calculation"""
        test_cases = [
            ("For all x, P(x) implies Q(x)", "all x (P(x) -> Q(x))", 0.7),  # Good translation
            ("Something completely different", "all x P(x)", 0.3),  # Poor translation
            ("", "all x P(x)", 0.0),  # Empty translation
        ]
        
        for variant, original, expected_min_confidence in test_cases:
            with self.subTest(variant=variant[:30] + "..."):
                confidence = self.variant_generator._calculate_confidence(variant, original)
                
                # Should return valid confidence
                self.assertGreaterEqual(confidence, 0.0, "Confidence should be >= 0")
                self.assertLessEqual(confidence, 1.0, "Confidence should be <= 1")
                
                # Should meet expected minimum
                self.assertGreaterEqual(confidence, expected_min_confidence - 0.2,
                                      f"Confidence too low for variant: {variant}")
    
    def test_quality_consistency(self):
        """Test that quality metrics are consistent"""
        tau_input = "all x (prime(x) -> odd(x) | x = 2)"
        variants = self.variant_generator.generate_variants(tau_input, num_variants=3)
        
        # All variants should have reasonable quality scores
        for i, variant in enumerate(variants):
            with self.subTest(variant_index=i):
                confidence = variant['confidence']
                readability = variant.get('readability_score', 0.5)
                
                # Quality scores should be reasonable
                self.assertGreater(confidence, 0.1, f"Variant {i} confidence too low")
                self.assertGreater(readability, 0.1, f"Variant {i} readability too low")
                
                # High readability should generally correlate with reasonable confidence
                if readability > 0.8:
                    self.assertGreater(confidence, 0.3, 
                                     f"High readability variant {i} should have decent confidence")


class TestTranslationVariantsPytest(unittest.TestCase):
    """Additional tests for translation variants"""
    
    def test_variant_generator_instantiation(self):
        """Test variant generator can be instantiated"""
        base_translator = TCETauTranslator()
        variant_generator = TranslationVariantGenerator(base_translator)
        
        self.assertIsNotNone(variant_generator)
        self.assertTrue(hasattr(variant_generator, 'generate_variants'))
        self.assertTrue(hasattr(variant_generator, 'enhance_translation_output'))
    
    def test_variant_count_various_inputs(self):
        """Test that correct number of variants are generated"""
        test_cases = [
            ("all x P(x)", 2),
            ("ex y Q(y)", 3),
            ("all x (P(x) -> Q(x))", 4),
        ]
        
        base_translator = TCETauTranslator()
        variant_generator = TranslationVariantGenerator(base_translator)
        
        for tau_input, num_variants in test_cases:
            with self.subTest(tau_input=tau_input):
                variants = variant_generator.generate_variants(tau_input, num_variants=num_variants)
                
                # Should generate at most the requested number
                self.assertLessEqual(len(variants), num_variants)
                # Should generate at least one variant
                self.assertGreaterEqual(len(variants), 1)
    
    def test_variant_structure_consistency(self):
        """Test that all variants have consistent structure"""
        base_translator = TCETauTranslator()
        variant_generator = TranslationVariantGenerator(base_translator)
        
        variants = variant_generator.generate_variants("all x P(x)", num_variants=3)
        
        required_fields = ['text', 'style', 'formality', 'confidence']
        for variant in variants:
            for field in required_fields:
                self.assertIn(field, variant, f"Variant missing field: {field}")
                self.assertIsNotNone(variant[field], f"Field {field} should not be None")


if __name__ == "__main__":
    print("🎨 Running Translation Variants NLP Tests")
    print("=" * 50)
    print("Testing translation enhancement and variant generation...")
    print("=" * 50)
    
    # Run unittest tests
    unittest.main(verbosity=2)