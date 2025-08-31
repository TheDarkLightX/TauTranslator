"""
Grammar translation domain types following the Intentional Disclosure Principle.

These immutable domain types replace primitive obsession and provide clear
type boundaries for grammar-based translation operations.

Copyright: DarkLightX / Dana Edwards
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List, Dict, Any, NewType
from enum import Enum

# Domain Type Aliases
GrammarPath = NewType("GrammarPath", str)
GrammarContent = NewType("GrammarContent", str)
GrammarName = NewType("GrammarName", str)
TransformerClassName = NewType("TransformerClassName", str)
ParsePatterns = NewType("ParsePatterns", List[str])
ParseConfidence = NewType("ParseConfidence", float)

class GrammarFormalism(Enum):
    """Supported grammar formalisms."""
    LARK = "lark"
    ANTLR = "antlr"
    
class ParserType(Enum):
    """Parser algorithm types."""
    LALR = "lalr"
    EARLEY = "earley"
    LR1 = "lr1"

class GrammarType(Enum):
    """Types of grammars in the system."""
    CNL = "cnl"          # Controlled Natural Language
    TAU = "tau"          # Tau language
    TCE = "tce"          # Tau Controlled English (default)

@dataclass(frozen=True)
class GrammarFileInfo:
    """Information about a grammar file."""
    path: GrammarPath
    exists: bool
    size_bytes: int
    last_modified: Optional[str] = None
    
    @classmethod
    def from_path(cls, path: str) -> 'GrammarFileInfo':
        """Create from file path with validation."""
        file_path = Path(path)
        
        return cls(
            path=GrammarPath(path),
            exists=file_path.exists(),
            size_bytes=file_path.stat().st_size if file_path.exists() else 0,
            last_modified=str(file_path.stat().st_mtime) if file_path.exists() else None
        )

@dataclass(frozen=True)
class ParserConfiguration:
    """Configuration for creating a grammar parser."""
    grammar_content: GrammarContent
    formalism: GrammarFormalism = GrammarFormalism.LARK
    parser_type: ParserType = ParserType.LALR
    start_rule: str = "start"
    propagate_positions: bool = True
    
    def to_lark_kwargs(self) -> Dict[str, Any]:
        """Convert to Lark parser constructor arguments."""
        return {
            "parser": self.parser_type.value,
            "start": self.start_rule,
            "propagate_positions": self.propagate_positions
        }

@dataclass(frozen=True)
class TransformerConfiguration:
    """Configuration for creating a transformer."""
    class_name: TransformerClassName
    module_path: str
    is_available: bool = True
    default_args: Dict[str, Any] = field(default_factory=dict)
    
    def create_identifier(self) -> str:
        """Create unique identifier for this transformer."""
        return f"{self.module_path}.{self.class_name}"

@dataclass(frozen=True)
class GrammarLoadResult:
    """Result of loading a grammar."""
    success: bool
    grammar_type: GrammarType
    grammar_name: GrammarName
    error_message: Optional[str] = None
    parser_created: bool = False
    transformer_created: bool = False
    
    @classmethod
    def success_result(cls, grammar_type: GrammarType, name: str) -> 'GrammarLoadResult':
        """Create successful load result."""
        return cls(
            success=True,
            grammar_type=grammar_type,
            grammar_name=GrammarName(name),
            parser_created=True,
            transformer_created=True
        )
    
    @classmethod
    def failure_result(cls, grammar_type: GrammarType, error: str) -> 'GrammarLoadResult':
        """Create failed load result."""
        return cls(
            success=False,
            grammar_type=grammar_type,
            grammar_name=GrammarName(""),
            error_message=error
        )

@dataclass(frozen=True)
class ParseTreeInfo:
    """Information extracted from a parse tree."""
    patterns: ParsePatterns
    node_count: int
    depth: int
    success: bool = True
    
    @classmethod
    def from_patterns(cls, patterns: List[str]) -> 'ParseTreeInfo':
        """Create from pattern list."""
        return cls(
            patterns=ParsePatterns(patterns[:10]),  # Limit to first 10 patterns
            node_count=len(patterns),
            depth=0,  # Would need tree traversal to calculate
            success=True
        )

@dataclass(frozen=True)
class TranslationMetadata:
    """Metadata for translation operations."""
    engine_type: str = "grammar_parser"
    parser_type: str = "lark"
    confidence: ParseConfidence = ParseConfidence(0.95)
    patterns_detected: Optional[ParseTreeInfo] = None
    parse_error_info: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "engine_type": self.engine_type,
            "parser_type": self.parser_type,
            "confidence": float(self.confidence)
        }
        
        if self.patterns_detected:
            result["patterns_detected"] = list(self.patterns_detected.patterns)
        
        if self.parse_error_info:
            result.update(self.parse_error_info)
        
        return result

@dataclass(frozen=True)
class GrammarEngineState:
    """Current state of the grammar translation engine."""
    cnl_grammar_loaded: bool
    tau_grammar_loaded: bool
    cnl_grammar_name: GrammarName
    tau_grammar_name: Optional[GrammarName]
    default_tce_available: bool
    
    @property
    def can_translate_to_tau(self) -> bool:
        """Check if engine can translate to Tau."""
        return self.cnl_grammar_loaded
    
    @property
    def can_translate_to_cnl(self) -> bool:
        """Check if engine can translate to CNL."""
        return self.cnl_grammar_loaded and self.tau_grammar_loaded
    
    def to_info_dict(self) -> Dict[str, Any]:
        """Convert to information dictionary."""
        return {
            "cnl_grammar": {
                "loaded": self.cnl_grammar_loaded,
                "name": str(self.cnl_grammar_name),
                "is_default": str(self.cnl_grammar_name) == "TCE (default)"
            },
            "tau_grammar": {
                "loaded": self.tau_grammar_loaded,
                "name": str(self.tau_grammar_name) if self.tau_grammar_name else None
            },
            "can_translate_to_tau": self.can_translate_to_tau,
            "can_translate_to_cnl": self.can_translate_to_cnl
        }

@dataclass(frozen=True)
class GrammarDirectoryConfig:
    """Configuration for grammar directory location."""
    directory_path: str
    environment_variable: str = "TAU_GRAMMAR_DIR"
    default_path: str = "./grammars"
    
    def resolve_path(self) -> str:
        """Resolve the actual grammar directory path."""
        import os
        return self.directory_path or os.environ.get(self.environment_variable, self.default_path)
    
    def validate_directory(self) -> bool:
        """Validate that directory exists and is accessible."""
        import os
        resolved_path = self.resolve_path()
        return os.path.exists(resolved_path) and os.path.isdir(resolved_path)

@dataclass(frozen=True)
class ParseError:
    """Structured parse error information."""
    message: str
    line: Optional[int] = None
    column: Optional[int] = None
    error_type: str = "parse_error"
    
    def to_metadata_dict(self) -> Dict[str, Any]:
        """Convert to metadata dictionary."""
        result = {
            "parse_error": True,
            "error_type": self.error_type,
            "message": self.message
        }
        
        if self.line is not None:
            result["error_line"] = self.line
        
        if self.column is not None:
            result["error_column"] = self.column
        
        return result
    
    @classmethod
    def from_lark_exception(cls, exception) -> 'ParseError':
        """Create from Lark parsing exception."""
        return cls(
            message=str(exception),
            line=getattr(exception, 'line', None),
            column=getattr(exception, 'column', None),
            error_type="lark_parse_error"
        )