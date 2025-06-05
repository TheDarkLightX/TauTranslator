#!/usr/bin/env python3
"""
Test Suite for Advanced Tau Translator
=====================================

Following TDD principles with comprehensive test coverage.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from translators.advanced_llm_translator import (
    AdvancedLLMTranslator, 
    TranslationContext,
    AVAILABLE_FRAMEWORKS
)
from nlp.nlp_requirements_engine import (
    NLPRequirementsEngine,
    RequirementType,
    ExtractedRequirement,
    TauSpecification
)


class TestTranslationContext:
    """Test TranslationContext data class."""
    
    def test_initialization(self):
        """Test context initialization with defaults."""
        context = TranslationContext(
            original_text="test requirement",
            current_translation="always x > 0"
        )
        assert context.original_text == "test requirement"
        assert context.current_translation == "always x > 0"
        assert context.iteration == 0
        assert context.feedback_history == []
        assert context.confidence_scores == []
    
    def test_initialization_with_values(self):
        """Test context initialization with provided values."""
        feedback = [{"iteration": 1, "feedback": "test"}]
        scores = [0.8, 0.9]
        
        context = TranslationContext(
            original_text="test",
            current_translation="r x[t] = 1",
            iteration=2,
            feedback_history=feedback,
            confidence_scores=scores
        )
        assert context.iteration == 2
        assert context.feedback_history == feedback
        assert context.confidence_scores == scores


class TestNLPRequirementsEngine:
    """Test NLP Requirements Engine with TDD approach."""
    
    @pytest.fixture
    def engine(self):
        """Create engine instance without external dependencies."""
        return NLPRequirementsEngine(use_spacy=False, use_transformers=False)
    
    def test_extract_single_requirement(self, engine):
        """Test extracting a single requirement."""
        text = "The temperature must always be between 20 and 80 degrees."
        requirements = engine.extract_requirements(text)
        
        assert len(requirements) == 1
        req = requirements[0]
        assert req.text == text
        assert req.type in [RequirementType.CONSTRAINT, RequirementType.INVARIANT]
        assert 'always' in req.temporal_markers
        assert any('between 20 and 80' in c for c in req.constraints)
    
    def test_extract_multiple_requirements(self, engine):
        """Test extracting multiple requirements."""
        text = """
        The system must monitor temperature sensors.
        Temperature readings must be validated.
        Always log sensor data to file.
        """
        requirements = engine.extract_requirements(text)
        
        assert len(requirements) == 3
        assert any('always' in req.temporal_markers for req in requirements)
    
    def test_requirement_type_classification(self, engine):
        """Test requirement type classification."""
        test_cases = [
            ("Always maintain temperature", RequirementType.INVARIANT),
            ("Monitor performance metrics", RequirementType.FUNCTIONAL),
            ("Emergency stop within 100ms", RequirementType.SAFETY),
            ("System has three states", RequirementType.STATE),
            ("Response time under 1 second", RequirementType.PERFORMANCE)
        ]
        
        for text, expected_type in test_cases:
            req = engine._extract_single_requirement(text)
            assert req.type == expected_type
    
    def test_entity_extraction(self, engine):
        """Test entity extraction from requirements."""
        text = 'Read temperature from "sensors.txt" and write to "output.log"'
        req = engine._extract_single_requirement(text)
        
        assert "sensors.txt" in req.entities['files']
        assert "output.log" in req.entities['files']
        assert 'temperature' in req.entities['variables']
    
    def test_temporal_marker_extraction(self, engine):
        """Test temporal marker extraction."""
        markers_test = [
            ("always check status", ["always"]),
            ("never exceed limit", ["never"]),
            ("sometimes update cache", ["sometimes"]),
            ("check every time", ["every time"]),
            ("respond within 5 seconds", ["within 5 seconds"])
        ]
        
        for text, expected_markers in markers_test:
            req = engine._extract_single_requirement(text)
            for marker in expected_markers:
                assert marker in req.temporal_markers
    
    def test_requirements_to_tau_conversion(self, engine):
        """Test converting requirements to Tau specification."""
        req = ExtractedRequirement(
            text="Always ensure temperature between 20 and 80",
            type=RequirementType.INVARIANT,
            temporal_markers=["always"],
            constraints=["between 20 and 80"],
            confidence=0.9
        )
        req.entities = {"variables": ["temperature"]}
        
        spec = engine.requirements_to_tau([req])
        
        assert len(spec.invariants) > 0
        assert any("always" in inv for inv in spec.invariants)
    
    def test_tau_code_generation(self, engine):
        """Test Tau code generation from specification."""
        spec = TauSpecification(
            streams=["sbf input = ifile(\"data.txt\")"],
            rules=["r temp[t] = input[t]"],
            invariants=["always temp[t] >= 20 & temp[t] <= 80"]
        )
        
        tau_code = engine.generate_tau_code(spec)
        
        assert "# Generated Tau Specification" in tau_code
        assert "sbf input = ifile(\"data.txt\")" in tau_code
        assert "r temp[t] = input[t]" in tau_code
        assert "always temp[t] >= 20 & temp[t] <= 80" in tau_code


class TestAdvancedLLMTranslator:
    """Test Advanced LLM Translator with mocked dependencies."""
    
    @pytest.fixture
    def translator(self):
        """Create translator with pattern-based fallback."""
        with patch.dict('sys.modules', {
            'lmql': MagicMock(),
            'guidance': MagicMock(),
            'transformers': MagicMock(),
            'openai': MagicMock(),
            'anthropic': MagicMock()
        }):
            # Force pattern-based mode
            translator = AdvancedLLMTranslator(preferred_framework="pattern")
            return translator
    
    def test_translator_initialization(self, translator):
        """Test translator initialization."""
        assert translator.framework == "pattern"
        assert translator.tau_patterns is not None
    
    def test_validate_tau_syntax_valid(self, translator):
        """Test Tau syntax validation with valid code."""
        valid_tau = """
        sbf input = ifile("data.txt")
        r temp[t] = input[t]
        always temp[t] >= 20 & temp[t] <= 80
        """
        
        result = translator._validate_tau_syntax(valid_tau)
        
        assert result['valid'] == True
        assert len(result['errors']) == 0
        assert result['confidence'] > 0
        assert 'stream_declaration' in result['patterns_found']
        assert 'rule_definition' in result['patterns_found']
        assert 'temporal_property' in result['patterns_found']
    
    def test_validate_tau_syntax_invalid(self, translator):
        """Test Tau syntax validation with invalid code."""
        invalid_tau = "r temp[t = input[t"  # Missing closing bracket
        
        result = translator._validate_tau_syntax(invalid_tau)
        
        assert result['valid'] == False
        assert len(result['errors']) > 0
        assert "Unmatched brackets" in result['errors'][0]
    
    def test_pattern_based_translation(self, translator):
        """Test fallback pattern-based translation."""
        requirements = "Always ensure temperature stays between 20 and 80 degrees"
        
        tau_code = translator._translate_with_patterns(requirements)
        
        assert tau_code is not None
        assert "always" in tau_code.lower()
    
    def test_auto_feedback_generation(self, translator):
        """Test automatic feedback generation."""
        validation_result = {
            'valid': False,
            'errors': ['Line 1: Syntax error'],
            'patterns_found': ['rule_definition'],
            'confidence': 0.3
        }
        
        feedback = translator._generate_auto_feedback(validation_result)
        
        assert "Fix these syntax errors" in feedback
        assert "Line 1: Syntax error" in feedback
        assert "Consider adding:" in feedback
    
    @pytest.mark.asyncio
    async def test_translate_requirements_basic(self, translator):
        """Test basic requirements translation."""
        requirements = "The system must always monitor temperature"
        
        context = await translator.translate_requirements_to_tau(
            requirements,
            max_iterations=1,
            interactive=False
        )
        
        assert context.original_text == requirements
        assert context.current_translation != ""
        assert context.iteration >= 1
    
    @pytest.mark.asyncio  
    async def test_iterative_refinement(self, translator):
        """Test iterative refinement process."""
        requirements = "Monitor temperature and ensure it stays safe"
        
        # Mock validation to trigger refinement
        with patch.object(translator, '_validate_tau_syntax') as mock_validate:
            # First validation fails, second succeeds
            mock_validate.side_effect = [
                {'valid': False, 'confidence': 0.5, 'errors': ['Missing temporal property'], 'patterns_found': []},
                {'valid': True, 'confidence': 0.9, 'errors': [], 'patterns_found': ['temporal_property']}
            ]
            
            context = await translator.translate_requirements_to_tau(
                requirements,
                max_iterations=3,
                interactive=False
            )
            
            assert context.iteration >= 2
            assert len(context.feedback_history) >= 1


class TestIntegration:
    """Integration tests for the complete pipeline."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_translation(self):
        """Test complete translation pipeline."""
        # Create components
        nlp_engine = NLPRequirementsEngine(use_spacy=False, use_transformers=False)
        translator = AdvancedLLMTranslator(preferred_framework="pattern")
        
        # Complex requirements
        requirements = """
        Create a traffic light control system.
        The system has three lights: red, yellow, and green.
        Only one light can be active at any time.
        Red light lasts 60 seconds.
        Yellow light lasts 5 seconds.
        Green light lasts 30 seconds.
        The sequence must be red -> green -> yellow -> red.
        Always log state changes to file.
        """
        
        # Process through pipeline
        extracted_reqs = nlp_engine.extract_requirements(requirements)
        assert len(extracted_reqs) > 0
        
        # Translate to Tau
        context = await translator.translate_requirements_to_tau(
            requirements,
            max_iterations=2,
            interactive=False
        )
        
        # Validate result
        assert context.current_translation != ""
        validation = translator._validate_tau_syntax(context.current_translation)
        assert validation['confidence'] > 0
    
    def test_performance_requirements(self):
        """Test handling of performance requirements."""
        engine = NLPRequirementsEngine(use_spacy=False, use_transformers=False)
        
        perf_req = "System must respond within 100 milliseconds"
        requirements = engine.extract_requirements(perf_req)
        
        assert len(requirements) == 1
        assert requirements[0].type == RequirementType.PERFORMANCE
        assert "within 100 milliseconds" in requirements[0].temporal_markers


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_requirements(self):
        """Test handling of empty requirements."""
        engine = NLPRequirementsEngine(use_spacy=False, use_transformers=False)
        
        requirements = engine.extract_requirements("")
        assert len(requirements) == 0
        
        spec = engine.requirements_to_tau(requirements)
        assert len(spec.rules) == 0
        assert len(spec.invariants) == 0
    
    def test_malformed_requirements(self):
        """Test handling of malformed requirements."""
        engine = NLPRequirementsEngine(use_spacy=False, use_transformers=False)
        
        malformed = "The the the system must must must"
        requirements = engine.extract_requirements(malformed)
        
        # Should still extract something
        assert len(requirements) == 1
        assert requirements[0].confidence < 0.7  # Lower confidence
    
    @pytest.mark.asyncio
    async def test_translation_timeout(self):
        """Test translation with timeout handling."""
        translator = AdvancedLLMTranslator(preferred_framework="pattern")
        
        # Very long requirements that might timeout
        long_req = " ".join(["Monitor sensor"] * 1000)
        
        context = await translator.translate_requirements_to_tau(
            long_req,
            max_iterations=1,
            interactive=False
        )
        
        # Should complete without hanging
        assert context.current_translation != ""


# Performance benchmarks
class TestPerformance:
    """Performance tests for optimization validation."""
    
    def test_nlp_engine_performance(self, benchmark):
        """Benchmark NLP engine performance."""
        engine = NLPRequirementsEngine(use_spacy=False, use_transformers=False)
        
        requirements = "The system must always monitor temperature and pressure sensors"
        
        # Benchmark requirement extraction
        result = benchmark(engine.extract_requirements, requirements)
        assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_translation_performance(self, benchmark):
        """Benchmark translation performance."""
        translator = AdvancedLLMTranslator(preferred_framework="pattern")
        
        requirements = "Always ensure temperature between 20 and 80"
        
        # Benchmark async translation
        async def translate():
            return await translator.translate_requirements_to_tau(
                requirements, max_iterations=1, interactive=False
            )
        
        result = await benchmark(translate)
        assert result.current_translation != ""


if __name__ == "__main__":
    pytest.main([__file__, "-v"])