"""
BDD Step Definitions for Parser Features
=======================================

Implements the step definitions for parser-related BDD scenarios.
"""

import pytest
from pytest_bdd import scenarios, given, when, then, parsers
import time
import tracemalloc
from pathlib import Path

# Add project root to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.tau_translator_omega.core_engine.cnl_parser.mock_parser import MockCNLParser
from src.tau_translator_omega.core_engine.cnl_parser.ast_nodes import (
    SentenceNode, FactNode, PredicateCallNode, ConstantNode
)

# Load parser feature scenarios
scenarios('../features/parser/parser_behavior.feature')


# Fixtures
@pytest.fixture
def parser_context():
    """Context object to store parser state."""
    return {
        'parser': None,
        'input': None,
        'tokens': [],
        'ast': None,
        'error': None,
        'parse_time': 0,
        'memory_usage': 0,
        'grammar_rules': {}
    }


# Background steps
@given('the CNL parser is initialized')
def initialize_parser(parser_context):
    """Initialize the CNL parser."""
    parser_context['parser'] = MockCNLParser(debug=False)


@given('the grammar rules are loaded')
def load_grammar_rules(parser_context):
    """Load grammar rules for parsing."""
    parser_context['grammar_rules'] = {
        'sentence': 'fact PERIOD',
        'fact': 'predicate_call | constant | comparison',
        'predicate_call': 'IDENTIFIER LPAREN arg_list RPAREN',
        'comparison': 'expr OPERATOR expr',
        'operators': ['=', '!=', '<', '>', '<=', '>='],
        'keywords': ['and', 'or', 'not', 'xor']
    }


# Input steps
@given(parsers.parse('I have input text "{input_text}"'))
def set_input_text(parser_context, input_text):
    """Set input text for parsing."""
    parser_context['input'] = input_text


@given('I have a complex expression with 100 nested operations')
def set_complex_expression(parser_context):
    """Generate complex nested expression for performance testing."""
    # Build deeply nested expression: ((((x))))...
    expr = "x"
    for i in range(100):
        if i % 2 == 0:
            expr = f"({expr} and y{i})"
        else:
            expr = f"({expr} or z{i})"
    
    parser_context['input'] = expr + "."


# Action steps
@when('I parse the input')
def parse_input(parser_context):
    """Parse the input text."""
    tracemalloc.start()
    start_time = time.time()
    
    try:
        parser_context['ast'] = parser_context['parser'].parse(parser_context['input'])
        parser_context['error'] = None
    except Exception as e:
        parser_context['ast'] = None
        parser_context['error'] = str(e)
    
    parser_context['parse_time'] = (time.time() - start_time) * 1000  # milliseconds
    
    current, peak = tracemalloc.get_traced_memory()
    parser_context['memory_usage'] = peak / (1024 * 1024)  # MB
    tracemalloc.stop()


@when('I tokenize the input')
def tokenize_input(parser_context):
    """Tokenize the input text."""
    try:
        tokens = parser_context['parser'].tokenize(parser_context['input'])
        parser_context['tokens'] = tokens
        parser_context['error'] = None
    except Exception as e:
        parser_context['tokens'] = []
        parser_context['error'] = str(e)


# Verification steps
@then('parsing should succeed')
def verify_parsing_succeeds(parser_context):
    """Verify parsing completed successfully."""
    assert parser_context['ast'] is not None, \
        f"Parsing failed: {parser_context['error']}"
    assert parser_context['error'] is None


@then('parsing should fail')
def verify_parsing_fails(parser_context):
    """Verify parsing failed as expected."""
    assert parser_context['ast'] is None, \
        "Parsing should have failed but succeeded"
    assert parser_context['error'] is not None


@then('the AST root should be a SentenceNode')
def verify_ast_root_type(parser_context):
    """Verify AST root node type."""
    assert isinstance(parser_context['ast'], SentenceNode), \
        f"Expected SentenceNode, got {type(parser_context['ast'])}"


@then('the sentence content should be a FactNode')
def verify_sentence_content_type(parser_context):
    """Verify sentence content node type."""
    assert hasattr(parser_context['ast'], 'content'), \
        "AST root should have content attribute"
    assert isinstance(parser_context['ast'].content, FactNode), \
        f"Expected FactNode, got {type(parser_context['ast'].content)}"


@then(parsers.parse('the error should mention "{error_text}"'))
def verify_error_mentions(parser_context, error_text):
    """Verify error message contains expected text."""
    assert parser_context['error'] is not None, "No error recorded"
    assert error_text.lower() in parser_context['error'].lower(), \
        f"Error should mention '{error_text}', got: {parser_context['error']}"


@then(parsers.parse('the error should indicate position {position:d}'))
def verify_error_position(parser_context, position):
    """Verify error indicates correct position."""
    # This would require enhanced error reporting in the parser
    # For now, check if position is mentioned in error
    assert str(position) in parser_context['error'] or \
           f"position {position}" in parser_context['error'].lower(), \
        f"Error should indicate position {position}"


# Token verification steps
@then('I should get tokens:')
def verify_tokens_table(parser_context, datatable):
    """Verify tokenization produces expected tokens."""
    expected_tokens = []
    for row in datatable:
        expected_tokens.append({
            'type': row['type'],
            'value': row['value'],
            'position': int(row['position'])
        })
    
    assert len(parser_context['tokens']) == len(expected_tokens), \
        f"Expected {len(expected_tokens)} tokens, got {len(parser_context['tokens'])}"
    
    for i, (actual, expected) in enumerate(zip(parser_context['tokens'], expected_tokens)):
        assert actual[0] == expected['type'], \
            f"Token {i}: expected type '{expected['type']}', got '{actual[0]}'"
        assert actual[1] == expected['value'], \
            f"Token {i}: expected value '{expected['value']}', got '{actual[1]}'"
        assert actual[2] == expected['position'], \
            f"Token {i}: expected position {expected['position']}, got {actual[2]}"


# AST verification steps
@then('the AST should contain:')
def verify_ast_contains(parser_context, datatable):
    """Verify AST contains expected nodes and properties."""
    ast = parser_context['ast']
    
    for row in datatable:
        node_type = row['node_type']
        property_path = row['property']
        expected_value = row['value']
        
        # Navigate AST to find nodes of specified type
        nodes = find_nodes_by_type(ast, node_type)
        assert nodes, f"No {node_type} found in AST"
        
        # Check property on first matching node
        node = nodes[0]
        actual_value = get_node_property(node, property_path)
        
        assert str(actual_value) == expected_value, \
            f"{node_type}.{property_path} should be '{expected_value}', got '{actual_value}'"


def find_nodes_by_type(node, node_type):
    """Recursively find all nodes of given type in AST."""
    nodes = []
    
    if node.__class__.__name__ == node_type:
        nodes.append(node)
    
    # Recursively search child nodes
    for attr_name in dir(node):
        if not attr_name.startswith('_'):
            attr = getattr(node, attr_name)
            if hasattr(attr, '__class__'):
                nodes.extend(find_nodes_by_type(attr, node_type))
            elif isinstance(attr, list):
                for item in attr:
                    if hasattr(item, '__class__'):
                        nodes.extend(find_nodes_by_type(item, node_type))
    
    return nodes


def get_node_property(node, property_path):
    """Get property value from node using dot/bracket notation."""
    parts = property_path.replace('[', '.').replace(']', '').split('.')
    value = node
    
    for part in parts:
        if part.isdigit():
            value = value[int(part)]
        else:
            value = getattr(value, part)
    
    return value


# Performance verification steps
@then(parsers.parse('parsing should complete within {max_time:d} milliseconds'))
def verify_parse_time(parser_context, max_time):
    """Verify parsing completes within time limit."""
    assert parser_context['parse_time'] <= max_time, \
        f"Parsing took {parser_context['parse_time']:.1f}ms, expected <= {max_time}ms"


@then(parsers.parse('memory usage should be under {max_memory:d} MB'))
def verify_memory_usage(parser_context, max_memory):
    """Verify memory usage stays within limit."""
    assert parser_context['memory_usage'] <= max_memory, \
        f"Memory usage was {parser_context['memory_usage']:.1f}MB, expected <= {max_memory}MB"


# Grammar verification steps
@then(parsers.parse('parsing should {result}'))
def verify_parsing_result(parser_context, result):
    """Verify parsing result (succeed/fail)."""
    if result == 'succeed':
        verify_parsing_succeeds(parser_context)
    else:
        verify_parsing_fails(parser_context)


@then(parsers.parse('the main construct should be "{construct}"'))
def verify_main_construct(parser_context, construct):
    """Verify the main grammatical construct identified."""
    if not parser_context['ast']:
        pytest.fail("No AST to verify construct")
    
    # Map construct names to expected node types
    construct_map = {
        'constant': ConstantNode,
        'comparison': 'ComparisonNode',
        'predicate': PredicateCallNode,
        'list': 'ListNode',
        'set_builder': 'SetBuilderNode',
        'logical_negation': 'NegationNode'
    }
    
    expected_type = construct_map.get(construct, construct)
    
    # Check the main content node type
    content = parser_context['ast'].content
    if hasattr(content, 'statement'):
        content = content.statement
    
    actual_type = type(content).__name__ if not isinstance(expected_type, str) else content.__class__.__name__
    
    assert actual_type == expected_type or isinstance(content, expected_type), \
        f"Expected {expected_type}, got {actual_type}"