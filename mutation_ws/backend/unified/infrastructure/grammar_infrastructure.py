"""
Grammar infrastructure layer following the Intentional Disclosure Principle.

Isolates all I/O operations, file system access, and external dependencies
from business logic according to IDP Rule 4.

Copyright: DarkLightX / Dana Edwards
"""

import os
import logging
from pathlib import Path
from typing import Optional, Any, Dict
from ..core.result_enhanced import Result, Success, Failure

from ..domain.grammar_types import (
    GrammarPath, GrammarContent, GrammarFileInfo, ParserConfiguration,
    TransformerConfiguration, GrammarFormalism, ParserType, GrammarType,
    GrammarDirectoryConfig
)

logger = logging.getLogger(__name__)

class GrammarFileLoader:
    """Handles all grammar file I/O operations."""
    
    @staticmethod
    def load_grammar_content(path: GrammarPath) -> Result[GrammarContent]:
        """Load grammar content from file with error handling."""
        try:
            if not os.path.exists(path):
                return Failure(f"Grammar file not found: {path}")
            
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip():
                return Failure(f"Grammar file is empty: {path}")
            
            logger.info(f"Grammar content loaded successfully from {path}")
            return Success(GrammarContent(content))
            
        except PermissionError:
            return Failure(f"Permission denied reading grammar file: {path}")
        except UnicodeDecodeError:
            return Failure(f"Grammar file encoding error: {path}")
        except Exception as e:
            return Failure(f"Failed to load grammar file {path}: {e}")
    
    @staticmethod
    def get_file_info(path: GrammarPath) -> GrammarFileInfo:
        """Get file information with validation."""
        return GrammarFileInfo.from_path(str(path))
    
    @staticmethod
    def load_default_tce_grammar() -> Result[GrammarContent]:
        """Load the default TCE grammar from embedded location."""
        try:
            # Calculate path relative to this file
            tce_grammar_path = (Path(__file__).parent.parent.parent.parent / 
                               "src/tau_translator_omega/core_engine/cnl_parser/grammars/tce_fixed.lark")
            
            if not tce_grammar_path.exists():
                return Failure(f"Default TCE grammar not found at {tce_grammar_path}")
            
            return GrammarFileLoader.load_grammar_content(GrammarPath(str(tce_grammar_path)))
            
        except Exception as e:
            return Failure(f"Failed to load default TCE grammar: {e}")

class LarkParserFactory:
    """Factory for creating Lark parser instances."""
    
    @staticmethod
    def create_parser(config: ParserConfiguration) -> Result[Any]:
        """Create Lark parser instance from configuration."""
        try:
            from lark import Lark
            
            parser = Lark(
                str(config.grammar_content),
                **config.to_lark_kwargs()
            )
            
            logger.info(f"Lark parser created successfully with {config.parser_type.value} algorithm")
            return Success(parser)
            
        except ImportError:
            return Failure("Lark library not available")
        except Exception as e:
            return Failure(f"Failed to create Lark parser: {e}")

class TransformerFactory:
    """Factory for creating transformer instances."""
    
    @staticmethod
    def create_transformer(config: TransformerConfiguration) -> Result[Any]:
        """Create transformer instance from configuration."""
        if not config.is_available:
            return Failure(f"Transformer {config.class_name} is not available")
        
        try:
            # Dynamic import based on configuration
            module = __import__(config.module_path, fromlist=[str(config.class_name)])
            transformer_class = getattr(module, str(config.class_name))
            
            # Instantiate with default args
            transformer = transformer_class(**config.default_args)
            
            logger.info(f"Transformer created: {config.class_name}")
            return Success(transformer)
            
        except ImportError as e:
            return Failure(f"Failed to import transformer module {config.module_path}: {e}")
        except AttributeError:
            return Failure(f"Transformer class {config.class_name} not found in {config.module_path}")
        except Exception as e:
            return Failure(f"Failed to create transformer {config.class_name}: {e}")
    
    @staticmethod
    def create_default_tce_transformer() -> Result[Any]:
        """Create default TCE to Tau transformer."""
        config = TransformerConfiguration(
            class_name="TCEToTauTransformer",
            module_path="src.tau_translator_omega.core_engine.tce_tau_transformer"
        )
        return TransformerFactory.create_transformer(config)
    
    @staticmethod
    def create_default_tau_transformer() -> Result[Any]:
        """Create default Tau to TCE transformer."""
        config = TransformerConfiguration(
            class_name="TauToTCETransformer", 
            module_path="src.tau_translator_omega.core_engine.tce_tau_transformer"
        )
        return TransformerFactory.create_transformer(config)

class GrammarDirectoryResolver:
    """Resolves grammar directory locations."""
    
    def __init__(self, config: GrammarDirectoryConfig):
        self._config = config
    
    def resolve_directory_path(self) -> str:
        """Resolve the grammar directory path."""
        return self._config.resolve_path()
    
    def validate_directory_access(self) -> Result[str]:
        """Validate directory exists and is accessible."""
        resolved_path = self.resolve_directory_path()
        
        if not os.path.exists(resolved_path):
            return Failure(f"Grammar directory does not exist: {resolved_path}")
        
        if not os.path.isdir(resolved_path):
            return Failure(f"Grammar path is not a directory: {resolved_path}")
        
        if not os.access(resolved_path, os.R_OK):
            return Failure(f"Grammar directory is not readable: {resolved_path}")
        
        logger.info(f"Grammar directory validated: {resolved_path}")
        return Success(resolved_path)

class ParseTreeAnalyzer:
    """Analyzes Lark parse trees for metadata extraction."""
    
    @staticmethod
    def extract_patterns(tree: Any) -> Result[list]:
        """Extract pattern types from parse tree."""
        try:
            patterns = set()
            
            def visit_node(node):
                # Check if node has a data attribute (Tree nodes)
                if hasattr(node, 'data'):
                    patterns.add(str(node.data))
                
                # Check if node has children to traverse
                if hasattr(node, 'children'):
                    for child in node.children:
                        visit_node(child)
            
            visit_node(tree)
            return Success(list(patterns)[:10])  # Limit to first 10 patterns
            
        except Exception as e:
            return Failure(f"Failed to extract patterns from parse tree: {e}")
    
    @staticmethod
    def analyze_tree_structure(tree: Any) -> Result[Dict[str, int]]:
        """Analyze tree structure for metrics."""
        try:
            node_count = 0
            max_depth = 0
            
            def analyze_node(node, depth=0):
                nonlocal node_count, max_depth
                node_count += 1
                max_depth = max(max_depth, depth)
                
                if hasattr(node, 'children'):
                    for child in node.children:
                        analyze_node(child, depth + 1)
            
            analyze_node(tree)
            
            return Success({
                "node_count": node_count,
                "max_depth": max_depth
            })
            
        except Exception as e:
            return Failure(f"Failed to analyze tree structure: {e}")

class PathResolver:
    """Resolves various project paths."""
    
    @staticmethod
    def resolve_project_root() -> Path:
        """Resolve project root directory."""
        # Start from this file and go up to find project root
        current_path = Path(__file__).parent
        
        # Look for common project root indicators
        indicators = ['pyproject.toml', '.git', 'README.md', 'setup.py']
        
        while current_path != current_path.parent:
            if any((current_path / indicator).exists() for indicator in indicators):
                return current_path
            current_path = current_path.parent
        
        # Fallback to current directory structure
        return Path(__file__).parent.parent.parent.parent
    
    @staticmethod
    def add_project_to_path():
        """Add project root to Python path for imports."""
        import sys
        project_root = PathResolver.resolve_project_root()
        
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
            logger.debug(f"Added project root to path: {project_root}")

class ParseErrorHandler:
    """Handles parsing errors from different parser libraries."""
    
    @staticmethod
    def handle_lark_error(exception: Exception) -> Dict[str, Any]:
        """Handle Lark parsing exceptions."""
        try:
            from lark import exceptions as lark_exceptions
            
            if isinstance(exception, lark_exceptions.UnexpectedInput):
                return {
                    "parse_error": True,
                    "error_line": getattr(exception, 'line', None),
                    "error_column": getattr(exception, 'column', None),
                    "error_type": "unexpected_input",
                    "message": str(exception)
                }
            else:
                return {
                    "parse_error": True,
                    "error_type": "lark_error",
                    "message": str(exception)
                }
                
        except ImportError:
            # Lark not available
            return {
                "parse_error": True,
                "error_type": "unknown",
                "message": str(exception)
            }
    
    @staticmethod
    def create_parse_error_message(error_info: Dict[str, Any], input_text: str) -> str:
        """Create user-friendly parse error message."""
        if error_info.get("error_line") and error_info.get("error_column"):
            line_num = error_info["error_line"]
            col_num = error_info["error_column"]
            
            # Try to show the problematic line
            lines = input_text.split('\n')
            if 0 <= line_num - 1 < len(lines):
                problematic_line = lines[line_num - 1]
                pointer = ' ' * (col_num - 1) + '^'
                
                return (f"Parse error at line {line_num}, column {col_num}:\n"
                       f"{problematic_line}\n"
                       f"{pointer}\n"
                       f"{error_info.get('message', 'Unknown error')}")
        
        return f"Parse error: {error_info.get('message', 'Unknown parsing error')}"