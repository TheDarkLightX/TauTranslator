"""
Semantic analysis infrastructure following the Intentional Disclosure Principle.

Isolates I/O and external operations from business logic.

Copyright: DarkLightX / Dana Edwards
"""

from typing import Dict, Any, Optional, List
import json
import os


class VocabularyLoader:
    """Handles vocabulary loading from external sources."""
    
    @staticmethod
    def load_from_file(file_path: str) -> Dict[str, Any]:
        """Load vocabulary from JSON file."""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            return {'types': set(), 'predicates': {}, 'functions': {}}
    
    @staticmethod
    def load_from_environment() -> Dict[str, Any]:
        """Load vocabulary from environment variables."""
        vocab_path = os.environ.get('TAU_VOCABULARY_PATH')
        if vocab_path and os.path.exists(vocab_path):
            return VocabularyLoader.load_from_file(vocab_path)
        return {'types': set(), 'predicates': {}, 'functions': {}}


class MethodResolver:
    """Resolves visitor method names for AST nodes."""
    
    @staticmethod
    def get_visitor_method_name(node: Any) -> str:
        """Get visitor method name for a node."""
        class_name = node.__class__.__name__
        return f'_visit_{class_name}'
    
    @staticmethod
    def has_visitor_method(obj: Any, node: Any) -> bool:
        """Check if object has visitor method for node."""
        method_name = MethodResolver.get_visitor_method_name(node)
        return hasattr(obj, method_name) and callable(getattr(obj, method_name))


class NodeChildrenExtractor:
    """Extracts children from AST nodes."""
    
    @staticmethod
    def get_children(node: Any) -> List[Any]:
        """Get all child nodes from an AST node."""
        children = []
        
        # Common patterns for AST nodes
        if hasattr(node, 'body'):
            if isinstance(node.body, list):
                children.extend(node.body)
            else:
                children.append(node.body)
                
        if hasattr(node, 'statements'):
            children.extend(node.statements)
            
        if hasattr(node, 'expressions'):
            children.extend(node.expressions)
            
        if hasattr(node, 'left') and hasattr(node, 'right'):
            children.append(node.left)
            children.append(node.right)
            
        if hasattr(node, 'operands'):
            children.extend(node.operands)
            
        if hasattr(node, 'arguments'):
            children.extend(node.arguments)
            
        if hasattr(node, 'value'):
            if node.value is not None:
                children.append(node.value)
                
        if hasattr(node, 'target') and hasattr(node, 'expression'):
            children.append(node.target)
            children.append(node.expression)
            
        return [child for child in children if child is not None]


class SemanticLogger:
    """Handles logging for semantic analysis."""
    
    def __init__(self, log_file: Optional[str] = None):
        """Initialize logger."""
        self.log_file = log_file
        self._enabled = log_file is not None
    
    def log_analysis_start(self, node_type: str) -> None:
        """Log start of node analysis."""
        if self._enabled:
            self._write_log(f"Analyzing {node_type}")
    
    def log_error_found(self, error_message: str) -> None:
        """Log when error is found."""
        if self._enabled:
            self._write_log(f"Error found: {error_message}")
    
    def log_symbol_declared(self, symbol_name: str, symbol_type: str) -> None:
        """Log symbol declaration."""
        if self._enabled:
            self._write_log(f"Symbol declared: {symbol_name} ({symbol_type})")
    
    def _write_log(self, message: str) -> None:
        """Write message to log file."""
        try:
            with open(self.log_file, 'a') as f:
                f.write(f"{message}\n")
        except IOError:
            pass  # Silently ignore logging errors