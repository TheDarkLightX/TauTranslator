# Translation Pipeline (Functional ROP-style)

_This document walks through the end-to-end flow that converts raw English input into Tau Language code.  Every box is a pure function except where noted.  Errors are captured in `Result[T, E]` values per our Railway-Oriented Programming (ROP) policy._

```
User English   ─┐
                ▼
┌─────────────────────────┐ 1. validate_english            (pure)
│ ValidatedEnglish        │─── success / Failure.InvalidInput
└──────────┬──────────────┘
           ▼
┌─────────────────────────┐ 2. english_to_tce              (pure)
│ TauControlledEnglish    │─── maps lexical patterns + synonyms
└──────────┬──────────────┘
           ▼
┌─────────────────────────┐ 3. parse_tce_to_ast            (pure)
│ CNLParser (Pratt) AST   │─── errors → Failure.ParseError
└──────────┬──────────────┘
           ▼
┌─────────────────────────┐ 4. ast_to_tau                  (pure)
│ TauCode                  │─── semantic checks → Failure.SemanticError
└──────────┬──────────────┘
           ▼
┌─────────────────────────┐ 5. postprocess / optimise      (pure)
│ TauCodeOptimised         │─── no side effects
└──────────┬──────────────┘
           ▼
┌─────────────────────────┐ 6. persist_or_respond          (impure)
│ REST API / CLI / GUI     │─── side-effects (I/O)
└─────────────────────────┘
```

## 1. `validate_english`
* Rejects empty or excessively long input.
* Normalises whitespace and ensures terminating period.
* Returns `Result[ValidatedEnglish, InputError]`.

## 2. `english_to_tce`
* Implemented in `EnglishToTauTranslator._english_to_tce`.
* Pure mapping table + regex rewrites.
* Handles temporal adverbs, logical connectors, basic quantifiers.

## 3. `parse_tce_to_ast`
* Calls `CNLParser.parse` (see Grammar Engine doc).
* Pratt parser produces a memory-optimised AST dataclass tree.

## 4. `ast_to_tau`
* `TCETauTranslator.translate` walks the AST via single-dispatch visitors.
* Produces canonical Tau syntax; no side-effects.

## 5. Post-processing
* Constant folding, dead rule elimination.
* Simple pattern: `TauCode -> TauCode` transformer functions.

## 6. Persist / Respond
* REST handler (`/translate`) or CLI prints the Tau.
* Only layer allowed to perform I/O.

---

### Error Railway
Errors propagate on the left rail; at each stage we short-circuit on `Failure`.  This avoids nested `try/except` and keeps every function easily testable.

### Testing Matrix
| Stage | Technique |
|-------|-----------|
| validate | Parametrised unit tests + property-based limits |
| TCE mapping | Golden tests (input → expected Tau) |
| Parser | Snapshot AST vs fixtures; mutation testing |
| Translator | Golden Tau outputs + mutation slated |

---
_Last updated 2025-06-23_
