"""
Hybrid Parser - Combines Earley parsing with gradient descent learning
Uses formal grammar as baseline with neural adaptation for edge cases.

Copyright: DarkLightX / Dana Edwards
"""

from typing import Dict, List, Optional, Union, Tuple, Any
from dataclasses import dataclass
import logging

from backend.unified.core.gradient_descent_parser import GradientDescentParser
from backend.unified.core.plugin_system import LearningPlugin, PluginMetadata, PluginType, ParseContext
from .domain_types import Result, Success, Failure, AppError


@dataclass
class Grammar:
    """Simple context-free grammar for TCE."""
    rules: Dict[str, List[List[str]]]
    terminals: Dict[str, str]


@dataclass
class EarleyItem:
    """Item in Earley chart."""
    rule: str
    production: List[str] 
    dot_position: int
    start_position: int
    
    @property
    def is_complete(self) -> bool:
        return self.dot_position >= len(self.production)
    
    @property
    def next_symbol(self) -> Optional[str]:
        if self.is_complete:
            return None
        return self.production[self.dot_position]


# === PURE EARLEY FUNCTIONS (CC=1 each) ===

def create_tce_grammar() -> Grammar:
    """Create TCE context-free grammar."""
    rules = {
        'S': [
            ['QUANTIFIED_STATEMENT'],
            ['TEMPORAL_STATEMENT'],
            ['MODAL_STATEMENT'],
            ['SIMPLE_STATEMENT']
        ],
        'QUANTIFIED_STATEMENT': [
            ['QUANTIFIER', 'ENTITY', 'PREDICATE']
        ],
        'TEMPORAL_STATEMENT': [
            ['TEMPORAL_WORD', 'CLAUSE', 'COMMA', 'CLAUSE']
        ],
        'MODAL_STATEMENT': [
            ['ENTITY', 'MODAL', 'ACTION']
        ],
        'SIMPLE_STATEMENT': [
            ['ENTITY', 'VERB', 'ENTITY']
        ]
    }
    
    terminals = {
        'QUANTIFIER': r'\b(all|every|some|many|few)\b',
        'ENTITY': r'\b[a-zA-Z_][a-zA-Z0-9_]*\b',
        'PREDICATE': r'\b[a-zA-Z_][a-zA-Z0-9_\s]*\b',
        'TEMPORAL_WORD': r'\b(when|while|before|after|during)\b',
        'MODAL': r'\b(must|should|can|may|might)\b',
        'VERB': r'\b(is|are|owns|drives|has)\b',
        'ACTION': r'\b[a-zA-Z_][a-zA-Z0-9_\s]*\b',
        'CLAUSE': r'[^,]+',
        'COMMA': r','
    }
    
    return Grammar(rules=rules, terminals=terminals)


def create_earley_item(rule: str, production: List[str], dot_pos: int, start_pos: int) -> EarleyItem:
    """Create Earley parser item."""
    return EarleyItem(
        rule=rule,
        production=production,
        dot_position=dot_pos,
        start_position=start_pos
    )


def predict_operation(item: EarleyItem, grammar: Grammar, chart_column: List[EarleyItem]):
    """Earley predict operation."""
    next_sym = item.next_symbol
    if next_sym and next_sym in grammar.rules:
        add_predicted_items(next_sym, grammar, chart_column, len(chart_column))


def add_predicted_items(symbol: str, grammar: Grammar, chart_column: List[EarleyItem], position: int):
    """Add predicted items to chart."""
    for production in grammar.rules[symbol]:
        new_item = create_earley_item(symbol, production, 0, position)
        add_item_if_new(chart_column, new_item)


def add_item_if_new(chart_column: List[EarleyItem], item: EarleyItem):
    """Add item to chart if not already present."""
    if not any(items_equal(existing, item) for existing in chart_column):
        chart_column.append(item)


def items_equal(item1: EarleyItem, item2: EarleyItem) -> bool:
    """Check if two Earley items are equal."""
    return (item1.rule == item2.rule and 
            item1.production == item2.production and
            item1.dot_position == item2.dot_position and
            item1.start_position == item2.start_position)


def scan_operation(item: EarleyItem, token: str, grammar: Grammar, next_column: List[EarleyItem]):
    """Earley scan operation."""
    next_sym = item.next_symbol
    if next_sym and token_matches_terminal(token, next_sym, grammar):
        scanned_item = create_earley_item(
            item.rule,
            item.production,
            item.dot_position + 1,
            item.start_position
        )
        add_item_if_new(next_column, scanned_item)


def token_matches_terminal(token: str, terminal: str, grammar: Grammar) -> bool:
    """Check if token matches terminal pattern."""
    if terminal not in grammar.terminals:
        return False
    
    import re
    pattern = grammar.terminals[terminal]
    return bool(re.match(pattern, token, re.IGNORECASE))


def complete_operation(completed_item: EarleyItem, chart: List[List[EarleyItem]], column_index: int):
    """Earley complete operation."""
    start_column = chart[completed_item.start_position]
    
    for item in start_column:
        if (not item.is_complete and 
            item.next_symbol == completed_item.rule):
            completed = create_earley_item(
                item.rule,
                item.production,
                item.dot_position + 1,
                item.start_position
            )
            add_item_if_new(chart[column_index], completed)


def check_parse_success(final_column: List[EarleyItem]) -> bool:
    """Check if parsing was successful."""
    return any(item.rule == 'S' and item.is_complete and item.start_position == 0 
              for item in final_column)


def simple_earley_parse(tokens: List[str], grammar: Grammar) -> bool:
    """Simple Earley parser implementation."""
    chart = initialize_earley_chart(tokens, grammar)
    
    for i in range(len(chart)):
        process_chart_column(chart, i, tokens, grammar)
    
    return check_parse_success(chart[-1])


def initialize_earley_chart(tokens: List[str], grammar: Grammar) -> List[List[EarleyItem]]:
    """Initialize Earley chart."""
    chart = [[] for _ in range(len(tokens) + 1)]
    
    # Add start item
    start_item = create_earley_item('START', ['S'], 0, 0)
    chart[0].append(start_item)
    
    return chart


def process_chart_column(chart: List[List[EarleyItem]], column_index: int, tokens: List[str], grammar: Grammar):
    """Process single chart column."""
    column = chart[column_index]
    i = 0
    
    while i < len(column):
        item = column[i]
        
        if item.is_complete:
            complete_operation(item, chart, column_index)
        elif item.next_symbol in grammar.rules:
            predict_operation(item, grammar, column)
        elif column_index < len(tokens):
            scan_operation(item, tokens[column_index], grammar, chart[column_index + 1])
        
        i += 1


class SimpleEarleyParser:
    """Simple Earley parser for TCE."""
    
    def __init__(self):
        """Initialize Earley parser."""
        self.grammar = create_tce_grammar()
        self.logger = logging.getLogger(__name__)
    
    def parse(self, text: str) -> bool:
        """Parse text using Earley algorithm."""
        tokens = tokenize_text(text)
        return simple_earley_parse(tokens, self.grammar)
    
    def can_parse(self, text: str) -> bool:
        """Check if text can be parsed."""
        return self.parse(text)


def tokenize_text(text: str) -> List[str]:
    """Simple tokenization."""
    import re
    return re.findall(r'\w+|[,.]', text.lower())


class HybridEarleyGradientParser(LearningPlugin):
    """
    Hybrid parser combining Earley formal parsing with gradient descent learning.
    Uses Earley for structure validation, gradient descent for adaptation.
    """
    
    def __init__(self):
        """Initialize hybrid parser."""
        metadata = PluginMetadata(
            name="hybrid_earley_gradient",
            version="1.0.0",
            plugin_type=PluginType.LEARNING,
            priority=85,
            description="Hybrid Earley + gradient descent parser"
        )
        super().__init__(metadata)
        
        self.earley_parser = SimpleEarleyParser()
        self.gradient_parser = GradientDescentParser()
        self.agreement_threshold = 0.8
        self.adaptation_rate = 0.1
    
    def can_handle(self, text: str, context: ParseContext) -> bool:
        """Hybrid parser can handle any text."""
        return True
    
    def process(self, text: str, context: ParseContext) -> Result[str]:
        """Process using hybrid approach."""
        return hybrid_parse_text(text, self.earley_parser, self.gradient_parser)
    
    def learn_from_correction(self, original: str, corrected: str, feedback: str):
        """Learn using gradient descent component."""
        self.gradient_parser.learn_from_correction(original, corrected, feedback)
    
    def predict_corrections(self, text: str) -> List[str]:
        """Predict corrections using both parsers."""
        return hybrid_predict_corrections(text, self.earley_parser, self.gradient_parser)
    
    def get_adaptation_suggestions(self, text: str) -> List[str]:
        """Get adaptation suggestions."""
        return hybrid_adaptation_suggestions(text, self.earley_parser, self.gradient_parser)
    
    def get_parser_agreement(self, text: str) -> float:
        """Get agreement between parsers."""
        return calculate_parser_agreement(text, self.earley_parser, self.gradient_parser)


# === HYBRID PROCESSING FUNCTIONS ===

def hybrid_parse_text(text: str, earley: SimpleEarleyParser, gradient: GradientDescentParser) -> Result[str]:
    """Parse using hybrid approach."""
    earley_result = earley.can_parse(text)
    context = ParseContext(original_text=text, preprocessed_text=text)
    gradient_result = gradient.process(text, context)
    
    return combine_parsing_results(text, earley_result, gradient_result)


def combine_parsing_results(text: str, earley_success: bool, gradient_result: Result) -> Result[str]:
    """Combine results from both parsers."""
    if earley_success and isinstance(gradient_result, Success):
        return Success(f"hybrid_agreed({gradient_result.unwrap()})")
    elif earley_success:
        return Success(f"earley_formal({text})")
    elif isinstance(gradient_result, Success):
        return Success(f"gradient_adaptive({gradient_result.unwrap()})")
    else:
        return gradient_result


def hybrid_predict_corrections(text: str, earley: SimpleEarleyParser, gradient: GradientDescentParser) -> List[str]:
    """Predict corrections using both parsers."""
    corrections = []
    
    # Get gradient predictions
    gradient_predictions = gradient.predict_corrections(text)
    corrections.extend(gradient_predictions)
    
    # Add formal grammar suggestions
    if not earley.can_parse(text):
        corrections.append("Try using formal TCE structure: QUANTIFIER ENTITY PREDICATE")
    
    return corrections[:5]  # Return top 5


def hybrid_adaptation_suggestions(text: str, earley: SimpleEarleyParser, gradient: GradientDescentParser) -> List[str]:
    """Get hybrid adaptation suggestions."""
    suggestions = []
    
    # Get gradient suggestions
    gradient_suggestions = gradient.get_adaptation_suggestions(text)
    suggestions.extend(gradient_suggestions)
    
    # Add formal grammar suggestions
    agreement = calculate_parser_agreement(text, earley, gradient)
    if agreement < 0.5:
        suggestions.append("Consider using more formal sentence structure")
    
    return suggestions


def calculate_parser_agreement(text: str, earley: SimpleEarleyParser, gradient: GradientDescentParser) -> float:
    """Calculate agreement between parsers."""
    earley_success = earley.can_parse(text)
    
    context = ParseContext(original_text=text, preprocessed_text=text)
    gradient_result = gradient.process(text, context)
    gradient_success = isinstance(gradient_result, Success)
    
    if earley_success == gradient_success:
        return 1.0 if earley_success else 0.3  # Both agree
    else:
        return 0.5  # Disagreement


def create_hybrid_parser() -> HybridEarleyGradientParser:
    """Create hybrid parser instance."""
    return HybridEarleyGradientParser()