Module src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser
=========================================================================
CNL Parser - O(n) Optimized Implementation

High-performance CNL (Controlled Natural Language) parser using operator precedence
(Pratt parser) algorithm for optimal O(n) complexity.

Features:
- O(n) operator precedence parsing (optimal for CNL)
- Memory-optimized AST nodes with __slots__
- Simple and efficient tokenization
- Comprehensive error handling and validation
- Full CNL grammar support with linear complexity

Functions
---------

`create_cnl_parser(debug: bool = False) ‑> src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.CNLParser`
:   Create an O(n) CNL parser instance.
    
    Args:
        debug: Enable debug output
    
    Returns:
        CNLParser: O(n) optimized parser instance

Classes
-------

`ASTNode()`
:   Base class for all AST nodes with memory optimization.

    ### Descendants

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ConditionNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.DefinitionNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ExprNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.FactNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ParameterNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.QuantifierBlockNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.RuleNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.SentenceNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.TimeSpecNode

`ArithmeticBinaryOpNode(left: src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ArithmeticNode, operator: str, right: src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ArithmeticNode)`
:   Memory-optimized arithmetic binary operation node.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ArithmeticNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ExprNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ASTNode

    ### Instance variables

    `left: src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ArithmeticNode`
    :

    `operator: str`
    :

    `right: src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ArithmeticNode`
    :

`ArithmeticNode()`
:   Base class for arithmetic expressions.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ExprNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ASTNode

    ### Descendants

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ArithmeticBinaryOpNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ConstantNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.PredicateCallNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.VariableNode

`AtomNode()`
:   Base class for atomic expressions.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ExprNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ASTNode

    ### Descendants

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ConstantNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.StreamReferenceNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.VariableNode

`BooleanBinaryOpNode(left: src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ExprNode, operator: str, right: src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ExprNode)`
:   Memory-optimized boolean binary operation node.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ExprNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ASTNode

    ### Instance variables

    `left: src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ExprNode`
    :

    `operator: str`
    :

    `right: src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ExprNode`
    :

`CNLParser(debug: bool = False)`
:   O(n) High-Performance CNL Parser
    
    Optimized implementation using Pratt parser algorithm with:
    - O(n) operator precedence parsing (optimal for CNL)
    - Memory-optimized AST nodes with __slots__
    - Simple caching for repeated patterns
    - Comprehensive error handling and validation
    - Linear complexity for all CNL constructs

    ### Methods

    `clear_cache(self)`
    :   Clear the parsing cache.

    `get_performance_stats(self) ‑> dict`
    :   Get parser performance statistics.

    `is_available(self) ‑> bool`
    :   Check if parser is available and working.

    `parse(self, text: str, use_cache: bool = True) ‑> src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ASTNode`
    :   Parse CNL text and return AST in O(n) time.
        
        Args:
            text: CNL text to parse
            use_cache: Whether to use simple caching for repeated patterns
        
        Returns:
            ASTNode: Root of the generated AST
        
        Raises:
            ValueError: For invalid input
            RuntimeError: For parsing errors

`ComparisonNode(left: src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ArithmeticNode, operator: str, right: src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ArithmeticNode)`
:   Memory-optimized comparison node.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ExprNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ASTNode

    ### Instance variables

    `left: src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ArithmeticNode`
    :

    `operator: str`
    :

    `right: src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ArithmeticNode`
    :

`ConditionNode(expression: src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ExprNode, quantifier: ForwardRef('QuantifierBlockNode') | None = None)`
:   Memory-optimized condition node.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ASTNode

    ### Instance variables

    `expression: src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ExprNode`
    :

    `quantifier: src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.QuantifierBlockNode | None`
    :

`ConstantNode(value: Any, value_type: str)`
:   Memory-optimized constant node.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.AtomNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ArithmeticNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ExprNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ASTNode

    ### Instance variables

    `value: Any`
    :

    `value_type: str`
    :

`DefinitionNode(name: str, parameters: List[ForwardRef('ParameterNode')], body: src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ASTNode, is_function: bool, return_type: str | None = None)`
:   Memory-optimized definition node.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ASTNode

    ### Instance variables

    `body: src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ASTNode`
    :

    `is_function: bool`
    :

    `name: str`
    :

    `parameters: List[src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ParameterNode]`
    :

    `return_type: str | None`
    :

`ExprNode()`
:   Base class for expression nodes.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ASTNode

    ### Descendants

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ArithmeticNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.AtomNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.BooleanBinaryOpNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ComparisonNode

`FactNode(statement: src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ExprNode)`
:   Memory-optimized fact node.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ASTNode

    ### Instance variables

    `statement: src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ExprNode`
    :

`OptimizedTokenizer()`
:   O(n) tokenizer for CNL with optimized pattern matching.
    
    Uses compiled regex patterns and efficient scanning for linear complexity.

    ### Methods

    `tokenize(self, text: str) ‑> List[src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.Token]`
    :   Tokenize text in O(n) time.
        
        Args:
            text: Input text to tokenize
        
        Returns:
            List of tokens
        
        Raises:
            ValueError: For invalid characters

`ParameterNode(name: str, param_type: str | None = None)`
:   Memory-optimized parameter node.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ASTNode

    ### Instance variables

    `name: str`
    :

    `param_type: str | None`
    :

`PrattParser(tokens: List[src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.Token], op_precedence: Dict[str, int])`
:   O(n) Pratt parser for CNL expressions.
    
    Implements operator precedence parsing for optimal linear complexity.
    Each token is processed exactly once, ensuring O(n) performance.

    ### Methods

    `consume_token(self) ‑> src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.Token | None`
    :   Consume and return current token.

    `current_token(self) ‑> src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.Token | None`
    :   Get current token without advancing.

    `parse_atom(self) ‑> src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ExprNode`
    :   Parse atomic values.

    `parse_expression(self, min_precedence: int = 0) ‑> src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ExprNode`
    :   Parse expression with operator precedence in O(n) time.
        
        This is the core of the Pratt parser algorithm.
        Each token is processed exactly once, ensuring linear complexity.

    `parse_function_call(self) ‑> src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.PredicateCallNode`
    :   Parse function/predicate calls.

    `parse_primary(self) ‑> src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ExprNode`
    :   Parse primary expressions (atoms, parentheses, function calls).

    `peek_precedence(self) ‑> int`
    :   Get precedence of current operator.

`PredicateCallNode(name: str, args: List[src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ExprNode])`
:   Memory-optimized predicate call node.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ArithmeticNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ExprNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ASTNode

    ### Instance variables

    `args: List[src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ExprNode]`
    :

    `name: str`
    :

`QuantifierBlockNode(quant_type: str, variables: List[src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.VariableNode], condition: src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ExprNode | None)`
:   Memory-optimized quantifier block node.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ASTNode

    ### Instance variables

    `condition: src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ExprNode | None`
    :

    `quant_type: str`
    :

    `variables: List[src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.VariableNode]`
    :

`RuleNode(condition: ConditionNode, consequent: src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.PredicateCallNode)`
:   Memory-optimized rule node.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ASTNode

    ### Instance variables

    `condition: src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ConditionNode`
    :

    `consequent: src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.PredicateCallNode`
    :

`SentenceNode(content: src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.FactNode | ForwardRef('RuleNode') | ForwardRef('DefinitionNode'))`
:   Memory-optimized sentence node.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ASTNode

    ### Instance variables

    `content: src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.FactNode | src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.RuleNode | src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.DefinitionNode`
    :

`StreamReferenceNode(name: str, time_spec: ForwardRef('TimeSpecNode') | None = None, stream_type: str | None = None)`
:   Memory-optimized stream reference node.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.AtomNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ExprNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ASTNode

    ### Instance variables

    `name: str`
    :

    `stream_type: str | None`
    :

    `time_spec: src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.TimeSpecNode | None`
    :

`TimeSpecNode(base: str, operator: str | None = None, offset: int | None = None)`
:   Memory-optimized time specification node.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ASTNode

    ### Instance variables

    `base: str`
    :

    `offset: int | None`
    :

    `operator: str | None`
    :

`Token(token_type: str, value: str, position: int)`
:   Simple token class for O(n) tokenizer.

`VariableNode(name: str)`
:   Memory-optimized variable node.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.AtomNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ArithmeticNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ExprNode
    * src.tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser.ASTNode

    ### Instance variables

    `name: str`
    :