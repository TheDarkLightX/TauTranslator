# Documentation: Translator Factory

**File:** `src/tau_translator_omega/core_engine/translators/nlp_enhanced/translator_factory.py`

This document describes the `TranslatorFactory`, a key architectural component that provides a centralized, configurable system for creating all translator-related objects. It encapsulates the complexity of instantiating and configuring the various parts of the NLP-enhanced translation system.

---

## 1. Design Patterns: Factory, Builder, and Strategy

The `translator_factory.py` module is a powerful example of several key design patterns working together:

-   **Factory Pattern**: The `TranslatorFactory` class provides a set of static methods (`create_*`) for producing different types of translators and their components (e.g., `create_english_to_tau_translator`, `create_requirements_analyzer`). This hides the complex creation logic from the client.
-   **Builder Pattern**: The `TranslatorConfig` dataclass acts as a builder object. It allows the user to specify a wide range of configuration options in a clear and readable way. This configuration object is then passed to the factory to build the desired translator.
-   **Strategy Pattern**: The configuration allows for different translation strategies (e.g., `PATTERN_BASED`, `SEMANTIC_ENHANCED`) to be plugged into the translator, allowing its core algorithm to be changed at runtime.

## 2. Core Components

### `TranslatorConfig`

This dataclass is the heart of the configuration system. It provides a comprehensive set of options to customize the translator's behavior, including:

-   **Core Settings**: Toggling major features like AMR analysis or incremental parsing.
-   **Performance Settings**: Adjusting parameters like cache size and timeouts.
-   **Domain Specialization**: Specifying domains like `MEDICAL` or `FINANCIAL` to load specialized vocabularies and patterns.
-   **Translation Strategy**: Selecting the core translation algorithm.
-   **Quality Settings**: Enforcing high confidence thresholds for mission-critical applications.

### `TranslatorFactory`

This class is the public entry point for creating translators. It provides two main types of creation methods:

1.  **Component Creators**:
    -   `create_english_to_tau_translator(config)`
    -   `create_requirements_analyzer(config)`
    -   `create_amr_analyzer(config)`
    -   `create_incremental_parser(config)`

    These methods create individual components, applying the specified `TranslatorConfig`.

2.  **Pre-configured "Recipe" Creators**:
    -   `create_medical_translator()`
    -   `create_financial_translator()`
    -   `create_security_translator()`
    -   `create_high_performance_translator()`
    -   `create_high_accuracy_translator()`

    These are convenience methods that return a translator pre-configured for a specific use case. For example, `create_high_accuracy_translator` returns a translator with AMR analysis enabled and a high confidence threshold, while `create_high_performance_translator` might use a faster, pattern-based strategy with a larger cache.

## 3. How to Use the Factory

The factory provides a clean and simple interface for getting a translator instance.

**Simple Usage (Default Configuration):**

```python
# Get a standard, default-configured translator
translator = TranslatorFactory.create_english_to_tau_translator()
```

**Advanced Usage (Custom Configuration):**

```python
# Define a custom configuration
my_config = TranslatorConfig(
    domain_specializations=[DomainSpecialization.FINANCIAL],
    confidence_threshold=0.85,
    enable_detailed_logging=True
)

# Create a translator with the custom configuration
financial_translator = TranslatorFactory.create_english_to_tau_translator(config=my_config)
```

**Recipe-Based Usage:**

```python
# Get a translator pre-configured for maximum accuracy
highly_accurate_translator = TranslatorFactory.create_high_accuracy_translator()
```

By encapsulating the complex setup logic, the `TranslatorFactory` makes the entire translation system much more approachable, maintainable, and extensible.
