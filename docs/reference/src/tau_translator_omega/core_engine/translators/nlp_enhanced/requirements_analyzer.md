Module src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer
==========================================================================================
Requirements Analyzer for Natural Language Processing
===================================================

Advanced analysis of natural language requirements documents for conversion
to formal Tau Language specifications.

Features:
- Multi-sentence requirement extraction
- Requirement type classification (constraints, behaviors, performance)
- Entity and predicate identification
- Logical structure analysis
- Temporal constraint detection
- Exception and edge case handling

Functions
---------

`create_requirements_analyzer() ‑> src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer.RequirementsAnalyzer`
:   Factory function to create a requirements analyzer

Classes
-------

`FormalConstraint(constraint_type: str, variables: List[str], predicates: List[str], logical_form: str, confidence: float)`
:   Represents a formal constraint extracted from requirements

    ### Instance variables

    `confidence: float`
    :

    `constraint_type: str`
    :

    `logical_form: str`
    :

    `predicates: List[str]`
    :

    `variables: List[str]`
    :

`LogicalStructure(quantifiers: List[str], conditionals: List[str], logical_operators: List[str], temporal_operators: List[str], has_quantification: bool = False, has_conditionals: bool = False, has_temporal: bool = False)`
:   Represents the logical structure of a requirement

    ### Instance variables

    `conditionals: List[str]`
    :

    `has_conditionals: bool`
    :

    `has_quantification: bool`
    :

    `has_temporal: bool`
    :

    `logical_operators: List[str]`
    :

    `quantifiers: List[str]`
    :

    `temporal_operators: List[str]`
    :

`RequirementItem(raw_text: str, type: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer.RequirementType, category: str, entities: List[str], predicates: List[str], logical_structure: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer.LogicalStructure, formal_constraints: List[src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer.FormalConstraint], confidence: float, has_quantification: bool = False)`
:   Represents a single extracted requirement

    ### Instance variables

    `category: str`
    :

    `confidence: float`
    :

    `entities: List[str]`
    :

    `formal_constraints: List[src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer.FormalConstraint]`
    :

    `has_quantification: bool`
    :

    `logical_structure: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer.LogicalStructure`
    :

    `predicates: List[str]`
    :

    `raw_text: str`
    :

    `type: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer.RequirementType`
    :

`RequirementType(*args, **kwds)`
:   Types of requirements that can be extracted

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
    
    Uses advanced NLP techniques including:
    - Named entity recognition
    - Dependency parsing
    - Semantic role labeling
    - Temporal expression extraction
    
    Initialize the requirements analyzer

    ### Methods

    `extract_requirements(self, text: str) ‑> List[src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer.RequirementItem]`
    :   Extract structured requirements from natural language text.
        
        Args:
            text: Natural language requirements text
            
        Returns:
            List of extracted requirement items

    `extract_requirements_from_document(self, document: str) ‑> List[src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer.RequirementItem]`
    :   Extract requirements from a complete requirements document.
        
        Handles multi-paragraph documents with section headers.