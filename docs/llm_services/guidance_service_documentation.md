# Documentation: Guidance Service (`guidance_service.py`)

**File Path:** `src/tau_translator_omega/llm_services/guidance_service.py`

## 1. Overview

This module provides a sophisticated, high-precision Tau code generation service by integrating Microsoft's Guidance framework. Unlike standard one-shot generation, this service implements a **self-correcting refinement loop**, enabling it to produce structured, syntactically valid Tau code that adheres to specific constraints.

Its primary role is to translate high-level natural language requirements into formal Tau specifications through a controlled, iterative process of generation, validation, and AI-driven correction.

---

## 2. Core Architecture: The Iterative Refinement Loop

The standout feature of this service is its autonomous refinement pipeline, which treats code generation not as a single action, but as a multi-step conversation with the AI:

1.  **Analyze**: The service first analyzes the user's natural language requirements to identify key entities and intent.
2.  **Generate**: It uses a Guidance program to generate an initial draft of the Tau code based on the analysis.
3.  **Validate**: The draft is passed to the `TauGrammarValidator`, an internal component that checks the code against a dictionary of regex-based grammar patterns.
4.  **Refine**: If the validator finds errors or missing patterns, the service constructs a new prompt that includes the original requirements, the flawed code, and the specific validation feedback. It then calls the Guidance model again, asking it to *correct* the code.
5.  **Repeat**: This generate-validate-refine loop continues until the code passes validation, the maximum number of iterations is reached, or a fallback is triggered.

This architecture ensures a much higher degree of reliability and syntactic correctness than is possible with simple prompting.

---

## 3. Key Components

### Data Contracts

-   **`GuidanceConfig`**: A dataclass for configuring the service, including the model to use (e.g., `microsoft/phi-2`), temperature, and caching settings.
-   **`TauGenerationRequest`**: The standardized input object. It contains the `requirements_text` and parameters to control the generation process, such as `validation_level` and `max_refinement_iterations`.
-   **`TauGenerationResult`**: The standardized output object. It provides not just the final `tau_code`, but also a `success` flag, a `confidence_score`, and detailed metadata about the generation process, including the number of refinement iterations and intermediate steps.

### Core Classes

-   **`GuidanceService`**: The main public class. It orchestrates the entire refinement loop, manages the model, and tracks performance statistics.
    -   **`generate_tau_code(request)`**: The primary public method that initiates a generation task.
-   **`TauGrammarValidator`**: A crucial internal component responsible for validating the generated Tau code. It uses a set of regular expressions to check for the presence and correctness of key Tau language constructs.

### Fallback Mechanisms

The service is designed for resilience. If the iterative AI refinement fails, it can fall back to:
-   **Template-based Generation**: `_generate_template_tau` can produce a basic, structured code block based on the initial analysis.
-   **Rule-based Refinement**: `_rule_based_refinement` can apply simple, deterministic fixes to the generated code.

---

## 4. Note on Refactoring

This file is over 700 lines long, which significantly exceeds the 600-line limit for production files. Its complexity, while powerful, makes it difficult to maintain.

**Recommendation**: For improved modularity and maintainability, the following components should be extracted into their own dedicated files:
-   `TauGrammarValidator`
-   The data classes (`GuidanceConfig`, `TauGenerationRequest`, `TauGenerationResult`)
-   The example usage/testing functions

This would allow the main `guidance_service.py` file to focus solely on the orchestration of the generation pipeline.
