"""
AST visitor pattern implementation following the Intentional Disclosure Principle.

Provides a flexible framework for AST traversal and transformation
with support for different visitor strategies.

Copyright: DarkLightX / Dana Edwards
"""

from typing import Any, Dict, List, Optional, Protocol, TypeVar, Generic
from abc import ABC, abstractmethod
from returns.result import Result, Success, Failure
from returns.maybe import Maybe, Some, Nothing

from .types import ParseNode, NodeType, ASTNode


T = TypeVar('T')
R = TypeVar('R')


class ASTVisitor(Protocol[T]):
    """Protocol for AST visitors."""
    
    def visit(self, node: ASTNode) -> Result[T, str]:
        """Visit an AST node."""
        ...
    
    def visit_program(self, node: Any) -> Result[T, str]:
        """Visit program node."""
        ...
    
    def visit_statement(self, node: Any) -> Result[T, str]:
        """Visit statement node."""
        ...
    
    def visit_expression(self, node: Any) -> Result[T, str]:
        """Visit expression node."""
        ...


class BaseASTVisitor(ABC, Generic[T]):
    """
    Base implementation of AST visitor with dispatch mechanism.
    Subclasses implement specific visit methods.
    """
    
    def visit(self, node: ASTNode) -> Result[T, str]:
        """Dispatch to appropriate visit method."""
        method_name = f"visit_{self._get_node_type_name(node)}"
        visitor_method = getattr(self, method_name, None)
        
        if visitor_method:
            return visitor_method(node)
        else:
            return self.generic_visit(node)
    
    def _get_node_type_name(self, node: ASTNode) -> str:
        """Extract node type name for dispatch."""
        # Handle different node type representations
        if hasattr(node, 'node_type'):
            return str(node.node_type).lower()
        elif hasattr(node, '__class__'):
            return node.__class__.__name__.lower()
        else:
            return 'unknown'
    
    def generic_visit(self, node: ASTNode) -> Result[T, str]:
        """Default visit for unhandled node types."""
        return Failure(f"No visitor method for node type: {self._get_node_type_name(node)}")
    
    @abstractmethod
    def visit_program(self, node: Any) -> Result[T, str]:
        """Visit program node - must be implemented."""
        pass


class RecursiveASTVisitor(BaseASTVisitor[T]):
    """
    Visitor that recursively visits all child nodes.
    Useful for transformations that need to process entire tree.
    """
    
    def visit_children(self, node: ASTNode) -> Result[List[T], str]:
        """Visit all children of a node."""
        results = []
        
        for child in self._get_children(node):
            result = self.visit(child)
            if isinstance(result, Failure):
                return result
            results.append(result.unwrap())
        
        return Success(results)
    
    def _get_children(self, node: ASTNode) -> List[ASTNode]:
        """Extract children from node."""
        if hasattr(node, 'children'):
            return node.children
        elif hasattr(node, 'body'):
            return [node.body] if not isinstance(node.body, list) else node.body
        elif hasattr(node, 'statements'):
            return node.statements
        else:
            return []


class TransformingVisitor(RecursiveASTVisitor[ASTNode]):
    """
    Visitor that transforms AST nodes.
    Creates new nodes rather than modifying in place.
    """
    
    def transform_node(self, node: ASTNode, **kwargs) -> ASTNode:
        """Transform a node with new attributes."""
        # Create new node with updated attributes
        node_class = node.__class__
        node_dict = node.__dict__.copy()
        node_dict.update(kwargs)
        
        return node_class(**node_dict)
    
    def visit_program(self, node: Any) -> Result[ASTNode, str]:
        """Transform program node."""
        children_result = self.visit_children(node)
        if isinstance(children_result, Failure):
            return children_result
        
        return Success(self.transform_node(
            node,
            statements=children_result.unwrap()
        ))


class CollectingVisitor(RecursiveASTVisitor[List[Any]]):
    """
    Visitor that collects information from nodes.
    Useful for analysis passes.
    """
    
    def __init__(self):
        """Initialize collector."""
        self._collected: List[Any] = []
    
    def collect(self, item: Any) -> None:
        """Add item to collection."""
        self._collected.append(item)
    
    def get_collected(self) -> List[Any]:
        """Get collected items."""
        return self._collected.copy()
    
    def visit_program(self, node: Any) -> Result[List[Any], str]:
        """Collect from program and return results."""
        self.visit_children(node)
        return Success(self.get_collected())


class ValidatingVisitor(RecursiveASTVisitor[bool]):
    """
    Visitor that validates AST structure.
    Returns true if valid, false with error otherwise.
    """
    
    def __init__(self):
        """Initialize validator."""
        self._errors: List[str] = []
    
    def add_error(self, error: str) -> None:
        """Add validation error."""
        self._errors.append(error)
    
    def has_errors(self) -> bool:
        """Check if validation errors exist."""
        return len(self._errors) > 0
    
    def get_errors(self) -> List[str]:
        """Get all validation errors."""
        return self._errors.copy()
    
    def visit_program(self, node: Any) -> Result[bool, str]:
        """Validate program node."""
        self.visit_children(node)
        
        if self.has_errors():
            return Failure(f"Validation failed: {'; '.join(self.get_errors())}")
        
        return Success(True)


class CompositeVisitor(BaseASTVisitor[Dict[str, Any]]):
    """
    Visitor that applies multiple visitors in sequence.
    Useful for multi-pass analysis.
    """
    
    def __init__(self, visitors: Dict[str, BaseASTVisitor]):
        """Initialize with named visitors."""
        self._visitors = visitors
    
    def visit(self, node: ASTNode) -> Result[Dict[str, Any], str]:
        """Apply all visitors and collect results."""
        results = {}
        
        for name, visitor in self._visitors.items():
            result = visitor.visit(node)
            if isinstance(result, Failure):
                return Failure(f"Visitor '{name}' failed: {result.failure()}")
            results[name] = result.unwrap()
        
        return Success(results)
    
    def visit_program(self, node: Any) -> Result[Dict[str, Any], str]:
        """Visit program with all visitors."""
        return self.visit(node)


class MemoizingVisitor(BaseASTVisitor[T]):
    """
    Visitor that caches results for repeated nodes.
    Useful for performance optimization.
    """
    
    def __init__(self, base_visitor: BaseASTVisitor[T]):
        """Initialize with base visitor."""
        self._base_visitor = base_visitor
        self._cache: Dict[int, Result[T, str]] = {}
    
    def visit(self, node: ASTNode) -> Result[T, str]:
        """Visit with memoization."""
        node_id = id(node)
        
        if node_id in self._cache:
            return self._cache[node_id]
        
        result = self._base_visitor.visit(node)
        self._cache[node_id] = result
        
        return result
    
    def visit_program(self, node: Any) -> Result[T, str]:
        """Delegate to base visitor."""
        return self._base_visitor.visit_program(node)
    
    def clear_cache(self) -> None:
        """Clear memoization cache."""
        self._cache.clear()


class DepthLimitedVisitor(BaseASTVisitor[T]):
    """
    Visitor that limits traversal depth.
    Prevents stack overflow on deeply nested trees.
    """
    
    def __init__(self, base_visitor: BaseASTVisitor[T], max_depth: int = 100):
        """Initialize with base visitor and depth limit."""
        self._base_visitor = base_visitor
        self._max_depth = max_depth
        self._current_depth = 0
    
    def visit(self, node: ASTNode) -> Result[T, str]:
        """Visit with depth tracking."""
        if self._current_depth >= self._max_depth:
            return Failure(f"Maximum depth {self._max_depth} exceeded")
        
        self._current_depth += 1
        try:
            result = self._base_visitor.visit(node)
            return result
        finally:
            self._current_depth -= 1
    
    def visit_program(self, node: Any) -> Result[T, str]:
        """Delegate to base visitor."""
        return self.visit(node)


class PreOrderVisitor(RecursiveASTVisitor[None]):
    """
    Visitor that processes nodes in pre-order.
    Process parent before children.
    """
    
    def visit_node_pre(self, node: ASTNode) -> Result[None, str]:
        """Process node before children."""
        return Success(None)
    
    def visit(self, node: ASTNode) -> Result[None, str]:
        """Visit in pre-order."""
        # Process current node
        pre_result = self.visit_node_pre(node)
        if isinstance(pre_result, Failure):
            return pre_result
        
        # Process children
        children_result = self.visit_children(node)
        if isinstance(children_result, Failure):
            return children_result
        
        return Success(None)
    
    def visit_program(self, node: Any) -> Result[None, str]:
        """Visit program in pre-order."""
        return self.visit(node)


class PostOrderVisitor(RecursiveASTVisitor[None]):
    """
    Visitor that processes nodes in post-order.
    Process children before parent.
    """
    
    def visit_node_post(self, node: ASTNode) -> Result[None, str]:
        """Process node after children."""
        return Success(None)
    
    def visit(self, node: ASTNode) -> Result[None, str]:
        """Visit in post-order."""
        # Process children first
        children_result = self.visit_children(node)
        if isinstance(children_result, Failure):
            return children_result
        
        # Process current node
        post_result = self.visit_node_post(node)
        return post_result
    
    def visit_program(self, node: Any) -> Result[None, str]:
        """Visit program in post-order."""
        return self.visit(node)


class PatternMatchingVisitor(BaseASTVisitor[Maybe[T]]):
    """
    Visitor that uses pattern matching for node processing.
    Returns Maybe type for optional results.
    """
    
    def __init__(self):
        """Initialize pattern matcher."""
        self._patterns: Dict[str, Any] = {}
    
    def register_pattern(self, node_type: str, handler: Any) -> None:
        """Register pattern handler for node type."""
        self._patterns[node_type] = handler
    
    def visit(self, node: ASTNode) -> Result[Maybe[T], str]:
        """Visit using pattern matching."""
        node_type = self._get_node_type_name(node)
        handler = self._patterns.get(node_type)
        
        if handler:
            try:
                result = handler(node)
                return Success(Some(result))
            except Exception as e:
                return Failure(f"Pattern handler failed: {e}")
        
        return Success(Nothing)
    
    def visit_program(self, node: Any) -> Result[Maybe[T], str]:
        """Visit program with pattern matching."""
        return self.visit(node)