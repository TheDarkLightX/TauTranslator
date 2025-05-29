"""Tests for TGF preprocessor #include directive functionality."""

import pytest
from pathlib import Path
from unittest.mock import patch, mock_open # Removed MagicMock as it's not directly used yet

from tau_translator_omega.core_engine.tgf_preprocessor import TGFPreprocessor
from tau_translator_omega.core_engine.preprocessor_errors import CircularIncludeError, IncludeFileNotFoundError, PreprocessorError

class TestTGFPreprocessorIncludes:
    """Tests focusing on #include directive processing."""

    @pytest.fixture
    def preprocessor(self):
        """Create a preprocessor instance for testing."""
        return TGFPreprocessor("") # Provide default empty string for initial_input

    def test_preprocess_with_include_directive(self, preprocessor, tmp_path):
        """Test preprocessing with include directives."""
        include_file = tmp_path / "common_rules.tgf"
        include_file.write_text("""
        // Common rules
        identifier: /[a-zA-Z_][a-zA-Z0-9_]*/
        string: /\"[^\"]*\"/
        """)
        
        main_grammar = f"""
        #include \"{include_file}\"
        
        start: identifier \"=\" expression
        expression: string | identifier
        """
        
        result = preprocessor.preprocess(main_grammar, base_path_override=tmp_path)
        
        assert "identifier:" in result
        assert "string:" in result
        assert "start:" in result
        assert "#include" not in result

    def test_preprocess_nested_includes(self, preprocessor, tmp_path):
        """Test preprocessing with nested include files."""
        common_terminals_file = tmp_path / "common_terminals.tgf"
        common_terminals_file.write_text("""
        NUMBER: /[0-9]+/
        IDENTIFIER: /[a-zA-Z_][a-zA-Z0-9_]*/
        """)

        level1_include_file = tmp_path / "level1_rules.tgf"
        level1_include_file.write_text(f"""
        #include \"{common_terminals_file}\"
        
        basic_expr: IDENTIFIER | NUMBER
        """)
        
        main_file_content = f"""
        #include \"{level1_include_file}\"
        
        start: complex_expr
        complex_expr: basic_expr (PLUS basic_expr)*
        PLUS: \"+\"
        """
        
        result = preprocessor.preprocess(main_file_content, base_path_override=tmp_path)
        
        assert "NUMBER:" in result
        assert "IDENTIFIER:" in result
        assert "basic_expr:" in result
        assert "complex_expr:" in result
        assert "start:" in result
        assert "#include" not in result

    def test_preprocess_circular_include_detection(self, preprocessor, tmp_path):
        """Test detection of circular includes raises CircularIncludeError."""
        file_a = tmp_path / "file_a.tgf"
        file_b = tmp_path / "file_b.tgf"

        file_a.write_text(f'#include \"{file_b}\"\na_rule: \"a\"')
        file_b.write_text(f'#include \"{file_a}\"\nb_rule: \"b\"')
        
        grammar_circular = f'#include \"{file_a}\"\nstart: a_rule | b_rule'

        raised_expected_exception = False
        actual_exception_value = None
        try:
            print("DEBUG TGFPP TEST: Calling preprocessor.preprocess...")
            preprocessor.preprocess(grammar_circular, base_path_override=tmp_path)
            print("DEBUG TGFPP TEST: preprocessor.preprocess returned WITHOUT error.") # Should not happen
        except CircularIncludeError as e:
            print(f"DEBUG TGFPP TEST: Caught CircularIncludeError: {e}")
            raised_expected_exception = True
            actual_exception_value = e
        except Exception as e_other:
            print(f"DEBUG TGFPP TEST: Caught UNEXPECTED Exception: {type(e_other).__name__}: {e_other}")
            actual_exception_value = e_other # Store for assertion if needed
        
        assert raised_expected_exception, f"CircularIncludeError was not raised. Instead, got: {actual_exception_value}"
        assert "Circular include detected" in str(actual_exception_value)
        # Check if one of the file names involved in the cycle is mentioned
        assert str(file_a.name) in str(actual_exception_value) or str(file_b.name) in str(actual_exception_value)

    @patch.object(Path, 'exists', return_value=False)
    @patch('builtins.open', new_callable=mock_open) # Mock open to ensure it's not called if exists is False
    def test_preprocess_include_file_not_found(self, mock_open_call, mock_path_exists, preprocessor, tmp_path):
        """Test handling of missing include files by raising IncludeFileNotFoundError."""
        grammar = '#include "missing.tgf"\nstart: "test"'
    
        with pytest.raises(IncludeFileNotFoundError) as exc_info:
            preprocessor.preprocess(grammar, base_path_override=tmp_path)
        
        assert "missing.tgf" in str(exc_info.value)
        assert str(tmp_path) in str(exc_info.value) # Check if the search path is mentioned

    def test_preprocess_include_with_relative_paths(self, preprocessor, tmp_path):
        """Test include with various relative path formats."""
        subdir = tmp_path / "includes"
        subdir.mkdir()
        
        include_file = subdir / "common.tgf"
        include_file.write_text("common_rule: 'common'")
        
        grammar = f"""
        #include "includes/common.tgf"
        #include "./includes/common.tgf"
        
        start: common_rule
        """
        
        result = preprocessor.preprocess(grammar, base_path_override=tmp_path)
        
        assert "common_rule:" in result
        assert result.count("common_rule:") == 1
