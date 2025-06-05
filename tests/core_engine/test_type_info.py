#!/usr/bin/env python3
"""
Type Information Tests
======================

Tests for the TypeInfo class which represents type information
for symbols and expressions in the semantic analyzer.

Author: DarkLightX/Dana Edwards
"""

import unittest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from tau_translator_omega.core_engine.semantic_types import TypeInfo


class TestTypeInfo(unittest.TestCase):
    """Tests for TypeInfo class"""
    
    def test_type_info_creation_valid(self):
        """Test creating valid type info"""
        type_info = TypeInfo("integer")
        self.assertEqual(type_info.type_name, "integer")
        self.assertFalse(type_info.is_inferred)
        
        # With inferred flag
        inferred = TypeInfo("string", is_inferred=True)
        self.assertEqual(inferred.type_name, "string")
        self.assertTrue(inferred.is_inferred)
    
    def test_type_info_invalid_type(self):
        """Test creating type info with invalid type"""
        with self.assertRaises(ValueError) as cm:
            TypeInfo("invalid_type")
        self.assertIn("Invalid type", str(cm.exception))
        self.assertIn("Valid types", str(cm.exception))
    
    def test_type_compatibility_same_type(self):
        """Test compatibility between same types"""
        int1 = TypeInfo("integer")
        int2 = TypeInfo("integer")
        self.assertTrue(int1.is_compatible_with(int2))
        self.assertTrue(int2.is_compatible_with(int1))
    
    def test_type_compatibility_different_types(self):
        """Test incompatibility between different types"""
        int_type = TypeInfo("integer")
        str_type = TypeInfo("string")
        self.assertFalse(int_type.is_compatible_with(str_type))
        self.assertFalse(str_type.is_compatible_with(int_type))
    
    def test_type_compatibility_auto_type(self):
        """Test auto type compatibility"""
        auto = TypeInfo("auto")
        integer = TypeInfo("integer")
        string = TypeInfo("string")
        
        # Auto is compatible with everything
        self.assertTrue(auto.is_compatible_with(integer))
        self.assertTrue(auto.is_compatible_with(string))
        self.assertTrue(integer.is_compatible_with(auto))
        self.assertTrue(string.is_compatible_with(auto))
    
    def test_type_hierarchy_compatibility(self):
        """Test type hierarchy compatibility"""
        integer = TypeInfo("integer")
        real = TypeInfo("real")
        
        # Both are numbers, should be compatible
        self.assertTrue(integer.is_compatible_with(real))
        self.assertTrue(real.is_compatible_with(integer))
    
    def test_type_info_equality(self):
        """Test type info equality"""
        type1 = TypeInfo("integer")
        type2 = TypeInfo("integer")
        type3 = TypeInfo("string")
        
        self.assertEqual(type1, type2)
        self.assertNotEqual(type1, type3)
        self.assertNotEqual(type1, "integer")  # Not equal to string
    
    def test_type_info_hash(self):
        """Test type info hashing"""
        type1 = TypeInfo("integer")
        type2 = TypeInfo("integer")
        
        self.assertEqual(hash(type1), hash(type2))
        
        # Can be used in sets
        type_set = {type1, type2}
        self.assertEqual(len(type_set), 1)
    
    def test_type_info_str(self):
        """Test string representation"""
        regular = TypeInfo("integer")
        self.assertEqual(str(regular), "integer")
        
        inferred = TypeInfo("string", is_inferred=True)
        self.assertEqual(str(inferred), "string (inferred)")


if __name__ == '__main__':
    unittest.main()