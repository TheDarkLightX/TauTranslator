# Documentation: Requirements Analyzer

**File:** `src/tau_translator_omega/core_engine/translators/nlp_enhanced/requirements_analyzer.py`

This document provides a detailed explanation of the `RequirementsAnalyzer` class, which is responsible for parsing natural language requirements and converting them into a structured, machine-readable format.

---

## 1. Overview

The `RequirementsAnalyzer` is the core engine for understanding unstructured requirements text. It leverages a combination of the **spaCy** NLP library and custom rule-based pattern matching to perform a deep analysis of each sentence. Its key responsibilities include:

-   **Sentence Segmentation**: Breaking down large blocks of text into individual, analyzable sentences.
-   **Requirement Classification**: Identifying the type of each requirement (e.g., `CONSTRAINT`, `BEHAVIOR`, `PERFORMANCE`).
-   **Entity and Predicate Extraction**: Finding the key actors (nouns) and actions (verbs) in the text.
-   **Logical and Temporal Analysis**: Detecting logical structures (e.g., `if/then`, `and/or`) and temporal constraints (e.g., `always`, `within 5 seconds`).
-   **Formal Constraint Extraction**: Translating parts of the requirement into a semi-formal logical representation.
-   **Confidence Scoring**: Assigning a confidence score to each extracted requirement to indicate the likelihood of a correct analysis.

## 2. Initialization

The analyzer is instantiated via the `create_requirements_analyzer()` factory function or by directly calling its constructor.

```python
from .requirements_analyzer import create_requirements_analyzer

analyzer = create_requirements_analyzer()
```

Upon initialization, the `RequirementsAnalyzer` attempts to load the `en_core_web_sm` spaCy model. If spaCy is not available or the model cannot be found, it gracefully falls back to a non-spaCy mode with limited functionality.

## 3. Public API

### `extract_requirements(text: str) -> List[RequirementItem]`

This is the primary method for processing a single block of natural language text. It splits the text into sentences and analyzes each one individually.

-   **Args**:
    -   `text` (`str`): A string containing one or more requirements.
-   **Returns**:
    -   A list of `RequirementItem` data models, each representing a structured requirement.

### `extract_requirements_from_document(document: str) -> List[RequirementItem]`

This method is designed to process a full requirements document, which may contain section headers that provide additional context.

-   **Args**:
    -   `document` (`str`): A multi-paragraph string containing the entire document.
-   **Returns**:
    -   A list of `RequirementItem` data models.

## 4. Internal Workflow

The analysis process follows a clear pipeline, orchestrated by a series of private helper methods:

1.  **`_split_into_sections` / `_split_into_sentences`**: The input text is first segmented into sections (if applicable) and then into individual sentences.
2.  **`_analyze_sentence`**: Each sentence is processed through this core method, which calls the other private methods to build a `RequirementItem`.
3.  **`_classify_requirement_type`**: Uses keyword indicators (e.g., "must", "shall", "when") to classify the sentence into a `RequirementType`.
4.  **`_extract_entities`**: Uses spaCy's Named Entity Recognition (NER) to identify key nouns and actors.
5.  **`_extract_predicates`**: Identifies the main actions (verbs) in the sentence.
6.  **`_analyze_logical_structure`**: Applies regular expressions to find logical, conditional, and temporal operators, populating a `LogicalStructure` model.
7.  **`_extract_formal_constraints`**: Attempts to convert parts of the sentence into a `FormalConstraint` model.
8.  **`_calculate_confidence`**: Calculates a confidence score based on the presence of formal language and the absence of ambiguous terms.

## 5. Pattern Matching

The analyzer uses several regular expression patterns to identify key linguistic features. These are defined in the `__init__` method and include:

-   **`quantifier_patterns`**: To find words like "all", "every", "any".
-   **`conditional_patterns`**: To find phrases like "if...then", "when".
-   **`logical_operator_patterns`**: To find connectives like "and", "or", "not".
-   **`temporal_patterns`**: To find temporal constraints like "before", "after", "within X seconds".

This combination of a powerful NLP library and targeted rule-based matching allows the `RequirementsAnalyzer` to perform a robust and nuanced analysis of requirements text.
