"""
Defines the base classes and data structures for Abstract Syntax Tree (AST) nodes
used in TauTranslatorOmega.
"""

from typing import Optional, Any, List, Tuple
from dataclasses import dataclass, field


@dataclass
class SourceLocation:
    """Represents a location in the source code."""
    line: int
    column: int
    end_line: Optional[int] = None
    end_column: Optional[int] = None
    absolute_char_start_index: Optional[int] = None
    absolute_char_end_index: Optional[int] = None


class ASTNode:
    """Base class for all AST nodes."""
    
    def __init__(self, location: Optional[SourceLocation] = None):
        self.location: Optional[SourceLocation] = location

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"

    # Potentially add methods for tree traversal (e.g., accept(visitor)),
    # or for accessing children, once specific node types are defined.


class IdentifierNode(ASTNode):
    """Represents an identifier (e.g., variable name, function name)."""
    def __init__(self, name: str, location: Optional[SourceLocation] = None):
        super().__init__(location=location)
        self.name: str = name

    def __repr__(self) -> str:
        return f"<IdentifierNode name='{self.name}'>"


class LiteralNode(ASTNode):
    """Represents a literal value (e.g., number, string, boolean)."""
    def __init__(self, value: Any, location: Optional[SourceLocation] = None):
        super().__init__(location=location)
        self.value: Any = value

    def __repr__(self) -> str:
        # For string literals, include quotes in the repr for clarity
        if isinstance(self.value, str):
            return f"<LiteralNode value='{self.value}'>"
        return f"<LiteralNode value={self.value}>"


class BinaryExpressionNode(ASTNode):
    """Represents a binary operation (e.g., a + b, x > y)."""
    def __init__(self, left: ASTNode, operator: str, right: ASTNode, location: Optional[SourceLocation] = None):
        super().__init__(location=location)
        self.left: ASTNode = left
        self.operator: str = operator
        self.right: ASTNode = right

    def __repr__(self) -> str:
        return (
            f"<BinaryExpressionNode "
            f"left={repr(self.left)} "
            f"operator='{self.operator}' "
            f"right={repr(self.right)}>"
        )


class UnaryExpressionNode(ASTNode):
    """Represents a unary operation (e.g., -a, not flag)."""
    def __init__(self, operator: str, operand: ASTNode, location: Optional[SourceLocation] = None):
        super().__init__(location=location)
        self.operator: str = operator
        self.operand: ASTNode = operand

    def __repr__(self) -> str:
        return (
            f"<UnaryExpressionNode "
            f"operator='{self.operator}' "
            f"operand={repr(self.operand)}>"
        )


class BlockNode(ASTNode):
    """Represents a block or sequence of statements."""
    def __init__(self, statements: List[ASTNode], location: Optional[SourceLocation] = None):
        super().__init__(location=location)
        self.statements: List[ASTNode] = statements

    def __repr__(self) -> str:
        return f"<BlockNode statements={len(self.statements)}>"


class VariableDeclarationNode(ASTNode):
    """Represents a variable declaration."""
    def __init__(self, 
                 identifier: IdentifierNode, 
                 type_hint: Optional[ASTNode] = None, 
                 initializer: Optional[ASTNode] = None, 
                 location: Optional[SourceLocation] = None):
        super().__init__(location=location)
        self.identifier: IdentifierNode = identifier
        self.type_hint: Optional[ASTNode] = type_hint
        self.initializer: Optional[ASTNode] = initializer

    def __repr__(self) -> str:
        parts = [f"identifier={repr(self.identifier)}"]
        if self.type_hint:
            parts.append(f"type_hint={repr(self.type_hint)}")
        if self.initializer:
            parts.append(f"initializer={repr(self.initializer)}")
        
        return f"<VariableDeclarationNode {' '.join(parts)}>"


class IfStatementNode(ASTNode):
    """Represents an if-elif-else control flow structure."""
    def __init__(self, 
                 condition: ASTNode, 
                 then_block: BlockNode, 
                 elif_clauses: Optional[List[Tuple[ASTNode, BlockNode]]] = None,
                 else_block: Optional[BlockNode] = None, 
                 location: Optional[SourceLocation] = None):
        super().__init__(location=location)
        self.condition: ASTNode = condition
        self.then_block: BlockNode = then_block
        self.elif_clauses: List[Tuple[ASTNode, BlockNode]] = elif_clauses if elif_clauses is not None else []
        self.else_block: Optional[BlockNode] = else_block

    def __repr__(self) -> str:
        return (
            f"<IfStatementNode condition={repr(self.condition)} "
            f"then_block={repr(self.then_block)} "
            f"elifs={len(self.elif_clauses)} else={self.else_block is not None}>"
        )


class WhileLoopNode(ASTNode):
    """Represents a 'while' loop."""
    def __init__(self, 
                 condition: ASTNode, 
                 body: BlockNode, 
                 location: Optional[SourceLocation] = None):
        super().__init__(location=location)
        self.condition: ASTNode = condition
        self.body: BlockNode = body

    def __repr__(self) -> str:
        return (
            f"<WhileLoopNode condition={repr(self.condition)} "
            f"body={repr(self.body)}>"
        )


class ForLoopNode(ASTNode):
    """Represents a 'for...in' style loop."""
    def __init__(self, 
                 iterator_variable: IdentifierNode, 
                 iterable: ASTNode, 
                 body: BlockNode, 
                 location: Optional[SourceLocation] = None):
        super().__init__(location=location)
        self.iterator_variable: IdentifierNode = iterator_variable
        self.iterable: ASTNode = iterable
        self.body: BlockNode = body

    def __repr__(self) -> str:
        return (
            f"<ForLoopNode iterator_variable={repr(self.iterator_variable)} "
            f"iterable={repr(self.iterable)} "
            f"body={repr(self.body)}>"
        )


# --- Function-related Nodes ---

class ParameterNode(ASTNode):
    """Represents a function parameter."""
    def __init__(self, 
                 name: IdentifierNode, 
                 type_hint: Optional[ASTNode] = None, 
                 location: Optional[SourceLocation] = None):
        super().__init__(location=location)
        self.name: IdentifierNode = name
        self.type_hint: Optional[ASTNode] = type_hint

    def __repr__(self) -> str:
        parts = [f"name={repr(self.name)}"]
        if self.type_hint:
            parts.append(f"type_hint={repr(self.type_hint)}")
        return f"<{self.__class__.__name__} {' '.join(parts)}>"


class FunctionDeclarationNode(ASTNode):
    """Represents a function definition."""
    def __init__(self, 
                 name: IdentifierNode, 
                 body: BlockNode,
                 parameters: Optional[List[ParameterNode]] = None, 
                 return_type: Optional[ASTNode] = None, 
                 location: Optional[SourceLocation] = None):
        super().__init__(location=location)
        self.name: IdentifierNode = name
        self.parameters: List[ParameterNode] = parameters if parameters is not None else []
        self.return_type: Optional[ASTNode] = return_type
        self.body: BlockNode = body

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} name={repr(self.name)} "
            f"params={len(self.parameters)} return_type={self.return_type is not None} "
            f"body_stmts={len(self.body.statements) if self.body else 0}>"
        )


class FunctionCallNode(ASTNode):
    """Represents a function call."""
    def __init__(self, 
                 callee: ASTNode, 
                 arguments: Optional[List[ASTNode]] = None, 
                 location: Optional[SourceLocation] = None):
        super().__init__(location=location)
        self.callee: ASTNode = callee
        self.arguments: List[ASTNode] = arguments if arguments is not None else []

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} callee={repr(self.callee)} "
            f"args={len(self.arguments)}>"
        )


class ReturnStatementNode(ASTNode):
    """Represents a return statement."""
    def __init__(self, 
                 expression: Optional[ASTNode] = None, 
                 location: Optional[SourceLocation] = None):
        super().__init__(location=location)
        self.expression: Optional[ASTNode] = expression

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} expression={self.expression is not None}>"
        )


# --- Class-related Nodes ---

class ClassDeclarationNode(ASTNode):
    """Represents a class definition."""
    def __init__(self, 
                 name: IdentifierNode, 
                 body: BlockNode, 
                 base_classes: Optional[List[IdentifierNode]] = None,
                 location: Optional[SourceLocation] = None):
        super().__init__(location=location)
        self.name: IdentifierNode = name
        self.base_classes: List[IdentifierNode] = base_classes if base_classes is not None else []
        self.body: BlockNode = body # Contains MethodDeclarationNode, AttributeDeclarationNode

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} name={repr(self.name)} "
            f"bases={len(self.base_classes)} "
            f"body_items={len(self.body.statements) if self.body else 0}>"
        )


class MethodDeclarationNode(ASTNode): # Similar to FunctionDeclarationNode
    """Represents a method definition within a class."""
    def __init__(self, 
                 name: IdentifierNode, 
                 body: BlockNode,
                 parameters: Optional[List[ParameterNode]] = None, 
                 return_type: Optional[ASTNode] = None, 
                 location: Optional[SourceLocation] = None):
        super().__init__(location=location)
        self.name: IdentifierNode = name
        self.parameters: List[ParameterNode] = parameters if parameters is not None else []
        self.return_type: Optional[ASTNode] = return_type
        self.body: BlockNode = body

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} name={repr(self.name)} "
            f"params={len(self.parameters)} return_type={self.return_type is not None} "
            f"body_stmts={len(self.body.statements) if self.body else 0}>"
        )


class AttributeDeclarationNode(ASTNode): # Similar to VariableDeclarationNode
    """Represents an attribute (class or instance variable) declaration."""
    def __init__(self, 
                 name: IdentifierNode, 
                 type_hint: Optional[ASTNode] = None, 
                 initializer: Optional[ASTNode] = None, 
                 location: Optional[SourceLocation] = None):
        super().__init__(location=location)
        self.name: IdentifierNode = name
        self.type_hint: Optional[ASTNode] = type_hint
        self.initializer: Optional[ASTNode] = initializer

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} name={repr(self.name)} "
            f"type_hint={self.type_hint is not None} "
            f"initializer={self.initializer is not None}>"
        )


class InstanceCreationNode(ASTNode): # e.g., new MyClass() or MyClass()
    """Represents the creation of a new class instance."""
    def __init__(self, 
                 class_identifier: ASTNode, # Typically IdentifierNode
                 arguments: Optional[List[ASTNode]] = None, 
                 location: Optional[SourceLocation] = None):
        super().__init__(location=location)
        self.class_identifier: ASTNode = class_identifier
        self.arguments: List[ASTNode] = arguments if arguments is not None else []

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} class={repr(self.class_identifier)} "
            f"args={len(self.arguments)}>"
        )


class MemberAccessNode(ASTNode): # e.g., object.property or object.method_name
    """Represents accessing a member of an object or class."""
    def __init__(self, 
                 object_expr: ASTNode, 
                 member_name: IdentifierNode, 
                 location: Optional[SourceLocation] = None):
        super().__init__(location=location)
        self.object_expr: ASTNode = object_expr
        self.member_name: IdentifierNode = member_name

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} object={repr(self.object_expr)} "
            f"member={repr(self.member_name)}>"
        )


# --- Module and Import-related Nodes ---

class ImportSpecifierNode(ASTNode):
    """Represents an item in an import statement, possibly with an alias.
    e.g., 'name' or 'name as alias' in 'from module import name as alias'.
    """
    def __init__(self, 
                 name: IdentifierNode, 
                 alias: Optional[IdentifierNode] = None, 
                 location: Optional[SourceLocation] = None):
        super().__init__(location=location)
        self.name: IdentifierNode = name
        self.alias: Optional[IdentifierNode] = alias

    def __repr__(self) -> str:
        parts = [f"name={repr(self.name)}"]
        if self.alias:
            parts.append(f"alias={repr(self.alias)}")
        return f"<{self.__class__.__name__} {' '.join(parts)}>"


class ImportStatementNode(ASTNode):
    """Represents an import statement.
    Covers 'import module.submodule' and 'from module import name1, name2 as alias2'.
    """
    def __init__(self, 
                 module_path: List[IdentifierNode], 
                 specifiers: Optional[List[ImportSpecifierNode]] = None,
                 location: Optional[SourceLocation] = None):
        super().__init__(location=location)
        self.module_path: List[IdentifierNode] = module_path
        # If specifiers is None or empty, it's a direct module import (e.g., import my_module)
        # Otherwise, it's a 'from module import ...' style import.
        self.specifiers: Optional[List[ImportSpecifierNode]] = specifiers

    def __repr__(self) -> str:
        path_str = '.'.join(p.name for p in self.module_path)
        num_specifiers = len(self.specifiers) if self.specifiers is not None else 0
        return (
            f"<{self.__class__.__name__} path='{path_str}' "
            f"specifiers={num_specifiers}>"
        )


class ModuleNode(ASTNode):
    """Represents an entire source file or module.
    Often the root node of an AST for a single file.
    """
    def __init__(self, 
                 body: List[ASTNode], 
                 location: Optional[SourceLocation] = None):
        super().__init__(location=location)
        self.body: List[ASTNode] = body # List of top-level statements/declarations

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} body_items={len(self.body)}>"
        )


# --- Exception Handling Nodes ---

class TryCatchClauseNode(ASTNode):
    """Represents a single 'catch' or 'except' clause in a try-statement."""
    def __init__(self, 
                 body: BlockNode,
                 exception_types: Optional[List[ASTNode]] = None, # List of IdentifierNode or similar
                 as_name: Optional[IdentifierNode] = None,
                 location: Optional[SourceLocation] = None):
        super().__init__(location=location)
        self.exception_types: List[ASTNode] = exception_types if exception_types is not None else []
        self.as_name: Optional[IdentifierNode] = as_name
        self.body: BlockNode = body

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} types={len(self.exception_types)} "
            f"as_name={self.as_name is not None} "
            f"body_stmts={len(self.body.statements) if self.body else 0}>"
        )


class RaiseStatementNode(ASTNode):
    """Represents a 'raise' or 'throw' statement."""
    def __init__(self, 
                 exception_expr: ASTNode, 
                 location: Optional[SourceLocation] = None):
        super().__init__(location=location)
        self.exception_expr: ASTNode = exception_expr

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} expr={repr(self.exception_expr)}>"
        )


class TryStatementNode(ASTNode):
    """Represents a try-catch-else-finally structure."""
    def __init__(self, 
                 try_block: BlockNode,
                 catch_clauses: Optional[List[TryCatchClauseNode]] = None,
                 else_block: Optional[BlockNode] = None,
                 finally_block: Optional[BlockNode] = None,
                 location: Optional[SourceLocation] = None):
        super().__init__(location=location)
        self.try_block: BlockNode = try_block
        self.catch_clauses: List[TryCatchClauseNode] = catch_clauses if catch_clauses is not None else []
        self.else_block: Optional[BlockNode] = else_block
        self.finally_block: Optional[BlockNode] = finally_block

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} "
            f"try_stmts={len(self.try_block.statements) if self.try_block else 0} "
            f"catches={len(self.catch_clauses)} "
            f"else={self.else_block is not None} "
            f"finally={self.finally_block is not None}>"
        )
