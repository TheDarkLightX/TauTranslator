"""
Domain types and value objects for the parser following the Intentional Disclosure Principle.

These immutable domain types provide complete type disclosure and eliminate
primitive obsession throughout the parser implementation.

Copyright: DarkLightX / Dana Edwards
"""

from dataclasses import dataclass, field
from typing import NewType, Optional, List, Dict, Any, Union, Protocol, Literal
from enum import Enum
from returns.result import Result

# Domain-specific type aliases
SourceCode = NewType("SourceCode", str)
GrammarPath = NewType("GrammarPath", str)
GrammarContent = NewType("GrammarContent", str)
TransformerClass = NewType("TransformerClass", str)
ModulePath = NewType("ModulePath", str)
ClassName = NewType("ClassName", str)
TokenValue = NewType("TokenValue", str)
NodeType = NewType("NodeType", str)
ErrorMessage = NewType("ErrorMessage", str)
VariableName = NewType("VariableName", str)
FunctionName = NewType("FunctionName", str)
OperatorSymbol = NewType("OperatorSymbol", str)

# Parser type literals
ParserType = Literal["lalr", "earley", "cyk"]
LexerType = Literal["contextual", "standard", "dynamic", "dynamic_complete"]

# Grammar formalism enumeration
class GrammarFormalism(Enum):
    """Supported grammar formalisms."""
    LARK = "Lark"
    ANTLR = "ANTLR"
    EBNF = "EBNF"
    BNF = "BNF"
    PEG = "PEG"

# Token types
@dataclass(frozen=True)
class Token:
    """Immutable token representation."""
    type: str
    value: TokenValue
    line: int
    column: int
    end_line: Optional[int] = None
    end_column: Optional[int] = None

@dataclass(frozen=True)
class SourceLocation:
    """Represents a location in source code."""
    line: int
    column: int
    end_line: Optional[int] = None
    end_column: Optional[int] = None
    file_path: Optional[GrammarPath] = None
    
    def to_string(self) -> str:
        """Convert location to human-readable string."""
        if self.file_path:
            return f"{self.file_path}:{self.line}:{self.column}"
        return f"line {self.line}, column {self.column}"

# Parser configuration
@dataclass(frozen=True)
class ParserConfig:
    """Immutable parser configuration."""
    formalism: GrammarFormalism
    parser_type: ParserType
    lexer_type: LexerType
    start_symbol: str = "start"
    keep_all_tokens: bool = False
    propagate_positions: bool = True
    maybe_placeholders: bool = False
    debug_mode: bool = False
    
    def with_debug(self, enabled: bool) -> 'ParserConfig':
        """Return new config with debug mode set."""
        return ParserConfig(
            formalism=self.formalism,
            parser_type=self.parser_type,
            lexer_type=self.lexer_type,
            start_symbol=self.start_symbol,
            keep_all_tokens=self.keep_all_tokens,
            propagate_positions=self.propagate_positions,
            maybe_placeholders=self.maybe_placeholders,
            debug_mode=enabled
        )

@dataclass(frozen=True)
class GrammarConfig:
    """Grammar configuration extracted from plugin."""
    grammar_path: GrammarPath
    formalism: GrammarFormalism
    parser_config: ParserConfig
    transformer_class: Optional[TransformerClass] = None
    import_paths: List[str] = field(default_factory=list)
    
    def has_transformer(self) -> bool:
        """Check if transformer is configured."""
        return self.transformer_class is not None

@dataclass(frozen=True)
class TransformerConfig:
    """Configuration for AST transformer."""
    class_name: TransformerClass
    module_path: ModulePath
    initialization_args: Dict[str, Any] = field(default_factory=dict)

# Parse tree nodes
@dataclass(frozen=True)
class ParseNode:
    """Base class for parse tree nodes."""
    node_type: NodeType
    location: Optional[SourceLocation] = None

@dataclass(frozen=True)
class ParseTree:
    """Immutable parse tree representation."""
    root: ParseNode
    source_file: Optional[GrammarPath] = None
    
    def accept(self, visitor: 'ParseTreeVisitor') -> Result[Any, str]:
        """Accept a visitor for tree traversal."""
        return visitor.visit(self.root)

# AST node protocol
class ASTNode(Protocol):
    """Protocol for AST nodes."""
    location: Optional[SourceLocation]
    
    def accept(self, visitor: 'ASTVisitor') -> Result[Any, str]:
        """Accept a visitor for processing."""
        ...

# Parser context for lookahead
@dataclass(frozen=True)
class ParserContext:
    """Immutable parsing context with lookahead support."""
    tokens: List[Token]
    position: int = 0
    error_recovery_points: List[int] = field(default_factory=list)
    
    def peek(self, offset: int = 0) -> Optional[Token]:
        """Look ahead at token without consuming."""
        idx = self.position + offset
        return self.tokens[idx] if 0 <= idx < len(self.tokens) else None
    
    def advance(self, count: int = 1) -> 'ParserContext':
        """Return new context with advanced position."""
        new_position = min(self.position + count, len(self.tokens))
        return ParserContext(
            tokens=self.tokens,
            position=new_position,
            error_recovery_points=self.error_recovery_points
        )
    
    def at_end(self) -> bool:
        """Check if at end of tokens."""
        return self.position >= len(self.tokens)
    
    def current_token(self) -> Optional[Token]:
        """Get current token without advancing."""
        return self.peek(0)
    
    def with_recovery_point(self) -> 'ParserContext':
        """Add current position as recovery point."""
        return ParserContext(
            tokens=self.tokens,
            position=self.position,
            error_recovery_points=self.error_recovery_points + [self.position]
        )

# Error types
@dataclass(frozen=True)
class ParseError:
    """Immutable parse error representation."""
    message: ErrorMessage
    location: Optional[SourceLocation] = None
    expected_tokens: List[str] = field(default_factory=list)
    found_token: Optional[Token] = None
    recovery_hint: Optional[str] = None
    
    def to_string(self) -> str:
        """Convert error to human-readable message."""
        parts = [str(self.message)]
        
        if self.location:
            parts.append(f" at {self.location.to_string()}")
        
        if self.expected_tokens:
            parts.append(f"\nExpected: {', '.join(self.expected_tokens)}")
        
        if self.found_token:
            parts.append(f"\nFound: {self.found_token.type} '{self.found_token.value}'")
        
        if self.recovery_hint:
            parts.append(f"\nHint: {self.recovery_hint}")
        
        return "".join(parts)

# Parse result
@dataclass(frozen=True)
class ParseResult:
    """Result of parsing operation."""
    tree: Optional[ParseTree] = None
    errors: List[ParseError] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    
    def is_success(self) -> bool:
        """Check if parsing succeeded."""
        return self.tree is not None and not self.errors
    
    def add_error(self, error: ParseError) -> 'ParseResult':
        """Return new result with additional error."""
        return ParseResult(
            tree=self.tree,
            errors=self.errors + [error],
            warnings=self.warnings,
            metrics=self.metrics
        )
    
    def add_warning(self, warning: str) -> 'ParseResult':
        """Return new result with additional warning."""
        return ParseResult(
            tree=self.tree,
            errors=self.errors,
            warnings=self.warnings + [warning],
            metrics=self.metrics
        )
    
    def with_metrics(self, new_metrics: Dict[str, Any]) -> 'ParseResult':
        """Return new result with updated metrics."""
        return ParseResult(
            tree=self.tree,
            errors=self.errors,
            warnings=self.warnings,
            metrics={**self.metrics, **new_metrics}
        )

# Visitor protocols
class ParseTreeVisitor(Protocol):
    """Protocol for parse tree visitors."""
    
    def visit(self, node: ParseNode) -> Result[Any, str]:
        """Visit a parse node."""
        ...

class ASTVisitor(Protocol):
    """Protocol for AST visitors."""
    
    def visit_program(self, node: Any) -> Result[Any, str]:
        """Visit program node."""
        ...
    
    def visit_expression(self, node: Any) -> Result[Any, str]:
        """Visit expression node."""
        ...
    
    def visit_statement(self, node: Any) -> Result[Any, str]:
        """Visit statement node."""
        ...

# Recovery actions for error recovery
class RecoveryAction(Enum):
    """Actions for error recovery."""
    SYNCHRONIZE = "synchronize"
    SKIP_TOKEN = "skip_token"
    INSERT_TOKEN = "insert_token"
    SKIP_TO_DELIMITER = "skip_to_delimiter"
    RESTART_AT_STATEMENT = "restart_at_statement"

@dataclass(frozen=True)
class RecoveryResult:
    """Result of error recovery attempt."""
    action: RecoveryAction
    new_context: ParserContext
    inserted_token: Optional[Token] = None
    skipped_tokens: List[Token] = field(default_factory=list)

# Cache key for memoization
@dataclass(frozen=True)
class CacheKey:
    """Key for parser cache."""
    source_hash: str
    grammar_version: str
    parser_config_hash: str
    
    @classmethod
    def from_source(cls, source: SourceCode, config: ParserConfig, version: str) -> 'CacheKey':
        """Create cache key from source and config."""
        import hashlib
        source_hash = hashlib.sha256(source.encode()).hexdigest()
        config_str = f"{config.formalism.value}:{config.parser_type}:{config.start_symbol}"
        config_hash = hashlib.sha256(config_str.encode()).hexdigest()
        return cls(source_hash, version, config_hash)

# Performance metrics
@dataclass(frozen=True)
class ParsingMetrics:
    """Metrics collected during parsing."""
    parse_time_ms: float
    token_count: int
    node_count: int
    error_count: int
    recovery_attempts: int
    cache_hit: bool = False
    incremental: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "parse_time_ms": self.parse_time_ms,
            "token_count": self.token_count,
            "node_count": self.node_count,
            "error_count": self.error_count,
            "recovery_attempts": self.recovery_attempts,
            "cache_hit": self.cache_hit,
            "incremental": self.incremental
        }