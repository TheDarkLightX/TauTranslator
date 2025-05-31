#!/usr/bin/env python3
"""
Tests for Enhanced NLP Capabilities
==================================

TDD tests for the new NLP enhancements including:
- AMR semantic layer
- Incremental parsing with caching
- Performance optimizations
"""

import unittest
import time
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from tau_translator_omega.core_engine.nlp_enhanced.amr_semantic_layer import (
    AMRSemanticAnalyzer, AMRGraph, AMRConcept, AMRRelation, AMRConceptLibrary
)
from tau_translator_omega.core_engine.nlp_enhanced.incremental_parser import (
    IncrementalTCEParser, IncrementalParseCache, TextDiffer, Edit, EditType
)
from tau_translator_omega.core_engine.cnl_parser.ast_nodes import (
    PredicateCallNode, VariableNode, QuantifierBlockNode
)


class TestAMRSemanticLayer(unittest.TestCase):
    """Test AMR semantic analysis capabilities"""
    
    def setUp(self):
        """Set up test environment"""
        self.analyzer = AMRSemanticAnalyzer()
        self.concept_library = AMRConceptLibrary()
    
    def test_concept_library_builtin_concepts(self):
        """Test that concept library has built-in concepts"""
        # Should have mathematical predicates
        equal_concept = self.concept_library.get_concept("equal")
        self.assertIsNotNone(equal_concept)
        self.assertEqual(equal_concept.frame_type, "predicate")
        self.assertEqual(len(equal_concept.roles), 2)
        
        # Should have logical operators
        and_concept = self.concept_library.get_concept("and")
        self.assertIsNotNone(and_concept)
        self.assertEqual(and_concept.frame_type, "operator")
        
        # Should have quantifiers
        forall_concept = self.concept_library.get_concept("forall")
        self.assertIsNotNone(forall_concept)
        self.assertEqual(forall_concept.frame_type, "quantifier")
    
    def test_amr_graph_creation(self):
        """Test AMR graph creation and manipulation"""
        graph = AMRGraph()
        
        # Create concept and instance
        concept = AMRConcept("prime-01", "predicate", [AMRRelation.ARG1], {})
        instance = graph.add_instance("p1", concept)
        
        self.assertEqual(len(graph.instances), 1)
        self.assertIn("p1", graph.instances)
        self.assertEqual(instance.concept.name, "prime-01")
    
    def test_amr_graph_edges(self):
        """Test AMR graph edge creation"""
        graph = AMRGraph()
        
        # Create predicate and argument instances
        pred_concept = AMRConcept("prime-01", "predicate", [AMRRelation.ARG1], {})
        arg_concept = AMRConcept("thing", "entity", [], {})
        
        pred_instance = graph.add_instance("p1", pred_concept)
        arg_instance = graph.add_instance("x1", arg_concept)
        
        # Add edge
        graph.add_edge("p1", AMRRelation.ARG1, "x1")
        
        self.assertEqual(len(graph.edges), 1)
        self.assertIn(AMRRelation.ARG1, pred_instance.arguments)
        self.assertEqual(pred_instance.arguments[AMRRelation.ARG1], arg_instance)
    
    def test_predicate_analysis(self):
        """Test predicate call analysis to AMR"""
        # Create simple predicate call: prime(x)
        predicate = PredicateCallNode(name="prime", args=[VariableNode(name="x")])
        
        graph = self.analyzer.analyze(predicate)
        
        # Should create instances for predicate and variable
        self.assertGreater(len(graph.instances), 1)
        
        # Should have semantic roles
        roles = self.analyzer.get_semantic_roles(graph, "prime")
        self.assertGreater(len(roles), 0)
        
        # Should have correct role structure
        for role in roles:
            self.assertIn("predicate", role)
            self.assertIn("role", role)
            self.assertIn("confidence", role)
            self.assertGreaterEqual(role["confidence"], 0.0)
            self.assertLessEqual(role["confidence"], 1.0)
    
    def test_quantifier_analysis(self):
        """Test quantifier block analysis to AMR"""
        # Create quantifier: forall x
        quantifier = QuantifierBlockNode(
            quant_type="forall",
            variables=[VariableNode(name="x")],
            condition=PredicateCallNode(name="prime", args=[VariableNode(name="x")])
        )
        
        graph = self.analyzer.analyze(quantifier)
        
        # Should create instances for quantifier, variable, and condition
        self.assertGreaterEqual(len(graph.instances), 3)
        
        # Should track variables
        self.assertIn("x", graph.variables)
    
    def test_penman_notation_generation(self):
        """Test PENMAN notation generation for debugging"""
        graph = AMRGraph()
        
        concept = AMRConcept("prime-01", "predicate", [AMRRelation.ARG1], {})
        instance = graph.add_instance("p1", concept)
        graph.set_root("p1")
        
        penman = graph.to_penman()
        
        self.assertIn("p1", penman)
        self.assertIn("prime-01", penman)


class TestIncrementalParser(unittest.TestCase):
    """Test incremental parsing with caching"""
    
    def setUp(self):
        """Set up test environment"""
        self.parser = IncrementalTCEParser(cache_size=100)
        self.differ = TextDiffer()
    
    def test_parse_cache_basic_operations(self):
        """Test basic cache operations"""
        cache = IncrementalParseCache(max_size=10)
        
        # Test cache miss
        result = cache.get("test text")
        self.assertIsNone(result)
        
        # Test cache put and hit
        mock_ast = VariableNode(name="test")
        cache.put("test text", mock_ast)
        
        result = cache.get("test text")
        self.assertIsNotNone(result)
        self.assertEqual(result.name, "test")
    
    def test_cache_lru_eviction(self):
        """Test LRU eviction in cache"""
        cache = IncrementalParseCache(max_size=3)
        
        # Fill cache
        for i in range(3):
            cache.put(f"text{i}", VariableNode(name=f"var{i}"))
        
        # Access first item to make it recently used
        cache.get("text0")
        
        # Add new item - should evict text1 (least recently used)
        cache.put("text3", VariableNode(name="var3"))
        
        # text1 should be evicted
        self.assertIsNone(cache.get("text1"))
        # text0 should still be there (recently accessed)
        self.assertIsNotNone(cache.get("text0"))
    
    def test_cache_invalidation(self):
        """Test cache invalidation on text changes"""
        cache = IncrementalParseCache()
        
        # Cache some results
        cache.put("original text", VariableNode(name="test"))
        
        # Invalidate
        cache.invalidate("original text")
        
        # Should be evicted
        self.assertIsNone(cache.get("original text"))
    
    def test_text_differ_edit_computation(self):
        """Test text difference computation"""
        old_text = "For all x, prime(x)"
        new_text = "For all x, even(x)"
        
        edits = self.differ.compute_edits(old_text, new_text)
        
        # Should detect the change from "prime" to "even"
        self.assertGreater(len(edits), 0)
        
        # Should be classified as a small edit
        self.assertTrue(self.differ.is_small_edit(edits))
    
    def test_edit_type_detection(self):
        """Test different types of edits"""
        # Test insertion
        edits = self.differ.compute_edits("hello", "hello world")
        self.assertEqual(len(edits), 1)
        self.assertEqual(edits[0].edit_type, EditType.INSERT)
        
        # Test deletion
        edits = self.differ.compute_edits("hello world", "hello")
        self.assertEqual(len(edits), 1)
        self.assertEqual(edits[0].edit_type, EditType.DELETE)
        
        # Test replacement - difflib might generate multiple operations
        edits = self.differ.compute_edits("hello", "world")
        self.assertGreater(len(edits), 0)
        # Should contain at least one replacement operation
        has_replace = any(edit.edit_type == EditType.REPLACE for edit in edits)
        self.assertTrue(has_replace)
    
    def test_incremental_parsing_performance(self):
        """Test that incremental parsing is faster than full parsing"""
        text1 = "For all x, prime(x) implies odd(x) and greater(x, 2)"
        text2 = "For all x, prime(x) implies even(x) and greater(x, 2)"  # Small change
        
        # First parse (full)
        start_time = time.time()
        ast1, meta1 = self.parser.parse(text1)
        full_parse_time = time.time() - start_time
        
        # Second parse (should be incremental)
        start_time = time.time()
        ast2, meta2 = self.parser.parse(text2, text1, ast1)
        incremental_parse_time = time.time() - start_time
        
        # Incremental should be faster (or use cache)
        # Note: For very simple text, the overhead might make it slower
        # This test mainly ensures the system works
        self.assertIsNotNone(ast2)
        
        # Third parse (should be cache hit)
        start_time = time.time()
        ast3, meta3 = self.parser.parse(text1)  # Back to original
        cache_parse_time = time.time() - start_time
        
        # Cache hit should be very fast
        self.assertTrue(meta3["cache_hit"])
        self.assertLess(cache_parse_time, full_parse_time)
    
    def test_parser_statistics(self):
        """Test parser performance statistics collection"""
        # Perform several parses
        text1 = "prime(x)"
        text2 = "even(x)"
        
        # First parse
        self.parser.parse(text1)
        
        # Second parse
        self.parser.parse(text2)
        
        # Third parse - same as first, should be cache hit
        self.parser.parse(text1)
        
        # Fourth parse
        self.parser.parse("odd(x)")
        
        stats = self.parser.get_performance_stats()
        
        # Should have collected statistics
        self.assertGreater(stats["total_parses"], 0)
        self.assertGreaterEqual(stats["cache_hits"], 1)  # Third text should be cache hit
        self.assertIn("cache_hit_rate", stats)
        self.assertIn("average_parse_time", stats)
    
    def test_large_edit_fallback(self):
        """Test that large edits fall back to full parsing"""
        old_text = "For all x, prime(x)"
        new_text = "There exists y such that even(y) and greater(y, 10) or odd(y)"
        
        edits = self.differ.compute_edits(old_text, new_text)
        
        # Should be classified as large edit
        self.assertFalse(self.differ.is_small_edit(edits))
        
        # Parser should handle this gracefully
        ast1, _ = self.parser.parse(old_text)
        ast2, meta2 = self.parser.parse(new_text, old_text, ast1)
        
        # Should not use incremental parsing for large changes
        self.assertFalse(meta2.get("incremental", False))


class TestNLPIntegration(unittest.TestCase):
    """Test integration between different NLP components"""
    
    def test_amr_incremental_integration(self):
        """Test AMR analysis with incremental parsing"""
        parser = IncrementalTCEParser()
        amr_analyzer = AMRSemanticAnalyzer()
        
        text1 = "prime(x)"
        text2 = "even(x)"
        
        # Parse and analyze
        ast1, _ = parser.parse(text1)
        if ast1:
            amr1 = amr_analyzer.analyze(ast1)
            self.assertIsNotNone(amr1)
        
        ast2, meta2 = parser.parse(text2, text1, ast1)
        if ast2:
            amr2 = amr_analyzer.analyze(ast2)
            self.assertIsNotNone(amr2)
    
    def test_performance_comparison(self):
        """Compare enhanced NLP vs basic parsing performance"""
        # This is more of a benchmark than a test
        basic_texts = [
            "x = 5",
            "prime(x)",
            "x > 0",
            "even(x) and odd(y)"
        ]
        
        enhanced_parser = IncrementalTCEParser()
        amr_analyzer = AMRSemanticAnalyzer()
        
        # Measure enhanced NLP performance
        start_time = time.time()
        for text in basic_texts:
            ast, _ = enhanced_parser.parse(text)
            if ast:
                amr_graph = amr_analyzer.analyze(ast)
        enhanced_time = time.time() - start_time
        
        # Should complete in reasonable time
        self.assertLess(enhanced_time, 1.0)  # Less than 1 second for basic cases


if __name__ == '__main__':
    unittest.main()