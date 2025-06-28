"""
Infrastructure layer for grammar-driven parsing.

Copyright: DarkLightX / Dana Edwards
"""

import os
import importlib
import logging
from pathlib import Path
from typing import Optional, Any, Type, Tuple
from .domain_types import (
    GrammarPath, GrammarContent, GrammarConfig, TransformerConfig,
    TransformerName, ModulePath, ClassName, ProjectRoot, ParserError,
    ASTTransformer, GrammarFormalism
)

try:
    from lark import Lark, LarkError
    LARK_AVAILABLE = True
except ImportError:
    Lark = None
    LarkError = Exception
    LARK_AVAILABLE = False


class ProjectPathResolver:
    """Resolves project-relative paths."""
    
    @staticmethod
    def resolve_project_root(current_file: str) -> ProjectRoot:
        """Resolve project root from current file path."""
        current_dir = os.path.dirname(os.path.abspath(current_file))
        # Navigate up three levels from parser module
        project_root = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
        return ProjectRoot(project_root)
    
    @staticmethod
    def resolve_grammars_directory(project_root: ProjectRoot) -> Path:
        """Get the common grammars directory."""
        return Path(project_root) / "src" / "tau_translator_omega" / "core_engine" / "grammars"


class GrammarFileLoader:
    """Loads and validates grammar files."""
    
    @staticmethod
    def load_grammar_content(grammar_path: GrammarPath) -> GrammarContent:
        """Load grammar content from file."""
        if not os.path.isfile(grammar_path):
            raise FileNotFoundError(f"Grammar file not found: {grammar_path}")
        
        try:
            with open(grammar_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            raise ParserError(f"Failed to read grammar file {grammar_path}: {e}") from e
        
        if not content.strip():
            raise ValueError(f"Grammar file is empty: {grammar_path}")
        
        return GrammarContent(content)


class LarkParserFactory:
    """Factory for creating Lark parser instances."""
    
    @staticmethod
    def create_parser(grammar_content: GrammarContent, config: GrammarConfig) -> Any:
        """Create Lark parser instance."""
        if not LARK_AVAILABLE:
            raise ParserError("Lark is not available. Please install lark-parser.")
        
        try:
            return Lark(
                grammar_content,
                parser=config.parser_type,
                lexer='contextual',
                start=config.start_symbol,
                keep_all_tokens=config.keep_all_tokens,
                propagate_positions=config.propagate_positions,
                maybe_placeholders=config.maybe_placeholders,
                debug=config.debug_lark
            )
        except LarkError as e:
            raise ParserError(f"Failed to create Lark parser: {e}") from e
        except Exception as e:
            raise ParserError(f"Unexpected error creating parser: {e}") from e


class TransformerLoader:
    """Loads transformer classes dynamically."""
    
    @staticmethod
    def load_transformer(config: TransformerConfig) -> Optional[ASTTransformer]:
        """Load transformer instance from configuration."""
        if not config.is_available:
            return None
        
        try:
            module = importlib.import_module(config.module_path)
            transformer_class = getattr(module, config.class_name)
            return transformer_class()
        except ImportError as e:
            raise ParserError(f"Failed to import transformer module {config.module_path}: {e}") from e
        except AttributeError as e:
            raise ParserError(f"Transformer class {config.class_name} not found in {config.module_path}: {e}") from e
        except Exception as e:
            raise ParserError(f"Failed to instantiate transformer {config.class_name}: {e}") from e
    
    @staticmethod
    def parse_transformer_fqn(fqn: TransformerName) -> Tuple[ModulePath, ClassName]:
        """Parse fully qualified name into module and class."""
        try:
            module_path, class_name = fqn.rsplit('.', 1)
            return ModulePath(module_path), ClassName(class_name)
        except ValueError as e:
            raise ParserError(f"Invalid transformer name format: {fqn}") from e


class GrammarValidator:
    """Validates grammar configurations."""
    
    @staticmethod
    def validate_formalism(formalism: str) -> GrammarFormalism:
        """Validate and convert formalism string."""
        try:
            return GrammarFormalism(formalism)
        except ValueError:
            if formalism == "ANTLR":
                raise ParserError(f"Unsupported grammar formalism: {formalism}")
            else:
                raise ParserError(f"Unknown grammar formalism: {formalism}")
    
    @staticmethod
    def validate_grammar_config(plugin_config: dict) -> None:
        """Validate grammar configuration completeness."""
        if not plugin_config:
            raise ParserError("Grammar configuration is missing")
        
        if not plugin_config.get('grammar_file_path'):
            raise ParserError("Grammar file path is missing from configuration")


class PluginConfigExtractor:
    """Extracts configuration from plugin objects."""
    
    @staticmethod
    def extract_grammar_config(plugin) -> GrammarConfig:
        """Extract grammar configuration from plugin."""
        config_dict = plugin.grammar_config
        GrammarValidator.validate_grammar_config(config_dict)
        
        formalism = GrammarValidator.validate_formalism(
            config_dict.get('formalism', 'Lark')
        )
        
        return GrammarConfig(
            formalism=formalism,
            file_path=GrammarPath(config_dict['grammar_file_path']),
            parser_type=config_dict.get('parser_type', 'lalr'),
            start_symbol=config_dict.get('start_symbol', 'start'),
            keep_all_tokens=config_dict.get('keep_all_tokens', False),
            propagate_positions=config_dict.get('propagate_positions', True),
            maybe_placeholders=config_dict.get('maybe_placeholders', False),
            debug_lark=config_dict.get('debug_lark', False)
        )
    
    @staticmethod
    def extract_transformer_config(plugin) -> TransformerConfig:
        """Extract transformer configuration from plugin."""
        manifest_dict = plugin.grammar_config.get('manifest', {})
        transformer_fqn = manifest_dict.get('transformer_class')
        
        if not transformer_fqn:
            return TransformerConfig(
                class_name=TransformerName(""),
                module_path=ModulePath(""),
                is_available=False
            )
        
        module_path, class_name = TransformerLoader.parse_transformer_fqn(
            TransformerName(transformer_fqn)
        )
        
        return TransformerConfig(
            class_name=TransformerName(class_name),
            module_path=module_path,
            is_available=True
        )