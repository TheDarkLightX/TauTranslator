# Core Engine Reorganization Guide

## Overview

This guide explains how to use the `reorganize_core_engine.py` script to restructure the core_engine directory for better modularity and organization.

## New Directory Structure

The script will create the following directory structure:

```
core_engine/
├── ast/              # AST-related modules (ast_nodes, ast_visitor, expression_builders)
├── parsers/          # All parser implementations
├── translators/      # Translation engines (core_translator, ilr_translator, nlp_translator)
├── semantic/         # Semantic analysis modules
├── ilr/              # ILR (Intermediate Language Representation) modules
├── plugins/          # Plugin system modules
├── preprocessing/    # Preprocessor and directives
├── utils/            # Utility modules (bloom_filter, lazy_loader, etc.)
└── config/           # Configuration modules
```

## Usage

### 1. Dry Run (Recommended First)

Always start with a dry run to see what changes will be made:

```bash
cd ~/TauTranslator
python scripts/reorganize_core_engine.py --dry-run
```

### 2. Execute Reorganization

Once you're satisfied with the dry run results:

```bash
python scripts/reorganize_core_engine.py
```

### 3. Update Imports

After reorganization, update all import statements:

```bash
python scripts/update_imports_after_cleanup.py
```

### 4. Run Tests

Verify everything still works:

```bash
pytest tests/
```

## What the Script Does

1. **Creates Backup**: Saves current state to `backups/core_engine_backup_TIMESTAMP/`
2. **Creates New Directories**: Sets up the new modular structure
3. **Moves Files**: Relocates files to appropriate directories based on their purpose
4. **Removes Duplicates**: Keeps only refactored versions when duplicates exist
5. **Extracts Demo Code**: Moves demo/example code to `scripts/demos/`
6. **Moves Test Files**: Relocates test files to the `tests/` directory
7. **Generates Report**: Creates a detailed JSON report of all changes

## File Mappings

- **AST**: ast_nodes.py, ast_visitor.py, expression_builders.py
- **Parsers**: All parser implementations including cnl_parser/ and ebnf_parser/ directories
- **Translators**: All translator modules including the nlp_enhanced/ directory
- **Semantic**: semantic_analyzer modules and AMR semantic layer
- **ILR**: All ILR-related modules (nodes, config, patterns, handlers)
- **Plugins**: Plugin manager and validator modules
- **Preprocessing**: Preprocessor directives and errors
- **Utils**: Utility modules like bloom_filter, lazy_loader, validation_pipeline
- **Config**: Configuration modules

## Duplicates Handled

The script automatically removes older versions when it finds:
- parser.py (keeps parser_refactored.py)
- semantic_analyzer.py (keeps semantic_analyzer_refactored.py)
- plugin_manager.py (keeps plugin_manager_refactored.py)
- ilr_pattern_analyzer.py (keeps ilr_pattern_analyzer_refactored.py)
- nlp_translator.py (keeps nlp_translator_refactored.py)
- requirements_analyzer.py (keeps requirements_analyzer_refactored.py)

## Reverting Changes

If you need to revert the reorganization:

1. The backup location is shown in the output and report
2. Copy the backup back: `cp -r backups/core_engine_backup_TIMESTAMP/core_engine/* src/tau_translator_omega/core_engine/`
3. Remove the newly created directories if needed

## Reports

The script generates a comprehensive JSON report in `reports/reorganization_report_TIMESTAMP.json` containing:
- Timestamp of the operation
- Backup location
- Detailed list of all changes made
- Summary statistics

## Safety Features

- **Dry Run Mode**: Test without making changes
- **Automatic Backup**: Always creates a backup before changes
- **Change Logging**: Every action is logged
- **Duplicate Detection**: Uses MD5 hashing to identify duplicate files
- **Demo Extraction**: Preserves example code in separate files