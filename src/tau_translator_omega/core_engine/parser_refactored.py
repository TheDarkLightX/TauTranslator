"""
Grammar-driven parser following the Intentional Disclosure Principle.

Main API that composes all parser modules into a cohesive parser.
All methods under 10 lines with single responsibility.

Copyright: DarkLightX / Dana Edwards
"""

import logging
from typing import Any, Optional
from .parser import (
    SourceCode, ParserError, GrammarConfig, TransformerConfig,
    ProjectPathResolver, PluginConfigExtractor, ParserFactory,
    TransformerFactory, ParsingService
)

try:
    from lark import Tree
except ImportError:
    Tree = object


class GrammarDrivenParser:
    """
    Parses source code using a grammar definition provided by a plugin
    and transforms the resulting CST into a project-specific AST.
    """

    def __init__(self, grammar_plugin):
        """Initialize parser with a loaded grammar plugin."""
        self._validate_plugin(grammar_plugin)
        self._logger = logging.getLogger(__name__)
        
        # Extract configurations
        self._grammar_config = self._extract_grammar_config(grammar_plugin)
        self._transformer_config = self._extract_transformer_config(grammar_plugin)
        
        # Initialize components
        self._parser_instance = self._create_parser_instance()
        self._transformer_instance = self._create_transformer_instance()
        self._parsing_service = self._create_parsing_service()
        
        self._log_initialization_success(grammar_plugin)
    
    def parse(self, source_code: str) -> Any:
        """Parse source code and return AST or CST."""
        return self._parsing_service.parse_source(SourceCode(source_code))
    
    def transform(self, cst: Tree) -> Any:
        """Transform CST to AST using loaded transformer."""
        return self._parsing_service.transform_cst(cst)
    
    def _validate_plugin(self, grammar_plugin) -> None:
        """Validate that plugin is suitable for parsing."""
        if not grammar_plugin or grammar_plugin.plugin_type != "grammar_definition":
            raise ValueError("GrammarDrivenParser requires a valid 'grammar_definition' plugin")
    
    def _extract_grammar_config(self, grammar_plugin) -> GrammarConfig:
        """Extract grammar configuration from plugin."""
        return PluginConfigExtractor.extract_grammar_config(grammar_plugin)
    
    def _extract_transformer_config(self, grammar_plugin) -> TransformerConfig:
        """Extract transformer configuration from plugin."""
        return PluginConfigExtractor.extract_transformer_config(grammar_plugin)
    
    def _create_parser_instance(self) -> Any:
        """Create parser instance based on grammar configuration."""
        try:
            return ParserFactory.create_parser(self._grammar_config)
        except Exception as e:
            raise ParserError(f"Failed to create parser: {e}") from e
    
    def _create_transformer_instance(self) -> Optional[Any]:
        """Create transformer instance if available."""
        try:
            return TransformerFactory.create_transformer(self._transformer_config)
        except ParserError:
            # Re-raise parser errors as-is
            raise
        except Exception as e:
            raise ParserError(f"Unexpected error creating transformer: {e}") from e
    
    def _create_parsing_service(self) -> ParsingService:
        """Create parsing service with parser and transformer."""
        return ParsingService(self._parser_instance, self._transformer_instance)
    
    def _log_initialization_success(self, grammar_plugin) -> None:
        """Log successful initialization."""
        project_root = ProjectPathResolver.resolve_project_root(__file__)
        self._logger.info(f"GrammarDrivenParser initialized with plugin: {grammar_plugin}")
        self._logger.info(f"Project root: {project_root}")
        self._logger.info(f"Grammar: {self._grammar_config.file_path}")
        
        if self._transformer_config.is_available:
            self._logger.info(f"Transformer: {self._transformer_config.class_name}")
        else:
            self._logger.info("No transformer available")