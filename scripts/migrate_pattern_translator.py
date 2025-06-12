#!/usr/bin/env python3
"""
Simple migration script to replace pattern_translator with the refactored version.

Copyright: DarkLightX/Dana Edwards
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent.parent


def main():
    """Migrate pattern translator to refactored version."""
    print("🔄 Migrating Pattern Translator to Refactored Version")
    
    # Paths
    current = project_root / "backend/unified/translators/pattern_translator.py"
    refactored = project_root / "backend/unified/translators/pattern_translator_refactored.py"
    deprecated_dir = project_root / "deprecated" / f"pre_refactor_{datetime.now().strftime('%Y%m%d')}"
    
    # Check files exist
    if not current.exists():
        print("❌ Current pattern_translator.py not found!")
        return
        
    if not refactored.exists():
        print("❌ Refactored pattern_translator_refactored.py not found!")
        return
    
    # Create deprecated directory
    deprecated_dir.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Backup current version
    print(f"1. Backing up current version to {deprecated_dir}")
    backup_path = deprecated_dir / "pattern_translator.py"
    shutil.copy2(current, backup_path)
    print(f"   ✅ Backed up to {backup_path.relative_to(project_root)}")
    
    # Step 2: Remove current version
    print("2. Removing current version")
    current.unlink()
    print("   ✅ Removed current pattern_translator.py")
    
    # Step 3: Rename refactored to current
    print("3. Renaming refactored version to current")
    shutil.move(str(refactored), str(current))
    print("   ✅ Renamed pattern_translator_refactored.py to pattern_translator.py")
    
    # Step 4: Update test file
    test_current = project_root / "tests/unit/test_pattern_translator.py"
    test_new = project_root / "tests/unit/test_pattern_translator_new.py"
    
    if test_current.exists():
        print("4. Renaming test file")
        shutil.move(str(test_current), str(test_new))
        print(f"   ✅ Renamed test file to test_pattern_translator_new.py")
    
    # Step 5: Update imports in the new pattern_translator.py
    print("5. Updating imports in pattern_translator.py")
    with open(current, 'r') as f:
        content = f.read()
    
    # Fix imports
    content = content.replace('from ..core.domain_types import (', 'from ..core.domain_types import (')
    content = content.replace('TranslationResult as BaseTranslationResult', 'TranslationResult')
    
    # Remove the old TranslationResult import from domain_types if it exists
    lines = content.split('\n')
    new_lines = []
    for line in lines:
        if 'TranslationResult,' in line and 'domain_types' in line:
            # Skip this line as TranslationResult comes from base
            continue
        new_lines.append(line)
    
    content = '\n'.join(new_lines)
    
    with open(current, 'w') as f:
        f.write(content)
    
    print("   ✅ Updated imports")
    
    print("\n✅ Migration complete!")
    print(f"\nBackup saved to: {backup_path.relative_to(project_root)}")
    print("\nNext steps:")
    print("1. Run tests: python3 -m pytest tests/unit/test_pattern_translator.py")
    print("2. Test the application manually")
    print("3. Commit the changes")


if __name__ == "__main__":
    main()