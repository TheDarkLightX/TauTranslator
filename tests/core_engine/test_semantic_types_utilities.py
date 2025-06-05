#!/usr/bin/env python3
"""
Semantic Types Utility Functions Tests
======================================

Tests for utility functions in the semantic types module
including factory functions and helper methods.

Author: DarkLightX/Dana Edwards
"""

import unittest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from tau_translator_omega.core_engine.semantic_types import (
    TypeInfo, create_type_info, check_type_compatibility
)


class TestUtilityFunctions(unittest.TestCase):
    """Tests for utility functions"""
    
    def test_create_type_info_factory(self):
        """Test create_type_info factory function"""
        type1 = create_type_info("integer")
        self.assertIsInstance(type1, TypeInfo)
        self.assertEqual(type1.type_name, "integer")
        self.assertFalse(type1.is_inferred)
        
        type2 = create_type_info("string", is_inferred=True)
        self.assertEqual(type2.type_name, "string")
        self.assertTrue(type2.is_inferred)
    
    def test_check_type_compatibility_function(self):
        """Test check_type_compatibility function"""
        int_type = TypeInfo("integer")
        str_type = TypeInfo("string")
        auto_type = TypeInfo("auto")
        
        self.assertTrue(check_type_compatibility(int_type, int_type))
        self.assertFalse(check_type_compatibility(int_type, str_type))
        self.assertTrue(check_type_compatibility(auto_type, int_type))


if __name__ == '__main__':
    unittest.main()