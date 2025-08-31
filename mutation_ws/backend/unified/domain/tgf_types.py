"""
TGF (Tau Grammar Format) domain types following the Intentional Disclosure Principle.

These immutable domain types replace primitive obsession and provide clear
type boundaries for TGF grammar loading operations.

Copyright: DarkLightX / Dana Edwards
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List, Dict, Any, NewType
from enum import Enum

# Domain Type Aliases
TGFFilename = NewType("TGFFilename", str)
TGFContent = NewType("TGFContent", str)
TGFRuleName = NewType("TGFRuleName", str)
TerminalSymbol = NewType("TerminalSymbol", str)
NonTerminalSymbol = NewType("NonTerminalSymbol", str)
LarkGrammar = NewType("LarkGrammar", str)
ConfigPath = NewType("ConfigPath", str)
GrammarDirectory = NewType("GrammarDirectory", str)

class GrammarFileType(Enum):
    """Supported grammar file types."""
    TGF = ".tgf"
    LARK = ".lark"
    EBNF = ".ebnf"
    ANTLR = ".g4"
    
class ElementType(Enum):
    """Types of elements in grammar rules."""
    LITERAL = "literal"
    NON_TERMINAL = "non_terminal"
    OPTIONAL = "optional"
    QUANTIFIER = "quantifier"

class QuantifierType(Enum):
    """Grammar quantifier types."""
    OPTIONAL = "?"      # Zero or one
    STAR = "*"          # Zero or more
    PLUS = "+"          # One or more

@dataclass(frozen=True)
class RuleElement:
    """Represents an element within a grammar rule."""
    element_type: ElementType
    value: str
    quantifier: Optional[QuantifierType] = None
    
    @classmethod
    def create_literal(cls, value: str, quantifier: Optional[QuantifierType] = None) -> 'RuleElement':
        """Create a literal element."""
        return cls(ElementType.LITERAL, value, quantifier)
    
    @classmethod
    def create_non_terminal(cls, value: str, quantifier: Optional[QuantifierType] = None) -> 'RuleElement':
        """Create a non-terminal element."""
        return cls(ElementType.NON_TERMINAL, value, quantifier)
    
    @classmethod
    def create_optional(cls, value: str) -> 'RuleElement':
        """Create an optional element."""
        return cls(ElementType.OPTIONAL, value)

@dataclass(frozen=True)
class GrammarRule:
    """Represents a parsed grammar rule with alternatives."""
    name: TGFRuleName
    alternatives: List[List[RuleElement]]
    
    def get_terminals(self) -> List[TerminalSymbol]:
        """Extract terminal symbols from this rule."""
        terminals = []
        for alternative in self.alternatives:
            for element in alternative:
                if element.element_type == ElementType.LITERAL:
                    terminals.append(TerminalSymbol(element.value))
        return terminals
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": str(self.name),
            "type": "rule",
            "alternatives": [
                [
                    {
                        "type": elem.element_type.value,
                        "value": elem.value,
                        "quantifier": elem.quantifier.value if elem.quantifier else None
                    }
                    for elem in alt
                ]
                for alt in self.alternatives
            ]
        }

@dataclass(frozen=True)
class ParsedTGFGrammar:
    """Complete parsed TGF grammar with all components."""
    rules: Dict[str, GrammarRule]
    terminals: List[TerminalSymbol]
    non_terminals: List[NonTerminalSymbol]
    
    @property
    def rule_count(self) -> int:
        """Number of rules in grammar."""
        return len(self.rules)
    
    @property
    def terminal_count(self) -> int:
        """Number of terminal symbols."""
        return len(self.terminals)
    
    @property
    def non_terminal_count(self) -> int:
        """Number of non-terminal symbols."""
        return len(self.non_terminals)
    
    def get_rule(self, name: str) -> Optional[GrammarRule]:
        """Get rule by name."""
        return self.rules.get(name)
    
    def to_summary_dict(self) -> Dict[str, Any]:
        """Convert to summary dictionary."""
        return {
            "rule_count": self.rule_count,
            "terminal_count": self.terminal_count,
            "non_terminal_count": self.non_terminal_count,
            "rules": list(self.rules.keys()),
            "terminals": [str(t) for t in self.terminals],
            "non_terminals": [str(nt) for nt in self.non_terminals]
        }

@dataclass(frozen=True)
class LoadedGrammar:
    """Immutable representation of a loaded grammar file."""
    filename: TGFFilename
    original_name: str
    file_type: GrammarFileType
    content: TGFContent
    is_active: bool
    parsed_grammar: Optional[ParsedTGFGrammar] = None
    
    @property
    def is_parsed(self) -> bool:
        """Check if grammar has been parsed."""
        return self.parsed_grammar is not None
    
    @property
    def supports_conversion(self) -> bool:
        """Check if grammar type supports conversion to Lark."""
        return self.file_type in [GrammarFileType.TGF, GrammarFileType.LARK]
    
    def get_display_info(self) -> Dict[str, Any]:
        """Get information for UI display."""
        info = {
            "filename": str(self.filename),
            "original_name": self.original_name,
            "type": self.file_type.value,
            "is_active": self.is_active,
            "is_parsed": self.is_parsed,
            "supports_conversion": self.supports_conversion
        }
        
        if self.parsed_grammar:
            info.update(self.parsed_grammar.to_summary_dict())
        
        return info
    
    def with_active_status(self, is_active: bool) -> 'LoadedGrammar':
        """Create new instance with updated active status."""
        return LoadedGrammar(
            filename=self.filename,
            original_name=self.original_name,
            file_type=self.file_type,
            content=self.content,
            is_active=is_active,
            parsed_grammar=self.parsed_grammar
        )
    
    def with_parsed_grammar(self, parsed_grammar: ParsedTGFGrammar) -> 'LoadedGrammar':
        """Create new instance with parsed grammar."""
        return LoadedGrammar(
            filename=self.filename,
            original_name=self.original_name,
            file_type=self.file_type,
            content=self.content,
            is_active=self.is_active,
            parsed_grammar=parsed_grammar
        )

@dataclass(frozen=True)
class GrammarConfig:
    """Configuration for a single grammar file."""
    filename: TGFFilename
    original_name: str
    file_type: str
    is_active: bool
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "filename": str(self.filename),
            "originalName": self.original_name,
            "type": self.file_type,
            "isActive": self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GrammarConfig':
        """Create from dictionary."""
        return cls(
            filename=TGFFilename(data["filename"]),
            original_name=data.get("originalName", data["filename"]),
            file_type=data.get("type", ".tgf"),
            is_active=data.get("isActive", False)
        )

@dataclass(frozen=True)
class GrammarLoaderConfig:
    """Configuration for the TGF grammar loader."""
    grammar_directory: GrammarDirectory
    config_file_path: ConfigPath
    auto_load_on_init: bool = True
    
    @classmethod
    def create_default(cls) -> 'GrammarLoaderConfig':
        """Create default configuration."""
        return cls(
            grammar_directory=GrammarDirectory("grammars"),
            config_file_path=ConfigPath("config/grammar-files.json")
        )
    
    def validate_paths(self) -> bool:
        """Validate that configured paths exist."""
        grammar_path = Path(self.grammar_directory)
        config_path = Path(self.config_file_path)
        
        return grammar_path.exists() and config_path.parent.exists()

@dataclass(frozen=True)
class LarkConversionResult:
    """Result of converting TGF grammar to Lark format."""
    success: bool
    lark_grammar: Optional[LarkGrammar] = None
    error_message: Optional[str] = None
    terminal_count: int = 0
    rule_count: int = 0
    
    @classmethod
    def success_result(cls, lark_grammar: str, terminal_count: int, rule_count: int) -> 'LarkConversionResult':
        """Create successful conversion result."""
        return cls(
            success=True,
            lark_grammar=LarkGrammar(lark_grammar),
            terminal_count=terminal_count,
            rule_count=rule_count
        )
    
    @classmethod
    def failure_result(cls, error_message: str) -> 'LarkConversionResult':
        """Create failed conversion result."""
        return cls(
            success=False,
            error_message=error_message
        )

@dataclass(frozen=True)
class GrammarLoadingState:
    """State of the grammar loading system."""
    loaded_grammars: Dict[str, LoadedGrammar]
    active_grammar: Optional[LoadedGrammar]
    total_loaded: int
    
    @property
    def has_active_grammar(self) -> bool:
        """Check if there's an active grammar."""
        return self.active_grammar is not None
    
    @property
    def active_grammar_name(self) -> Optional[str]:
        """Get name of active grammar."""
        return str(self.active_grammar.filename) if self.active_grammar else None
    
    def get_grammar_list(self) -> List[Dict[str, Any]]:
        """Get list of all loaded grammars for display."""
        return [grammar.get_display_info() for grammar in self.loaded_grammars.values()]
    
    def to_summary_dict(self) -> Dict[str, Any]:
        """Convert to summary dictionary."""
        return {
            "total_loaded": self.total_loaded,
            "has_active_grammar": self.has_active_grammar,
            "active_grammar_name": self.active_grammar_name,
            "loaded_grammar_names": list(self.loaded_grammars.keys())
        }

@dataclass(frozen=True)
class TGFParseError:
    """Structured error information for TGF parsing failures."""
    line_number: Optional[int]
    error_message: str
    context: Optional[str] = None
    rule_name: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "line_number": self.line_number,
            "error_message": self.error_message,
            "context": self.context,
            "rule_name": self.rule_name
        }