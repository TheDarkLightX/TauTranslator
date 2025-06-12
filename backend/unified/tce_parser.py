"""
TCE Parser - Main entry point
Provides all parsing capabilities from minimal to production-ready.

Copyright: DarkLightX / Dana Edwards
"""

# Import all parser versions
from backend.unified.tce_parser_v1_01 import TCEParserV101
from backend.unified.tce_parser_v1_51 import TCEParserV151
from backend.unified.tce_parser_semantic import TCEParserSemantic
from backend.unified.tce_parser_enhanced import EnhancedTCEParser, create_enhanced_tce_parser, create_production_parser

# Production-ready parser hierarchy
TCEParser = create_production_parser()  # Production-ready with all features
EnhancedParser = create_enhanced_tce_parser()  # Enhanced with configuration options

# Feature-specific parsers
SemanticParser = TCEParserSemantic  # Semantic reasoning only (CC=8)
ExtensibleParser = TCEParserV151  # User dictionary support (CC=9)
MinimalParser = TCEParserV101  # Minimal complexity baseline (CC=10)

# Aliases for backward compatibility
ProductionTCEParser = TCEParser
FullFeaturedTCEParser = EnhancedParser
BaseTCEParser = TCEParserV101

# Convenience functions
from backend.unified.tce_parser_enhanced import quick_parse, parse_with_validation, parse_and_learn