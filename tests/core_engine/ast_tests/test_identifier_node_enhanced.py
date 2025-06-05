import unittest
from dataclasses import FrozenInstanceError
import pytest
import time
import string
import sys
from hypothesis import given, strategies as st, settings, assume

# Import specific AST nodes needed for these tests
from tau_translator_omega.core_engine.ast import ASTNode, IdentifierNode

class TestIdentifierNodeEnhanced(unittest.TestCase):
    """Enhanced IdentifierNode tests following VibeArchitect principles.
    
    Tests include:
    - Property-based testing with hypothesis
    - Performance benchmarks (<200ms p99)
    - Boundary value analysis
    - Comprehensive error scenarios
    - Memory efficiency validation
    - Unicode and edge case handling
    """

    def test_import_ast_nodes_eventually_succeeds(self):
        """Ensures IdentifierNode and its base ASTNode are importable."""
        self.assertIsNotNone(IdentifierNode, "IdentifierNode class should be imported.")
        self.assertIsNotNone(ASTNode, "ASTNode class should be imported.")
        
        # Enhanced import validation
        self.assertTrue(hasattr(IdentifierNode, '__init__'), "IdentifierNode should have __init__ method")
        # Note: dataclass fields are not direct attributes on the class
        self.assertTrue(issubclass(IdentifierNode, ASTNode), "IdentifierNode should inherit from ASTNode")
        
        # Verify it's a dataclass with frozen=True
        self.assertTrue(hasattr(IdentifierNode, '__dataclass_fields__'), "Should be a dataclass")
        self.assertTrue(IdentifierNode.__dataclass_params__.frozen, "Should be frozen dataclass")

    def test_create_identifier_node_valid(self):
        """Test creating an IdentifierNode with valid names and performance measurement."""
        valid_names = [
            "my_var",
            "variable123", 
            "_private_var",
            "CamelCaseVar",
            "snake_case_var",
            "x",
            "very_long_variable_name_that_should_still_work_fine"
        ]
        
        for name in valid_names:
            with self.subTest(name=name):
                # Performance measurement
                start_time = time.perf_counter()
                node = IdentifierNode(name=name)
                creation_time = time.perf_counter() - start_time
                
                # Performance assertion: <100μs for single node creation
                self.assertLess(creation_time, 0.0001, f"Node creation should be <100μs, got {creation_time:.6f}s")
                
                # Comprehensive validation
                self.assertEqual(node.name, name, f"Name should be '{name}'")
                self.assertIsInstance(node, ASTNode, "Should be instance of ASTNode")
                self.assertIsInstance(node, IdentifierNode, "Should be instance of IdentifierNode")
                
                # Type validation
                self.assertIsInstance(node.name, str, "Name should be string")
                
                # Memory efficiency check
                self.assertLessEqual(sys.getsizeof(node), 200, "Node should be memory efficient (<200 bytes)")

    def test_identifier_node_immutable(self):
        """Test that IdentifierNode is immutable with comprehensive scenarios."""
        node = IdentifierNode(name="test_immutability")
        
        # Test basic immutability
        with pytest.raises(FrozenInstanceError, match="cannot assign to field"):
            node.name = "new_name"  # type: ignore
        
        # Test that original value is preserved
        self.assertEqual(node.name, "test_immutability", "Original value should be preserved")
        
        # Test immutability with various attempted assignment types
        invalid_assignments = [
            "string_value",
            123,
            None,
            [],
            {},
            object()
        ]
        
        for invalid_value in invalid_assignments:
            with self.subTest(value=invalid_value):
                with pytest.raises(FrozenInstanceError):
                    node.name = invalid_value  # type: ignore
                # Verify name hasn't changed
                self.assertEqual(node.name, "test_immutability")

    def test_identifier_node_invalid_name_comprehensive(self):
        """Test creating an IdentifierNode with comprehensive invalid inputs."""
        
        # Empty string tests
        empty_strings = ["", "   ", "\t", "\n", "\r\n", " \t \n "]
        for empty_str in empty_strings:
            with self.subTest(name=empty_str):
                with pytest.raises(ValueError, match="Identifier name must be a non-empty string"):
                    IdentifierNode(name=empty_str)
        
        # Non-string type tests
        non_string_values = [
            123, 0, -1,           # Integers
            123.45, 0.0, -1.5,    # Floats
            True, False,          # Booleans
            None,                 # None
            [],                   # List
            {},                   # Dict
            set(),                # Set
            object(),             # Object
            lambda x: x,          # Function
        ]
        
        for invalid_value in non_string_values:
            with self.subTest(name=invalid_value):
                with pytest.raises((ValueError, TypeError), 
                                 match="Identifier name must be a non-empty string"):
                    IdentifierNode(name=invalid_value)  # type: ignore

    def test_identifier_node_equality_and_hash_comprehensive(self):
        """Test equality and hashability with comprehensive scenarios."""
        # Create test nodes
        node1_var1 = IdentifierNode(name="var1")
        node2_var1 = IdentifierNode(name="var1")  # Same name as node1
        node3_var2 = IdentifierNode(name="var2")  # Different name
        node4_empty = IdentifierNode(name="x")     # Minimal valid name
        
        # Equality tests with performance measurement
        start_time = time.perf_counter()
        equality_result = node1_var1 == node2_var1
        equality_time = time.perf_counter() - start_time
        
        self.assertTrue(equality_result, "Nodes with same name should be equal")
        self.assertLess(equality_time, 0.00001, "Equality check should be <10μs")
        
        # Hash consistency
        self.assertEqual(hash(node1_var1), hash(node2_var1), "Equal nodes should have same hash")
        
        # Inequality tests
        inequality_tests = [
            (node1_var1, node3_var2, "Different names"),
            (node1_var1, node4_empty, "Different name lengths"),
            (node3_var2, node4_empty, "Different specific names"),
        ]
        
        for node_a, node_b, description in inequality_tests:
            with self.subTest(test=description):
                self.assertNotEqual(node_a, node_b, f"Should be unequal: {description}")
        
        # Cross-type equality (should always be False)
        cross_type_tests = [
            ("var1", "String with same value"),
            (123, "Integer"),
            (None, "None"),
            ([], "Empty list"),
            ({}, "Empty dict"),
            (object(), "Generic object"),
        ]
        
        for other_value, description in cross_type_tests:
            with self.subTest(cross_type=description):
                self.assertNotEqual(node1_var1, other_value, f"Should not equal {description}")

        # Hashability and set operations with performance measurement
        start_time = time.perf_counter()
        node_set = {node1_var1, node2_var1, node3_var2, node4_empty}
        set_creation_time = time.perf_counter() - start_time
        
        self.assertLess(set_creation_time, 0.0001, "Set creation should be <100μs")
        self.assertEqual(len(node_set), 3, "Set should contain 3 unique nodes (node1 == node2)")
        
        # Verify specific nodes are in set
        expected_nodes = [node1_var1, node3_var2, node4_empty]
        for node in expected_nodes:
            self.assertIn(node, node_set, f"Node {node.name} should be in set")
        
        # Large set performance test
        start_time = time.perf_counter()
        large_set = set()
        for i in range(1000):
            node = IdentifierNode(f"var_{i}")
            large_set.add(node)
        large_set_time = time.perf_counter() - start_time
        
        self.assertLess(large_set_time, 0.01, "Creating set with 1000 nodes should be <10ms")
        self.assertEqual(len(large_set), 1000, "All 1000 nodes should be unique")

    @given(st.text(min_size=1, max_size=100, alphabet=st.characters(
        whitelist_categories=['Lu', 'Ll', 'Nd'], 
        whitelist_characters='_'
    )).filter(lambda x: x[0].isalpha() or x[0] == '_'))
    @settings(max_examples=100, deadline=1000)
    def test_property_valid_identifier_names(self, name):
        """Property-based test: All valid identifier names should create valid nodes."""
        assume(name.strip() == name)  # No leading/trailing whitespace
        assume(len(name.strip()) > 0)  # Non-empty after strip
        
        # Test node creation
        node = IdentifierNode(name=name)
        
        # Validate properties
        self.assertEqual(node.name, name, "Name should be preserved exactly")
        self.assertIsInstance(node, IdentifierNode, "Should be IdentifierNode instance")
        self.assertIsInstance(node, ASTNode, "Should be ASTNode instance")
        
        # Test immutability
        with pytest.raises(FrozenInstanceError):
            node.name = "changed"  # type: ignore
        
        # Test equality and hashing
        identical_node = IdentifierNode(name=name)
        self.assertEqual(node, identical_node, "Identical nodes should be equal")
        self.assertEqual(hash(node), hash(identical_node), "Identical nodes should hash equally")

    @given(st.one_of(
        st.text(max_size=0),  # Empty strings
        st.text(min_size=1).filter(lambda x: x.isspace()),  # Whitespace only
        st.integers(),  # Integers
        st.floats(),  # Floats  
        st.booleans(),  # Booleans
        st.none(),  # None
        st.lists(st.text()),  # Lists
        st.dictionaries(st.text(), st.text()),  # Dicts
    ))
    @settings(max_examples=50, deadline=1000)
    def test_property_invalid_names_always_fail(self, invalid_name):
        """Property-based test: Invalid names should always raise errors."""
        with pytest.raises((ValueError, TypeError)):
            IdentifierNode(name=invalid_name)  # type: ignore

    def test_boundary_values_comprehensive(self):
        """Test boundary value scenarios comprehensively."""
        
        # Minimum valid identifiers
        minimal_valid = [
            "a", "b", "z",  # Single letters
            "A", "B", "Z",  # Single uppercase
            "_",            # Single underscore
            "_a", "_1",     # Underscore prefixed
        ]
        
        for name in minimal_valid:
            with self.subTest(minimal=name):
                node = IdentifierNode(name=name)
                self.assertEqual(node.name, name)
                self.assertIsInstance(node, IdentifierNode)
        
        # Maximum reasonable length (test system limits)
        max_lengths = [100, 1000, 10000]
        for length in max_lengths:
            with self.subTest(length=length):
                name = "a" * length
                try:
                    start_time = time.perf_counter()
                    node = IdentifierNode(name=name)
                    creation_time = time.perf_counter() - start_time
                    
                    self.assertEqual(node.name, name)
                    # Even very long names should create quickly
                    self.assertLess(creation_time, 0.001, f"Long name ({length} chars) should create <1ms")
                except MemoryError:
                    self.skipTest(f"System cannot handle {length} character names")
        
        # Edge case characters (valid in identifiers)
        edge_cases = [
            "var_123",          # Mixed alphanumeric with underscore
            "_private",         # Leading underscore
            "__dunder__",       # Double underscore (Python style)
            "CamelCase",        # Mixed case
            "ALL_CAPS",         # All uppercase
            "lowercase",        # All lowercase
            "a1b2c3",          # Alternating letters/numbers
            "_" * 10,          # Multiple underscores
        ]
        
        for name in edge_cases:
            with self.subTest(edge_case=name):
                node = IdentifierNode(name=name)
                self.assertEqual(node.name, name)
                
                # Test these can be used in sets efficiently
                node_set = {node}
                self.assertIn(node, node_set)

    def test_performance_benchmarks(self):
        """Test performance requirements per VibeArchitect standards."""
        
        # Benchmark 1: Node creation performance
        start_time = time.perf_counter()
        nodes = []
        for i in range(10000):
            node = IdentifierNode(f"var_{i}")
            nodes.append(node)
        creation_time = time.perf_counter() - start_time
        
        # Performance requirement: <50ms for 10,000 nodes (p99 <0.005ms per node)
        self.assertLess(creation_time, 0.05, 
                       f"10,000 node creation should be <50ms, got {creation_time:.4f}s")
        
        # Benchmark 2: Equality comparison performance  
        start_time = time.perf_counter()
        comparisons = 0
        for i in range(0, 1000, 10):  # Sample every 10th node
            for j in range(0, 1000, 10):
                equal = nodes[i] == nodes[j]
                comparisons += 1
        equality_time = time.perf_counter() - start_time
        
        # Performance requirement: <10ms for 10,000 equality checks
        self.assertLess(equality_time, 0.01, 
                       f"{comparisons} equality checks should be <10ms, got {equality_time:.4f}s")
        
        # Benchmark 3: Hash performance and set operations
        start_time = time.perf_counter()
        node_set = set(nodes[:1000])  # Add 1000 nodes to set
        hash_time = time.perf_counter() - start_time
        
        # Performance requirement: <5ms for 1000 hash operations
        self.assertLess(hash_time, 0.005, 
                       f"1000 hash operations should be <5ms, got {hash_time:.4f}s")
        
        # Verify set has correct size (all unique)
        self.assertEqual(len(node_set), 1000, "All nodes should be unique in set")
        
        # Benchmark 4: Memory efficiency
        node_sizes = [sys.getsizeof(node) for node in nodes[:100]]
        avg_size = sum(node_sizes) / len(node_sizes)
        max_size = max(node_sizes)
        
        # Memory requirements: average <100 bytes, max <200 bytes per node
        self.assertLess(avg_size, 100, f"Average node size should be <100 bytes, got {avg_size:.1f}")
        self.assertLess(max_size, 200, f"Max node size should be <200 bytes, got {max_size}")

    def test_string_representation_and_debugging(self):
        """Test string representation for debugging purposes."""
        node = IdentifierNode("test_var")
        
        # Test __repr__ exists and is useful
        repr_str = repr(node)
        self.assertIsInstance(repr_str, str, "__repr__ should return string")
        self.assertIn("test_var", repr_str, "__repr__ should contain the name")
        self.assertIn("IdentifierNode", repr_str, "__repr__ should contain class name")
        
        # Test __str__ if implemented
        str_str = str(node)
        self.assertIsInstance(str_str, str, "__str__ should return string")
        
        # Representation should be evaluable for debugging (if possible)
        try:
            # This might not work depending on implementation, but test if it does
            eval_result = eval(repr_str)
            if hasattr(eval_result, 'name'):
                self.assertEqual(eval_result.name, "test_var", "repr should be evaluable")
        except (NameError, SyntaxError):
            # This is okay - not all reprs are evaluable
            pass

if __name__ == '__main__':
    unittest.main()