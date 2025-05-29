# Plugin Interface Specification

## 1. Overview

This document specifies the interface between the TauTranslatorOmega core engine and grammar-specific plugins. Plugins are responsible for translating the Intermediate Logical Representation (ILR) into a concrete target language or formalism.

## 2. Plugin Discovery and Loading

The TauTranslatorOmega core engine discovers plugins by scanning a designated `plugins` directory.
- By default, this directory is named `plugins` and is located at the root of the TauTranslatorOmega application. This path may be user-configurable.
- Each direct subdirectory within the `plugins` directory is treated as a potential plugin.
- The core engine expects to find a `plugin_manifest.json` file (as defined in Section 3) in the root of each such subdirectory.
- If a `plugin_manifest.json` file is found and successfully parsed, and its declared `ilr_versions_supported` array contains the ILR version string currently used by the core engine (e.g., if core uses "0.1.0", the plugin must list "0.1.0" as one of its supported versions), the plugin is registered.
- Plugin `id`s (from the manifest) must be unique across all loaded plugins. If duplicate `id`s are encountered, the core engine will log an error and will not load any plugin whose ID conflicts with an already registered plugin.

## 3. Plugin Capabilities Declaration

Plugins must declare their capabilities and metadata. This is typically done via a manifest file named `plugin_manifest.json` located in the root of the plugin's directory.

The structure of `plugin_manifest.json` is as follows:

```json
{
  "manifest_version": "1.0", // Version of this manifest schema
  "id": "string", // Unique machine-readable identifier for the plugin (e.g., "idni-tau-lang-official-v1.2"). It is recommended to use a reverse-domain-like naming convention (e.g., "com.example.my-plugin-name") to promote global uniqueness.
  "name": "string", // Human-readable name for the plugin (e.g., "Tau Language (IDNI Official) Plugin")
  "description": "string", // Brief description of the plugin's purpose
  "version": "string", // Plugin's own semantic version (e.g., "1.2.0")
  "author": "string_or_null", // Author or organization
  "license": "string_or_null", // License of the plugin code (e.g., SPDX ID or custom license text)
  "target_grammar": {
    "name": "string", // Name of the target grammar (e.g., "Tau-IDNI")
    "version_constraint": "string_or_null" // Semantic versioning constraint for the target grammar (e.g., ">=1.0.0 <2.0.0")
  },
  "ilr_versions_supported": ["string"], // Array of ILR specification versions this plugin can consume (e.g., ["0.1.0"])
  "output_details": {
    "format_mime_type": "string", // Default MIME type of the output (e.g., "text/plain", "application/tau+text")
    "file_extension_suggestion": "string_or_null" // Suggested file extension for the output (e.g., ".tau")
  },
  "entry_point": {
    "type": "string_enum", // E.g., "command_line", "python_module", "javascript_module", "web_service"
    "command": "string_or_null", // Required if type is "command_line". The command to execute (e.g., "python main.py translate")
    "module_path": "string_or_null", // Required if type is "python_module" or "javascript_module". Path to the module/class (e.g., "my_plugin.translator_class")
    "function_name": "string_or_null", // Required if type is "python_module" or "javascript_module". Name of the function to call (e.g., "translate_ilr")
    "url": "string_or_null" // Required if type is "web_service". The URL endpoint
    // Additional fields per type may be needed
  },
  "configuration_schema": "object_or_null" // Optional: A JSON Schema defining plugin-specific configuration options
}
```

## 4. Translation Process

### 4.1. Input to Plugin

The primary input to a plugin's translation function/entry point is:
1.  **ILR Data:** The Intermediate Logical Representation object (conforming to `ILR_Specification.md`). For the CLI execution model, this is provided as a JSON string via stdin.
2.  **Configuration Options (Optional):** A JSON object containing plugin-specific configuration options, conforming to the plugin's `configuration_schema` (if defined in its manifest).

The method of passing these inputs (e.g., stdin, file paths, function arguments, HTTP request body) depends on the plugin's `entry_point.type`.

### 4.2. Output from Plugin

The plugin's translation function/entry point must return a JSON string representing the outcome. This JSON string should conform to the following structure:

```json
{
  "status": "string_enum", // "success" or "error"
  "data": { // Present if status is "success"
    "translated_text": "string", // The translated output as a string
    "mime_type": "string", // Actual MIME type of the output (should align with manifest, but can be overridden)
    "warnings": [ // Optional array of warning objects
      {
        "code": "string_or_null", // Plugin-specific warning code
        "message": "string", // Human-readable warning message
        "ilr_path": "string_or_null" // Optional: JSONPath (e.g., "$.statements[2].condition") to the ILR node related to the warning
      }
    ]
  },
  "error": { // Present if status is "error"
    "code": "string_or_null", // Plugin-specific error code
    "message": "string", // Human-readable error message
    "details": "string_or_null", // Optional: Further technical details or stack trace snippet
    "ilr_path": "string_or_null" // Optional: JSONPath to the problematic ILR node
  }
}
```

## 5. Plugin Execution Model

The primary execution model supported for plugins is **Command-Line Interface (CLI) execution**. This model allows plugin developers to use any programming language for their implementation.

When the core engine invokes a plugin that specifies `"type": "command_line"` in its manifest's `entry_point`:
1.  The core engine prepares:
    a.  The **ILR data** as a JSON string.
    b.  Plugin-specific **configuration options** (if any, from user settings or task context) as a JSON string. This string will be an empty JSON object (`{}`) if no options are provided.
2.  The core engine executes the `command` specified in the plugin's manifest.
3.  **Input Passing:**
    a.  The **ILR JSON string** is passed to the plugin's process via **standard input (stdin)**.
    b.  The **configuration options JSON string** is passed as a command-line argument. To ensure safety and handle complex characters, this JSON string will be Base64 encoded, and the plugin will be expected to decode it. A specific argument name like `--options-base64` will be used.
    *Example Invocation:*
    ```bash
    echo '<ILR_JSON_STRING>' | <plugin_command_from_manifest> --options-base64 '<BASE64_ENCODED_OPTIONS_JSON_STRING>'
    ```
4.  **Output Handling:**
    a.  The plugin is expected to print the **Translation Result JSON string** (as defined in Section 4.2) to its **standard output (stdout)** upon completion.
    b.  Any diagnostic messages, logs, or non-structured error details from the plugin should be written to its **standard error (stderr)**.
5.  The core engine captures `stdout` to parse the Translation Result JSON and `stderr` for logging.

Future versions of this specification may define additional execution models (e.g., "python_module", "javascript_module", "web_service") which would involve different mechanisms for invocation and data exchange.

## 6. API Definition (CLI Invocation Workflow)

This section details the workflow for the core engine interacting with a CLI-based plugin.

1.  **Plugin Selection:** The core engine identifies the appropriate plugin based on user choice or task requirements, using the plugin's `id` from its manifest.
2.  **Data Preparation:**
    - The ILR object is serialized to `ILR_JSON_STRING`.
    - Plugin-specific options are serialized to `OPTIONS_JSON_STRING`, then Base64 encoded to `BASE64_ENCODED_OPTIONS_JSON_STRING`.
3.  **Command Execution:**
    - The `command` is retrieved from the plugin's manifest `entry_point`.
    - The core engine executes the command using the input passing mechanism described in Section 5.
4.  **Plugin Responsibility:**
    - Read `ILR_JSON_STRING` from `stdin`.
    - Read `BASE64_ENCODED_OPTIONS_JSON_STRING` from the `--options-base64` command-line argument and decode it.
    - Perform the translation from ILR to the target grammar.
    - Construct the Translation Result JSON string.
    - Print the Translation Result JSON string to `stdout`.
    - Print any other logs/errors to `stderr`.
5.  **Result Processing by Core Engine:**
    - Read the entire `stdout` from the plugin process.
    - Parse this `stdout` content as the Translation Result JSON.
    - If parsing fails or the `status` field in the result indicates an error, handle it accordingly (e.g., log error, notify user).
    - If successful, use the `translated_text` from the result.
    - Log any output received on `stderr` from the plugin process for diagnostic purposes.

---
*(This is a very initial draft and will be expanded significantly.)*
