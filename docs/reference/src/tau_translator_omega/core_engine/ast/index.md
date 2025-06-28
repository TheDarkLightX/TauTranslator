Module src.tau_translator_omega.core_engine.ast
===============================================

Sub-modules
-----------
* src.tau_translator_omega.core_engine.ast.ast_nodes
* src.tau_translator_omega.core_engine.ast.ast_visitor
* src.tau_translator_omega.core_engine.ast.expression_builders

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