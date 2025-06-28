Module src.tau_translator_omega.core_engine.translators.nlp_enhanced
====================================================================
Enhanced NLP Module for TauTranslator
===================================

State-of-the-art natural language processing capabilities for Tau Controlled English.

Features:
- Abstract Meaning Representation (AMR) semantic analysis
- Incremental parsing with caching
- Neural constituency parsing integration
- Coreference resolution
- Template-guided neural parsing
- Neuro-symbolic reasoning integration

This module implements cutting-edge NLP algorithms based on academic research
to enhance the natural language understanding capabilities of TauTranslator.

Sub-modules
-----------
* src.tau_translator_omega.core_engine.translators.nlp_enhanced.amr_semantic_layer
* src.tau_translator_omega.core_engine.translators.nlp_enhanced.english_to_tau_translator
* src.tau_translator_omega.core_engine.translators.nlp_enhanced.incremental_parser
* src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements
* src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer
* src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer_modular
* src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer_refactored
* src.tau_translator_omega.core_engine.translators.nlp_enhanced.symmetric_translator
* src.tau_translator_omega.core_engine.translators.nlp_enhanced.translator_factory

Functions
---------

`create_english_to_tau_translator() ‑> src.tau_translator_omega.core_engine.translators.nlp_enhanced.english_to_tau_translator.EnglishToTauTranslator`
:   Factory function to create an English to Tau translator

`create_incremental_parser() ‑> src.tau_translator_omega.core_engine.translators.nlp_enhanced.incremental_parser.IncrementalTCEParser`
:   Factory function for creating incremental parser

`create_requirements_analyzer() ‑> src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer.RequirementsAnalyzer`
:   Factory function to create a requirements analyzer

`create_symmetric_translator() ‑> src.tau_translator_omega.core_engine.translators.nlp_enhanced.symmetric_translator.SymmetricTranslator`
:   Factory function to create a symmetric translator

`enhance_semantic_analysis(ast_node: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode) ‑> Dict[str, Any]`
:   Enhanced semantic analysis using AMR.
    
    This function can be integrated into the existing semantic analyzer
    to provide deeper understanding of TCE semantics.

Classes
-------

`AMRConcept(name: str, frame_type: str, roles: List[src.tau_translator_omega.core_engine.translators.nlp_enhanced.amr_semantic_layer.AMRRelation], constraints: Dict[str, Any])`
:   Represents an AMR concept with its frame semantics.
    Maps TCE predicates to semantic frames.

    ### Instance variables

    `constraints: Dict[str, Any]`
    :

    `frame_type: str`
    :

    `name: str`
    :

    `roles: List[src.tau_translator_omega.core_engine.translators.nlp_enhanced.amr_semantic_layer.AMRRelation]`
    :

`AMRGraph()`
:   Represents the complete AMR graph for a TCE sentence.
    
    Provides semantic role labeling, coreference resolution,
    and compositional meaning representation.

    ### Methods

    `add_edge(self, source_id: str, relation: src.tau_translator_omega.core_engine.translators.nlp_enhanced.amr_semantic_layer.AMRRelation, target_id: str)`
    :   Add a semantic relation between instances

    `add_instance(self, instance_id: str, concept: src.tau_translator_omega.core_engine.translators.nlp_enhanced.amr_semantic_layer.AMRConcept) ‑> src.tau_translator_omega.core_engine.translators.nlp_enhanced.amr_semantic_layer.AMRInstance`
    :   Add a new concept instance to the graph

    `get_semantic_roles(self, predicate_id: str) ‑> Dict[src.tau_translator_omega.core_engine.translators.nlp_enhanced.amr_semantic_layer.AMRRelation, str]`
    :   Get all semantic roles for a predicate

    `set_root(self, instance_id: str)`
    :   Set the root instance of the graph

    `to_penman(self) ‑> str`
    :   Convert to PENMAN notation for debugging

`AMRRelation(*args, **kwds)`
:   Standard AMR semantic relations

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `ARG0`
    :

    `ARG1`
    :

    `ARG2`
    :

    `ARG3`
    :

    `ARG4`
    :

    `CONDITION`
    :

    `DOMAIN`
    :

    `LOCATION`
    :

    `MANNER`
    :

    `MODE`
    :

    `POLARITY`
    :

    `PURPOSE`
    :

    `QUANT`
    :

    `SCOPE`
    :

    `TEMPORAL`
    :

`AMRSemanticAnalyzer()`
:   Main AMR semantic analyzer for TCE.
    
    Converts AST nodes to AMR graphs with semantic role labeling.
    Provides enhanced semantic understanding beyond basic parsing.

    ### Methods

    `analyze(self, ast_node: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode) ‑> src.tau_translator_omega.core_engine.translators.nlp_enhanced.amr_semantic_layer.AMRGraph`
    :   Convert AST to AMR graph with semantic analysis.
        
        Args:
            ast_node: Root AST node from CNL parser
            
        Returns:
            AMRGraph with semantic role labeling

    `get_semantic_roles(self, graph: src.tau_translator_omega.core_engine.translators.nlp_enhanced.amr_semantic_layer.AMRGraph, predicate_name: str) ‑> List[Dict[str, Any]]`
    :   Extract semantic roles for analysis.
        
        Returns list of role assignments with confidence scores.

`ConfidenceScore(overall: float, syntax: float, semantics: float, logical_structure: float, mathematical: float, issues: List[str])`
:   Detailed confidence scoring for translations

    ### Instance variables

    `issues: List[str]`
    :

    `logical_structure: float`
    :

    `mathematical: float`
    :

    `overall: float`
    :

    `semantics: float`
    :

    `syntax: float`
    :

`DocumentTranslationResult(source_document: str, tau_specification: str, individual_translations: List[src.tau_translator_omega.core_engine.translators.nlp_enhanced.english_to_tau_translator.TranslationResult], overall_confidence: float, traceability_map: Dict[str, str])`
:   Result of translating an entire document

    ### Instance variables

    `individual_translations: List[src.tau_translator_omega.core_engine.translators.nlp_enhanced.english_to_tau_translator.TranslationResult]`
    :

    `overall_confidence: float`
    :

    `source_document: str`
    :

    `tau_specification: str`
    :

    `traceability_map: Dict[str, str]`
    :

`EnglishToTauTranslator()`
:   Main translator for converting English requirements to Tau specifications.
    
    Uses semantic analysis and template-based translation to produce
    high-quality Tau Language output with confidence scoring.
    
    Initialize the English to Tau translator

    ### Methods

    `analyze_semantics(self, text: str) ‑> src.tau_translator_omega.core_engine.translators.nlp_enhanced.english_to_tau_translator.SemanticAnalysis`
    :   Analyze semantic structure of text using improved extraction.
        
        This method applies various NLP techniques to extract semantic components
        from natural language text, including predicates, entities, quantifiers,
        logical operators, and temporal expressions.
        
        Args:
            text: Input text to analyze
            
        Returns:
            SemanticAnalysis: Structured semantic components

    `analyze_tau_semantics(self, tau_spec: str) ‑> src.tau_translator_omega.core_engine.translators.nlp_enhanced.english_to_tau_translator.SemanticAnalysis`
    :   Analyze semantic structure of Tau specification

    `translate(self, text: str) ‑> src.tau_translator_omega.core_engine.translators.nlp_enhanced.english_to_tau_translator.TranslationResult`
    :   Translate English text to Tau specification.
        
        Args:
            text: English requirements text
            
        Returns:
            TranslationResult with Tau specification and confidence

    `translate_document(self, document: str) ‑> src.tau_translator_omega.core_engine.translators.nlp_enhanced.english_to_tau_translator.DocumentTranslationResult`
    :   Translate an entire requirements document.
        
        Args:
            document: Complete requirements document
            
        Returns:
            DocumentTranslationResult with complete Tau specification

    `translate_tau_to_english(self, tau_spec: str) ‑> src.tau_translator_omega.core_engine.translators.nlp_enhanced.english_to_tau_translator.TranslationResult`
    :   Translate Tau specification back to English.
        
        Args:
            tau_spec: Tau language specification
            
        Returns:
            TranslationResult with English text

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

`IncrementalParseCache(max_size: int = 1000)`
:   LRU cache for parsed subtrees with dependency tracking.
    
    Maintains parsed subtrees and intelligently invalidates
    dependent entries when source text changes.

    ### Methods

    `get(self, text: str) ‑> src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode | None`
    :   Get cached parse result for text

    `get_cache_stats(self) ‑> Dict[str, Any]`
    :   Get cache performance statistics

    `invalidate(self, text: str)`
    :   Invalidate cache entries affected by text change

    `put(self, text: str, ast_node: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode, dependencies: Set[str] = None)`
    :   Cache parse result for text

`IncrementalTCEParser(cache_size: int = 1000)`
:   Main incremental parser for TCE with intelligent caching.
    
    Provides O(log n) incremental parsing for small edits by reusing
    cached parse subtrees and only reparsing affected regions.

    ### Methods

    `get_performance_stats(self) ‑> Dict[str, Any]`
    :   Get detailed performance statistics

    `invalidate_cache(self, text_pattern: str = None)`
    :   Invalidate cache entries matching pattern

    `parse(self, text: str, previous_text: str = None, previous_ast: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode = None) ‑> Tuple[src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode, Dict[str, Any]]`
    :   Parse text with incremental optimization.
        
        Args:
            text: Current text to parse
            previous_text: Previous version of text (for incremental parsing)
            previous_ast: Previous AST (for subtree reuse)
            
        Returns:
            Tuple of (AST node, parsing metadata)

`LinearizationStrategy(*args, **kwds)`
:   Strategy for linearizing AMR graphs to text

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `BREADTH_FIRST`
    :

    `DEPTH_FIRST`
    :

    `PENMAN_STYLE`
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

`SemanticAnalysis(predicates: List[str], entities: List[str], quantifiers: List[str], logical_operators: List[str], temporal_expressions: List[str])`
:   Semantic analysis results

    ### Instance variables

    `entities: List[str]`
    :

    `logical_operators: List[str]`
    :

    `predicates: List[str]`
    :

    `quantifiers: List[str]`
    :

    `temporal_expressions: List[str]`
    :

`SymmetricTranslationResult(input_text: str, output: str, direction: src.tau_translator_omega.core_engine.translators.nlp_enhanced.symmetric_translator.TranslationDirection, linearization: src.tau_translator_omega.core_engine.translators.nlp_enhanced.symmetric_translator.LinearizationStrategy, confidence: float, semantic_analysis: src.tau_translator_omega.core_engine.translators.nlp_enhanced.english_to_tau_translator.SemanticAnalysis, amr_graph: src.tau_translator_omega.core_engine.translators.nlp_enhanced.amr_semantic_layer.AMRGraph | None = None, alignment_scores: Dict[str, float] = None)`
:   Result of symmetric translation

    ### Instance variables

    `alignment_scores: Dict[str, float]`
    :

    `amr_graph: src.tau_translator_omega.core_engine.translators.nlp_enhanced.amr_semantic_layer.AMRGraph | None`
    :

    `confidence: float`
    :

    `direction: src.tau_translator_omega.core_engine.translators.nlp_enhanced.symmetric_translator.TranslationDirection`
    :

    `input_text: str`
    :

    `linearization: src.tau_translator_omega.core_engine.translators.nlp_enhanced.symmetric_translator.LinearizationStrategy`
    :

    `output: str`
    :

    `semantic_analysis: src.tau_translator_omega.core_engine.translators.nlp_enhanced.english_to_tau_translator.SemanticAnalysis`
    :

`SymmetricTranslator()`
:   Main symmetric translator inspired by SPRING.
    
    Provides unified bidirectional translation between English and Tau Language
    using symmetric seq2seq-style approach with multiple linearization strategies.
    
    Initialize the symmetric translator

    ### Methods

    `calculate_semantic_similarity(self, text1: str, text2: str) ‑> float`
    :   Calculate semantic similarity between two texts

    `check_logical_equivalence(self, tau1: str, tau2: str) ‑> bool`
    :   Check if two Tau expressions are logically equivalent

    `is_valid_tau(self, tau_text: str) ‑> bool`
    :   Check if text represents valid Tau Language

    `linearize_amr(self, amr_graph: src.tau_translator_omega.core_engine.translators.nlp_enhanced.amr_semantic_layer.AMRGraph, strategy: src.tau_translator_omega.core_engine.translators.nlp_enhanced.symmetric_translator.LinearizationStrategy) ‑> str`
    :   Linearize AMR graph using specified strategy

    `translate(self, text: str, direction: src.tau_translator_omega.core_engine.translators.nlp_enhanced.symmetric_translator.TranslationDirection, linearization: src.tau_translator_omega.core_engine.translators.nlp_enhanced.symmetric_translator.LinearizationStrategy = LinearizationStrategy.DEPTH_FIRST) ‑> src.tau_translator_omega.core_engine.translators.nlp_enhanced.symmetric_translator.SymmetricTranslationResult`
    :   Perform symmetric translation in specified direction.
        
        Args:
            text: Input text to translate
            direction: Direction of translation
            linearization: Linearization strategy for output
            
        Returns:
            SymmetricTranslationResult with translation and metadata

`TextDiffer(edit_threshold: int = 5)`
:   Efficient text difference computation for incremental parsing.
    
    Uses optimized algorithms to find minimal edit sequences.

    ### Methods

    `compute_edits(self, old_text: str, new_text: str) ‑> List[src.tau_translator_omega.core_engine.translators.nlp_enhanced.incremental_parser.Edit]`
    :   Compute minimal edit sequence between old and new text.
        
        Returns list of Edit operations needed to transform old_text to new_text.

    `is_small_edit(self, edits: List[src.tau_translator_omega.core_engine.translators.nlp_enhanced.incremental_parser.Edit]) ‑> bool`
    :   Check if edits qualify as 'small' for incremental parsing

`TranslationDirection(*args, **kwds)`
:   Direction of translation

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `ENGLISH_TO_TAU`
    :

    `TAU_TO_ENGLISH`
    :

`TranslationResult(source_text: str, tau_specification: str, confidence: src.tau_translator_omega.core_engine.translators.nlp_enhanced.english_to_tau_translator.ConfidenceScore, semantic_analysis: src.tau_translator_omega.core_engine.translators.nlp_enhanced.english_to_tau_translator.SemanticAnalysis, amr_graph: src.tau_translator_omega.core_engine.translators.nlp_enhanced.amr_semantic_layer.AMRGraph | None = None, translation_notes: List[str] = None)`
:   Result of English to Tau translation

    ### Instance variables

    `amr_graph: src.tau_translator_omega.core_engine.translators.nlp_enhanced.amr_semantic_layer.AMRGraph | None`
    :

    `confidence: src.tau_translator_omega.core_engine.translators.nlp_enhanced.english_to_tau_translator.ConfidenceScore`
    :

    `semantic_analysis: src.tau_translator_omega.core_engine.translators.nlp_enhanced.english_to_tau_translator.SemanticAnalysis`
    :

    `source_text: str`
    :

    `tau_specification: str`
    :

    `translation_notes: List[str]`
    :