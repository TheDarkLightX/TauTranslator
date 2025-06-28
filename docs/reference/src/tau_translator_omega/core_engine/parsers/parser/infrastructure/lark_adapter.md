Module src.tau_translator_omega.core_engine.parsers.parser.infrastructure.lark_adapter
======================================================================================
Lark parser adapter following the Intentional Disclosure Principle.

Isolates Lark-specific implementation details from domain logic.

Copyright: DarkLightX / Dana Edwards

Classes
-------

`GrammarImportResolver()`
:   Resolves grammar imports for Lark.

    ### Methods

    `resolve_imports(self, grammar_content: str, base_path: pathlib.Path) ‑> returns.result.Result[typing.List[pathlib.Path], str]`
    :   Extract and resolve import statements from grammar.

`LarkParserAdapter()`
:   Adapter for Lark parsing library.
    
    Initialize Lark adapter.

    ### Methods

    `create_parser(self, grammar: src.tau_translator_omega.core_engine.parsers.parser.domain.types.GrammarContent, config: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserConfig, import_paths: List[pathlib.Path] = None) ‑> returns.result.Result[typing.Any, str]`
    :   Create Lark parser instance.

    `create_parser_context(self, tokens: List[src.tau_translator_omega.core_engine.parsers.parser.domain.types.Token]) ‑> src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserContext`
    :   Create parser context from tokens.

    `extract_tokens(self, source: src.tau_translator_omega.core_engine.parsers.parser.domain.types.SourceCode, parser: Any) ‑> returns.result.Result[typing.List[src.tau_translator_omega.core_engine.parsers.parser.domain.types.Token], str]`
    :   Extract tokens from source for recursive descent.

    `parse_source(self, parser: Any, source: src.tau_translator_omega.core_engine.parsers.parser.domain.types.SourceCode) ‑> returns.result.Result[lark.tree.Tree, str]`
    :   Parse source code using Lark parser.

    `tree_to_parse_tree(self, lark_tree: lark.tree.Tree) ‑> returns.result.Result[src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParseTree, str]`
    :   Convert Lark tree to domain parse tree.

`LarkTransformerAdapter()`
:   Adapter for Lark transformer functionality.

    ### Methods

    `transform_tree(self, transformer: Any, tree: lark.tree.Tree) ‑> returns.result.Result[typing.Any, str]`
    :   Apply Lark transformer to tree.

    `validate_transformer(self, transformer: Any) ‑> returns.result.Result[typing.Any, str]`
    :   Validate transformer is compatible.