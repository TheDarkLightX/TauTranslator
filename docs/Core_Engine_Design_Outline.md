# TauTranslatorOmega - Core Engine Design Outline

## 1. Overview

This document provides a high-level design outline for the TauTranslatorOmega core engine. The engine is responsible for orchestrating the translation of natural language (NL) user requirements into an Intermediate Logical Representation (ILR), managing plugins, and facilitating the final translation to a target grammar via these plugins.

## 2. Core Principles

-   **Modularity:** Components should be loosely coupled and well-defined.
-   **Extensibility:** The design should easily accommodate new plugins and potentially new ILR versions or features.
-   **Robustness:** The engine should handle errors gracefully, from NL processing to plugin execution.
-   **Configurability:** Key aspects like plugin directories and LLM endpoints should be configurable.

## 3. Main Components and Responsibilities

The core engine can be conceptualized as having the following major components:

### 3.1. NL Processing & ILR Generation Orchestrator

-   **Responsibilities:**
    -   Manages interaction with the configured Large Language Model (LLM) as per `LLM_Interaction_Strategy.md`.
    -   Constructs prompts for the LLM, incorporating user NL input, specification context, and schema guidance.
    -   Receives ILR JSON (or clarification requests) from the LLM.
    -   Orchestrates the validation of LLM-generated ILR against `ilr_schema.json`.
    -   Manages the feedback loop with the LLM for corrections or clarifications.
    -   Presents validated ILR to the user for review and potential iterative refinement.
-   **Key Interactions:**
    -   User Interface (for NL input and feedback).
    -   LLM Service.
    -   JSON Schema Validator.
    -   Plugin Manager (once ILR is finalized and ready for translation).

### 3.2. Plugin Manager

-   **Responsibilities:**
    -   Discovers available plugins by scanning the configured plugin directory(ies).
    -   Parses and validates `plugin_manifest.json` for each discovered plugin against `plugin_manifest_schema.json`.
    -   Registers valid plugins and maintains a registry of their capabilities (e.g., supported ILR versions, target grammars).
    -   Handles plugin selection based on user choice or task requirements (e.g., matching target grammar).
    -   Manages the lifecycle of plugin execution.
-   **Key Interactions:**
    -   Filesystem (for plugin discovery).
    -   JSON Schema Validator.
    -   Translation Workflow Controller.

### 3.3. Translation Workflow Controller

-   **Responsibilities:**
    -   Receives a finalized ILR document (as a JSON object/string) and a target plugin selection.
    -   Prepares inputs for the selected plugin according to its `entry_point` type (initially focusing on "command_line").
        -   Serializes ILR to JSON string for stdin.
        -   Prepares configuration options (if any) and passes them as per the plugin interface spec (e.g., base64 encoded argument).
    -   Invokes the plugin (e.g., executes the command for CLI plugins).
    -   Captures `stdout` (for Translation Result JSON) and `stderr` (for logs/diagnostics) from the plugin.
    -   Parses and validates the Translation Result JSON from `stdout` against `translation_result_schema.json`.
    -   Handles errors reported by the plugin or issues during plugin execution.
    -   Returns the final translated text (or error information) to the orchestrator or user interface.
-   **Key Interactions:**
    -   Plugin Manager (to get plugin details and execute it).
    -   Operating System (for process execution, stdin/stdout/stderr handling for CLI plugins).
    -   JSON Schema Validator.
    -   ILR Generation Orchestrator (to receive ILR and return results).

### 3.4. Configuration Manager (Conceptual)

-   **Responsibilities:**
    -   Provides access to system-wide configurations (e.g., path to plugin directory, LLM API keys/endpoints, default logging levels).
    -   Loads configuration from files or environment variables.
-   **Key Interactions:**
    -   All other core components.

### 3.5. JSON Schema Validator (Utility)

-   **Responsibilities:**
    -   A utility component/library used by other components to validate JSON data against the defined schemas:
        -   `ilr_schema.json`
        -   `plugin_manifest_schema.json`
        -   `translation_result_schema.json`
-   **Key Interactions:**
    -   ILR Generation Orchestrator.
    -   Plugin Manager.
    -   Translation Workflow Controller.

## 4. High-Level Data Flow Example (NL to Target Grammar)

1.  User provides NL requirement.
2.  **NL Processing & ILR Generation Orchestrator** sends NL to LLM.
3.  LLM returns ILR JSON.
4.  Orchestrator validates ILR JSON using **JSON Schema Validator**. (Iterates with LLM if invalid).
5.  User reviews and confirms ILR.
6.  Orchestrator passes confirmed ILR and target choice to **Translation Workflow Controller**.
7.  Controller requests plugin details from **Plugin Manager**.
8.  Controller executes the selected plugin, passing ILR and config.
9.  Plugin returns Translation Result JSON.
10. Controller validates Translation Result JSON using **JSON Schema Validator**.
11. Controller extracts translated text (or error) and returns it.

## 5. Future Considerations

-   **State Management:** How application state (e.g., current ILR, user preferences) is managed.
-   **User Interface (UI/CLI):** How users interact with the core engine.
-   **Logging and Diagnostics:** Centralized logging mechanism.
-   **Caching:** Caching ILR generated from NL or plugin translation results.

This outline serves as an initial architectural sketch and will be elaborated upon during detailed design and implementation phases.
