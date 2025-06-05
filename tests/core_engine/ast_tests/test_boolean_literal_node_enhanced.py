import unittest
from dataclasses import FrozenInstanceError
import pytest
import time
import sys
from hypothesis import given, strategies as st, settings

# Import specific AST nodes needed for these tests
from tau_translator_omega.core_engine.ast import ASTNode, BooleanLiteralNode

class TestBooleanLiteralNodeEnhanced(unittest.TestCase):
    """Enhanced BooleanLiteralNode tests following VibeArchitect principles.
    
    Tests include:
    - Property-based testing with hypothesis
    - Performance benchmarks (<200ms p99)
    - Boundary value analysis
    - Comprehensive error scenarios
    - Memory efficiency validation
    - Type safety and immutability verification
    """

    def test_import_boolean_literal_node_eventually_succeeds(self):
        """Ensures BooleanLiteralNode is importable with enhanced validation."""
        self.assertIsNotNone(BooleanLiteralNode, "BooleanLiteralNode class should be imported.")
        
        # Enhanced import validation
        self.assertTrue(hasattr(BooleanLiteralNode, '__init__'), "BooleanLiteralNode should have __init__ method")
        # Note: dataclass fields are not direct attributes on the class
        self.assertTrue(issubclass(BooleanLiteralNode, ASTNode), "BooleanLiteralNode should inherit from ASTNode")
        
        # Verify it's a dataclass with frozen=True
        self.assertTrue(hasattr(BooleanLiteralNode, '__dataclass_fields__'), "Should be a dataclass")
        self.assertTrue(BooleanLiteralNode.__dataclass_params__.frozen, "Should be frozen dataclass")

    def test_create_boolean_literal_node_valid(self):
        """Test creating BooleanLiteralNode with valid values and performance measurement."""
        boolean_values = [True, False]
        
        for value in boolean_values:
            with self.subTest(value=value):
                # Performance measurement
                start_time = time.perf_counter()
                node = BooleanLiteralNode(value=value)
                creation_time = time.perf_counter() - start_time
                
                # Performance assertion: <50μs for single node creation
                self.assertLess(creation_time, 0.00005, f"Node creation should be <50μs, got {creation_time:.6f}s")
                
                # Comprehensive validation
                self.assertEqual(node.value, value, f"Value should be {value}")
                self.assertIsInstance(node, ASTNode, "Should be instance of ASTNode")
                self.assertIsInstance(node, BooleanLiteralNode, "Should be instance of BooleanLiteralNode")
                
                # Type validation - ensure value is exactly the boolean type
                self.assertIsInstance(node.value, bool, "Value should be bool type")
                self.assertEqual(type(node.value), bool, "Value should be exactly bool, not subclass")
                
                # Memory efficiency check
                node_size = sys.getsizeof(node)
                self.assertLessEqual(node_size, 150, f"Node should be memory efficient (<150 bytes), got {node_size}")

    def test_boolean_literal_node_immutable(self):
        """Test that BooleanLiteralNode is immutable with comprehensive scenarios."""
        true_node = BooleanLiteralNode(value=True)
        false_node = BooleanLiteralNode(value=False)
        
        # Test basic immutability for True node
        with pytest.raises(FrozenInstanceError, match="cannot assign to field"):
            true_node.value = False  # type: ignore
        
        # Test basic immutability for False node  
        with pytest.raises(FrozenInstanceError, match="cannot assign to field"):
            false_node.value = True  # type: ignore
        
        # Test that original values are preserved
        self.assertTrue(true_node.value, "True node value should remain True")
        self.assertFalse(false_node.value, "False node value should remain False")
        
        # Test immutability with various attempted assignment types
        invalid_assignments = [
            True, False,          # Other booleans
            "True", "False",      # Strings
            1, 0,                 # Integers (truthy/falsy)
            None,                 # None
            [],                   # Empty list (falsy)
            [1],                  # Non-empty list (truthy)
            {},                   # Empty dict (falsy)
            {"a": 1},            # Non-empty dict (truthy)
            object(),            # Object
        ]
        
        for invalid_value in invalid_assignments:
            with self.subTest(value=invalid_value):
                with pytest.raises(FrozenInstanceError):
                    true_node.value = invalid_value  # type: ignore
                # Verify value hasn't changed
                self.assertTrue(true_node.value, "True node should remain True after failed assignment")

    def test_boolean_literal_node_invalid_value_type_comprehensive(self):
        """Test creating BooleanLiteralNode with comprehensive invalid types."""
        
        # String representations of booleans (common mistake)
        string_booleans = ["True", "False", "true", "false", "TRUE", "FALSE", "yes", "no", "1", "0"]
        for val in string_booleans:
            with self.subTest(string_bool=val):
                with pytest.raises((ValueError, TypeError), 
                                 match="BooleanLiteralNode value must be a boolean"):
                    BooleanLiteralNode(value=val)  # type: ignore
        
        # Numeric representations (common in C-style languages)
        numeric_booleans = [0, 1, -1, 2, 0.0, 1.0, -1.0, 2.5]
        for val in numeric_booleans:
            with self.subTest(numeric_bool=val):
                with pytest.raises((ValueError, TypeError), 
                                 match="BooleanLiteralNode value must be a boolean"):
                    BooleanLiteralNode(value=val)  # type: ignore
        
        # None and container types
        other_types = [None, [], [True], {}, {"bool": True}, set(), {True}, object()]
        for val in other_types:
            with self.subTest(other_type=val):
                with pytest.raises((ValueError, TypeError), 
                                 match="BooleanLiteralNode value must be a boolean"):
                    BooleanLiteralNode(value=val)  # type: ignore
        
        # Function and lambda (edge cases)
        callable_types = [lambda: True, bool, type, len]
        for val in callable_types:
            with self.subTest(callable_type=val):
                with pytest.raises((ValueError, TypeError), 
                                 match="BooleanLiteralNode value must be a boolean"):
                    BooleanLiteralNode(value=val)  # type: ignore

    def test_boolean_literal_node_equality_and_hash_comprehensive(self):
        """Test equality and hashability with comprehensive scenarios."""
        # Create test nodes
        node_true1 = BooleanLiteralNode(value=True)
        node_true2 = BooleanLiteralNode(value=True)   # Same value as node_true1
        node_false1 = BooleanLiteralNode(value=False)
        node_false2 = BooleanLiteralNode(value=False) # Same value as node_false1
        
        # Equality tests with performance measurement
        start_time = time.perf_counter()
        equality_results = [
            node_true1 == node_true2,
            node_false1 == node_false2,
            node_true1 != node_false1,
        ]
        equality_time = time.perf_counter() - start_time
        
        self.assertTrue(all(equality_results), "All equality tests should pass")
        self.assertLess(equality_time, 0.00001, "Equality checks should be <10μs")
        
        # Detailed equality assertions
        self.assertEqual(node_true1, node_true2, "Nodes with True should be equal")
        self.assertEqual(node_false1, node_false2, "Nodes with False should be equal")
        self.assertNotEqual(node_true1, node_false1, "True and False nodes should be unequal")
        self.assertNotEqual(node_true2, node_false2, "True and False nodes should be unequal")
        
        # Hash consistency tests
        self.assertEqual(hash(node_true1), hash(node_true2), "Equal True nodes should have same hash")
        self.assertEqual(hash(node_false1), hash(node_false2), "Equal False nodes should have same hash")
        
        # Hash difference (not guaranteed but often true)
        # Note: We don't assert inequality of hashes as it's not guaranteed
        true_hash = hash(node_true1)
        false_hash = hash(node_false1)
        self.assertIsInstance(true_hash, int, "Hash should be integer")
        self.assertIsInstance(false_hash, int, "Hash should be integer")
        
        # Cross-type equality (should always be False)
        cross_type_tests = [
            (True, "Raw True boolean"),
            (False, "Raw False boolean"),
            ("True", "String 'True'"),
            ("False", "String 'False'"),
            (1, "Integer 1"),
            (0, "Integer 0"),
            (None, "None"),
            ([], "Empty list"),
            ({}, "Empty dict"),
            (object(), "Generic object"),
        ]
        
        for other_value, description in cross_type_tests:
            with self.subTest(cross_type=description):
                self.assertNotEqual(node_true1, other_value, f"Should not equal {description}")
                self.assertNotEqual(node_false1, other_value, f"Should not equal {description}")

        # Set operations with performance measurement
        start_time = time.perf_counter()
        node_set = {node_true1, node_true2, node_false1, node_false2}
        set_creation_time = time.perf_counter() - start_time
        
        self.assertLess(set_creation_time, 0.00005, "Set creation should be <50μs")
        self.assertEqual(len(node_set), 2, "Set should contain 2 unique nodes (True and False)")
        
        # Verify specific values are in set
        self.assertIn(BooleanLiteralNode(value=True), node_set, "True node should be in set")
        self.assertIn(BooleanLiteralNode(value=False), node_set, "False node should be in set")
        
        # Large set performance test
        start_time = time.perf_counter()
        large_set = set()
        for _ in range(1000):
            # Alternate between True and False
            value = True if len(large_set) % 2 == 0 else False
            node = BooleanLiteralNode(value)
            large_set.add(node)
        large_set_time = time.perf_counter() - start_time
        
        self.assertLess(large_set_time, 0.001, "Creating set with 1000 boolean nodes should be <1ms")
        self.assertEqual(len(large_set), 2, "Large set should still only contain 2 unique values")

    @given(st.booleans())
    @settings(max_examples=50, deadline=500)
    def test_property_valid_boolean_values(self, value):
        """Property-based test: All boolean values should create valid nodes."""
        # Test node creation
        node = BooleanLiteralNode(value=value)
        
        # Validate properties
        self.assertEqual(node.value, value, "Value should be preserved exactly")
        self.assertIsInstance(node, BooleanLiteralNode, "Should be BooleanLiteralNode instance")
        self.assertIsInstance(node, ASTNode, "Should be ASTNode instance")
        self.assertIsInstance(node.value, bool, "Value should be bool type")
        
        # Test immutability
        with pytest.raises(FrozenInstanceError):
            node.value = not value  # type: ignore
        
        # Test equality and hashing
        identical_node = BooleanLiteralNode(value=value)
        self.assertEqual(node, identical_node, "Identical nodes should be equal")
        self.assertEqual(hash(node), hash(identical_node), "Identical nodes should hash equally")

    @given(st.one_of(
        st.text(),  # Strings
        st.integers(),  # Integers
        st.floats(),  # Floats  
        st.none(),  # None
        st.lists(st.booleans()),  # Lists
        st.dictionaries(st.text(), st.booleans()),  # Dicts
        st.sets(st.booleans()),  # Sets
    ))
    @settings(max_examples=50, deadline=500)
    def test_property_invalid_values_always_fail(self, invalid_value):
        """Property-based test: Non-boolean values should always raise errors."""
        with pytest.raises((ValueError, TypeError)):
            BooleanLiteralNode(value=invalid_value)  # type: ignore

    def test_boolean_literal_exhaustive_coverage(self):
        """Test exhaustive coverage of all possible boolean values."""
        # There are only two possible boolean values - test both exhaustively
        boolean_values = [True, False]
        
        for value in boolean_values:
            with self.subTest(value=value):
                node = BooleanLiteralNode(value=value)
                
                # Basic properties
                self.assertEqual(node.value, value)
                self.assertIsInstance(node.value, bool)
                self.assertEqual(type(node.value), bool)  # Exact type check
                
                # Logical properties
                if value:
                    self.assertTrue(node.value, "True node should have truthy value")
                    self.assertNotEqual(node.value, False, "True node should not equal False")
                else:
                    self.assertFalse(node.value, "False node should have falsy value")
                    self.assertNotEqual(node.value, True, "False node should not equal True")
                
                # Memory and performance
                node_size = sys.getsizeof(node)
                self.assertLessEqual(node_size, 150, f"Node should be memory efficient, got {node_size} bytes")

    def test_performance_benchmarks(self):
        """Test performance requirements per VibeArchitect standards."""
        
        # Benchmark 1: Node creation performance
        start_time = time.perf_counter()
        nodes = []
        for i in range(10000):
            value = i % 2 == 0  # Alternate True/False
            node = BooleanLiteralNode(value)
            nodes.append(node)
        creation_time = time.perf_counter() - start_time
        
        # Performance requirement: <20ms for 10,000 nodes (p99 <0.002ms per node)
        self.assertLess(creation_time, 0.02, 
                       f"10,000 node creation should be <20ms, got {creation_time:.4f}s")
        
        # Benchmark 2: Equality comparison performance  
        start_time = time.perf_counter()
        comparisons = 0
        for i in range(0, 1000, 10):  # Sample every 10th node
            for j in range(0, 1000, 10):
                equal = nodes[i] == nodes[j]
                comparisons += 1
        equality_time = time.perf_counter() - start_time
        
        # Performance requirement: <5ms for equality checks
        self.assertLess(equality_time, 0.005, 
                       f"{comparisons} equality checks should be <5ms, got {equality_time:.4f}s")
        
        # Benchmark 3: Hash performance and set operations
        start_time = time.perf_counter()
        node_set = set(nodes[:1000])  # Add 1000 nodes to set
        hash_time = time.perf_counter() - start_time
        
        # Performance requirement: <2ms for 1000 hash operations
        self.assertLess(hash_time, 0.002, 
                       f"1000 hash operations should be <2ms, got {hash_time:.4f}s")
        
        # Verify set has correct size (only True and False)
        self.assertEqual(len(node_set), 2, "Set should contain exactly 2 unique boolean values")
        
        # Benchmark 4: Memory efficiency
        node_sizes = [sys.getsizeof(node) for node in nodes[:100]]
        avg_size = sum(node_sizes) / len(node_sizes)
        max_size = max(node_sizes)
        
        # Memory requirements: average <80 bytes, max <150 bytes per node
        self.assertLess(avg_size, 80, f"Average node size should be <80 bytes, got {avg_size:.1f}")
        self.assertLess(max_size, 150, f"Max node size should be <150 bytes, got {max_size}")

    def test_logical_operations_compatibility(self):
        """Test that boolean literal nodes work correctly with logical operations."""
        true_node = BooleanLiteralNode(value=True)
        false_node = BooleanLiteralNode(value=False)
        
        # Test that node values work with Python logical operators
        self.assertTrue(true_node.value and True, "True node should work with 'and'")
        self.assertFalse(false_node.value and True, "False node should work with 'and'")
        self.assertTrue(true_node.value or False, "True node should work with 'or'")
        self.assertFalse(false_node.value or False, "False node should work with 'or'")
        self.assertFalse(not true_node.value, "True node should work with 'not'")
        self.assertTrue(not false_node.value, "False node should work with 'not'")
        
        # Test with conditional expressions
        result1 = "yes" if true_node.value else "no"
        result2 = "yes" if false_node.value else "no"
        self.assertEqual(result1, "yes", "True node should work in conditionals")
        self.assertEqual(result2, "no", "False node should work in conditionals")

    def test_string_representation_and_debugging(self):
        """Test string representation for debugging purposes."""
        true_node = BooleanLiteralNode(value=True)
        false_node = BooleanLiteralNode(value=False)
        
        # Test __repr__ exists and is useful
        true_repr = repr(true_node)
        false_repr = repr(false_node)
        
        self.assertIsInstance(true_repr, str, "__repr__ should return string")
        self.assertIsInstance(false_repr, str, "__repr__ should return string")
        self.assertIn("True", true_repr, "__repr__ should contain the value")
        self.assertIn("False", false_repr, "__repr__ should contain the value")
        self.assertIn("BooleanLiteralNode", true_repr, "__repr__ should contain class name")
        self.assertIn("BooleanLiteralNode", false_repr, "__repr__ should contain class name")
        
        # Test __str__ if implemented
        true_str = str(true_node)
        false_str = str(false_node)
        self.assertIsInstance(true_str, str, "__str__ should return string")
        self.assertIsInstance(false_str, str, "__str__ should return string")

if __name__ == '__main__':
    unittest.main()