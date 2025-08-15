# A Comprehensive Guide to Tau Specification Best Practices

## Introduction: The Tau Philosophy

Tau is a formally verifiable, temporal logic programming language. Its power lies in its ability to describe complex, stateful systems in a way that can be mathematically proven correct. The core philosophy of Tau is **declarative, functional, and verifiable.**

-   **Declarative:** You describe *what* the system does, not *how* it does it. You define relationships and rules, and the Tau solver finds the solution.
-   **Functional:** Tau programs are composed of pure functions. There are no variables or mutable state in the traditional sense. State is managed explicitly through time-based relations.
-   **Verifiable:** Every Tau specification is a set of logical assertions that can be proven for correctness, consistency, and completeness.

This guide provides the principles and patterns to write effective, maintainable, and verifiable Tau code.

---

## 1. Core Concepts

### WFF vs. BF (Well-Formed Formulas vs. Boolean Functions)

-   **Boolean Functions (BFs):** These are the building blocks. They represent computations that result in a boolean value (`1` or `0`). They are composed using operators like `&` (AND), `|` (OR), `+` (XOR), and `'` (NOT).
    -   **Example:** `light_is_on := switch_a & switch_b.`
-   **Well-Formed Formulas (WFFs):** These are assertions *about* BFs. They introduce temporal logic and constraints, evaluating to `T` (True) or `F` (False). They use operators like `[]` (always), `<>` (sometimes), and `->` (implies).
    -   **Example:** `main := [](light_is_on -> power_is_on).` (It is always true that if the light is on, the power must be on).

### Temporal Logic: Managing State Through Time

State in Tau is not stored; it's re-derived at each time step based on past states. This is achieved using temporal offsets.

-   `state[t]` refers to the value of `state` at the current time step `t` (the `[t]` is often implicit).
-   `state[t-1]` refers to the value of `state` at the previous time step.

This is the fundamental mechanism for building Finite State Machines (FSMs) and any system with memory.

**Example: A Simple Toggle Switch**
```tau
// The switch is on if it was off previously and is now pressed,
// or if it was on previously and was not pressed.
switch_on[t] := (switch_on[t-1]' & pressed[t]) | (switch_on[t-1] & pressed[t]').
```

### Execution: REPL vs. `--evaluate`

-   **REPL (`tau`):** The interactive Read-Eval-Print Loop is for symbolic manipulation and checking the satisfiability of formulas. It's not for concrete computation.
-   **Batch (`tau --evaluate` or Docker):** This is the canonical method for validation and running simulations. It takes a complete set of definitions and an expression to evaluate, producing a concrete result (`1` or `0`).

**Best Practice:** Always use batch evaluation for testing and validation. The most reliable method is the official Docker container:
`docker run --rm -i tau-lang:latest < your_spec.tau`

---

## 2. Syntax and Semantics: The Rules

These rules are derived from the formal Tau grammar.

### Function Definitions

-   **Syntax:** `function_name(param1, param2) := body.`
-   **Rules:**
    1.  **Short Names:** Keep function and parameter names short and descriptive (e.g., `attr` for attraction, `p1` for player 1).
    2.  **Max 3 Parameters:** Functions are limited to a maximum of three parameters.
    3.  **Single Line:** The entire definition must be on a single line.
    4.  **Pure Functions:** Functions must be pure. They can only depend on their inputs.

**Example: A 2-bit Adder**
```tau
// Half adder
ha(a, b) := (a+b) (a&b). // Returns: sum, carry_out

// Full adder
fa(a, b, cin) := ha(a+b, cin) (a&b | (a+b)&cin). // Returns: sum, carry_out
```

### Operators

-   **Boolean AND:** `&` or implicit concatenation (e.g., `a b` is `a & b`).
-   **Boolean OR:** `|`
-   **Boolean XOR:** `+`
-   **Boolean NOT (Postfix):** `A'`
-   **WFF Implies:** `->`
-   **WFF Always (Temporal):** `[]`
-   **WFF Sometimes (Temporal):** `<>`

### Representing Data

Everything in Tau is a boolean. Complex data is built from collections of booleans.

-   **Numbers:** Use a binary representation (a collection of bits). For example, a 4-bit number can be represented by four functions: `num_b0`, `num_b1`, `num_b2`, `num_b3`.
-   **Enums:** Use a one-hot encoding. If you have three states (e.g., `HAPPY`, `SAD`, `NEUTRAL`), create three boolean functions, where only one can be true at any time.

**Example: 2-bit Number**
```tau
// Represents the number 3 (binary 11)
three_b1 := 1.
three_b0 := 1.

// Represents the number 2 (binary 10)
two_b1 := 1.
two_b0 := 0.
```

---

## 3. Best Practices & Design Patterns

### Modularity: The `TauHeart` Pattern

Complex systems should be broken down into smaller, self-contained modules (files).

-   **One File, One Concept:** Each `.tau` file should represent a single logical unit (e.g., `arithmetic.tau`, `relationship_logic.tau`, `events.tau`).
-   **Concatenation for Validation:** To validate the full system, concatenate the module files into a single stream and pipe it to the Tau validator.
    -   **Example (`Makefile` or script):** `cat systems/*.tau scenarios/*.tau main.tau | docker run --rm -i tau-lang:latest`
-   **Use Libraries:** Leverage standard libraries like `TauStandardLibrary` for common operations (e.g., arithmetic, logic gates) to avoid reinventing the wheel.

### Testing and Validation

-   **Write Test Assertions:** For every module, create a corresponding test file that makes assertions about its behavior.
-   **Use a Main WFF:** The `main` WFF is the entry point for validation. It should contain the primary assertions to be proven.

**Example: Testing an Adder**
```tau
// In arithmetic.tau
adder(a, b) := a+b.

// In test_arithmetic.tau
@use arithmetic.tau.

// Assert that 1 + 0 = 1
test_add_1_0 := adder(1, 0) = 1.

// Assert that 1 + 1 = 0 (in single-bit XOR)
test_add_1_1 := adder(1, 1) = 0.

// The main test harness
main := [] (test_add_1_0 & test_add_1_1).
```

### FSM Design

1.  **Define States:** Clearly define all possible states of your system as boolean functions.
2.  **Define Inputs:** Define all external inputs that can affect the state.
3.  **Write Transition Functions:** For each state bit, write a function `state_bit[t] := ...` that defines its value based on `state[t-1]` and `inputs[t]`.
4.  **Define Outputs:** Write functions that determine the system's outputs based on the current state `state[t]`.

---

## 4. For LLMs: A Prompt Template for Generating Tau

When prompting an LLM to generate Tau code, be explicit and provide the rules and a high-quality example.

```text
You are an expert in the Tau programming language, a formally verifiable temporal logic language. Your task is to translate a description of a system into a valid, modular, and testable Tau specification.

**Key Tau Language Rules:**
1.  **Pure Functions:** All definitions use `:=` and must be pure.
2.  **Syntax:** `function_name(param1, param2) := body.`
3.  **Parameters:** Maximum of 3 parameters per function.
4.  **State:** State is managed via temporal offsets, e.g., `state[t-1]`.
5.  **Modularity:** Each logical component should be in its own file.
6.  **Testing:** Every module must have corresponding test assertions.
7.  **Core Operators:** `&` (AND), `|` (OR), `+` (XOR), `'` (postfix NOT).

**Example: A Simple Vending Machine FSM**

**File: `vending_machine.tau`**
```tau
// State: Has a coin been inserted?
has_coin[t] := (insert_coin[t] | has_coin[t-1]) & dispense'[t].

// Output: Dispense a soda if a coin is present and the dispense button is pressed.
dispense[t] := has_coin[t] & press_dispense[t].
```

**File: `test_vending_machine.tau`**
```tau
@use "vending_machine.tau".

// Test 1: If we insert a coin, has_coin becomes true.
insert_coin[t] := 1.
press_dispense[t] := 0.
assert_has_coin_after_insert := has_coin[t] = 1.

// Main validation formula
main := [] (assert_has_coin_after_insert).
```

--- 

**Your Task:**

[Insert clear, concise description of the system to be modeled here.]

Generate the necessary `.tau` files, following all the rules and patterns described above. Ensure you provide both the core logic and the test assertions.
```
