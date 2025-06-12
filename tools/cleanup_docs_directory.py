#!/usr/bin/env python3
"""
Script to clean up the docs directory, removing internal documentation that has been moved.
Keeps only user-facing documentation like API docs, schemas, etc.

Copyright: DarkLightX/Dana Edwards
"""

import os
import shutil
from pathlib import Path

# Base project path
PROJECT_ROOT = Path(__file__).parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
INTERNAL_DOCS = PROJECT_ROOT / "internal" / "docs"

# Files to remove from docs (already moved to internal)
FILES_TO_REMOVE = [
    "ACTUAL_PROJECT_STATUS.md",
    "AI_MODEL_INTEGRATION.md", 
    "API_KEY_INTEGRATION_GUIDE.md",
    "CORS_SETUP_GUIDE.md",
    "Core_Engine_Design_Outline.md",
    "DEEP_NLP_RESEARCH_2024.md",
    "DIALOG_SIZING_FIXED.md",
    "FASTAPI_BACKEND_GUIDE.md",
    "FRONTEND_DEMO.md",
    "FRONTEND_GUIDE.md",
    "ILR_Specification.md",
    "LLM_Interaction_Strategy.md",
    "NLP_INTENT_DETECTION_RESEARCH_2024.md",
    "PARSER_ENGINE_INTEGRATION.md",
    "PRODUCTION_README.md",
    "PRODUCTION_READY_SUMMARY.md",
    "PROFESSIONAL_MENU_SYSTEM.md",
    "PROJECT_STATUS.md",
    "Plugin_Interface_Specification.md",
    "REAL_SECURITY_IMPLEMENTATION.md",
    "SECURE_API_OPENROUTER_GUIDE.md",
    "SECURITY_FIXED_SUMMARY.md",
    "SEMANTIC_ANALYSIS_ALGORITHMS_REPORT.md",
    "SIMD_IMPLEMENTATION_SUMMARY.md",
    "TESTING_GUIDE.md",
    "TRANSLATION_PIPELINE_EXPLAINED.md",
    "TRANSLATION_QUALITY_IMPROVEMENTS.md",
    "TauEpics1.md",
    "TauTranslatorPRD.md",
    "UI_UX_DESIGN_SUMMARY.md",
    "UI_UX_IMPROVEMENTS_2024.md",
    "USE_UNIFIED_BACKEND.md",
    "WORKING_TEST_GUIDE.md",
    "backend_requirements.txt",
    "production_requirements.txt",
    "progress.md",
    "tce_specification.md",
    "test_requirements.txt",
]

# Archived files to remove
ARCHIVED_FILES_TO_REMOVE = [
    "archived/COMPLETE_STARTUP_GUIDE.md",
    "archived/COMPLETE_TAU_GRAMMAR_ANALYSIS.md",
    "archived/DEVELOPMENT_ENVIRONMENT_COMPLETE.md",
    "archived/ENHANCED_PRODUCTION_SUMMARY.md",
    "archived/FINAL_COMPREHENSIVE_ANALYSIS.md",
    "archived/SEMANTIC_ANALYZER_TDD_COMPLETE.md",
]

# User-facing documentation to keep in docs
FILES_TO_KEEP = [
    "UBUNTU_INSTALLATION.md",  # Installation guide for users
    "requirements.txt",  # Dependencies for users
    "schemas/",  # API/Schema documentation
]

def main():
    """Main execution function."""
    print("TauTranslator Docs Directory Cleanup")
    print("=" * 50)
    print(f"Cleaning up: {DOCS_DIR.relative_to(PROJECT_ROOT)}")
    print()
    
    removed_count = 0
    failed_count = 0
    
    # Remove internal documentation files
    print("Removing internal documentation files...")
    for file_name in FILES_TO_REMOVE:
        file_path = DOCS_DIR / file_name
        if file_path.exists():
            try:
                file_path.unlink()
                print(f"  ✓ Removed: {file_path.relative_to(PROJECT_ROOT)}")
                removed_count += 1
            except Exception as e:
                print(f"  ✗ Error removing {file_path.relative_to(PROJECT_ROOT)}: {e}")
                failed_count += 1
        else:
            # File might have already been moved/removed
            pass
    
    # Remove archived internal files
    print("\nRemoving archived internal files...")
    for file_name in ARCHIVED_FILES_TO_REMOVE:
        file_path = DOCS_DIR / file_name
        if file_path.exists():
            try:
                file_path.unlink()
                print(f"  ✓ Removed: {file_path.relative_to(PROJECT_ROOT)}")
                removed_count += 1
            except Exception as e:
                print(f"  ✗ Error removing {file_path.relative_to(PROJECT_ROOT)}: {e}")
                failed_count += 1
    
    # Remove empty archived directory if it exists
    archived_dir = DOCS_DIR / "archived"
    if archived_dir.exists() and not any(archived_dir.iterdir()):
        try:
            archived_dir.rmdir()
            print(f"  ✓ Removed empty directory: {archived_dir.relative_to(PROJECT_ROOT)}")
        except Exception as e:
            print(f"  ✗ Error removing directory: {e}")
    
    # List what remains in docs
    print("\nFiles kept in docs/ (user-facing documentation):")
    for item in sorted(DOCS_DIR.iterdir()):
        if item.is_file():
            print(f"  • {item.relative_to(PROJECT_ROOT)}")
        elif item.is_dir():
            print(f"  • {item.relative_to(PROJECT_ROOT)}/ (directory)")
    
    # Summary
    print("\n" + "=" * 50)
    print("Cleanup Complete!")
    print(f"Files removed: {removed_count}")
    print(f"Errors: {failed_count}")
    print("\nThe docs/ directory now contains only user-facing documentation.")

if __name__ == "__main__":
    main()