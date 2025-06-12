#!/usr/bin/env python3
"""
Script to migrate from UFO-tools to returns/toolz libraries.
Replaces @mutation_free decorators and updates imports.
"""

import os
import re
from pathlib import Path
from typing import List, Tuple

# Files to process
BACKEND_DIR = Path(__file__).parent.parent / "backend" / "unified"
TEST_DIR = Path(__file__).parent.parent / "tests"

def find_files_with_ufo() -> List[Path]:
    """Find all Python files using UFO."""
    files = []
    for directory in [BACKEND_DIR, TEST_DIR]:
        if directory.exists():
            files.extend(directory.rglob("*.py"))
    
    ufo_files = []
    for file in files:
        try:
            content = file.read_text()
            if "from ufo" in content or "import ufo" in content or "@mutation_free" in content:
                ufo_files.append(file)
        except Exception:
            pass
    
    return ufo_files

def migrate_file(file_path: Path) -> Tuple[bool, str]:
    """Migrate a single file from UFO to returns/toolz."""
    try:
        content = file_path.read_text()
        original_content = content
        
        # Remove UFO imports
        content = re.sub(r'from ufo\.wrappers import mutation_free\n', '', content)
        content = re.sub(r'from ufo import.*\n', '', content)
        content = re.sub(r'import ufo.*\n', '', content)
        
        # Check if file uses Result type
        uses_result = "Result[" in content or "Success(" in content or "Failure(" in content
        
        # Add appropriate imports if needed
        if uses_result and "from ..core.result_enhanced import" not in content:
            # Find the right import path based on file location
            if "backend/unified/api" in str(file_path):
                import_line = "from ..core.result_enhanced import Result, Success, Failure, success, failure\n"
            elif "backend/unified/translators" in str(file_path):
                import_line = "from ..core.result_enhanced import Result, Success, Failure, success, failure\n"
            elif "backend/unified/core" in str(file_path):
                import_line = "from .result_enhanced import Result, Success, Failure, success, failure\n"
            else:
                import_line = ""
            
            if import_line:
                # Add import after other imports
                lines = content.split('\n')
                import_index = 0
                for i, line in enumerate(lines):
                    if line.startswith('from') or line.startswith('import'):
                        import_index = i + 1
                    elif import_index > 0 and line.strip() == '':
                        break
                
                lines.insert(import_index, import_line.strip())
                content = '\n'.join(lines)
        
        # Remove @mutation_free decorators
        content = re.sub(r'@mutation_free\n\s*', '', content)
        
        # Add comment where @mutation_free was removed
        if "@mutation_free" in original_content and "@mutation_free" not in content:
            # Add a note about pure functions
            content = re.sub(
                r'(def\s+\w+.*?:)(\s*\n\s*""")',
                r'\1\2\n        Note: This is a pure function (no side effects).\n        ',
                content
            )
        
        if content != original_content:
            file_path.write_text(content)
            return True, f"Migrated {file_path}"
        else:
            return False, f"No changes needed for {file_path}"
            
    except Exception as e:
        return False, f"Error processing {file_path}: {e}"

def main():
    """Run the migration."""
    print("🔄 Starting UFO to returns/toolz migration...")
    
    files = find_files_with_ufo()
    print(f"Found {len(files)} files using UFO")
    
    migrated = 0
    errors = 0
    
    for file in files:
        success, message = migrate_file(file)
        print(f"  {'✅' if success else '❌'} {message}")
        if success:
            migrated += 1
        else:
            errors += 1
    
    print(f"\n📊 Migration complete:")
    print(f"  - Files migrated: {migrated}")
    print(f"  - Errors: {errors}")
    print(f"  - Total files: {len(files)}")
    
    print("\n📝 Next steps:")
    print("1. Review the changes with 'git diff'")
    print("2. Run tests to ensure everything works")
    print("3. Update any documentation mentioning UFO")
    print("4. Remove ufo-tools from requirements.txt")

if __name__ == "__main__":
    main()