import unittest
from tau_translator_omega.core_engine.semantic.semantic_analyzer import SemanticAnalyzer, SemanticError
from tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes import (
    SentenceNode, VariableDeclNode, VariableNode, AssignmentNode, ConstantNode
)

class TestAnalyzerUsage(unittest.TestCase):

    def setUp(self):
        self.default_vocabulary = {
            'types': set(['integer', 'string', 'boolean', 'auto']),
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

    def test_declare_and_use_variable_ok(self):
        # AST: let x: integer; x = 10;
        node = SentenceNode(content=[
            VariableDeclNode(name='x', var_type='integer', value=None, line=1, column=4),
            AssignmentNode(target=VariableNode(name='x', line=2, column=0),
                           expression=ConstantNode(value=10, value_type='integer', line=2, column=4),
                           line=2, column=2)
        ], line=1, column=0)
        processed_node, errors = self.analyzer.analyze(node)
        self.assertNoError(errors)

    def test_use_undeclared_variable(self):
        # AST: x = 10;
        node = SentenceNode(content=[
            AssignmentNode(target=VariableNode(name='x', line=1, column=0),
                           expression=ConstantNode(value=10, value_type='integer', line=1, column=4),
                           line=1, column=2)
        ], line=1, column=0)
        processed_node, errors = self.analyzer.analyze(node)
        self.assertHasError(errors, "Variable 'x' not declared")

if __name__ == '__main__':
    unittest.main()
