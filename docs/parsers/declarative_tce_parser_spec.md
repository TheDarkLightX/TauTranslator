# Declarative Tau Controlled English (TCE) Parser Specification (Alpha)

**Version:** 0.1.0
**Status:** Alpha / Proof of Concept

## 1. Overview

The Declarative TCE Parser is designed to translate a constrained subset of English sentences into formal Tau logical predicates. Its purpose is to provide a simple, human-readable interface for defining facts and rules within the Tau system.

This document outlines the exact grammar and capabilities of the parser in its current alpha state. While the core translation mechanism is functional for the patterns listed below, the parser is not yet considered production-ready.

## 2. Supported Grammar Patterns

The parser currently supports the following atomic sentence structures.

### 2.1. Simple Facts (Entity Relationships)

These sentences establish a relationship between two entities.

-   **Pattern:** `[Subject] [Verb] [Object].`
-   **Supported Verbs:** `owns`, `has`, `is a`
-   **Examples:**
    -   `john owns a house.` -> `owns(john, a_house)`
    -   `a car has a wheel.` -> `has(a_car, a_wheel)`
    -   `socrates is a man.` -> `is_a(socrates, man)`

### 2.2. Quantified Properties

These sentences declare that all members of a certain class must possess a specific property.

-   **Pattern:** `all [Plural Noun] must have [Property].`
-   **Supported Verbs:** `must have`
-   **Example:**
    -   `all users must have valid passwords.` -> `forall x. (is_user(x) -> has_valid_password(x))`

## 3. Current Limitations & Roadmap to Production

The current implementation is a successful proof of concept but has significant limitations that must be addressed before it can be considered production-ready.

### 3.1. Known Limitations

-   **Limited Vocabulary:** The set of recognized verbs and quantifiers is extremely small.
-   **No Error Recovery:** Invalid sentences will cause the parser to fail with a raw exception. There is no user-friendly error reporting.
-   **Minimal Test Coverage:** The test suite only covers the exact patterns listed above. It does not test edge cases, failures, or more complex sentence structures.
-   **No Integration Testing:** The parser has only been tested in isolation. Its integration with the broader TauTranslator application is unverified.
-   **No Complex Sentences:** The grammar does not support conjunctions (`and`, `or`), nested clauses, temporal logic, or other advanced constructs.

### 3.2. Roadmap to Production-Ready

1.  **Grammar Expansion:** Systematically expand the grammar to include a wider range of verbs, quantifiers, and sentence structures.
2.  **Robust Error Handling:** Implement a comprehensive error-handling layer that catches invalid input and provides clear, actionable feedback to the user.
3.  **Comprehensive Test Suite:** Develop a full BDD/TDD test suite covering valid inputs, expected failures, edge cases, and integration points.
4.  **Full Integration:** Integrate the parser into the main application and verify its end-to-end functionality.
5.  **Complete Documentation:** Finalize user and developer documentation for the production-ready version.
