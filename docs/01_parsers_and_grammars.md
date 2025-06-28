# Documentation: CNL Grammar Files

**Directory Path:** `src/tau_translator_omega/core_engine/parsers/cnl_parser/grammars/`

## 1. Overview

This directory contains the formal grammar definitions for the various dialects of the Controlled Natural Language (CNL) used in the TauTranslator system. These grammars are written in the `lark` EBNF format and are used by the `lark`-based parser (`parser.py`) to parse input text into a structured parse tree.

The presence of multiple grammar files indicates a modular and extensible architecture, allowing the system to support different versions or feature sets of the language.

---

## 2. Shared Grammar: `common.lark`

This file defines a set of common, reusable terminal symbols that are shared across the different CNL dialects. This is a good practice for grammar design, as it promotes consistency and reduces duplication.

### Key Terminals:

-   `SIGNED_NUMBER`: Defines the format for integers and floating-point numbers.
-   `ESCAPED_STRING`: Defines the format for single- and double-quoted strings.
-   `WS`: Defines whitespace characters, which are ignored by the parser.

---

## 3. Core Grammar: `tce.lark` (Tau Controlled English)

This is the main grammar file for the core Tau Controlled English language. It defines the fundamental syntax and structure of the language.

### Key Architectural Features:

-   **Modular Imports**: It correctly imports the shared terminals from `common.lark`.
-   **Top-Level Structure**: The grammar starts by defining a `sentence`, which can be a `fact`, a `rule`, or a `definition`.
-   **Operator Precedence**: It implements a standard operator precedence hierarchy for expressions, ensuring that arithmetic and boolean logic are parsed unambiguously (e.g., `and` is evaluated before `or`).
-   **Rich Syntax**: The grammar supports a sophisticated set of features, including:
    -   **Facts**: Simple statements of truth (e.g., `the sky is blue.`).
    -   **Rules**: Conditional logic using `if/then` constructs.
    -   **Definitions**: The ability to define new predicates or functions.
    -   **Quantifiers**: Support for `forall` and `exists` to make statements about collections of items.
-   **Keyword-Driven**: The language is built around a set of case-insensitive keywords (e.g., `IF`, `THEN`, `DEFINE`, `FORALL`), which provides a clear and structured syntax.

---

## 4. Strict Grammar: `tce_controlled.lark`

This grammar file defines a much stricter and more naturalistic dialect of CNL, explicitly based on the design principles of **Attempto Controlled English (ACE)**. Its goal is to provide a subset of English that is computer-parsable but reads more like natural language than a formal specification.

### Key Architectural Differences:

-   **Linguistic Structure**: Unlike `tce.lark`, which is structured like a traditional programming language grammar, this dialect is built around linguistic concepts like `noun_phrase`, `verb_phrase`, `relative_clause`, and `prepositional_phrase`.
-   **Strict Sentence Forms**: It defines explicit sentence patterns, such as:
    -   `simple_sentence`: Subject -> Verb -> Object
    -   `existential_sentence`: `There is a...`
    -   `conditional_sentence`: `If... then...`
-   **Rich Lexicon**: It defines a much larger and more specific set of terminals for common English words, including different forms of verbs (`BE_VERB`, `HAVE_KW`), pronouns (`HE_KW`, `THEM_KW`), prepositions, and determiners.
-   **Unambiguous by Design**: The grammar is designed to enforce rules that prevent ambiguity. For example, it specifies how relative clauses and prepositional phrases should attach to other parts of the sentence, which is a common source of ambiguity in natural language.

---

## 5. Declarative Grammar: `tce_declarative.lark`

This grammar defines a powerful, purely declarative specification language for expressing facts, relationships, and constraints about a system. Unlike the other grammars, it is not designed to parse natural language sentences but to provide a formal way to define system properties.

### Key Architectural Features:

-   **Purely Declarative**: The language contains no imperative commands. Every statement is a declaration of fact, a constraint that must hold, or a definition.
-   **Temporal Logic**: Its most advanced feature is the inclusion of temporal operators (`ALWAYS`, `EVENTUALLY`, `NEVER`). This allows for specifying system invariants and behaviors that must be true over time, which is critical for designing complex, stateful systems.
-   **Rich Specification Constructs**: It supports a wide range of declarative statements:
    -   `fact`: Simple assertions of truth (e.g., `x IS positive`).
    -   `relationship`: How entities relate to one another (`system CONTAINS component`).
    -   `constraint`: Rules that must always be true, using quantifiers like `FOR_ALL` and `THERE_EXISTS`.
    -   `definition`: The ability to define new terms and concepts.
-   **Formal and Unambiguous**: While it uses English keywords, the structure is formal and symbolic, designed for precise, machine-readable specifications.
