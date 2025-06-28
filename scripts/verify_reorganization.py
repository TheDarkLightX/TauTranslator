#!/usr/bin/env python3
"""
Verify the core_engine reorganization was successful.
"""

import os
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def verify_structure(base_path: str):
    """Verify the new directory structure exists and contains files."""
    core_engine_path = Path(base_path) / "src" / "tau_translator_omega" / "core_engine"
    
    expected_dirs = [
        "ast", "parsers", "translators", "semantic", "ilr",
        "plugins", "preprocessing", "utils", "config"
    ]
    
    print("Verifying directory structure...")
    all_good = True
    
    for dir_name in expected_dirs:
        dir_path = core_engine_path / dir_name
        if dir_path.exists() and dir_path.is_dir():
            py_files = list(dir_path.glob("*.py"))
            print(f"✓ {dir_name}/ exists with {len(py_files)} Python files")
            
            # Check for __init__.py
            if (dir_path / "__init__.py").exists():
                print(f"  ✓ __init__.py present")
            else:
                print(f"  ✗ __init__.py missing")
                all_good = False
        else:
            print(f"✗ {dir_name}/ missing")
            all_good = False
    
    # Check for specific expected files
    print("\nVerifying key files...")
    expected_files = {
        "ast/ast_nodes.py": "AST node definitions",
        "parsers/parser_refactored.py": "Main parser",
        "translators/core_translator.py": "Core translator",
        "semantic/semantic_analyzer_core.py": "Semantic analyzer",
        "ilr/ilr_nodes.py": "ILR nodes",
        "plugins/plugin_manager_refactored.py": "Plugin manager",
        "utils/bloom_filter.py": "Bloom filter utility"
    }
    
    for file_path, description in expected_files.items():
        full_path = core_engine_path / file_path
        if full_path.exists():
            print(f"✓ {file_path} - {description}")
        else:
            print(f"✗ {file_path} - {description}")
            all_good = False
    
    # Check for leftover files in root
    print("\nChecking for files in core_engine root...")
    root_files = [f for f in core_engine_path.glob("*.py") 
                  if f.name != "__init__.py" and f.is_file()]
    
    if root_files:
        print(f"⚠️  Found {len(root_files)} Python files still in root:")
        for f in root_files[:5]:  # Show first 5
            print(f"   - {f.name}")
        if len(root_files) > 5:
            print(f"   ... and {len(root_files) - 5} more")
    else:
        print("✓ No Python files left in root (except __init__.py)")
    
    # Summary
    print("\n" + "="*50)
    if all_good and not root_files:
        print("✅ Reorganization verification PASSED!")
    else:
        print("❌ Reorganization verification FAILED!")
        print("   Please check the issues above.")
    
    return all_good and not root_files

def main():
    base_path = str(PROJECT_ROOT)
    if len(sys.argv) > 1:
        base_path = sys.argv[1]
    
    success = verify_structure(base_path)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()