#!/usr/bin/env python3
"""
Semantic Error Exception Tests
==============================

Tests for the SemanticError exception class used for reporting
semantic analysis errors with location information.

Author: DarkLightX/Dana Edwards
"""

import unittest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from tau_translator_omega.core_engine.semantic_types import SemanticError


class TestSemanticError(unittest.TestCase):
    """Tests for SemanticError exception class"""
    
    def test_semantic_error_with_full_location(self):
        """Test error creation with line and column numbers"""
        error = SemanticError("Test error", 10, 5)
        self.assertEqual(error.message, "Test error")
        self.assertEqual(error.line_number, 10)
        self.assertEqual(error.column_number, 5)
        self.assertEqual(str(error), "SemanticError (L10, C5): Test error")
    
    def test_semantic_error_with_line_only(self):
        """Test error creation with only line number"""
        error = SemanticError("Line only error", 20)
        self.assertEqual(error.message, "Line only error")
        self.assertEqual(error.line_number, 20)
        self.assertIsNone(error.column_number)
        self.assertEqual(str(error), "SemanticError (L20): Line only error")
    
    def test_semantic_error_without_location(self):
        """Test error creation without location info"""
        error = SemanticError("No location error")
        self.assertEqual(error.message, "No location error")
        self.assertIsNone(error.line_number)
        self.assertIsNone(error.column_number)
        self.assertEqual(str(error), "SemanticError: No location error")
    
    def test_semantic_error_inheritance(self):
        """Test that SemanticError inherits from Exception"""
        error = SemanticError("Test")
        self.assertIsInstance(error, Exception)
        
        # Test it can be raised and caught
        with self.assertRaises(SemanticError) as cm:
            raise error
        self.assertEqual(cm.exception.message, "Test")


if __name__ == '__main__':
    unittest.main()