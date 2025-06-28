Module src.tau_translator_omega.core_engine.translators.nlp_enhanced.requirements.pattern_repository
====================================================================================================
Repository of linguistic patterns for requirement analysis.

Copyright: DarkLightX / Dana Edwards

Classes
-------

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