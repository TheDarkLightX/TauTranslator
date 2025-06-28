# Tau REPL and Solver Findings

This document summarizes the key findings from our intensive, data-driven analysis of the Tau toolchain (v0.7.0-alpha) when processing piped `.tau` script files.

## 1. Canonical Scripting Syntax

Through iterative testing, we have determined a set of strict rules required for writing `.tau` scripts that are correctly parsed by the REPL:

- **No Trailing Periods:** Definition lines using the `:=` operator must *not* end with a period. The REPL adds these interactively, but they are syntax errors in scripts.
- **No Comments or Blank Lines:** Scripts must be pure code. Comments (`#`) and blank lines cause the REPL's line-buffered parser to fail or crash.
- **Declarative Definitions Only:** The `:=` operator is for defining Boolean predicates, not for assigning the results of equations. A line like `p():=q()=F` is invalid.
- **Pure Logical Conjunctions:** To verify a state, one must define a predicate as a conjunction of other predicates or their negations. The `&` operator cannot conjoin equations.
  - **Correct:** `correct():=(p())'&q()&r()`
  - **Incorrect:** `correct():=p()=F&q()=T&r()=T`
- **Postfix Negation:** The negation operator is postfix (e.g., `p()'`).
- **No Arithmetic in Indices:** Predicate indices do not support arithmetic (e.g., `c[i+1]()` is invalid). Logic must be unrolled explicitly.

## 2. Solver Instability (v0.7.0-alpha)

Our primary finding is that the `solve` command, while syntactically correct, causes the Tau REPL to crash with a segmentation fault (`exit code 139`) on even moderately complex, composed predicates.

- **Test Case:** A 4-bit ripple-carry adder, defined using the canonical syntax above, parses correctly but crashes the solver.
- **Diagnostic Test:** A simpler 2-bit ripple-carry adder, using the exact same syntax, also crashes the solver.

**Conclusion:** The crash is not due to the complexity of the 4-bit adder, but is a runtime bug within the `solve` command's implementation in this alpha version of Tau when dealing with composed predicates. Our generated specifications are syntactically valid but expose instability in the underlying toolchain.
