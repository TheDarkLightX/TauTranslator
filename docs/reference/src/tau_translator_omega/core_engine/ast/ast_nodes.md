Module src.tau_translator_omega.core_engine.ast.ast_nodes
=========================================================
Defines the base classes and data structures for Abstract Syntax Tree (AST) nodes
used in TauTranslatorOmega.

Classes
-------

`ASTNode(**data: Any)`
:   Base class for all AST nodes.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Descendants

    * src.tau_translator_omega.core_engine.ast.ast_nodes.AttributeDeclarationNode
    * src.tau_translator_omega.core_engine.ast.ast_nodes.BinaryExpressionNode
    * src.tau_translator_omega.core_engine.ast.ast_nodes.BlockNode
    * src.tau_translator_omega.core_engine.ast.ast_nodes.ClassDeclarationNode
    * src.tau_translator_omega.core_engine.ast.ast_nodes.ForLoopNode
    * src.tau_translator_omega.core_engine.ast.ast_nodes.FunctionCallNode
    * src.tau_translator_omega.core_engine.ast.ast_nodes.FunctionDeclarationNode
    * src.tau_translator_omega.core_engine.ast.ast_nodes.IdentifierNode
    * src.tau_translator_omega.core_engine.ast.ast_nodes.IfStatementNode
    * src.tau_translator_omega.core_engine.ast.ast_nodes.ImportSpecifierNode
    * src.tau_translator_omega.core_engine.ast.ast_nodes.ImportStatementNode
    * src.tau_translator_omega.core_engine.ast.ast_nodes.InstanceCreationNode
    * src.tau_translator_omega.core_engine.ast.ast_nodes.LiteralNode
    * src.tau_translator_omega.core_engine.ast.ast_nodes.MemberAccessNode
    * src.tau_translator_omega.core_engine.ast.ast_nodes.MethodDeclarationNode
    * src.tau_translator_omega.core_engine.ast.ast_nodes.ModuleNode
    * src.tau_translator_omega.core_engine.ast.ast_nodes.ParameterNode
    * src.tau_translator_omega.core_engine.ast.ast_nodes.RaiseStatementNode
    * src.tau_translator_omega.core_engine.ast.ast_nodes.ReturnStatementNode
    * src.tau_translator_omega.core_engine.ast.ast_nodes.TryCatchClauseNode
    * src.tau_translator_omega.core_engine.ast.ast_nodes.TryStatementNode
    * src.tau_translator_omega.core_engine.ast.ast_nodes.UnaryExpressionNode
    * src.tau_translator_omega.core_engine.ast.ast_nodes.VariableDeclarationNode
    * src.tau_translator_omega.core_engine.ast.ast_nodes.WhileLoopNode

    ### Class variables

    `location: src.tau_translator_omega.core_engine.ast.ast_nodes.SourceLocation | None`
    :

    `model_config`
    :

`AttributeDeclarationNode(name: src.tau_translator_omega.core_engine.ast.ast_nodes.IdentifierNode, type_hint: src.tau_translator_omega.core_engine.ast.ast_nodes.ASTNode | None = None, initializer: src.tau_translator_omega.core_engine.ast.ast_nodes.ASTNode | None = None, location: src.tau_translator_omega.core_engine.ast.ast_nodes.SourceLocation | None = None)`
:   Represents an attribute (class or instance variable) declaration.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.ast.ast_nodes.ASTNode
    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :

`BinaryExpressionNode(**data: Any)`
:   Represents a binary operation (e.g., a + b, x > y).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.ast.ast_nodes.ASTNode
    * pydantic.main.BaseModel

    ### Class variables

    `left: src.tau_translator_omega.core_engine.ast.ast_nodes.ASTNode`
    :

    `model_config`
    :

    `operator: str`
    :

    `right: src.tau_translator_omega.core_engine.ast.ast_nodes.ASTNode`
    :

`BlockNode(statements: List[src.tau_translator_omega.core_engine.ast.ast_nodes.ASTNode], location: src.tau_translator_omega.core_engine.ast.ast_nodes.SourceLocation | None = None)`
:   Represents a block or sequence of statements.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.ast.ast_nodes.ASTNode
    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :

`ClassDeclarationNode(name: src.tau_translator_omega.core_engine.ast.ast_nodes.IdentifierNode, body: src.tau_translator_omega.core_engine.ast.ast_nodes.BlockNode, base_classes: List[src.tau_translator_omega.core_engine.ast.ast_nodes.IdentifierNode] | None = None, location: src.tau_translator_omega.core_engine.ast.ast_nodes.SourceLocation | None = None)`
:   Represents a class definition.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.ast.ast_nodes.ASTNode
    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :

`ForLoopNode(iterator_variable: src.tau_translator_omega.core_engine.ast.ast_nodes.IdentifierNode, iterable: src.tau_translator_omega.core_engine.ast.ast_nodes.ASTNode, body: src.tau_translator_omega.core_engine.ast.ast_nodes.BlockNode, location: src.tau_translator_omega.core_engine.ast.ast_nodes.SourceLocation | None = None)`
:   Represents a 'for...in' style loop.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.ast.ast_nodes.ASTNode
    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :

`FunctionCallNode(callee: src.tau_translator_omega.core_engine.ast.ast_nodes.ASTNode, arguments: List[src.tau_translator_omega.core_engine.ast.ast_nodes.ASTNode] | None = None, location: src.tau_translator_omega.core_engine.ast.ast_nodes.SourceLocation | None = None)`
:   Represents a function call.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.ast.ast_nodes.ASTNode
    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :

`FunctionDeclarationNode(name: src.tau_translator_omega.core_engine.ast.ast_nodes.IdentifierNode, body: src.tau_translator_omega.core_engine.ast.ast_nodes.BlockNode, parameters: List[src.tau_translator_omega.core_engine.ast.ast_nodes.ParameterNode] | None = None, return_type: src.tau_translator_omega.core_engine.ast.ast_nodes.ASTNode | None = None, location: src.tau_translator_omega.core_engine.ast.ast_nodes.SourceLocation | None = None)`
:   Represents a function definition.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.ast.ast_nodes.ASTNode
    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :

`IdentifierNode(**data: Any)`
:   Represents an identifier (e.g., variable name, function name).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.ast.ast_nodes.ASTNode
    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :

    `name: str`
    :

    ### Static methods

    `validate_name(v)`
    :

`IfStatementNode(condition: src.tau_translator_omega.core_engine.ast.ast_nodes.ASTNode, then_block: src.tau_translator_omega.core_engine.ast.ast_nodes.BlockNode, elif_clauses: List[Tuple[src.tau_translator_omega.core_engine.ast.ast_nodes.ASTNode, src.tau_translator_omega.core_engine.ast.ast_nodes.BlockNode]] | None = None, else_block: src.tau_translator_omega.core_engine.ast.ast_nodes.BlockNode | None = None, location: src.tau_translator_omega.core_engine.ast.ast_nodes.SourceLocation | None = None)`
:   Represents an if-elif-else control flow structure.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.ast.ast_nodes.ASTNode
    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :

`ImportSpecifierNode(name: src.tau_translator_omega.core_engine.ast.ast_nodes.IdentifierNode, alias: src.tau_translator_omega.core_engine.ast.ast_nodes.IdentifierNode | None = None, location: src.tau_translator_omega.core_engine.ast.ast_nodes.SourceLocation | None = None)`
:   Represents an item in an import statement, possibly with an alias.
    e.g., 'name' or 'name as alias' in 'from module import name as alias'.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.ast.ast_nodes.ASTNode
    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :

`ImportStatementNode(module_path: List[src.tau_translator_omega.core_engine.ast.ast_nodes.IdentifierNode], specifiers: List[src.tau_translator_omega.core_engine.ast.ast_nodes.ImportSpecifierNode] | None = None, location: src.tau_translator_omega.core_engine.ast.ast_nodes.SourceLocation | None = None)`
:   Represents an import statement.
    Covers 'import module.submodule' and 'from module import name1, name2 as alias2'.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.ast.ast_nodes.ASTNode
    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :

`InstanceCreationNode(class_identifier: src.tau_translator_omega.core_engine.ast.ast_nodes.ASTNode, arguments: List[src.tau_translator_omega.core_engine.ast.ast_nodes.ASTNode] | None = None, location: src.tau_translator_omega.core_engine.ast.ast_nodes.SourceLocation | None = None)`
:   Represents the creation of a new class instance.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.ast.ast_nodes.ASTNode
    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :

`LiteralNode(**data: Any)`
:   Represents a literal value (e.g., number, string, boolean).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.ast.ast_nodes.ASTNode
    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :

    `value: Any`
    :

`MemberAccessNode(object_expr: src.tau_translator_omega.core_engine.ast.ast_nodes.ASTNode, member_name: src.tau_translator_omega.core_engine.ast.ast_nodes.IdentifierNode, location: src.tau_translator_omega.core_engine.ast.ast_nodes.SourceLocation | None = None)`
:   Represents accessing a member of an object or class.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.ast.ast_nodes.ASTNode
    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :

`MethodDeclarationNode(name: src.tau_translator_omega.core_engine.ast.ast_nodes.IdentifierNode, body: src.tau_translator_omega.core_engine.ast.ast_nodes.BlockNode, parameters: List[src.tau_translator_omega.core_engine.ast.ast_nodes.ParameterNode] | None = None, return_type: src.tau_translator_omega.core_engine.ast.ast_nodes.ASTNode | None = None, location: src.tau_translator_omega.core_engine.ast.ast_nodes.SourceLocation | None = None)`
:   Represents a method definition within a class.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.ast.ast_nodes.ASTNode
    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :

`ModuleNode(body: List[src.tau_translator_omega.core_engine.ast.ast_nodes.ASTNode], location: src.tau_translator_omega.core_engine.ast.ast_nodes.SourceLocation | None = None)`
:   Represents an entire source file or module.
    Often the root node of an AST for a single file.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.ast.ast_nodes.ASTNode
    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :

`ParameterNode(name: src.tau_translator_omega.core_engine.ast.ast_nodes.IdentifierNode, type_hint: src.tau_translator_omega.core_engine.ast.ast_nodes.ASTNode | None = None, location: src.tau_translator_omega.core_engine.ast.ast_nodes.SourceLocation | None = None)`
:   Represents a function parameter.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.ast.ast_nodes.ASTNode
    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :

`RaiseStatementNode(exception_expr: src.tau_translator_omega.core_engine.ast.ast_nodes.ASTNode, location: src.tau_translator_omega.core_engine.ast.ast_nodes.SourceLocation | None = None)`
:   Represents a 'raise' or 'throw' statement.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.ast.ast_nodes.ASTNode
    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :

`ReturnStatementNode(expression: src.tau_translator_omega.core_engine.ast.ast_nodes.ASTNode | None = None, location: src.tau_translator_omega.core_engine.ast.ast_nodes.SourceLocation | None = None)`
:   Represents a return statement.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.ast.ast_nodes.ASTNode
    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :

`SourceLocation(line: int, column: int, end_line: int | None = None, end_column: int | None = None, absolute_char_start_index: int | None = None, absolute_char_end_index: int | None = None)`
:   Represents a location in the source code.

    ### Instance variables

    `absolute_char_end_index: int | None`
    :

    `absolute_char_start_index: int | None`
    :

    `column: int`
    :

    `end_column: int | None`
    :

    `end_line: int | None`
    :

    `line: int`
    :

`TryCatchClauseNode(body: src.tau_translator_omega.core_engine.ast.ast_nodes.BlockNode, exception_types: List[src.tau_translator_omega.core_engine.ast.ast_nodes.ASTNode] | None = None, as_name: src.tau_translator_omega.core_engine.ast.ast_nodes.IdentifierNode | None = None, location: src.tau_translator_omega.core_engine.ast.ast_nodes.SourceLocation | None = None)`
:   Represents a single 'catch' or 'except' clause in a try-statement.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.ast.ast_nodes.ASTNode
    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :

`TryStatementNode(try_block: src.tau_translator_omega.core_engine.ast.ast_nodes.BlockNode, catch_clauses: List[src.tau_translator_omega.core_engine.ast.ast_nodes.TryCatchClauseNode] | None = None, else_block: src.tau_translator_omega.core_engine.ast.ast_nodes.BlockNode | None = None, finally_block: src.tau_translator_omega.core_engine.ast.ast_nodes.BlockNode | None = None, location: src.tau_translator_omega.core_engine.ast.ast_nodes.SourceLocation | None = None)`
:   Represents a try-catch-else-finally structure.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.ast.ast_nodes.ASTNode
    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :

`UnaryExpressionNode(**data: Any)`
:   Represents a unary operation (e.g., -a, not flag).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.ast.ast_nodes.ASTNode
    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :

    `operand: src.tau_translator_omega.core_engine.ast.ast_nodes.ASTNode`
    :

    `operator: str`
    :

`VariableDeclarationNode(identifier: src.tau_translator_omega.core_engine.ast.ast_nodes.IdentifierNode, type_hint: src.tau_translator_omega.core_engine.ast.ast_nodes.ASTNode | None = None, initializer: src.tau_translator_omega.core_engine.ast.ast_nodes.ASTNode | None = None, location: src.tau_translator_omega.core_engine.ast.ast_nodes.SourceLocation | None = None)`
:   Represents a variable declaration.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.ast.ast_nodes.ASTNode
    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :

`WhileLoopNode(condition: src.tau_translator_omega.core_engine.ast.ast_nodes.ASTNode, body: src.tau_translator_omega.core_engine.ast.ast_nodes.BlockNode, location: src.tau_translator_omega.core_engine.ast.ast_nodes.SourceLocation | None = None)`
:   Represents a 'while' loop.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.ast.ast_nodes.ASTNode
    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :