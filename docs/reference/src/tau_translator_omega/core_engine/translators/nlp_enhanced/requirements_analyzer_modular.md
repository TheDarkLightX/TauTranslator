Module src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer_modular
==================================================================================================
Modular Requirements Analyzer following the Intentional Disclosure Principle.

Main API that composes all the smaller modules into a cohesive analyzer.

Copyright: DarkLightX / Dana Edwards

Functions
---------

`create_requirements_analyzer() ‑> src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer_modular.RequirementsAnalyzer`
:   Factory function to create a requirements analyzer.

Classes
-------

`RequirementsAnalyzer()`
:   Main analyzer for extracting structured requirements from natural language.
    
    Initialize the requirements analyzer.

    ### Methods

    `extract_requirements(self, text: str) ‑> List[src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.domain_types.RequirementItem]`
    :   Extract structured requirements from natural language text.

    `extract_requirements_from_document(self, document: str) ‑> List[src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.domain_types.RequirementItem]`
    :   Extract requirements from a complete requirements document.