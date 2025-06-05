"""
AST Visitor Pattern Implementation
=================================

Implements the visitor pattern for AST traversal, replacing
isinstance() checks with polymorphic dispatch.

Author: DarkLightX / Dana Edwards
"""

from typing import Any, Optional, Dict, Type, Callable
from abc import ABC, abstractmethod
import logging

from .cnl_parser.ast_nodes import (
    ASTNode, VariableNode, ConstantNode, NumberNode, StringNode,
    ArithmeticBinaryOpNode, BooleanBinaryOpNode, ComparisonNode,
    PredicateCallNode, VariableDeclNode, AssignmentNode,
    PredicateDefinitionNode, FunctionDefinitionNode,
    QuantifierBlockNode, ConditionNode, SentenceNode,
    FactNode, RuleNode, DefinitionNode
)

logger = logging.getLogger(__name__)


class ASTVisitor(ABC):
    """
    Abstract base class for AST visitors.
    
    Implements double-dispatch visitor pattern for type-safe
    AST traversal without isinstance() checks.
    """
    
    def __init__(self):
        """Initialize visitor with dispatch table."""
        self._dispatch_table = self._build_dispatch_table()
        self._visit_count = 0
    
    def _build_dispatch_table(self) -> Dict[Type[ASTNode], Callable]:
        """
        Build dispatch table mapping node types to visit methods.
        
        This allows O(1) dispatch without isinstance checks.
        """
        return {
            VariableNode: self.visit_variable_node,
            ConstantNode: self.visit_constant_node,
            NumberNode: self.visit_number_node,
            StringNode: self.visit_string_node,
            ArithmeticBinaryOpNode: self.visit_arithmetic_binary_op_node,
            BooleanBinaryOpNode: self.visit_boolean_binary_op_node,
            ComparisonNode: self.visit_comparison_node,
            PredicateCallNode: self.visit_predicate_call_node,
            VariableDeclNode: self.visit_variable_decl_node,
            AssignmentNode: self.visit_assignment_node,
            PredicateDefinitionNode: self.visit_predicate_definition_node,
            FunctionDefinitionNode: self.visit_function_definition_node,
            QuantifierBlockNode: self.visit_quantifier_block_node,
            ConditionNode: self.visit_condition_node,
            SentenceNode: self.visit_sentence_node,
            FactNode: self.visit_fact_node,
            RuleNode: self.visit_rule_node,
            DefinitionNode: self.visit_definition_node,
        }
    
    def visit(self, node: Optional[ASTNode]) -> Any:
        """
        Visit a node using polymorphic dispatch.
        
        Args:
            node: AST node to visit
            
        Returns:
            Result of visiting the node
        """
        if node is None:
            return self.visit_none()
        
        self._visit_count += 1
        
        # Use dispatch table for O(1) type resolution
        node_type = type(node)
        visitor_method = self._dispatch_table.get(node_type)
        
        if visitor_method:
            return visitor_method(node)
        else:
            # Fallback for unknown node types
            return self.visit_generic_node(node)
    
    def visit_none(self) -> Any:
        """Visit None node."""
        return None
    
    def visit_generic_node(self, node: ASTNode) -> Any:
        """
        Fallback visitor for unknown node types.
        
        Args:
            node: Unknown node type
            
        Returns:
            Default result
        """
        logger.warning(f"No specific visitor for node type: {type(node).__name__}")
        return None
    
    # Abstract visitor methods for each node type
    
    @abstractmethod
    def visit_variable_node(self, node: VariableNode) -> Any:
        """Visit variable node."""
        pass
    
    @abstractmethod
    def visit_constant_node(self, node: ConstantNode) -> Any:
        """Visit constant node."""
        pass
    
    @abstractmethod
    def visit_number_node(self, node: NumberNode) -> Any:
        """Visit number node."""
        pass
    
    @abstractmethod
    def visit_string_node(self, node: StringNode) -> Any:
        """Visit string node."""
        pass
    
    @abstractmethod
    def visit_arithmetic_binary_op_node(self, node: ArithmeticBinaryOpNode) -> Any:
        """Visit arithmetic binary operation node."""
        pass
    
    @abstractmethod
    def visit_boolean_binary_op_node(self, node: BooleanBinaryOpNode) -> Any:
        """Visit boolean binary operation node."""
        pass
    
    @abstractmethod
    def visit_comparison_node(self, node: ComparisonNode) -> Any:
        """Visit comparison node."""
        pass
    
    @abstractmethod
    def visit_predicate_call_node(self, node: PredicateCallNode) -> Any:
        """Visit predicate call node."""
        pass
    
    @abstractmethod
    def visit_variable_decl_node(self, node: VariableDeclNode) -> Any:
        """Visit variable declaration node."""
        pass
    
    @abstractmethod
    def visit_assignment_node(self, node: AssignmentNode) -> Any:
        """Visit assignment node."""
        pass
    
    @abstractmethod
    def visit_predicate_definition_node(self, node: PredicateDefinitionNode) -> Any:
        """Visit predicate definition node."""
        pass
    
    @abstractmethod
    def visit_function_definition_node(self, node: FunctionDefinitionNode) -> Any:
        """Visit function definition node."""
        pass
    
    @abstractmethod
    def visit_quantifier_block_node(self, node: QuantifierBlockNode) -> Any:
        """Visit quantifier block node."""
        pass
    
    @abstractmethod
    def visit_condition_node(self, node: ConditionNode) -> Any:
        """Visit condition node."""
        pass
    
    @abstractmethod
    def visit_sentence_node(self, node: SentenceNode) -> Any:
        """Visit sentence node."""
        pass
    
    @abstractmethod
    def visit_fact_node(self, node: FactNode) -> Any:
        """Visit fact node."""
        pass
    
    @abstractmethod
    def visit_rule_node(self, node: RuleNode) -> Any:
        """Visit rule node."""
        pass
    
    @abstractmethod
    def visit_definition_node(self, node: DefinitionNode) -> Any:
        """Visit definition node."""
        pass
    
    def get_visit_stats(self) -> Dict[str, int]:
        """Get visitation statistics."""
        return {
            'total_visits': self._visit_count
        }


class TypeResolvingVisitor(ASTVisitor):
    """
    Visitor for resolving expression types.
    
    Replaces the isinstance-based type resolution in ExpressionTypeResolver.
    """
    
    def __init__(self, symbol_table):
        super().__init__()
        self.symbol_table = symbol_table
        self._type_cache = {}
    
    def visit_variable_node(self, node: VariableNode) -> Optional[str]:
        """Resolve variable type from symbol table."""
        symbol = self.symbol_table.lookup_symbol(node.name)
        if symbol and symbol.symbol_type == 'variable':
            return symbol.var_type
        return None
    
    def visit_constant_node(self, node: ConstantNode) -> Optional[str]:
        """Resolve constant type."""
        if hasattr(node, 'value_type'):
            type_map = {
                "NUMBER": 'integer',
                "STRING": 'string',
                "BOOLEAN": 'boolean'
            }
            return type_map.get(node.value_type)
        
        # Fallback inference
        if isinstance(node.value, (int, float)):
            return 'integer' if isinstance(node.value, int) else 'real'
        elif isinstance(node.value, str):
            return 'string'
        elif isinstance(node.value, bool):
            return 'boolean'
        
        return None
    
    def visit_number_node(self, node: NumberNode) -> str:
        """Number nodes are always integers."""
        return 'integer'
    
    def visit_string_node(self, node: StringNode) -> str:
        """String nodes are always strings."""
        return 'string'
    
    def visit_arithmetic_binary_op_node(self, node: ArithmeticBinaryOpNode) -> Optional[str]:
        """Resolve arithmetic operation type."""
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)
        
        if left_type in ('integer', 'real') and right_type in ('integer', 'real'):
            return 'real' if 'real' in (left_type, right_type) else 'integer'
        
        return None
    
    def visit_boolean_binary_op_node(self, node: BooleanBinaryOpNode) -> str:
        """Boolean operations always return boolean."""
        return 'boolean'
    
    def visit_comparison_node(self, node: ComparisonNode) -> str:
        """Comparisons always return boolean."""
        return 'boolean'
    
    def visit_predicate_call_node(self, node: PredicateCallNode) -> str:
        """Predicate calls return boolean."""
        return 'boolean'
    
    # Other node types don't have types
    
    def visit_variable_decl_node(self, node: VariableDeclNode) -> None:
        return None
    
    def visit_assignment_node(self, node: AssignmentNode) -> None:
        return None
    
    def visit_predicate_definition_node(self, node: PredicateDefinitionNode) -> None:
        return None
    
    def visit_function_definition_node(self, node: FunctionDefinitionNode) -> None:
        return None
    
    def visit_quantifier_block_node(self, node: QuantifierBlockNode) -> None:
        return None
    
    def visit_condition_node(self, node: ConditionNode) -> None:
        return None
    
    def visit_sentence_node(self, node: SentenceNode) -> None:
        return None
    
    def visit_fact_node(self, node: FactNode) -> None:
        return None
    
    def visit_rule_node(self, node: RuleNode) -> None:
        return None
    
    def visit_definition_node(self, node: DefinitionNode) -> None:
        return None