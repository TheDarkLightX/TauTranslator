#!/usr/bin/env python3
"""
Type System Implementation for Semantic Analyzer
===============================================

Following TDD, this module implements a comprehensive type system
for the semantic analyzer with type inference and checking.
"""

from typing import Optional, Dict, Any, List, Union
from enum import Enum, auto


class TypeKind(Enum):
    """Different kinds of types in the type system"""
    PRIMITIVE = auto()  # int, string, bool, etc.
    FUNCTION = auto()   # Function types with signatures
    PREDICATE = auto()  # Predicate types with arities
    AUTO = auto()       # Type to be inferred
    UNKNOWN = auto()    # Failed type inference
    UNION = auto()      # Union of multiple types


class Type:
    """Base class for all types in the type system"""
    
    def __init__(self, name: str, kind: TypeKind = TypeKind.PRIMITIVE):
        self.name = name
        self.kind = kind
        self.attributes = {}
    
    def is_compatible_with(self, other: 'Type') -> bool:
        """Check if this type is compatible with another type"""
        if self.kind == TypeKind.AUTO or other.kind == TypeKind.AUTO:
            return True  # Auto is compatible with anything
        
        if self.kind != other.kind:
            return False
        
        # For primitives, exact match required
        if self.kind == TypeKind.PRIMITIVE:
            return self.name == other.name
        
        # For functions/predicates, check signatures
        if self.kind in (TypeKind.FUNCTION, TypeKind.PREDICATE):
            return self._check_signature_compatibility(other)
        
        return False
    
    def _check_signature_compatibility(self, other: 'Type') -> bool:
        """Check signature compatibility for functions/predicates"""
        # Check arity
        if self.attributes.get('arity') != other.attributes.get('arity'):
            return False
        
        # Check parameter types
        self_params = self.attributes.get('parameter_types', [])
        other_params = other.attributes.get('parameter_types', [])
        
        if len(self_params) != len(other_params):
            return False
        
        for s_type, o_type in zip(self_params, other_params):
            if not s_type.is_compatible_with(o_type):
                return False
        
        # Check return type for functions
        if self.kind == TypeKind.FUNCTION:
            self_return = self.attributes.get('return_type')
            other_return = other.attributes.get('return_type')
            if self_return and other_return:
                return self_return.is_compatible_with(other_return)
        
        return True
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return f"Type({self.name}, {self.kind})"


class TypeSystem:
    """
    Type system for semantic analysis with support for:
    - Type inference
    - Type checking
    - Function/predicate signatures
    - Union types
    """
    
    def __init__(self):
        # Built-in primitive types
        self.primitive_types = {
            'integer': Type('integer'),
            'string': Type('string'),
            'boolean': Type('boolean'),
            'real': Type('real'),
            'number': Type('number'),  # Parent of integer and real
        }
        
        # Type hierarchy
        self.type_hierarchy = {
            'integer': 'number',
            'real': 'number',
        }
        
        # Type for unresolved inference
        self.auto_type = Type('auto', TypeKind.AUTO)
        self.unknown_type = Type('unknown', TypeKind.UNKNOWN)
    
    def get_type(self, type_name: str) -> Type:
        """Get a type by name"""
        if type_name == 'auto':
            return self.auto_type
        return self.primitive_types.get(type_name, self.unknown_type)
    
    def infer_literal_type(self, value: Any, value_type: Optional[str] = None) -> Type:
        """Infer type from a literal value"""
        if value_type == "NUMBER":
            # Check if it's an integer or real
            if isinstance(value, int) or (isinstance(value, str) and '.' not in str(value)):
                return self.primitive_types['integer']
            else:
                return self.primitive_types['real']
        elif value_type == "STRING":
            return self.primitive_types['string']
        elif value_type == "BOOLEAN":
            return self.primitive_types['boolean']
        
        # Fallback type inference based on Python type
        if isinstance(value, bool):
            return self.primitive_types['boolean']
        elif isinstance(value, int):
            return self.primitive_types['integer']
        elif isinstance(value, float):
            return self.primitive_types['real']
        elif isinstance(value, str):
            return self.primitive_types['string']
        
        return self.unknown_type
    
    def infer_binary_op_type(self, left_type: Type, right_type: Type, operator: str) -> Type:
        """Infer result type of binary operation"""
        # Arithmetic operators
        if operator in ['+', '-', '*', '/', '%']:
            # Both must be numeric
            if self._is_numeric(left_type) and self._is_numeric(right_type):
                # If either is real, result is real
                if left_type.name == 'real' or right_type.name == 'real':
                    return self.primitive_types['real']
                return self.primitive_types['integer']
            return self.unknown_type
        
        # Comparison operators
        elif operator in ['<', '>', '<=', '>=', '==', '!=']:
            # Result is always boolean if types are compatible
            if self._are_comparable(left_type, right_type):
                return self.primitive_types['boolean']
            return self.unknown_type
        
        # Boolean operators
        elif operator in ['and', 'or']:
            # Both must be boolean
            if left_type.name == 'boolean' and right_type.name == 'boolean':
                return self.primitive_types['boolean']
            return self.unknown_type
        
        return self.unknown_type
    
    def _is_numeric(self, type_obj: Type) -> bool:
        """Check if type is numeric"""
        return type_obj.name in ['integer', 'real', 'number']
    
    def _are_comparable(self, type1: Type, type2: Type) -> bool:
        """Check if two types can be compared"""
        # Same type is always comparable
        if type1.name == type2.name:
            return True
        
        # Numeric types are comparable
        if self._is_numeric(type1) and self._is_numeric(type2):
            return True
        
        # Strings are only comparable with strings
        if type1.name == 'string' and type2.name == 'string':
            return True
        
        return False
    
    def check_assignment_compatibility(self, target_type: Type, value_type: Type) -> bool:
        """Check if a value type can be assigned to a target type"""
        # Auto type accepts anything
        if target_type.kind == TypeKind.AUTO:
            return True
        
        # Direct compatibility
        if target_type.is_compatible_with(value_type):
            return True
        
        # Check type hierarchy (e.g., integer can be assigned to number)
        value_parent = self.type_hierarchy.get(value_type.name)
        if value_parent and value_parent == target_type.name:
            return True
        
        return False
    
    def create_function_type(self, name: str, param_types: List[Type], return_type: Type) -> Type:
        """Create a function type with signature"""
        func_type = Type(name, TypeKind.FUNCTION)
        func_type.attributes['arity'] = len(param_types)
        func_type.attributes['parameter_types'] = param_types
        func_type.attributes['return_type'] = return_type
        return func_type
    
    def create_predicate_type(self, name: str, param_types: List[Type]) -> Type:
        """Create a predicate type with signature"""
        pred_type = Type(name, TypeKind.PREDICATE)
        pred_type.attributes['arity'] = len(param_types)
        pred_type.attributes['parameter_types'] = param_types
        return pred_type