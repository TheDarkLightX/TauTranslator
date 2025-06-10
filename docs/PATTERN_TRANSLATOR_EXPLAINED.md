# Pattern Translator: A Deep Dive

## Overview: The Language Alchemist

Imagine a skilled alchemist who transforms base metals into gold. The Pattern Translator is our linguistic alchemist, transforming human-readable expressions into formal logic and back again. It uses pattern matching rules - like recipe cards - to perform these transformations systematically.

**File**: `backend/unified/translators/pattern_translator.py`  
**Purpose**: Simple pattern-based translation engine that serves as a fallback when more sophisticated methods aren't available  
**Architecture**: Follows the Intentional Disclosure Principle with clean separation of concerns

---

## The Cast of Characters (Data Classes)

### PatternRule: The Recipe Card
```python
@dataclass
class PatternRule:
    """Represents a single translation pattern rule."""
    pattern: Pattern[str]
    replacement: str
    description: str
```

Think of `PatternRule` as a recipe card in our alchemist's collection:
- **pattern**: The ingredient to look for (regex pattern)
- **replacement**: What to transform it into
- **description**: Notes about what this transformation does

### PatternSet: The Recipe Book
```python
@dataclass 
class PatternSet:
    """Collection of pattern rules for a specific direction."""
    direction: TranslationDirection
    rules: List[PatternRule]
```

`PatternSet` is like a recipe book for a specific type of transformation:
- **direction**: Whether we're cooking TCE→Tau or Tau→TCE
- **rules**: The collection of recipe cards to use

---

## The Main Alchemist: PatternTranslationEngine

### Birth of an Alchemist (Initialization)
```python
def __init__(self) -> None:
    """Initialize pattern translation engine with predefined rule sets."""
    super().__init__(
        name="pattern_based",
        description="Simple pattern-based translation with regex rules"
    )
    
    # Initialize pattern sets following Rule 2: Orchestrator pattern
    self._pattern_sets = self._initialize_pattern_sets()
```

**The Metaphor**: When our alchemist sets up their workshop, they:
1. Inherit the tools from the master craftsman (`super().__init__`)
2. Label their workshop with name and purpose
3. Organize their recipe books (`_initialize_pattern_sets()`)

### The Capability Check
```python
def can_translate(self, text: SourceText, direction: TranslationDirection) -> bool:
    """Determine if engine can handle the requested translation."""
    # Rule 2: High-level orchestration
    return (
        self._validate_input_text(text) and
        self._is_direction_supported(direction)
    )
```

**The Metaphor**: Before accepting a commission, the alchemist checks:
- Is the material suitable for transformation? (`_validate_input_text`)
- Do I have the right recipe book? (`_is_direction_supported`)

### The Synchronous Bridge
```python
def translate(self, text: str, direction: TranslationDirection, **kwargs) -> TranslationResult:
    """Implementation of abstract translate method from base class."""
    # Since translate_text_with_patterns_async is async, we need to run it synchronously
    import asyncio
    
    async def _translate():
        return await self.translate_text_with_patterns_async(
            SourceText(text), direction, **kwargs
        )
    
    # Run async method in sync context
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If we're already in an async context, create a task
            task = asyncio.create_task(_translate())
            result = asyncio.run_until_complete(task)
        else:
            result = loop.run_until_complete(_translate())
    except RuntimeError:
        # No event loop, create one
        result = asyncio.run(_translate())
```

**The Metaphor**: This is like having a modern electric workshop (async) but needing to work with traditional hand tools (sync). The method creates an adapter:
- Checks if the power is already on (`loop.is_running()`)
- If yes, plugs into existing power
- If no, starts up a generator
- Converts the electric process to manual output

### The Master Transformation Process
```python
async def translate_text_with_patterns_async(
    self, 
    text: SourceText, 
    direction: TranslationDirection, 
    **kwargs: Dict[str, Any]
) -> Result[BaseTranslationResult]:
    """
    Translate text using pattern matching rules.
    Rule 1: Name explicitly indicates pattern-based operation and async nature.
    Rule 2: Orchestrator pattern for high-level flow.
    """
    start_time = time.time()
    
    # Validate preconditions
    validation_result = self._validate_translation_request(text, direction)
    if isinstance(validation_result, Failure):
        return validation_result
        
    # Select appropriate pattern set
    pattern_set = self._select_pattern_set_for_direction(direction)
    if not pattern_set:
        return Failure(
            error_code="UNSUPPORTED_DIRECTION",
            message=f"Direction {direction.value} not supported"
        )
        
    # Apply translation patterns
    translation_result = self._apply_pattern_rules_to_text(text, pattern_set)
    if isinstance(translation_result, Failure):
        return translation_result
        
    # Post-process and calculate metrics
    cleaned_text = self._clean_translated_text(translation_result.value, direction)
    confidence = self._calculate_translation_confidence(text, cleaned_text)
    
    # Create final result
    return Success(self._create_translation_result(
        original_text=text,
        translated_text=cleaned_text,
        direction=direction,
        confidence=confidence,
        start_time=start_time
    ))
```

**The Grand Orchestration**: This is the alchemist's main ritual, performed in precise steps:

1. **Record the Time** (`start_time`): Note when the transformation begins
2. **Check the Materials** (`_validate_translation_request`): Ensure everything is suitable
3. **Select the Recipe Book** (`_select_pattern_set_for_direction`): Choose TCE→Tau or Tau→TCE recipes
4. **Perform the Transformation** (`_apply_pattern_rules_to_text`): Apply each recipe in sequence
5. **Polish the Result** (`_clean_translated_text`): Remove impurities
6. **Assess Quality** (`_calculate_translation_confidence`): How well did we do?
7. **Package the Gold** (`Success(...)`): Wrap in a success container

---

## The Workshop Tools (Private Methods)

### Creating Recipe Books
```python
def _create_tce_to_tau_patterns(self) -> PatternSet:
    """Create pattern rules for TCE to Tau translation."""
    return PatternSet(
        direction=TranslationDirection.TO_TAU,
        rules=[
            PatternRule(re.compile(r'\band\b'), '&', 'Logical AND operator'),
            PatternRule(re.compile(r'\bor\b'), '|', 'Logical OR operator'),
            PatternRule(re.compile(r'\bnot\b'), '!', 'Logical NOT operator'),
            # ... more rules ...
        ]
    )
```

**The Recipe Collection**: Each rule is like a specific transformation:
- "When you see the word 'and', replace it with '&'"
- "When you see 'divided by', replace it with '/'"
- Word boundaries (`\b`) ensure we don't transform 'hand' into 'h&'

### The Transformation Chamber
```python
def _apply_pattern_rules_to_text(
    self, 
    text: SourceText, 
    pattern_set: PatternSet
) -> Result[TargetText]:
    """Apply pattern rules to transform the text."""
    try:
        result = text
        
        # Apply each rule in sequence
        for rule in pattern_set.rules:
            result = rule.pattern.sub(rule.replacement, result)
            
        return Success(TargetText(result))
        
    except Exception as e:
        return Failure("PATTERN_APPLICATION_ERROR", str(e))
```

**The Alchemical Process**: 
- Start with raw material (`text`)
- Apply each transformation rule in order
- Each rule searches for its pattern and replaces it
- Wrap the final gold in a `Success` container
- If anything explodes, contain it in a `Failure` wrapper

### The Quality Inspector
```python
def _calculate_translation_confidence(
    self, 
    original: SourceText, 
    translated: TargetText
) -> float:
    """Calculate confidence score based on text transformation."""
    if not original or not translated:
        return 0.0
        
    # Simple heuristic: more changes = higher confidence it was translated
    similarity = self._calculate_text_similarity(original, translated)
    return max(0.0, min(1.0, 1.0 - similarity))
```

**The Quality Metaphor**: Like a jeweler examining their work:
- If nothing changed, confidence is low (maybe nothing needed translation?)
- More changes indicate more transformation occurred
- Uses similarity as inverse of confidence

### The Levenshtein Distance Calculator
```python
def _levenshtein_distance(self, s1: str, s2: str) -> int:
    """Calculate Levenshtein distance between two strings."""
    if len(s1) < len(s2):
        return self._levenshtein_distance(s2, s1)
        
    if len(s2) == 0:
        return len(s1)
        
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
        
    return previous_row[-1]
```

**The Distance Metaphor**: Imagine two cities (strings) and you want to find the minimum number of steps to transform one into the other:
- **Insertion**: Adding a new building (character)
- **Deletion**: Demolishing a building
- **Substitution**: Renovating a building into a different type

The algorithm builds a map showing the minimum steps needed at each position, like a city planner calculating the most efficient renovation plan.

---

## Key Design Patterns

### 1. Result Pattern (Railway-Oriented Programming)
Instead of throwing exceptions like grenades, we use `Result[T]` - imagine a train that can take either the Success track or the Failure track. The cargo (data) stays safely contained either way.

### 2. Domain Types (SourceText, TargetText)
Rather than using raw strings everywhere (like shipping everything in unmarked boxes), we use specific types that announce their purpose - SourceText for input, TargetText for output.

### 3. Orchestrator Pattern
The main method (`translate_text_with_patterns_async`) acts like a conductor, calling specialized musicians (private methods) in the right order to create a symphony.

### 4. Separation of Concerns
Each method has one job:
- Validation validates
- Pattern selection selects
- Application applies
- Cleaning cleans

Like a well-organized kitchen where the prep cook preps, the line cook cooks, and the plater plates.

---

## Summary

The Pattern Translator embodies clean architecture principles:
- **Explicit naming** tells you exactly what async methods do
- **Type safety** prevents mixing up source and target text
- **Error handling** uses Result types for predictable failures
- **Single responsibility** keeps each method focused
- **Testability** through pure functions and dependency injection

It's a linguistic alchemist that transforms languages using simple but effective pattern matching, wrapped in a robust architectural framework that makes it reliable, maintainable, and extensible.

Copyright: DarkLightX/Dana Edwards