Module src.tau_translator_omega.core_engine.ilr.ilr_nodes
=========================================================
ILR Node Definitions
===================

Defines the Intermediate Logic Representation (ILR) node types
used for translating between natural language and formal languages.

Author: DarkLightX/Dana Edwards

Classes
-------

`ArithmeticExpression(operator: str, operands: List[ForwardRef('ILRNode')])`
:   Arithmetic operation between expressions.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.ilr.ilr_nodes.ILRNode

    ### Instance variables

    `operands: List[src.tau_translator_omega.core_engine.ilr.ilr_nodes.ILRNode]`
    :

    `operator: str`
    :

    ### Methods

    `to_dict(self) ‑> Dict[str, Any]`
    :   Convert to dictionary with proper operand serialization.

`AssignmentStatement(variable: str, value: ILRNode)`
:   Assignment of value to variable.

    ### Instance variables

    `value: src.tau_translator_omega.core_engine.ilr.ilr_nodes.ILRNode`
    :

    `variable: str`
    :

    ### Methods

    `to_dict(self) ‑> Dict[str, Any]`
    :   Convert to dictionary.

`BooleanConstant(value: bool)`
:   Boolean literal value.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.ilr.ilr_nodes.ILRNode

    ### Instance variables

    `value: bool`
    :

`ComparisonExpression(left: ILRNode, operator: str, right: ILRNode)`
:   Comparison between two expressions.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.ilr.ilr_nodes.ILRNode

    ### Instance variables

    `left: src.tau_translator_omega.core_engine.ilr.ilr_nodes.ILRNode`
    :

    `operator: str`
    :

    `right: src.tau_translator_omega.core_engine.ilr.ilr_nodes.ILRNode`
    :

`ConditionalExpression(condition: ILRNode, then_branch: ILRNode, else_branch: ForwardRef('ILRNode') | None = None)`
:   Conditional (if-then-else) expression.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.ilr.ilr_nodes.ILRNode

    ### Instance variables

    `condition: src.tau_translator_omega.core_engine.ilr.ilr_nodes.ILRNode`
    :

    `else_branch: src.tau_translator_omega.core_engine.ilr.ilr_nodes.ILRNode | None`
    :

    `then_branch: src.tau_translator_omega.core_engine.ilr.ilr_nodes.ILRNode`
    :

`FunctionCall(name: str, arguments: List[ForwardRef('ILRNode')])`
:   Function or predicate call.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.ilr.ilr_nodes.ILRNode

    ### Instance variables

    `arguments: List[src.tau_translator_omega.core_engine.ilr.ilr_nodes.ILRNode]`
    :

    `name: str`
    :

`FunctionDeclaration(name: str, parameters: List[str], body: ForwardRef('ILRNode') | None = None, return_type: str | None = None)`
:   Function or predicate declaration.

    ### Instance variables

    `body: src.tau_translator_omega.core_engine.ilr.ilr_nodes.ILRNode | None`
    :

    `name: str`
    :

    `parameters: List[str]`
    :

    `return_type: str | None`
    :

    ### Methods

    `to_dict(self) ‑> Dict[str, Any]`
    :   Convert to dictionary.

`ILRNode(node_type: str)`
:   Base class for ILR nodes.

    ### Descendants

    * src.tau_translator_omega.core_engine.ilr.ilr_nodes.ArithmeticExpression
    * src.tau_translator_omega.core_engine.ilr.ilr_nodes.BooleanConstant
    * src.tau_translator_omega.core_engine.ilr.ilr_nodes.ComparisonExpression
    * src.tau_translator_omega.core_engine.ilr.ilr_nodes.ConditionalExpression
    * src.tau_translator_omega.core_engine.ilr.ilr_nodes.FunctionCall
    * src.tau_translator_omega.core_engine.ilr.ilr_nodes.LogicalExpression
    * src.tau_translator_omega.core_engine.ilr.ilr_nodes.NumericConstant
    * src.tau_translator_omega.core_engine.ilr.ilr_nodes.StringConstant
    * src.tau_translator_omega.core_engine.ilr.ilr_nodes.VariableReference

    ### Instance variables

    `node_type: str`
    :

    ### Methods

    `to_dict(self) ‑> Dict[str, Any]`
    :   Convert to dictionary for JSON serialization.

`LogicalExpression(operator: str, operands: List[ForwardRef('ILRNode')])`
:   Logical operation between expressions.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.ilr.ilr_nodes.ILRNode

    ### Instance variables

    `operands: List[src.tau_translator_omega.core_engine.ilr.ilr_nodes.ILRNode]`
    :

    `operator: str`
    :

`NumericConstant(value: float)`
:   Numeric literal value.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.ilr.ilr_nodes.ILRNode

    ### Instance variables

    `value: float`
    :

`StringConstant(value: str)`
:   String literal value.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.ilr.ilr_nodes.ILRNode

    ### Instance variables

    `value: str`
    :

`VariableDeclaration(name: str, var_type: str | None = None, initial_value: ForwardRef('ILRNode') | None = None, is_stream: bool = False)`
:   Variable declaration with optional type and initial value.

    ### Instance variables

    `initial_value: src.tau_translator_omega.core_engine.ilr.ilr_nodes.ILRNode | None`
    :

    `is_stream: bool`
    :

    `name: str`
    :

    `var_type: str | None`
    :

    ### Methods

    `to_dict(self) ‑> Dict[str, Any]`
    :   Convert to dictionary.

`VariableReference(name: str, temporal_offset: int | None = None)`
:   Reference to a variable or stream.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.ilr.ilr_nodes.ILRNode

    ### Instance variables

    `name: str`
    :

    `temporal_qualifier: Dict[str, Any] | None`
    :