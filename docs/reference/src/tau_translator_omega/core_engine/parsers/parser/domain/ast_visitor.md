Module src.tau_translator_omega.core_engine.parsers.parser.domain.ast_visitor
=============================================================================
AST visitor pattern implementation following the Intentional Disclosure Principle.

Provides a flexible framework for AST traversal and transformation
with support for different visitor strategies.

Copyright: DarkLightX / Dana Edwards

Classes
-------

`ASTVisitor(*args, **kwargs)`
:   Protocol for AST visitors.

    ### Ancestors (in MRO)

    * typing.Protocol
    * typing.Generic

    ### Methods

    `visit(self, node: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ASTNode) ‑> returns.result.Result[~T, str]`
    :   Visit an AST node.

    `visit_expression(self, node: Any) ‑> returns.result.Result[~T, str]`
    :   Visit expression node.

    `visit_program(self, node: Any) ‑> returns.result.Result[~T, str]`
    :   Visit program node.

    `visit_statement(self, node: Any) ‑> returns.result.Result[~T, str]`
    :   Visit statement node.

`BaseASTVisitor()`
:   Base implementation of AST visitor with dispatch mechanism.
    Subclasses implement specific visit methods.

    ### Ancestors (in MRO)

    * abc.ABC
    * typing.Generic

    ### Descendants

    * src.tau_translator_omega.core_engine.parsers.parser.domain.ast_visitor.CompositeVisitor
    * src.tau_translator_omega.core_engine.parsers.parser.domain.ast_visitor.DepthLimitedVisitor
    * src.tau_translator_omega.core_engine.parsers.parser.domain.ast_visitor.MemoizingVisitor
    * src.tau_translator_omega.core_engine.parsers.parser.domain.ast_visitor.PatternMatchingVisitor
    * src.tau_translator_omega.core_engine.parsers.parser.domain.ast_visitor.RecursiveASTVisitor

    ### Methods

    `generic_visit(self, node: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ASTNode) ‑> returns.result.Result[~T, str]`
    :   Default visit for unhandled node types.

    `visit(self, node: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ASTNode) ‑> returns.result.Result[~T, str]`
    :   Dispatch to appropriate visit method.

    `visit_program(self, node: Any) ‑> returns.result.Result[~T, str]`
    :   Visit program node - must be implemented.

`CollectingVisitor()`
:   Visitor that collects information from nodes.
    Useful for analysis passes.
    
    Initialize collector.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.parser.domain.ast_visitor.RecursiveASTVisitor
    * src.tau_translator_omega.core_engine.parsers.parser.domain.ast_visitor.BaseASTVisitor
    * abc.ABC
    * typing.Generic

    ### Methods

    `collect(self, item: Any) ‑> None`
    :   Add item to collection.

    `get_collected(self) ‑> List[Any]`
    :   Get collected items.

    `visit_program(self, node: Any) ‑> returns.result.Result[typing.List[typing.Any], str]`
    :   Collect from program and return results.

`CompositeVisitor(visitors: Dict[str, src.tau_translator_omega.core_engine.parsers.parser.domain.ast_visitor.BaseASTVisitor])`
:   Visitor that applies multiple visitors in sequence.
    Useful for multi-pass analysis.
    
    Initialize with named visitors.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.parser.domain.ast_visitor.BaseASTVisitor
    * abc.ABC
    * typing.Generic

    ### Methods

    `visit(self, node: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ASTNode) ‑> returns.result.Result[typing.Dict[str, typing.Any], str]`
    :   Apply all visitors and collect results.

    `visit_program(self, node: Any) ‑> returns.result.Result[typing.Dict[str, typing.Any], str]`
    :   Visit program with all visitors.

`DepthLimitedVisitor(base_visitor: src.tau_translator_omega.core_engine.parsers.parser.domain.ast_visitor.BaseASTVisitor[~T], max_depth: int = 100)`
:   Visitor that limits traversal depth.
    Prevents stack overflow on deeply nested trees.
    
    Initialize with base visitor and depth limit.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.parser.domain.ast_visitor.BaseASTVisitor
    * abc.ABC
    * typing.Generic

    ### Methods

    `visit(self, node: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ASTNode) ‑> returns.result.Result[~T, str]`
    :   Visit with depth tracking.

    `visit_program(self, node: Any) ‑> returns.result.Result[~T, str]`
    :   Delegate to base visitor.

`MemoizingVisitor(base_visitor: src.tau_translator_omega.core_engine.parsers.parser.domain.ast_visitor.BaseASTVisitor[~T])`
:   Visitor that caches results for repeated nodes.
    Useful for performance optimization.
    
    Initialize with base visitor.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.parser.domain.ast_visitor.BaseASTVisitor
    * abc.ABC
    * typing.Generic

    ### Methods

    `clear_cache(self) ‑> None`
    :   Clear memoization cache.

    `visit(self, node: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ASTNode) ‑> returns.result.Result[~T, str]`
    :   Visit with memoization.

    `visit_program(self, node: Any) ‑> returns.result.Result[~T, str]`
    :   Delegate to base visitor.

`PatternMatchingVisitor()`
:   Visitor that uses pattern matching for node processing.
    Returns Maybe type for optional results.
    
    Initialize pattern matcher.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.parser.domain.ast_visitor.BaseASTVisitor
    * abc.ABC
    * typing.Generic

    ### Methods

    `register_pattern(self, node_type: str, handler: Any) ‑> None`
    :   Register pattern handler for node type.

    `visit(self, node: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ASTNode) ‑> returns.result.Result[returns.maybe.Maybe[~T], str]`
    :   Visit using pattern matching.

    `visit_program(self, node: Any) ‑> returns.result.Result[returns.maybe.Maybe[~T], str]`
    :   Visit program with pattern matching.

`PostOrderVisitor()`
:   Visitor that processes nodes in post-order.
    Process children before parent.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.parser.domain.ast_visitor.RecursiveASTVisitor
    * src.tau_translator_omega.core_engine.parsers.parser.domain.ast_visitor.BaseASTVisitor
    * abc.ABC
    * typing.Generic

    ### Methods

    `visit(self, node: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ASTNode) ‑> returns.result.Result[None, str]`
    :   Visit in post-order.

    `visit_node_post(self, node: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ASTNode) ‑> returns.result.Result[None, str]`
    :   Process node after children.

    `visit_program(self, node: Any) ‑> returns.result.Result[None, str]`
    :   Visit program in post-order.

`PreOrderVisitor()`
:   Visitor that processes nodes in pre-order.
    Process parent before children.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.parser.domain.ast_visitor.RecursiveASTVisitor
    * src.tau_translator_omega.core_engine.parsers.parser.domain.ast_visitor.BaseASTVisitor
    * abc.ABC
    * typing.Generic

    ### Methods

    `visit(self, node: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ASTNode) ‑> returns.result.Result[None, str]`
    :   Visit in pre-order.

    `visit_node_pre(self, node: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ASTNode) ‑> returns.result.Result[None, str]`
    :   Process node before children.

    `visit_program(self, node: Any) ‑> returns.result.Result[None, str]`
    :   Visit program in pre-order.

`RecursiveASTVisitor()`
:   Visitor that recursively visits all child nodes.
    Useful for transformations that need to process entire tree.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.parser.domain.ast_visitor.BaseASTVisitor
    * abc.ABC
    * typing.Generic

    ### Descendants

    * src.tau_translator_omega.core_engine.parsers.parser.domain.ast_visitor.CollectingVisitor
    * src.tau_translator_omega.core_engine.parsers.parser.domain.ast_visitor.PostOrderVisitor
    * src.tau_translator_omega.core_engine.parsers.parser.domain.ast_visitor.PreOrderVisitor
    * src.tau_translator_omega.core_engine.parsers.parser.domain.ast_visitor.TransformingVisitor
    * src.tau_translator_omega.core_engine.parsers.parser.domain.ast_visitor.ValidatingVisitor

    ### Methods

    `visit_children(self, node: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ASTNode) ‑> returns.result.Result[typing.List[~T], str]`
    :   Visit all children of a node.

`TransformingVisitor()`
:   Visitor that transforms AST nodes.
    Creates new nodes rather than modifying in place.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.parser.domain.ast_visitor.RecursiveASTVisitor
    * src.tau_translator_omega.core_engine.parsers.parser.domain.ast_visitor.BaseASTVisitor
    * abc.ABC
    * typing.Generic

    ### Methods

    `transform_node(self, node: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ASTNode, **kwargs) ‑> src.tau_translator_omega.core_engine.parsers.parser.domain.types.ASTNode`
    :   Transform a node with new attributes.

    `visit_program(self, node: Any) ‑> returns.result.Result[src.tau_translator_omega.core_engine.parsers.parser.domain.types.ASTNode, str]`
    :   Transform program node.

`ValidatingVisitor()`
:   Visitor that validates AST structure.
    Returns true if valid, false with error otherwise.
    
    Initialize validator.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.parser.domain.ast_visitor.RecursiveASTVisitor
    * src.tau_translator_omega.core_engine.parsers.parser.domain.ast_visitor.BaseASTVisitor
    * abc.ABC
    * typing.Generic

    ### Methods

    `add_error(self, error: str) ‑> None`
    :   Add validation error.

    `get_errors(self) ‑> List[str]`
    :   Get all validation errors.

    `has_errors(self) ‑> bool`
    :   Check if validation errors exist.

    `visit_program(self, node: Any) ‑> returns.result.Result[bool, str]`
    :   Validate program node.