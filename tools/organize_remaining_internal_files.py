#!/usr/bin/env python3
"""
Script to organize remaining internal documentation files from internal_docs to internal.
Handles the migration of files from the existing internal_docs directory.

Copyright: DarkLightX/Dana Edwards
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

# Base project path
PROJECT_ROOT = Path(__file__).parent.parent

# Source and destination paths
INTERNAL_DOCS_OLD = PROJECT_ROOT / "internal_docs"
INTERNAL_ROOT = PROJECT_ROOT / "internal"
INTERNAL_DOCS = INTERNAL_ROOT / "docs"
INTERNAL_ANALYSIS = INTERNAL_ROOT / "analysis"
INTERNAL_MIGRATION = INTERNAL_ROOT / "migration"

# Files to move from internal_docs
FILES_TO_MOVE = {
    "internal_docs": [
        "INTEGRATION_COMPLETE.md",
        "PHASE1_IMPLEMENTATION_COMPLETE.md", 
        "PHASE1_IMPROVEMENT_CHECKLIST.md",
        "PHASE2_IMPLEMENTATION_COMPLETE.md",
        "ORGANIZATION_COMPLETE.md",
        "SEMANTIC_ANALYSIS_ALGORITHMS_REPORT.md",
        "SIMD_IMPLEMENTATION_SUMMARY.md",
        "UI_UX_DESIGN_SUMMARY.md",
        "PRODUCTION_READY_SUMMARY.md",
        "REFACTORING_SUMMARY.md",
        "ACTUAL_PROJECT_STATUS.md",
        "AI_MODEL_INTEGRATION.md",
        "API_KEY_INTEGRATION_GUIDE.md",
        "CORS_SETUP_GUIDE.md",
        "DIALOG_SIZING_FIXED.md",
        "FASTAPI_BACKEND_GUIDE.md",
        "PARSER_ENGINE_INTEGRATION.md",
        "PROFESSIONAL_MENU_SYSTEM.md",
        "USE_UNIFIED_BACKEND.md",
        "WORKING_TEST_GUIDE.md",
        "craftmanship.md",
        "progress.md",
        "tce_specification.md",
        "Core_Engine_Design_Outline.md",
        "ILR_Specification.md",
        "LLM_Interaction_Strategy.md",
        "Plugin_Interface_Specification.md",
        "TRANSLATION_PIPELINE_EXPLAINED.md",
        "TRANSLATION_QUALITY_IMPROVEMENTS.md",
        "UI_UX_IMPROVEMENTS_2024.md",
        "TESTING_GUIDE.md",
        "FRONTEND_DEMO.md",
        "FRONTEND_GUIDE.md",
        "PRODUCTION_README.md",
        "UBUNTU_INSTALLATION.md",
        "TauEpics1.md",
        "TauTranslatorPRD.md",
        "backend_requirements.txt",
        "production_requirements.txt",
        "test_requirements.txt",
        "organize_files.py",
    ],
    "analysis": [
        "nlp_state_of_art_analysis.md",
        "CODE_QUALITY_RESEARCH_2024.md",
        "DEEP_NLP_RESEARCH_2024.md",
        "NLP_INTENT_DETECTION_RESEARCH_2024.md",
    ],
    "migration": [
        "PROJECT_STRUCTURE.md",
    ],
    "system_prompts": [
        "CLAUDE.md",
        "CLAUDE.local.md",
        "INSTRUCTIONS.md",
        "VIBEARCHITECT_COMPRESSED.md",
        "compressed_vibearchitect_prompt.md",
    ],
    "todo_audit": [
        "TODO.md",
        "PLACEHOLDER_CODE_AUDIT.md",
        "ROOT_FILES.md",
    ],
    "archived": [
        "archived/COMPLETE_STARTUP_GUIDE.md",
        "archived/COMPLETE_TAU_GRAMMAR_ANALYSIS.md",
        "archived/DEVELOPMENT_ENVIRONMENT_COMPLETE.md",
        "archived/ENHANCED_PRODUCTION_SUMMARY.md",
        "archived/FINAL_COMPREHENSIVE_ANALYSIS.md",
        "archived/SEMANTIC_ANALYZER_TDD_COMPLETE.md",
    ]
}

def move_file(source: Path, destination: Path) -> bool:
    """Move a file from source to destination."""
    try:
        if source.exists():
            # Create parent directory if needed
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            # Move the file
            shutil.move(str(source), str(destination))
            print(f"  → Moved: {source.relative_to(PROJECT_ROOT)} to {destination.relative_to(PROJECT_ROOT)}")
            return True
        else:
            print(f"  ⚠ File not found: {source.relative_to(PROJECT_ROOT)}")
            return False
    except Exception as e:
        print(f"  ✗ Error moving {source.relative_to(PROJECT_ROOT)}: {e}")
        return False

def main():
    """Main execution function."""
    print("TauTranslator Remaining Internal Files Organization")
    print("=" * 50)
    print(f"Moving files from: {INTERNAL_DOCS_OLD.relative_to(PROJECT_ROOT)}")
    print(f"To: {INTERNAL_ROOT.relative_to(PROJECT_ROOT)}")
    print()
    
    moved_count = 0
    failed_count = 0
    
    # Move internal documentation files
    print("Moving internal documentation files...")
    for file_name in FILES_TO_MOVE["internal_docs"]:
        source = INTERNAL_DOCS_OLD / file_name
        destination = INTERNAL_DOCS / file_name
        if move_file(source, destination):
            moved_count += 1
        else:
            failed_count += 1
    
    # Move analysis files
    print("\nMoving analysis files...")
    for file_name in FILES_TO_MOVE["analysis"]:
        source = INTERNAL_DOCS_OLD / file_name
        destination = INTERNAL_ANALYSIS / file_name
        if move_file(source, destination):
            moved_count += 1
        else:
            failed_count += 1
    
    # Move migration files
    print("\nMoving migration files...")
    for file_name in FILES_TO_MOVE["migration"]:
        source = INTERNAL_DOCS_OLD / file_name
        destination = INTERNAL_MIGRATION / file_name
        if move_file(source, destination):
            moved_count += 1
        else:
            failed_count += 1
    
    # Skip system prompts and sensitive files - these should remain in internal_docs
    print("\nSkipping system prompts and sensitive files (they remain in internal_docs)...")
    for file_name in FILES_TO_MOVE["system_prompts"]:
        print(f"  ⚠ Keeping in internal_docs: {file_name}")
    
    # Skip TODO and audit files
    print("\nSkipping TODO and audit files (they remain in internal_docs)...")
    for file_name in FILES_TO_MOVE["todo_audit"]:
        print(f"  ⚠ Keeping in internal_docs: {file_name}")
    
    # Move archived files
    print("\nMoving archived files...")
    archive_dest = INTERNAL_DOCS / "archived"
    archive_dest.mkdir(parents=True, exist_ok=True)
    for file_name in FILES_TO_MOVE["archived"]:
        source = INTERNAL_DOCS_OLD / file_name
        destination = INTERNAL_DOCS / file_name
        if move_file(source, destination):
            moved_count += 1
        else:
            failed_count += 1
    
    # Check if internal_docs has a README
    internal_docs_readme = INTERNAL_DOCS_OLD / "README.md"
    if internal_docs_readme.exists():
        # Keep the README in internal_docs
        print(f"\n⚠ Keeping README.md in internal_docs")
    
    # Summary
    print("\n" + "=" * 50)
    print("Organization Complete!")
    print(f"Files moved: {moved_count}")
    print(f"Files failed: {failed_count}")
    print(f"\nNote: System prompts and sensitive files remain in internal_docs/")
    print("which is already excluded by .gitignore")

if __name__ == "__main__":
    main()