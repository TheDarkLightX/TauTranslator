Module src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer_refactored
=====================================================================================================
Requirements Analyzer following the Intentional Disclosure Principle.

This module analyzes natural language requirements for conversion to formal Tau specifications.
- All methods under 10 lines with single responsibility
- Domain types replace primitives for type safety
- I/O operations isolated in repositories
- Business logic separated from infrastructure

Copyright: DarkLightX / Dana Edwards

Functions
---------

`create_requirements_analyzer() ‑> src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer_refactored.RequirementsAnalyzer`
:   Factory function to create a requirements analyzer.

Classes
-------

`ConfidenceCalculator()`
:   Calculates confidence scores for requirements.

    ### Static methods

    `calculate(sentence: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer_refactored.SentenceText, entities: List[src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer_refactored.EntityName], predicates: List[src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer_refactored.PredicateName], logical_structure: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer_refactored.LogicalStructure) ‑> src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer_refactored.ConfidenceScore`
    :   Calculate confidence score for requirement extraction.

`ConstraintExtractor(pattern_repo: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer_refactored.PatternRepository)`
:   Extracts formal constraints from sentences.
    
    Initialize with pattern repository.

    ### Methods

    `extract(self, sentence: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer_refactored.SentenceText, entities: List[src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer_refactored.EntityName], predicates: List[src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer_refactored.PredicateName]) ‑> List[src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer_refactored.FormalConstraint]`
    :   Extract formal constraints from sentence.

`DocumentSplitter()`
:   Splits documents into sections and sentences.

    ### Static methods

    `split_into_sections(document: str) ‑> List[Tuple[src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer_refactored.SectionTitle, src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer_refactored.SectionContent]]`
    :   Split document into sections with headers.

`FormalConstraint(constraint_type: str, variables: List[str], predicates: List[str], logical_form: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer_refactored.LogicalFormula, confidence: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer_refactored.ConfidenceScore)`
:   Represents a formal constraint extracted from requirements.

    ### Instance variables

    `confidence: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer_refactored.ConfidenceScore`
    :

    `constraint_type: str`
    :

    `logical_form: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer_refactored.LogicalFormula`
    :

    `predicates: List[str]`
    :

    `variables: List[str]`
    :

`LogicalAnalyzer(pattern_repo: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer_refactored.PatternRepository)`
:   Analyzes logical structure of sentences.
    
    Initialize with pattern repository.

    ### Methods

    `analyze(self, sentence: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer_refactored.SentenceText) ‑> src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer_refactored.LogicalStructure`
    :   Analyze logical structure of sentence.

`LogicalStructure(quantifiers: List[str] = <factory>, conditionals: List[str] = <factory>, logical_operators: List[str] = <factory>, temporal_operators: List[str] = <factory>)`
:   Represents the logical structure of a requirement.

    ### Instance variables

    `conditionals: List[str]`
    :

    `has_conditionals: bool`
    :   Check if structure has conditionals.

    `has_quantification: bool`
    :   Check if structure has quantification.

    `has_temporal: bool`
    :   Check if structure has temporal operators.

    `logical_operators: List[str]`
    :

    `quantifiers: List[str]`
    :

    `temporal_operators: List[str]`
    :

`NLPProcessor(*args, **kwargs)`
:   Protocol for NLP processing implementations.

    ### Ancestors (in MRO)

    * typing.Protocol
    * typing.Generic

    ### Methods

    `extract_entities(self, sentence: str) ‑> List[src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer_refactored.EntityName]`
    :   Extract entities from sentence.

    `extract_predicates(self, sentence: str) ‑> List[src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer_refactored.PredicateName]`
    :   Extract predicates from sentence.

    `process_sentences(self, text: str) ‑> List[src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer_refactored.SentenceText]`
    :   Split text into sentences.

`PatternRepository()`
:   Repository of linguistic patterns for requirement analysis.

    ### Static methods

    `get_conditional_patterns() ‑> List[str]`
    :   Get conditional regex patterns.

    `get_logical_operator_patterns() ‑> List[str]`
    :   Get logical operator regex patterns.

    `get_mathematical_patterns() ‑> List[Tuple[str, str]]`
    :   Get mathematical constraint patterns.

    `get_quantifier_patterns() ‑> List[str]`
    :   Get quantifier regex patterns.

    `get_requirement_indicators() ‑> Dict[src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer_refactored.RequirementType, List[str]]`
    :   Get indicators for each requirement type.

    `get_temporal_patterns() ‑> List[str]`
    :   Get temporal regex patterns.

`RequirementAnalysisService(nlp_processor: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer_refactored.NLPProcessor, classifier: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer_refactored.RequirementClassifier, logical_analyzer: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer_refactored.LogicalAnalyzer, constraint_extractor: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer_refactored.ConstraintExtractor)`
:   Orchestrates requirement analysis operations.
    
    Initialize with analysis components.

    ### Methods

    `analyze_sentence(self, sentence: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer_refactored.SentenceText) ‑> src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer_refactored.RequirementItem | None`
    :   Analyze single sentence for requirements.

    `analyze_text(self, text: str) ‑> List[src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer_refactored.RequirementItem]`
    :   Analyze text for requirements.

`RequirementClassifier(indicators: Dict[src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer_refactored.RequirementType, List[str]])`
:   Classifies requirements by type.
    
    Initialize with requirement indicators.

    ### Methods

    `classify(self, sentence: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer_refactored.SentenceText) ‑> src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer_refactored.RequirementType`
    :   Classify requirement type based on indicators.

`RequirementItem(raw_text: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer_refactored.RequirementText, type: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer_refactored.RequirementType, category: str, entities: List[src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer_refactored.EntityName], predicates: List[src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer_refactored.PredicateName], logical_structure: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer_refactored.LogicalStructure, formal_constraints: List[src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer_refactored.FormalConstraint], confidence: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer_refactored.ConfidenceScore)`
:   Represents a single extracted requirement.

    ### Instance variables

    `category: str`
    :

    `confidence: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer_refactored.ConfidenceScore`
    :

    `entities: List[src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer_refactored.EntityName]`
    :

    `formal_constraints: List[src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer_refactored.FormalConstraint]`
    :

    `has_quantification: bool`
    :   Check if requirement has quantification.

    `logical_structure: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer_refactored.LogicalStructure`
    :

    `predicates: List[src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer_refactored.PredicateName]`
    :

    `raw_text: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer_refactored.RequirementText`
    :

    `type: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer_refactored.RequirementType`
    :

`RequirementType(*args, **kwds)`
:   Types of requirements that can be extracted.

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `BEHAVIOR`
    :

    `CONSTRAINT`
    :

    `EXCEPTION`
    :

    `OUTPUT`
    :

    `PERFORMANCE`
    :

    `SECURITY`
    :

    `VALIDATION`
    :

`RequirementsAnalyzer()`
:   Main analyzer for extracting structured requirements from natural language.
    
    Initialize the requirements analyzer.

    ### Methods

    `extract_requirements(self, text: str) ‑> List[src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer_refactored.RequirementItem]`
    :   Extract structured requirements from natural language text.

    `extract_requirements_from_document(self, document: str) ‑> List[src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer_refactored.RequirementItem]`
    :   Extract requirements from a complete requirements document.

`SectionCategorizer()`
:   Categorizes requirements based on section titles.

    ### Static methods

    `categorize(section_title: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer_refactored.SectionTitle) ‑> str`
    :   Categorize requirement based on section title.

`SpacyNLPProcessor()`
:   SpaCy-based NLP processor.
    
    Initialize SpaCy processor.

    ### Methods

    `extract_entities(self, sentence: str) ‑> List[src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer_refactored.EntityName]`
    :   Extract entities using SpaCy NER.

    `extract_predicates(self, sentence: str) ‑> List[src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer_refactored.PredicateName]`
    :   Extract predicates using SpaCy.

    `process_sentences(self, text: str) ‑> List[src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer_refactored.SentenceText]`
    :   Split text into sentences using SpaCy.