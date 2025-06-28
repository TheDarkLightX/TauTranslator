# Grammar Design and Evolution Notes

This document tracks key design decisions and changes made to the TCE Lark grammar (`tce_tau_compatible.lark`) to resolve parsing ambiguities.

## Resolving Ambiguity (2025-06-28)

### Problem 1: `variable` vs. `predicate_name`

*   **Initial State:** The grammar initially had two distinct rules, `variable` and `predicate_name`, which were both defined as a single `IDENTIFIER`. 
*   **Issue:** This created a `Reduce/Reduce` collision because the Lark parser could not determine whether to reduce a token like `X` to a `variable` or a `predicate_name`.
*   **Solution:** The `variable` and `predicate_name` rules were removed. Rules that consumed them (`term`, `atomic_prop`, `variable_list`) were refactored to use the `IDENTIFIER` terminal directly. This simplified the grammar but led to a deeper ambiguity.

### Problem 2: `term` vs. `atomic_prop`

*   **Initial State:** After the first refactor, both the `term` rule (for variables/values) and the `atomic_prop` rule (for propositions) could be reduced from a single `IDENTIFIER`.
*   **Issue:** This created a new `Reduce/Reduce` collision. The parser could not distinguish between a variable `X` (a `term`) and a parameter-less predicate `raining` (an `atomic_prop`).
*   **Solution:** The `atomic_prop` rule was modified to require parentheses. It was changed from `IDENTIFIER [LPAR argument_list RPAR]` (optional parentheses) to `IDENTIFIER LPAR [argument_list] RPAR` (required parentheses). This enforces a clear syntactic distinction: variables are bare identifiers (`X`), while predicates are function-like (`raining()`). This resolves the ambiguity for the parser.

### Problem 3: `term` vs. `boolean_term` for `stream_access`

*   **Initial State:** After the second refactor, a `stream_access` (e.g., `s[t]`) could be parsed as a `term` (a value) or a `boolean_term` (a truth value).
*   **Issue:** This created a `Reduce/Reduce` collision because the parser didn't know how to interpret a standalone `stream_access` inside parentheses.
*   **Solution:** The grammar was made more explicit. `stream_access` was removed from the `boolean_term` rule. A `stream_access` is now only a `term`. To use it in a boolean context, it must be part of a `relation` (e.g., `s[t] = true`). This makes the intended meaning clear from the syntax, resolving the final ambiguity.
