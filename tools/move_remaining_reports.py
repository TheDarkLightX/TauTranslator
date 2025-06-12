#!/usr/bin/env python3
"""
Script to move remaining internal reports that weren't caught earlier.

Copyright: DarkLightX/Dana Edwards
"""

import shutil
from pathlib import Path

# Base project path
PROJECT_ROOT = Path(__file__).parent.parent
REPORTS_DIR = PROJECT_ROOT / "reports"
INTERNAL_REPORTS = PROJECT_ROOT / "internal" / "reports"

# Files to move from reports to internal
FILES_TO_MOVE = [
    "BACKEND_FEATURE_MATRIX.md",
    "TEST_RESULTS_AFTER_REFACTORING.md",
]

def main():
    """Main execution function."""
    print("Moving remaining reports to internal directory")
    print("=" * 50)
    
    moved_count = 0
    
    for file_name in FILES_TO_MOVE:
        source = REPORTS_DIR / file_name
        destination = INTERNAL_REPORTS / file_name
        
        if source.exists():
            try:
                shutil.move(str(source), str(destination))
                print(f"  → Moved: {source.relative_to(PROJECT_ROOT)} to {destination.relative_to(PROJECT_ROOT)}")
                moved_count += 1
            except Exception as e:
                print(f"  ✗ Error moving {source.relative_to(PROJECT_ROOT)}: {e}")
        else:
            print(f"  ⚠ File not found: {source.relative_to(PROJECT_ROOT)}")
    
    print(f"\nMoved {moved_count} files")
    print("\nThe reports/ directory now contains only its README explaining the reports structure.")

if __name__ == "__main__":
    main()