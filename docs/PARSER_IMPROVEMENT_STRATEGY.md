# Parser Improvement Strategy - Ultra Planning

## Deep Thinking Analysis

### Core Problem Decomposition

The parser failures reveal a fundamental architectural issue: we're trying to handle complex linguistic transformations with simple pattern matching. This is like trying to parse a programming language with only regex - it works for simple cases but fails at complexity boundaries.

### Philosophical Approach

Instead of patching individual failures, we need to think about the parser as a **semantic transformation pipeline** with distinct phases:

1. **Linguistic Analysis** → 2. **Semantic Extraction** → 3. **Formal Representation** → 4. **Notation Generation**

## Strategic Architecture

### Phase 1: Linguistic Preprocessing Layer

```python
class LinguisticPreprocessor:
    """
    Handles morphology, tokenization, and linguistic normalization.
    Uses NLTK or spaCy for robust linguistic analysis.
    """
    
    def singularize_nouns(self, text: str) -> str:
        """Convert plural nouns to singular for predicate formation."""
        pass
    
    def normalize_numbers(self, text: str) -> str:
        """Convert 'one', 'two' etc. to digits."""
        pass
    
    def expand_contractions(self, text: str) -> str:
        """Expand don't → do not, etc."""
        pass
```

**Key Insight**: Separate linguistic concerns from semantic parsing.

### Phase 2: Mathematical Expression Parser

```python
class MathematicalExpressionParser:
    """
    Dedicated parser for mathematical expressions using proper parsing techniques.
    Handles nested expressions, operators, and time indices.
    """
    
    def parse_time_expression(self, expr: str) -> TimeExpression:
        """Parse 't minus 1' → TimeOffset(base='t', offset=-1)"""
        pass
    
    def parse_arithmetic(self, expr: str) -> ArithmeticAST:
        """Parse complex arithmetic into AST."""
        pass
```

**Key Insight**: Mathematical expressions need their own parser with proper precedence handling.

### Phase 3: Semantic Graph Builder

```python
class SemanticGraphBuilder:
    """
    Builds a semantic graph representation before generating notation.
    This intermediate representation captures all relationships.
    """
    
    def build_from_parse_tree(self, tree: ParseTree) -> SemanticGraph:
        """Convert parse tree to semantic graph."""
        pass
    
    def resolve_all_references(self, graph: SemanticGraph) -> SemanticGraph:
        """Complete pronoun and reference resolution on graph."""
        pass
```

**Key Insight**: An intermediate representation allows multiple passes for resolution and optimization.

### Phase 4: Context-Aware Notation Generator

```python
class NotationGenerator:
    """
    Generates consistent notation based on context.
    Maintains notation standards across all output.
    """
    
    def generate_stream_notation(self, stream: Stream) -> str:
        """Always produces consistent oN[t] notation."""
        pass
    
    def generate_logical_notation(self, expr: LogicalExpr) -> str:
        """Consistent logical operator notation."""
        pass
```

**Key Insight**: Notation generation should be centralized and consistent.

## Implementation Strategy

### Step 1: Create Robust Test Infrastructure (Week 1)

1. **Test Data Structure**
   ```python
   @dataclass
   class ParserTestCase:
       input_text: str
       expected_output: str
       expected_ast: Optional[AST]
       linguistic_features: List[str]
       semantic_features: List[str]
   ```

2. **Test Categories**
   - Linguistic edge cases (pluralization, contractions)
   - Mathematical expressions (nested, complex operators)
   - Temporal expressions (time offsets, ranges)
   - Coreference chains (pronouns, definite articles)
   - Notation consistency (all contexts)

### Step 2: Implement Core Components (Week 2-3)

1. **Mathematical Expression Parser**
   - Use pyparsing or Lark for proper grammar-based parsing
   - Support full arithmetic expressions
   - Handle time index expressions specially

2. **Enhanced Coreference Resolver**
   ```python
   class EnhancedCoreferenceResolver:
       def __init__(self):
           self.pronoun_rules = {
               'it': self._resolve_it_pronoun,
               'they': self._resolve_they_pronoun,
               'them': self._resolve_them_pronoun
           }
       
       def _resolve_it_pronoun(self, context: ParseContext) -> str:
           # Find nearest singular noun entity
           pass
   ```

3. **Linguistic Normalizer**
   - Integrate inflect library for singularization
   - Build number word converter
   - Create contraction expander

### Step 3: Refactor Existing Parser (Week 4)

1. **Modularize Pattern Matching**
   ```python
   class PatternModule:
       def can_handle(self, text: str) -> bool:
           pass
       
       def parse(self, text: str, context: ParseContext) -> ParseResult:
           pass
   
   class QuantifierPatternModule(PatternModule):
       # Handles "all X are Y", "every X who Y"
       pass
   
   class TemporalPatternModule(PatternModule):
       # Handles "always", "eventually", time expressions
       pass
   ```

2. **Pipeline Architecture**
   ```python
   class EnhancedTCEParserV2:
       def __init__(self):
           self.pipeline = [
               LinguisticPreprocessor(),
               MathematicalExpressionParser(),
               PatternBasedParser(),
               SemanticGraphBuilder(),
               ReferenceResolver(),
               NotationGenerator()
           ]
       
       def parse(self, text: str) -> str:
           result = text
           context = ParseContext()
           
           for stage in self.pipeline:
               result = stage.process(result, context)
           
           return result
   ```

### Step 4: Incremental Migration (Week 5)

1. **Parallel Implementation**
   - Keep existing parser working
   - Implement new components alongside
   - A/B test on test suite

2. **Feature Flags**
   ```python
   class ParserConfig:
       use_mathematical_parser = True
       use_enhanced_coreference = True
       use_linguistic_preprocessing = True
   ```

3. **Gradual Rollout**
   - Start with mathematical expressions
   - Add linguistic preprocessing
   - Enable enhanced coreference
   - Switch to new notation generator

## Algorithm Selection

### For Mathematical Expressions
- **Recursive Descent Parser**: Clean, understandable, handles precedence well
- **Pratt Parser**: Excellent for operator precedence
- **Parser Combinator**: Composable, testable

### For Coreference Resolution
- **Rule-Based System**: Start simple, handles pronouns
- **Recency-Based**: Most recent compatible entity
- **Type-Checking**: Ensure semantic compatibility

### For Notation Generation
- **Template-Based**: Consistent, maintainable
- **Visitor Pattern**: Walk semantic graph, generate notation
- **Strategy Pattern**: Different strategies per context

## Design Patterns

1. **Pipeline Pattern**: For overall architecture
2. **Strategy Pattern**: For context-specific parsing
3. **Visitor Pattern**: For AST/graph traversal
4. **Factory Pattern**: For creating parse modules
5. **Builder Pattern**: For complex object construction

## Quality Metrics

1. **Test Coverage**: 95% for all components
2. **Cyclomatic Complexity**: ≤ 10 per method
3. **Performance**: < 100ms for typical sentences
4. **Accuracy**: 90%+ on test suite
5. **Consistency**: 100% notation consistency

## Risk Mitigation

1. **Backward Compatibility**: Keep old parser available
2. **Incremental Testing**: Test each component in isolation
3. **Performance Monitoring**: Track parsing speed
4. **Error Recovery**: Graceful fallbacks
5. **Documentation**: Comprehensive examples

## Timeline

- **Week 1**: Test infrastructure and analysis
- **Week 2-3**: Core component implementation
- **Week 4**: Parser refactoring
- **Week 5**: Integration and migration
- **Week 6**: Testing and optimization

## Success Criteria

1. All identified test failures pass
2. No regression in existing functionality
3. Performance within acceptable bounds
4. Code quality metrics met
5. Documentation complete

## Conclusion

This strategy addresses the root causes of parser failures through architectural improvements rather than patches. By separating concerns, using appropriate algorithms, and maintaining consistency, we can build a robust parser capable of handling complex natural language specifications.