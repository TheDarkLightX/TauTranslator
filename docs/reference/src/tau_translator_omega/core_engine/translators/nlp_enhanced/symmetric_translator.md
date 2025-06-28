Module src.tau_translator_omega.core_engine.translators.nlp_enhanced.symmetric_translator
=========================================================================================
Symmetric Translator for Bidirectional English↔Tau Translation
============================================================

Inspired by SapienzaNLP SPRING's symmetric parsing and generation approach.
Provides unified bidirectional translation between English and Tau Language.

Key Features:
- Symmetric seq2seq-style translation
- Multiple linearization strategies (DFS, BFS, PENMAN)
- Semantic similarity preservation
- Logical equivalence checking
- Unified model architecture for both directions

Functions
---------

`create_symmetric_translator() ‑> src.tau_translator_omega.core_engine.translators.nlp_enhanced.symmetric_translator.SymmetricTranslator`
:   Factory function to create a symmetric translator

Classes
-------

`AMRLinearizer()`
:   Handles different linearization strategies for AMR graphs
    
    Initialize the linearizer

    ### Methods

    `linearize(self, amr_graph: src.tau_translator_omega.core_engine.translators.nlp_enhanced.amr_semantic_layer.AMRGraph, strategy: src.tau_translator_omega.core_engine.translators.nlp_enhanced.symmetric_translator.LinearizationStrategy) ‑> str`
    :   Linearize AMR graph according to specified strategy

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

`TranslationDirection(*args, **kwds)`
:   Direction of translation

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `ENGLISH_TO_TAU`
    :

    `TAU_TO_ENGLISH`
    :