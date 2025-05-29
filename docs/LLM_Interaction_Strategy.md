# LLM Interaction Strategy for ILR Generation

## 1. Overview

This document outlines the strategy for leveraging a Large Language Model (LLM) to translate natural language (NL) user requirements into the Intermediate Logical Representation (ILR) JSON format, as defined by `ILR_Specification.md` and validated by `ilr_schema.json`.

The primary goal is to enable users to specify system behaviors or properties in natural language, which the TauTranslatorOmega core engine can then convert into a formal ILR structure suitable for further processing by plugins.

## 2. Core Principles

-   **Accuracy:** The generated ILR must accurately reflect the user's intent expressed in NL.
-   **Validity:** The generated ILR JSON must strictly conform to `ilr_schema.json`.
-   **Clarity:** When NL input is ambiguous or underspecified, the LLM should seek clarification rather than making assumptions that could lead to incorrect ILR.
-   **Iterative Refinement:** The process should support iterative refinement, allowing users to correct or elaborate on their NL input or the generated ILR.

## 3. Process Flow

The interaction will generally follow these steps:

1.  **User Input:** The user provides a natural language description of a requirement, property, or behavior.
2.  **Prompt Construction:** The core engine constructs a detailed prompt for the LLM. This includes:
    *   The user's NL input.
    *   A system message defining the LLM's role, the task, and output expectations.
    *   Essential context from `ILR_Specification.md` (e.g., definitions of core data types, node types, and their structures). This might be a condensed version or key excerpts to manage token limits.
    *   Reference to or key aspects of `ilr_schema.json` to guide the structure of the output.
    *   Few-shot examples of NL-to-ILR mappings.
    *   Current date/time (if relevant for resolving temporal NL expressions).
3.  **LLM Invocation:** The prompt is sent to the selected LLM.
4.  **LLM Response Processing:** The core engine receives the LLM's response, which could be:
    *   The generated ILR JSON string.
    *   A request for clarification if the NL input was ambiguous.
    *   An indication that it cannot fulfill the request with the given input.
5.  **Validation:**
    *   **Syntactic Validation:** If ILR JSON is received, it's first validated against `docs/schemas/ilr_schema.json`.
    *   **Semantic Validation (Basic):** Initial semantic checks could be performed (e.g., ensuring `node_type` values are consistent with the data provided). Deeper semantic validation (e.g., type checking across expressions, variable usage) is a more advanced topic.
6.  **Feedback Loop & Refinement:**
    *   **Schema Validation Errors:** If schema validation fails, the errors are presented to the LLM (potentially with the erroneous JSON) for correction in a subsequent turn.
    *   **Clarification Requests:** If the LLM asks for clarification, these questions are relayed to the user. The user's response is then used to re-prompt the LLM.
    *   **User Review:** Successfully validated ILR is presented to the user for review. The user can accept it, or provide further NL instructions to modify it.

## 4. Prompt Engineering

### 4.1. System Prompt

The system prompt will establish the LLM's persona and task:

```
You are an expert assistant for the TauTranslatorOmega system. Your task is to translate natural language (NL) user requirements into a structured Intermediate Logical Representation (ILR) JSON format.

You MUST adhere to the ILR v0.1 specification. Key aspects include:
- Core Data Types: BOOLEAN, NUMBER, STRING, VOID, BITVECTOR, BITSTRING.
- ILR Document Structure: Consists of 'ilr_version', 'metadata' (optional), 'declarations' (array), and 'statements' (array).
- Node Types: Ensure you use the correct 'node_type', 'declaration_type', or 'statement_type' for each construct.
- Output Format: Your output MUST be a single, valid JSON object conforming to the ILR schema. Do not include any explanatory text outside the JSON structure itself unless explicitly asked to clarify.

If the user's NL requirement is ambiguous or lacks sufficient detail to generate valid ILR, you MUST ask clarifying questions. Do not make assumptions.
If you generate ILR, ensure it is a complete and valid JSON object.
```

### 4.2. User Request Prompt Structure

A user request prompt will typically combine the system prompt (or a reference to it) with:

-   The specific NL input from the user.
-   Few-shot examples demonstrating NL-to-ILR conversion.
-   (Potentially) Condensed snippets from `ILR_Specification.md` relevant to the user's query, if identifiable.

### 4.3. Few-Shot Examples

Examples will be crucial for guiding the LLM.
*(Example to be added here)*
E.g.,
NL: "The signal 'temperature' should always be less than 100."
ILR:
```json
{
  "ilr_version": "0.1.0",
  "declarations": [
    {
      "declaration_type": "VARIABLE",
      "name": "temperature",
      "data_type": "NUMBER",
      "is_stream": true,
      "stream_kind": "INPUT"
    }
  ],
  "statements": [
    {
      "statement_type": "TEMPORAL_LOGIC",
      "operator": "ALWAYS",
      "condition": {
        "node_type": "COMPARISON_EXPRESSION",
        "operator": "LESS_THAN",
        "lhs": {
          "node_type": "VARIABLE_REFERENCE",
          "name": "temperature"
        },
        "rhs": {
          "node_type": "NUMERIC_CONSTANT",
          "value": 100
        }
      },
      "label": "temperature_limit_check"
    }
  ]
}
```

## 5. Handling Ambiguity and Clarification

-   The LLM will be explicitly instructed to ask for clarification if the NL is ambiguous, underspecified, or seems contradictory.
-   Clarification prompts from the LLM will be presented to the user.
-   The user's answers will be incorporated into a revised prompt for the LLM.

## 6. Validation and Error Correction

-   **Schema Validation:** All LLM-generated ILR JSON will be validated against `docs/schemas/ilr_schema.json`.
-   **Error Feedback to LLM:** If validation fails, the LLM will be re-prompted with the original NL, the erroneous JSON it generated, and the validation error messages from the schema validator. It will be asked to correct its output.

```
The previous ILR JSON you generated was:
<erroneous_json>

It failed schema validation with the following errors:
<validation_errors>

Please correct the ILR JSON based on the original natural language requirement and these errors.
Original NL: <original_nl>
```

## 7. Context Management

-   **ILR Specification Snippets:** For complex requests, relevant sections of the `ILR_Specification.md` might be dynamically included in the prompt to provide targeted context without overwhelming the LLM.
-   **Conversation History:** For iterative refinement, a summary of the conversation or key decisions from previous turns might be included.

## 8. Future Considerations

-   **Advanced Semantic Validation:** Implementing more sophisticated semantic checks post-LLM generation.
-   **LLM Fine-tuning:** For higher accuracy and more nuanced understanding, fine-tuning a base LLM on a curated dataset of NL-to-ILR pairs could be explored.
-   **Tool Use by LLM:** Allowing the LLM to "query" specific parts of the ILR specification or schema if it needs more information.
-   **Confidence Scores:** Having the LLM provide a confidence score for its generated ILR.

This strategy provides a starting point and will be refined based on empirical results and further development of the TauTranslatorOmega system.
