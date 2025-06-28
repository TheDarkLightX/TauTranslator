"""
Unit tests for the CodeLineProcessor class from the NLP module.

Copyright: DarkLightX / Dana Edwards
"""

import pytest

from backend.unified.api.nlp import (
    CodeText,
    LineNumber,
    CodeLineProcessor
)


class TestCodeLineProcessor:
    """Test the CodeLineProcessor class."""
    
    def test_extract_code_lines_WithMixedContent_ReturnsOnlyCodeLines(self):
        # Given: Code with mixed content (code, comments, empty lines)
        code = CodeText("""// This is a comment
DEFINE x := true

// Another comment
always y -> z
""")
        
        # When: Extracting code lines
        result = CodeLineProcessor.extract_code_lines(code)
        
        # Then: Only non-comment, non-empty lines are returned with correct line numbers
        assert len(result) == 2
        assert result[0] == (LineNumber(2), CodeText("DEFINE x := true"))
        assert result[1] == (LineNumber(5), CodeText("always y -> z"))
    
    def test_extract_code_lines_WithEmptyCode_ReturnsEmptyList(self):
        # Given: Empty code
        code = CodeText("")
        
        # When: Extracting code lines
        result = CodeLineProcessor.extract_code_lines(code)
        
        # Then: Empty list is returned
        assert result == []
    
    @pytest.mark.parametrize("line,expected", [
        ("DEFINE x := true", True),
        ("// comment", False),
        ("", False),
        ("   ", False),
        ("   // indented comment", False),
    ])
    def test_is_meaningful_line_WithVariousInputs_ReturnsExpectedBoolean(self, line, expected):
        # Given: Various line types
        code_line = CodeText(line)
        
        # When: Checking if line is meaningful
        result = CodeLineProcessor.is_meaningful_line(code_line)
        
        # Then: Correct boolean is returned
        assert result == expected
