#!/usr/bin/env python3
"""
Script to organize internal documentation and analysis files into the internal/ directory.
Maintains appropriate subdirectory structure for different types of internal files.

Copyright: DarkLightX/Dana Edwards
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Dict

# Base project path
PROJECT_ROOT = Path(__file__).parent.parent

# Internal folder structure
INTERNAL_ROOT = PROJECT_ROOT / "internal"
INTERNAL_DOCS = INTERNAL_ROOT / "docs"
INTERNAL_ANALYSIS = INTERNAL_ROOT / "analysis"
INTERNAL_REPORTS = INTERNAL_ROOT / "reports"
INTERNAL_DEBUG = INTERNAL_ROOT / "debug"
INTERNAL_BENCHMARKS = INTERNAL_ROOT / "benchmarks"
INTERNAL_QUALITY = INTERNAL_ROOT / "quality"
INTERNAL_MIGRATION = INTERNAL_ROOT / "migration"
INTERNAL_REFACTORING = INTERNAL_ROOT / "refactoring"

# Files to move - organized by category
FILES_TO_MOVE = {
    "analysis_json": [
        "data/code_analysis_results.json",
        "data/quality_analysis_results.json",
        "tools/quality_analysis_results.json",
        "reports/enhanced_quality_analysis.json",
        "tools/llm_features_analysis_report.json",
        "reports/deep_analysis_src.json",
        "reports/deep_analysis_backend.json",
        "reports/deep_analysis_translators.json",
        "reports/quality_analysis_results.json",
        "data/execution_traces.json",
    ],
    "reports_json": [
        "data/qt_integration_test_report.json",
        "reports/task-complexity-report.json",
        "data/organization_report.json",
        "reports/mutation_testing_readiness_report.json",
        "reports/test_suite_health_report.json",
        "reports/scaled_mutation_testing_report_1749011787.json",
        "reports/quality_report_20250604_133111.json",
        "reports/quality_report_20250604_133833.json",
        "reports/quality_report_20250604_134635.json",
        "reports/quality_report_20250605_151844.json",
        "pwa/grammar_input_test_report.json",
        "reports/coverage.json",
        "reports/llm_api_test_results_20250604_153320.json",
    ],
    "benchmarks": [
        "benchmark_results/benchmark_data_20250606_165139.json",
        "tools/phase2_benchmark_summary.json",
        "benchmark_results/baseline_metrics.json",
        "benchmark_results/performance_report_20250606_165139.txt",
    ],
    "debug_files": [
        "tools/debug_utilities.py",
        "tools/debug_ilr_cnl.py",
        "tools/debug_nlp_integration.py",
        "tools/debug_cnl_parser.py",
        "tools/debug_cnl_proper.py",
        "tools/debug_amr_detailed.py",
        "scripts/analysis/debug_parsing_isolated.py",
        "archive/debug_frontend.html",
    ],
    "internal_docs_md": [
        "PHASE1_IMPROVEMENT_CHECKLIST.md",
        "INTEGRATION_COMPLETE.md",
        "PHASE1_IMPLEMENTATION_COMPLETE.md",
        "PHASE2_IMPLEMENTATION_COMPLETE.md",
        "backend/unified/MIGRATION_COMPLETE.md",
        "docs/SEMANTIC_ANALYSIS_ALGORITHMS_REPORT.md",
        "docs/SIMD_IMPLEMENTATION_SUMMARY.md",
        "docs/UI_UX_DESIGN_SUMMARY.md",
        "docs/PRODUCTION_READY_SUMMARY.md",
        "docs/SECURITY_FIXED_SUMMARY.md",
        "backend/unified/core/algorithms/STRING_MATCHING_SUMMARY.md",
    ],
    "analysis_md": [
        "reports/COMPREHENSIVE_REFACTORING_ANALYSIS.md",
        "reports/ALGORITHMIC_OPTIMIZATION_ANALYSIS.md",
        "reports/PWA_FRONTEND_ANALYSIS.md",
        "DUPLICATE_ANALYSIS.md",
        "REFACTORED_VS_CURRENT_ANALYSIS.md",
        "src/tau_translator_omega/core_engine/REORGANIZATION_ANALYSIS.md",
    ],
    "reports_md": [
        "tools/LLM_FEATURES_COMPREHENSIVE_REPORT.md",
        "reports/TEST_QUALITY_IMPROVEMENT_REPORT.md",
        "reports/END_TO_END_TEST_REPORT.md",
        "tools/phase2_performance_report.md",
        "reports/PERFORMANCE_IMPROVEMENTS_SUMMARY.md",
        "reports/TEST_RESULTS_SUMMARY.md",
        "reports/CRAFTSMANSHIP_REFACTORING_REPORT.md",
        "reports/REFACTORING_TEST_CREATION_SUMMARY.md",
        "CLEANUP_SUMMARY.md",
    ],
    "quality_reports": [
        "reports/core_engine_quality_report.txt",
        "reports/enhanced_quality_report.txt",
        "reports/test_quality_report.txt",
    ],
    "migration_docs": [
        "PROJECT_STRUCTURE.md",  # This seems more internal than user-facing
    ]
}

def create_directory_structure():
    """Create the internal directory structure."""
    directories = [
        INTERNAL_ROOT,
        INTERNAL_DOCS,
        INTERNAL_ANALYSIS,
        INTERNAL_REPORTS,
        INTERNAL_DEBUG,
        INTERNAL_BENCHMARKS,
        INTERNAL_QUALITY,
        INTERNAL_MIGRATION,
        INTERNAL_REFACTORING,
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {directory.relative_to(PROJECT_ROOT)}")

def get_destination_path(file_path: str, category: str) -> Path:
    """Determine the appropriate destination path for a file."""
    filename = Path(file_path).name
    
    # Map categories to destination directories
    category_map = {
        "analysis_json": INTERNAL_ANALYSIS,
        "reports_json": INTERNAL_REPORTS,
        "benchmarks": INTERNAL_BENCHMARKS,
        "debug_files": INTERNAL_DEBUG,
        "internal_docs_md": INTERNAL_DOCS,
        "analysis_md": INTERNAL_ANALYSIS,
        "reports_md": INTERNAL_REPORTS,
        "quality_reports": INTERNAL_QUALITY,
        "migration_docs": INTERNAL_MIGRATION,
    }
    
    dest_dir = category_map.get(category, INTERNAL_ROOT)
    return dest_dir / filename

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

def update_gitignore():
    """Update .gitignore to exclude the internal folder."""
    gitignore_path = PROJECT_ROOT / ".gitignore"
    
    # Read existing .gitignore
    if gitignore_path.exists():
        with open(gitignore_path, 'r') as f:
            content = f.read()
    else:
        content = ""
    
    # Check if internal/ is already in .gitignore
    if "internal/" not in content and "/internal" not in content:
        # Add internal/ to .gitignore
        with open(gitignore_path, 'a') as f:
            if not content.endswith('\n'):
                f.write('\n')
            f.write('\n# Internal documentation and analysis\n')
            f.write('internal/\n')
        print("\n✓ Updated .gitignore to exclude internal/ folder")
    else:
        print("\n✓ .gitignore already excludes internal/ folder")

def create_internal_readme():
    """Create a README in the internal folder explaining its purpose."""
    readme_path = INTERNAL_ROOT / "README.md"
    readme_content = """# Internal Documentation and Analysis

This directory contains internal documentation, analysis reports, and temporary files that are not intended for external distribution.

## Directory Structure

- **analysis/**: Code analysis reports and refactoring analysis
- **benchmarks/**: Performance benchmark results
- **debug/**: Debug utilities and scripts
- **docs/**: Internal documentation (implementation details, checklists, etc.)
- **migration/**: Migration and reorganization documentation
- **quality/**: Code quality reports and metrics
- **refactoring/**: Refactoring analysis and reports
- **reports/**: Various internal reports (test results, coverage, etc.)

## Note

This directory is excluded from version control via .gitignore to keep the repository clean and focused on production code and user-facing documentation.

Copyright: DarkLightX/Dana Edwards
"""
    
    with open(readme_path, 'w') as f:
        f.write(readme_content)
    print("\n✓ Created internal/README.md")

def main():
    """Main execution function."""
    print("TauTranslator Internal Files Organization Script")
    print("=" * 50)
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Internal root: {INTERNAL_ROOT}")
    print()
    
    # Create directory structure
    print("Creating internal directory structure...")
    create_directory_structure()
    print()
    
    # Move files
    print("Moving files to internal directories...")
    moved_count = 0
    failed_count = 0
    
    for category, file_list in FILES_TO_MOVE.items():
        print(f"\n{category}:")
        for file_path in file_list:
            source = PROJECT_ROOT / file_path
            destination = get_destination_path(file_path, category)
            
            if move_file(source, destination):
                moved_count += 1
            else:
                failed_count += 1
    
    # Create internal README
    create_internal_readme()
    
    # Update .gitignore
    update_gitignore()
    
    # Summary
    print("\n" + "=" * 50)
    print("Organization Complete!")
    print(f"Files moved: {moved_count}")
    print(f"Files failed: {failed_count}")
    print(f"\nInternal directory created at: {INTERNAL_ROOT.relative_to(PROJECT_ROOT)}")
    
    # Create a summary report
    summary = {
        "timestamp": datetime.now().isoformat(),
        "files_moved": moved_count,
        "files_failed": failed_count,
        "internal_structure": {
            "analysis": len(list(INTERNAL_ANALYSIS.glob("*"))),
            "benchmarks": len(list(INTERNAL_BENCHMARKS.glob("*"))),
            "debug": len(list(INTERNAL_DEBUG.glob("*"))),
            "docs": len(list(INTERNAL_DOCS.glob("*"))),
            "migration": len(list(INTERNAL_MIGRATION.glob("*"))),
            "quality": len(list(INTERNAL_QUALITY.glob("*"))),
            "reports": len(list(INTERNAL_REPORTS.glob("*"))),
        }
    }
    
    summary_path = INTERNAL_ROOT / "organization_summary.json"
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\nOrganization summary saved to: {summary_path.relative_to(PROJECT_ROOT)}")

if __name__ == "__main__":
    main()