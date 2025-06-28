# Documentation: `ebnf_parser.py`

**Module**: `src.tau_translator_omega.grammar_tools.ebnf_parser`

## 1. Module Overview

The `ebnf_parser.py` module provides a robust, dedicated parser for EBNF (Extended Backus-Naur Form) grammars. It serves as a specialized tool within the `grammar_tools` package, leveraging the powerful `lark-parser` library to validate and transform EBNF grammar definitions into a structured syntax tree (`lark.Tree`).

Its primary purpose is to ensure that grammar files used elsewhere in the system are syntactically correct before they are used to build other parsers, thereby preventing runtime errors and improving system reliability.

## 2. Architecture and Design

The module's design is centered around simplicity and robustness, following the **Wrapper** and **Exception Wrapping** patterns.

-   **Wrapper Pattern**: The `EbnfParser` class acts as a high-level wrapper around the `lark` library's internal EBNF meta-parser. This encapsulates the complexity of initializing and running the Lark parser, providing a clean and straightforward API (`parse_string`, `parse_file`) for the rest of the system.
-   **Exception Wrapping**: The module defines a custom `EbnfParsingError` to create a clear error handling contract. Instead of exposing `lark.exceptions.LarkError` directly, the parser catches it and re-raises it as an `EbnfParsingError`. This decouples the rest of the application from the specific implementation details of the underlying parsing library.
-   **Fail-Fast Initialization**: The `EbnfParser`'s constructor will raise a `RuntimeError` if it cannot locate Lark's internal EBNF grammar file. This fail-fast approach ensures that configuration or installation issues are detected immediately upon application startup, rather than causing unexpected failures later.

## 3. Key Classes and API

### `EbnfParsingError`

A custom exception class that inherits from Python's base `Exception`. It is raised whenever the parser encounters a syntax error in the provided EBNF grammar string or file.

---

### `EbnfParser`

The central class of the module.

#### `__init__(self)`
-   **Description**: Initializes the EBNF meta-parser by loading Lark's built-in EBNF grammar.
-   **Raises**: `RuntimeError` if Lark's internal grammar files cannot be found, indicating an installation or environment issue.

#### `parse_string(self, ebnf_string: str) -> lark.Tree`
-   **Description**: Parses a string containing an EBNF grammar.
-   **Arguments**:
    -   `ebnf_string` (str): The grammar definition to parse.
-   **Returns**: A `lark.Tree` object representing the abstract syntax tree of the parsed grammar.
-   **Raises**: `EbnfParsingError` if the input string contains invalid EBNF syntax.

#### `parse_file(self, file_path: str) -> lark.Tree`
-   **Description**: Reads an EBNF grammar from a file and parses it.
-   **Arguments**:
    -   `file_path` (str): The absolute or relative path to the `.ebnf` file.
-   **Returns**: A `lark.Tree` object representing the abstract syntax tree of the parsed grammar.
-   **Raises**:
    -   `FileNotFoundError`: If the file at `file_path` does not exist.
    -   `EbnfParsingError`: If the file content contains invalid EBNF syntax.

## 4. Usage Example

```python
from tau_translator_omega.grammar_tools.ebnf_parser import EbnfParser, EbnfParsingError

# --- 1. Initialize the parser ---
try:
    parser = EbnfParser()
except RuntimeError as e:
    print(f"Configuration Error: {e}")
    # Handle missing Lark dependency
    exit(1)

# --- 2. Parse a valid grammar string ---
valid_grammar = 'start: "a" "b";'
try:
    ast = parser.parse_string(valid_grammar)
    print("Successfully parsed valid grammar:")
    print(ast.pretty())
except EbnfParsingError as e:
    print(f"Unexpected parsing error: {e}")

# --- 3. Attempt to parse an invalid grammar string ---
invalid_grammar = 'start := "a" "b" # Invalid assignment operator'
try:
    parser.parse_string(invalid_grammar)
except EbnfParsingError as e:
    print(f"\nSuccessfully caught invalid grammar error: {e}")

# --- 4. Parse from a file ---
# Assume 'my_grammar.ebnf' contains: rule: "c" | "d";
try:
    file_ast = parser.parse_file('my_grammar.ebnf')
    print("\nSuccessfully parsed grammar from file.")
except FileNotFoundError:
    print("\nError: Grammar file not found.")
except EbnfParsingError as e:
    print(f"\nError parsing grammar file: {e}")
```

## 5. Dependencies

-   **`lark-parser`**: This module requires the Lark library to be installed. It can be installed via pip:
    ```bash
    pip install lark-parser
    ```
