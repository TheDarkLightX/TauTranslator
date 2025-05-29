import unittest
from src.tau_translator_omega.core_engine.semantic_analyzer import SemanticAnalyzer, SemanticError
from src.tau_translator_omega.core_engine.cnl_parser.ast_nodes import (
    SentenceNode, VariableDeclNode, ConstantNode
)

class TestAnalyzerDeclarations(unittest.TestCase):

    def setUp(self):
        self.default_vocabulary = {
            'types': set(['integer', 'string', 'boolean', 'custom_type', 'any', 'auto']),
            'predicates': {},
            'functions': {}
        }
        self.analyzer = SemanticAnalyzer(vocabulary=self.default_vocabulary)

    def assertHasError(self, errors, message_substring, node_name=None):
        found = False
        for error in errors:
            if message_substring in error.message:
                if node_name and node_name in error.message:
                    found = True
                    break
                elif not node_name:
                    found = True
                    break
        self.assertTrue(found, f"Expected error containing '{message_substring}'" + (f" for node '{node_name}'" if node_name else "") + f" but got errors: {[str(e) for e in errors]}")

    def assertNoError(self, errors, message_substring=""):
        if not message_substring:
            self.assertEqual(len(errors), 0, f"Expected no errors, but got: {[str(e) for e in errors]}")
            return
        
        found = False
        for error in errors:
            if message_substring in error.message:
                found = True
                break
        self.assertFalse(found, f"Expected no error containing '{message_substring}', but got: {[str(e) for e in errors]}")

    def test_declare_variable_ok(self):
        # AST: let x: integer;
        node = SentenceNode(content=[
            VariableDeclNode(name='x', var_type='integer', value=None, line=1, column=4) 
        ], line=1, column=0)
        processed_node, errors = self.analyzer.analyze(node)
        self.assertNoError(errors)

    def test_redeclare_variable_in_same_scope(self):
        # AST: let x: integer; let x: string;
        node = SentenceNode(content=[
            VariableDeclNode(name='x', var_type='integer', value=None, line=1, column=4),
            VariableDeclNode(name='x', var_type='string', value=None, line=2, column=4) 
        ], line=1, column=0) 
        processed_node, errors = self.analyzer.analyze(node)
        self.assertHasError(errors, "Variable 'x' already declared in this scope")

    def test_declare_variable_unknown_type(self):
        # AST: let x: foobar;
        node = SentenceNode(content=[
            VariableDeclNode(name='x', var_type='foobar', value=None, line=1, column=4)
        ], line=1, column=0)
        processed_node, errors = self.analyzer.analyze(node)
        self.assertHasError(errors, "Type 'foobar' is not defined in the vocabulary")

    def test_declare_variable_with_auto_type_ok(self):
        # AST: let x: auto = 10;
        node = SentenceNode(content=[
            VariableDeclNode(name='x', var_type='auto', 
                             value=ConstantNode(value=10, value_type='integer', line=1, column=15),
                             line=1, column=4)
        ], line=1, column=0)
        processed_node, errors = self.analyzer.analyze(node)
        self.assertNoError(errors, "Type 'auto' is not defined")

if __name__ == '__main__':
    unittest.main()
