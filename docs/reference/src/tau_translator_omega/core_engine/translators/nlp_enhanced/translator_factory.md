Module src.tau_translator_omega.core_engine.translators.nlp_enhanced.translator_factory
=======================================================================================
Translator Factory
================

Factory pattern implementation for creating and configuring translator components.
Provides clean, consistent instantiation of NLP enhanced translation system.

This factory encapsulates the complexity of component creation and configuration,
following the Factory Method and Abstract Factory patterns for clean architecture.

Usage:
    ```python
    # Simple usage - get default configured translator
    translator = TranslatorFactory.create_english_to_tau_translator()
    
    # Advanced usage - custom configuration
    config = TranslatorConfig(
        enable_amr_analysis=True,
        confidence_threshold=0.7,
        domain_specialization=['medical', 'financial']
    )
    translator = TranslatorFactory.create_translator(config)
    
    # Quick setup for different use cases
    medical_translator = TranslatorFactory.create_medical_translator()
    financial_translator = TranslatorFactory.create_financial_translator()
    ```

Design Patterns:
    - **Factory Method**: Creates specific translator types
    - **Builder Pattern**: Configurable translator construction  
    - **Strategy Pattern**: Pluggable semantic analyzers
    - **Dependency Injection**: Clean component composition

Functions
---------

`create_amr_semantic_analyzer() ‑> src.tau_translator_omega.core_engine.translators.nlp_enhanced.amr_semantic_layer.AMRSemanticAnalyzer`
:   Convenience function for creating default AMR analyzer.

`create_english_to_tau_translator() ‑> src.tau_translator_omega.core_engine.translators.nlp_enhanced.english_to_tau_translator.EnglishToTauTranslator`
:   Convenience function for creating default translator.

`create_incremental_parser() ‑> src.tau_translator_omega.core_engine.translators.nlp_enhanced.incremental_parser.IncrementalTCEParser`
:   Convenience function for creating default incremental parser.

`create_requirements_analyzer() ‑> src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer.RequirementsAnalyzer`
:   Convenience function for creating default requirements analyzer.

Classes
-------

`DomainSpecialization(*args, **kwds)`
:   Supported domain specializations

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `BUSINESS`
    :

    `FINANCIAL`
    :

    `GENERAL`
    :

    `MEDICAL`
    :

    `SECURITY`
    :

    `TECHNICAL`
    :

`TranslationStrategy(*args, **kwds)`
:   Translation strategy options

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `HYBRID`
    :

    `PATTERN_BASED`
    :

    `SEMANTIC_ENHANCED`
    :

`TranslatorConfig(enable_amr_analysis: bool = True, enable_incremental_parsing: bool = True, confidence_threshold: float = 0.6, cache_size: int = 1000, max_sentence_length: int = 200, timeout_seconds: float = 5.0, domain_specializations: List[src.tau_translator_omega.core_engine.translators.nlp_enhanced.translator_factory.DomainSpecialization] = <factory>, custom_vocabulary: Dict[str, List[str]] = <factory>, translation_strategy: src.tau_translator_omega.core_engine.translators.nlp_enhanced.translator_factory.TranslationStrategy = TranslationStrategy.HYBRID, require_high_confidence: bool = False, enable_detailed_logging: bool = False, enable_bidirectional: bool = True, enable_document_processing: bool = True)`
:   Configuration for translator creation.
    
    Provides comprehensive configuration options for customizing
    translator behavior, performance, and specialization.

    ### Instance variables

    `cache_size: int`
    :

    `confidence_threshold: float`
    :

    `custom_vocabulary: Dict[str, List[str]]`
    :

    `domain_specializations: List[src.tau_translator_omega.core_engine.translators.nlp_enhanced.translator_factory.DomainSpecialization]`
    :

    `enable_amr_analysis: bool`
    :

    `enable_bidirectional: bool`
    :

    `enable_detailed_logging: bool`
    :

    `enable_document_processing: bool`
    :

    `enable_incremental_parsing: bool`
    :

    `max_sentence_length: int`
    :

    `require_high_confidence: bool`
    :

    `timeout_seconds: float`
    :

    `translation_strategy: src.tau_translator_omega.core_engine.translators.nlp_enhanced.translator_factory.TranslationStrategy`
    :

`TranslatorFactory()`
:   Factory for creating configured translator components.
    
    This factory provides multiple creation methods for different use cases,
    from simple default configurations to highly customized setups.

    ### Static methods

    `create_amr_analyzer(config: src.tau_translator_omega.core_engine.translators.nlp_enhanced.translator_factory.TranslatorConfig | None = None) ‑> src.tau_translator_omega.core_engine.translators.nlp_enhanced.amr_semantic_layer.AMRSemanticAnalyzer`
    :   Create a configured AMR semantic analyzer.
        
        Args:
            config: Optional configuration for AMR setup
            
        Returns:
            AMRSemanticAnalyzer: Configured AMR analyzer instance

    `create_english_to_tau_translator(config: src.tau_translator_omega.core_engine.translators.nlp_enhanced.translator_factory.TranslatorConfig | None = None) ‑> src.tau_translator_omega.core_engine.translators.nlp_enhanced.english_to_tau_translator.EnglishToTauTranslator`
    :   Create a standard English to Tau translator.
        
        Args:
            config: Optional configuration. Uses defaults if not provided.
            
        Returns:
            EnglishToTauTranslator: Configured translator instance

    `create_financial_translator() ‑> src.tau_translator_omega.core_engine.translators.nlp_enhanced.english_to_tau_translator.EnglishToTauTranslator`
    :   Create a translator specialized for financial domain.
        
        Pre-configured with financial vocabulary and specialized patterns
        for trading systems and financial regulations.
        
        Returns:
            EnglishToTauTranslator: Financial-specialized translator

    `create_high_accuracy_translator() ‑> src.tau_translator_omega.core_engine.translators.nlp_enhanced.english_to_tau_translator.EnglishToTauTranslator`
    :   Create a translator optimized for maximum accuracy.
        
        Configured for highest quality output with comprehensive
        analysis and strict confidence requirements.
        
        Returns:
            EnglishToTauTranslator: Accuracy-optimized translator

    `create_high_performance_translator() ‑> src.tau_translator_omega.core_engine.translators.nlp_enhanced.english_to_tau_translator.EnglishToTauTranslator`
    :   Create a translator optimized for high performance.
        
        Configured for maximum speed with larger caches and
        optimized processing for high-throughput scenarios.
        
        Returns:
            EnglishToTauTranslator: Performance-optimized translator

    `create_incremental_parser(config: src.tau_translator_omega.core_engine.translators.nlp_enhanced.translator_factory.TranslatorConfig | None = None) ‑> src.tau_translator_omega.core_engine.translators.nlp_enhanced.incremental_parser.IncrementalTCEParser`
    :   Create a configured incremental parser.
        
        Args:
            config: Optional configuration for parser setup
            
        Returns:
            IncrementalTCEParser: Configured parser instance

    `create_medical_translator() ‑> src.tau_translator_omega.core_engine.translators.nlp_enhanced.english_to_tau_translator.EnglishToTauTranslator`
    :   Create a translator specialized for medical domain.
        
        Pre-configured with medical vocabulary and specialized patterns
        for healthcare and medical device requirements.
        
        Returns:
            EnglishToTauTranslator: Medical-specialized translator

    `create_requirements_analyzer(config: src.tau_translator_omega.core_engine.translators.nlp_enhanced.translator_factory.TranslatorConfig | None = None) ‑> src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer.RequirementsAnalyzer`
    :   Create a configured requirements analyzer.
        
        Args:
            config: Optional configuration for analyzer setup
            
        Returns:
            RequirementsAnalyzer: Configured analyzer instance

    `create_security_translator() ‑> src.tau_translator_omega.core_engine.translators.nlp_enhanced.english_to_tau_translator.EnglishToTauTranslator`
    :   Create a translator specialized for security domain.
        
        Pre-configured with security vocabulary and specialized patterns
        for cryptographic and access control requirements.
        
        Returns:
            EnglishToTauTranslator: Security-specialized translator