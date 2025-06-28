Module src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.domain_types
==============================================================================================
Domain types and data classes for requirements analysis.

Copyright: DarkLightX / Dana Edwards

Classes
-------

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