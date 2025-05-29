import pytest
from tau_translator_omega.core_engine.tgf_preprocessor import TGFPreprocessor
from pathlib import Path

def normalize_lark_string(lark_string: str) -> str:
    """Normalizes Lark grammar string by stripping leading/trailing whitespace from each line
       and removing empty lines. This makes comparisons less brittle.
    """
    lines = [line.strip() for line in lark_string.strip().splitlines()]
    return "\n".join(filter(None, lines))


class TestTgfPreprocessorBasic:
    def test_empty_tgf_input(self):
        """Tests that an empty TGF input string results in an empty Lark output string."""
        tgf_content = ""
        preprocessor = TGFPreprocessor(tgf_content)
        
        expected_lark_output = ""
        actual_lark_output = preprocessor.to_lark()
        
        assert normalize_lark_string(actual_lark_output) == normalize_lark_string(expected_lark_output)

    def test_tgf_input_with_only_comments(self):
        """Tests that TGF input with only comments is processed correctly."""
        tgf_content = """\
# This is a comment line
# And another one
        """
        preprocessor = TGFPreprocessor(tgf_content)
        
        expected_lark_output = """\
// TGF Comment: # This is a comment line
// TGF Comment: # And another one
        """
        actual_lark_output = preprocessor.to_lark()
        
        assert normalize_lark_string(actual_lark_output) == normalize_lark_string(expected_lark_output)
