Module src.tau_translator_omega.core_engine.translators.nlp_enhanced.incremental_parser
=======================================================================================
Incremental Parser with Caching
==============================

Advanced incremental parsing system for real-time TCE editing.
Based on state-of-the-art research in incremental syntactic analysis.

Features:
- O(log n) incremental reparse for small edits
- Intelligent cache invalidation
- Partial parse tree reuse
- Edit distance optimization
- Real-time error recovery

Research basis:
- Incremental Earley parsing algorithms
- Left-corner prediction for CNL
- Cache-based parse tree reconstruction

Functions
---------

`create_incremental_parser() ‑> src.tau_translator_omega.core_engine.translators.nlp_enhanced.incremental_parser.IncrementalTCEParser`
:   Factory function for creating incremental parser

`demonstrate_incremental_parsing()`
:   Demonstrate incremental parsing capabilities

Classes
-------

`Edit(edit_type: src.tau_translator_omega.core_engine.translators.nlp_enhanced.incremental_parser.EditType, start_pos: int, end_pos: int, new_text: str = '', old_text: str = '')`
:   Represents a single edit operation

    ### Instance variables

    `edit_type: src.tau_translator_omega.core_engine.translators.nlp_enhanced.incremental_parser.EditType`
    :

    `end_pos: int`
    :

    `new_text: str`
    :

    `old_text: str`
    :

    `start_pos: int`
    :

`EditType(*args, **kwds)`
:   Types of text edits for incremental parsing

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `DELETE`
    :

    `INSERT`
    :

    `MOVE`
    :

    `REPLACE`
    :

`IncrementalParseCache(max_size: int = 1000)`
:   LRU cache for parsed subtrees with dependency tracking.
    
    Maintains parsed subtrees and intelligently invalidates
    dependent entries when source text changes.

    ### Methods

    `get(self, text: str) ‑> src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode | None`
    :   Get cached parse result for text

    `get_cache_stats(self) ‑> Dict[str, Any]`
    :   Get cache performance statistics

    `invalidate(self, text: str)`
    :   Invalidate cache entries affected by text change

    `put(self, text: str, ast_node: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode, dependencies: Set[str] = None)`
    :   Cache parse result for text

`IncrementalTCEParser(cache_size: int = 1000)`
:   Main incremental parser for TCE with intelligent caching.
    
    Provides O(log n) incremental parsing for small edits by reusing
    cached parse subtrees and only reparsing affected regions.

    ### Methods

    `get_performance_stats(self) ‑> Dict[str, Any]`
    :   Get detailed performance statistics

    `invalidate_cache(self, text_pattern: str = None)`
    :   Invalidate cache entries matching pattern

    `parse(self, text: str, previous_text: str = None, previous_ast: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode = None) ‑> Tuple[src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode, Dict[str, Any]]`
    :   Parse text with incremental optimization.
        
        Args:
            text: Current text to parse
            previous_text: Previous version of text (for incremental parsing)
            previous_ast: Previous AST (for subtree reuse)
            
        Returns:
            Tuple of (AST node, parsing metadata)

`ParseCacheEntry(text_hash: str, ast_node: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode, timestamp: float, access_count: int, dependencies: Set[str])`
:   Cache entry for parsed subtrees

    ### Instance variables

    `access_count: int`
    :

    `ast_node: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode`
    :

    `dependencies: Set[str]`
    :

    `text_hash: str`
    :

    `timestamp: float`
    :

`TextDiffer(edit_threshold: int = 5)`
:   Efficient text difference computation for incremental parsing.
    
    Uses optimized algorithms to find minimal edit sequences.

    ### Methods

    `compute_edits(self, old_text: str, new_text: str) ‑> List[src.tau_translator_omega.core_engine.translators.nlp_enhanced.incremental_parser.Edit]`
    :   Compute minimal edit sequence between old and new text.
        
        Returns list of Edit operations needed to transform old_text to new_text.

    `is_small_edit(self, edits: List[src.tau_translator_omega.core_engine.translators.nlp_enhanced.incremental_parser.Edit]) ‑> bool`
    :   Check if edits qualify as 'small' for incremental parsing