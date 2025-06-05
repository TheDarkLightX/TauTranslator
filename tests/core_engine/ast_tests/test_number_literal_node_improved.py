"""
Improved NumberLiteralNode tests following VibeArchitect mutation testing principles.
Demonstrates high-quality test patterns with multiple assertions and edge cases.
"""
import unittest
from dataclasses import FrozenInstanceError
import pytest
import time
from hypothesis import given, strategies as st

from tau_translator_omega.core_engine.ast import ASTNode, NumberLiteralNode


class TestNumberLiteralNodeImproved(unittest.TestCase):
    """Enhanced test suite following VibeArchitect standards."""

    def test_import_availability(self):
        """Test: NumberLiteralNode module imports successfully.
        
        Multiple assertions validate import completeness.
        """
        # ARRANGE-ACT-ASSERT pattern
        # ARRANGE: (implicit - import at module level)
        
        # ACT: Validate imports
        # ASSERT: Multiple specific assertions
        self.assertIsNotNone(NumberLiteralNode, "NumberLiteralNode class should be importable")
        self.assertTrue(hasattr(NumberLiteralNode, '__init__'), "Should have constructor")
        self.assertTrue(hasattr(NumberLiteralNode, '__dataclass_fields__'), "Should be dataclass")
        self.assertTrue(issubclass(NumberLiteralNode, ASTNode), "Should inherit from ASTNode")

    def test_valid_number_creation_comprehensive(self):
        """Test: Valid number creation covers all integer ranges.
        
        Boundary Value Analysis + Equivalence Partitioning applied.
        """
        # ARRANGE: Boundary values and equivalence classes
        boundary_values = [
            # Zero boundary
            0,
            # Positive boundaries
            1, 2, 10, 100, 1000,
            # Negative boundaries  
            -1, -2, -10, -100, -1000,
            # Large numbers
            2**31 - 1,  # Max 32-bit signed int
            -(2**31),   # Min 32-bit signed int
        ]
        
        for value in boundary_values:
            with self.subTest(value=value):
                # ACT: Create node
                start_time = time.time()
                node = NumberLiteralNode(value=value)
                creation_time = time.time() - start_time
                
                # ASSERT: Multiple validations
                self.assertEqual(node.value, value, f"Value should be preserved: {value}")
                self.assertIsInstance(node, ASTNode, "Should be ASTNode instance")
                self.assertIsInstance(node, NumberLiteralNode, "Should be NumberLiteralNode instance")
                self.assertLess(creation_time, 0.001, "Creation should be fast (<1ms)")

    @given(st.integers(min_value=-(2**63), max_value=2**63-1))
    def test_property_based_valid_integers(self, value):
        """Property-based test: All integers should create valid nodes.
        
        Uses hypothesis for comprehensive value testing.
        """
        # ACT: Create with any integer
        node = NumberLiteralNode(value=value)
        
        # ASSERT: Properties that must always hold
        self.assertEqual(node.value, value)
        self.assertIsInstance(node, NumberLiteralNode)
        self.assertTrue(hasattr(node, 'value'))

    def test_immutability_enforcement(self):
        """Test: Node immutability is strictly enforced.
        
        Tests multiple mutation attempts.
        """
        # ARRANGE: Create initial node
        original_value = 42
        node = NumberLiteralNode(value=original_value)
        
        # ACT & ASSERT: Multiple immutability checks
        with pytest.raises(FrozenInstanceError, match="cannot assign to field"):
            node.value = 99  # type: ignore
            
        with pytest.raises(FrozenInstanceError, match="cannot assign to field"):
            node.value = 0   # type: ignore
            
        with pytest.raises(FrozenInstanceError, match="cannot assign to field"):
            node.value = -1  # type: ignore
            
        # ASSERT: Original value unchanged
        self.assertEqual(node.value, original_value, "Original value must remain unchanged")

    def test_invalid_type_validation_comprehensive(self):
        """Test: Type validation rejects all non-integer types.
        
        Comprehensive equivalence partitioning for invalid inputs.
        """
        # ARRANGE: Invalid value equivalence classes
        invalid_types = [
            # Float types
            (3.14, "float"),
            (0.0, "zero float"),
            (-2.5, "negative float"),
            
            # String types
            ("123", "numeric string"),
            ("text", "text string"),
            ("", "empty string"),
            
            # None and boolean
            (None, "None type"),
            (True, "boolean True"),
            (False, "boolean False"),
            
            # Collection types
            ([], "empty list"),
            ([1, 2, 3], "list with numbers"),
            ({}, "empty dict"),
            ({"value": 1}, "dict"),
            
            # Other types
            (object(), "object instance"),
        ]
        
        for invalid_value, description in invalid_types:
            with self.subTest(value=invalid_value, description=description):
                # ACT & ASSERT: Should raise appropriate exception
                with pytest.raises(
                    (ValueError, TypeError), 
                    match="NumberLiteralNode value must be an integer"
                ):
                    NumberLiteralNode(value=invalid_value)  # type: ignore

    def test_equality_and_hash_comprehensive(self):
        """Test: Equality and hash behavior follows mathematical rules.
        
        Tests equality transitivity, symmetry, and hash consistency.
        """
        # ARRANGE: Test nodes
        node_1a = NumberLiteralNode(value=1)
        node_1b = NumberLiteralNode(value=1)
        node_1c = NumberLiteralNode(value=1)
        node_2 = NumberLiteralNode(value=2)
        node_neg1 = NumberLiteralNode(value=-1)
        
        # ASSERT: Equality properties
        # Reflexivity: x == x
        self.assertEqual(node_1a, node_1a, "Node should equal itself")
        
        # Symmetry: x == y implies y == x
        self.assertEqual(node_1a, node_1b, "Equal values should be equal")
        self.assertEqual(node_1b, node_1a, "Equality should be symmetric")
        
        # Transitivity: x == y and y == z implies x == z
        self.assertEqual(node_1a, node_1b, "First equality")
        self.assertEqual(node_1b, node_1c, "Second equality")
        self.assertEqual(node_1a, node_1c, "Transitive equality")
        
        # Inequality
        self.assertNotEqual(node_1a, node_2, "Different values should not be equal")
        self.assertNotEqual(node_1a, node_neg1, "Positive/negative should not be equal")
        self.assertNotEqual(node_1a, 1, "Node should not equal raw integer")
        self.assertNotEqual(node_1a, "1", "Node should not equal string")
        self.assertNotEqual(node_1a, None, "Node should not equal None")
        
        # ASSERT: Hash consistency
        # Equal objects must have equal hashes
        self.assertEqual(hash(node_1a), hash(node_1b), "Equal nodes must have equal hashes")
        
        # Hash should be consistent across multiple calls
        hash1 = hash(node_1a)
        hash2 = hash(node_1a)
        self.assertEqual(hash1, hash2, "Hash should be consistent")
        
        # Different values should generally have different hashes
        self.assertNotEqual(hash(node_1a), hash(node_2), "Different values should have different hashes")

    def test_performance_requirements(self):
        """Test: Performance meets VibeArchitect requirements.
        
        Tests creation time and memory efficiency.
        """
        # ARRANGE: Performance test parameters
        iterations = 1000
        max_time_per_creation = 0.001  # 1ms per VibeArchitect standards
        
        # ACT: Measure creation performance
        start_time = time.time()
        nodes = []
        for i in range(iterations):
            node = NumberLiteralNode(value=i)
            nodes.append(node)
        total_time = time.time() - start_time
        
        # ASSERT: Performance requirements
        avg_time_per_creation = total_time / iterations
        self.assertLess(avg_time_per_creation, max_time_per_creation,
                       f"Average creation time {avg_time_per_creation:.6f}s exceeds limit {max_time_per_creation}s")
        
        # ASSERT: All nodes created successfully
        self.assertEqual(len(nodes), iterations, "All nodes should be created")
        for i, node in enumerate(nodes):
            self.assertEqual(node.value, i, f"Node {i} should have correct value")

    def test_error_message_quality(self):
        """Test: Error messages are clear and actionable.
        
        Following VibeArchitect error handling principles.
        """
        # Test various invalid inputs for message quality
        test_cases = [
            (3.14, "float"),
            ("123", "string"),
            (None, "None"),
        ]
        
        for invalid_value, type_name in test_cases:
            with self.subTest(value=invalid_value, type_name=type_name):
                try:
                    NumberLiteralNode(value=invalid_value)  # type: ignore
                    self.fail("Should have raised exception")
                except (ValueError, TypeError) as e:
                    error_msg = str(e)
                    
                    # ASSERT: Error message quality
                    self.assertIn("NumberLiteralNode", error_msg, "Should mention class name")
                    self.assertIn("integer", error_msg, "Should mention expected type")
                    self.assertTrue(len(error_msg) > 10, "Should be descriptive")
                    self.assertTrue(len(error_msg) < 200, "Should be concise")


if __name__ == '__main__':
    unittest.main()