Module src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.nlp_processor
===============================================================================================
NLP processing infrastructure for requirements analysis.

Copyright: DarkLightX / Dana Edwards

Classes
-------

`NLPProcessor(*args, **kwargs)`
:   Protocol for NLP processing implementations.

    ### Ancestors (in MRO)

    * typing.Protocol
    * typing.Generic

    ### Methods

    `extract_entities(self, sentence: str) ‑> List[src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.domain_types.EntityName]`
    :   Extract entities from sentence.

    `extract_predicates(self, sentence: str) ‑> List[src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.domain_types.PredicateName]`
    :   Extract predicates from sentence.

    `process_sentences(self, text: str) ‑> List[src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.domain_types.SentenceText]`
    :   Split text into sentences.

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