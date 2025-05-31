# Translation Pipeline Architecture
==================================

## Overview

The system implements a multi-stage translation pipeline:

```
Natural Language → TCE → AST → Tau Code
```

## Stage 1: Natural Language to TCE

**Input**: Plain English text that humans write naturally
**Output**: TCE (Tau Controlled English) - a structured subset of English

Examples:
- "Whenever x is greater than zero, the function of x must equal one"
  → "Always x greater than 0 implies f(x) equals 1."

- "There must be some y where Q holds for y"
  → "There exists y such that Q(y)."

## Stage 2: TCE to AST (Abstract Syntax Tree)

**Input**: TCE text
**Parser**: Lark-based parser using TCE grammar
**Output**: AST nodes representing the logical structure

The AST serves as the **Intermediate Logic Representation**.

Example AST for "Always x and y.":
```
SentenceNode(
  content=FactNode(
    statement=BooleanBinaryOpNode(
      operator='and',
      left=VariableNode(name='x'),
      right=VariableNode(name='y')
    )
  )
)
```

## Stage 3: AST to Tau Code

**Input**: AST (the intermediate representation)
**Translator**: TCETauTranslator
**Output**: Formal Tau language code

The translator walks the AST and generates corresponding Tau syntax:
- `BooleanBinaryOpNode(op='and')` → `&`
- `QuantifierBlockNode(type='forall')` → `forall x :`
- `TemporalNode(op='always')` → `always`

## Why AST as Intermediate Logic?

1. **Structure Preservation**: AST captures the logical structure independent of surface syntax
2. **Type Safety**: Each node has a specific type (Boolean, Arithmetic, Temporal, etc.)
3. **Validation**: Can validate logical consistency before translation
4. **Extensibility**: Easy to add new node types for new language features
5. **Bidirectional**: Can potentially generate TCE back from AST

## Key AST Node Types

### Expression Nodes
- **BooleanBinaryOpNode**: and, or, implies, iff
- **ArithmeticBinaryOpNode**: +, -, *, /, >, <, =
- **QuantifierBlockNode**: forall, exists
- **TemporalNode**: always, sometimes, until

### Atomic Nodes
- **VariableNode**: x, y, z
- **ConstantNode**: numbers, strings, booleans
- **PredicateCallNode**: f(x), P(x,y)
- **StreamReferenceNode**: x@t, input s

### Structure Nodes
- **SentenceNode**: Top-level wrapper
- **FactNode**: Statements of fact
- **RuleNode**: If-then rules
- **DefinitionNode**: Function/predicate definitions

## Example: Complex Translation

**Natural Language**: 
"For every time point, if x is true at that time, then x must also be true at the next time"

**TCE**:
"For all t such that x at time t implies x at time t+1."

**AST** (simplified):
```
QuantifierBlockNode(
  type='forall',
  variables=[VariableNode('t')],
  condition=BooleanBinaryOpNode(
    operator='implies',
    left=StreamReferenceNode(name='x', time='t'),
    right=StreamReferenceNode(name='x', time='t+1')
  )
)
```

**Tau Output**:
```
forall t : (x@t -> x@(t+1))
```

## Current Implementation Status

### ✅ Working
- TCE parser (using Lark grammar)
- AST node definitions
- Basic TCE to Tau translation
- Pattern-based fallback

### 🚧 Partially Working
- Complex temporal expressions
- Nested quantifiers
- Stream operations

### ❌ Not Implemented
- Tau to AST parsing (for reverse translation)
- Full grammar integration from loaded files
- Semantic validation of AST

## Benefits of This Architecture

1. **Separation of Concerns**: Each stage has a single responsibility
2. **Debugging**: Can inspect AST to understand translation
3. **Flexibility**: Can swap parsers or translators independently
4. **Formal Verification**: AST can be analyzed for logical properties
5. **Error Messages**: Can provide precise error locations in AST