"""
Modular grammar-driven parser following the Intentional Disclosure Principle.

Copyright: DarkLightX / Dana Edwards
"""

from .domain_types import (
    SourceCode, GrammarPath, GrammarContent, TransformerName,
    GrammarFormalism, GrammarConfig, TransformerConfig,
    ParseResult, ASTTransformer, ParserError
)

from .path_resolver import (
    ProjectPathResolver, GrammarFileLoader, LarkParserFactory,
    TransformerLoader, GrammarValidator, PluginConfigExtractor
)


from .parser_factory import (
    ParserFactory, TransformerFactory, FallbackTransformer
)

from .parsing_service import (
    ParsingService, TransformationService, ErrorContextBuilder
)

__all__ = [
    # Domain types
    'SourceCode', 'GrammarPath', 'GrammarContent', 'TransformerName',
    'GrammarFormalism', 'GrammarConfig', 'TransformerConfig',
    'ParseResult', 'ASTTransformer', 'ParserError',
    
    # Infrastructure
    'ProjectPathResolver', 'GrammarFileLoader', 'LarkParserFactory',
    'TransformerLoader', 'GrammarValidator', 'PluginConfigExtractor',
    
    # Factories
    'ParserFactory', 'TransformerFactory', 'FallbackTransformer',
    
    # Services
    'ParsingService', 'TransformationService', 'ErrorContextBuilder'
]