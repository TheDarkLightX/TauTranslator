Module src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements
=================================================================================
Requirements analysis module.

This module provides comprehensive natural language requirements analysis
following the Intentional Disclosure Principle.

Copyright: DarkLightX / Dana Edwards

Sub-modules
-----------
* src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.analyzers
* src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.domain_types
* src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.nlp_processor
* src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.pattern_repository
* src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.service

Classes
-------

`ConfidenceCalculator()`
:   Calculates confidence scores for requirements.

    ### Static methods

    `calculate(sentence: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.domain_types.SentenceText, entities: List[src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.domain_types.EntityName], predicates: List[src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.domain_types.PredicateName], logical_structure: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.domain_types.LogicalStructure) ‑> src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.domain_types.ConfidenceScore`
    :   Calculate confidence score for requirement extraction.

`ConstraintExtractor(pattern_repo: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.pattern_repository.PatternRepository)`
:   Extracts formal constraints from sentences.
    
    Initialize with pattern repository.

    ### Methods

    `extract(self, sentence: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.domain_types.SentenceText, entities: List[src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.domain_types.EntityName], predicates: List[src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.domain_types.PredicateName]) ‑> List[src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.domain_types.FormalConstraint]`
    :   Extract formal constraints from sentence.

`DocumentSplitter()`
:   Splits documents into sections and sentences.

    ### Static methods

    `split_into_sections(document: str) ‑> List[Tuple[src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.domain_types.SectionTitle, src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.domain_types.SectionContent]]`
    :   Split document into sections with headers.

`FormalConstraint(constraint_type: str, variables: List[str], predicates: List[str], logical_form: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.domain_types.LogicalFormula, confidence: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.domain_types.ConfidenceScore)`
:   Represents a formal constraint extracted from requirements.

    ### Instance variables

    `confidence: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.domain_types.ConfidenceScore`
    :

    `constraint_type: str`
    :

    `logical_form: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.domain_types.LogicalFormula`
    :

    `predicates: List[str]`
    :

    `variables: List[str]`
    :

`LogicalAnalyzer(pattern_repo: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.pattern_repository.PatternRepository)`
:   Analyzes logical structure of sentences.
    
    Initialize with pattern repository.

    ### Methods

    `analyze(self, sentence: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.domain_types.SentenceText) ‑> src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.domain_types.LogicalStructure`
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

    `get_requirement_indicators() ‑> Dict[src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.domain_types.RequirementType, List[str]]`
    :   Get indicators for each requirement type.

    `get_temporal_patterns() ‑> List[str]`
    :   Get temporal regex patterns.

`RequirementAnalysisService(nlp_processor: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.nlp_processor.NLPProcessor, classifier: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.analyzers.RequirementClassifier, logical_analyzer: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.analyzers.LogicalAnalyzer, constraint_extractor: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.analyzers.ConstraintExtractor)`
:   Orchestrates requirement analysis operations.
    
    Initialize with analysis components.

    ### Methods

    `analyze_sentence(self, sentence: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.domain_types.SentenceText) ‑> src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.domain_types.RequirementItem | None`
    :   Analyze single sentence for requirements.

    `analyze_text(self, text: str) ‑> List[src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.domain_types.RequirementItem]`
    :   Analyze text for requirements.

`RequirementClassifier(indicators: Dict[src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.domain_types.RequirementType, List[str]])`
:   Classifies requirements by type.
    
    Initialize with requirement indicators.

    ### Methods

    `classify(self, sentence: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.domain_types.SentenceText) ‑> src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.domain_types.RequirementType`
    :   Classify requirement type based on indicators.

`RequirementItem(raw_text: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.domain_types.RequirementText, type: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.domain_types.RequirementType, category: str, entities: List[src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.domain_types.EntityName], predicates: List[src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.domain_types.PredicateName], logical_structure: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.domain_types.LogicalStructure, formal_constraints: List[src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.domain_types.FormalConstraint], confidence: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.domain_types.ConfidenceScore)`
:   Represents a single extracted requirement.

    ### Instance variables

    `category: str`
    :

    `confidence: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.domain_types.ConfidenceScore`
    :

    `entities: List[src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.domain_types.EntityName]`
    :

    `formal_constraints: List[src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.domain_types.FormalConstraint]`
    :

    `has_quantification: bool`
    :   Check if requirement has quantification.

    `logical_structure: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.domain_types.LogicalStructure`
    :

    `predicates: List[src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.domain_types.PredicateName]`
    :

    `raw_text: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.domain_types.RequirementText`
    :

    `type: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.domain_types.RequirementType`
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

`SectionCategorizer()`
:   Categorizes requirements based on section titles.

    ### Static methods

    `categorize(section_title: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.domain_types.SectionTitle) ‑> str`
    :   Categorize requirement based on section title.

`SpacyNLPProcessor()`
:   SpaCy-based NLP processor.
    
    Initialize SpaCy processor.

    ### Methods

    `extract_entities(self, sentence: str) ‑> List[src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.domain_types.EntityName]`
    :   Extract entities using SpaCy NER.

    `extract_predicates(self, sentence: str) ‑> List[src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.domain_types.PredicateName]`
    :   Extract predicates using SpaCy.

    `process_sentences(self, text: str) ‑> List[src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.domain_types.SentenceText]`
    :   Split text into sentences using SpaCy.