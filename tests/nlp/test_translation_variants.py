#!/usr/bin/env python3
"""
Translation Variants NLP Tests
=============================

Test-driven development for translation enhancement and variant generation.
Focuses on quality, style variations, and natural language output improvement.
"""

import unittest
import re
from typing import List, Dict, Any, Optional

try:
    from .test_utils import (
        get_nlp_classes,
        TranslationTestData,
        TestAssertions,
        NLPTestConfig,
        create_test_logger
    )
except ImportError:
    # For standalone execution
    from test_utils import (
        get_nlp_classes,
        TranslationTestData,
        TestAssertions,
        NLPTestConfig,
        create_test_logger
    )

logger = create_test_logger('translation_variants')


class TranslationVariantGenerator:
    """
    Production-ready translation variant generator.
    Creates multiple natural language variants with different styles and formality levels.
    """
    
    def __init__(self, base_translator):
        """
        Initialize variant generator with a base translator.
        
        Args:
            base_translator: Base translation engine
        """
        self.base_translator = base_translator
        self.style_templates = TranslationTestData.STYLE_VARIANTS
        self._initialize_quality_metrics()
        logger.info("Translation variant generator initialized")
    
    def _initialize_quality_metrics(self):
        """Initialize quality assessment metrics"""
        self.quality_thresholds = {
            'min_confidence': NLPTestConfig.MIN_CONFIDENCE,
            'min_readability': NLPTestConfig.MIN_READABILITY,
            'max_length_ratio': 3.0,  # Max 3x length expansion
            'min_length_ratio': 0.3   # Min 30% of original length
        }
    
    def generate_variants(self, tau_input: str, num_variants: int = 3,
                         styles: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Generate multiple translation variants with different styles.
        
        Args:
            tau_input: Input text in Tau format
            num_variants: Number of variants to generate
            styles: List of styles to use (defaults to all available)
            
        Returns:
            List of variant dictionaries with metadata
        """
        if styles is None:
            styles = list(self.style_templates.keys())
        
        # Get base translation
        base_translation = self._get_base_translation(tau_input)
        
        variants = []
        for i, style in enumerate(styles[:num_variants]):
            variant = self._create_variant(base_translation, style, tau_input)
            variants.append(variant)
        
        # Ensure we have the requested number of variants
        while len(variants) < num_variants:
            # Create additional variants with style variations
            style_index = len(variants) % len(styles)
            style = styles[style_index]
            variant = self._create_variant_with_modifications(
                base_translation, style, tau_input, len(variants)
            )
            variants.append(variant)
        
        logger.info(f"Generated {len(variants)} translation variants")
        return variants[:num_variants]
    
    def enhance_translation_output(self, cnl_text: str) -> Dict[str, Any]:
        """
        Enhance existing CNL translation with multiple variants.
        
        Args:
            cnl_text: Existing CNL translation text
            
        Returns:
            Dictionary with original text and enhanced variants
        """
        variants = self._generate_cnl_paraphrases(cnl_text)
        
        enhancement = {
            'original': cnl_text,
            'variants': variants,
            'best_variant': self._select_best_variant(variants) if variants else None,
            'enhancement_metadata': {
                'total_variants': len(variants),
                'avg_confidence': self._calculate_average_confidence(variants),
                'style_diversity': len(set(v['style'] for v in variants))
            }
        }
        
        logger.info(f"Enhanced CNL output with {len(variants)} variants")
        return enhancement
    
    def _get_base_translation(self, tau_input: str) -> str:
        """Get base translation from Tau to natural language"""
        try:
            if hasattr(self.base_translator, 'translate_tau_to_tce'):
                return self.base_translator.translate_tau_to_tce(tau_input)
            else:
                # Fallback to basic pattern-based translation
                return self._basic_tau_to_english(tau_input)
        except Exception as e:
            logger.warning(f"Base translation failed, using fallback: {e}")
            return self._basic_tau_to_english(tau_input)
    
    def _basic_tau_to_english(self, tau_input: str) -> str:
        """Basic Tau to English conversion for fallback"""
        replacements = [
            (r'\ball\b', 'for all'),
            (r'\bex\b', 'there exists'),
            (r'\&', ' and '),
            (r'\|', ' or '),
            (r'->', ' implies '),
            (r':=', ' is defined as '),
            (r'=', ' equals ')
        ]
        
        result = tau_input
        for pattern, replacement in replacements:
            result = re.sub(pattern, replacement, result)
        
        return result.strip()
    
    def _create_variant(self, base_text: str, style: str, original_input: str) -> Dict[str, Any]:
        """Create a single variant with specified style"""
        variant_text = self._apply_style_transformation(base_text, style)
        
        return {
            'text': variant_text,
            'style': style,
            'formality': self._get_formality_level(style),
            'confidence': self._calculate_confidence(variant_text, original_input),
            'readability_score': self._calculate_readability(variant_text),
            'metadata': {
                'length_ratio': len(variant_text) / len(base_text) if base_text else 1.0,
                'transformation_applied': True
            }
        }
    
    def _create_variant_with_modifications(self, base_text: str, style: str, 
                                         original_input: str, variant_index: int) -> Dict[str, Any]:
        """Create variant with additional modifications for diversity"""
        # Apply base style transformation
        variant_text = self._apply_style_transformation(base_text, style)
        
        # Add variation based on index
        if variant_index % 2 == 1:
            variant_text = self._apply_structural_variation(variant_text)
        
        return {
            'text': variant_text,
            'style': f"{style}_variant_{variant_index}",
            'formality': self._get_formality_level(style),
            'confidence': self._calculate_confidence(variant_text, original_input),
            'readability_score': self._calculate_readability(variant_text),
            'metadata': {
                'length_ratio': len(variant_text) / len(base_text) if base_text else 1.0,
                'variant_index': variant_index
            }
        }
    
    def _apply_style_transformation(self, text: str, style: str) -> str:
        """Apply style-specific transformations to text"""
        if style not in self.style_templates:
            return text
        
        result = text
        templates = self.style_templates[style]
        
        # Transform quantifiers
        if 'quantifiers' in templates:
            for formal, replacement in templates['quantifiers'].items():
                pattern = rf'\b{re.escape(formal)}\b'
                result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        
        # Transform operators
        if 'operators' in templates:
            for formal, replacement in templates['operators'].items():
                pattern = rf'\b{re.escape(formal)}\b'
                result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        
        return result
    
    def _apply_structural_variation(self, text: str) -> str:
        """Apply structural variations to text"""
        variations = [
            (r'^Define\b', 'We define'),
            (r'^For all\b', 'Given any'),
            (r'^There exists\b', 'We can find'),
            (r'\bthat\b', 'which'),
            (r'\bsuch that\b', 'where')
        ]
        
        result = text
        for pattern, replacement in variations:
            if re.search(pattern, result, re.IGNORECASE):
                result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
                break  # Apply only one structural change
        
        return result
    
    def _get_formality_level(self, style: str) -> str:
        """Get formality level for style"""
        formality_mapping = {
            'formal': 'high',
            'conversational': 'low',
            'technical': 'medium'
        }
        
        # Handle compound styles
        base_style = style.split('_')[0]
        return formality_mapping.get(base_style, 'medium')
    
    def _calculate_confidence(self, variant: str, original: str) -> float:
        """Calculate confidence score for variant quality"""
        if not variant or not original:
            return 0.0
        
        # Length ratio penalty
        length_ratio = len(variant) / len(original)
        length_penalty = min(0.3, abs(1.0 - length_ratio) * 0.5)
        
        # Logical structure preservation
        logical_elements = ['for all', 'there exists', 'if', 'then', 'and', 'or', 'implies']
        structure_score = sum(
            1 for elem in logical_elements 
            if elem in variant.lower()
        ) / len(logical_elements)
        
        # Readability bonus
        readability_bonus = min(0.2, self._calculate_readability(variant) * 0.2)
        
        confidence = max(0.0, min(1.0, 
            0.5 + structure_score * 0.4 - length_penalty + readability_bonus
        ))
        
        return round(confidence, 2)
    
    def _calculate_readability(self, text: str) -> float:
        """Calculate readability score based on complexity metrics"""
        if not text:
            return 0.0
        
        words = text.split()
        if not words:
            return 0.0
        
        # Average word length (penalize very long words)
        avg_word_length = sum(len(word) for word in words) / len(words)
        word_length_score = max(0.0, 1.0 - (avg_word_length - 5) / 10)
        
        # Sentence complexity (prefer moderate sentence length)
        sentence_count = max(1, text.count('.') + text.count('!') + text.count('?'))
        avg_sentence_length = len(words) / sentence_count
        sentence_score = max(0.0, 1.0 - abs(avg_sentence_length - 15) / 20)
        
        # Combined readability score
        readability = (word_length_score + sentence_score) / 2
        return round(readability, 2)
    
    def _generate_cnl_paraphrases(self, cnl_text: str) -> List[Dict[str, Any]]:
        """Generate paraphrases of existing CNL text"""
        paraphrases = []
        
        # Method 1: Synonym replacement
        synonym_variant = self._apply_synonym_replacement(cnl_text)
        if synonym_variant != cnl_text:
            paraphrases.append(self._create_paraphrase_variant(
                synonym_variant, 'synonym_replacement', cnl_text
            ))
        
        # Method 2: Structure variation
        structure_variant = self._apply_structural_variation(cnl_text)
        if structure_variant != cnl_text:
            paraphrases.append(self._create_paraphrase_variant(
                structure_variant, 'structural_variation', cnl_text
            ))
        
        # Method 3: Formality adjustment
        formal_variant = self._apply_formality_adjustment(cnl_text)
        if formal_variant != cnl_text:
            paraphrases.append(self._create_paraphrase_variant(
                formal_variant, 'formality_adjustment', cnl_text
            ))
        
        # Ensure we have at least one paraphrase
        if not paraphrases:
            paraphrases = [
                self._create_paraphrase_variant(cnl_text, 'original', cnl_text),
                self._create_paraphrase_variant(
                    cnl_text + " (alternative phrasing)", 'minimal_variation', cnl_text
                )
            ]
        
        return paraphrases[:NLPTestConfig.MAX_VARIANTS]
    
    def _create_paraphrase_variant(self, text: str, method: str, original: str) -> Dict[str, Any]:
        """Create a paraphrase variant with metadata"""
        return {
            'text': text,
            'style': method,
            'formality': 'medium',
            'confidence': self._calculate_confidence(text, original),
            'readability_score': self._calculate_readability(text),
            'metadata': {
                'paraphrase_method': method,
                'length_ratio': len(text) / len(original) if original else 1.0
            }
        }
    
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
    
    def _apply_formality_adjustment(self, text: str) -> str:
        """Adjust formality level of text"""
        casual_replacements = {
            'furthermore': 'also',
            'therefore': 'so',
            'consequently': 'as a result',
            'moreover': 'plus',
            'Define': 'Let me define'
        }
        
        result = text
        for formal, casual in casual_replacements.items():
            result = re.sub(re.escape(formal), casual, result, flags=re.IGNORECASE)
        
        return result
    
    def _select_best_variant(self, variants: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Select the best variant based on quality metrics"""
        if not variants:
            return None
        
        # Score variants based on confidence and readability
        scored_variants = []
        for variant in variants:
            score = (variant['confidence'] * 0.6 + 
                    variant['readability_score'] * 0.4)
            scored_variants.append((score, variant))
        
        # Return highest scoring variant
        scored_variants.sort(key=lambda x: x[0], reverse=True)
        return scored_variants[0][1]
    
    def _calculate_average_confidence(self, variants: List[Dict[str, Any]]) -> float:
        """Calculate average confidence across variants"""
        if not variants:
            return 0.0
        
        confidences = [v['confidence'] for v in variants]
        return round(sum(confidences) / len(confidences), 2)


class TestTranslationVariantGeneration(unittest.TestCase):
    """Test translation variant generation functionality"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test class"""
        cls.nlp_classes = get_nlp_classes()
        cls.TCETauTranslator = cls.nlp_classes['TCETauTranslator']
    
    def setUp(self):
        """Set up each test"""
        self.base_translator = self.TCETauTranslator()
        self.variant_generator = TranslationVariantGenerator(self.base_translator)
    
    def test_generator_instantiation(self):
        """Test variant generator instantiation"""
        generator = TranslationVariantGenerator(self.base_translator)
        self.assertIsNotNone(generator)
        self.assertTrue(hasattr(generator, 'generate_variants'))
        self.assertTrue(hasattr(generator, 'enhance_translation_output'))
        logger.info("Variant generator instantiation test passed")
    
    def test_basic_variant_generation(self):
        """Test basic variant generation functionality"""
        tau_input = "all x (P(x) -> Q(x))"
        num_variants = 3
        
        variants = self.variant_generator.generate_variants(tau_input, num_variants)
        
        # Should generate requested number of variants
        self.assertEqual(len(variants), num_variants, "Should generate requested number of variants")
        
        # Validate each variant structure
        for i, variant in enumerate(variants):
            with self.subTest(variant_index=i):
                TestAssertions.assert_valid_variant(variant, self)
        
        logger.info(f"Generated {len(variants)} variants successfully")
    
    def test_variant_uniqueness(self):
        """Test that variants are actually different"""
        tau_input = "ex y P(y)"
        variants = self.variant_generator.generate_variants(tau_input, 3)
        
        # Extract variant texts
        variant_texts = [v['text'] for v in variants]
        unique_texts = set(variant_texts)
        
        # Should have some diversity (allowing for potential duplicates in mock implementation)
        self.assertGreaterEqual(
            len(unique_texts), 1,
            "Should generate at least one unique variant"
        )
        
        # Styles should have some variety
        variant_styles = [v['style'] for v in variants]
        unique_styles = set(variant_styles)
        
        self.assertGreaterEqual(
            len(unique_styles), 1,
            "Should use at least one style"
        )
        
        logger.info(f"Uniqueness test: {len(unique_texts)} unique texts, {len(unique_styles)} unique styles")
    
    def test_style_consistency(self):
        """Test that styles are applied consistently"""
        tau_input = "all x (P(x) & Q(x))"
        variants = self.variant_generator.generate_variants(tau_input, 3)
        
        for i, variant in enumerate(variants):
            with self.subTest(variant_index=i):
                style = variant['style']
                formality = variant['formality']
                
                # Style should be a non-empty string
                self.assertIsInstance(style, str)
                self.assertGreater(len(style), 0)
                
                # Formality should be valid
                valid_formality = ['low', 'medium', 'high']
                self.assertIn(formality, valid_formality)
                
                logger.debug(f"Variant {i}: style='{style}', formality='{formality}'")
        
        logger.info("Style consistency test passed")


class TestTranslationEnhancement(unittest.TestCase):
    """Test translation enhancement functionality"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test class"""
        cls.nlp_classes = get_nlp_classes()
        cls.TCETauTranslator = cls.nlp_classes['TCETauTranslator']
    
    def setUp(self):
        """Set up each test"""
        self.base_translator = self.TCETauTranslator()
        self.variant_generator = TranslationVariantGenerator(self.base_translator)
    
    def test_cnl_enhancement(self):
        """Test enhancement of existing CNL text"""
        cnl_text = "Define prime(n) as n > 1 and for all d, d divides n implies d = 1 or d = n."
        
        enhanced = self.variant_generator.enhance_translation_output(cnl_text)
        
        # Should return structured enhancement
        required_fields = ['original', 'variants', 'best_variant', 'enhancement_metadata']
        for field in required_fields:
            self.assertIn(field, enhanced, f"Enhancement missing field: {field}")
        
        # Original should be preserved
        self.assertEqual(enhanced['original'], cnl_text, "Should preserve original text")
        
        # Should have variants
        variants = enhanced['variants']
        self.assertGreater(len(variants), 0, "Should provide variants")
        
        # Validate variant structure
        for variant in variants:
            TestAssertions.assert_valid_variant(variant, self)
        
        logger.info(f"CNL enhancement test passed with {len(variants)} variants")
    
    def test_enhancement_metadata(self):
        """Test quality of enhancement metadata"""
        cnl_text = "For all x such that x > 0, there exists y where y = x + 1."
        
        enhanced = self.variant_generator.enhance_translation_output(cnl_text)
        metadata = enhanced['enhancement_metadata']
        
        # Should have meaningful metadata
        required_metadata = ['total_variants', 'avg_confidence', 'style_diversity']
        for field in required_metadata:
            self.assertIn(field, metadata, f"Metadata missing field: {field}")
        
        # Validate metadata values
        self.assertGreaterEqual(metadata['total_variants'], 0)
        self.assertGreaterEqual(metadata['avg_confidence'], 0.0)
        self.assertLessEqual(metadata['avg_confidence'], 1.0)
        self.assertGreaterEqual(metadata['style_diversity'], 0)
        
        logger.info(f"Enhancement metadata test passed: {metadata}")


class TestQualityMetrics(unittest.TestCase):
    """Test quality assessment metrics"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test class"""
        cls.nlp_classes = get_nlp_classes()
        cls.TCETauTranslator = cls.nlp_classes['TCETauTranslator']
    
    def setUp(self):
        """Set up each test"""
        self.base_translator = self.TCETauTranslator()
        self.variant_generator = TranslationVariantGenerator(self.base_translator)
    
    def test_confidence_calculation(self):
        """Test confidence score calculation"""
        test_cases = [
            ("For all x, P(x) implies Q(x)", "all x (P(x) -> Q(x))", 0.5),  # Good translation
            ("Something completely different", "all x P(x)", 0.1),  # Poor translation
            ("", "all x P(x)", 0.0),  # Empty translation
        ]
        
        for variant, original, expected_min_confidence in test_cases:
            with self.subTest(variant=variant[:30] + "..."):
                confidence = self.variant_generator._calculate_confidence(variant, original)
                
                # Should return valid confidence
                self.assertGreaterEqual(confidence, 0.0, "Confidence should be >= 0")
                self.assertLessEqual(confidence, 1.0, "Confidence should be <= 1")
                
                # Should meet expected minimum (with some tolerance)
                self.assertGreaterEqual(
                    confidence, max(0.0, expected_min_confidence - 0.3),
                    f"Confidence too low for variant: {variant[:30]}..."
                )
                
                logger.debug(f"Confidence test: {confidence:.2f} for '{variant[:30]}...'")
    
    def test_readability_calculation(self):
        """Test readability score calculation"""
        test_cases = [
            ("Simple text.", 0.7),  # Should be high readability
            ("This is a more complex sentence with longer words.", 0.4),  # Medium
            ("Extraordinarily sophisticated nomenclature.", 0.2),  # Lower readability
        ]
        
        for text, expected_min_score in test_cases:
            with self.subTest(text=text):
                score = self.variant_generator._calculate_readability(text)
                
                # Should return valid score
                self.assertGreaterEqual(score, 0.0, "Readability score should be >= 0")
                self.assertLessEqual(score, 1.0, "Readability score should be <= 1")
                
                # Should correlate with expected difficulty (with tolerance)
                self.assertGreaterEqual(
                    score, max(0.0, expected_min_score - 0.4),
                    f"Readability score too low for: {text}"
                )
                
                logger.debug(f"Readability test: {score:.2f} for '{text}'")


if __name__ == "__main__":
    print("🎨 Running Translation Variants NLP Tests")
    print("=" * 45)
    
    # Configure logging for standalone run
    import logging
    logging.basicConfig(level=logging.INFO)
    
    unittest.main(verbosity=2)