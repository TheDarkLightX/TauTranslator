import unittest
from dataclasses import FrozenInstanceError
import pytest
import time
import sys
from hypothesis import given, strategies as st, settings

# Import specific AST nodes needed for these tests
from tau_translator_omega.core_engine.ast import ASTNode, BooleanLiteralNode

class TestBooleanLiteralNodeFixed(unittest.TestCase):
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

    def test_boolean_literal_node_invalid_value_type_comprehensive(self):
        """Test creating BooleanLiteralNode with comprehensive invalid types."""
        
        # String representations of booleans (common mistake)
        string_booleans = ["True", "False", "true", "false", "TRUE", "FALSE", "yes", "no", "1", "0"]
        for val in string_booleans:
            with self.subTest(string_bool=val):
                with pytest.raises(ValueError, match="BooleanLiteralNode value must be a boolean"):
                    BooleanLiteralNode(value=val)  # type: ignore
        
        # Numeric representations (common in C-style languages)
        numeric_booleans = [0, 1, -1, 2, 0.0, 1.0, -1.0, 2.5]
        for val in numeric_booleans:
            with self.subTest(numeric_bool=val):
                with pytest.raises(ValueError, match="BooleanLiteralNode value must be a boolean"):
                    BooleanLiteralNode(value=val)  # type: ignore
        
        # None and container types
        other_types = [None, [], [True], {}, {"bool": True}, set(), {True}]
        for val in other_types:
            with self.subTest(other_type=val):
                with pytest.raises(ValueError, match="BooleanLiteralNode value must be a boolean"):
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
        
        # Hash consistency tests
        self.assertEqual(hash(node_true1), hash(node_true2), "Equal True nodes should have same hash")
        self.assertEqual(hash(node_false1), hash(node_false2), "Equal False nodes should have same hash")
        
        # Set operations
        node_set = {node_true1, node_true2, node_false1, node_false2}
        self.assertEqual(len(node_set), 2, "Set should contain 2 unique nodes (True and False)")

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

    def test_performance_benchmarks(self):
        """Test performance requirements per VibeArchitect standards."""
        
        # Benchmark node creation performance
        start_time = time.perf_counter()
        nodes = []
        for i in range(10000):
            value = i % 2 == 0  # Alternate True/False
            node = BooleanLiteralNode(value)
            nodes.append(node)
        creation_time = time.perf_counter() - start_time
        
        # Performance requirement: <20ms for 10,000 nodes
        self.assertLess(creation_time, 0.02, 
                       f"10,000 node creation should be <20ms, got {creation_time:.4f}s")
        
        # Benchmark equality comparison performance  
        start_time = time.perf_counter()
        for i in range(0, 100):  
            for j in range(0, 100):
                equal = nodes[i] == nodes[j]
        equality_time = time.perf_counter() - start_time
        
        # Performance requirement: <5ms for equality checks
        self.assertLess(equality_time, 0.005, 
                       f"10,000 equality checks should be <5ms, got {equality_time:.4f}s")
        
        # Memory efficiency
        node_sizes = [sys.getsizeof(node) for node in nodes[:100]]
        avg_size = sum(node_sizes) / len(node_sizes)
        
        # Memory requirement: average <80 bytes per node
        self.assertLess(avg_size, 80, f"Average node size should be <80 bytes, got {avg_size:.1f}")

if __name__ == '__main__':
    unittest.main()