# Parser Implementation Plan - Following Intentional Disclosure Principle

## Architecture Overview

Following the IDP principles, we'll create a parser with clear separation of concerns, explicit naming, and transparent data flow.

## Core Domain Types (Rule 3: Maximize Disclosure via Type System)

```python
# core/domain/parser_types.py
from typing import NewType, Union, List, Optional
from dataclasses import dataclass
from enum import Enum

# Domain-specific types instead of primitives
SentenceText = NewType('SentenceText', str)
VariableName = NewType('VariableName', str)
PredicateName = NewType('PredicateName', str)
EntityType = NewType('EntityType', str)
TimeIndex = NewType('TimeIndex', str)

class QuantifierType(Enum):
    UNIVERSAL = "all"
    EXISTENTIAL = "exists"
    NO = "no"
    
class TemporalOperator(Enum):
    ALWAYS = "always"
    EVENTUALLY = "eventually"
    NEVER = "never"

@dataclass
class TimeExpression:
    base: TimeIndex
    offset: Optional[int] = None
    
    def to_notation(self) -> str:
        if self.offset is None:
            return f"[{self.base}]"
        elif self.offset > 0:
            return f"[{self.base}+{self.offset}]"
        else:
            return f"[{self.base}{self.offset}]"

@dataclass
class StreamReference:
    stream_type: str  # "input" or "output"
    stream_number: int
    time: TimeExpression
    
    def to_notation(self) -> str:
        prefix = "i" if self.stream_type == "input" else "o"
        return f"{prefix}{self.stream_number}{self.time.to_notation()}"

# Result types using discriminated unions
@dataclass
class ParseSuccess:
    status: str = "SUCCESS"
    tau_notation: str = ""
    semantic_graph: Optional['SemanticGraph'] = None
    warnings: List[str] = None

@dataclass
class ParseFailure:
    status: str = "FAILURE"
    error_type: str = ""
    error_message: str = ""
    partial_result: Optional[str] = None

ParseResult = Union[ParseSuccess, ParseFailure]
```

## Layer Architecture (Rule 4: Isolate Impurity)

### Core Layer - Pure Logic

```python
# core/parsing/mathematical_expression_parser.py
class MathematicalExpressionParser:
    """Pure parser for mathematical expressions - no I/O, fully deterministic."""
    
    def parse_time_expression_to_ast(self, expr: str) -> TimeExpression:
        """Transforms 't minus 1' -> TimeExpression(base='t', offset=-1)"""
        # Pure parsing logic
        pass
    
    def parse_arithmetic_to_ast(self, expr: str) -> 'ArithmeticAST':
        """Transforms arithmetic expressions to AST"""
        # Pure parsing logic
        pass

# core/parsing/coreference_resolver.py
class CoreferenceResolver:
    """Pure coreference resolution - no I/O, fully deterministic."""
    
    def resolve_pronoun_to_antecedent(
        self, 
        pronoun: str, 
        entities: Dict[VariableName, EntityType]
    ) -> Optional[VariableName]:
        """Resolves 'it' -> nearest compatible entity variable"""
        # Pure resolution logic
        pass

# core/parsing/notation_generator.py
class NotationGenerator:
    """Pure notation generation - no I/O, fully deterministic."""
    
    def generate_quantifier_notation(
        self,
        quantifier: QuantifierType,
        variable: VariableName,
        predicate: PredicateName
    ) -> str:
        """Generates consistent quantifier notation"""
        # Pure generation logic
        pass
```

### Infrastructure Layer - Impure I/O

```python
# infrastructure/linguistic/nltk_preprocessor.py
class NLTKLinguisticPreprocessor:
    """Handles NLTK I/O operations - downloads, model loading, etc."""
    
    def load_models_from_disk_async(self) -> None:
        """Impure: Loads NLTK models from filesystem"""
        pass
    
    def fetch_wordnet_data_async(self, word: str) -> 'WordNetData':
        """Impure: Queries WordNet database"""
        pass

# infrastructure/parsing/lark_grammar_loader.py  
class LarkGrammarLoader:
    """Handles grammar file I/O operations."""
    
    def load_grammar_from_file_async(self, path: str) -> 'LarkGrammar':
        """Impure: Reads grammar file from filesystem"""
        pass
```

### Application Layer - Orchestration

```python
# application/enhanced_tce_parser_v2.py
class EnhancedTCEParserV2:
    """Orchestrates parsing pipeline - Rule 2: Structure for Scannability"""
    
    def __init__(
        self,
        linguistic_preprocessor: ILinguisticPreprocessor,
        math_parser: IMathematicalParser,
        coreference_resolver: ICoreferenceResolver,
        notation_generator: INotationGenerator
    ):
        self._linguistic_preprocessor = linguistic_preprocessor
        self._math_parser = math_parser
        self._coreference_resolver = coreference_resolver
        self._notation_generator = notation_generator
    
    def parse_sentence_to_tau_notation_async(
        self, 
        sentence: SentenceText
    ) -> ParseResult:
        """
        High-level orchestration - Rule 2: Orchestrator pattern.
        Each line delegates to a specific component.
        """
        normalized_text = self._normalize_sentence_text(sentence)
        tokens = self._tokenize_into_segments(normalized_text)
        math_expressions = self._extract_and_parse_mathematical_expressions(tokens)
        semantic_graph = self._build_semantic_graph_from_tokens(tokens, math_expressions)
        resolved_graph = self._resolve_all_coreferences_in_graph(semantic_graph)
        tau_notation = self._generate_tau_notation_from_graph(resolved_graph)
        
        return ParseSuccess(tau_notation=tau_notation, semantic_graph=resolved_graph)
    
    # Private implementation methods - single responsibility each
    def _normalize_sentence_text(self, sentence: SentenceText) -> str:
        """Normalizes text: singularization, expansion, etc."""
        return self._linguistic_preprocessor.normalize_text(sentence)
    
    def _tokenize_into_segments(self, text: str) -> List['Token']:
        """Breaks text into semantic tokens"""
        pass
    
    def _extract_and_parse_mathematical_expressions(
        self, 
        tokens: List['Token']
    ) -> List['MathExpression']:
        """Identifies and parses all mathematical expressions"""
        pass
```

## Implementation Components (Rule 1: Name for Consequence)

```python
# core/parsing/pronoun_resolver.py
class PronounResolver:
    """Resolves pronouns to their antecedents - pure logic."""
    
    def resolve_it_pronoun_to_entity(
        self,
        context_entities: List[Tuple[VariableName, EntityType]],
        pronoun_position: int
    ) -> VariableName:
        """
        Resolves 'it' to nearest singular entity.
        Uses recency and type compatibility.
        """
        # Find most recent singular entity
        for var, entity_type in reversed(context_entities[:pronoun_position]):
            if self._is_singular_entity(entity_type):
                return var
        raise PronounResolutionError("No suitable antecedent for 'it'")
    
    def resolve_they_pronoun_to_entities(
        self,
        context_entities: List[Tuple[VariableName, EntityType]],
        pronoun_position: int  
    ) -> List[VariableName]:
        """Resolves 'they' to nearest plural entity or group"""
        pass

# core/parsing/stream_notation_normalizer.py
class StreamNotationNormalizer:
    """Ensures consistent stream notation - pure transformation."""
    
    def normalize_stream_reference_to_compact_notation(
        self,
        stream_desc: str
    ) -> StreamReference:
        """
        Transforms 'output stream 1 at time t' -> StreamReference
        which generates 'o1[t]'
        """
        # Parse stream description
        stream_type, number, time_expr = self._parse_stream_description(stream_desc)
        time = self._parse_time_expression(time_expr)
        
        return StreamReference(
            stream_type=stream_type,
            stream_number=number,
            time=time
        )

# core/linguistic/singularizer.py
class NounSingularizer:
    """Handles noun singularization - pure transformation."""
    
    def singularize_noun_for_predicate(self, plural_noun: str) -> PredicateName:
        """
        Transforms plural nouns to singular for predicate formation.
        'cats' -> 'cat', 'people' -> 'person'
        """
        # Rule-based singularization
        if plural_noun.endswith('ies'):
            return PredicateName(plural_noun[:-3] + 'y')
        elif plural_noun.endswith('es'):
            return PredicateName(plural_noun[:-2])
        elif plural_noun.endswith('s'):
            return PredicateName(plural_noun[:-1])
        else:
            return PredicateName(plural_noun)
```

## Test Infrastructure

```python
# tests/core/test_mathematical_parser.py
class TestMathematicalExpressionParser:
    """Tests for mathematical expression parsing."""
    
    def test_parse_time_offset_minus(self):
        """Test: 't minus 1' -> TimeExpression(base='t', offset=-1)"""
        parser = MathematicalExpressionParser()
        result = parser.parse_time_expression_to_ast("t minus 1")
        
        assert result.base == "t"
        assert result.offset == -1
        assert result.to_notation() == "[t-1]"
    
    def test_parse_time_offset_plus(self):
        """Test: 't plus 2' -> TimeExpression(base='t', offset=2)"""
        parser = MathematicalExpressionParser()
        result = parser.parse_time_expression_to_ast("t plus 2")
        
        assert result.base == "t"
        assert result.offset == 2
        assert result.to_notation() == "[t+2]"

# tests/core/test_pronoun_resolution.py
class TestPronounResolver:
    """Tests for pronoun resolution."""
    
    def test_resolve_it_to_nearest_singular(self):
        """Test: 'it' resolves to nearest singular entity"""
        resolver = PronounResolver()
        entities = [
            (VariableName("p"), EntityType("person")),
            (VariableName("c"), EntityType("car"))
        ]
        
        result = resolver.resolve_it_pronoun_to_entity(entities, 2)
        assert result == VariableName("c")  # car is nearest
```

## Migration Strategy

1. **Phase 1**: Implement core domain types and pure parsers
2. **Phase 2**: Build infrastructure adapters  
3. **Phase 3**: Create application orchestrator
4. **Phase 4**: Migrate existing tests to new architecture
5. **Phase 5**: Parallel run and validation
6. **Phase 6**: Switch over and deprecate old parser

## Success Metrics

- All methods ≤ 10 lines (IDP compliance)
- Zero primitives in public APIs
- 100% pure/impure separation
- All I/O in infrastructure layer
- Function names reveal consequences
- Type signatures are complete contracts

This implementation plan follows all IDP principles:
- **Rule 1**: Names reveal consequences and async nature
- **Rule 2**: Orchestrator pattern with scannable structure  
- **Rule 3**: Rich type system with no primitives
- **Rule 4**: Clear separation of pure/impure code