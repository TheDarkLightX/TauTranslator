"""
Micro unit tests for EBNF AST nodes.
Tests every single node type, method, and property individually.
Following TDD principles - test first, implement after.
"""

import pytest
from tau_translator_omega.core_engine.ebnf_parser.ebnf_ast_nodes import (
    EBNFNode, GrammarNode, RuleNode, ChoiceNode, SequenceNode,
    TerminalNode, NonTerminalNode, OptionalNode, RepetitionNode,
    GroupNode, LiteralNode, RegexNode, ExpressionNode,
    create_choice, create_sequence, EBNFVisitor
)


class TestEBNFNodeBase:
    """Test the base EBNFNode class."""
    
    def test_ebnf_node_is_abstract(self):
        """Test that EBNFNode cannot be instantiated directly."""
        with pytest.raises(TypeError):
            EBNFNode()
    
    def test_ebnf_node_has_slots(self):
        """Test that EBNFNode uses __slots__ for memory optimization."""
        assert hasattr(EBNFNode, '__slots__')
        assert EBNFNode.__slots__ == ()
    
    def test_ebnf_node_has_accept_method(self):
        """Test that EBNFNode defines abstract accept method."""
        assert hasattr(EBNFNode, 'accept')
        # Abstract method should exist but not be callable on base class


class TestGrammarNode:
    """Test GrammarNode - root of EBNF AST."""
    
    def test_grammar_node_creation_empty(self):
        """Test creating GrammarNode with empty rules list."""
        node = GrammarNode(rules=[])
        assert node.rules == []
        assert isinstance(node.rules, list)
    
    def test_grammar_node_creation_with_rules(self):
        """Test creating GrammarNode with rule list."""
        rule1 = RuleNode(name="test", expression=LiteralNode(value="hello"))
        rule2 = RuleNode(name="test2", expression=LiteralNode(value="world"))
        
        node = GrammarNode(rules=[rule1, rule2])
        assert len(node.rules) == 2
        assert node.rules[0] == rule1
        assert node.rules[1] == rule2
    
    def test_grammar_node_has_slots(self):
        """Test GrammarNode uses __slots__ for memory optimization."""
        assert hasattr(GrammarNode, '__slots__')
        assert GrammarNode.__slots__ == ('rules',)
    
    def test_grammar_node_repr(self):
        """Test GrammarNode string representation."""
        node = GrammarNode(rules=[])
        repr_str = repr(node)
        assert "GrammarNode" in repr_str
        assert "rules=0" in repr_str
        
        # With rules
        rule = RuleNode(name="test", expression=LiteralNode(value="hello"))
        node = GrammarNode(rules=[rule])
        repr_str = repr(node)
        assert "rules=1" in repr_str
    
    def test_grammar_node_accept_method(self):
        """Test GrammarNode accept method exists."""
        node = GrammarNode(rules=[])
        assert hasattr(node, 'accept')
        assert callable(node.accept)


class TestRuleNode:
    """Test RuleNode - individual EBNF rule."""
    
    def test_rule_node_creation(self):
        """Test creating RuleNode with name and expression."""
        expr = LiteralNode(value="test")
        node = RuleNode(name="my_rule", expression=expr)
        
        assert node.name == "my_rule"
        assert node.expression == expr
        assert isinstance(node.name, str)
    
    def test_rule_node_has_slots(self):
        """Test RuleNode uses __slots__ for memory optimization."""
        assert hasattr(RuleNode, '__slots__')
        assert RuleNode.__slots__ == ('name', 'expression')
    
    def test_rule_node_repr(self):
        """Test RuleNode string representation."""
        expr = LiteralNode(value="test")
        node = RuleNode(name="my_rule", expression=expr)
        repr_str = repr(node)
        assert "RuleNode" in repr_str
        assert "my_rule" in repr_str
    
    def test_rule_node_accept_method(self):
        """Test RuleNode accept method exists."""
        expr = LiteralNode(value="test")
        node = RuleNode(name="test", expression=expr)
        assert hasattr(node, 'accept')
        assert callable(node.accept)


class TestChoiceNode:
    """Test ChoiceNode - represents A | B | C."""
    
    def test_choice_node_creation_empty(self):
        """Test creating ChoiceNode with empty alternatives."""
        node = ChoiceNode(alternatives=[])
        assert node.alternatives == []
        assert isinstance(node.alternatives, list)
    
    def test_choice_node_creation_with_alternatives(self):
        """Test creating ChoiceNode with alternatives."""
        alt1 = LiteralNode(value="a")
        alt2 = LiteralNode(value="b")
        
        node = ChoiceNode(alternatives=[alt1, alt2])
        assert len(node.alternatives) == 2
        assert node.alternatives[0] == alt1
        assert node.alternatives[1] == alt2
    
    def test_choice_node_has_slots(self):
        """Test ChoiceNode uses __slots__ for memory optimization."""
        assert hasattr(ChoiceNode, '__slots__')
        assert ChoiceNode.__slots__ == ('alternatives',)
    
    def test_choice_node_repr(self):
        """Test ChoiceNode string representation."""
        node = ChoiceNode(alternatives=[])
        repr_str = repr(node)
        assert "ChoiceNode" in repr_str
        assert "alternatives=0" in repr_str
        
        # With alternatives
        alt = LiteralNode(value="test")
        node = ChoiceNode(alternatives=[alt])
        repr_str = repr(node)
        assert "alternatives=1" in repr_str
    
    def test_choice_node_is_expression_node(self):
        """Test ChoiceNode inherits from ExpressionNode."""
        node = ChoiceNode(alternatives=[])
        assert isinstance(node, ExpressionNode)


class TestSequenceNode:
    """Test SequenceNode - represents A B C."""
    
    def test_sequence_node_creation_empty(self):
        """Test creating SequenceNode with empty elements."""
        node = SequenceNode(elements=[])
        assert node.elements == []
        assert isinstance(node.elements, list)
    
    def test_sequence_node_creation_with_elements(self):
        """Test creating SequenceNode with elements."""
        elem1 = LiteralNode(value="a")
        elem2 = LiteralNode(value="b")
        
        node = SequenceNode(elements=[elem1, elem2])
        assert len(node.elements) == 2
        assert node.elements[0] == elem1
        assert node.elements[1] == elem2
    
    def test_sequence_node_has_slots(self):
        """Test SequenceNode uses __slots__ for memory optimization."""
        assert hasattr(SequenceNode, '__slots__')
        assert SequenceNode.__slots__ == ('elements',)
    
    def test_sequence_node_repr(self):
        """Test SequenceNode string representation."""
        node = SequenceNode(elements=[])
        repr_str = repr(node)
        assert "SequenceNode" in repr_str
        assert "elements=0" in repr_str
    
    def test_sequence_node_is_expression_node(self):
        """Test SequenceNode inherits from ExpressionNode."""
        node = SequenceNode(elements=[])
        assert isinstance(node, ExpressionNode)


class TestOptionalNode:
    """Test OptionalNode - represents [A] or A?."""
    
    def test_optional_node_creation(self):
        """Test creating OptionalNode with expression."""
        expr = LiteralNode(value="test")
        node = OptionalNode(expression=expr)
        
        assert node.expression == expr
    
    def test_optional_node_has_slots(self):
        """Test OptionalNode uses __slots__ for memory optimization."""
        assert hasattr(OptionalNode, '__slots__')
        assert OptionalNode.__slots__ == ('expression',)
    
    def test_optional_node_repr(self):
        """Test OptionalNode string representation."""
        expr = LiteralNode(value="test")
        node = OptionalNode(expression=expr)
        repr_str = repr(node)
        assert "OptionalNode" in repr_str
        assert "LiteralNode" in repr_str
    
    def test_optional_node_is_expression_node(self):
        """Test OptionalNode inherits from ExpressionNode."""
        expr = LiteralNode(value="test")
        node = OptionalNode(expression=expr)
        assert isinstance(node, ExpressionNode)


class TestRepetitionNode:
    """Test RepetitionNode - represents {A}, A*, A+."""
    
    def test_repetition_node_creation_defaults(self):
        """Test creating RepetitionNode with default values."""
        expr = LiteralNode(value="test")
        node = RepetitionNode(expression=expr)
        
        assert node.expression == expr
        assert node.min_count == 0
        assert node.max_count is None
    
    def test_repetition_node_creation_with_counts(self):
        """Test creating RepetitionNode with specific counts."""
        expr = LiteralNode(value="test")
        node = RepetitionNode(expression=expr, min_count=1, max_count=5)
        
        assert node.expression == expr
        assert node.min_count == 1
        assert node.max_count == 5
    
    def test_repetition_node_has_slots(self):
        """Test RepetitionNode uses __slots__ for memory optimization."""
        assert hasattr(RepetitionNode, '__slots__')
        assert RepetitionNode.__slots__ == ('expression', 'min_count', 'max_count')
    
    def test_repetition_node_repr(self):
        """Test RepetitionNode string representation."""
        expr = LiteralNode(value="test")
        node = RepetitionNode(expression=expr, min_count=1, max_count=3)
        repr_str = repr(node)
        assert "RepetitionNode" in repr_str
        assert "1-3" in repr_str
    
    def test_repetition_node_is_expression_node(self):
        """Test RepetitionNode inherits from ExpressionNode."""
        expr = LiteralNode(value="test")
        node = RepetitionNode(expression=expr)
        assert isinstance(node, ExpressionNode)


class TestGroupNode:
    """Test GroupNode - represents (A B C)."""
    
    def test_group_node_creation(self):
        """Test creating GroupNode with expression."""
        expr = LiteralNode(value="test")
        node = GroupNode(expression=expr)
        
        assert node.expression == expr
    
    def test_group_node_has_slots(self):
        """Test GroupNode uses __slots__ for memory optimization."""
        assert hasattr(GroupNode, '__slots__')
        assert GroupNode.__slots__ == ('expression',)
    
    def test_group_node_repr(self):
        """Test GroupNode string representation."""
        expr = LiteralNode(value="test")
        node = GroupNode(expression=expr)
        repr_str = repr(node)
        assert "GroupNode" in repr_str
        assert "LiteralNode" in repr_str
    
    def test_group_node_is_expression_node(self):
        """Test GroupNode inherits from ExpressionNode."""
        expr = LiteralNode(value="test")
        node = GroupNode(expression=expr)
        assert isinstance(node, ExpressionNode)


class TestLiteralNode:
    """Test LiteralNode - represents "string" or 'string'."""
    
    def test_literal_node_creation_defaults(self):
        """Test creating LiteralNode with default quote type."""
        node = LiteralNode(value="hello")
        
        assert node.value == "hello"
        assert node.quote_type == '"'
    
    def test_literal_node_creation_with_quote_type(self):
        """Test creating LiteralNode with specific quote type."""
        node = LiteralNode(value="hello", quote_type="'")
        
        assert node.value == "hello"
        assert node.quote_type == "'"
    
    def test_literal_node_has_slots(self):
        """Test LiteralNode uses __slots__ for memory optimization."""
        assert hasattr(LiteralNode, '__slots__')
        assert LiteralNode.__slots__ == ('value', 'quote_type')
    
    def test_literal_node_repr(self):
        """Test LiteralNode string representation."""
        node = LiteralNode(value="hello", quote_type='"')
        repr_str = repr(node)
        assert "LiteralNode" in repr_str
        assert '"hello"' in repr_str
    
    def test_literal_node_is_terminal_node(self):
        """Test LiteralNode inherits from TerminalNode."""
        node = LiteralNode(value="test")
        assert isinstance(node, TerminalNode)
        assert isinstance(node, ExpressionNode)


class TestRegexNode:
    """Test RegexNode - represents /pattern/flags."""
    
    def test_regex_node_creation_defaults(self):
        """Test creating RegexNode with default flags."""
        node = RegexNode(pattern="[a-z]+")
        
        assert node.pattern == "[a-z]+"
        assert node.flags == ""
    
    def test_regex_node_creation_with_flags(self):
        """Test creating RegexNode with flags."""
        node = RegexNode(pattern="[a-z]+", flags="i")
        
        assert node.pattern == "[a-z]+"
        assert node.flags == "i"
    
    def test_regex_node_has_slots(self):
        """Test RegexNode uses __slots__ for memory optimization."""
        assert hasattr(RegexNode, '__slots__')
        assert RegexNode.__slots__ == ('pattern', 'flags')
    
    def test_regex_node_repr(self):
        """Test RegexNode string representation."""
        node = RegexNode(pattern="[a-z]+", flags="i")
        repr_str = repr(node)
        assert "RegexNode" in repr_str
        assert "/[a-z]+/i" in repr_str
    
    def test_regex_node_is_terminal_node(self):
        """Test RegexNode inherits from TerminalNode."""
        node = RegexNode(pattern="test")
        assert isinstance(node, TerminalNode)
        assert isinstance(node, ExpressionNode)


class TestNonTerminalNode:
    """Test NonTerminalNode - represents rule_name."""
    
    def test_nonterminal_node_creation(self):
        """Test creating NonTerminalNode with name."""
        node = NonTerminalNode(name="my_rule")
        
        assert node.name == "my_rule"
        assert isinstance(node.name, str)
    
    def test_nonterminal_node_has_slots(self):
        """Test NonTerminalNode uses __slots__ for memory optimization."""
        assert hasattr(NonTerminalNode, '__slots__')
        assert NonTerminalNode.__slots__ == ('name',)
    
    def test_nonterminal_node_repr(self):
        """Test NonTerminalNode string representation."""
        node = NonTerminalNode(name="my_rule")
        repr_str = repr(node)
        assert "NonTerminalNode" in repr_str
        assert "my_rule" in repr_str
    
    def test_nonterminal_node_is_expression_node(self):
        """Test NonTerminalNode inherits from ExpressionNode."""
        node = NonTerminalNode(name="test")
        assert isinstance(node, ExpressionNode)


class TestUtilityFunctions:
    """Test utility functions for AST manipulation."""
    
    def test_create_choice_single_alternative(self):
        """Test create_choice with single alternative returns the alternative."""
        alt = LiteralNode(value="test")
        result = create_choice(alt)
        
        assert result == alt
        assert not isinstance(result, ChoiceNode)
    
    def test_create_choice_multiple_alternatives(self):
        """Test create_choice with multiple alternatives creates ChoiceNode."""
        alt1 = LiteralNode(value="a")
        alt2 = LiteralNode(value="b")
        result = create_choice(alt1, alt2)
        
        assert isinstance(result, ChoiceNode)
        assert len(result.alternatives) == 2
        assert result.alternatives[0] == alt1
        assert result.alternatives[1] == alt2
    
    def test_create_choice_flattens_nested_choices(self):
        """Test create_choice flattens nested ChoiceNode instances."""
        alt1 = LiteralNode(value="a")
        alt2 = LiteralNode(value="b")
        alt3 = LiteralNode(value="c")
        
        nested_choice = ChoiceNode(alternatives=[alt1, alt2])
        result = create_choice(nested_choice, alt3)
        
        assert isinstance(result, ChoiceNode)
        assert len(result.alternatives) == 3
        assert result.alternatives[0] == alt1
        assert result.alternatives[1] == alt2
        assert result.alternatives[2] == alt3
    
    def test_create_sequence_single_element(self):
        """Test create_sequence with single element returns the element."""
        elem = LiteralNode(value="test")
        result = create_sequence(elem)
        
        assert result == elem
        assert not isinstance(result, SequenceNode)
    
    def test_create_sequence_multiple_elements(self):
        """Test create_sequence with multiple elements creates SequenceNode."""
        elem1 = LiteralNode(value="a")
        elem2 = LiteralNode(value="b")
        result = create_sequence(elem1, elem2)
        
        assert isinstance(result, SequenceNode)
        assert len(result.elements) == 2
        assert result.elements[0] == elem1
        assert result.elements[1] == elem2
    
    def test_create_sequence_flattens_nested_sequences(self):
        """Test create_sequence flattens nested SequenceNode instances."""
        elem1 = LiteralNode(value="a")
        elem2 = LiteralNode(value="b")
        elem3 = LiteralNode(value="c")
        
        nested_sequence = SequenceNode(elements=[elem1, elem2])
        result = create_sequence(nested_sequence, elem3)
        
        assert isinstance(result, SequenceNode)
        assert len(result.elements) == 3
        assert result.elements[0] == elem1
        assert result.elements[1] == elem2
        assert result.elements[2] == elem3


class TestEBNFVisitor:
    """Test EBNFVisitor abstract base class."""
    
    def test_ebnf_visitor_is_abstract(self):
        """Test that EBNFVisitor cannot be instantiated directly."""
        with pytest.raises(TypeError):
            EBNFVisitor()
    
    def test_ebnf_visitor_has_all_visit_methods(self):
        """Test that EBNFVisitor defines all required visit methods."""
        required_methods = [
            'visit_grammar', 'visit_rule', 'visit_choice', 'visit_sequence',
            'visit_optional', 'visit_repetition', 'visit_group', 'visit_literal',
            'visit_regex', 'visit_nonterminal'
        ]
        
        for method_name in required_methods:
            assert hasattr(EBNFVisitor, method_name)
            method = getattr(EBNFVisitor, method_name)
            assert callable(method)
