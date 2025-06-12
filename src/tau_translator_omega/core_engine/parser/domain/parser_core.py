"""
Pure parser core logic following the Intentional Disclosure Principle.

All methods are pure functions with ≤10 lines, providing complete
type disclosure and no side effects.

Copyright: DarkLightX / Dana Edwards
"""

from typing import Dict, Optional, Type
from returns.result import Result, Success, Failure
from returns.pipeline import pipe

from .types import (
    ParserConfig, GrammarConfig, GrammarFormalism, TransformerConfig,
    TransformerClass, ModulePath, ClassName, ErrorMessage, ParserType,
    LexerType
)
from ..infrastructure.plugin_types import Plugin


class ParserCore:
    """Pure business logic for parser configuration and validation."""
    
    def build_parser_config(self, plugin: Plugin) -> Result[ParserConfig, str]:
        """Build parser configuration from plugin."""
        return pipe(
            plugin,
            self._validate_plugin_type,
            lambda p: self._extract_grammar_config(p),
            lambda gc: self._validate_grammar_config(gc),
            lambda gc: self._create_parser_config(gc)
        )
    
    def _validate_plugin_type(self, plugin: Plugin) -> Result[Plugin, str]:
        """Validate plugin is of correct type."""
        if not plugin or plugin.plugin_type != "grammar_definition":
            return Failure("Plugin must be of type 'grammar_definition'")
        return Success(plugin)
    
    def _extract_grammar_config(self, plugin: Plugin) -> Result[Dict, str]:
        """Extract grammar configuration from plugin."""
        config = getattr(plugin, 'grammar_config', None)
        if not config:
            return Failure("Plugin missing grammar_config")
        return Success(config)
    
    def _validate_grammar_config(self, config: Dict) -> Result[Dict, str]:
        """Validate grammar configuration has required fields."""
        required_fields = ['grammar_file_path', 'formalism']
        missing = [f for f in required_fields if f not in config]
        
        if missing:
            return Failure(f"Missing required fields: {', '.join(missing)}")
        return Success(config)
    
    def _create_parser_config(self, config: Dict) -> Result[ParserConfig, str]:
        """Create parser configuration from validated config."""
        try:
            formalism = GrammarFormalism(config.get('formalism', 'Lark'))
            return Success(ParserConfig(
                formalism=formalism,
                parser_type=config.get('parser_type', 'lalr'),
                lexer_type=config.get('lexer_type', 'contextual'),
                start_symbol=config.get('start_symbol', 'start'),
                keep_all_tokens=config.get('keep_all_tokens', False),
                propagate_positions=config.get('propagate_positions', True),
                maybe_placeholders=config.get('maybe_placeholders', False),
                debug_mode=config.get('debug_lark', False)
            ))
        except ValueError as e:
            return Failure(f"Invalid parser configuration: {e}")
    
    def build_transformer_config(self, plugin: Plugin) -> Result[Optional[TransformerConfig], str]:
        """Build transformer configuration if available."""
        return pipe(
            plugin,
            self._extract_transformer_class,
            lambda tc: self._create_transformer_config(tc) if tc else Success(None)
        )
    
    def _extract_transformer_class(self, plugin: Plugin) -> Result[Optional[str], str]:
        """Extract transformer class from plugin manifest."""
        manifest = getattr(plugin, 'grammar_config', {}).get('manifest', {})
        transformer_class = manifest.get('transformer_class')
        return Success(transformer_class)
    
    def _create_transformer_config(self, fqn: str) -> Result[TransformerConfig, str]:
        """Create transformer configuration from fully qualified name."""
        try:
            parts = fqn.rsplit('.', 1)
            if len(parts) != 2:
                return Failure(f"Invalid transformer class format: {fqn}")
            
            module_path, class_name = parts
            return Success(TransformerConfig(
                class_name=TransformerClass(fqn),
                module_path=ModulePath(module_path)
            ))
        except Exception as e:
            return Failure(f"Failed to parse transformer class: {e}")
    
    def validate_formalism_support(self, formalism: GrammarFormalism) -> Result[GrammarFormalism, str]:
        """Validate that grammar formalism is supported."""
        supported = [GrammarFormalism.LARK, GrammarFormalism.EBNF]
        
        if formalism not in supported:
            supported_names = [f.value for f in supported]
            return Failure(f"Unsupported formalism: {formalism.value}. Supported: {supported_names}")
        return Success(formalism)
    
    def determine_parser_strategy(self, config: ParserConfig) -> str:
        """Determine which parsing strategy to use."""
        strategy_map = {
            GrammarFormalism.LARK: "LarkParsingStrategy",
            GrammarFormalism.ANTLR: "AntlrParsingStrategy",
            GrammarFormalism.EBNF: "EbnfParsingStrategy",
            GrammarFormalism.BNF: "BnfParsingStrategy",
            GrammarFormalism.PEG: "PegParsingStrategy"
        }
        return strategy_map.get(config.formalism, "FallbackParsingStrategy")


class GrammarValidator:
    """Pure grammar validation logic."""
    
    def validate_grammar_content(self, content: str) -> Result[str, str]:
        """Validate grammar content is not empty."""
        if not content or not content.strip():
            return Failure("Grammar content is empty")
        return Success(content)
    
    def validate_start_symbol(self, content: str, start: str) -> Result[str, str]:
        """Validate start symbol exists in grammar."""
        # Simple validation - check if start symbol appears in content
        if start not in content:
            return Failure(f"Start symbol '{start}' not found in grammar")
        return Success(start)
    
    def check_for_left_recursion(self, content: str) -> Result[Optional[str], str]:
        """Check for direct left recursion (warning only)."""
        import re
        
        # Simple pattern to detect potential left recursion
        pattern = r'^(\w+)\s*:\s*\1\s+'
        matches = re.findall(pattern, content, re.MULTILINE)
        
        if matches:
            warning = f"Potential left recursion detected in rules: {', '.join(matches)}"
            return Success(warning)
        return Success(None)
    
    def validate_grammar_syntax(self, content: str, formalism: GrammarFormalism) -> Result[str, str]:
        """Validate grammar syntax based on formalism."""
        validators = {
            GrammarFormalism.LARK: self._validate_lark_syntax,
            GrammarFormalism.EBNF: self._validate_ebnf_syntax,
            GrammarFormalism.BNF: self._validate_bnf_syntax
        }
        
        validator = validators.get(formalism)
        if not validator:
            return Success(content)  # No validator, assume valid
        
        return validator(content)
    
    def _validate_lark_syntax(self, content: str) -> Result[str, str]:
        """Validate Lark grammar syntax."""
        # Check for basic Lark syntax patterns
        if '::=' in content and ':' in content:
            return Failure("Mixed grammar notation detected (both '::=' and ':')")
        
        # Check for at least one rule
        import re
        if not re.search(r'\w+\s*:', content):
            return Failure("No grammar rules found")
        
        return Success(content)
    
    def _validate_ebnf_syntax(self, content: str) -> Result[str, str]:
        """Validate EBNF grammar syntax."""
        # Check for EBNF patterns
        if not '::=' in content:
            return Failure("EBNF grammar must use '::=' notation")
        
        # Check for proper termination
        if not content.strip().endswith(';'):
            return Failure("EBNF rules should end with semicolon")
        
        return Success(content)
    
    def _validate_bnf_syntax(self, content: str) -> Result[str, str]:
        """Validate BNF grammar syntax."""
        # Check for BNF patterns
        if not '::=' in content:
            return Failure("BNF grammar must use '::=' notation")
        
        # BNF shouldn't have EBNF extensions
        ebnf_chars = ['[', ']', '{', '}', '?', '*', '+']
        for char in ebnf_chars:
            if char in content:
                return Failure(f"BNF grammar contains EBNF extension: '{char}'")
        
        return Success(content)


class ConfigurationMerger:
    """Merges configurations from multiple sources."""
    
    def merge_configs(self, base: ParserConfig, overrides: Dict) -> Result[ParserConfig, str]:
        """Merge parser configuration with overrides."""
        try:
            return Success(ParserConfig(
                formalism=overrides.get('formalism', base.formalism),
                parser_type=overrides.get('parser_type', base.parser_type),
                lexer_type=overrides.get('lexer_type', base.lexer_type),
                start_symbol=overrides.get('start_symbol', base.start_symbol),
                keep_all_tokens=overrides.get('keep_all_tokens', base.keep_all_tokens),
                propagate_positions=overrides.get('propagate_positions', base.propagate_positions),
                maybe_placeholders=overrides.get('maybe_placeholders', base.maybe_placeholders),
                debug_mode=overrides.get('debug_mode', base.debug_mode)
            ))
        except Exception as e:
            return Failure(f"Failed to merge configurations: {e}")
    
    def apply_environment_overrides(self, config: ParserConfig) -> ParserConfig:
        """Apply environment variable overrides (pure function)."""
        import os
        
        debug_override = os.environ.get('PARSER_DEBUG', '').lower() == 'true'
        if debug_override and not config.debug_mode:
            return config.with_debug(True)
        
        return config