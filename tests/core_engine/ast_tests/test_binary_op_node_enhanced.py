import unittest
from dataclasses import FrozenInstanceError
import pytest
from enum import Enum
import time
from hypothesis import given, strategies as st, settings, assume
from hypothesis.strategies import composite

# Import specific AST nodes needed for these tests
from tau_translator_omega.core_engine.ast import (
    ASTNode, BinaryOpNode, BinaryOperatorEnum, IdentifierNode, NumberLiteralNode
)

class TestBinaryOpNodeEnhanced(unittest.TestCase):
    """Enhanced BinaryOpNode tests following VibeArchitect principles.
    
    Tests include:
    - Property-based testing with hypothesis
    - Performance benchmarks
    - Boundary value analysis
    - Comprehensive error scenarios
    - Type safety validation
    """

    def test_import_binary_op_node_eventually_succeeds(self):
        """Ensures BinaryOpNode and BinaryOperatorEnum are importable."""
        self.assertIsNotNone(BinaryOpNode, "BinaryOpNode class should be imported.")
        self.assertIsNotNone(BinaryOperatorEnum, "BinaryOperatorEnum enum should be imported.")
        
        # Additional import validation
        self.assertTrue(hasattr(BinaryOpNode, '__init__'), "BinaryOpNode should have __init__ method")
        self.assertTrue(issubclass(BinaryOpNode, ASTNode), "BinaryOpNode should inherit from ASTNode")
        
        # Verify enum has expected operators
        expected_operators = ['LOGICAL_AND', 'LOGICAL_OR', 'EQUAL']
        for op in expected_operators:
            self.assertTrue(hasattr(BinaryOperatorEnum, op), f"BinaryOperatorEnum should have {op}")

    def test_create_binary_op_node_valid(self):
        """Test creating BinaryOpNode with valid parameters."""
        left = IdentifierNode("p")
        right_id = IdentifierNode("q")
        right_num = NumberLiteralNode(10)

        # Test logical AND with performance measurement
        start_time = time.perf_counter()
        node_and = BinaryOpNode(BinaryOperatorEnum.LOGICAL_AND, left, right_id)
        creation_time = time.perf_counter() - start_time
        
        # Performance assertion: <1ms for simple node creation
        self.assertLess(creation_time, 0.001, "BinaryOpNode creation should be <1ms")
        
        # Comprehensive validation
        self.assertEqual(node_and.operator, BinaryOperatorEnum.LOGICAL_AND)
        self.assertEqual(node_and.left_operand, left)
        self.assertEqual(node_and.right_operand, right_id)
        self.assertIsInstance(node_and, ASTNode)
        self.assertIsInstance(node_and, BinaryOpNode)
        
        # Type safety validation
        self.assertIsInstance(node_and.operator, BinaryOperatorEnum)
        self.assertIsInstance(node_and.left_operand, ASTNode)
        self.assertIsInstance(node_and.right_operand, ASTNode)

        # Test equality with different operand types
        node_eq = BinaryOpNode(BinaryOperatorEnum.EQUAL, left, right_num)
        self.assertEqual(node_eq.operator, BinaryOperatorEnum.EQUAL)
        self.assertEqual(node_eq.left_operand, left)
        self.assertEqual(node_eq.right_operand, right_num)
        
        # Verify different node types are not equal
        self.assertNotEqual(node_and, node_eq, "Different operators should create different nodes")

    def test_binary_op_node_immutable(self):
        """Test that BinaryOpNode is immutable."""
        node = BinaryOpNode(BinaryOperatorEnum.LOGICAL_OR, IdentifierNode("a"), IdentifierNode("b"))
        with pytest.raises(FrozenInstanceError):
            node.operator = BinaryOperatorEnum.LOGICAL_AND # type: ignore
        with pytest.raises(FrozenInstanceError):
            node.left_operand = IdentifierNode("c") # type: ignore
        with pytest.raises(FrozenInstanceError):
            node.right_operand = IdentifierNode("d") # type: ignore

    def test_binary_op_node_invalid_operator(self):
        """Test creating BinaryOpNode with invalid operator types."""
        left = IdentifierNode("p")
        right = IdentifierNode("q")
        
        # Test various invalid operator types
        invalid_operators = [
            "AND", "OR", "=",  # Strings
            123, 0, -1,        # Integers
            True, False,       # Booleans
            None,             # None
            [],               # List
            {},               # Dict
            object(),         # Object
        ]
        
        for invalid_op in invalid_operators:
            with self.subTest(operator=invalid_op):
                with pytest.raises((ValueError, TypeError), 
                                 match="operator must be an instance of BinaryOperatorEnum"):
                    BinaryOpNode(operator=invalid_op, left_operand=left, right_operand=right)  # type: ignore

    def test_binary_op_node_invalid_operands(self):
        """Test creating BinaryOpNode with invalid operand types."""
        invalid_operands = [
            "p", "q",          # Strings
            123, 0, -1,        # Integers
            True, False,       # Booleans
            None,             # None
            [],               # List
            {},               # Dict
            object(),         # Object
        ]
        
        valid_node = IdentifierNode("valid")
        
        # Test invalid left operands
        for invalid_left in invalid_operands:
            with self.subTest(left_operand=invalid_left):
                with pytest.raises((ValueError, TypeError), 
                                 match="left_operand must be an ASTNode instance"):
                    BinaryOpNode(BinaryOperatorEnum.LOGICAL_AND, invalid_left, valid_node)  # type: ignore
        
        # Test invalid right operands
        for invalid_right in invalid_operands:
            with self.subTest(right_operand=invalid_right):
                with pytest.raises((ValueError, TypeError), 
                                 match="right_operand must be an ASTNode instance"):
                    BinaryOpNode(BinaryOperatorEnum.LOGICAL_AND, valid_node, invalid_right)  # type: ignore
        
        # Test both operands invalid
        with pytest.raises((ValueError, TypeError)):
            BinaryOpNode(BinaryOperatorEnum.LOGICAL_AND, "invalid_left", "invalid_right")  # type: ignore

    def test_binary_op_node_equality_and_hash(self):
        """Test equality and hashability with comprehensive scenarios."""
        p = IdentifierNode("p")
        q = IdentifierNode("q")
        r = IdentifierNode("r")
        num10 = NumberLiteralNode(10)
        num20 = NumberLiteralNode(20)

        b1 = BinaryOpNode(BinaryOperatorEnum.LOGICAL_AND, p, q)
        b2 = BinaryOpNode(BinaryOperatorEnum.LOGICAL_AND, p, q)  # Same as b1
        b3 = BinaryOpNode(BinaryOperatorEnum.LOGICAL_OR, p, q)   # Diff operator
        b4 = BinaryOpNode(BinaryOperatorEnum.LOGICAL_AND, r, q)  # Diff left operand
        b5 = BinaryOpNode(BinaryOperatorEnum.LOGICAL_AND, p, r)  # Diff right operand
        b6 = BinaryOpNode(BinaryOperatorEnum.EQUAL, p, num10)    # Diff operator and right type
        b7 = BinaryOpNode(BinaryOperatorEnum.EQUAL, p, num20)    # Diff value

        # Equality tests with detailed assertions
        self.assertEqual(b1, b2, "Identical nodes should be equal")
        self.assertEqual(hash(b1), hash(b2), "Equal nodes should have same hash")
        
        # Inequality tests
        inequality_pairs = [
            (b1, b3, "Different operators"),
            (b1, b4, "Different left operands"),
            (b1, b5, "Different right operands"),
            (b1, b6, "Different operator and operand type"),
            (b6, b7, "Different operand values"),
        ]
        
        for node1, node2, description in inequality_pairs:
            with self.subTest(comparison=description):
                self.assertNotEqual(node1, node2, f"Should be unequal: {description}")
        
        # Cross-type equality (should be False)
        self.assertNotEqual(b1, p, "BinaryOpNode should not equal IdentifierNode")
        self.assertNotEqual(b1, "string", "BinaryOpNode should not equal string")
        self.assertNotEqual(b1, 123, "BinaryOpNode should not equal integer")
        self.assertNotEqual(b1, None, "BinaryOpNode should not equal None")

        # Hashability and set operations
        try:
            node_set = {b1, b2, b3, b4, b5, b6, b7}
            expected_unique = 6  # b1 and b2 are identical
            self.assertEqual(len(node_set), expected_unique, 
                           f"Set should contain {expected_unique} unique nodes")
            
            # Verify specific nodes are in set
            for node in [b1, b3, b4, b5, b6, b7]:
                self.assertIn(node, node_set, f"Node {node} should be in set")
            
            # Test set operations performance
            start_time = time.perf_counter()
            large_set = set()
            for i in range(100):
                node = BinaryOpNode(BinaryOperatorEnum.LOGICAL_AND, 
                                  IdentifierNode(f"var{i}"), 
                                  NumberLiteralNode(i))
                large_set.add(node)
            set_time = time.perf_counter() - start_time
            
            self.assertLess(set_time, 0.01, "Set operations should be efficient (<10ms for 100 nodes)")
            self.assertEqual(len(large_set), 100, "All nodes should be unique in large set")
            
        except TypeError as e:
            self.fail(f"BinaryOpNode instances are not hashable: {e}")

    @composite
    def binary_node_strategy(draw):
        """Hypothesis strategy for generating BinaryOpNode instances."""
        operator = draw(st.sampled_from(list(BinaryOperatorEnum)))
        
        # Generate valid operand names
        left_name = draw(st.text(min_size=1, max_size=20, alphabet=st.characters(
            whitelist_categories=['Lu', 'Ll', 'Nd'], whitelist_characters='_'
        )).filter(lambda x: x[0].isalpha() or x[0] == '_'))
        
        right_value = draw(st.one_of(
            st.text(min_size=1, max_size=20, alphabet=st.characters(
                whitelist_categories=['Lu', 'Ll', 'Nd'], whitelist_characters='_'
            )).filter(lambda x: x[0].isalpha() or x[0] == '_'),
            st.integers(min_value=-1000, max_value=1000)
        ))
        
        left_operand = IdentifierNode(left_name)
        
        if isinstance(right_value, str):
            right_operand = IdentifierNode(right_value)
        else:
            right_operand = NumberLiteralNode(right_value)
        
        return BinaryOpNode(operator, left_operand, right_operand)
    
    @given(binary_node_strategy())
    @settings(max_examples=50, deadline=1000)  # Performance constraint
    def test_property_binary_node_creation_always_valid(self, node):
        """Property-based test: All generated BinaryOpNodes should be valid."""
        # Basic properties that should always hold
        self.assertIsInstance(node, BinaryOpNode, "Generated node should be BinaryOpNode")
        self.assertIsInstance(node, ASTNode, "Generated node should inherit from ASTNode")
        self.assertIsInstance(node.operator, BinaryOperatorEnum, "Operator should be valid enum")
        self.assertIsInstance(node.left_operand, ASTNode, "Left operand should be ASTNode")
        self.assertIsInstance(node.right_operand, ASTNode, "Right operand should be ASTNode")
        
        # Test immutability
        with pytest.raises(FrozenInstanceError):
            node.operator = BinaryOperatorEnum.LOGICAL_OR  # type: ignore
    
    @given(binary_node_strategy(), binary_node_strategy())
    @settings(max_examples=25, deadline=1000)
    def test_property_equality_symmetry(self, node1, node2):
        """Property-based test: Equality should be symmetric."""
        # If nodes are equal, equality should be symmetric
        if node1 == node2:
            self.assertEqual(node2, node1, "Equality should be symmetric")
            self.assertEqual(hash(node1), hash(node2), "Equal nodes should have equal hashes")
    
    @given(binary_node_strategy())
    @settings(max_examples=50, deadline=1000)
    def test_property_reflexivity(self, node):
        """Property-based test: Node should equal itself."""
        self.assertEqual(node, node, "Node should equal itself (reflexivity)")
        self.assertEqual(hash(node), hash(node), "Hash should be consistent")
    
    def test_boundary_values(self):
        """Test boundary value scenarios."""
        # Test with extreme identifier names
        boundary_names = [
            "a",                    # Single character
            "_",                    # Single underscore
            "a" * 100,             # Very long name
            "_var_with_underscores", # Multiple underscores
            "CamelCaseVariable",    # Mixed case
        ]
        
        for name in boundary_names:
            with self.subTest(name=name):
                try:
                    left = IdentifierNode(name)
                    right = NumberLiteralNode(0)
                    node = BinaryOpNode(BinaryOperatorEnum.LOGICAL_AND, left, right)
                    
                    self.assertEqual(node.left_operand.name, name)
                    self.assertIsInstance(node, BinaryOpNode)
                except Exception as e:
                    self.fail(f"Boundary value test failed for name '{name}': {e}")
        
        # Test with extreme number values
        boundary_numbers = [
            0,                      # Zero
            1,                      # Positive small
            -1,                     # Negative small
            2**31 - 1,             # Max 32-bit int
            -(2**31),              # Min 32-bit int
            2**63 - 1,             # Max 64-bit int
            -(2**63),              # Min 64-bit int
        ]
        
        for num in boundary_numbers:
            with self.subTest(number=num):
                try:
                    left = IdentifierNode("var")
                    right = NumberLiteralNode(num)
                    node = BinaryOpNode(BinaryOperatorEnum.EQUAL, left, right)
                    
                    self.assertEqual(node.right_operand.value, num)
                    self.assertIsInstance(node, BinaryOpNode)
                except Exception as e:
                    self.fail(f"Boundary value test failed for number {num}: {e}")
    
    def test_performance_benchmarks(self):
        """Test performance requirements per VibeArchitect standards."""
        # Benchmark node creation
        start_time = time.perf_counter()
        nodes = []
        for i in range(1000):
            node = BinaryOpNode(
                BinaryOperatorEnum.LOGICAL_AND,
                IdentifierNode(f"var{i}"),
                NumberLiteralNode(i)
            )
            nodes.append(node)
        creation_time = time.perf_counter() - start_time
        
        # Performance requirement: <10ms for 1000 nodes (p99 <0.01ms per node)
        self.assertLess(creation_time, 0.01, 
                       f"1000 node creation should be <10ms, got {creation_time:.4f}s")
        
        # Benchmark equality operations
        start_time = time.perf_counter()
        comparisons = 0
        for i in range(100):
            for j in range(100):
                equal = nodes[i] == nodes[j]
                comparisons += 1
        equality_time = time.perf_counter() - start_time
        
        # Performance requirement: <20ms for 10,000 equality checks
        self.assertLess(equality_time, 0.02, 
                       f"10,000 equality checks should be <20ms, got {equality_time:.4f}s")
        
        # Benchmark hash operations
        start_time = time.perf_counter()
        node_set = set(nodes[:100])  # Add 100 nodes to set
        hash_time = time.perf_counter() - start_time
        
        # Performance requirement: <5ms for 100 hash operations
        self.assertLess(hash_time, 0.005, 
                       f"100 hash operations should be <5ms, got {hash_time:.4f}s")

if __name__ == '__main__':
    unittest.main()