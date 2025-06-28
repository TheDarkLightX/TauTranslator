# tests/unit/test_function_definition.py

import unittest
from src.tau_translator_omega.core_engine.parsers.cnl_parser.parser import CNLParser
from src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes import RuleNode, PredicateCallNode, VariableNode, ArithmeticBinaryOpNode, ConstantNode

class TestFunctionDefinition(unittest.TestCase):
    def setUp(self):
        self.parser = CNLParser()

    def test_simple_function_definition(self):
        """Test parsing a simple function definition: 'the definition of f with x is x + 1'"""
        text = "the definition of f with x is x + 1"
        expected_ast = RuleNode(
            head=PredicateCallNode(
                name='f',
                args=[VariableNode(name='x')]
            ),
            body=ArithmeticBinaryOpNode(
                left=VariableNode(name='x'),
                operator='+',
                right=ConstantNode(value=1, value_type='INTEGER')
            )
        )
        
        # This is expected to fail until the grammar and transformer are updated
        ast = self.parser.parse(text)
        
        self.assertEqual(ast, expected_ast, f"AST mismatch for '{text}'")

if __name__ == '__main__':
    unittest.main()
