import unittest
from unittest.mock import patch, MagicMock, mock_open, PropertyMock
import os
import logging
import re
from lark import Lark, Tree
from pathlib import Path
import io
import contextlib

from tau_translator_omega.core_engine.parser import GrammarDrivenParser, ParserError
from tau_translator_omega.core_engine.plugin import Plugin
from tau_translator_omega.core_engine.ast_nodes import ASTNode, BinaryExpressionNode, LiteralNode, UnaryExpressionNode
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

class TestGrammarDrivenParser(unittest.TestCase):
    valid_grammar_file_path = _SIMPLE_MATH_LARK_GRAMMAR_PATH 
    invalid_grammar_file_path = str(_GRAMMARS_DIR / "non_existent_grammar.lark")
    empty_grammar_file_path = str(_GRAMMARS_DIR / "empty_grammar.lark")
    malformed_grammar_file_path = str(_GRAMMARS_DIR / "malformed_grammar.lark")

    @classmethod
    def setUpClass(cls):
        # Configure logging for tests
        # Remove existing handlers
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        
        log_dir = _LOG_DIR
        # cls.debug_log_path = os.path.join(log_dir, "parser_debug.log")
        # cls.transformer_log_path = os.path.join(log_dir, "transformer_debug.log") # No longer primary focus
        logging.basicConfig(level=logging.DEBUG, filename=str(_LOG_DIR / "test_parser_debug.log"), filemode='w')
        logging.getLogger("Lark").setLevel(logging.INFO) # Reduce Lark's verbosity unless needed
        logging.debug("TestGrammarDrivenParser.setUpClass: Logging configured.")

        cls.original_open = open # Store original open

        # Force re-read of grammar content every time setUpClass is called
        # This avoids issues with stale content if the file changes and tests are re-run without full interpreter restart.
        try:
            with open(_SIMPLE_MATH_LARK_GRAMMAR_PATH, 'r', encoding='utf-8') as f:
                cls.simple_math_grammar_content = f.read()
            logging.debug(f"Successfully (re-)read {_SIMPLE_MATH_LARK_GRAMMAR_PATH} for test mocks in setUpClass.")
        except Exception as e:
            logging.error(f"Failed to read {_SIMPLE_MATH_LARK_GRAMMAR_PATH} in setUpClass: {e}")
            cls.simple_math_grammar_content = "" # Ensure it's a string to prevent downstream errors

        cls.mock_grammar_plugin = MagicMock(spec=Plugin)
        cls.mock_grammar_plugin.name = "TestLarkGrammarPlugin"
        cls.mock_grammar_plugin.plugin_type = "grammar_definition"
        type(cls.mock_grammar_plugin).manifest = PropertyMock(return_value=_ACTUAL_MANIFEST_DICT)
        type(cls.mock_grammar_plugin).grammar_config = PropertyMock(return_value=_ACTUAL_GRAMMAR_CONFIG_DICT)

        cls.mock_plugin_no_transformer = MagicMock(spec=Plugin)
        # cls.mock_plugin_no_transformer.id = "no_transformer_plugin" # ID not strictly needed for mock
        cls.mock_plugin_no_transformer.name = "NoTransformerPlugin"
        cls.mock_plugin_no_transformer.plugin_type = "grammar_definition"
        type(cls.mock_plugin_no_transformer).manifest = PropertyMock(return_value=_NO_TRANSFORMER_MANIFEST_DICT)
        type(cls.mock_plugin_no_transformer).grammar_config = PropertyMock(return_value=_NO_TRANSFORMER_GRAMMAR_CONFIG_DICT)

        cls.mock_plugin_invalid_transformer = MagicMock(spec=Plugin)
        cls.mock_plugin_invalid_transformer.name = "InvalidTransformerPlugin"
        cls.mock_plugin_invalid_transformer.plugin_type = "grammar_definition"
        type(cls.mock_plugin_invalid_transformer).manifest = PropertyMock(return_value=_INVALID_TRANSFORMER_MANIFEST_DICT)
        type(cls.mock_plugin_invalid_transformer).grammar_config = PropertyMock(return_value=_INVALID_TRANSFORMER_GRAMMAR_CONFIG_DICT)

        # For testing non-existent grammar file
        cls.non_existent_grammar_file_path = str(_GRAMMARS_DIR / "non_existent_grammar.lark")

        # For testing empty grammar file
        cls.empty_grammar_file_path = str(_GRAMMARS_DIR / "empty_grammar.lark")

        # For testing malformed grammar file
        cls.malformed_grammar_file_path = str(_GRAMMARS_DIR / "malformed_grammar.lark")

        # Content for a valid grammar (used by mocks)
        cls.grammar_content = """
start: expr
?expr: term ((PLUS | MINUS) term)*
?term: factor ((TIMES | DIVIDE) factor)*
?factor: NUMBER | LPAR expr RPAR | PLUS factor | MINUS factor
PLUS: "+"
MINUS: "-"
TIMES: "*"
DIVIDE: "/"
LPAR: "("
RPAR: ")"
%import common.NUMBER
%import common.WS
%ignore WS
"""

        cls.mock_file_open = mock_open(read_data=cls.grammar_content)

        os.makedirs(os.path.dirname(cls.empty_grammar_file_path), exist_ok=True)
        with open(cls.empty_grammar_file_path, 'w') as f:
            pass 
        os.makedirs(os.path.dirname(cls.malformed_grammar_file_path), exist_ok=True)
        with open(cls.malformed_grammar_file_path, 'w') as f:
            f.write("?start: expr\nexpr: term ADD term\nterm: FACTOR (MUL FACTOR)*\nFACTOR: NUMBER | NAME | LPAREN expr RPAREN\n%import common.NUMBER\n%import common.WS\n%ignore WS\nLPAREN: '('\nRPAREN: ')'\nMUL: '*'\nNAME: /[a-zA-Z_][a-zA-Z0-9_]*/") # Malformed: ADD not defined as token

    def setUp(self):
        self.mock_grammar_plugin.reset_mock()
        self.mock_plugin_no_transformer.reset_mock()
        self.mock_plugin_invalid_transformer.reset_mock()

    def _create_mock_file_context_manager(self, file_content):
        mock_file = MagicMock()
        mock_file.read.return_value = file_content
        mock_file.__enter__.return_value = mock_file  # __enter__ returns the file-like object
        mock_file.__exit__.return_value = None      # __exit__ typically returns None or bool
        return mock_file

    # --- Initialization Tests ---
    @patch('os.path.isfile', return_value=True)
    @patch('tau_translator_omega.core_engine.parser.open') # Standardized mock
    def test_initialization_with_valid_lark_grammar_and_plugin(self, mock_open_func, mock_isfile):
        mock_open_func.return_value.__enter__.return_value.read.return_value = self.simple_math_grammar_content
        
        # This setup should be valid and not raise an error.
        try:
            parser = GrammarDrivenParser(self.mock_grammar_plugin)
            self.assertIsNotNone(parser) # Basic check that parser was created
        except ParserError as e:
            self.fail(f"ParserError raised unexpectedly: {e}")
        except Exception as e:
            self.fail(f"An unexpected exception was raised: {e}")

    @patch('os.path.isfile', return_value=True)
    @patch('tau_translator_omega.core_engine.parser.open') # Standardized mock
    def test_initialization_lark_plugin_no_transformer_class(self, mock_open_func, mock_isfile):
        mock_open_func.return_value.__enter__.return_value.read.return_value = "start: RULE\nRULE: \"a\"\n%ignore \" \"" # Minimal valid grammar
        # Grammar is valid, start symbol 'start' is present. No transformer to load. Should succeed.
        try:
            parser = GrammarDrivenParser(self.mock_plugin_no_transformer)
            self.assertIsNotNone(parser)
        except ParserError as e:
            self.fail(f"ParserError raised unexpectedly: {e}")
        except Exception as e:
            self.fail(f"An unexpected exception was raised: {e}")

    @patch('os.path.isfile', return_value=True)
    @patch('tau_translator_omega.core_engine.parser.open') # Standardized mock
    def test_initialization_lark_plugin_invalid_transformer_class(self, mock_open_func, mock_isfile):
        mock_open_func.return_value.__enter__.return_value.read.return_value = "start: RULE\nRULE: \"a\"\n%ignore \" \"" # Minimal valid grammar
        # Grammar is valid. Transformer loading should fail.
        expected_error_regex = r"An unexpected error occurred during parser initialization: Failed to import or instantiate transformer class 'non_existent_module.NonExistentClass': No module named 'non_existent_module'"
        with self.assertRaisesRegex(ParserError, expected_error_regex):
            GrammarDrivenParser(self.mock_plugin_invalid_transformer)

    @patch('os.path.isfile', return_value=False) # File does not exist
    def test_initialization_with_non_existent_grammar_file(self, mock_isfile):
        mock_plugin_bad_path = MagicMock(spec=Plugin)
        mock_plugin_bad_path.id = "bad_path_plugin"
        mock_plugin_bad_path.plugin_type = "grammar_definition"
        mock_plugin_bad_path.grammar_config = {'grammar_file_path': self.non_existent_grammar_file_path, 'formalism': 'Lark'}

        # Updated regex to match the FileNotFoundError message from parser.py
        with self.assertRaisesRegex(ParserError, rf"Grammar file processing error: Grammar file not found: {re.escape(self.non_existent_grammar_file_path)}"):
            GrammarDrivenParser(mock_plugin_bad_path)

    @patch('os.path.isfile', return_value=True)
    @patch('tau_translator_omega.core_engine.parser.open') # Standardized mock
    def test_initialization_with_empty_grammar_file(self, mock_open_func, mock_isfile):
        mock_open_func.return_value.__enter__.return_value.read.return_value = "" # Empty content
        mock_plugin_empty_grammar = MagicMock(spec=Plugin)
        mock_plugin_empty_grammar.id = "empty_grammar_plugin"
        mock_plugin_empty_grammar.plugin_type = "grammar_definition"
        mock_plugin_empty_grammar.grammar_config = {'grammar_file_path': self.empty_grammar_file_path, 'formalism': 'Lark'}

        # Updated regex to match the ValueError for empty grammar file from parser.py
        with self.assertRaisesRegex(ParserError, rf"Parser initialization error due to ValueError: Lark grammar file is empty: {re.escape(self.empty_grammar_file_path)}"):
            GrammarDrivenParser(mock_plugin_empty_grammar)

    @patch('os.path.isfile', return_value=True)
    @patch('tau_translator_omega.core_engine.parser.open') # Standardized mock
    def test_initialization_with_malformed_grammar_file(self, mock_open_func, mock_isfile):
        malformed_grammar_content = "?start: expr\nexpr: term ADD term\nterm: FACTOR (MUL FACTOR)*\nFACTOR: NUMBER | NAME | LPAREN expr RPAREN\n%import common.NUMBER\n%import common.WS\n%ignore WS\nLPAREN: '('\nRPAREN: ')'\nMUL: '*'\nNAME: /[a-zA-Z_][a-zA-Z0-9_]*/"
        mock_open_func.return_value.__enter__.return_value.read.return_value = malformed_grammar_content
        mock_plugin_malformed_grammar = MagicMock(spec=Plugin)
        mock_plugin_malformed_grammar.id = "malformed_grammar_plugin"
        mock_plugin_malformed_grammar.plugin_type = "grammar_definition"
        mock_plugin_malformed_grammar.grammar_config = {
            'formalism': 'Lark',
            'grammar_file_path': self.malformed_grammar_file_path,
            'manifest': {}
        }
        type(mock_plugin_malformed_grammar).manifest = PropertyMock(return_value={})

        # Expecting Lark's own GrammarError for the malformed content, wrapped in ParserError
        expected_error_regex = r"(?s)An unexpected error occurred during parser initialization: Error processing Lark grammar file: .*?malformed_grammar.lark. Lark error details: Unexpected input at line 8 column 9 in <string>:\s*LPAREN: '\('"
        with self.assertRaisesRegex(ParserError, expected_error_regex):
            GrammarDrivenParser(mock_plugin_malformed_grammar)

    # --- Test with ANTLR (should raise NotImplementedError) ---
    def test_initialization_antlr_plugin_not_implemented(self):
        mock_antlr_plugin = MagicMock(spec=Plugin)
        mock_antlr_plugin.id = "antlr_plugin"
        mock_antlr_plugin.plugin_type = "grammar_definition"
        mock_antlr_plugin.grammar_config = {
            'formalism': 'ANTLR',
            'grammar_file_path': 'dummy.g4',
            'manifest': {}
        }
        type(mock_antlr_plugin).manifest = PropertyMock(return_value={})

        # Updated regex to match the wrapped ValueError from parser.py
        with self.assertRaisesRegex(ParserError, r"Parser initialization error due to ValueError: Unsupported grammar formalism: ANTLR"):
            GrammarDrivenParser(mock_antlr_plugin)

    # --- Parsing Tests (Lark formalism) ---
    @patch('tau_translator_omega.core_engine.parser.open') # Target specific open
    def test_parse_with_lark_plugin_returns_ast(self, mock_open_func):
        mock_open_func.return_value.__enter__.return_value.read.return_value = self.simple_math_grammar_content
        parser = GrammarDrivenParser(self.mock_grammar_plugin)
        source_code = "1 + 2"
        ast = parser.parse(source_code)
        self.assertIsInstance(ast, ASTNode)
        self.assertIsInstance(ast, BinaryExpressionNode)
        self.assertEqual(ast.operator, '+')
        self.assertIsInstance(ast.left, LiteralNode)
        self.assertEqual(ast.left.value, 1) # Expecting number, not string
        self.assertIsInstance(ast.right, LiteralNode)
        self.assertEqual(ast.right.value, 2) # Expecting number

    @patch('tau_translator_omega.core_engine.parser.open') # Target specific open
    def test_parse_with_lark_more_complex_expression(self, mock_open_func):
        mock_open_func.return_value.__enter__.return_value.read.return_value = self.grammar_content
        parser = GrammarDrivenParser(self.mock_grammar_plugin)
        source_code = "(1 + 2) * 3 - 4 / 2" 
        ast = parser.parse(source_code)
        self.assertIsInstance(ast, BinaryExpressionNode)
        self.assertEqual(ast.operator, '-')
        self.assertIsInstance(ast.left, BinaryExpressionNode)
        self.assertEqual(ast.left.operator, '*')
        self.assertIsInstance(ast.left.left, BinaryExpressionNode)
        self.assertEqual(ast.left.left.operator, '+')
        self.assertIsInstance(ast.left.left.left, LiteralNode)
        self.assertEqual(ast.left.left.left.value, 1)
        self.assertIsInstance(ast.left.left.right, LiteralNode)
        self.assertEqual(ast.left.left.right.value, 2)
        self.assertIsInstance(ast.left.right, LiteralNode)
        self.assertEqual(ast.left.right.value, 3)
        self.assertIsInstance(ast.right, BinaryExpressionNode)
        self.assertEqual(ast.right.operator, '/')
        self.assertIsInstance(ast.right.left, LiteralNode)
        self.assertEqual(ast.right.left.value, 4)
        self.assertIsInstance(ast.right.right, LiteralNode)
        self.assertEqual(ast.right.right.value, 2)

    @patch('tau_translator_omega.core_engine.parser.open') # Target specific open
    def test_parse_with_lark_plugin_no_transformer(self, mock_open_func):
        mock_open_func.return_value.__enter__.return_value.read.return_value = self.grammar_content
        parser = GrammarDrivenParser(self.mock_plugin_no_transformer)
        source_code = "1 + 2"
        result = parser.parse(source_code)
        self.assertIsInstance(result, Tree) # Expecting a raw Lark Tree

    @patch('tau_translator_omega.core_engine.parser.open') # Target specific open
    def test_parse_with_lark_invalid_syntax(self, mock_open_func):
        mock_open_func.return_value.__enter__.return_value.read.return_value = self.grammar_content
        parser = GrammarDrivenParser(self.mock_grammar_plugin)
        source_code = "1 +/ 2"
        # Simplified regex: focus on the unexpected token, line/col, and the specific previous token.
        # Corrected to match Token('TYPE', 'value') format without extra escapes for quotes inside Token repr.
        expected_regex = (
            r"(?s)Lark parsing error: Unexpected token Token\('DIVIDE', '/'\) at line \d+, column \d+\..*?"
            r"Previous tokens: \s*\[Token\('PLUS', '\+'\)\]"
        )
        with self.assertRaisesRegex(ParserError, expected_regex):
            parser.parse(source_code)

    @patch('tau_translator_omega.core_engine.parser.Lark')
    @patch('importlib.import_module') # CORRECTED PATCH TARGET
    @patch('builtins.open', new=mock_open_lark_context_manager) # CHANGED TO 'new'
    def test_parse_unary_minus(self, mock_import_module, mock_lark_parser):
        # mock_open_lark is no longer passed as an argument due to `new=...` behavior.
        # The mock_open_lark_context_manager directly replaces builtins.open.

        # Setup mock for Lark parser instance and its parse method
        # The mock_lark_parser argument corresponds to @patch('...parser.Lark')
        # The mock_import_module argument corresponds to @patch('importlib.import_module')
        
        # Original logic from before simplification:
        mock_lark_parser.return_value.parse.return_value = self._create_mock_file_context_manager("1").read.return_value # Simple CST
        mock_transformer_instance = SimpleMathTransformer()
        # Configure the mock_import_module to return our mock transformer when 'SimpleMathTransformer' is accessed
        mock_import_module.return_value.SimpleMathTransformer = MagicMock(return_value=mock_transformer_instance)

        logging.debug(f"TEST_DEBUG: Before parser init: self.mock_grammar_plugin.manifest is {self.mock_grammar_plugin.manifest} (type: {type(self.mock_grammar_plugin.manifest)})" )
        logging.debug(f"TEST_DEBUG: Before parser init: self.mock_grammar_plugin.grammar_config is {self.mock_grammar_plugin.grammar_config} (type: {type(self.mock_grammar_plugin.grammar_config)})" )

        parser = GrammarDrivenParser(self.mock_grammar_plugin)
        tree = parser.parse("-5") # Source code to parse
        # At this point, parser.transform(tree) would be called if we were testing that far.
        # For now, let's assume the original test's intent was to check up to here or a bit further.
        # The original test had assertions on the transformed AST.
        ast = parser.transform(tree)
        self.assertIsInstance(ast, UnaryExpressionNode)
        self.assertEqual(ast.operator, '-')
        self.assertIsInstance(ast.operand, LiteralNode)
        self.assertEqual(ast.operand.value, 5)

    @patch('tau_translator_omega.core_engine.parser.open') # Target specific open
    def test_parse_unary_plus(self, mock_open_func):
        mock_open_func.return_value.__enter__.return_value.read.return_value = self.grammar_content
        parser = GrammarDrivenParser(self.mock_grammar_plugin)
        source_code = "+3"
        ast = parser.parse(source_code)
        # SimpleMathTransformer optimizes +NUMBER to NUMBER (LiteralNode directly)
        self.assertIsInstance(ast, LiteralNode) 
        self.assertEqual(ast.value, 3)

    @patch('tau_translator_omega.core_engine.parser.open') # Target specific open
    def test_parse_left_associativity_plus_minus(self, mock_open_func):
        mock_open_func.return_value.__enter__.return_value.read.return_value = self.grammar_content
        parser = GrammarDrivenParser(self.mock_grammar_plugin)
        source_code = "10 - 4 + 2" # (10-4)+2 = 8
        ast = parser.parse(source_code)
        self.assertIsInstance(ast, BinaryExpressionNode)
        self.assertEqual(ast.operator, '+')
        self.assertIsInstance(ast.right, LiteralNode)
        self.assertEqual(ast.right.value, 2)
        left_subtree = ast.left
        self.assertIsInstance(left_subtree, BinaryExpressionNode)
        self.assertEqual(left_subtree.operator, '-')
        self.assertIsInstance(left_subtree.left, LiteralNode)
        self.assertEqual(left_subtree.left.value, 10)
        self.assertIsInstance(left_subtree.right, LiteralNode)
        self.assertEqual(left_subtree.right.value, 4)

    @patch('tau_translator_omega.core_engine.parser.open') # Target specific open
    def test_parse_left_associativity_mul_div(self, mock_open_func):
        mock_open_func.return_value.__enter__.return_value.read.return_value = self.grammar_content
        parser = GrammarDrivenParser(self.mock_grammar_plugin)
        source_code = "10 / 2 * 5" # (10/2)*5 = 25
        ast = parser.parse(source_code)
        self.assertIsInstance(ast, BinaryExpressionNode)
        self.assertEqual(ast.operator, '*')
        self.assertIsInstance(ast.right, LiteralNode)
        self.assertEqual(ast.right.value, 5)
        left_subtree = ast.left
        self.assertIsInstance(left_subtree, BinaryExpressionNode)
        self.assertEqual(left_subtree.operator, '/')
        self.assertIsInstance(left_subtree.left, LiteralNode)
        self.assertEqual(left_subtree.left.value, 10)
        self.assertIsInstance(left_subtree.right, LiteralNode)
        self.assertEqual(left_subtree.right.value, 2)

    @patch('tau_translator_omega.core_engine.parser.open') # Target specific open
    def test_parse_parentheses_around_number(self, mock_open_func):
        mock_open_func.return_value.__enter__.return_value.read.return_value = self.grammar_content
        parser = GrammarDrivenParser(self.mock_grammar_plugin)
        source_code = "(5)"
        ast = parser.parse(source_code)
        self.assertIsInstance(ast, LiteralNode)
        self.assertEqual(ast.value, 5)

    @patch('tau_translator_omega.core_engine.parser.open') # Target specific open
    def test_parse_mixed_precedence_no_parens(self, mock_open_func):
        mock_open_func.return_value.__enter__.return_value.read.return_value = self.grammar_content
        parser = GrammarDrivenParser(self.mock_grammar_plugin)
        source_code = "1 + 2 * 3 - 4 / 2"  # 1 + (2*3) - (4/2) = 1 + 6 - 2 = 5
        ast = parser.parse(source_code)
        self.assertIsInstance(ast, BinaryExpressionNode) 
        self.assertEqual(ast.operator, '-') 
        right_minus = ast.right
        self.assertIsInstance(right_minus, BinaryExpressionNode)
        self.assertEqual(right_minus.operator, '/')
        self.assertIsInstance(right_minus.left, LiteralNode)
        self.assertEqual(right_minus.left.value, 4)
        self.assertIsInstance(right_minus.right, LiteralNode)
        self.assertEqual(right_minus.right.value, 2)
        left_minus = ast.left
        self.assertIsInstance(left_minus, BinaryExpressionNode)
        self.assertEqual(left_minus.operator, '+')
        self.assertIsInstance(left_minus.left, LiteralNode)
        self.assertEqual(left_minus.left.value, 1)
        right_plus = left_minus.right
        self.assertIsInstance(right_plus, BinaryExpressionNode)
        self.assertEqual(right_plus.operator, '*')
        self.assertIsInstance(right_plus.left, LiteralNode)
        self.assertEqual(right_plus.left.value, 2)
        self.assertIsInstance(right_plus.right, LiteralNode)
        self.assertEqual(right_plus.right.value, 3)

    @patch('tau_translator_omega.core_engine.parser.open') # Target specific open
    def test_parse_nested_parentheses(self, mock_open_func):
        mock_open_func.return_value.__enter__.return_value.read.return_value = self.grammar_content
        parser = GrammarDrivenParser(self.mock_grammar_plugin)
        source_code = "((1 + 2) * (3 - 4)) / 5"
        ast = parser.parse(source_code)
        self.assertIsInstance(ast, BinaryExpressionNode) 
        self.assertEqual(ast.operator, '/')
        self.assertEqual(ast.right.value, 5) 
        left_div = ast.left
        self.assertIsInstance(left_div, BinaryExpressionNode)
        self.assertEqual(left_div.operator, '*') 
        left_mul = left_div.left
        self.assertIsInstance(left_mul, BinaryExpressionNode)
        self.assertEqual(left_mul.operator, '+')
        self.assertEqual(left_mul.left.value, 1)
        self.assertEqual(left_mul.right.value, 2)
        right_mul = left_div.right
        self.assertIsInstance(right_mul, BinaryExpressionNode)
        self.assertEqual(right_mul.operator, '-')
        self.assertEqual(right_mul.left.value, 3)
        self.assertEqual(right_mul.right.value, 4)

    # --- Error Handling / Edge Cases ---
    @patch('tau_translator_omega.core_engine.parser.open') # Target specific open
    def test_parse_empty_string(self, mock_open_func):
        mock_open_func.return_value.__enter__.return_value.read.return_value = self.grammar_content
        parser = GrammarDrivenParser(self.mock_grammar_plugin)
        source_code = ""
        # Regex for UnexpectedToken at end of input
        expected_regex = r"(?s)Lark parsing error: Unexpected token Token\('\$END', ''\) at line \d+, column \d+\.\s*Expected one of:.*?NUMBER"
        with self.assertRaisesRegex(ParserError, expected_regex):
            parser.parse(source_code)

    @patch('tau_translator_omega.core_engine.parser.open') # Target specific open
    def test_parse_whitespace_only_string(self, mock_open_func):
        mock_open_func.return_value.__enter__.return_value.read.return_value = self.grammar_content
        parser = GrammarDrivenParser(self.mock_grammar_plugin)
        source_code = "   \t  \n  "
        # Regex for UnexpectedToken at end of input (after consuming whitespace)
        expected_regex = r"(?s)Lark parsing error: Unexpected token Token\('\$END', ''\) at line \d+, column \d+\.\s*Expected one of:.*?NUMBER"
        with self.assertRaisesRegex(ParserError, expected_regex):
            parser.parse(source_code)

    @patch('tau_translator_omega.core_engine.parser.open') # Target specific open
    def test_parse_incomplete_expression_trailing_operator(self, mock_open_func):
        mock_open_func.return_value.__enter__.return_value.read.return_value = self.grammar_content
        parser = GrammarDrivenParser(self.mock_grammar_plugin)
        source_code = "3 +"
        # Regex for UnexpectedToken at end of input, expecting an operand
        expected_regex = r"(?s)Lark parsing error: Unexpected token Token\('\$END', ''\) at line \d+, column \d+\.\s*Expected one of:.*?NUMBER"
        with self.assertRaisesRegex(ParserError, expected_regex):
            parser.parse(source_code)

    @patch('tau_translator_omega.core_engine.parser.open') # Target specific open
    def test_parse_incomplete_expression_leading_operator(self, mock_open_func):
        mock_open_func.return_value.__enter__.return_value.read.return_value = self.grammar_content
        parser = GrammarDrivenParser(self.mock_grammar_plugin)
        source_code = "* 3"
        # Regex for UnexpectedToken at end of input, expecting an operand
        expected_regex = r"(?s)Lark parsing error: Unexpected token Token\('TIMES', '\*'\) at line \d+, column \d+\..*"
        with self.assertRaisesRegex(ParserError, expected_regex):
            parser.parse(source_code)

    @patch('tau_translator_omega.core_engine.parser.open') # Target specific open
    def test_parse_unmatched_parentheses_open(self, mock_open_func):
        mock_open_func.return_value.__enter__.return_value.read.return_value = self.grammar_content
        parser = GrammarDrivenParser(self.mock_grammar_plugin)
        source_code = "(1 + 2"
        # Regex for UnexpectedToken at end of input, expecting RPAR
        expected_regex = r"(?s)Lark parsing error: Unexpected token Token\('\$END', ''\) at line \d+, column \d+\.\s*Expected one of:.*?RPAR"
        with self.assertRaisesRegex(ParserError, expected_regex):
            parser.parse(source_code)

    # --- Test with ANTLR (should raise NotImplementedError) ---
    def test_initialization_antlr_plugin_not_implemented(self):
        mock_antlr_plugin = MagicMock(spec=Plugin)
        mock_antlr_plugin.id = "antlr_plugin"
        mock_antlr_plugin.plugin_type = "grammar_definition"
        mock_antlr_plugin.grammar_config = {
            'formalism': 'ANTLR',
            'grammar_file_path': 'dummy.g4',
            'manifest': {}
        }
        type(mock_antlr_plugin).manifest = PropertyMock(return_value={})

        # Updated regex to match the wrapped ValueError from parser.py
        with self.assertRaisesRegex(ParserError, r"Parser initialization error due to ValueError: Unsupported grammar formalism: ANTLR"):
            GrammarDrivenParser(mock_antlr_plugin)

if __name__ == '__main__':
    unittest.main()
