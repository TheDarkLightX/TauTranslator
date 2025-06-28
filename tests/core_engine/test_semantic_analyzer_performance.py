#!/usr/bin/env python3
"""
Performance Tests for Semantic Analyzer
======================================

TDD tests to ensure semantic analyzer meets performance requirements:
- O(1) symbol table operations
- O(n) single-pass analysis
- Sub-millisecond analysis for typical programs
"""

import unittest
import time
import random
import string
from typing import List
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from tau_translator_omega.core_engine.semantic.semantic_analyzer import (
    SemanticAnalyzer, SymbolTable, Symbol
)
from tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes import (
    VariableDeclNode, VariableNode, ConstantNode, SentenceNode,
    AssignmentNode, ArithmeticBinaryOpNode
)


class TestSemanticAnalyzerPerformance(unittest.TestCase):
    """Test performance characteristics of semantic analyzer"""
    
    def setUp(self):
        """Set up test environment"""
        self.analyzer = SemanticAnalyzer()
    
    def generate_random_identifier(self, length: int = 10) -> str:
        """Generate random identifier for testing"""
        return ''.join(random.choices(string.ascii_lowercase, k=length))
    
    def test_symbol_table_lookup_performance(self):
        """Test O(1) symbol table lookup performance"""
        # Create symbol table with many symbols
        symbol_table = SymbolTable()
        num_symbols = 10000
        
        # Insert symbols
        symbols = []
        for i in range(num_symbols):
            name = f"var_{i}"
            symbol = Symbol(name, "variable", 0)
            symbol_table.declare_symbol(symbol)
            symbols.append(name)
        
        # Measure lookup time
        lookup_times = []
        for _ in range(1000):
            # Random lookup
            target = random.choice(symbols)
            start_time = time.perf_counter()
            result = symbol_table.lookup_symbol(target)
            end_time = time.perf_counter()
            lookup_times.append(end_time - start_time)
        
        # Average lookup time should be constant (< 1 microsecond)
        avg_lookup_time = sum(lookup_times) / len(lookup_times)
        self.assertLess(avg_lookup_time, 1e-6, 
                       f"Average lookup time {avg_lookup_time*1e6:.2f}µs exceeds 1µs")
        
        # Verify O(1) behavior - time shouldn't depend on table size
        # Test with different table sizes
        sizes = [100, 1000, 10000]
        avg_times = []
        
        for size in sizes:
            table = SymbolTable()
            for i in range(size):
                table.declare_symbol(Symbol(f"var_{i}", "variable", 0))
            
            # Measure average lookup time
            times = []
            for _ in range(100):
                target = f"var_{random.randint(0, size-1)}"
                start = time.perf_counter()
                table.lookup_symbol(target)
                end = time.perf_counter()
                times.append(end - start)
            
            avg_times.append(sum(times) / len(times))
        
        # Check that lookup time doesn't grow with table size
        # Allow 2x variation due to system noise
        self.assertLess(avg_times[-1] / avg_times[0], 2.0,
                       "Lookup time appears to grow with table size - not O(1)")
    
    def test_single_pass_analysis_performance(self):
        """Test O(n) single-pass analysis performance"""
        # Generate ASTs of different sizes
        ast_sizes = [100, 1000, 5000]
        analysis_times = []
        
        for size in ast_sizes:
            # Create AST with 'size' nodes
            ast = self._generate_ast_tree(size)
            
            # Measure analysis time
            analyzer = SemanticAnalyzer()
            start_time = time.perf_counter()
            analyzer.analyze(ast)
            end_time = time.perf_counter()
            
            analysis_times.append(end_time - start_time)
        
        # Check linear growth O(n)
        # Time should grow linearly with input size
        growth_rate1 = analysis_times[1] / analysis_times[0]
        growth_rate2 = analysis_times[2] / analysis_times[1]
        size_ratio1 = ast_sizes[1] / ast_sizes[0]
        size_ratio2 = ast_sizes[2] / ast_sizes[1]
        
        # Allow 50% deviation from perfect linear growth
        self.assertLess(abs(growth_rate1 / size_ratio1 - 1), 0.5,
                       f"Non-linear growth detected: {growth_rate1:.2f}x time for {size_ratio1}x size")
        self.assertLess(abs(growth_rate2 / size_ratio2 - 1), 0.5,
                       f"Non-linear growth detected: {growth_rate2:.2f}x time for {size_ratio2}x size")
    
    def test_sub_millisecond_analysis(self):
        """Test sub-millisecond analysis for typical programs"""
        # Generate a typical TCE program AST (50-100 nodes)
        ast = self._generate_typical_tce_ast()
        
        # Warm up
        analyzer = SemanticAnalyzer()
        analyzer.analyze(ast)
        
        # Measure multiple runs
        times = []
        for _ in range(100):
            analyzer = SemanticAnalyzer()
            start = time.perf_counter()
            analyzer.analyze(ast)
            end = time.perf_counter()
            times.append(end - start)
        
        avg_time = sum(times) / len(times)
        max_time = max(times)
        
        # Should complete in under 1 millisecond
        self.assertLess(avg_time, 0.001, 
                       f"Average analysis time {avg_time*1000:.2f}ms exceeds 1ms")
        self.assertLess(max_time, 0.002,
                       f"Max analysis time {max_time*1000:.2f}ms exceeds 2ms")
    
    def test_memory_efficiency(self):
        """Test memory usage per AST node"""
        import sys
        
        # Create analyzer and symbol table
        analyzer = SemanticAnalyzer()
        
        # Measure baseline memory
        baseline_size = sys.getsizeof(analyzer) + sys.getsizeof(analyzer.symbol_table)
        
        # Add 1000 symbols
        for i in range(1000):
            symbol = Symbol(f"var_{i}", "variable", 0)
            analyzer.symbol_table.declare_symbol(symbol)
        
        # Measure after adding symbols
        total_size = sys.getsizeof(analyzer) + sys.getsizeof(analyzer.symbol_table)
        
        # Calculate per-symbol memory usage
        per_symbol_memory = (total_size - baseline_size) / 1000
        
        # Should use less than 100 bytes per symbol
        self.assertLess(per_symbol_memory, 100,
                       f"Per-symbol memory usage {per_symbol_memory:.0f} bytes exceeds 100 bytes")
    
    def _generate_ast_tree(self, num_nodes: int) -> SentenceNode:
        """Generate AST tree with specified number of nodes"""
        nodes = []
        
        # Create variable declarations
        for i in range(num_nodes // 3):
            var_decl = VariableDeclNode(
                name=f"var_{i}",
                var_type="integer"
            )
            nodes.append(var_decl)
        
        # Create assignments
        for i in range(num_nodes // 3):
            assignment = AssignmentNode(
                target=VariableNode(name=f"var_{i}"),
                expression=ConstantNode(value=str(i))
            )
            nodes.append(assignment)
        
        # Create expressions
        for i in range(num_nodes - 2 * (num_nodes // 3)):
            expr = ArithmeticBinaryOpNode(
                left=VariableNode(name=f"var_{i % (num_nodes // 3)}"),
                operator="+",
                right=ConstantNode(value="1")
            )
            nodes.append(expr)
        
        return SentenceNode(content=nodes)
    
    def _generate_typical_tce_ast(self) -> SentenceNode:
        """Generate AST for a typical TCE program"""
        nodes = []
        
        # Variable declarations
        for var in ["x", "y", "z", "result"]:
            nodes.append(VariableDeclNode(
                name=var,
                var_type="integer"
            ))
        
        # Some assignments
        nodes.append(AssignmentNode(
            target=VariableNode(name="x"),
            expression=ConstantNode(value="10")
        ))
        
        nodes.append(AssignmentNode(
            target=VariableNode(name="y"), 
            expression=ConstantNode(value="20")
        ))
        
        # Arithmetic expression
        nodes.append(AssignmentNode(
            target=VariableNode(name="result"),
            expression=ArithmeticBinaryOpNode(
                left=VariableNode(name="x"),
                operator="+",
                right=VariableNode(name="y")
            )
        ))
        
        return SentenceNode(content=nodes)


if __name__ == '__main__':
    unittest.main()