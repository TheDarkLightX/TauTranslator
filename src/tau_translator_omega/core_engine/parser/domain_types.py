"""
Domain types for grammar-driven parsing.

Copyright: DarkLightX / Dana Edwards
"""

from typing import NewType, Protocol, Any
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

# Domain Types (Rule 3: Maximize Disclosure via Type System)
SourceCode = NewType("SourceCode", str)
GrammarPath = NewType("GrammarPath", str)
GrammarContent = NewType("GrammarContent", str)
TransformerName = NewType("TransformerName", str)
ModulePath = NewType("ModulePath", str)
ClassName = NewType("ClassName", str)
ProjectRoot = NewType("ProjectRoot", str)


class GrammarFormalism(Enum):
    """Supported grammar formalisms."""
    LARK = "Lark"
    ANTLR = "ANTLR"


@dataclass(frozen=True)
class GrammarConfig:
    """Grammar configuration data."""
    formalism: GrammarFormalism
    file_path: GrammarPath
    parser_type: str = "lalr"
    start_symbol: str = "start"
    keep_all_tokens: bool = False
    propagate_positions: bool = True
    maybe_placeholders: bool = False
    debug_lark: bool = False


@dataclass(frozen=True)
class TransformerConfig:
    """Transformer configuration data."""
    class_name: TransformerName
    module_path: ModulePath
    is_available: bool = False


class ParseResult(Protocol):
    """Protocol for parse results."""
    def pretty(self) -> str:
        """Return pretty-printed representation."""
        ...


class ASTTransformer(Protocol):
    """Protocol for AST transformers."""
    def transform(self, cst: Any) -> Any:
        """Transform CST to AST."""
        ...


class ParserError(Exception):
    """Custom exception for parser-related errors."""
    pass