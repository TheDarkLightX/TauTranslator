# Internal Scripts Inventory

This document lists all scripts and tools that should be moved to `internal/scripts/`.

## Tools Directory (`tools/`)

### Analysis Tools
- `analyze_complexity.py` - Code complexity analyzer
- `deep_codebase_analyzer.py` - Deep code analysis tool
- `enhanced_code_quality_analyzer.py` - Enhanced quality metrics
- `llm_features_analysis.py` - LLM feature analyzer
- `mutation_testing_analysis.py` - Mutation testing analyzer
- `performance_benchmark_suite.py` - Performance benchmarking
- `performance_visualization.py` - Performance data visualization
- `generate_performance_report.py` - Performance report generator

### Quality Tools
- `code_quality_analyzer.py` - Basic code quality metrics
- `code_quality_tool.py` - Code quality measurement
- `enhanced_code_quality_tool.py` - Enhanced quality tool
- `craftsmanship_refactoring_toolkit.py` - Refactoring utilities
- `refactoring_demo.py` - Refactoring demonstration
- `enhanced_styling_toolkit.py` - Code styling utilities

### Debug Tools
- `debug_amr_detailed.py` - AMR debugging
- `debug_cnl_parser.py` - CNL parser debugging
- `debug_cnl_proper.py` - Proper CNL debugging
- `debug_ilr_cnl.py` - ILR CNL debugging
- `debug_nlp_integration.py` - NLP integration debugging
- `debug_utilities.py` - General debug utilities

### Testing Tools
- `llm_api_tester.py` - LLM API testing
- `test_benchmark_components.py` - Benchmark component tests
- `validate_tests.py` - Test validation

### Development Tools
- `check_backend_status.py` - Backend status checker
- `code_review_checklist.py` - Code review utilities
- `dev_tools.py` - Development utilities
- `pre_commit_checks.py` - Pre-commit validation

## Scripts Directory (`scripts/`)

### Analysis Scripts (`scripts/analysis/`)
- `debug_parsing_isolated.py` - Isolated parser debugging
- `run_project_wide_mutation_analysis.py` - Project mutation analysis

### Migration Scripts
- `migrate_pattern_translator.py` - Pattern translator migration
- `migrate_to_refactored.py` - Refactoring migration

### Utility Scripts
- `cleanup_duplicates.py` - Duplicate file cleanup
- `update_imports_after_cleanup.py` - Import updater
- `benchmark_simd_performance.py` - SIMD benchmarking

### Demo Scripts (`scripts/demos/`)
- `nlp_gui_demo.py` - NLP GUI demonstration
- `start_nlp_demo.py` - NLP demo starter

### Setup Scripts (`scripts/setup/`)
- `recommended_local_models.py` - Local model recommendations

## Backend Unified Directory (`backend/unified/`)

### Migration Scripts
- `migration_phase2.py` - Phase 2 migration
- `verify_migration.py` - Migration verification

### Test Scripts
- `test_direct.py` - Direct testing utilities

## Utilities Directory (`utilities/`)

- `demonstrate_ast_translation.py` - AST translation demo
- `organize_repository.py` - Repository organization
- `requirements_to_tau_system.py` - Requirements converter
- `run_tests.py` - Test runner
- `verify_refactoring.py` - Refactoring verification

## Test Mutation Scripts (`tests/mutation/`)

- `quick_mutation_test.py` - Quick mutation testing
- `run_boolean_mutation_test.py` - Boolean mutation tests
- `run_hardened_mutation_test.py` - Hardened mutation tests
- `run_mutation_test.py` - General mutation tests
- `run_proper_mutation_test.py` - Proper mutation tests
- `run_simple_mutation_test.py` - Simple mutation tests
- `scale_mutation_testing.py` - Scaled mutation testing

## Scripts to Keep in Current Location

These scripts should remain where they are as they're user-facing:

### Essential Startup Scripts (`scripts/`)
- `start_backend.py` - Backend starter
- `start_all_backends.py` - All backends starter
- `start_production.sh` - Production starter
- `start_jupyter.sh` - Jupyter starter
- `start_llm_config_service.py` - LLM config service
- `launch_tau_translator.py` - Main launcher

### Build Scripts (`scripts/`)
- `build_desktop_app.py` - Desktop app builder
- `build_executable_ubuntu.py` - Ubuntu executable builder
- `create_ubuntu_launcher.py` - Ubuntu launcher creator

### Setup Scripts (`scripts/`)
- `setup_complete_system.py` - Complete system setup
- `setup_gemma_model.py` - Gemma model setup
- `uninstall.sh` - Uninstallation script

## Organization Structure

```
internal/
└── scripts/
    ├── analysis/      # Code analysis and benchmarking tools
    ├── demos/         # Demonstration scripts
    ├── migration/     # Migration and refactoring scripts
    ├── mutation/      # Mutation testing scripts
    ├── quality/       # Code quality and refactoring tools
    ├── setup/         # Internal setup utilities
    ├── tools/         # Development and debug tools
    └── utilities/     # General utility scripts
```

## Migration Notes

1. Scripts that are frequently called by users remain in their original locations
2. Internal development tools are moved to `internal/scripts/`
3. For commonly used tools, redirect scripts are created at the original location
4. All moved scripts maintain their executable permissions
5. Category-specific READMEs are created in each subdirectory