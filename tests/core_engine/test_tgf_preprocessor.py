import pytest
from tau_translator_omega.core_engine.tgf_preprocessor import TGFPreprocessor
from pathlib import Path

# Consider moving normalize_lark_string to a shared test utility file
def normalize_lark_string(lark_string: str) -> str:
    """Normalizes Lark grammar string by stripping leading/trailing whitespace from each line
       and removing empty lines. This makes comparisons less brittle.
    """
    lines = [line.strip() for line in lark_string.strip().splitlines()]
    return "\n".join(filter(None, lines))

class TestTgfPreprocessorDirectives:
    def test_directive_use_simple(self):
        """Tests the @use directive raises FileNotFoundError for a non-existent file."""
        tgf_content = """
@use "non_existent_grammar.tgf"
my_rule : A B C ;
        """
        preprocessor = TGFPreprocessor(tgf_content)
    
        # Determine the expected path for the error message
        # For string input, base_dir_for_includes defaults to Path.cwd()
        expected_missing_path = (Path.cwd() / "non_existent_grammar.tgf").resolve()
        expected_error_msg = f"Included file not found: {expected_missing_path} (referenced in _direct_content.tgf_)"

        with pytest.raises(FileNotFoundError) as excinfo:
            preprocessor.to_lark()
        
        assert str(excinfo.value) == expected_error_msg
        assert "non_existent_grammar.tgf" in preprocessor.included_files # Still records the attempt

    def test_directive_enable_production(self):
        """Tests the @enable productions directive."""
        tgf_content = "@enable productions some_production, another_prod ."
        preprocessor = TGFPreprocessor(tgf_content)
        expected_lark_output = "// TGF Directive: @enable productions some_production, another_prod ."
        actual_lark_output = preprocessor.to_lark()
        assert normalize_lark_string(actual_lark_output) == normalize_lark_string(expected_lark_output)
        assert "some_production" in preprocessor._productions_enabled
        assert "another_prod" in preprocessor._productions_enabled

    def test_directive_trim_whitespace_symbols(self):
        """Tests the @trim directive for whitespace symbols."""
        tgf_content = "@trim _, __ ." # Note the space before the period is optional by TGF spec
        preprocessor = TGFPreprocessor(tgf_content)
        expected_lark_output = "// TGF Directive: @trim _, __ ."
        actual_lark_output = preprocessor.to_lark()
        assert normalize_lark_string(actual_lark_output) == normalize_lark_string(expected_lark_output)
        assert "_" in preprocessor._whitespace_rules
        assert "__" in preprocessor._whitespace_rules

    def test_directive_inline_rule(self):
        """Tests the @inline directive."""
        tgf_content = "@inline common_rule, another_to_inline."
        preprocessor = TGFPreprocessor(tgf_content)
        expected_lark_output = "// TGF Directive: @inline common_rule, another_to_inline."
        actual_lark_output = preprocessor.to_lark()
        assert normalize_lark_string(actual_lark_output) == normalize_lark_string(expected_lark_output)
        assert "common_rule" in preprocessor._rules_to_inline
        assert "another_to_inline" in preprocessor._rules_to_inline
        # assert preprocessor._rules_to_inline["common_rule"] is True # or some specific value

    def test_directive_use_char_classes(self):
        """Tests the @use char classes directive."""
        tgf_content = "@use char classes Letters, Digits ."
        preprocessor = TGFPreprocessor(tgf_content)
        expected_lark_output = "// TGF Directive: @use char classes Letters, Digits ."
        actual_lark_output = preprocessor.to_lark()
        assert normalize_lark_string(actual_lark_output) == normalize_lark_string(expected_lark_output)
        assert "Letters" in preprocessor._char_classes_used
        assert "Digits" in preprocessor._char_classes_used

    def test_directive_use_terminals_to_keep(self):
        """Tests the @use terminals to keep directive."""
        tgf_content = "@use terminals to keep LPAREN, RPAREN ."
        preprocessor = TGFPreprocessor(tgf_content)
        expected_lark_output = "// TGF Directive: @use terminals to keep LPAREN, RPAREN ."
        actual_lark_output = preprocessor.to_lark()
        assert normalize_lark_string(actual_lark_output) == normalize_lark_string(expected_lark_output)
        assert "LPAREN" in preprocessor._terminals_to_keep
        assert "RPAREN" in preprocessor._terminals_to_keep

    def test_directive_unknown_directive(self):
        """Tests that an unknown directive is passed through as a comment."""
        tgf_content = "@unknown_directive this is some data."
        preprocessor = TGFPreprocessor(tgf_content)
        expected_lark_output = "// TGF Directive: @unknown_directive this is some data."
        actual_lark_output = preprocessor.to_lark()
        assert normalize_lark_string(actual_lark_output) == normalize_lark_string(expected_lark_output)
