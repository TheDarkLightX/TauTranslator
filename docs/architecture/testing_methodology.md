# Testing Methodology for Mathematical and Algorithmic Components

This document formalizes best practices and our concrete approach to testing lattice logic (FDL), Formal Concept Analysis (FCA), and AST-driven transformations.

## Principles
- Property-Based Testing (PBT): specify invariants/laws; generate diverse inputs.
- Metamorphic Testing: define transformations that yield predictable output relations when an oracle is hard.
- Model-Based Testing: use a simple reference model to check the implementation.
- Algebraic Law Verification: assert identities (associativity, absorption, distributivity) over randomized samples.
- Mutation Testing (lightweight): locally mutate operators and ensure tests fail.
- Differential Testing: cross-check multiple implementations or paths.

References (state of the art): Property-based testing patterns and law checks; metamorphic and model-based testing for algorithmic systems.

## Application to This Codebase

### Finite Distributive Lattice (FDL)
- Laws: commutativity, associativity, idempotence, absorption, distributivity.
- Model: bitset OR/AND correspond to join/meet. Tests compare operations to model and verify algebraic laws.
- Roundtrip: encode_bitset → decode_bitset → encode_bitset ⊆ original.

### Formal Concept Analysis (FCA)
- Closure: idempotence (B'' = B''), monotonicity (B ⊆ C ⇒ B'' ⊆ C'').
- Implications: U → V iff V ⊆ closure(U). Tests assert soundness of generated implications.
- Metamorphic: duplicating an object does not change closures; renaming attributes without changing incidence leaves closures invariant.

### Spec→Prompt AST
- Structure preservation: implication “if … then …”, boolean “and/or”, negation “do not …”, and quantifiers “for every/there exists” appear in English emission for canonical inputs.
- Future: property tests over generated formulae families (implication chains, nested quantifiers).

## Test Files
- `tests/unit/test_fdl_laws.py`: algebraic laws and bitset roundtrip.
- `tests/unit/test_fca_closure_implications.py`: closure properties, implication soundness.
- `tests/unit/test_spec_to_prompt_ast_properties.py`: English emission preserves logical structure.

## Running
Use the project venv:

```bash
python -m pytest -q
```

Increase exploration depth for PBT by running tests with higher iterations (via environment flags in future Hypothesis integration).

## Future Work
- Add Hypothesis generators for random contexts and ASTs.
- Add mutation-testing automation.
- Add differential tests comparing alternative FCA algorithms.
