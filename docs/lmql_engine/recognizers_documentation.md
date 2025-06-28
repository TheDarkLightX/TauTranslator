# Documentation: Pattern Recognizers (`recognizers.py`)

**File Path:** `src/tau_translator_omega/lmql_engine/recognizers.py`

## 1. Overview

This module represents the final and most advanced component of the pattern-based translation engine. It provides a set of specialized, expert systems for identifying and translating complex, domain-specific Tau language constructs that are beyond the scope of simple regular expressions.

This file works in concert with `pattern_analyzers.py` to create a powerful, two-layer recognition system:
1.  **Broad Analysis (`PatternAnalyzer`)**: Performs the initial, high-level scan to identify general syntactic structures.
2.  **Specialized Recognition (`PatternRecognizer`)**: When a complex structure is suspected, a dedicated `PatternRecognizer` is deployed to perform a deep, expert analysis.

---

## 2. Core Architectural Patterns

-   **Strategy Pattern**: Each `PatternRecognizer` is a self-contained strategy for handling one specific type of complex pattern (e.g., arithmetic, temporal logic).
-   **Factory Pattern**: The `RecognizerFactory` manages the creation and deployment of these specialized recognizer instances.
-   **Facade Pattern**: The `RecognizerFactory.recognize_any()` method provides a simple facade, allowing a client to easily run all recognizers on a piece of text.

---

## 3. Key Components

### `PatternRecognizer` (Abstract Base Class)

This class defines the contract for all specialized recognizers. It is more advanced than the `PatternAnalyzer` contract, requiring three distinct methods:
-   `recognize()`: Deconstructs a complex text pattern into its fundamental, named components (e.g., identifying the inputs, outputs, and operator of an arithmetic expression).
-   `translate_to_tce()`: Uses the components from a successful recognition to construct a grammatically correct sentence in Tau Controlled English.
-   `translate_to_tau()`: Uses the components to reconstruct the formal Tau language statement.

### Concrete Recognizer Implementations

This module provides a suite of expert recognizers for various domains:
-   `BinaryArithmeticRecognizer`: Understands complex arithmetic circuits like full adders and multipliers.
-   `StreamRecognizer`: Handles various forms of stream I/O (file, console).
-   `LogicGateRecognizer`: Recognizes fundamental logic gates (AND, OR, NOT, etc.).
-   `ConsensusRecognizer`: Identifies patterns related to distributed consensus algorithms, like majority voting.
-   `TemporalRecognizer`: Specializes in temporal logic operators like `delay`, `always`, and `eventually`.

### `RecognizerFactory`

This factory is the orchestrator of the recognition process.
-   It can create specific recognizer instances on demand (`create_recognizer`).
-   More powerfully, its `get_all_recognizers()` and `recognize_any()` methods allow the system to deploy all of its experts at once to see if any of them can make sense of the input text. This provides a robust and extensible mechanism for handling a wide variety of complex patterns.

---

## 4. Note on Refactoring

This file currently exceeds the recommended 600-line limit for production code. While its internal structure is sound, its size makes it difficult to maintain.

**Recommendation**: In a future refactoring cycle, each `PatternRecognizer` class should be moved into its own file within a `recognizers` sub-directory (e.g., `recognizers/arithmetic.py`, `recognizers/temporal.py`). This would significantly improve modularity and align the codebase with best practices for maintainability.
