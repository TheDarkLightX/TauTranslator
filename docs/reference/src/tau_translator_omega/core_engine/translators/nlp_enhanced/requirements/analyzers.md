Module src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.analyzers
===========================================================================================
Business logic analyzers for requirements processing.

Copyright: DarkLightX / Dana Edwards

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

`LogicalAnalyzer(pattern_repo: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.pattern_repository.PatternRepository)`
:   Analyzes logical structure of sentences.
    
    Initialize with pattern repository.

    ### Methods

    `analyze(self, sentence: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.domain_types.SentenceText) ‑> src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.domain_types.LogicalStructure`
    :   Analyze logical structure of sentence.

`RequirementClassifier(indicators: Dict[src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.domain_types.RequirementType, List[str]])`
:   Classifies requirements by type.
    
    Initialize with requirement indicators.

    ### Methods

    `classify(self, sentence: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.domain_types.SentenceText) ‑> src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.domain_types.RequirementType`
    :   Classify requirement type based on indicators.

`SectionCategorizer()`
:   Categorizes requirements based on section titles.

    ### Static methods

    `categorize(section_title: src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.domain_types.SectionTitle) ‑> str`
    :   Categorize requirement based on section title.