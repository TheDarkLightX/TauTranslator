import unittest
from unittest.mock import patch, MagicMock, mock_open, PropertyMock
import os
import logging
import re
from lark import Lark, Tree
from pathlib import Path
import io
import contextlib

from tau_translator_omega.core_engine.parsers.grammar_driven_parser import GrammarDrivenParser
from tau_translator_omega.core_engine.parsers.parser import ParserError
from tau_translator_omega.infrastructure.grammar_io import GrammarRepository
from tau_translator_omega.core_engine.grammar_processing import TGFGrammarService, LoadedGrammar
from returns.result import Success, Failure
from lark import Lark # For creating a mock Lark parser instance
from tau_translator_omega.core_engine.plugin import Plugin
from tau_translator_omega.core_engine.ast.ast_nodes import ASTNode, BinaryExpressionNode, LiteralNode, UnaryExpressionNode
from tau_translator_omega.core_engine.lark_transformer import SimpleMathTransformer

# Define constants for paths
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_FIXTURES_DIR = _PROJECT_ROOT / "tests" / "fixtures"
_GRAMMARS_DIR = _FIXTURES_DIR / "grammars"
_SIMPLE_MATH_LARK_GRAMMAR_PATH = str(_GRAMMARS_DIR / "simple_math.lark")
_CURRENT_FILE_DIR = Path(__file__).resolve().parent
_LOG_DIR = _CURRENT_FILE_DIR / "logs"

# Ensure log directory exists early
logging.info(f"Attempting to create log directory: {_LOG_DIR}")
try:
    os.makedirs(_LOG_DIR, exist_ok=True)
    logging.info(f"Successfully called os.makedirs for: {_LOG_DIR}")
    if _LOG_DIR.exists() and _LOG_DIR.is_dir():
        logging.info(f"Log directory {_LOG_DIR} exists and is a directory after makedirs call.")
    else:
        logging.warning(f"Log directory {_LOG_DIR} DOES NOT exist or is not a directory after makedirs call. Exists: {_LOG_DIR.exists()}, IsDir: {_LOG_DIR.is_dir() if _LOG_DIR.exists() else 'N/A'}")
except Exception as e:
    logging.error(f"Error creating log directory {_LOG_DIR}: {e}", exc_info=True)

_LOG_FILE_PATH = str(_LOG_DIR / "transformer_debug.log")

# Helper for mocking open specifically for the grammar file
@contextlib.contextmanager
def mock_open_lark_context_manager(filename, mode='r', encoding=None):
    # This function needs access to TestGrammarDrivenParser.simple_math_grammar_content
    # and TestGrammarDrivenParser.original_open. This implies it might be better as a method
    # or TestGrammarDrivenParser needs to be accessible globally here, which is not ideal.
    # For now, assuming TestGrammarDrivenParser will be defined when this is called by patch.
    # This is a common pattern, the class will be defined by the time the test method runs.
    if filename == _SIMPLE_MATH_LARK_GRAMMAR_PATH and mode == 'r':
        content = getattr(TestGrammarDrivenParser, 'simple_math_grammar_content', '')
        if not content:
            # This case might indicate an issue if setUpClass hasn't run or failed to read content
            logging.warning("mock_open_lark_context_manager: simple_math_grammar_content is empty.")
        mock_file = io.StringIO(content)
        mock_file.name = filename # Lark checks file.name for context in errors
        yield mock_file
    else:
        # Fallback to original open for other files
        original_open_func = getattr(TestGrammarDrivenParser, 'original_open', open)
        with original_open_func(filename, mode, encoding=encoding) as f:
            yield f


# Define standard mock configurations for reuse
_SM_TRANSFORMER_PATH = 'tau_translator_omega.core_engine.lark_transformer.SimpleMathTransformer'
_ACTUAL_MANIFEST_DICT = {'transformer_class': _SM_TRANSFORMER_PATH}
_ACTUAL_GRAMMAR_CONFIG_DICT = {
    'formalism': 'Lark',
    'grammar_file_path': _SIMPLE_MATH_LARK_GRAMMAR_PATH,
    'manifest': _ACTUAL_MANIFEST_DICT # Nested manifest, parser might use top-level plugin.manifest
}

_NO_TRANSFORMER_MANIFEST_DICT = {}
_NO_TRANSFORMER_GRAMMAR_CONFIG_DICT = {
    'formalism': 'Lark',
    'grammar_file_path': _SIMPLE_MATH_LARK_GRAMMAR_PATH,
    'manifest': _NO_TRANSFORMER_MANIFEST_DICT
}

_INVALID_TRANSFORMER_MANIFEST_DICT = {'transformer_class': 'non_existent_module.NonExistentClass'}
_INVALID_TRANSFORMER_GRAMMAR_CONFIG_DICT = {
    'formalism': 'Lark',
    'grammar_file_path': _SIMPLE_MATH_LARK_GRAMMAR_PATH,
    'manifest': _INVALID_TRANSFORMER_MANIFEST_DICT
}

@patch('tau_translator_omega.core_engine.parsers.grammar_driven_parser.Lark')
@patch('tau_translator_omega.core_engine.parsers.grammar_driven_parser.TGFGrammarService')
class TestGrammarDrivenParser(unittest.TestCase):

    simple_math_grammar_content: str = ""

    @classmethod
    def setUpClass(cls):
        """Set up resources once for all tests in this class."""
        logging.basicConfig(level=logging.INFO)
        try:
            with open(_SIMPLE_MATH_LARK_GRAMMAR_PATH, 'r', encoding='utf-8') as f:
                cls.simple_math_grammar_content = f.read()
            logging.debug(f"Successfully loaded grammar from {_SIMPLE_MATH_LARK_GRAMMAR_PATH}")
        except Exception as e:
            logging.error(f"Failed to read {_SIMPLE_MATH_LARK_GRAMMAR_PATH}: {e}")
            cls.simple_math_grammar_content = ""

    def test_parse_successful_with_valid_grammar(self, mock_grammar_service_class, mock_lark_class):
        # Arrange
        from tau_translator_omega.core_engine.parsers.grammar_driven_parser import ParseResult
        
        mock_grammar_service_instance = mock_grammar_service_class.return_value
        mock_lark_instance = mock_lark_class.return_value

        mock_active_grammar = LoadedGrammar(
            filename="simple_math.lark",
            original_name="simple_math",
            type=".lark",
            content=self.simple_math_grammar_content,
            is_active=True
        )
        type(mock_grammar_service_instance).active_grammar = PropertyMock(return_value=mock_active_grammar)
        mock_grammar_service_instance.load_and_parse_all_grammars.return_value = Success(None)
        mock_grammar_service_instance.get_grammar_for_parser.return_value = (self.simple_math_grammar_content, "diagnostics")

        expected_tree = Tree("start", [])
        mock_lark_instance.parse.return_value = expected_tree
        
        # Act
        parser = GrammarDrivenParser()
        result = parser.parse("1 + 2")

        # Assert
        self.assertIsInstance(result, ParseResult)
        self.assertTrue(result.success)
        self.assertEqual(result.ast, expected_tree)
        mock_lark_class.assert_called_once()
        mock_lark_instance.parse.assert_called_once_with("1 + 2")

    def test_parse_fails_when_grammar_not_set(self, mock_grammar_service_class, mock_lark_class):
        # Arrange
        from tau_translator_omega.core_engine.parsers.grammar_driven_parser import ParseResult
        
        mock_grammar_service_instance = mock_grammar_service_class.return_value
        type(mock_grammar_service_instance).active_grammar = PropertyMock(return_value=None)
        mock_grammar_service_instance.load_and_parse_all_grammars.return_value = Success(None)

        # Act
        parser = GrammarDrivenParser()
        result = parser.parse("some code")

        # Assert
        self.assertIsInstance(result, ParseResult)
        self.assertFalse(result.success)
        self.assertIn("has no active grammar set", result.error)
        mock_lark_class.assert_not_called()

    def test_parse_fails_on_lark_parsing_error(self, mock_grammar_service_class, mock_lark_class):
        # Arrange
        from tau_translator_omega.core_engine.parsers.grammar_driven_parser import ParseResult
        from lark import LarkError

        mock_grammar_service_instance = mock_grammar_service_class.return_value
        mock_lark_instance = mock_lark_class.return_value

        mock_active_grammar = LoadedGrammar(
            filename="simple_math.lark",
            original_name="simple_math",
            type=".lark",
            content=self.simple_math_grammar_content,
            is_active=True
        )
        type(mock_grammar_service_instance).active_grammar = PropertyMock(return_value=mock_active_grammar)
        mock_grammar_service_instance.load_and_parse_all_grammars.return_value = Success(None)
        mock_grammar_service_instance.get_grammar_for_parser.return_value = (self.simple_math_grammar_content, "diagnostics")
        
        lark_error = LarkError("Lark failed")
        mock_lark_instance.parse.side_effect = lark_error

        # Act
        parser = GrammarDrivenParser()
        result = parser.parse("invalid syntax")

        # Assert
        self.assertIsInstance(result, ParseResult)
        self.assertFalse(result.success)
        self.assertIn("Lark parsing error", result.error)