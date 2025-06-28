import logging
import os
import pathlib
from lark import Lark

from .tce_transformer import TCETransformer

class TCEParser:
    """
    The official parser for Tau Controlled English (TCE).
    This parser translates TCE sentences into canonical Tau expressions.
    """

    def __init__(self):
        """Initializes the TCEParser, loading the grammar and creating the parser instance."""
        self.logger = logging.getLogger(__name__)
        self.grammar_dir = None
        self.grammar = None
        self.parser = None
        self.transformer = None

        self._load_grammar()
        self._create_parser()
        self.transformer = TCETransformer()

    def _load_grammar(self):
        """Loads the TCE grammar file with robust pathing."""
        try:
            # Determine the project root relative to this file's location
            # backend/unified/tce_parser.py -> backend/unified -> backend -> project root
            project_root = pathlib.Path(__file__).resolve().parent.parent.parent
            
            grammar_name = "tce.lark"
            self.grammar_dir = project_root / "src/tau_translator_omega/core_engine/parsers/cnl_parser/grammars"
            grammar_path = self.grammar_dir / grammar_name

            if grammar_path.exists():
                self.logger.info(f"Loading grammar from: {grammar_path}")
                with open(grammar_path, 'r', encoding='utf-8') as f:
                    self.grammar = f.read()
            else:
                self.logger.error(f"Could not find grammar file at '{grammar_path}'.")
                raise FileNotFoundError(f"Grammar file not found: {grammar_path}")

        except Exception as e:
            self.logger.error(f"Failed to load grammar: {e}")
            raise

    def _create_parser(self):
        """Creates the Lark parser instance."""
        if not self.grammar:
            self.logger.error("Cannot create parser because grammar was not loaded.")
            return
        
        try:
            import_paths = [str(self.grammar_dir)] if self.grammar_dir else []
            self.parser = Lark(
                self.grammar, 
                start="statement", 
                parser='lalr',
                import_paths=import_paths
            )
        except Exception as e:
            self.logger.error(f"Failed to create Lark parser: {e}")
            raise

    def parse(self, text: str) -> str:
        """
        Parses a TCE sentence into a Tau expression.
        """
        if not self.parser or not self.transformer:
            self.logger.error("Parser or transformer not initialized. Cannot parse.")
            return ""
            
        try:
            # Basic preprocessing
            text = text.strip()
            if not text.endswith('.'):
                text += '.'

            # Step 1: Parse the text to get a parse tree
            tree = self.parser.parse(text)

            # Step 2: Apply the transformer to the tree
            return self.transformer.transform(tree)

        except Exception as e:
            self.logger.error(f"Parse error for text '{text}': {e}")
            # It's often useful to log the tree for debugging
            try:
                tree = self.parser.parse(text)
                self.logger.debug(f"Parse tree before transform failed: {tree.pretty()}")
            except Exception as pe:
                 self.logger.error(f"Could not even parse the text: {pe}")
            raise
