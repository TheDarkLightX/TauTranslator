Module src.tau_translator_omega.core_engine.parsers.parser.domain.natural_language_parser
=========================================================================================
Natural language parser for true NL to Tau translation following the Intentional Disclosure Principle.

Implements a multi-stage approach: NL → Semantic Parse → CNL → ILR → TCE → Tau

Copyright: DarkLightX / Dana Edwards

Classes
-------

`AmbiguityResolver()`
:   Resolves ambiguities in natural language using context and heuristics.
    This is crucial for handling real-world language variations.

    ### Methods

    `resolve_ambiguity(self, sentence: str, dependencies: Dict[str, Any]) ‑> returns.result.Result[src.tau_translator_omega.core_engine.parsers.parser.domain.natural_language_parser.SemanticFrame, str]`
    :   Try to resolve ambiguous sentences.

`DependencyParser()`
:   Lightweight dependency parser for understanding sentence structure.
    Uses patterns and heuristics rather than full NLP models.

    ### Methods

    `parse_dependencies(self, sentence: str) ‑> returns.result.Result[typing.Dict[str, typing.Any], str]`
    :   Parse sentence into dependency structure.

`NaturalLanguageParser()`
:   Main parser that orchestrates NL → CNL → ILR pipeline.
    This is the entry point for true natural language parsing.
    
    Initialize natural language parser.

    ### Methods

    `parse_natural_language_async(self, text: str) ‑> returns.result.Result[typing.List[str], str]`
    :   Parse natural language text into CNL statements.
        Returns list of CNL statements ready for ILR translation.

`SemanticAnalyzer()`
:   Analyzes sentence meaning and maps to logical structures.
    This is the key component that bridges NL to formal logic.
    
    Initialize semantic analyzer.

    ### Methods

    `analyze_semantics(self, dependencies: Dict[str, Any]) ‑> returns.result.Result[src.tau_translator_omega.core_engine.parsers.parser.domain.natural_language_parser.SemanticFrame, str]`
    :   Analyze dependencies to extract semantic meaning.

`SemanticFrame(frame_type: str, participants: Dict[str, Any] = <factory>, modifiers: List[str] = <factory>, confidence: float = 1.0)`
:   Represents a semantic understanding of a sentence.

    ### Instance variables

    `confidence: float`
    :

    `frame_type: str`
    :

    `modifiers: List[str]`
    :

    `participants: Dict[str, Any]`
    :

    ### Methods

    `to_cnl(self) ‑> str`
    :   Convert semantic frame to controlled natural language.