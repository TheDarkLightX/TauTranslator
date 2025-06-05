#!/usr/bin/env python3
"""
Error Collector Tests
=====================

Tests for the ErrorCollector class which collects and manages
semantic errors and warnings during analysis.

Author: DarkLightX/Dana Edwards
"""

import unittest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from tau_translator_omega.core_engine.semantic_types import ErrorCollector, SemanticError


class TestErrorCollector(unittest.TestCase):
    """Tests for ErrorCollector class"""
    
    def test_error_collector_initialization(self):
        """Test initial state of error collector"""
        collector = ErrorCollector()
        self.assertEqual(len(collector.errors), 0)
        self.assertEqual(len(collector.warnings), 0)
        self.assertFalse(collector.has_errors())
        self.assertFalse(collector.has_warnings())
    
    def test_add_error(self):
        """Test adding errors"""
        collector = ErrorCollector()
        error1 = SemanticError("Error 1", 1, 0)
        error2 = SemanticError("Error 2", 2, 0)
        
        collector.add_error(error1)
        collector.add_error(error2)
        
        self.assertEqual(len(collector.errors), 2)
        self.assertTrue(collector.has_errors())
        self.assertIn(error1, collector.errors)
        self.assertIn(error2, collector.errors)
    
    def test_add_error_invalid_type(self):
        """Test adding non-SemanticError raises exception"""
        collector = ErrorCollector()
        
        with self.assertRaises(ValueError) as cm:
            collector.add_error("not an error")
        self.assertIn("Expected SemanticError instance", str(cm.exception))
    
    def test_add_warning(self):
        """Test adding warnings"""
        collector = ErrorCollector()
        
        collector.add_warning("Warning 1", 10)
        collector.add_warning("Warning 2")  # No line number
        
        self.assertEqual(len(collector.warnings), 2)
        self.assertTrue(collector.has_warnings())
        
        # Check warning structure
        warning1 = collector.warnings[0]
        self.assertEqual(warning1['message'], "Warning 1")
        self.assertEqual(warning1['line_number'], 10)
        
        warning2 = collector.warnings[1]
        self.assertEqual(warning2['message'], "Warning 2")
        self.assertIsNone(warning2['line_number'])
    
    def test_error_type_tracking(self):
        """Test error type counting"""
        collector = ErrorCollector()
        
        # Add different types of errors
        collector.add_error(SemanticError("Error 1"))
        collector.add_error(SemanticError("Error 2"))
        
        # Check internal tracking
        self.assertEqual(collector._error_count_by_type['SemanticError'], 2)
    
    def test_error_summary(self):
        """Test getting error summary"""
        collector = ErrorCollector()
        
        # Add errors and warnings
        collector.add_error(SemanticError("Error 1"))
        collector.add_error(SemanticError("Error 2"))
        collector.add_warning("Warning 1")
        
        summary = collector.get_error_summary()
        
        self.assertEqual(summary['total_errors'], 2)
        self.assertEqual(summary['total_warnings'], 1)
        self.assertTrue(summary['has_errors'])
        self.assertIn('SemanticError', summary['errors_by_type'])
        self.assertEqual(summary['errors_by_type']['SemanticError'], 2)
    
    def test_clear_errors_and_warnings(self):
        """Test clearing all errors and warnings"""
        collector = ErrorCollector()
        
        # Add some errors and warnings
        collector.add_error(SemanticError("Error"))
        collector.add_warning("Warning")
        
        # Clear
        collector.clear()
        
        self.assertEqual(len(collector.errors), 0)
        self.assertEqual(len(collector.warnings), 0)
        self.assertFalse(collector.has_errors())
        self.assertFalse(collector.has_warnings())
        self.assertEqual(len(collector._error_count_by_type), 0)


if __name__ == '__main__':
    unittest.main()