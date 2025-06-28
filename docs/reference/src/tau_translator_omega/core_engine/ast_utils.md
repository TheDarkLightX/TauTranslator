Module src.tau_translator_omega.core_engine.ast_utils
=====================================================
AST (Abstract Syntax Tree) utilities for node manipulation.

This module provides pure helper classes for common AST operations like
visitor method resolution and child extraction, intended for use within
the core engine.

Classes
-------

`MethodResolver()`
:   Resolves visitor method names for AST nodes.

    ### Static methods

    `get_visitor_method_name(node: Any) ‑> str`
    :   Get visitor method name for a node.
        
        Args:
            node: The AST node.
        
        Returns:
            The conventional visitor method name (e.g., '_visit_ClassName').

    `has_visitor_method(obj: Any, node: Any) ‑> bool`
    :   Check if an object has a visitor method for a given AST node.
        
        Args:
            obj: The object (typically a visitor class instance).
            node: The AST node.
        
        Returns:
            True if the object has a callable visitor method for the node, False otherwise.

`NodeChildrenExtractor()`
:   Extracts children from AST nodes based on common attribute patterns.

    ### Static methods

    `get_children(node: Any) ‑> List[Any]`
    :   Get all child nodes from a given AST node.
        
        This method inspects common attributes of AST nodes (like 'body', 
        'statements', 'left'/'right', 'value', etc.) to find potential children.
        It filters out None values from the collected children.
        
        Args:
            node: The AST node from which to extract children.
        
        Returns:
            A list of child nodes. The list may be empty if no children are found.