Module src.tau_translator_omega.core_engine.semantic.semantic_analyzer
======================================================================
Refactored Semantic Analyzer for TauTranslator
=============================================

Refactored from 675 lines to <300 lines following VibeArchitect principles.
Uses Strategy pattern for analysis components and Factory pattern for creation.

Key improvements:
- Strategy pattern for analysis components
- Factory pattern for object creation
- Clear separation of concerns
- Enhanced error handling
- Comprehensive type system

Author: DarkLightX / Dana Edwards

Classes
-------

`SemanticAnalyzer(vocabulary: dict | None = None)`
:   Refactored semantic analyzer using Strategy pattern for component separation.
    
    Follows VibeArchitect principles:
    - Strategy pattern for analysis components
    - Factory pattern for component creation
    - Single Responsibility: Coordination only
    - Clear error handling and logging
    - Performance monitoring capability
    
    Initialize semantic analyzer with strategy components.
    
    Args:
        vocabulary: Dictionary containing available types, predicates, functions.
                   Defaults to basic types if not provided.

    ### Methods

    `analyze(self, node: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode | None) ‑> Tuple[src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode | None, List[src.tau_translator_omega.core_engine.semantic.semantic_types.SemanticError]]`
    :   Perform semantic analysis using Strategy pattern components.
        
        Args:
            node: Root AST node to analyze
            
        Returns:
            Tuple of (analyzed_node, list_of_errors)

    `get_analysis_stats(self) ‑> dict`
    :   Get semantic analysis performance statistics.
        
        Returns:
            Dictionary with performance metrics