# Tau Translator

**A Python library for translating Tau Controlled English (TCE) into canonical Tau language specifications.**

[![Status](https://img.shields.io/badge/Status-Alpha-yellow)](#)
[![Tests](https://img.shields.io/badge/Tests-Passing-green)](#running-tests)
[![Language](https://img.shields.io/badge/Language-Python-blue)](#)

## Mission

This project provides a bridge between human-readable language and the formal, verifiable logic of the Tau Language. It offers a deterministic parser that translates a carefully designed subset of English (TCE) into precise Tau specifications, enabling users to write formal logic in a more intuitive way.

## Key Features

- **Deterministic Translation**: Uses a robust LARK-based grammar to ensure that a given TCE sentence always produces the same Tau output.
- **Broad Feature Coverage**: Supports a wide range of logical constructs, including:
  - Factual statements (`Socrates is a man`)
  - Relations (`Plato teaches Aristotle`)
  - Universal quantifiers (`every car is a vehicle`)
  - Existential quantifiers (`some animal is a mammal`)
  - Boolean logic (`X is a cat and X is fluffy`)
  - Recursive definitions
- **Fully Tested**: A comprehensive `pytest` suite ensures the reliability and correctness of the translator.

## Getting Started

### Prerequisites
- Python 3.9+

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/TheDarkLightX/TauTranslator.git
    cd TauTranslator
    ```

2.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

The translator is managed through a central `TranslationManager` accessed via a dependency injection container. Here is a simple example of how to perform a translation:

```python
from backend.unified.di_container import container
from backend.unified.domain.source_text import SourceText, TranslationDirection

# 1. Get the translation manager from the container
translation_manager = container.translation_manager()

# 2. Define the text to translate
sentences = [
    "every man is mortal",
    "some animal is a mammal",
    "Plato teaches Aristotle"
]

# 3. Translate each sentence from TCE to Tau
for tce_text in sentences:
    source = SourceText(text=tce_text)
    result = translation_manager.translate(
        source_text=source,
        direction=TranslationDirection.TCE_TO_TAU
    )

    # 4. Print the result
    if result.is_success():
        print(f'"{tce_text}" -> {result.value.translated_text}')
    else:
        print(f'Translation failed for "{tce_text}": {result.failure().message}')
```

**Expected Output:**
```
"every man is mortal" -> forall X : (man(X) -> mortal(X)).
"some animal is a mammal" -> exists X : (animal(X) and mammal(X)).
"Plato teaches Aristotle" -> teaches(Plato, Aristotle).
```

## Running Tests

We use `pytest` for all testing. To run the full test suite, execute the following command from the project's root directory:

```bash
pytest -v
```

## Documentation

The primary guide for understanding the mapping between Tau Controlled English and canonical Tau is located in the `/docs` directory:

- **[docs/tce_to_tau_mapping.md](docs/tce_to_tau_mapping.md)**: Explains the translation rules, Tau language limitations, and provides clear examples.

## Contributing

Contributions are welcome! Please see the **[Contributing Guide](docs/CONTRIBUTING.md)** for more details on how to submit pull requests, report bugs, and improve documentation.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.