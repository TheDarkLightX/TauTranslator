# Documentation: Pattern Analyzers (`pattern_analyzers.py`)

**File Path:** `src/tau_translator_omega/lmql_engine/pattern_analyzers.py`

## 1. Overview

This module is the foundational layer for the `PatternBasedTranslationStrategy`. It was extracted from the main translator script to create a focused, dedicated component responsible for a single task: understanding and categorizing input text.

These analyzers are the "eyes" of the rule-based translation engine. They deconstruct raw text into a structured set of recognized patterns, which the `PatternBasedTranslationStrategy` then uses as a blueprint for the translation process. The module provides specialized analyzers for both the formal Tau language and the more ambiguous Tau Controlled English (TCE).

---

## 2. Core Architectural Patterns

-   **Strategy Pattern**: The `PatternAnalyzer` abstract base class defines a common interface (`analyze_text`), allowing different analyzers to be used interchangeably.
-   **Factory Pattern**: The `PatternAnalyzerFactory` provides a clean, centralized method for creating analyzer instances, decoupling client code from the concrete analyzer classes.
-   **Single Responsibility Principle**: Each analyzer class has one job: analyze one specific language (`Tau` or `TCE`).

---

## 3. Key Components

### `PatternAnalyzer` (Abstract Base Class)

This class defines the contract for all pattern analyzers, ensuring they all have a consistent `analyze_text` method.

### `TauPatternAnalyzer`

This class is a specialist in the formal, structured **Tau language**.

-   **Mechanism**: It uses a comprehensive dictionary of regular expressions to systematically find and categorize all known Tau constructs within a given text. It can identify everything from function definitions and stream declarations to temporal logic statements and solver commands.
-   **Output**: It returns all patterns it finds, as the formal syntax of Tau means there is little to no ambiguity.

### `TCEPatternAnalyzer`

This class is designed to handle the more flexible and potentially ambiguous **Tau Controlled English**.

-   **Mechanism**: Like its Tau counterpart, it uses a dictionary of regex patterns to identify known English phrases and structures.
-   **Key Innovation: Priority Matching**: The `TCEPatternAnalyzer`'s most important feature is its `_pattern_priority` list. Natural language can be ambiguous, and a single sentence might match multiple patterns. This priority list allows the analyzer to determine the **best** or most likely intended pattern. The `get_best_match()` method iterates through this list to find the highest-priority match, which is critical for resolving ambiguity and ensuring the most accurate translation.

### `PatternAnalyzerFactory`

Following the established design of the `lmql_engine`, this factory provides a simple, static interface (`create_analyzer`) for instantiating the correct analyzer on demand. This promotes loose coupling and makes the system easier to manage and test.
