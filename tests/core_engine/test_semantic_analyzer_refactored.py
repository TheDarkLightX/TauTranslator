import unittest
from dataclasses import dataclass
from typing import Optional

# Import refactored semantic analyzer components
from tau_translator_omega.core_engine.semantic_analyzer import SemanticAnalyzer
from tau_translator_omega.core_engine.semantic_types import (
    SemanticError, Symbol, SymbolTable, TypeInfo, ErrorCollector,
    create_type_info, check_type_compatibility
)
from tau_translator_omega.core_engine.semantic_analyzer_core import (
    ExpressionTypeResolver, ValidationEngine, SymbolDefinitionManager
)

# Simple mock AST nodes for testing
@dataclass
class MockASTNode:
    """Mock AST node for testing."""
    line: Optional[int] = None
    column: Optional[int] = None
    line_number: Optional[int] = None  # For compatibility with semantic analyzer

@dataclass
class MockVariableNode(MockASTNode):
    """Mock variable node for testing."""
    name: str = "test_var"

@dataclass
class MockVariableDeclNode(MockASTNode):
    """Mock variable declaration node for testing."""
    name: str = "test_var"
    var_type: str = "integer"
    value: Optional[MockASTNode] = None

@dataclass 
class MockConstantNode(MockASTNode):
    """Mock constant node for testing."""
    value: int = 42

class TestRefactoredSemanticAnalyzer(unittest.TestCase):
    """Test suite for refactored semantic analyzer components."""

    def setUp(self):
        """Set up test fixtures."""
        self.vocabulary = {
            'types': {'integer', 'string', 'boolean', 'auto'},
            'predicates': {
                'is_valid': {'arity': 1, 'signature': ['auto']},
                'equals': {'arity': 2, 'signature': ['auto', 'auto']}
            },
            'functions': {
                'add': {'arity': 2, 'signature': ['integer', 'integer'], 'return': 'integer'}
            }
        }
        self.analyzer = SemanticAnalyzer(self.vocabulary)

    def test_semantic_analyzer_initialization(self):
        """Test semantic analyzer initializes correctly."""
        self.assertIsNotNone(self.analyzer)
        self.assertIsInstance(self.analyzer.symbol_table, SymbolTable)
        self.assertIsInstance(self.analyzer.error_collector, ErrorCollector)
        self.assertIsInstance(self.analyzer.type_resolver, ExpressionTypeResolver)
        self.assertIsInstance(self.analyzer.validation_engine, ValidationEngine)
        self.assertIsInstance(self.analyzer.symbol_manager, SymbolDefinitionManager)

    def test_semantic_analyzer_vocabulary_loading(self):
        """Test that vocabulary symbols are loaded correctly."""
        # Test predicate loading
        is_valid_symbol = self.analyzer.symbol_table.lookup_symbol('is_valid')
        self.assertIsNotNone(is_valid_symbol)
        self.assertEqual(is_valid_symbol.symbol_type, 'predicate')
        self.assertEqual(is_valid_symbol.attributes['arity'], 1)

        # Test function loading
        add_symbol = self.analyzer.symbol_table.lookup_symbol('add')
        self.assertIsNotNone(add_symbol)
        self.assertEqual(add_symbol.symbol_type, 'function')
        self.assertEqual(add_symbol.attributes['arity'], 2)

    def test_semantic_analyzer_analysis_stats(self):
        """Test analysis statistics tracking."""
        mock_node = MockVariableNode(name="test")
        
        # Run analysis
        analyzed_node, errors = self.analyzer.analyze(mock_node)
        
        # Check stats
        stats = self.analyzer.get_analysis_stats()
        self.assertIn('analysis_count', stats)
        self.assertIn('symbol_table_stats', stats)
        self.assertIn('type_resolution_stats', stats)
        self.assertIn('error_summary', stats)
        
        self.assertEqual(stats['analysis_count'], 1)

class TestSemanticTypes(unittest.TestCase):
    """Test suite for semantic types module."""

    def test_semantic_error_creation(self):
        """Test SemanticError creation and formatting."""
        # Basic error
        error1 = SemanticError("Test error")
        self.assertEqual(str(error1), "SemanticError: Test error")
        
        # Error with line number
        error2 = SemanticError("Test error", line_number=10)
        self.assertEqual(str(error2), "SemanticError (L10): Test error")
        
        # Error with line and column
        error3 = SemanticError("Test error", line_number=10, column_number=5)
        self.assertEqual(str(error3), "SemanticError (L10, C5): Test error")

    def test_symbol_creation_and_validation(self):
        """Test Symbol creation and validation."""
        # Valid symbol
        symbol = Symbol("test_var", "variable", 0)
        self.assertEqual(symbol.name, "test_var")
        self.assertEqual(symbol.symbol_type, "variable")
        self.assertEqual(symbol.scope_level, 0)
        
        # Test validation
        with self.assertRaises(ValueError):
            Symbol("", "variable", 0)  # Empty name
        
        with self.assertRaises(ValueError):
            Symbol("test", "", 0)  # Empty type
        
        with self.assertRaises(ValueError):
            Symbol("test", "variable", -1)  # Negative scope

    def test_symbol_equality_and_hashing(self):
        """Test Symbol equality and hashing."""
        symbol1 = Symbol("test", "variable", 0)
        symbol2 = Symbol("test", "variable", 0)
        symbol3 = Symbol("test", "function", 0)
        
        # Equality
        self.assertEqual(symbol1, symbol2)
        self.assertNotEqual(symbol1, symbol3)
        
        # Hashing
        symbol_set = {symbol1, symbol2, symbol3}
        self.assertEqual(len(symbol_set), 2)  # symbol1 and symbol2 are the same

    def test_symbol_table_operations(self):
        """Test SymbolTable operations."""
        table = SymbolTable()
        
        # Test initial state
        self.assertEqual(table.current_scope_level, 0)
        
        # Test symbol declaration
        symbol = Symbol("test_var", "variable", 0)
        table.declare_symbol(symbol)
        
        # Test symbol lookup
        found_symbol = table.lookup_symbol("test_var")
        self.assertEqual(found_symbol, symbol)
        
        # Test scope operations
        table.enter_scope()
        self.assertEqual(table.current_scope_level, 1)
        
        table.exit_scope()
        self.assertEqual(table.current_scope_level, 0)

    def test_symbol_table_redeclaration_error(self):
        """Test that symbol redeclaration raises error."""
        table = SymbolTable()
        
        symbol1 = Symbol("test_var", "variable", 0)
        table.declare_symbol(symbol1)
        
        # Try to redeclare in same scope
        symbol2 = Symbol("test_var", "function", 0)
        with self.assertRaises(SemanticError):
            table.declare_symbol(symbol2)

    def test_symbol_table_performance_stats(self):
        """Test SymbolTable performance statistics."""
        table = SymbolTable()
        
        # Add some symbols
        for i in range(10):
            symbol = Symbol(f"var_{i}", "variable", 0)
            table.declare_symbol(symbol)
        
        # Perform lookups
        for i in range(5):
            table.lookup_symbol(f"var_{i}")
        
        stats = table.get_performance_stats()
        self.assertIn('lookup_count', stats)
        self.assertIn('symbol_count', stats)
        self.assertIn('scope_depth', stats)
        self.assertEqual(stats['symbol_count'], 10)
        self.assertEqual(stats['lookup_count'], 5)

    def test_type_info_creation_and_compatibility(self):
        """Test TypeInfo creation and compatibility checking."""
        # Create type infos
        int_type = create_type_info('integer')
        str_type = create_type_info('string')
        auto_type = create_type_info('auto')
        
        # Test same type compatibility
        self.assertTrue(check_type_compatibility(int_type, int_type))
        
        # Test auto type compatibility (auto accepts anything)
        self.assertTrue(check_type_compatibility(auto_type, int_type))
        self.assertTrue(check_type_compatibility(int_type, auto_type))
        
        # Test incompatible types
        self.assertFalse(check_type_compatibility(int_type, str_type))

    def test_type_info_invalid_types(self):
        """Test TypeInfo with invalid types."""
        with self.assertRaises(ValueError):
            create_type_info('invalid_type')

    def test_error_collector_operations(self):
        """Test ErrorCollector functionality."""
        collector = ErrorCollector()
        
        # Test initial state
        self.assertFalse(collector.has_errors())
        self.assertFalse(collector.has_warnings())
        
        # Add error
        error = SemanticError("Test error")
        collector.add_error(error)
        
        self.assertTrue(collector.has_errors())
        self.assertEqual(len(collector.errors), 1)
        
        # Add warning
        collector.add_warning("Test warning", line_number=5)
        self.assertTrue(collector.has_warnings())
        self.assertEqual(len(collector.warnings), 1)
        
        # Test summary
        summary = collector.get_error_summary()
        self.assertEqual(summary['total_errors'], 1)
        self.assertEqual(summary['total_warnings'], 1)
        self.assertTrue(summary['has_errors'])
        
        # Test clear
        collector.clear()
        self.assertFalse(collector.has_errors())
        self.assertFalse(collector.has_warnings())

class TestSemanticAnalyzerCore(unittest.TestCase):
    """Test suite for semantic analyzer core components."""

    def setUp(self):
        """Set up test fixtures."""
        self.symbol_table = SymbolTable()
        self.error_collector = ErrorCollector()
        self.type_resolver = ExpressionTypeResolver(self.symbol_table)
        
        self.vocabulary = {'types': {'integer', 'string', 'boolean', 'auto'}}
        self.validation_engine = ValidationEngine(
            self.symbol_table, self.type_resolver, self.error_collector, self.vocabulary
        )
        self.symbol_manager = SymbolDefinitionManager(self.symbol_table, self.error_collector)

    def test_expression_type_resolver(self):
        """Test ExpressionTypeResolver functionality."""
        # Test with mock constant node
        mock_number = MockConstantNode(value=42)
        
        # This would need actual implementation to work
        # For now, test that it doesn't crash
        result = self.type_resolver.get_expression_type(mock_number)
        # Result might be None for mock nodes, that's okay
        
        # Test stats
        stats = self.type_resolver.get_resolution_stats()
        self.assertIn('resolution_count', stats)
        self.assertIn('cached_types', stats)

    def test_validation_engine_type_validation(self):
        """Test ValidationEngine type validation."""
        mock_decl = MockVariableDeclNode(name="test", var_type="integer")
        
        # Test valid type
        self.validation_engine.validate_variable_type(mock_decl)
        self.assertFalse(self.error_collector.has_errors())
        
        # Test invalid type
        mock_decl_invalid = MockVariableDeclNode(name="test", var_type="invalid_type")
        self.validation_engine.validate_variable_type(mock_decl_invalid)
        self.assertTrue(self.error_collector.has_errors())

    def test_symbol_definition_manager(self):
        """Test SymbolDefinitionManager functionality."""
        mock_decl = MockVariableDeclNode(name="test_var", var_type="integer")
        
        # Test symbol definition
        success = self.symbol_manager.define_variable_symbol(mock_decl, "integer")
        self.assertTrue(success)
        
        # Test redefinition (should fail)
        success2 = self.symbol_manager.define_variable_symbol(mock_decl, "integer")
        self.assertFalse(success2)
        self.assertTrue(self.error_collector.has_errors())

if __name__ == '__main__':
    unittest.main()