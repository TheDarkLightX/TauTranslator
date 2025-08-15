# Tau Controlled English (TCE) Grammar Specification

This document provides a detailed specification for the Tau Controlled English (TCE) grammar, as defined in `tau_controlled.lark`. TCE is a formal subset of English designed to be unambiguous and directly translatable into the formal Tau language.

## 1. Overview

TCE is a procedural and functional language that allows for the precise specification of system behavior, logic, and computations. It includes constructs for temporal logic, function definitions, variable assignments, and complex logical and arithmetic expressions.

## 2. Top-Level Structure

All TCE specifications begin with a `start` rule, which is typically a `statement`.

```lark
start: statement
```

A `statement` can be a definition, a specification, or an assignment.

## 3. Temporal Logic Specifications

TCE supports high-level temporal logic to define properties that must hold over time.

- `always`: The property must be true for all time.
- `sometimes` / `eventually`: The property must be true at some point in time.
- `never`: The property must never be true.

**Example:**
`always the button is not pressed`

## 4. Definitions

You can define functions and variables within TCE.

### Function Definitions

```lark
function_definition: "define" "the" "function" CNAME ["(" param_list ")"] "as" term
```

**Example:**
`define the function is_valid(user) as user has a valid_id`

### Variable Definitions

```lark
variable: CNAME
```

Variables are used to hold values and are assigned using `is defined as` or `becomes`.

**Example:**
`x is defined as 5`
`y becomes x and z`

## 5. Expressions

TCE supports a rich set of expressions.

### Logical Expressions
- `if ... then ... else ...`
- `... and ...`
- `... or ...`
- `... xor ...`
- `... is equivalent to ...` (iff)
- `it is not the case that ...` (not)

### Quantified Expressions
- `for all ... such that ...`
- `there exists ... such that ...`

**Example:**
`for all users such that the user is active`

### Comparison Expressions
- `is equal to`, `is not equal to`
- `is less than`, `is greater than or equal to`, etc.

## 6. Data Types and Literals

- **Booleans:** `true`, `false`
- **Numbers:** `SIGNED_NUMBER` (e.g., `5`, `-10`)
- **Bitvectors:** `"..."` (e.g., `"1010"`)
- **Strings:** `"..."` (via imported `STRING_LITERAL`)
- **Streams:** Special variables representing a sequence of values over time, used with `input` and `output` keywords.

## 7. Function Calls

Defined functions can be called using natural language syntax.

```lark
function_call: "call" "the" "function" CNAME ["with" "parameters" term_list]
```

**Example:**
`call the function is_valid with parameters current_user`

## 8. Full Example

```
always if the light is green then it is not the case that the crosswalk signal is walk
```
