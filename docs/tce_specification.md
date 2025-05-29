# Tau Controlled English (TCE) Specification

Version: 0.1.0

## 1. Introduction

Tau Controlled English (TCE) is a Controlled Natural Language (CNL) designed to map *deterministically* to the Tau Language. The primary goal of TCE is to allow analysts, developers, or policy authors to write requirements and system specifications in plain English-looking sentences while guaranteeing that:

*   Every well-formed TCE sentence can be compiled into a **single, syntactically-valid Tau clause**.
*   Different TCE sentences will never compile to the *same* Tau formula (no hidden ambiguity).
*   Every operator or construct needed by Tau (Boolean connectives, quantifiers, streams, recursion, pointwise-revision, etc.) has a clear TCE counterpart.

TCE is deliberately based on principles from *Attempto Controlled English (ACE)* and *Common Logic Controlled English (CLCE)* but is specifically tailored for Tau's logic and stream semantics.

This document outlines the design principles, grammar, Tau mapping, and usage of TCE.

## 2. Design Principles

| Principle                             | Rationale for Tau                                                                                                                                                                   |
| ------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **One sentence ⇒ one clause**         | Makes automatic AST ↔ Tau conversion trivial and keeps error reporting human-friendly.                                                                                              |
| **No hidden quantifiers**             | TCE interprets "A `variable`" existentially (if not otherwise quantified) and requires explicit universal quantification. "Every `variable`" maps universally. This ensures quantification is always explicit in CNL and maps to `{ex …}` or `{all …}` in Tau. |
| **Explicit connectives & precedence** | TCE uses the English keywords **and**, **or**, **xor**, **not** that map 1-to-1 onto Tau's `&`, `\\`, `+`, `'`. Parentheses `(` `)` may be used for grouping and *must* be used if the intended precedence differs from Tau’s default (`' > & > + > \\`). |
| **No anaphora / pronouns**            | Pronouns (he, she, it, they, etc.) and other anaphoric references are banned. Every variable must be explicitly named in each sentence to preserve referential clarity.             |
| **Deterministic temporal phrases**    | Keywords like **always**, **at time n**, **next**, **until** map directly to Tau’s stream syntax (e.g., `o1[t]`, `o1[t+1]`, etc.) or temporal operators.                                  |
| **Restricted but Extensible Vocabulary** | Users define nouns (concepts) and verbs (predicates/functions) through grammar plugins. Each user-defined term must bind to a Tau *predicate* or *function* signature (name and arity) so the compiler does not guess. The core TCE grammar provides the sentence structure. |

## 3. Core TCE Grammar (Lark EBNF)

The following EBNF defines the structure of TCE sentences. This grammar is intended for use with the Lark parsing library. User-defined terms (primarily `<Name>` for predicates/functions and `<Variable>`/`<Constant>` for their arguments) are integrated into these structures.

```ebnf
// TCE Grammar v0.1.0
// Based on blueprint provided by user.

?start: sentence

sentence: fact "."
        | rule "."
        | definition "."

fact: predicate_call
    | comparison       // Allows comparisons as top-level facts, adjusted from initial draft

rule: "if" condition "then" predicate_call

definition: "define" ("predicate" | "function") CNAME // CNAME is a Lark terminal for identifiers
            "(" [var_list] ")" "as" expr

predicate_call: CNAME "(" [arg_list] ")" // CNAME for predicate/function name

?condition: [quant_block] expr

quant_block: ("for" "every" | "there" "exists") var_list ("such" "that" expr)?

?expr: term (BOOL_OP term)*

?term: factor
     | "(" expr ")"

?factor: "not" factor
       | predicate_call
       | comparison

comparison: arithmetic COMPARISON_OP arithmetic

// Arithmetic expressions are simplified for now, can be expanded
?arithmetic: atom
           | arithmetic ARITHMETIC_OP atom // Allows left-recursion for chained ops

?atom: constant
     | variable
     | stream_ref

constant: SIGNED_NUMBER // Lark terminal
        | ESCAPED_STRING // Lark terminal for quoted strings

variable: CNAME // Variables are identifiers

stream_ref: ("input" | "output") SIGNED_NUMBER "at" "time" time_spec

time_spec: SIGNED_NUMBER
         | variable
         | variable ("+"|"-") SIGNED_NUMBER

var_list: variable ("," variable)*
arg_list: (expr | constant | variable) ("," (expr | constant | variable))* // Arguments can be more complex

// Terminals
CNAME: /[a-zA-Z_][a-zA-Z0-9_]*/
BOOL_OP: "and" | "or" | "xor"
COMPARISON_OP: "=" | "!=" | "<" | ">" | "<=" | ">="
ARITHMETIC_OP: "+" | "-" | "*" | "/"
COMMENT: /\/\/.*/ // For comments

%import common.SIGNED_NUMBER
%import common.ESCAPED_STRING
%import common.WS

%ignore WS // Ignore whitespace
%ignore COMMENT // Ignore comments

// Case-insensitivity for keywords (Lark feature)
%caseless "if"
%caseless "then"
%caseless "define"
%caseless "predicate"
%caseless "function"
%caseless "as"
%caseless "for"
%caseless "every"
%caseless "there"
%caseless "exists"
%caseless "such"
%caseless "that"
%caseless "not"
%caseless "and"
%caseless "or"
%caseless "xor"
%caseless "input"
%caseless "output"
%caseless "at"
%caseless "time"

```

**Notes on EBNF:**
*   `CNAME` is a Lark built-in for typical identifiers (used for predicate names, function names, variable names).
*   `SIGNED_NUMBER`, `ESCAPED_STRING`, `WS` are imported from Lark's common terminals.
*   Keywords are marked case-insensitive using `%caseless`.
*   Rules starting with `?` (e.g., `?expr`) have their single child node inlined in the parse tree if they have only one.
*   The `fact` rule was updated to `fact: predicate_call | comparison` to allow direct assertions like `variable = value.` as facts.
*   `COMMENT: /\/\/.*/` and `%ignore COMMENT` have been added for line comments.

## 4. Vocabulary and User-Defined Grammar Plugins

TCE provides the sentence *structure*. The *vocabulary* (specific names for concepts, predicates, functions, and their expected argument types/arities) is primarily supplied by user-defined **grammar plugins**.

*   **Predicates and Functions:** When the TCE parser encounters a `CNAME` in a `predicate_call` or `definition`, it will consult the active grammar plugin(s) to:
    *   Verify that the `CNAME` corresponds to a known predicate or function.
    *   Check the arity (number of arguments) provided against the definition in the plugin.
    *   (Future) Check argument types if the plugin provides type information.
*   **Variables and Constants:** The types of variables and constants might also be informed by the plugin context. For instance, a plugin might define specific enumerated types or custom constant formats.

The `PluginManager` will be responsible for loading this vocabulary from plugins and making it available to the TCE parser and semantic analyzer.

## 5. Mapping TCE to Tau

The following table outlines the primary mapping from TCE constructs to Tau language elements:

| TCE Token/Construct             | Tau Token/Construct       | Notes                                                                 |
| ------------------------------- | ------------------------- | --------------------------------------------------------------------- |
| `and`                           | `&`                       | Boolean AND                                                           |
| `or`                            | `\\`                       | Boolean OR                                                            |
| `xor`                           | `+`                       | Boolean XOR                                                           |
| `not`                           | `'` (prefix)              | Boolean NOT                                                           |
| `for every X`                   | `{all X}`                 | Universal quantifier. `X` is a list of variables.                     |
| `there exists X`                | `{ex X}`                  | Existential quantifier. `X` is a list of variables.                   |
| `if CONDITION then PRED_CALL`   | `CONDITION -> PRED_CALL`  | Implication (desugars to `'(CONDITION) \\ PRED_CALL`)                 |
| `output N at time T`            | `oN[T]`                   | Output stream reference (e.g., `output1 at time t` → `o1[t]`)         |
| `input N at time T`             | `iN[T]`                   | Input stream reference (e.g., `input2 at time t+1` → `i2[t+1]`)       |
| `define predicate P(x,y) as EXPR` | `P(x,y) := EXPR`          | Predicate definition                                                  |
| `define function F(x,y) as EXPR`  | `F(x,y) := EXPR`          | Function definition (Tau functions are essentially predicates)        |
| `X = Y` (comparison)            | `X = Y`                   | Equality                                                              |
| `X != Y` (comparison)           | `X != Y`                  | Inequality                                                            |
| `X < Y` (comparison)            | `X < Y`                   | Less than                                                             |
| `X > Y` (comparison)            | `X > Y`                   | Greater than                                                          |
| `X <= Y` (comparison)           | `X <= Y`                  | Less than or equal to                                                 |
| `X >= Y` (comparison)           | `X >= Y`                  | Greater than or equal to                                              |
| *Arithmetic ops (+, -, \*, /)*  | *Directly mapped*         | e.g., `A + B` → `A + B` (if types compatible with Tau arithmetic)     |
| `always PHI`                    | `always PHI`              | Tau's built-in temporal operator (Planned EBNF Extension)             |
| `sometimes PHI`                 | `sometimes PHI`           | Tau's built-in temporal operator (Planned EBNF Extension)             |

*(Note: "always" and "sometimes" are not yet in the core EBNF above but are planned extensions as per the blueprint.)*

## 6. Illustrative Examples

(Adapted from the user's blueprint)

| Controlled English Sentence                                                    | Generated Tau (Conceptual)                                         |
| ------------------------------------------------------------------------------ | ------------------------------------------------------------------ |
| `define predicate bottom(x) as x = 0.`                                         | `bottom(x) := x = 0`                                               |
| `define function union_func(x, y, z) as x or y or z.`                          | `union_func(x,y,z) := x \\ y \\ z`                                   |
| `if for every y such that y < x and y != 0 then chain(x,y,z).`                 | `{all y} (y < x & y != 0) -> chain(x,y,z)`                         |
| `output1 at time t = 0.`                                                       | `o1[t] = 0` (Parsed as a top-level comparison fact)                |
| `always output1 at time t = 0.`                                                | `always (o1[t] = 0)` (Requires 'always' keyword in EBNF)           |

## 7. Compiler Pipeline (Conceptual)

1.  **Tokenizer & Parser (Lark):**
    *   Uses the TCE EBNF (defined in `tce.lark`).
    *   Produces a Concrete Syntax Tree (CST).
2.  **AST Transformation (Lark Transformer):**
    *   Converts the CST to a custom Abstract Syntax Tree (AST).
    *   AST nodes are designed to represent logical constructs directly (e.g., `DefinePredicateNode`, `UniversalQuantificationNode`).
3.  **Semantic Analysis:**
    *   Traverses the AST.
    *   Verifies predicate/function names and arities against vocabulary from active grammar plugins.
    *   Checks for undeclared variables within their scopes.
    *   (Future) Type checking.
4.  **Code Generation:**
    *   Traverses the validated AST.
    *   Emits Tau textual representation.

## 8. Extension Hooks (Future Considerations)

(From user's blueprint)

| Need                                 | CNL Feature Suggestion                                                                                                |
| ------------------------------------ | --------------------------------------------------------------------------------------------------------------------- |
| **Recurrence / indexed definitions** | Add grammar fragment `define predicate P of index n (x, y) ...` to map to `P[n](x,y)` syntax.                         |
| **Pointwise revision**               | Reserve the keyword **revise**: `revise last-rule with ...` to compile to Tau’s pointwise-revision operator.          |
| **Domain ontologies**                | Allow “alias” declarations: `alias customer for person.` then `customer` maps to predicate `person`.                  |
| **Temporal operators**               | Expose `until`, `next`, `eventually` if desired; each token translates to the Tau stream pattern. (e.g., `next P` -> `P[t+1]`) |
| **Comments**                         | `// This is a comment` (Handled in EBNF)                                                                              |

## 9. Meta-Grammar Explanation

The TCE grammar detailed in Section 3 *is* the "meta-grammar." It's "meta" in the sense that it defines fixed sentence structures and logical keywords, but the actual nouns and verbs (predicate names, function names, concept names used as types or variables) are filled in from external user-defined grammar plugins.

*   **Fixed Structure:** Keywords like `if...then`, `define predicate`, `for every`, `and`, `or`, `not` are part of TCE itself.
*   **Variable Vocabulary:** The `CNAME` terminal in the Lark grammar (representing identifiers) is where user-supplied vocabulary comes in. When the parser sees `my_predicate(arg1, arg2).`, `my_predicate` is a `CNAME`. The semantic analyzer will then check if `my_predicate` with 2 arguments is defined in any active grammar plugin.

This approach provides a balance:
*   **Control & Determinism:** The overall sentence structure and logical interpretation are fixed by TCE, ensuring reliable translation to Tau.
*   **Flexibility & Expressiveness:** Users can define their own domain-specific terms and use them within the TCE framework.

---