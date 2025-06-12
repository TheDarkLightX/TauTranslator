"""
Lark parser adapter following the Intentional Disclosure Principle.

Isolates Lark-specific implementation details from domain logic.

Copyright: DarkLightX / Dana Edwards
"""

from typing import List, Optional, Any, Dict
from pathlib import Path
from returns.result import Result, Success, Failure

try:
    from lark import Lark, Tree, Token, Transformer
    from lark.exceptions import LarkError, UnexpectedInput, ParseError as LarkParseError
    LARK_AVAILABLE = True
except ImportError:
    LARK_AVAILABLE = False
    Lark = None
    Tree = None
    Token = None
    Transformer = None
    LarkError = Exception
    UnexpectedInput = Exception
    LarkParseError = Exception

from ..domain.types import (
    GrammarContent, ParserConfig, SourceCode, ParseNode,
    ParseTree, Token as DomainToken, SourceLocation, NodeType,
    ParserContext
)


class LarkParserAdapter:
    """Adapter for Lark parsing library."""
    
    def __init__(self):
        """Initialize Lark adapter."""
        if not LARK_AVAILABLE:
            raise ImportError("Lark parser library not available")
    
    def create_parser(
        self,
        grammar: GrammarContent,
        config: ParserConfig,
        import_paths: List[Path] = None
    ) -> Result[Any, str]:
        """Create Lark parser instance."""
        try:
            parser_options = self._build_parser_options(config, import_paths)
            parser = Lark(str(grammar), **parser_options)
            return Success(parser)
            
        except LarkError as e:
            return Failure(f"Lark grammar error: {e}")
        except ValueError as e:
            return Failure(f"Invalid parser configuration: {e}")
        except Exception as e:
            return Failure(f"Failed to create parser: {e}")
    
    def _build_parser_options(
        self,
        config: ParserConfig,
        import_paths: Optional[List[Path]]
    ) -> Dict[str, Any]:
        """Build Lark parser options from config."""
        options = {
            'parser': config.parser_type,
            'lexer': config.lexer_type,
            'start': config.start_symbol,
            'keep_all_tokens': config.keep_all_tokens,
            'propagate_positions': config.propagate_positions,
            'maybe_placeholders': config.maybe_placeholders,
            'debug': config.debug_mode
        }
        
        if import_paths:
            options['import_paths'] = [str(p) for p in import_paths]
        
        return options
    
    def parse_source(self, parser: Any, source: SourceCode) -> Result[Tree, str]:
        """Parse source code using Lark parser."""
        try:
            tree = parser.parse(str(source))
            return Success(tree)
            
        except UnexpectedInput as e:
            error_msg = self._format_unexpected_input_error(e)
            return Failure(error_msg)
            
        except LarkParseError as e:
            return Failure(f"Parse error: {e}")
            
        except Exception as e:
            return Failure(f"Unexpected parsing error: {e}")
    
    def _format_unexpected_input_error(self, error: UnexpectedInput) -> str:
        """Format Lark UnexpectedInput error."""
        parts = [f"Unexpected input at line {error.line}, column {error.column}"]
        
        if hasattr(error, 'expected'):
            expected = list(error.expected)[:5]  # Limit to 5 suggestions
            if expected:
                parts.append(f"Expected: {', '.join(expected)}")
        
        if hasattr(error, 'token'):
            parts.append(f"Found: {error.token}")
        
        return ". ".join(parts)
    
    def tree_to_parse_tree(self, lark_tree: Tree) -> Result[ParseTree, str]:
        """Convert Lark tree to domain parse tree."""
        try:
            root = self._convert_node(lark_tree)
            return Success(ParseTree(root=root))
        except Exception as e:
            return Failure(f"Failed to convert parse tree: {e}")
    
    def _convert_node(self, node: Any) -> ParseNode:
        """Convert Lark node to domain node."""
        if isinstance(node, Tree):
            return self._convert_tree_node(node)
        elif isinstance(node, Token):
            return self._convert_token_node(node)
        else:
            # Literal value
            return ParseNode(
                node_type=NodeType("LITERAL"),
                location=None
            )
    
    def _convert_tree_node(self, tree: Tree) -> ParseNode:
        """Convert Lark Tree to ParseNode."""
        location = self._extract_tree_location(tree)
        
        return ParseNode(
            node_type=NodeType(tree.data.upper()),
            location=location
        )
    
    def _convert_token_node(self, token: Token) -> ParseNode:
        """Convert Lark Token to ParseNode."""
        location = self._extract_token_location(token)
        
        return ParseNode(
            node_type=NodeType(token.type),
            location=location
        )
    
    def _extract_tree_location(self, tree: Tree) -> Optional[SourceLocation]:
        """Extract location from Lark tree."""
        if hasattr(tree.meta, 'line') and hasattr(tree.meta, 'column'):
            return SourceLocation(
                line=tree.meta.line,
                column=tree.meta.column,
                end_line=getattr(tree.meta, 'end_line', None),
                end_column=getattr(tree.meta, 'end_column', None)
            )
        return None
    
    def _extract_token_location(self, token: Token) -> Optional[SourceLocation]:
        """Extract location from Lark token."""
        if hasattr(token, 'line') and hasattr(token, 'column'):
            return SourceLocation(
                line=token.line,
                column=token.column,
                end_line=getattr(token, 'end_line', None),
                end_column=getattr(token, 'end_column', None)
            )
        return None
    
    def extract_tokens(self, source: SourceCode, parser: Any) -> Result[List[DomainToken], str]:
        """Extract tokens from source for recursive descent."""
        try:
            # Use Lark's lexer to tokenize
            lexer = parser.lexer
            token_stream = lexer.lex(str(source))
            
            tokens = []
            for lark_token in token_stream:
                domain_token = self._convert_to_domain_token(lark_token)
                tokens.append(domain_token)
            
            return Success(tokens)
            
        except Exception as e:
            return Failure(f"Failed to tokenize source: {e}")
    
    def _convert_to_domain_token(self, lark_token: Token) -> DomainToken:
        """Convert Lark token to domain token."""
        return DomainToken(
            type=lark_token.type,
            value=lark_token.value,
            line=getattr(lark_token, 'line', 1),
            column=getattr(lark_token, 'column', 1),
            end_line=getattr(lark_token, 'end_line', None),
            end_column=getattr(lark_token, 'end_column', None)
        )
    
    def create_parser_context(self, tokens: List[DomainToken]) -> ParserContext:
        """Create parser context from tokens."""
        return ParserContext(tokens=tokens)


class LarkTransformerAdapter:
    """Adapter for Lark transformer functionality."""
    
    def transform_tree(self, transformer: Any, tree: Tree) -> Result[Any, str]:
        """Apply Lark transformer to tree."""
        try:
            if not transformer:
                return Success(tree)
            
            result = transformer.transform(tree)
            return Success(result)
            
        except LarkError as e:
            return Failure(f"Transformation error: {e}")
        except Exception as e:
            return Failure(f"Unexpected transformation error: {e}")
    
    def validate_transformer(self, transformer: Any) -> Result[Any, str]:
        """Validate transformer is compatible."""
        if transformer and not hasattr(transformer, 'transform'):
            return Failure("Transformer must have 'transform' method")
        return Success(transformer)


class GrammarImportResolver:
    """Resolves grammar imports for Lark."""
    
    def resolve_imports(
        self,
        grammar_content: str,
        base_path: Path
    ) -> Result[List[Path], str]:
        """Extract and resolve import statements from grammar."""
        import re
        
        # Pattern to match Lark import statements
        import_pattern = r'%import\s+(\S+)(?:\s+as\s+\S+)?'
        
        imports = []
        for match in re.finditer(import_pattern, grammar_content):
            import_path = match.group(1)
            
            # Handle common imports (relative to Lark's common directory)
            if import_path.startswith('common.'):
                continue  # Lark handles these internally
            
            # Resolve relative import
            resolved = self._resolve_import_path(import_path, base_path)
            imports.append(resolved)
        
        return Success(imports)
    
    def _resolve_import_path(self, import_path: str, base_path: Path) -> Path:
        """Resolve single import path."""
        # Convert dot notation to path
        path_str = import_path.replace('.', '/')
        
        # Add .lark extension if not present
        if not path_str.endswith('.lark'):
            path_str += '.lark'
        
        # Resolve relative to base
        return base_path / path_str