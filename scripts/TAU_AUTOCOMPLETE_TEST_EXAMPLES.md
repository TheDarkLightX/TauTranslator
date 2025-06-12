# TAU AutoComplete Test Examples
===============================

Test the autocomplete functionality with these examples. Type them slowly to see suggestions appear!

## 1. Basic Temporal Logic
Type this in the left editor with "TAU" selected:

```tau
// Test 1: Basic temporal operators
always P(x)
sometimes Q(y)
eventually R(z)
never S(a)
```

**What to expect:**
- When you type "al" → should suggest "always"
- When you type "so" → should suggest "sometimes"
- When you type "ev" → should suggest "eventually"
- When you type "ne" → should suggest "never"

## 2. Quantifiers
```tau
// Test 2: Universal and existential quantifiers
forall x (P(x) -> Q(x))
exists y (R(y) && S(y))
```

**What to expect:**
- When you type "for" → should suggest "forall" and "for every"
- When you type "ex" → should suggest "exists"

## 3. Definitions
```tau
// Test 3: Defining concepts
DEFINE isEven(x) := exists k (x = 2 * k)
DEFINE isOdd(x) := !isEven(x)
```

**What to expect:**
- When you type "DEF" → should suggest "DEFINE"
- When you type ":" → should suggest ":=" (definition operator)

## 4. Logical Operators
```tau
// Test 4: Logical connectives
P(x) && Q(x)
A(y) || B(y)
X -> Y
M <-> N
!Z
```

**What to expect:**
- When you type "-" → should suggest "->" (implication)
- When you type "<" → should suggest "<->" (equivalence)

## 5. Complete Example - Barber Paradox
```tau
// Test 5: The Barber Paradox in TAU
DEFINE shaves(barber, person) := 
  person != barber && !shavesSelf(person)

DEFINE shavesSelf(person) := 
  shaves(person, person)

// The paradox
exists barber forall person (
  shaves(barber, person) <-> !shavesSelf(person)
)
```

## 6. Stream Processing Example
```tau
// Test 6: Stream operations
always (temperature > 30 -> coolingOn)
eventually (pressure < 10 -> alert)
```

## AutoComplete Testing Checklist

### Basic Functionality
- [ ] Type "al" - see "always" suggestion
- [ ] Type "for" - see "forall" suggestion
- [ ] Type "ex" - see "exists" suggestion
- [ ] Type ":" - see ":=" suggestion
- [ ] Type "-" - see "->" suggestion

### Keyboard Navigation
- [ ] Use ↓ arrow to move down in suggestions
- [ ] Use ↑ arrow to move up in suggestions
- [ ] Press Tab or Enter to accept suggestion
- [ ] Press Escape to cancel suggestions

### Language Switching
- [ ] Select "TAU" → autocomplete works
- [ ] Select "CNL" → autocomplete works
- [ ] Select "PLAIN_ENGLISH" → no autocomplete
- [ ] Select "ILR" → no autocomplete

### Performance
- [ ] Type quickly - suggestions debounce (300ms delay)
- [ ] Type slowly - suggestions appear smoothly
- [ ] Large text - no performance issues

## Tips for Testing

1. **Start Simple**: Begin with single keywords like "al", "for", "ex"
2. **Test Operators**: Try typing ":", "-", "<" to see operator suggestions
3. **Check Debouncing**: Type "always" quickly vs slowly
4. **Test Cancellation**: Press Escape while suggestions are shown
5. **Language Switch**: Change from TAU to PLAIN_ENGLISH and back

## Expected Behavior

When autocomplete is working correctly:
1. Suggestions appear ~300ms after you stop typing
2. Only relevant suggestions based on what you typed
3. TAU keywords highlighted in blue
4. Operators highlighted in red
5. Comments in gray (start with //)