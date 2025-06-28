# Copyright (c) DarkLightX / Dana Edwards
"""
AST (Abstract Syntax Tree) utilities for node manipulation.

This module provides pure helper classes for common AST operations like
visitor method resolution and child extraction, intended for use within
the core engine.
"""

from typing import Any, List

class MethodResolver:
    """Resolves visitor method names for AST nodes."""
    
    @staticmethod
    def get_visitor_method_name(node: Any) -> str:
        """Get visitor method name for a node.
        
        Args:
            node: The AST node.

        Returns:
            The conventional visitor method name (e.g., '_visit_ClassName').
        """
        class_name = node.__class__.__name__
        return f'_visit_{class_name}'
    
    @staticmethod
    def has_visitor_method(obj: Any, node: Any) -> bool:
        """Check if an object has a visitor method for a given AST node.

        Args:
            obj: The object (typically a visitor class instance).
            node: The AST node.

        Returns:
            True if the object has a callable visitor method for the node, False otherwise.
        """
        method_name = MethodResolver.get_visitor_method_name(node)
        return hasattr(obj, method_name) and callable(getattr(obj, method_name))

class NodeChildrenExtractor:
    """Extracts children from AST nodes based on common attribute patterns."""
    
    _CHILD_BEARING_ATTRIBUTES = [
        ('body', True),          # Can be single item or list
        ('statements', False),   # Always a list
        ('expressions', False),  # Always a list
        ('operands', False),     # Always a list
        ('arguments', False),    # Always a list
    ]
    
    _CHILD_PAIR_ATTRIBUTES = [
        ('left', 'right'),
        ('target', 'expression'),
    ]

    _SINGLE_CHILD_ATTRIBUTES = [
        'value',
    ]

    @staticmethod
    def get_children(node: Any) -> List[Any]:
        """
        Get all child nodes from a given AST node.

        This method inspects common attributes of AST nodes (like 'body', 
        'statements', 'left'/'right', 'value', etc.) to find potential children.
        It filters out None values from the collected children.

        Args:
            node: The AST node from which to extract children.

        Returns:
            A list of child nodes. The list may be empty if no children are found.
        """
        children: List[Any] = []
        
        for attr_name, is_list_or_single in NodeChildrenExtractor._CHILD_BEARING_ATTRIBUTES:
            if hasattr(node, attr_name):
                attr_value = getattr(node, attr_name)
                if attr_value is not None:
                    if is_list_or_single and isinstance(attr_value, list):
                        children.extend(attr_value)
                    elif is_list_or_single:
                         children.append(attr_value)
                    elif isinstance(attr_value, list):
                        children.extend(attr_value)

        for left_attr, right_attr in NodeChildrenExtractor._CHILD_PAIR_ATTRIBUTES:
            if hasattr(node, left_attr) and hasattr(node, right_attr):
                left_child = getattr(node, left_attr)
                right_child = getattr(node, right_attr)
                if left_child is not None:
                    children.append(left_child)
                if right_child is not None:
                    children.append(right_child)
        
        for attr_name in NodeChildrenExtractor._SINGLE_CHILD_ATTRIBUTES:
            if hasattr(node, attr_name):
                attr_value = getattr(node, attr_name)
                if attr_value is not None:
                     children.append(attr_value)
            
        return [child for child in children if child is not None]
