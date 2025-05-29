# Intermediate Logical Representation (ILR) Specification

## 1. Overview

This document specifies the Intermediate Logical Representation (ILR) for the TauTranslatorOmega project. The ILR serves as a grammar-agnostic, structured representation of user requirements, translated from natural language by an LLM. This ILR is then consumed by plugins to generate code in specific target formal languages.

## 2. Serialization Format

The ILR will be serialized using **JSON (JavaScript Object Notation)**.
A formal definition of the ILR's structure, types, and constraints will be provided using **JSON Schema** in the future.

## 2.1 Core Data Types

The ILR v0.1 supports the following fundamental data types, which are used in declarations and can be produced by expressions:
-   `"BOOLEAN"`: Represents a logical true or false value.
-   `"NUMBER"`: Represents numerical values. This can include integers and floating-point numbers. Plugins should aim to support standard representations (e.g., IEEE 754 for floats if applicable to the target).
-   `"STRING"`: Represents a sequence of characters, typically UTF-8 encoded.
-   `"BITVECTOR"`: Represents a fixed-width sequence of bits.
-   `"BITSTRING"`: Represents a variable-length sequence of bits, typically represented as a string of '0's and '1's.
-   `"VOID"`: Used specifically as a `return_type` for functions/procedures that do not return a value.
-   `"FUNCTION_SIGNATURE"`: Represents the type of a function, defined by its parameter types and return type. Used for declaring variables that hold functions or for passing functions as arguments.

*(Future Consideration: A `TABLE` type for representing structured tabular data may be added in a future version.)*

## 3. Core Constructs

All ILR constructs defined below will include a type-discriminator field: `node_type` for expressions, `declaration_type` for declarations, or `statement_type` for statements. This field contains a string literal uniquely identifying the kind of ILR element.

### 3.1. Boolean Expressions

Boolean expressions represent logical conditions.

- **Object Type Identifier:** (e.g., a field like `"node_type": "BOOLEAN_EXPRESSION"`)
- **Attributes:**
    - `operator`: (String Enum) The Boolean operator. Supported values:
        - `"AND"` (n-ary, at least 2 operands)
        - `"OR"` (n-ary, at least 2 operands)
        - `"NOT"` (unary)
        - `"XOR"` (n-ary, or binary and nested)
        - `"IMPLIES"` (binary: operands should be an array of two: `[antecedent, consequent]`)
        - `"EQUIVALENT"` (binary: operands should be an array of two)
    - `operands`: (Array) An array of operand objects. The number and nature of operands depend on the operator.

#### 3.1.1. Operands for Boolean Expressions

Operands within a Boolean expression can be one of the following types (each will have its own object structure with a `node_type` identifier):

*   Another `BOOLEAN_EXPRESSION` (allowing for nested logic)
*   `VARIABLE_REFERENCE`
*   `BOOLEAN_CONSTANT`
*   `COMPARISON_EXPRESSION`
*   `FUNCTION_CALL` (returning a Boolean)

**(Further details on these operand types will be specified in subsequent sections.)**

#### 3.1.1.1. `VARIABLE_REFERENCE`
Represents a reference to a declared variable, stream, or entity.
```json
{
  "node_type": "VARIABLE_REFERENCE",
  "name": "string", // The unique name/identifier of the variable or stream
  "temporal_qualifier": { // Optional: For streams or time-dependent variables
    "type": "TIME_OFFSET", // Currently only TIME_OFFSET is defined
    "offset": "integer" // 0 for current time [t], -1 for [t-1], 1 for [t+1], etc.
  }
  // Future extensions: 'scope', 'namespace'
}
```

#### 3.1.1.2. `BOOLEAN_CONSTANT`
Represents a literal boolean value.
```json
{
  "node_type": "BOOLEAN_CONSTANT",
  "value": "boolean" // true or false
}
```

#### 3.1.1.3. `COMPARISON_EXPRESSION`
Represents a comparison between two operands, evaluating to a boolean.
```json
{
  "node_type": "COMPARISON_EXPRESSION",
  "operator": "string_enum", // E.g., "EQUALS", "NOT_EQUALS", "GREATER_THAN", "LESS_THAN", "GTE" (Greater Than or Equal), "LTE" (Less Than or Equal)
  "lhs": "object", // Left-hand side operand (e.g., VARIABLE_REFERENCE, CONSTANT, FUNCTION_CALL, ARITHMETIC_EXPRESSION)
  "rhs": "object"  // Right-hand side operand (e.g., VARIABLE_REFERENCE, CONSTANT, FUNCTION_CALL, ARITHMETIC_EXPRESSION)
}
```
*(Note: The structures for `CONSTANT` (other than boolean), `FUNCTION_CALL`, and `ARITHMETIC_EXPRESSION` will be defined in subsequent sections.)*

#### 3.1.1.4. `BITVECTOR_CONSTANT`

Represents a constant bitvector value.

-   `node_type`: Must be `"BITVECTOR_CONSTANT"`.
-   `value`: (String) The string representation of the bitvector's value (e.g., "0xDEADBEEF", "0b1010"). The interpretation of this string (e.g. hex, binary) is context-dependent or may be further specified by a dialect.
-   `width`: (Integer, Optional) The width of the bitvector in bits. If not provided, it might be inferred from the `value` or context.

#### 3.1.1.5. `BITSTRING_CONSTANT`

Represents a constant bitstring value (e.g., '1010xz01b'). Note that 'x' (don't care) and 'z' (high-impedance) are allowed, aligning with standard bit format (SBF) usage.

-   `node_type`: Must be `"BITSTRING_CONSTANT"`.
-   `value`: (String) The bitstring value as a string (e.g., "1010xz01"). Should only contain '0', '1', 'x', 'z'.
-   `length`: (Integer) The number of characters in the bitstring value.

### 3.1.2. `LOGICAL_EXPRESSION`

Represents a logical operation (AND, OR, XOR, NOT, IMPLIES) performed on Boolean operands.

-   **`node_type`**: "LOGICAL_EXPRESSION"
-   **`operator`**: (String, Enum) The logical operator.
    -   `"AND"`: Logical AND (&&).
    -   `"OR"`: Logical OR (||).
    -   `"XOR"`: Logical XOR.
    -   `"NOT"`: Logical NOT (!).
    -   `"IMPLIES"`: Logical implication (A -> B is equivalent to !A || B).
-   **`operands`**: (Array of `ExpressionNode`) An array of `ExpressionNode` objects.
    -   For `"NOT"`, there is one operand.
    -   For `"AND"`, `"OR"`, `"XOR"`, `"IMPLIES"`, there are two operands.
    -   All operands must evaluate to a `BOOLEAN` type. The result is also `BOOLEAN`.

*Example: `(var_x > 5) AND (var_y < 10)`*

```json
{
  "node_type": "LOGICAL_EXPRESSION",
  "operator": "AND",
  "operands": [
    {
      "node_type": "COMPARISON_EXPRESSION",
      "operator": "GREATER_THAN",
      "lhs": { "node_type": "VARIABLE_REFERENCE", "name": "var_x" },
      "rhs": { "node_type": "NUMERIC_CONSTANT", "value": 5 }
    },
    {
      "node_type": "COMPARISON_EXPRESSION",
      "operator": "LESS_THAN",
      "lhs": { "node_type": "VARIABLE_REFERENCE", "name": "var_y" },
      "rhs": { "node_type": "NUMERIC_CONSTANT", "value": 10 }
    }
  ]
}
```

### 3.1.3. `COMPARISON_EXPRESSION`

Represents a comparison between two expressions.

-   **`node_type`**: "COMPARISON_EXPRESSION"
-   **`operator`**: (String, Enum) The comparison operator.
    -   `"EQUAL_TO"`: (== or ===)
    -   `"NOT_EQUAL_TO"`: (!= or !==)
    -   `"LESS_THAN"`: (<)
    -   `"LESS_THAN_OR_EQUAL_TO"`: (<=)
    -   `"GREATER_THAN"`: (>)
    -   `"GREATER_THAN_OR_EQUAL_TO"`: (>=)
-   **`lhs`**: (`ExpressionNode`) The left-hand side expression.
-   **`rhs`**: (`ExpressionNode`) The right-hand side expression.
    -   `lhs` and `rhs` must evaluate to compatible data types (e.g., both `NUMBER`, both `STRING`).
    -   The result of a comparison expression is always `BOOLEAN`.

*Example: `current_value >= threshold`*

```json
{
  "node_type": "COMPARISON_EXPRESSION",
  "operator": "GREATER_THAN_OR_EQUAL_TO",
  "lhs": {
    "node_type": "VARIABLE_REFERENCE",
    "name": "current_value"
  },
  "rhs": {
    "node_type": "VARIABLE_REFERENCE",
    "name": "threshold"
  }
}
```

### 3.1.4. `ARITHMETIC_EXPRESSION`

Represents an arithmetic operation.

-   **`node_type`**: "ARITHMETIC_EXPRESSION"
-   **`operator`**: (String, Enum) The arithmetic operator.
    -   `"ADD"`: Addition (+).
    -   `"SUBTRACT"`: Subtraction (-).
    -   `"MULTIPLY"`: Multiplication (*).
    -   `"DIVIDE"`: Division (/).
    -   `"MODULO"`: Modulo (%).
    -   `"NEGATE"`: Arithmetic negation (unary -).
-   **`operands`**: (Array of `ExpressionNode`) An array of `ExpressionNode` objects.
    -   For `"NEGATE"`, there is one operand.
    -   For all other operators, there are two operands.
    -   Operands must evaluate to a `NUMBER` type. The result is also `NUMBER`.

*Example: `(count + 1) * 2`*

```json
{
  "node_type": "ARITHMETIC_EXPRESSION",
  "operator": "MULTIPLY",
  "operands": [
    {
      "node_type": "ARITHMETIC_EXPRESSION",
      "operator": "ADD",
      "operands": [
        { "node_type": "VARIABLE_REFERENCE", "name": "count" },
        { "node_type": "NUMERIC_CONSTANT", "value": 1 }
      ]
    },
    { "node_type": "NUMERIC_CONSTANT", "value": 2 }
  ]
}
```

### 3.1.5. `FUNCTION_CALL`

Represents a call to a function or a predefined operation.

-   **`node_type`**: "FUNCTION_CALL"
-   **`function_name`**: (String) The name of the function being called (e.g., "isEmpty", "isPrime"). This name should correspond to a `FUNCTION_DECLARATION` or a plugin-provided function.
-   **`arguments`**: (Array of `ExpressionNode`) An ordered list of arguments passed to the function. The type and number of arguments must be compatible with the function's signature.
-   **`return_type`**: (`CoreDataType`) The expected data type of the value returned by the function, matching the function's declaration.

*Example: `max(value1, value2)`*

```json
{
  "node_type": "FUNCTION_CALL",
  "function_name": "max",
  "arguments": [
    { "node_type": "VARIABLE_REFERENCE", "name": "value1" },
    { "node_type": "VARIABLE_REFERENCE", "name": "value2" }
  ],
  "return_type": "NUMBER"
}
```

### 3.1.6. `QUANTIFIER_EXPRESSION`

Represents a quantified logical expression (e.g., "for all x, P(x)" or "there exists y such that Q(y)").

-   **`node_type`**: "QUANTIFIER_EXPRESSION"
-   **`operator`**: (String, Enum) The quantifier operator.
    -   `"FOR_ALL"`: Universal quantifier (∀).
    -   `"EXISTS"`: Existential quantifier (∃).
-   **`bound_variables`**: (Array of Objects) An array of variables bound by this quantifier. Each object has:
    -   **`name`**: (String) The name of the bound variable.
    -   **`data_type`**: (`CoreDataType`) The data type of the bound variable.
-   **`expression`**: (`ExpressionNode`) The logical expression being quantified. This expression typically uses the bound variables and must evaluate to `BOOLEAN`.

*Example: "For all numbers x, x >= 0"*

```json
{
  "node_type": "QUANTIFIER_EXPRESSION",
  "operator": "FOR_ALL",
  "bound_variables": [
    {
      "name": "x",
      "data_type": "NUMBER"
    }
  ],
  "expression": {
    "node_type": "COMPARISON_EXPRESSION",
    "operator": "GREATER_THAN_OR_EQUAL_TO",
    "lhs": {
      "node_type": "VARIABLE_REFERENCE",
      "name": "x"
    },
    "rhs": {
      "node_type": "NUMERIC_CONSTANT",
      "value": 0
    }
  }
}
```

### 3.1.7. `BITWISE_BINARY_EXPRESSION`

Represents a binary bitwise operation performed on operands that should evaluate to `BITVECTOR` or `BITSTRING` types.

-   **`node_type`**: "BITWISE_BINARY_EXPRESSION"
-   **`operator`**: (String, Enum) The binary bitwise operator.
    -   `"BITWISE_AND"`: Bitwise AND (&).
    -   `"BITWISE_OR"`: Bitwise OR (|).
    -   `"BITWISE_XOR"`: Bitwise XOR (^).
    -   `"SHIFT_LEFT"`: Bitwise left shift (<<).
    -   `"SHIFT_RIGHT_LOGICAL"`: Logical right shift (>>>, fills with zeros).
    -   `"SHIFT_RIGHT_ARITHMETIC"`: Arithmetic right shift (>>, preserves sign bit).
-   **`operands`**: (Array of `ExpressionNode`) An array containing exactly two `ExpressionNode` objects. These operands must evaluate to compatible bit-level data types (`BITVECTOR`, `BITSTRING`). For shift operations, the second operand typically evaluates to a `NUMBER` indicating the shift amount.

*Example: `(var_a & 0xFF) << 2`*

```json
{
  "node_type": "BITWISE_BINARY_EXPRESSION",
  "operator": "SHIFT_LEFT",
  "operands": [
    {
      "node_type": "BITWISE_BINARY_EXPRESSION",
      "operator": "BITWISE_AND",
      "operands": [
        {
          "node_type": "VARIABLE_REFERENCE",
          "name": "var_a"
        },
        {
          "node_type": "BITVECTOR_CONSTANT",
          "value": "0xFF",
          "width": 8
        }
      ]
    },
    {
      "node_type": "NUMERIC_CONSTANT",
      "value": 2
    }
  ]
}
```

### 3.1.8. `BITWISE_UNARY_EXPRESSION`

Represents a unary bitwise operation (complement) performed on an operand that should evaluate to a `BITVECTOR` or `BITSTRING` type.

-   **`node_type`**: "BITWISE_UNARY_EXPRESSION"
-   **`operator`**: (String, Enum) The unary bitwise operator.
    -   `"BITWISE_NOT"`: Bitwise NOT (~, complement).
-   **`operands`**: (Array of `ExpressionNode`) An array containing exactly one `ExpressionNode` object. This operand must evaluate to a `BITVECTOR` or `BITSTRING` data type.

*Example: `~status_flags`*

```json
{
  "node_type": "BITWISE_UNARY_EXPRESSION",
  "operator": "BITWISE_NOT",
  "operands": [
    {
      "node_type": "VARIABLE_REFERENCE",
      "name": "status_flags"
    }
  ]
}
```

### 3.1.9. `LAMBDA_EXPRESSION`

Represents a lambda expression or an anonymous function. Lambda expressions can be assigned to variables of type `FUNCTION_SIGNATURE` or passed as arguments to functions expecting a compatible function signature.

-   **`node_type`**: "LAMBDA_EXPRESSION"
-   **`parameters`**: (Array of `FunctionParameter` objects) An ordered list of parameters for the lambda expression. Each parameter object has a `name` and `data_type`.
-   **`body`**: (`ExpressionNode`) The expression that forms the body of the lambda. The type of this expression must be compatible with the `return_type` of the lambda.
-   **`return_type`**: (`CoreDataType`) The data type of the value returned by the lambda expression.

*Example: A lambda that takes two numbers and returns their sum.*

```json
{
  "node_type": "LAMBDA_EXPRESSION",
  "parameters": [
    { "name": "a", "data_type": "NUMBER" },
    { "name": "b", "data_type": "NUMBER" }
  ],
  "body": {
    "node_type": "ARITHMETIC_EXPRESSION",
    "operator": "ADD",
    "operands": [
      { "node_type": "VARIABLE_REFERENCE", "name": "a" },
      { "node_type": "VARIABLE_REFERENCE", "name": "b" }
    ]
  },
  "return_type": "NUMBER"
}
```

### 3.2. Common Expression Nodes

These nodes can appear as operands in various expressions, including `BOOLEAN_EXPRESSION` and `COMPARISON_EXPRESSION`.

#### 3.2.1. `NUMERIC_CONSTANT`
Represents a literal numeric value (integer or floating-point).
```json
{
  "node_type": "NUMERIC_CONSTANT",
  "value": "number" // e.g., 123, 45.67
}
```

#### 3.2.2. `STRING_CONSTANT`
Represents a literal string value.
```json
{
  "node_type": "STRING_CONSTANT",
  "value": "string" // e.g., "active_state", "error_message"
}
```

#### 3.2.3. `ARITHMETIC_EXPRESSION`
Represents an arithmetic operation.
```json
{
  "node_type": "ARITHMETIC_EXPRESSION",
  "operator": "string_enum", // E.g., "ADD", "SUBTRACT", "MULTIPLY", "DIVIDE", "MODULO", "POWER", "NEGATE" (Unary operation, takes one operand in the `operands` array)
  "operands": [ // Array of operand objects. For binary operators (ADD, SUBTRACT, etc.), this array contains two operands. For unary operators (NEGATE), it contains one.
    // e.g., CONSTANT, VARIABLE_REFERENCE, another ARITHMETIC_EXPRESSION, FUNCTION_CALL
  ]
}
```

#### 3.2.4. `FUNCTION_CALL`
Represents a call to a declared function or predicate.
```json
{
  "node_type": "FUNCTION_CALL",
  "function_name": "string", // Name of the function, must match a declared function
  "arguments": [ // Array of argument objects, each being a valid ILR expression node
    // e.g., CONSTANT, VARIABLE_REFERENCE, another FUNCTION_CALL, ARITHMETIC_EXPRESSION
  ]
  // "return_type" is typically inferred from the function's declaration.
}
```

### 3.3 Declarations

This section defines how named entities like variables, streams, functions, and predicates are declared. These declarations provide context for `VARIABLE_REFERENCE` and `FUNCTION_CALL` nodes used in expressions. An ILR document would typically contain an array of such declaration objects.

#### 3.3.1. `VARIABLE_DECLARATION`
Declares a variable or a stream.
```json
{
  "declaration_type": "VARIABLE",
  "name": "string", // Unique name/identifier for the variable or stream
  "data_type": "string_enum", // E.g., "BOOLEAN", "NUMBER", "STRING", "BITVECTOR", "BITSTRING", "FUNCTION_SIGNATURE"
  // If data_type is "FUNCTION_SIGNATURE", the following two fields are required:
  // "parameter_types": ["CoreDataType", ...], // Array of CoreDataType for the function's parameters
  // "function_return_type": "CoreDataType", // CoreDataType for the function's return value
  "is_stream": "boolean", // true if this variable is time-indexed (e.g., input_signal[t])
  "stream_kind": "string_enum_or_null", // Optional, if is_stream is true. E.g., "INPUT", "OUTPUT", "INTERNAL_STATE"
  "initial_value": "object_or_null" // Optional: A constant node, or a LAMBDA_EXPRESSION if data_type is FUNCTION_SIGNATURE.
}
```

*Example of a variable holding a function signature:*
```json
{
  "declaration_type": "VARIABLE",
  "name": "myFunctionVar",
  "data_type": "FUNCTION_SIGNATURE",
  "parameter_types": ["NUMBER", "NUMBER"],
  "function_return_type": "BOOLEAN",
  "is_stream": false,
  "initial_value": null
}
```

#### 3.3.2. `FUNCTION_DECLARATION`
Declares the signature of a function or predicate. The implementation is plugin-dependent.
```json
{
  "declaration_type": "FUNCTION",
  "name": "string", // Unique name/identifier for the function
  "parameters": [ // Array of parameter objects
    {
      "name": "string", // Parameter name, unique within this function's scope
      "data_type": "string_enum" // Data type of the parameter. Can be "FUNCTION_SIGNATURE".
      // If data_type is "FUNCTION_SIGNATURE", the following two fields are required:
      // "parameter_types": ["CoreDataType", ...], // Array of CoreDataType for the function's parameters
      // "function_return_type": "CoreDataType" // CoreDataType for the function's return value
    }
    // ... more parameters
  ],
  "return_type": "string_enum" // Data type of the return value. Use "VOID" for procedures. Can be "FUNCTION_SIGNATURE".
  // If return_type is "FUNCTION_SIGNATURE", the following two fields are required to describe the signature of the returned function:
  // "return_parameter_types": ["CoreDataType", ...],
  // "return_function_return_type": "CoreDataType"
}
```

*Example of a function parameter that is itself a function:*
```json
{
  "declaration_type": "FUNCTION",
  "name": "applyOperation",
  "parameters": [
    {
      "name": "input_val",
      "data_type": "NUMBER"
    },
    {
      "name": "operation_func",
      "data_type": "FUNCTION_SIGNATURE",
      "parameter_types": ["NUMBER"],
      "function_return_type": "NUMBER"
    }
  ],
  "return_type": "NUMBER"
}
```

### 3.4 Statements and Rules
{{ ... }}

### 3.1.9. `LAMBDA_EXPRESSION`

Represents a lambda expression or an anonymous function. Lambda expressions can be assigned to variables of type `FUNCTION_SIGNATURE` or passed as arguments to functions expecting a compatible function signature.

-   **`node_type`**: "LAMBDA_EXPRESSION"
-   **`parameters`**: (Array of `FunctionParameter` objects) An ordered list of parameters for the lambda expression. Each parameter object has a `name` and `data_type`.
-   **`body`**: (`ExpressionNode`) The expression that forms the body of the lambda. The type of this expression must be compatible with the `return_type` of the lambda.
-   **`return_type`**: (`CoreDataType`) The data type of the value returned by the lambda expression.

*Example: A lambda that takes two numbers and returns their sum.*

```json
{
  "node_type": "LAMBDA_EXPRESSION",
  "parameters": [
    { "name": "a", "data_type": "NUMBER" },
    { "name": "b", "data_type": "NUMBER" }
  ],
  "body": {
    "node_type": "ARITHMETIC_EXPRESSION",
    "operator": "ADD",
    "operands": [
      { "node_type": "VARIABLE_REFERENCE", "name": "a" },
      { "node_type": "VARIABLE_REFERENCE", "name": "b" }
    ]
  },
  "return_type": "NUMBER"
}
```

### 3.2. Common Constant Value Nodes

These nodes represent literal values that can appear as operands in various expressions.

#### 3.2.1. `NUMERIC_CONSTANT`
Represents a literal numeric value (integer or floating-point).
```json
{
  "node_type": "NUMERIC_CONSTANT",
  "value": "number" // e.g., 42, 3.14159
}
```

#### 3.2.2. `STRING_CONSTANT`
Represents a literal string value.
```json
{
  "node_type": "STRING_CONSTANT",
  "value": "string" // e.g., "hello world"
}
```

### 3.3 Declarations

This section defines how named entities like variables, streams, functions, and predicates are declared. These declarations provide context for `VARIABLE_REFERENCE` and `FUNCTION_CALL` nodes used in expressions. An ILR document would typically contain an array of such declaration objects.

#### 3.3.1. `VARIABLE_DECLARATION`
Declares a variable or a stream.
```json
{
  "declaration_type": "VARIABLE",
  "name": "string", // Unique name/identifier for the variable or stream
  "data_type": "string_enum", // E.g., "BOOLEAN", "NUMBER", "STRING", "BITVECTOR", "BITSTRING", "FUNCTION_SIGNATURE"
  // If data_type is "FUNCTION_SIGNATURE", the following two fields are required:
  // "parameter_types": ["CoreDataType", ...], // Array of CoreDataType for the function's parameters
  // "function_return_type": "CoreDataType", // CoreDataType for the function's return value
  "is_stream": "boolean", // true if this variable is time-indexed (e.g., input_signal[t])
  "stream_kind": "string_enum_or_null", // Optional, if is_stream is true. E.g., "INPUT", "OUTPUT", "INTERNAL_STATE"
  "initial_value": "object_or_null" // Optional: A constant node, a LAMBDA_EXPRESSION if data_type is FUNCTION_SIGNATURE, or null.
}
```

*Example of a variable holding a function signature:*
```json
{
  "declaration_type": "VARIABLE",
  "name": "myFunctionVar",
  "data_type": "FUNCTION_SIGNATURE",
  "parameter_types": ["NUMBER", "NUMBER"],
  "function_return_type": "BOOLEAN",
  "is_stream": false,
  "initial_value": null
}
```

#### 3.3.2. `FUNCTION_DECLARATION`
Declares the signature of a function or predicate. The implementation is plugin-dependent.
```json
{
  "declaration_type": "FUNCTION",
  "name": "string", // Unique name/identifier for the function
  "parameters": [ // Array of parameter objects
    {
      "name": "string", // Parameter name, unique within this function's scope
      "data_type": "string_enum" // Data type of the parameter. Can be "FUNCTION_SIGNATURE".
      // If data_type is "FUNCTION_SIGNATURE", the following two fields are required:
      // "parameter_types": ["CoreDataType", ...], // Array of CoreDataType for the function's parameters
      // "function_return_type": "CoreDataType" // CoreDataType for the function's return value
    }
    // ... more parameters
  ],
  "return_type": "string_enum" // Data type of the return value. Use "VOID" for procedures. Can be "FUNCTION_SIGNATURE".
  // If return_type is "FUNCTION_SIGNATURE", the following two fields are required to describe the signature of the returned function:
  // "return_parameter_types": ["CoreDataType", ...],
  // "return_function_return_type": "CoreDataType"
}
```

*Example of a function parameter that is itself a function:*
```json
{
  "declaration_type": "FUNCTION",
  "name": "applyOperation",
  "parameters": [
    {
      "name": "input_val",
      "data_type": "NUMBER"
    },
    {
      "name": "operation_func",
      "data_type": "FUNCTION_SIGNATURE",
      "parameter_types": ["NUMBER"],
      "function_return_type": "NUMBER"
    }
  ],
  "return_type": "NUMBER"
}
```

### 3.4. Statements and Rules

This section defines the structure of statements that form the core logic or rules of the specification. These statements utilize the declared entities and expressions defined earlier.

#### 3.4.1. `ASSIGNMENT_STATEMENT`
Assigns the result of an expression to a writable variable or stream.
```json
{
  "statement_type": "ASSIGNMENT",
  "target": {
    "node_type": "VARIABLE_REFERENCE", // Must refer to a declared variable/stream
    "name": "string",
    "temporal_qualifier": "object_or_null" // Relevant if assigning to a stream at a specific time
  },
  "expression": "object" // Any valid ILR expression node compatible with the target's data type
}
```

#### 3.4.2. `ASSERTION_STATEMENT` (or `CONSTRAINT_STATEMENT`)
Asserts that a Boolean expression must hold true.
```json
{
  "statement_type": "ASSERTION",
  "condition": {
    "node_type": "BOOLEAN_EXPRESSION" // The condition that must be true
  },
  "label": "string_or_null" // Optional descriptive label for the assertion
}
```

#### 3.4.3. `TEMPORAL_STATEMENT`
Applies a temporal operator to a Boolean condition.
```json
{
  "statement_type": "TEMPORAL_LOGIC",
  "operator": "string_enum", // E.g., "ALWAYS", "SOMETIMES" (or "EVENTUALLY"), "NEXT".
                               // Future: "UNTIL", "WEAK_UNTIL", "RELEASE"
  "condition": {
    "node_type": "BOOLEAN_EXPRESSION" // The condition subject to the temporal operator
  },
  "label": "string_or_null" // Optional descriptive label for the temporal statement
}
```

## 4. Overall ILR Document Structure

An ILR document is a single JSON object. It typically contains metadata, a list of declarations, and a list of statements.

```json
{
  "ilr_version": "string", // Version of the ILR specification (e.g., "0.1.0")
  "metadata": { // Optional
    "source_description": "string_or_null", // Description of the original natural language requirement
    "translation_timestamp": "string_or_null", // ISO 8601 timestamp
    // ... other relevant metadata
  },
  "declarations": [
    // Array of declaration objects (VARIABLE_DECLARATION, FUNCTION_DECLARATION)
  ],
  "statements": [
    // Array of statement objects (ASSIGNMENT_STATEMENT, ASSERTION_STATEMENT, TEMPORAL_STATEMENT, etc.)
  ]
}
```
