Module src.tau_translator_omega.core_engine.translators.ilr_translator
======================================================================
ILR-based Natural Language Translator
====================================

Translates natural language to ILR (Intermediate Logic Representation) in JSON format,
which can then be converted to TAU or other target languages.

Classes
-------

`ArithmeticExpression(operator: str, left: src.tau_translator_omega.core_engine.translators.ilr_translator.ILRNode | None = None, right: src.tau_translator_omega.core_engine.translators.ilr_translator.ILRNode | None = None, operand: src.tau_translator_omega.core_engine.translators.ilr_translator.ILRNode | None = None)`
:   Arithmetic operation.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.translators.ilr_translator.ILRNode

    ### Instance variables

    `left_operand: Dict[str, Any] | None`
    :

    `operand: Dict[str, Any] | None`
    :

    `operator: str`
    :

    `right_operand: Dict[str, Any] | None`
    :

`AssignmentStatement(target: Dict[str, Any], expression: Dict[str, Any], node_type: str = 'ASSIGNMENT_STATEMENT')`
:   Assignment statement.

    ### Instance variables

    `expression: Dict[str, Any]`
    :

    `node_type: str`
    :

    `target: Dict[str, Any]`
    :

    ### Methods

    `to_dict(self) ‑> Dict[str, Any]`
    :

`BooleanConstant(value: bool)`
:   Boolean literal value.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.translators.ilr_translator.ILRNode

    ### Instance variables

    `value: bool`
    :

`ComparisonExpression(operator: str, left: src.tau_translator_omega.core_engine.translators.ilr_translator.ILRNode, right: src.tau_translator_omega.core_engine.translators.ilr_translator.ILRNode)`
:   Comparison between two expressions.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.translators.ilr_translator.ILRNode

    ### Instance variables

    `left_operand: Dict[str, Any]`
    :

    `operator: str`
    :

    `right_operand: Dict[str, Any]`
    :

`ConditionalExpression(condition: src.tau_translator_omega.core_engine.translators.ilr_translator.ILRNode, if_true: src.tau_translator_omega.core_engine.translators.ilr_translator.ILRNode, if_false: src.tau_translator_omega.core_engine.translators.ilr_translator.ILRNode)`
:   If-then-else expression.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.translators.ilr_translator.ILRNode

    ### Instance variables

    `condition: Dict[str, Any]`
    :

    `value_if_false: Dict[str, Any]`
    :

    `value_if_true: Dict[str, Any]`
    :

`FunctionCall(function_name: str, *arguments: src.tau_translator_omega.core_engine.translators.ilr_translator.ILRNode)`
:   Function call expression.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.translators.ilr_translator.ILRNode

    ### Instance variables

    `arguments: List[Dict[str, Any]]`
    :

    `function_name: str`
    :

`FunctionDeclaration(name: str, parameters: List[Dict[str, Any]], return_type: str, node_type: str = 'FUNCTION_DECLARATION', body: List[Dict[str, Any]] | None = None)`
:   Function declaration.

    ### Instance variables

    `body: List[Dict[str, Any]] | None`
    :

    `name: str`
    :

    `node_type: str`
    :

    `parameters: List[Dict[str, Any]]`
    :

    `return_type: str`
    :

    ### Methods

    `to_dict(self) ‑> Dict[str, Any]`
    :

`ILRNode(node_type: str)`
:   Base class for ILR nodes.

    ### Descendants

    * src.tau_translator_omega.core_engine.translators.ilr_translator.ArithmeticExpression
    * src.tau_translator_omega.core_engine.translators.ilr_translator.BooleanConstant
    * src.tau_translator_omega.core_engine.translators.ilr_translator.ComparisonExpression
    * src.tau_translator_omega.core_engine.translators.ilr_translator.ConditionalExpression
    * src.tau_translator_omega.core_engine.translators.ilr_translator.FunctionCall
    * src.tau_translator_omega.core_engine.translators.ilr_translator.LogicalExpression
    * src.tau_translator_omega.core_engine.translators.ilr_translator.NumericConstant
    * src.tau_translator_omega.core_engine.translators.ilr_translator.StringConstant
    * src.tau_translator_omega.core_engine.translators.ilr_translator.VariableReference

    ### Instance variables

    `node_type: str`
    :

    ### Methods

    `to_dict(self) ‑> Dict[str, Any]`
    :   Convert to dictionary for JSON serialization.

`ILRToTauTranslator()`
:   Translates ILR (JSON) to TAU format.

    ### Methods

    `translate_to_tau(self, ilr: Dict[str, Any]) ‑> str`
    :   Translate ILR to TAU syntax.

`LogicalExpression(operator: str, *operands: src.tau_translator_omega.core_engine.translators.ilr_translator.ILRNode)`
:   Logical operation (AND, OR, XOR, NOT).

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.translators.ilr_translator.ILRNode

    ### Instance variables

    `operands: List[Dict[str, Any]]`
    :

    `operator: str`
    :

`NaturalLanguageToILRTranslator(vocabulary: Dict[str, Any] | None = None)`
:   Translates natural language to ILR (JSON intermediate representation).

    ### Methods

    `translate_to_ilr(self, nl_text: str) ‑> Dict[str, Any]`
    :   Translate natural language to ILR format.

`NumericConstant(value: int | float)`
:   Numeric literal value.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.translators.ilr_translator.ILRNode

    ### Instance variables

    `value: int | float`
    :

`StringConstant(value: str)`
:   String literal value.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.translators.ilr_translator.ILRNode

    ### Instance variables

    `value: str`
    :

`VariableDeclaration(name: str, data_type: Dict[str, Any], node_type: str = 'VARIABLE_DECLARATION', is_constant: bool = False, is_stream: bool = False, initial_value: Dict[str, Any] | None = None)`
:   Variable declaration.

    ### Instance variables

    `data_type: Dict[str, Any]`
    :

    `initial_value: Dict[str, Any] | None`
    :

    `is_constant: bool`
    :

    `is_stream: bool`
    :

    `name: str`
    :

    `node_type: str`
    :

    ### Methods

    `to_dict(self) ‑> Dict[str, Any]`
    :

`VariableReference(name: str, temporal_offset: int | None = None)`
:   Reference to a variable or stream.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.translators.ilr_translator.ILRNode

    ### Instance variables

    `name: str`
    :

    `temporal_qualifier: Dict[str, Any] | None`
    :