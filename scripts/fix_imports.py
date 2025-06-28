import os
import re
from pathlib import Path

# Define the root of the project
PROJECT_ROOT = Path(__file__).parent.parent

# Define the import mappings
# (old_pattern, new_replacement)
IMPORT_MAPPINGS = [
    # Case 1: nlp_enhanced moved into translators
    (r'from (tau_translator_omega\.core_engine)\.nlp_enhanced', r'from \1.translators.nlp_enhanced'),
    
    # Case 2: RefactoredTranslationManager moved to orchestrator.py
    (r'from (backend\.unified\.translators)\.refactored_manager', r'from \1.orchestrator'),

    # Case 3: Remove incorrect 'src.' prefix
    (r'from src\.(tau_translator_omega.*)', r'from \1'),
    (r'import src\.(tau_translator_omega.*)', r'import \1'),

    # Case 4: Fix remaining backend import issue
    (r'from (backend\.unified\.translators)\.manager', r'from \1.orchestrator'),
]

def fix_imports_in_file(file_path: Path):
    """Reads a file, applies import fixes, and writes it back if changed."""
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content

        for old_pattern, new_replacement in IMPORT_MAPPINGS:
            content = re.sub(old_pattern, new_replacement, content)

        if content != original_content:
            file_path.write_text(content, encoding='utf-8')
            print(f'Updated: {file_path.relative_to(PROJECT_ROOT)}')
            return True
    except Exception as e:
        print(f'Error processing {file_path}: {e}')
    return False

def main():
    """Main function to find all Python files and fix their imports."""
    print('Starting import fixing process...')
    update_count = 0
    # Iterate over all .py files in the project directory
    for file_path in PROJECT_ROOT.rglob('*.py'):
        # Skip venv and other irrelevant directories
        if any(part in file_path.parts for part in ['venv', '.venv', '__pycache__', 'node_modules', 'build', 'dist']):
            continue
        
        if fix_imports_in_file(file_path):
            update_count += 1
            
    print(f'\nFinished. Updated {update_count} files.')

if __name__ == '__main__':
    main()
