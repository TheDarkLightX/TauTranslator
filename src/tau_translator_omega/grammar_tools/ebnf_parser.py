# src/tau_translator_omega/grammar_tools/ebnf_parser.py
from lark import Lark, Tree
from lark.exceptions import LarkError


class EbnfParsingError(Exception):
    """Custom exception for EBNF parsing errors."""
    pass


class EbnfParser:
    """A parser for EBNF grammar files, using the Lark library."""

    def __init__(self):
        """Initializes the Lark EBNF meta-parser."""
        try:
            # Lark has a built-in grammar for parsing EBNF.
            # We load it here to create a "meta-parser" that can parse other grammars.
            self.meta_parser = Lark.open('lark/grammars/ebnf.lark', parser='lalr', rel_to_lark_file=True)
        except FileNotFoundError as e:
            # If Lark's internal grammar file isn't found, it indicates a setup issue.
            # This is treated as a fatal configuration error.
            raise RuntimeError(
                "Could not initialize Lark EBNF meta-parser. "
                "Ensure Lark is correctly installed and its grammar files are accessible."
            ) from e

    def parse_string(self, ebnf_string: str) -> Tree:
        """
        Parses an EBNF grammar from a string.

        Args:
            ebnf_string: The string containing the EBNF grammar.

        Returns:
            A Lark.Tree representing the parsed grammar structure.

        Raises:
            EbnfParsingError: If parsing fails due to syntax errors in the grammar string.
        """
        try:
            return self.meta_parser.parse(ebnf_string)
        except LarkError as e:
            raise EbnfParsingError(f"Failed to parse EBNF string: {e}") from e

    def parse_file(self, file_path: str) -> Tree:
        """
        Parses an EBNF grammar from a file.

        Args:
            file_path: The path to the file containing the EBNF grammar.

        Returns:
            A Lark.Tree representing the parsed grammar structure.

        Raises:
            FileNotFoundError: If the specified file does not exist.
            EbnfParsingError: If parsing fails due to syntax errors in the grammar file.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                ebnf_content = f.read()
            return self.parse_string(ebnf_content)
        except FileNotFoundError:
            raise
        except EbnfParsingError as e:
            # Re-raise to include the file path in the error message
            raise EbnfParsingError(f"Failed to parse EBNF file '{file_path}': {e}") from e
