"""
Parser factory for different grammar formalisms.

Copyright: DarkLightX / Dana Edwards
"""

import logging
from typing import Any, Optional
from .domain_types import (
    GrammarConfig, TransformerConfig, ParserError,
    GrammarFormalism, ASTTransformer
)
from .infrastructure import (
    GrammarFileLoader, LarkParserFactory, TransformerLoader
)


class ParserFactory:
    """Factory for creating parser instances based on formalism."""
    
    @staticmethod
    def create_parser(grammar_config: GrammarConfig) -> Any:
        """Create parser instance based on formalism."""
        logger = logging.getLogger(__name__)
        
        if grammar_config.formalism == GrammarFormalism.LARK:
            return ParserFactory._create_lark_parser(grammar_config, logger)
        elif grammar_config.formalism == GrammarFormalism.ANTLR:
            raise ParserError(f"Unsupported formalism: {grammar_config.formalism.value}")
        else:
            raise ParserError(f"Unknown formalism: {grammar_config.formalism}")
    
    @staticmethod
    def _create_lark_parser(grammar_config: GrammarConfig, logger: logging.Logger) -> Any:
        """Create Lark parser instance."""
        logger.info(f"Creating Lark parser for grammar: {grammar_config.file_path}")
        
        # Load grammar content
        grammar_content = GrammarFileLoader.load_grammar_content(grammar_config.file_path)
        logger.info("Grammar content loaded successfully")
        
        # Create parser
        parser = LarkParserFactory.create_parser(grammar_content, grammar_config)
        logger.info("Lark parser initialized successfully")
        
        return parser


class TransformerFactory:
    """Factory for creating transformer instances."""
    
    @staticmethod
    def create_transformer(transformer_config: TransformerConfig) -> Optional[ASTTransformer]:
        """Create transformer instance if available."""
        logger = logging.getLogger(__name__)
        
        if not transformer_config.is_available:
            logger.warning("No transformer class specified in plugin manifest")
            return None
        
        logger.info(f"Loading transformer: {transformer_config.class_name}")
        
        try:
            transformer = TransformerLoader.load_transformer(transformer_config)
            logger.info(f"Successfully instantiated transformer: {transformer_config.class_name}")
            return transformer
        except ParserError:
            logger.error(f"Failed to load transformer: {transformer_config.class_name}")
            raise


class FallbackTransformer:
    """Fallback transformer when no custom transformer is available."""
    
    @staticmethod
    def create_fallback_ast(cst: Any) -> Any:
        """Create basic AST from CST when no transformer available."""
        logger = logging.getLogger(__name__)
        logger.warning("Using fallback CST-to-AST conversion")
        
        try:
            from ..ast.ast_nodes import ProgramNode, StatementNode
            
            if hasattr(cst, 'children'):
                statements = [StatementNode() for _ in cst.children]
                return ProgramNode(statements=statements)
            else:
                return ProgramNode(statements=[StatementNode()])
        except ImportError:
            logger.warning("AST nodes not available, returning CST")
            return cst