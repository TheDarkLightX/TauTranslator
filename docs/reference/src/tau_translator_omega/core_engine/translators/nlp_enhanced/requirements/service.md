Module src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.service
=========================================================================================
Service layer for requirements analysis orchestration.

Copyright: DarkLightX / Dana Edwards

Classes
-------

`RequirementAnalysisService(nlp_processor: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.nlp_processor.NLPProcessor, classifier: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.analyzers.RequirementClassifier, logical_analyzer: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.analyzers.LogicalAnalyzer, constraint_extractor: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.analyzers.ConstraintExtractor)`
:   Orchestrates requirement analysis operations.
    
    Initialize with analysis components.

    ### Methods

    `analyze_sentence(self, sentence: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.domain_types.SentenceText) ‑> src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.domain_types.RequirementItem | None`
    :   Analyze single sentence for requirements.

    `analyze_text(self, text: str) ‑> List[src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.domain_types.RequirementItem]`
    :   Analyze text for requirements.