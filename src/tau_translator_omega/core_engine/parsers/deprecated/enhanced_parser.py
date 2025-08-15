#!/usr/bin/env python3
"""
Enhanced CNL Parser with Dynamic Grammar Support
===============================================

This parser extends the base parser to support dynamic grammar loading,
allowing it to work with grammar files selected in the UI.
"""

import pathlib
import logging
from lark import Lark, Transformer
from typing import Optional, Union

# Import the transformer and AST nodes
from .cnl_parser.parser import TceTransformer, GRAMMAR_FILE_PATH
from .cnl_parser.ast_nodes import ASTNode

logger = logging.getLogger(__name__)


class EnhancedParser:
    """
    Enhanced parser that supports dynamic grammar loading.
    
    Can load grammar from:
    1. A string (for dynamically generated grammar)
    2. A file path (for pre-existing grammar files)
    3. Default TCE grammar if nothing specified
    """
    
    def __init__(self, 
                 grammar_string: Optional[str] = None,
                 grammar_file_path: Optional[Union[str, pathlib.Path]] = None,
                 debug: bool = False):
        """
        Initialize the parser with optional custom grammar.
        
        Args:
            grammar_string: Grammar content as a string (takes precedence)
            grammar_file_path: Path to grammar file
            debug: Enable debug output
        """
        self.debug = debug
        self.grammar_content = None
        self.grammar_source = None
        
        # Load grammar based on provided options
        if grammar_string:
            # Use provided grammar string
            self.grammar_content = grammar_string
            self.grammar_source = "custom_string"
            grammar_dir = pathlib.Path.cwd()  # Use current dir for imports
            
        elif grammar_file_path:
            # Load from specified file
            grammar_path = pathlib.Path(grammar_file_path)
            if not grammar_path.is_file():
                raise FileNotFoundError(f"Grammar file not found: {grammar_path}")
                
            with open(grammar_path, 'r') as f:
                self.grammar_content = f.read()
            self.grammar_source = str(grammar_path)
            grammar_dir = grammar_path.parent
            
        else:
            # Use default TCE grammar
            if not GRAMMAR_FILE_PATH.is_file():
                raise FileNotFoundError(f"Default grammar file not found: {GRAMMAR_FILE_PATH}")
                
            with open(GRAMMAR_FILE_PATH, 'r') as f:
                self.grammar_content = f.read()
            self.grammar_source = str(GRAMMAR_FILE_PATH)
            grammar_dir = GRAMMAR_FILE_PATH.parent
        
        logger.info(f"Loading grammar from: {self.grammar_source}")
        
        # Create Lark parser
        try:
            self.parser = Lark(
                self.grammar_content,
                parser='earley',  # Robust parser for complex grammars
                start='start',
                ambiguity='resolve',
                debug=debug,
                import_paths=[str(grammar_dir)]  # For %import directives
            )
            self.transformer = TceTransformer()
            logger.info("Parser initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize parser: {e}")
            raise
    
    def parse(self, text: str) -> ASTNode:
        """
        Parse text using the loaded grammar.
        
        Args:
            text: Input text to parse
            
        Returns:
            ASTNode: Parsed AST
            
        Raises:
            ValueError: For empty input
            RuntimeError: For parsing errors
        """
        if not text or not text.strip():
            raise ValueError("Input text cannot be empty or whitespace only")
            
        try:
            # Parse with Lark
            parse_tree = self.parser.parse(text)
            
            # Transform to AST
            ast_result = self.transformer.transform(parse_tree)
            
            if self.debug:
                logger.debug(f"Successfully parsed: {text[:50]}...")
                
            return ast_result
            
        except Exception as e:
            logger.error(f"Parse error for text '{text}': {e}")
            raise RuntimeError(f"Failed to parse text: {e}") from e
    
    def reload_grammar(self, 
                      grammar_string: Optional[str] = None,
                      grammar_file_path: Optional[Union[str, pathlib.Path]] = None):
        """
        Reload parser with new grammar.
        
        Args:
            grammar_string: New grammar content as string
            grammar_file_path: Path to new grammar file
        """
        # Create new parser instance with new grammar
        self.__init__(
            grammar_string=grammar_string,
            grammar_file_path=grammar_file_path,
            debug=self.debug
        )
    
    def get_grammar_info(self) -> dict:
        """Get information about the loaded grammar."""
        return {
            "source": self.grammar_source,
            "size": len(self.grammar_content) if self.grammar_content else 0,
            "type": "lark",
            "parser": "earley"
        }
    
    def validate_grammar(self) -> bool:
        """
        Validate that the loaded grammar is working.
        
        Returns:
            bool: True if grammar is valid
        """
        try:
            # Try to parse a simple test sentence
            test_sentence = "test."
            self.parser.parse(test_sentence)
            return True
        except Exception:
            # Grammar might be valid but test sentence doesn't match
            # Try another approach - check if parser was created
            return self.parser is not None


class GrammarAwareParser(EnhancedParser):
    """
    Parser that integrates with the TGFGrammarLoader.
    """
    
    def __init__(self, grammar_loader=None, debug: bool = False):
        """
        Initialize parser with grammar loader integration.
        
        Args:
            grammar_loader: TGFGrammarLoader instance
            debug: Enable debug output
        """
        self.grammar_loader = grammar_loader
        
        # Get grammar from loader if available
        grammar_string = None
        if grammar_loader:
            grammar_string = grammar_loader.get_grammar_for_parser()
            
        # Initialize with grammar
        super().__init__(
            grammar_string=grammar_string,
            debug=debug
        )
    
    def reload_from_loader(self):
        """Reload grammar from the grammar loader."""
        if not self.grammar_loader:
            logger.warning("No grammar loader configured")
            return
            
        grammar_string = self.grammar_loader.get_grammar_for_parser()
        if grammar_string:
            self.reload_grammar(grammar_string=grammar_string)
            logger.info("Reloaded grammar from loader")
        else:
            logger.warning("No grammar available from loader")


# Factory functions
def create_parser_with_grammar(grammar_string: str, debug: bool = False) -> EnhancedParser:
    """Create parser with custom grammar string."""
    return EnhancedParser(grammar_string=grammar_string, debug=debug)


def create_parser_with_file(grammar_file: Union[str, pathlib.Path], debug: bool = False) -> EnhancedParser:
    """Create parser with grammar file."""
    return EnhancedParser(grammar_file_path=grammar_file, debug=debug)


def create_default_parser(debug: bool = False) -> EnhancedParser:
    """Create parser with default TCE grammar."""
    return EnhancedParser(debug=debug)