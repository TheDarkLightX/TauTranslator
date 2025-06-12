"""
TCE Parser Infrastructure Adapter
Copyright: DarkLightX/Dana Edwards

Isolates impure I/O operations for TCE parsing.
"""

from typing import Any
from ..core.result_enhanced import Result, Success, Failure
import logging
import sys
from pathlib import Path

# Add core engine to path for parser access
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

logger = logging.getLogger(__name__)


class TCEParserAdapter:
    """Infrastructure adapter for TCE parsing operations."""
    
    def parse_tce_text_to_ast(self, tce_text: str) -> Result[Any]:
        """Parse TCE text to AST via external parser (I/O operation)."""
        try:
            # Import the external parser (file I/O)
            from src.tau_translator_omega.core_engine.cnl_parser.cnl_parser import CNLParser
            
            # Create parser instance (may load grammar files)
            parser = self._create_parser_instance()
            
            # Parse text to AST
            ast = self._invoke_parser_on_text(parser, tce_text)
            
            if ast:
                return Success(ast)
            else:
                return Failure("Parser returned empty AST")
                
        except ImportError as e:
            logger.error(f"Failed to import parser: {e}")
            return Failure(f"Parser import failed: {str(e)}")
        except Exception as e:
            logger.error(f"Parsing failed: {e}")
            return Failure(f"Parsing error: {str(e)}")
    
    def _create_parser_instance(self):
        """Create parser instance (may involve file I/O for grammar loading)."""
        from src.tau_translator_omega.core_engine.cnl_parser.cnl_parser import CNLParser
        return CNLParser()
    
    def _invoke_parser_on_text(self, parser, text: str):
        """Invoke parser on text (actual parsing operation)."""
        return parser.parse(text)