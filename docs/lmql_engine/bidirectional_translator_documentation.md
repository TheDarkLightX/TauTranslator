# Documentation: LMQL Bidirectional Translator (`bidirectional_translator.py`)

**File Path:** `src/tau_translator_omega/lmql_engine/bidirectional_translator.py`

## 1. Overview

This module represents a masterclass in modern software architecture, providing a highly flexible and maintainable engine for bidirectional translation between Tau Language and Tau Controlled English (TCE). It is the result of a significant refactoring effort, transforming a large, monolithic script into a clean, component-based system that follows core VibeArchitect principles.

The key feature of this module is its ability to dynamically switch between different translation algorithms at runtime.

---

## 2. Core Architectural Patterns

This module's design is built on a foundation of proven software design patterns:

-   **Strategy Pattern**: This is the central pattern. The main `LMQLBidirectionalTranslator` class does not contain any translation logic itself. Instead, it delegates the translation task to a `TranslationStrategy` object. This allows the system to use different translation methods (e.g., a pattern-based approach vs. a more advanced LMQL-based one) interchangeably.
-   **Factory Pattern**: To further decouple the components, the responsibility of creating these strategy objects is given to a `TranslationStrategyFactory`. This makes the system highly extensible; adding a new translation algorithm is as simple as creating a new strategy class and registering it with the factory.
-   **Facade / Legacy Wrapper**: The module provides a clean, modern API via the `LMQLBidirectionalTranslator` class and its associated factory function, `create_bidirectional_translator`. To ensure a smooth transition and backward compatibility, it also includes the `LMQLBidirectionalTranslatorLegacy` class, which acts as a wrapper around the new implementation, exposing the original API.

---

## 3. Key Components

-   **`LMQLBidirectionalTranslator`**: The primary public class. It acts as a coordinator, managing the currently selected translation strategy and handling high-level tasks like performance monitoring and error handling.
    -   `translate_tce_to_tau()` / `translate_tau_to_tce()`: The main translation methods. They delegate the actual work to the active strategy.
    -   `switch_strategy()`: Allows the client to change the translation algorithm on the fly.
    -   `get_translation_stats()`: Provides valuable performance metrics, such as success rate and total translations, for the current session.

-   **`LMQLBidirectionalTranslatorLegacy`**: A compatibility wrapper that ensures older parts of the codebase can continue to function without modification by calling the new, refactored implementation under the hood.

-   **Factory and Convenience Functions**:
    -   `create_bidirectional_translator()`: The recommended factory function for creating a new translator instance.
    -   `translate_tce_to_tau()` / `translate_tau_to_tce()`: Standalone convenience functions for performing a quick, one-off translation without needing to manually instantiate the class.

---

## 4. Separation of Concerns

This module is a prime example of the Single Responsibility Principle:

-   The **Translator** is responsible for *coordinating* the translation.
-   The **Strategies** are responsible for the *implementation* of the translation.
-   The **Factories** are responsible for the *creation* of the strategies.

This clear separation makes the codebase significantly easier to understand, test, and extend compared to a monolithic design.
