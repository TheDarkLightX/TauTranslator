# Mapping Tau Controlled English to Canonical Tau

This document explains the relationship between the human-readable Tau Controlled English (TCE) and the formal, canonical Tau language. Understanding this mapping is key to using the translator effectively.

## CRITICAL: Tau Language Limitations

Before proceeding, it is essential to understand two critical limitations of the Tau toolchain that heavily influence how specifications must be written:

1.  **No Multi-Digit Numeric Literals:** The Tau parser **does not accept multi-digit numbers** (e.g., `170`, `80000`) directly in definitions or formulas. All numeric constants must be single digits or defined as zero-argument functions.
2.  **Multiplication is by Juxtaposition:** The `*` operator is not used for multiplication. Instead, multiplication is implied by placing terms next to each other (juxtaposition), e.g., `a x` means `a * x`.

These constraints are fundamental and must be respected for any Tau specification to be valid.

## The Definition Operator: `:=`

The most fundamental operator for adding knowledge in Tau is the **definition operator**, `:=`. This operator should be read as **"is defined as"** or **"if"**.

### 1. Defining Facts

A fact is a statement that is asserted to be `true`.

- **TCE Statement:** `Socrates is a man`
- **Canonical Tau:** `man(Socrates) := true.`

### 2. Defining Rules (Implications)

A rule establishes a logical implication.

- **TCE Statement:** `every man is mortal`
- **Canonical Tau:** `mortal(X) := man(X).`
- **Logic:** For any `X`, if `X` is a man, then `X` is mortal.

### 3. Defining Constants (Zero-Argument Functions)

Due to the numeric literal limitation, constants must be defined as functions with no arguments.

- **TCE Statement:** `the coefficient is 170`
- **Canonical Tau:** `coefficient() := 170.`
    - **Note:** While the definition can contain a multi-digit number, this function **cannot** be used in a `solve` formula. This syntax is for defining functions that can be normalized, not for use in solver constraints. For solver constraints, constants must be broken down or represented symbolically.

## Mapping Common TCE Constructs

### Identity and Relations

- **TCE:** `Socrates is a man` -> **Tau:** `man(Socrates) := true.`
- **TCE:** `Plato teaches Aristotle` -> **Tau:** `teaches(Plato, Aristotle) := true.`

### Quantifiers

- **Universal (`every`, `all`):** `every car is a vehicle` -> **Tau:** `vehicle(X) := car(X).`
- **Existential (`some`, `a`):** `some animal is a mammal` -> **Tau:** `exists X : (animal(X) and mammal(X)).`

### Boolean Logic

- **AND:** `X is a cat and X is fluffy` -> **Tau:** `(cat(X) and fluffy(X))`
- **OR:** `X is a cat or X is a dog` -> **Tau:** `(cat(X) or dog(X))`
- **NOT:** `X is not a dog` -> **Tau:** `not dog(X).`

## Advanced Example: Arithmetic

Consider the formula `liquidation_price * 2 * 85 = 80000`. Due to the language limitations, this must be expressed declaratively and symbolically.

**Canonical Tau Approach:**
```tau
# Define constants as zero-argument functions
coefficient() := 170.
constant_term() := 80000.

# Use the functions in a solve query
# NOTE: This specific query failed due to parser limitations.
# It illustrates the intended symbolic approach.
solve coefficient() lp = constant_term().
```

This mapping document provides the core translations needed to write effective Tau specs. Always refer back to the canonical demos for advanced patterns.
