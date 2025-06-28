"""
Parser Combinators - Composable functional parsing
Enables building complex parsers from simple, reusable components.

Copyright: DarkLightX / Dana Edwards
"""

from typing import Callable, TypeVar, Generic, Optional, List, Union, Tuple, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod
import re

from .domain_types import Result, Success, Failure, AppError
from .error_handling import ParseError


T = TypeVar('T')
U = TypeVar('U')


@dataclass
class ParseState:
    """State of parsing including position and remaining input."""
    input_text: str
    position: int = 0
    
    @property
    def remaining(self) -> str:
        """Get remaining text to parse."""
        return self.input_text[self.position:]
    
    @property
    def is_end(self) -> bool:
        """Check if at end of input."""
        return self.position >= len(self.input_text)


@dataclass
class ParseResult(Generic[T]):
    """Result of a parsing operation."""
    value: T
    new_state: ParseState


class Parser(Generic[T], ABC):
    """Base class for all parsers."""
    
    @abstractmethod
    def parse(self, state: ParseState) -> Result[ParseResult[T], ParseError]:
        """Parse input and return result or error."""
        pass
    
    def map(self, func: Callable[[T], U]) -> 'Parser[U]':
        """Transform successful parse results."""
        return MapParser(self, func)
    
    def flat_map(self, func: Callable[[T], 'Parser[U]']) -> 'Parser[U]':
        """Chain parsers together."""
        return FlatMapParser(self, func)
    
    def or_else(self, other: 'Parser[T]') -> 'Parser[T]':
        """Try this parser, fall back to other on failure."""
        return OrElseParser(self, other)
    
    def optional(self) -> 'Parser[Optional[T]]':
        """Make parser optional."""
        return OptionalParser(self)
    
    def many(self) -> 'Parser[List[T]]':
        """Parse zero or more occurrences."""
        return ManyParser(self)
    
    def many1(self) -> 'Parser[List[T]]':
        """Parse one or more occurrences."""
        return Many1Parser(self)
    
    def separated_by(self, separator: 'Parser[Any]') -> 'Parser[List[T]]':
        """Parse list separated by separator."""
        return SeparatedByParser(self, separator)


# === BASIC PARSER IMPLEMENTATIONS ===

class LiteralParser(Parser[str]):
    """Parser for exact string literals."""
    
    def __init__(self, literal: str):
        self.literal = literal
    
    def parse(self, state: ParseState) -> Result[ParseResult[str], ParseError]:
        return parse_literal(self.literal, state)


class RegexParser(Parser[str]):
    """Parser for regex patterns."""
    
    def __init__(self, pattern: str, flags: int = 0):
        self.pattern = re.compile(pattern, flags)
    
    def parse(self, state: ParseState) -> Result[ParseResult[str], ParseError]:
        return parse_regex(self.pattern, state)


class WhitespaceParser(Parser[str]):
    """Parser for whitespace."""
    
    def parse(self, state: ParseState) -> Result[ParseResult[str], ParseError]:
        return parse_whitespace(state)


class EndOfInputParser(Parser[None]):
    """Parser that succeeds only at end of input."""
    
    def parse(self, state: ParseState) -> Result[ParseResult[None], ParseError]:
        return parse_end_of_input(state)


# === COMBINATOR IMPLEMENTATIONS ===

class MapParser(Parser[U]):
    """Parser that transforms result with function."""
    
    def __init__(self, parser: Parser[T], func: Callable[[T], U]):
        self.parser = parser
        self.func = func
    
    def parse(self, state: ParseState) -> Result[ParseResult[U], ParseError]:
        return parse_with_map(self.parser, self.func, state)


class FlatMapParser(Parser[U]):
    """Parser that chains parsers together."""
    
    def __init__(self, parser: Parser[T], func: Callable[[T], Parser[U]]):
        self.parser = parser
        self.func = func
    
    def parse(self, state: ParseState) -> Result[ParseResult[U], ParseError]:
        return parse_with_flat_map(self.parser, self.func, state)


class OrElseParser(Parser[T]):
    """Parser that tries alternatives."""
    
    def __init__(self, first: Parser[T], second: Parser[T]):
        self.first = first
        self.second = second
    
    def parse(self, state: ParseState) -> Result[ParseResult[T], ParseError]:
        return parse_with_or_else(self.first, self.second, state)


class OptionalParser(Parser[Optional[T]]):
    """Parser that makes result optional."""
    
    def __init__(self, parser: Parser[T]):
        self.parser = parser
    
    def parse(self, state: ParseState) -> Result[ParseResult[Optional[T]], ParseError]:
        return parse_optional(self.parser, state)


class ManyParser(Parser[List[T]]):
    """Parser for zero or more occurrences."""
    
    def __init__(self, parser: Parser[T]):
        self.parser = parser
    
    def parse(self, state: ParseState) -> Result[ParseResult[List[T]], ParseError]:
        return parse_many(self.parser, state)


class Many1Parser(Parser[List[T]]):
    """Parser for one or more occurrences."""
    
    def __init__(self, parser: Parser[T]):
        self.parser = parser
    
    def parse(self, state: ParseState) -> Result[ParseResult[List[T]], ParseError]:
        return parse_many1(self.parser, state)


class SeparatedByParser(Parser[List[T]]):
    """Parser for separated lists."""
    
    def __init__(self, parser: Parser[T], separator: Parser[Any]):
        self.parser = parser
        self.separator = separator
    
    def parse(self, state: ParseState) -> Result[ParseResult[List[T]], ParseError]:
        return parse_separated_by(self.parser, self.separator, state)


class SequenceParser(Parser[List[Any]]):
    """Parser for sequence of parsers."""
    
    def __init__(self, parsers: List[Parser[Any]]):
        self.parsers = parsers
    
    def parse(self, state: ParseState) -> Result[ParseResult[List[Any]], ParseError]:
        return parse_sequence(self.parsers, state)


# === PURE PARSING FUNCTIONS (CC=1 each) ===

def parse_literal(literal: str, state: ParseState) -> Result[ParseResult[str], ParseError]:
    """Parse exact literal string."""
    if state.remaining.startswith(literal):
        return create_success_result(literal, advance_state(state, len(literal)))
    else:
        return create_parse_failure(f"Expected '{literal}' at position {state.position}")


def parse_regex(pattern: re.Pattern, state: ParseState) -> Result[ParseResult[str], ParseError]:
    """Parse regex pattern."""
    match = pattern.match(state.remaining)
    if match:
        matched_text = match.group(0)
        return create_success_result(matched_text, advance_state(state, len(matched_text)))
    else:
        return create_parse_failure(f"Pattern {pattern.pattern} not found at position {state.position}")


def parse_whitespace(state: ParseState) -> Result[ParseResult[str], ParseError]:
    """Parse whitespace characters."""
    whitespace_pattern = re.compile(r'\s*')
    return parse_regex(whitespace_pattern, state)


def parse_end_of_input(state: ParseState) -> Result[ParseResult[None], ParseError]:
    """Parse end of input."""
    if state.is_end:
        return create_success_result(None, state)
    else:
        return create_parse_failure(f"Expected end of input at position {state.position}")


def create_success_result(value: T, new_state: ParseState) -> Result[ParseResult[T], ParseError]:
    """Create successful parse result."""
    return Success(ParseResult(value=value, new_state=new_state))


def create_parse_failure(message: str) -> Result[ParseResult[T], ParseError]:
    """Create parse failure."""
    return Failure(message)


def advance_state(state: ParseState, chars: int) -> ParseState:
    """Advance parse state by given characters."""
    return ParseState(input_text=state.input_text, position=state.position + chars)


def parse_with_map(parser: Parser[T], func: Callable[[T], U], state: ParseState) -> Result[ParseResult[U], ParseError]:
    """Parse with mapping function."""
    result = parser.parse(state)
    if isinstance(result, Success):
        parse_result = result.unwrap()
        transformed_value = func(parse_result.value)
        return create_success_result(transformed_value, parse_result.new_state)
    else:
        return result


def parse_with_flat_map(parser: Parser[T], func: Callable[[T], Parser[U]], state: ParseState) -> Result[ParseResult[U], ParseError]:
    """Parse with flat mapping function."""
    result = parser.parse(state)
    if isinstance(result, Success):
        parse_result = result.unwrap()
        next_parser = func(parse_result.value)
        return next_parser.parse(parse_result.new_state)
    else:
        return result


def parse_with_or_else(first: Parser[T], second: Parser[T], state: ParseState) -> Result[ParseResult[T], ParseError]:
    """Parse with alternative."""
    result = first.parse(state)
    if isinstance(result, Success):
        return result
    else:
        return second.parse(state)


def parse_optional(parser: Parser[T], state: ParseState) -> Result[ParseResult[Optional[T]], ParseError]:
    """Parse optional element."""
    result = parser.parse(state)
    if isinstance(result, Success):
        parse_result = result.unwrap()
        return create_success_result(parse_result.value, parse_result.new_state)
    else:
        return create_success_result(None, state)


def parse_many(parser: Parser[T], state: ParseState) -> Result[ParseResult[List[T]], ParseError]:
    """Parse many occurrences."""
    results = []
    current_state = state
    
    while True:
        result = parser.parse(current_state)
        if isinstance(result, Success):
            parse_result = result.unwrap()
            results.append(parse_result.value)
            current_state = parse_result.new_state
        else:
            break
    
    return create_success_result(results, current_state)


def parse_many1(parser: Parser[T], state: ParseState) -> Result[ParseResult[List[T]], ParseError]:
    """Parse one or more occurrences."""
    first_result = parser.parse(state)
    if isinstance(first_result, Failure):
        return create_parse_failure("Expected at least one occurrence")
    
    first_parse = first_result.unwrap()
    many_result = parse_many(parser, first_parse.new_state)
    
    if isinstance(many_result, Success):
        many_parse = many_result.unwrap()
        all_results = [first_parse.value] + many_parse.value
        return create_success_result(all_results, many_parse.new_state)
    else:
        return many_result


def parse_separated_by(parser: Parser[T], separator: Parser[Any], state: ParseState) -> Result[ParseResult[List[T]], ParseError]:
    """Parse separated list."""
    # Try to parse first element
    first_result = parser.parse(state)
    if isinstance(first_result, Failure):
        return create_success_result([], state)  # Empty list is valid
    
    first_parse = first_result.unwrap()
    results = [first_parse.value]
    current_state = first_parse.new_state
    
    # Parse remaining elements
    while True:
        sep_result = separator.parse(current_state)
        if isinstance(sep_result, Failure):
            break
        
        sep_parse = sep_result.unwrap()
        elem_result = parser.parse(sep_parse.new_state)
        if isinstance(elem_result, Failure):
            break
        
        elem_parse = elem_result.unwrap()
        results.append(elem_parse.value)
        current_state = elem_parse.new_state
    
    return create_success_result(results, current_state)


def parse_sequence(parsers: List[Parser[Any]], state: ParseState) -> Result[ParseResult[List[Any]], ParseError]:
    """Parse sequence of parsers."""
    results = []
    current_state = state
    
    for parser in parsers:
        result = parser.parse(current_state)
        if isinstance(result, Failure):
            return result
        
        parse_result = result.unwrap()
        results.append(parse_result.value)
        current_state = parse_result.new_state
    
    return create_success_result(results, current_state)


# === FACTORY FUNCTIONS ===

def literal(text: str) -> Parser[str]:
    """Create literal parser."""
    return LiteralParser(text)


def regex(pattern: str, flags: int = 0) -> Parser[str]:
    """Create regex parser."""
    return RegexParser(pattern, flags)


def whitespace() -> Parser[str]:
    """Create whitespace parser."""
    return WhitespaceParser()


def end_of_input() -> Parser[None]:
    """Create end-of-input parser."""
    return EndOfInputParser()


def choice(parsers: List[Parser[T]]) -> Parser[T]:
    """Create choice parser from list."""
    if not parsers:
        raise ValueError("Choice requires at least one parser")
    
    result = parsers[0]
    for parser in parsers[1:]:
        result = result.or_else(parser)
    
    return result


def sequence(*parsers: Parser[Any]) -> Parser[List[Any]]:
    """Create sequence parser."""
    return SequenceParser(list(parsers))


def between(open_parser: Parser[Any], close_parser: Parser[Any], content_parser: Parser[T]) -> Parser[T]:
    """Parse content between delimiters."""
    return sequence(open_parser, content_parser, close_parser).map(lambda parts: parts[1])


def surrounded_by(delimiter: Parser[Any], content_parser: Parser[T]) -> Parser[T]:
    """Parse content surrounded by delimiter."""
    return between(delimiter, delimiter, content_parser)


# === TCE-SPECIFIC PARSERS ===

def quantifier_parser() -> Parser[str]:
    """Parse quantifier words."""
    quantifiers = ['all', 'every', 'some', 'many', 'few', 'most', 'several', 'each']
    return choice([literal(q) for q in quantifiers])


def entity_parser() -> Parser[str]:
    """Parse entity names."""
    return regex(r'[a-zA-Z_][a-zA-Z0-9_]*')


def temporal_word_parser() -> Parser[str]:
    """Parse temporal words."""
    temporal_words = ['when', 'while', 'before', 'after', 'during', 'until', 'since']
    return choice([literal(w) for w in temporal_words])


def modal_parser() -> Parser[str]:
    """Parse modal verbs."""
    modals = ['must', 'should', 'can', 'may', 'might', 'could', 'ought', 'will', 'would']
    return choice([literal(m) for m in modals])


def quantified_statement_parser() -> Parser[Tuple[str, str, str]]:
    """Parse quantified statements."""
    return sequence(
        quantifier_parser(),
        whitespace(),
        entity_parser(),
        whitespace(),
        literal('are'),
        whitespace(),
        entity_parser()
    ).map(lambda parts: (parts[0], parts[2], parts[6]))


def temporal_statement_parser() -> Parser[Tuple[str, str]]:
    """Parse temporal statements."""
    return sequence(
        temporal_word_parser(),
        whitespace(),
        regex(r'.+?'),
        literal(','),
        whitespace(),
        regex(r'.+')
    ).map(lambda parts: (parts[2], parts[5]))


def modal_statement_parser() -> Parser[Tuple[str, str, str]]:
    """Parse modal statements."""
    return sequence(
        entity_parser(),
        whitespace(),
        modal_parser(),
        whitespace(),
        regex(r'.+')
    ).map(lambda parts: (parts[0], parts[2], parts[4]))


class TCEParserCombinator:
    """
    TCE parser using combinator approach.
    Enables composable, testable parsing logic.
    """
    
    def __init__(self):
        """Initialize TCE parser combinator."""
        self.main_parser = self._build_main_parser()
    
    def parse(self, text: str) -> Result[str, ParseError]:
        """Parse TCE text using combinators."""
        state = ParseState(input_text=text.strip())
        result = self.main_parser.parse(state)
        
        if isinstance(result, Success):
            parse_result = result.unwrap()
            return Success(self._format_result(parse_result.value))
        else:
            return result
    
    def _build_main_parser(self) -> Parser[Any]:
        """Build main TCE parser."""
        return choice([
            quantified_statement_parser(),
            temporal_statement_parser(),
            modal_statement_parser(),
            regex(r'.+')  # Fallback
        ])
    
    def _format_result(self, parsed_value: Any) -> str:
        """Format parsed result."""
        if isinstance(parsed_value, tuple):
            if len(parsed_value) == 3:
                return f"statement({parsed_value[0]}, {parsed_value[1]}, {parsed_value[2]})"
            elif len(parsed_value) == 2:
                return f"temporal({parsed_value[0]}, {parsed_value[1]})"
        
        return str(parsed_value)


def create_tce_parser_combinator() -> TCEParserCombinator:
    """Create TCE parser combinator instance."""
    return TCEParserCombinator()