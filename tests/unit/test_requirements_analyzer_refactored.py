"""
Comprehensive unit tests for refactored requirements analyzer.

Tests follow BDD principles and ensure mutation resistance.
All tests use clear Given-When-Then structure.

Copyright: DarkLightX / Dana Edwards
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from typing import List

from src.tau_translator_omega.core_engine.nlp_enhanced.requirements_analyzer_refactored import (
    # Domain types
    RequirementText, SentenceText, SectionTitle, SectionContent,
    EntityName, PredicateName, ConfidenceScore, LogicalFormula,
    
    # Enums and data classes
    RequirementType, LogicalStructure, FormalConstraint, RequirementItem,
    
    # Infrastructure
    SpacyNLPProcessor, PatternRepository,
    
    # Business logic
    DocumentSplitter, RequirementClassifier, LogicalAnalyzer,
    ConstraintExtractor, ConfidenceCalculator, SectionCategorizer,
    
    # Service
    RequirementAnalysisService, RequirementsAnalyzer,
    
    # Factory
    create_requirements_analyzer
)


class TestDomainTypes:
    """Test domain type behaviors and properties."""
    
    def test_logical_structure_properties(self):
        """Test LogicalStructure computed properties."""
        # Given: Empty logical structure
        empty_structure = LogicalStructure()
        
        # Then: All properties are False
        assert empty_structure.has_quantification is False
        assert empty_structure.has_conditionals is False
        assert empty_structure.has_temporal is False
        
        # Given: Structure with quantifiers
        with_quantifiers = LogicalStructure(quantifiers=["all", "every"])
        
        # Then: Only quantification is True
        assert with_quantifiers.has_quantification is True
        assert with_quantifiers.has_conditionals is False
        assert with_quantifiers.has_temporal is False
        
        # Given: Structure with all elements
        full_structure = LogicalStructure(
            quantifiers=["all"],
            conditionals=["if", "then"],
            temporal_operators=["before", "after"]
        )
        
        # Then: All properties are True
        assert full_structure.has_quantification is True
        assert full_structure.has_conditionals is True
        assert full_structure.has_temporal is True
    
    def test_requirement_item_quantification_property(self):
        """Test RequirementItem quantification property."""
        # Given: Requirement with quantified logical structure
        logical_structure = LogicalStructure(quantifiers=["forall"])
        requirement = RequirementItem(
            raw_text=RequirementText("For all x, x > 0"),
            type=RequirementType.CONSTRAINT,
            category="validation",
            entities=[],
            predicates=[],
            logical_structure=logical_structure,
            formal_constraints=[],
            confidence=ConfidenceScore(0.8)
        )
        
        # Then: Requirement has quantification
        assert requirement.has_quantification is True
    
    def test_formal_constraint_immutability(self):
        """Test that FormalConstraint is immutable."""
        constraint = FormalConstraint(
            constraint_type="equality",
            variables=["x"],
            predicates=["equals"],
            logical_form=LogicalFormula("equals(x, 5)"),
            confidence=ConfidenceScore(0.9)
        )
        
        # Then: Cannot modify attributes
        with pytest.raises(AttributeError):
            constraint.constraint_type = "inequality"


class TestPatternRepository:
    """Test pattern repository behaviors."""
    
    def test_get_requirement_indicators_returns_all_types(self):
        """Test that all requirement types have indicators."""
        # When: Getting requirement indicators
        indicators = PatternRepository.get_requirement_indicators()
        
        # Then: All requirement types are present
        assert len(indicators) == 7
        for req_type in RequirementType:
            assert req_type in indicators
            assert len(indicators[req_type]) > 0
    
    def test_get_mathematical_patterns_returns_tuples(self):
        """Test mathematical patterns structure."""
        # When: Getting mathematical patterns
        patterns = PatternRepository.get_mathematical_patterns()
        
        # Then: Each pattern is a tuple of (regex, type)
        assert len(patterns) == 6
        for pattern, constraint_type in patterns:
            assert isinstance(pattern, str)
            assert isinstance(constraint_type, str)
            assert constraint_type in ['equality', 'greater_than', 'less_than', 'prime', 'even', 'odd']
    
    def test_temporal_patterns_include_units(self):
        """Test temporal patterns include time units."""
        # When: Getting temporal patterns
        patterns = PatternRepository.get_temporal_patterns()
        
        # Then: Patterns include time units
        pattern_text = ' '.join(patterns)
        assert 'seconds' in pattern_text
        assert 'minutes' in pattern_text
        assert 'hours' in pattern_text
        assert 'milliseconds' in pattern_text


class TestDocumentSplitter:
    """Test document splitting functionality."""
    
    def test_given_flat_document_when_splitting_then_returns_single_section(self):
        """Test splitting document without headers."""
        # Given: Document without section headers
        document = """This is a requirement.
        The system must validate input.
        All users shall be authenticated."""
        
        # When: Splitting into sections
        sections = DocumentSplitter.split_into_sections(document)
        
        # Then: Single general section returned
        assert len(sections) == 1
        assert sections[0][0] == "General"
        assert "requirement" in sections[0][1]
        assert "validate" in sections[0][1]
        assert "authenticated" in sections[0][1]
    
    def test_given_numbered_sections_when_splitting_then_recognizes_headers(self):
        """Test recognition of numbered section headers."""
        # Given: Document with numbered sections
        document = """1. Introduction
        This is the introduction.
        
        2. Requirements
        The system must be fast.
        
        3. Security
        All data must be encrypted."""
        
        # When: Splitting into sections
        sections = DocumentSplitter.split_into_sections(document)
        
        # Then: Three sections recognized
        assert len(sections) == 3
        assert sections[0][0] == "1. Introduction"
        assert sections[1][0] == "2. Requirements"
        assert sections[2][0] == "3. Security"
        assert "encrypted" in sections[2][1]
    
    def test_given_uppercase_headers_when_splitting_then_recognizes_sections(self):
        """Test recognition of uppercase headers."""
        # Given: Document with uppercase headers
        document = """VALIDATION REQUIREMENTS
        Input must be validated.
        
        PERFORMANCE CRITERIA
        Response time under 100ms."""
        
        # When: Splitting into sections
        sections = DocumentSplitter.split_into_sections(document)
        
        # Then: Sections recognized
        assert len(sections) == 2
        assert sections[0][0] == "VALIDATION REQUIREMENTS"
        assert sections[1][0] == "PERFORMANCE CRITERIA"
    
    def test_given_empty_sections_when_splitting_then_excludes_them(self):
        """Test that empty sections are excluded."""
        # Given: Document with empty sections
        document = """Section 1
        
        Section 2
        This has content.
        
        Section 3
        
        Section 4
        More content here."""
        
        # When: Splitting into sections
        sections = DocumentSplitter.split_into_sections(document)
        
        # Then: Only sections with content included
        assert len(sections) == 2
        assert sections[0][0] == "Section 2"
        assert sections[1][0] == "Section 4"


class TestRequirementClassifier:
    """Test requirement classification."""
    
    def test_given_constraint_indicators_when_classifying_then_returns_constraint(self):
        """Test classification of constraint requirements."""
        # Given: Classifier with indicators
        indicators = PatternRepository.get_requirement_indicators()
        classifier = RequirementClassifier(indicators)
        
        # When: Classifying sentences with constraint words
        sentences = [
            "The system must validate all inputs",
            "Users shall be authenticated",
            "Password should be at least 8 characters",
            "Authentication is required for access",
            "Encryption is mandatory"
        ]
        
        # Then: All classified as constraints
        for sentence in sentences:
            result = classifier.classify(SentenceText(sentence))
            assert result == RequirementType.CONSTRAINT
    
    def test_given_behavior_indicators_when_classifying_then_returns_behavior(self):
        """Test classification of behavior requirements."""
        # Given: Classifier and behavior sentence
        indicators = PatternRepository.get_requirement_indicators()
        classifier = RequirementClassifier(indicators)
        
        sentences = [
            "When user clicks submit, validate the form",
            "If temperature exceeds 100, trigger alarm",
            "Upon startup, load configuration"
        ]
        
        # Then: Classified as behavior
        for sentence in sentences:
            result = classifier.classify(SentenceText(sentence))
            assert result == RequirementType.BEHAVIOR
    
    def test_given_multiple_indicators_when_classifying_then_returns_highest_score(self):
        """Test classification with multiple indicator types."""
        # Given: Sentence with multiple indicators
        indicators = PatternRepository.get_requirement_indicators()
        classifier = RequirementClassifier(indicators)
        
        # Sentence has both constraint and validation indicators
        sentence = SentenceText("The system must validate and verify all inputs")
        
        # When: Classifying
        result = classifier.classify(sentence)
        
        # Then: Returns type with most indicators (validation has 2: validate, verify)
        assert result == RequirementType.VALIDATION
    
    def test_given_no_indicators_when_classifying_then_returns_constraint(self):
        """Test default classification."""
        # Given: Sentence without indicators
        indicators = PatternRepository.get_requirement_indicators()
        classifier = RequirementClassifier(indicators)
        
        sentence = SentenceText("The temperature is measured in Celsius")
        
        # When: Classifying
        result = classifier.classify(sentence)
        
        # Then: Defaults to CONSTRAINT
        assert result == RequirementType.CONSTRAINT


class TestLogicalAnalyzer:
    """Test logical structure analysis."""
    
    def test_given_quantified_sentence_when_analyzing_then_extracts_quantifiers(self):
        """Test quantifier extraction."""
        # Given: Analyzer and quantified sentences
        analyzer = LogicalAnalyzer(PatternRepository())
        
        test_cases = [
            ("For all integers n, n + 0 = n", ["all"]),
            ("Every user must have a password", ["every"]),
            ("∀x ∈ ℝ, x² ≥ 0", ["∀"]),
            ("There exists some value that satisfies", ["some", "exists"])
        ]
        
        # When/Then: Analyzing each sentence
        for sentence, expected_quantifiers in test_cases:
            result = analyzer.analyze(SentenceText(sentence))
            assert all(q in result.quantifiers for q in expected_quantifiers)
            assert result.has_quantification is True
    
    def test_given_conditional_sentence_when_analyzing_then_extracts_conditionals(self):
        """Test conditional extraction."""
        # Given: Analyzer and conditional sentences
        analyzer = LogicalAnalyzer(PatternRepository())
        
        test_cases = [
            ("If x > 0 then x is positive", ["if", "then"]),
            ("When temperature rises, pressure increases", ["when"]),
            ("Provided that input is valid, process continues", ["provided that"])
        ]
        
        # When/Then: Analyzing each sentence
        for sentence, expected_conditionals in test_cases:
            result = analyzer.analyze(SentenceText(sentence))
            assert all(c in result.conditionals for c in expected_conditionals)
            assert result.has_conditionals is True
    
    def test_given_temporal_sentence_when_analyzing_then_extracts_temporal_operators(self):
        """Test temporal operator extraction."""
        # Given: Analyzer and temporal sentences
        analyzer = LogicalAnalyzer(PatternRepository())
        
        test_cases = [
            ("Complete within 5 seconds", ["within 5"]),
            ("Process before midnight", ["before"]),
            ("Wait until signal received", ["until"]),
            ("Execute after 10 milliseconds", ["after 10"])
        ]
        
        # When/Then: Analyzing each sentence
        for sentence, expected_temporal in test_cases:
            result = analyzer.analyze(SentenceText(sentence))
            assert any(t in str(result.temporal_operators) for t in expected_temporal)
            assert result.has_temporal is True


class TestConstraintExtractor:
    """Test formal constraint extraction."""
    
    def test_given_mathematical_sentence_when_extracting_then_creates_constraints(self):
        """Test extraction of mathematical constraints."""
        # Given: Extractor and mathematical sentences
        extractor = ConstraintExtractor(PatternRepository())
        
        # When: Extracting from equality
        constraints = extractor.extract(
            SentenceText("x equals 5"),
            [EntityName("x")],
            [PredicateName("equals")]
        )
        
        # Then: Constraint created correctly
        assert len(constraints) == 1
        assert constraints[0].constraint_type == "equality"
        assert constraints[0].variables == ["x"]
        assert constraints[0].logical_form == "equality(x, 5)"
        assert constraints[0].confidence == 0.8
    
    def test_given_comparison_sentence_when_extracting_then_creates_comparison_constraints(self):
        """Test extraction of comparison constraints."""
        # Given: Extractor
        extractor = ConstraintExtractor(PatternRepository())
        
        test_cases = [
            ("n is greater than 10", "greater_than", "greater_than(n, 10)"),
            ("count less than 100", "less_than", "less_than(count, 100)"),
            ("x > 0", "greater_than", "greater_than(x, 0)")
        ]
        
        # When/Then: Testing each case
        for sentence, expected_type, expected_form in test_cases:
            constraints = extractor.extract(SentenceText(sentence), [], [])
            assert len(constraints) >= 1
            assert any(c.constraint_type == expected_type for c in constraints)
            assert any(c.logical_form == expected_form for c in constraints)
    
    def test_given_property_sentence_when_extracting_then_creates_unary_constraints(self):
        """Test extraction of unary property constraints."""
        # Given: Extractor
        extractor = ConstraintExtractor(PatternRepository())
        
        test_cases = [
            ("n is prime", "prime", "prime(n)"),
            ("x is even", "even", "even(x)"),
            ("y is odd", "odd", "odd(y)")
        ]
        
        # When/Then: Testing each case
        for sentence, expected_type, expected_form in test_cases:
            constraints = extractor.extract(SentenceText(sentence), [], [])
            assert len(constraints) >= 1
            assert constraints[0].constraint_type == expected_type
            assert constraints[0].logical_form == expected_form


class TestConfidenceCalculator:
    """Test confidence score calculation."""
    
    def test_given_empty_analysis_when_calculating_then_returns_base_score(self):
        """Test base confidence score."""
        # Given: Empty analysis results
        confidence = ConfidenceCalculator.calculate(
            SentenceText("Some text"),
            entities=[],
            predicates=[],
            logical_structure=LogicalStructure()
        )
        
        # Then: Returns base score
        assert confidence == 0.5
    
    def test_given_structured_requirement_when_calculating_then_increases_score(self):
        """Test confidence increase for structured requirements."""
        # Given: Well-structured requirement
        confidence = ConfidenceCalculator.calculate(
            SentenceText("The system must validate input"),
            entities=[EntityName("system"), EntityName("input")],
            predicates=[PredicateName("validate")],
            logical_structure=LogicalStructure(
                quantifiers=["all"],
                conditionals=["if", "then"]
            )
        )
        
        # Then: Score increased for structure and formality
        assert confidence > 0.5
        assert confidence >= 0.8  # Base + entities + predicates + quantification + conditionals + "must"
    
    def test_given_ambiguous_language_when_calculating_then_decreases_score(self):
        """Test confidence decrease for ambiguous language."""
        # Given: Requirement with ambiguous words
        confidence = ConfidenceCalculator.calculate(
            SentenceText("The system should properly handle appropriate input"),
            entities=[EntityName("system"), EntityName("input")],
            predicates=[PredicateName("handle")],
            logical_structure=LogicalStructure()
        )
        
        # Then: Score decreased for ambiguity
        # Base (0.5) + entities (0.1) + predicates (0.1) - properly (0.1) - appropriate (0.1) = 0.5
        assert confidence == 0.5
    
    def test_confidence_score_boundaries(self):
        """Test confidence score stays within bounds."""
        # Test maximum score scenario
        max_confidence = ConfidenceCalculator.calculate(
            SentenceText("The system must shall should required specified validate"),
            entities=[EntityName("system")],
            predicates=[PredicateName("validate")],
            logical_structure=LogicalStructure(
                quantifiers=["all"],
                conditionals=["if"]
            )
        )
        assert max_confidence <= 1.0
        
        # Test minimum score scenario
        min_confidence = ConfidenceCalculator.calculate(
            SentenceText("properly appropriately suitable adequate reasonable"),
            entities=[],
            predicates=[],
            logical_structure=LogicalStructure()
        )
        assert min_confidence >= 0.0


class TestSectionCategorizer:
    """Test section categorization."""
    
    def test_given_titled_sections_when_categorizing_then_returns_correct_category(self):
        """Test categorization based on keywords."""
        test_cases = [
            ("Input Validation Rules", "validation"),
            ("System Verification Process", "verification"),
            ("Output Format Specification", "output"),
            ("Performance Requirements", "performance"),
            ("Security and Authentication", "security"),
            ("System Behavior Description", "behavior"),
            ("Miscellaneous Notes", "general")
        ]
        
        for title, expected_category in test_cases:
            # When: Categorizing
            category = SectionCategorizer.categorize(SectionTitle(title))
            
            # Then: Correct category returned
            assert category == expected_category
    
    def test_given_mixed_case_titles_when_categorizing_then_case_insensitive(self):
        """Test case-insensitive categorization."""
        titles = [
            "VALIDATION RULES",
            "Validation Rules",
            "validation rules",
            "VaLiDaTiOn RuLeS"
        ]
        
        for title in titles:
            category = SectionCategorizer.categorize(SectionTitle(title))
            assert category == "validation"


class TestSpacyNLPProcessor:
    """Test SpaCy NLP processor with and without SpaCy."""
    
    def test_given_no_spacy_when_processing_then_uses_fallback(self):
        """Test fallback processing without SpaCy."""
        # Given: Processor without SpaCy
        with patch('src.tau_translator_omega.core_engine.nlp_enhanced.requirements_analyzer_refactored.SpacyNLPProcessor._load_spacy_model') as mock_load:
            mock_load.return_value = None
            processor = SpacyNLPProcessor()
        
        # When: Processing sentences
        sentences = processor.process_sentences("First sentence. Second sentence! Third sentence?")
        
        # Then: Fallback splitting works
        assert len(sentences) == 3
        assert sentences[0] == "First sentence"
        assert sentences[1] == "Second sentence"
        assert sentences[2] == "Third sentence"
    
    def test_given_no_spacy_when_extracting_entities_then_uses_patterns(self):
        """Test entity extraction fallback."""
        # Given: Processor without SpaCy
        with patch('src.tau_translator_omega.core_engine.nlp_enhanced.requirements_analyzer_refactored.SpacyNLPProcessor._load_spacy_model') as mock_load:
            mock_load.return_value = None
            processor = SpacyNLPProcessor()
        
        # When: Extracting entities
        entities = processor.extract_entities("The system validates user input from the database")
        
        # Then: Pattern-based extraction works
        assert EntityName("system") in entities
        assert EntityName("user") in entities
        assert EntityName("input") in entities
        assert EntityName("database") in entities
    
    def test_given_no_spacy_when_extracting_predicates_then_uses_patterns(self):
        """Test predicate extraction fallback."""
        # Given: Processor without SpaCy
        with patch('src.tau_translator_omega.core_engine.nlp_enhanced.requirements_analyzer_refactored.SpacyNLPProcessor._load_spacy_model') as mock_load:
            mock_load.return_value = None
            processor = SpacyNLPProcessor()
        
        # When: Extracting predicates
        predicates = processor.extract_predicates("The system must validate and verify data")
        
        # Then: Pattern-based extraction finds verbs
        assert any("must" in p for p in predicates)
        assert any("validate" in p for p in predicates)


class TestRequirementAnalysisService:
    """Test requirement analysis service orchestration."""
    
    def test_given_short_sentence_when_analyzing_then_returns_none(self):
        """Test that short sentences are skipped."""
        # Given: Service with mocked components
        nlp = Mock()
        classifier = Mock()
        analyzer = Mock()
        extractor = Mock()
        
        service = RequirementAnalysisService(nlp, classifier, analyzer, extractor)
        
        # When: Analyzing short sentence
        result = service.analyze_sentence(SentenceText("Too short"))
        
        # Then: Returns None without calling components
        assert result is None
        nlp.extract_entities.assert_not_called()
        classifier.classify.assert_not_called()
    
    def test_given_valid_sentence_when_analyzing_then_orchestrates_components(self):
        """Test component orchestration."""
        # Given: Service with mocked components
        nlp = Mock()
        nlp.extract_entities.return_value = [EntityName("system")]
        nlp.extract_predicates.return_value = [PredicateName("validate")]
        
        classifier = Mock()
        classifier.classify.return_value = RequirementType.VALIDATION
        
        analyzer = Mock()
        analyzer.analyze.return_value = LogicalStructure(quantifiers=["all"])
        
        extractor = Mock()
        extractor.extract.return_value = []
        
        service = RequirementAnalysisService(nlp, classifier, analyzer, extractor)
        
        # When: Analyzing valid sentence
        sentence = SentenceText("The system must validate all user inputs")
        result = service.analyze_sentence(sentence)
        
        # Then: All components called and result assembled
        assert result is not None
        assert result.type == RequirementType.VALIDATION
        assert result.entities == [EntityName("system")]
        assert result.predicates == [PredicateName("validate")]
        assert result.has_quantification is True
        
        # Verify orchestration
        classifier.classify.assert_called_once_with(sentence)
        nlp.extract_entities.assert_called_once_with(sentence)
        nlp.extract_predicates.assert_called_once_with(sentence)
        analyzer.analyze.assert_called_once_with(sentence)


class TestRequirementsAnalyzerIntegration:
    """Integration tests for the full analyzer."""
    
    def test_extract_requirements_from_simple_text(self):
        """Test requirement extraction from simple text."""
        # Given: Analyzer
        analyzer = create_requirements_analyzer()
        
        # When: Extracting from text
        text = """
        The system must validate all input data.
        When user submits form, check required fields.
        Response time shall be under 100 milliseconds.
        """
        
        requirements = analyzer.extract_requirements(text)
        
        # Then: Requirements extracted
        assert len(requirements) >= 2
        
        # Verify first requirement
        validation_req = next((r for r in requirements if "validate" in r.raw_text), None)
        assert validation_req is not None
        assert validation_req.type in [RequirementType.CONSTRAINT, RequirementType.VALIDATION]
        
        # Verify performance requirement
        perf_req = next((r for r in requirements if "milliseconds" in r.raw_text), None)
        assert perf_req is not None
        assert perf_req.type == RequirementType.PERFORMANCE
    
    def test_extract_requirements_from_document_with_sections(self):
        """Test extraction from structured document."""
        # Given: Analyzer and structured document
        analyzer = create_requirements_analyzer()
        
        document = """
        1. VALIDATION REQUIREMENTS
        All input must be validated before processing.
        Check that numbers are positive.
        
        2. PERFORMANCE CRITERIA
        System must respond within 50 milliseconds.
        Throughput shall exceed 1000 requests per second.
        
        3. SECURITY
        Users must be authenticated before access.
        All data must be encrypted at rest.
        """
        
        # When: Extracting from document
        requirements = analyzer.extract_requirements_from_document(document)
        
        # Then: Requirements extracted with correct categories
        assert len(requirements) >= 5
        
        # Check categorization
        validation_reqs = [r for r in requirements if r.category == "validation"]
        assert len(validation_reqs) >= 2
        
        performance_reqs = [r for r in requirements if r.category == "performance"]
        assert len(performance_reqs) >= 2
        
        security_reqs = [r for r in requirements if r.category == "security"]
        assert len(security_reqs) >= 2
    
    def test_extract_mathematical_constraints(self):
        """Test extraction of mathematical constraints."""
        # Given: Analyzer
        analyzer = create_requirements_analyzer()
        
        text = """
        For all integers n, n must be greater than 0.
        The value x equals 42.
        Every prime number p is odd except 2.
        """
        
        # When: Extracting requirements
        requirements = analyzer.extract_requirements(text)
        
        # Then: Mathematical constraints extracted
        assert len(requirements) >= 2
        
        # Check for formal constraints
        constraints_found = []
        for req in requirements:
            constraints_found.extend(req.formal_constraints)
        
        # Should find at least "greater_than" and "equality" constraints
        constraint_types = [c.constraint_type for c in constraints_found]
        assert "greater_than" in constraint_types or "equality" in constraint_types


class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error conditions."""
    
    def test_empty_document_returns_empty_list(self):
        """Test handling of empty input."""
        analyzer = create_requirements_analyzer()
        
        assert analyzer.extract_requirements("") == []
        assert analyzer.extract_requirements("   \n  \t  ") == []
        assert analyzer.extract_requirements_from_document("") == []
    
    def test_single_word_sentences_ignored(self):
        """Test that single word sentences are ignored."""
        analyzer = create_requirements_analyzer()
        
        text = "Yes. No. Maybe. The system must validate input. OK."
        requirements = analyzer.extract_requirements(text)
        
        # Only the actual requirement should be extracted
        assert len(requirements) == 1
        assert "validate" in requirements[0].raw_text
    
    def test_unicode_handling(self):
        """Test handling of unicode characters."""
        analyzer = create_requirements_analyzer()
        
        text = "The system must handle émojis 🎉 and 中文 characters. ∀x ∈ ℝ, x² ≥ 0."
        requirements = analyzer.extract_requirements(text)
        
        assert len(requirements) >= 1
        # Should handle mathematical symbols
        if len(requirements) > 1:
            math_req = requirements[1]
            assert math_req.logical_structure.has_quantification
    
    def test_very_long_sentence_handling(self):
        """Test handling of very long sentences."""
        analyzer = create_requirements_analyzer()
        
        # Create a very long but valid sentence
        long_sentence = "The system must " + " and ".join([f"validate field{i}" for i in range(50)]) + "."
        
        requirements = analyzer.extract_requirements(long_sentence)
        
        assert len(requirements) == 1
        assert requirements[0].type == RequirementType.CONSTRAINT
        assert len(requirements[0].entities) > 0