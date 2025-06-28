Module src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes
========================================================================

Classes
-------

`ASTNode(line: int | None = None, column: int | None = None)`
:   Base class for all AST nodes.

    ### Descendants

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.AssignmentNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.BitvectorDeclarationNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ConceptDeclarationNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ConditionNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.DefinitionNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.FactNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.FunctionDefinitionNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.MathematicalAssertionNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.MetaFieldNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.MetaStatementNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ParameterNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.PredicateDefNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.PredicateDefinitionNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.QuantifierBlockNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.RecurrenceCaseNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.RecurrenceDefinitionNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.RuleNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.SentenceNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.SolverCommandNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.StreamDeclarationNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.TimeSpecNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.VariableDeclNode

    ### Instance variables

    `column: int | None`
    :

    `line: int | None`
    :

`ArithmeticBinaryOpNode(line: int | None = None, column: int | None = None, left: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ArithmeticNode | None = None, operator: str = 'plus', right: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ArithmeticNode | None = None)`
:   ArithmeticBinaryOpNode(line: Optional[int] = None, column: Optional[int] = None, left: Optional[src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ArithmeticNode] = None, operator: str = 'plus', right: Optional[src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ArithmeticNode] = None)

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ArithmeticNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode

    ### Instance variables

    `column: int | None`
    :

    `left: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ArithmeticNode | None`
    :

    `line: int | None`
    :

    `operator: str`
    :

    `right: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ArithmeticNode | None`
    :

`ArithmeticNode(line: int | None = None, column: int | None = None)`
:   Base class for nodes that can be part of an arithmetic expression.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode

    ### Descendants

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ArithmeticBinaryOpNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ArithmeticUnaryOpNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ConstantNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.EnhancedArithmeticNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.NumberNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.PredicateCallNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.VariableNode

`ArithmeticUnaryOpNode(line: int | None = None, column: int | None = None, operator: str = '+', operand: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ArithmeticNode | None = None)`
:   ArithmeticUnaryOpNode(line: Optional[int] = None, column: Optional[int] = None, operator: str = '+', operand: Optional[src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ArithmeticNode] = None)

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ArithmeticNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode

    ### Instance variables

    `column: int | None`
    :

    `line: int | None`
    :

    `operand: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ArithmeticNode | None`
    :

    `operator: str`
    :

`AssignmentNode(line: int | None = None, column: int | None = None, target: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.VariableNode | None = None, expression: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode | None = None)`
:   AssignmentNode(line: Optional[int] = None, column: Optional[int] = None, target: Optional[src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.VariableNode] = None, expression: Optional[src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode] = None)

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode

    ### Instance variables

    `column: int | None`
    :

    `expression: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode | None`
    :

    `line: int | None`
    :

    `target: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.VariableNode | None`
    :

`AtomNode(line: int | None = None, column: int | None = None)`
:   Base class for atomic elements in expressions.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode

    ### Descendants

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.BitvectorLiteralNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ConstantNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.NumberNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.StreamReferenceNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.StringNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.VariableNode

`BitvectorDeclarationNode(line: int | None = None, column: int | None = None, name: str = '', width: int = 32)`
:   Represents a bitvector declaration.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode

    ### Instance variables

    `column: int | None`
    :

    `line: int | None`
    :

    `name: str`
    :

    `width: int`
    :

`BitvectorLiteralNode(line: int | None = None, column: int | None = None, value: str = '0', format: str = 'decimal')`
:   Represents bitvector literals (0xFF, 0b1010).

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.AtomNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode

    ### Instance variables

    `column: int | None`
    :

    `format: str`
    :

    `line: int | None`
    :

    `value: str`
    :

`BitvectorOperationNode(line: int | None = None, column: int | None = None, left: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode | None = None, operator: str = 'and', right: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode | None = None)`
:   Represents bitvector operations.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode

    ### Instance variables

    `column: int | None`
    :

    `left: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode | None`
    :

    `line: int | None`
    :

    `operator: str`
    :

    `right: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode | None`
    :

`BooleanBinaryOpNode(line: int | None = None, column: int | None = None, left: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode | None = None, operator: str = 'and', right: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode | None = None)`
:   BooleanBinaryOpNode(line: Optional[int] = None, column: Optional[int] = None, left: Optional[src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode] = None, operator: str = 'and', right: Optional[src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode] = None)

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode

    ### Instance variables

    `column: int | None`
    :

    `left: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode | None`
    :

    `line: int | None`
    :

    `operator: str`
    :

    `right: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode | None`
    :

`BooleanUnaryOpNode(line: int | None = None, column: int | None = None, operator: str = 'not', operand: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode | None = None)`
:   BooleanUnaryOpNode(line: Optional[int] = None, column: Optional[int] = None, operator: str = 'not', operand: Optional[src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode] = None)

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode

    ### Instance variables

    `column: int | None`
    :

    `line: int | None`
    :

    `operand: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode | None`
    :

    `operator: str`
    :

`ComparisonNode(line: int | None = None, column: int | None = None, left: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ArithmeticNode | None = None, operator: str = 'equals', right: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ArithmeticNode | None = None)`
:   ComparisonNode(line: Optional[int] = None, column: Optional[int] = None, left: Optional[src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ArithmeticNode] = None, operator: str = 'equals', right: Optional[src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ArithmeticNode] = None)

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode

    ### Instance variables

    `column: int | None`
    :

    `left: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ArithmeticNode | None`
    :

    `line: int | None`
    :

    `operator: str`
    :

    `right: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ArithmeticNode | None`
    :

`ConceptDeclarationNode(line: int | None = None, column: int | None = None, name: str = '', description: str | None = None)`
:   Represents concept declarations.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode

    ### Instance variables

    `column: int | None`
    :

    `description: str | None`
    :

    `line: int | None`
    :

    `name: str`
    :

`ConditionNode(line: int | None = None, column: int | None = None, expression: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode | None = None, quant_block: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.QuantifierBlockNode | None = None)`
:   Represents the conditional part of a rule or a quantified expression.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode

    ### Instance variables

    `column: int | None`
    :

    `expression: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode | None`
    :

    `line: int | None`
    :

    `quant_block: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.QuantifierBlockNode | None`
    :

`ConditionalExpressionNode(line: int | None = None, column: int | None = None, condition: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode | None = None, consequent: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode | None = None, conditional_type: str = 'if_then')`
:   Represents conditional expressions (if-then, when-then).

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode

    ### Instance variables

    `column: int | None`
    :

    `condition: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode | None`
    :

    `conditional_type: str`
    :

    `consequent: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode | None`
    :

    `line: int | None`
    :

`ConstantNode(line: int | None = None, column: int | None = None, value: Any = None, value_type: str = 'UNKNOWN')`
:   ConstantNode(line: Optional[int] = None, column: Optional[int] = None, value: Any = None, value_type: str = 'UNKNOWN')

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.AtomNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ArithmeticNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode

    ### Instance variables

    `column: int | None`
    :

    `line: int | None`
    :

    `value: Any`
    :

    `value_type: str`
    :

`DefinitionNode(line: int | None = None, column: int | None = None, name: str = '', parameters: List[src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ParameterNode] = <factory>, body: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode | None = None, is_function: bool = False, return_type: str | None = None)`
:   DefinitionNode(line: Optional[int] = None, column: Optional[int] = None, name: str = '', parameters: List[src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ParameterNode] = <factory>, body: Optional[src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode] = None, is_function: bool = False, return_type: Optional[str] = None)

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode

    ### Instance variables

    `body: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode | None`
    :

    `column: int | None`
    :

    `is_function: bool`
    :

    `line: int | None`
    :

    `name: str`
    :

    `parameters: List[src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ParameterNode]`
    :

    `return_type: str | None`
    :

`EnhancedArithmeticNode(line: int | None = None, column: int | None = None, left: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ArithmeticNode | None = None, operator: str = 'plus', right: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ArithmeticNode | None = None)`
:   Enhanced arithmetic operations including power, root, modulo.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ArithmeticNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode

    ### Instance variables

    `column: int | None`
    :

    `left: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ArithmeticNode | None`
    :

    `line: int | None`
    :

    `operator: str`
    :

    `right: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ArithmeticNode | None`
    :

`ExprNode(line: int | None = None, column: int | None = None)`
:   Base class for all nodes that can be part of an expression.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode

    ### Descendants

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ArithmeticNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.AtomNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.BitvectorOperationNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.BooleanBinaryOpNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.BooleanUnaryOpNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ComparisonNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ConditionalExpressionNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.FunctionCallWithIndexNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.QuantifiedExpressionNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.SetOperationNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.TemporalQuantifierNode

`FactNode(line: int | None = None, column: int | None = None, statement: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode | None = None)`
:   FactNode(line: Optional[int] = None, column: Optional[int] = None, statement: Optional[src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode] = None)

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode

    ### Instance variables

    `column: int | None`
    :

    `line: int | None`
    :

    `statement: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode | None`
    :   A fact can contain any expression as its statement.

`FunctionCallWithIndexNode(line: int | None = None, column: int | None = None, name: str = '', index: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode | None = None, arguments: List[src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode] = <factory>)`
:   Represents function calls with index (for recurrence relations).

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode

    ### Instance variables

    `arguments: List[src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode]`
    :

    `column: int | None`
    :

    `index: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode | None`
    :

    `line: int | None`
    :

    `name: str`
    :

`FunctionDefinitionNode(line: int | None = None, column: int | None = None, name: str = '', parameters: List[src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ParameterNode] = None, body: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode | None = None, is_recurrence: bool = False, recurrence_index: str | None = None)`
:   Represents a function definition with mathematical semantics.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode

    ### Instance variables

    `body: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode | None`
    :

    `column: int | None`
    :

    `is_recurrence: bool`
    :

    `line: int | None`
    :

    `name: str`
    :

    `parameters: List[src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ParameterNode]`
    :

    `recurrence_index: str | None`
    :

`MathematicalAssertionNode(line: int | None = None, column: int | None = None, assertion_type: str = 'assert', expression: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode | None = None)`
:   Represents mathematical assertions.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode

    ### Instance variables

    `assertion_type: str`
    :

    `column: int | None`
    :

    `expression: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode | None`
    :

    `line: int | None`
    :

`MetaFieldNode(line: int | None = None, column: int | None = None, key: str = '', value: str | List[str] = '')`
:   Represents a single meta field.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode

    ### Instance variables

    `column: int | None`
    :

    `key: str`
    :

    `line: int | None`
    :

    `value: str | List[str]`
    :

`MetaStatementNode(line: int | None = None, column: int | None = None, fields: List[ForwardRef('MetaFieldNode')] = <factory>)`
:   Represents meta statements with metadata.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode

    ### Instance variables

    `column: int | None`
    :

    `fields: List[src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.MetaFieldNode]`
    :

    `line: int | None`
    :

`NumberNode(line: int | None = None, column: int | None = None, value: int | float | str = 0)`
:   Represents a numeric literal.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.AtomNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ArithmeticNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode

    ### Instance variables

    `column: int | None`
    :

    `line: int | None`
    :

    `value: int | float | str`
    :

`ParameterNode(line: int | None = None, column: int | None = None, name: str = '', param_type: str | None = None)`
:   ParameterNode(line: Optional[int] = None, column: Optional[int] = None, name: str = '', param_type: Optional[str] = None)

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode

    ### Instance variables

    `column: int | None`
    :

    `line: int | None`
    :

    `name: str`
    :

    `param_type: str | None`
    :

`PredicateCallNode(line: int | None = None, column: int | None = None, name: str = '', args: List[src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode] = <factory>)`
:   PredicateCallNode(line: Optional[int] = None, column: Optional[int] = None, name: str = '', args: List[src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode] = <factory>)

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ArithmeticNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode

    ### Instance variables

    `args: List[src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode]`
    :

    `column: int | None`
    :

    `line: int | None`
    :

    `name: str`
    :

`PredicateDefNode(line: int | None = None, column: int | None = None, name: str = '', parameters: List[src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ParameterNode] = <factory>, is_function: bool = False)`
:   PredicateDefNode(line: Optional[int] = None, column: Optional[int] = None, name: str = '', parameters: List[src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ParameterNode] = <factory>, is_function: bool = False)

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode

    ### Instance variables

    `column: int | None`
    :

    `is_function: bool`
    :

    `line: int | None`
    :

    `name: str`
    :

    `parameters: List[src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ParameterNode]`
    :

`PredicateDefinitionNode(line: int | None = None, column: int | None = None, name: str = '', parameters: List[src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ParameterNode] = None, body: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode | None = None)`
:   Represents a predicate definition with logical semantics.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode

    ### Instance variables

    `body: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode | None`
    :

    `column: int | None`
    :

    `line: int | None`
    :

    `name: str`
    :

    `parameters: List[src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ParameterNode]`
    :

`QuantifiedExpressionNode(line: int | None = None, column: int | None = None, quantifier: str = 'for_all', variables: List[src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.VariableNode] = <factory>, expression: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode | None = None)`
:   Represents quantified expressions (for all, there exists).

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode

    ### Instance variables

    `column: int | None`
    :

    `expression: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode | None`
    :

    `line: int | None`
    :

    `quantifier: str`
    :

    `variables: List[src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.VariableNode]`
    :

`QuantifierBlockNode(line: int | None = None, column: int | None = None, quant_type: str = 'forall', variables: List[src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.VariableNode] = <factory>, condition: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode | None = None)`
:   QuantifierBlockNode(line: Optional[int] = None, column: Optional[int] = None, quant_type: str = 'forall', variables: List[src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.VariableNode] = <factory>, condition: Optional[src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode] = None)

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode

    ### Instance variables

    `column: int | None`
    :

    `condition: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode | None`
    :

    `line: int | None`
    :

    `quant_type: str`
    :

    `variables: List[src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.VariableNode]`
    :

`RecurrenceCaseNode(line: int | None = None, column: int | None = None, index: int | str = 0, parameters: List[src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ParameterNode] = None, body: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode | None = None)`
:   Represents a single case in a recurrence relation.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode

    ### Instance variables

    `body: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode | None`
    :

    `column: int | None`
    :

    `index: int | str`
    :

    `line: int | None`
    :

    `parameters: List[src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ParameterNode]`
    :

`RecurrenceDefinitionNode(line: int | None = None, column: int | None = None, name: str = '', base_cases: List[ForwardRef('RecurrenceCaseNode')] = None, recursive_cases: List[ForwardRef('RecurrenceCaseNode')] = None)`
:   Represents a recurrence relation definition.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode

    ### Instance variables

    `base_cases: List[src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.RecurrenceCaseNode]`
    :

    `column: int | None`
    :

    `line: int | None`
    :

    `name: str`
    :

    `recursive_cases: List[src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.RecurrenceCaseNode]`
    :

`RuleNode(line: int | None = None, column: int | None = None, condition: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ConditionNode | None = None, consequent: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.PredicateCallNode | None = None)`
:   RuleNode(line: Optional[int] = None, column: Optional[int] = None, condition: Optional[src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ConditionNode] = None, consequent: Optional[src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.PredicateCallNode] = None)

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode

    ### Instance variables

    `column: int | None`
    :

    `condition: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ConditionNode | None`
    :

    `consequent: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.PredicateCallNode | None`
    :

    `line: int | None`
    :

`SentenceNode(line: int | None = None, column: int | None = None, content: List[src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode | src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode] = <factory>)`
:   SentenceNode(line: Optional[int] = None, column: Optional[int] = None, content: List[Union[src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode, src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode]] = <factory>)

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode

    ### Instance variables

    `column: int | None`
    :

    `content: List[src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode | src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode]`
    :

    `line: int | None`
    :

`SetOperationNode(line: int | None = None, column: int | None = None, left: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode | None = None, operator: str = 'intersected_with', right: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode | None = None)`
:   Represents set operations (intersection, union, complement).

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode

    ### Instance variables

    `column: int | None`
    :

    `left: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode | None`
    :

    `line: int | None`
    :

    `operator: str`
    :

    `right: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode | None`
    :

`SolverCommandNode(line: int | None = None, column: int | None = None, command_type: str = 'sat', expression: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode | None = None, variables: List[str] | None = None)`
:   Represents solver commands.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode

    ### Instance variables

    `column: int | None`
    :

    `command_type: str`
    :

    `expression: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode | None`
    :

    `line: int | None`
    :

    `variables: List[str] | None`
    :

`StreamDeclarationNode(line: int | None = None, column: int | None = None, identifier: str = '', version: str | None = None)`
:   Represents stream declarations.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode

    ### Instance variables

    `column: int | None`
    :

    `identifier: str`
    :

    `line: int | None`
    :

    `version: str | None`
    :

`StreamReferenceNode(line: int | None = None, column: int | None = None, name: str = '', time_spec: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.TimeSpecNode | None = None, stream_type: str | None = None)`
:   StreamReferenceNode(line: Optional[int] = None, column: Optional[int] = None, name: str = '', time_spec: Optional[src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.TimeSpecNode] = None, stream_type: Optional[str] = None)

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.AtomNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode

    ### Instance variables

    `column: int | None`
    :

    `line: int | None`
    :

    `name: str`
    :

    `stream_type: str | None`
    :

    `time_spec: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.TimeSpecNode | None`
    :

`StringNode(line: int | None = None, column: int | None = None, value: str = '')`
:   Represents a string literal.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.AtomNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode

    ### Instance variables

    `column: int | None`
    :

    `line: int | None`
    :

    `value: str`
    :

`TemporalQuantifierNode(line: int | None = None, column: int | None = None, quantifier: str = 'always', expression: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode | None = None)`
:   Represents temporal quantifiers (always, sometimes, eventually, never).

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode

    ### Instance variables

    `column: int | None`
    :

    `expression: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode | None`
    :

    `line: int | None`
    :

    `quantifier: str`
    :

`TimeLiteralNode(line: int | None = None, column: int | None = None, value: int = 0)`
:   TimeLiteralNode(line: Optional[int] = None, column: Optional[int] = None, value: int = 0)

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.TimeSpecNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode

    ### Instance variables

    `column: int | None`
    :

    `line: int | None`
    :

    `value: int`
    :

`TimeOffsetNode(line: int | None = None, column: int | None = None, variable: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.VariableNode | None = None, operator: str = '+', offset: int = 0)`
:   TimeOffsetNode(line: Optional[int] = None, column: Optional[int] = None, variable: Optional[src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.VariableNode] = None, operator: str = '+', offset: int = 0)

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.TimeSpecNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode

    ### Instance variables

    `column: int | None`
    :

    `line: int | None`
    :

    `offset: int`
    :

    `operator: str`
    :

    `variable: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.VariableNode | None`
    :

`TimeSpecNode(line: int | None = None, column: int | None = None)`
:   Base class for time specifications.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode

    ### Descendants

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.TimeLiteralNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.TimeOffsetNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.TimeVariableNode

`TimeVariableNode(line: int | None = None, column: int | None = None, variable_name: str = '')`
:   TimeVariableNode(line: Optional[int] = None, column: Optional[int] = None, variable_name: str = '')

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.TimeSpecNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode

    ### Instance variables

    `column: int | None`
    :

    `line: int | None`
    :

    `variable_name: str`
    :

`VariableDeclNode(line: int | None = None, column: int | None = None, name: str = '', var_type: str = 'auto', value: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode | None = None)`
:   Represents a variable declaration, e.g., 'let x: integer = 5'.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode

    ### Instance variables

    `column: int | None`
    :

    `line: int | None`
    :

    `name: str`
    :

    `value: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode | None`
    :

    `var_type: str`
    :

`VariableNode(line: int | None = None, column: int | None = None, name: str = '')`
:   VariableNode(line: Optional[int] = None, column: Optional[int] = None, name: str = '')

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.AtomNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ArithmeticNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ExprNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode

    ### Instance variables

    `column: int | None`
    :

    `line: int | None`
    :

    `name: str`
    :