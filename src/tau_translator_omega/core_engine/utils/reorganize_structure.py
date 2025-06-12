#!/usr/bin/env python3
"""
Core Engine Directory Reorganization Script
==========================================

This script analyzes the current folder structure and reorganizes files into
a cleaner, more logical structure.

Copyright: DarkLightX/Dana Edwards
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Tuple

# Define the proposed new structure
NEW_STRUCTURE = {
    # AST and node-related files
    "ast": [
        "ast_nodes.py",  # Duplicate - will handle merge
        "ast_visitor.py",
        "ast/ast_nodes.py",  # Keep in ast subfolder
        "ast/__init__.py"
    ],
    
    # Parser implementations
    "parsers": [
        "parser.py",
        "enhanced_parser.py",
        "grammar_driven_parser.py",
        "cnl_parser",  # Keep as subdirectory
        "ebnf_parser",  # Keep as subdirectory
    ],
    
    # Translator implementations
    "translators": [
        "core_translator.py",
        "ilr_translator.py",
        "ilr_translator_refactored.py",
        "nlp_translator.py",
        "nlp_translator_refactored.py",
        "tce_tau_translator.py",
        "tce_tau_transformer.py",
    ],
    
    # NLP-specific components
    "nlp": [
        "nlp_enhanced",  # Keep as subdirectory
    ],
    
    # Semantic analysis
    "semantic": [
        "semantic_analyzer.py",
        "semantic_analyzer_core.py",
        "semantic_types.py",
        "semantic_layer_validator.py",
        "semantic_construct_plugin_validator.py",
    ],
    
    # ILR (Intermediate Language Representation) components
    "ilr": [
        "ilr_config.py",
        "ilr_nodes.py",
        "ilr_pattern_analyzer_refactored.py",
        "ilr_pattern_handlers.py",
    ],
    
    # Plugin system
    "plugins": [
        "plugin.py",
        "plugin_manager.py",
        "generic_plugin_validator.py",
        "grammar_plugin_validator.py",
        "grammar_plugin_validator_v2.py",
        "validation_pipeline.py",
    ],
    
    # Preprocessing and grammar handling
    "preprocessing": [
        "preprocessor_directives.py",
        "preprocessor_errors.py",
        "tgf_preprocessor.py",
        "tgf_directive_handler.py",
        "tgf_grammar_loader.py",
        "tgf_macro_processor.py",
    ],
    
    # Utilities and helpers
    "utils": [
        "bloom_filter.py",
        "trie.py",
        "pattern_cache.py",
        "optimized_symbol_table.py",
        "lazy_loader.py",
        "performance_utils.py",
        "expression_builders.py",
        "lark_transformer.py",
    ],
    
    # Configuration
    "config": [
        "logging_config.py",
        "version_handler.py",
    ],
    
    # Test files (should be moved to tests directory)
    "_tests_to_move": [
        "test_visitor_pattern.py",
    ],
    
    # Data files (non-code)
    "_data_files": [
        "semantic_analyzer_review.json",
    ]
}

# Files that appear to be duplicates or deprecated
POTENTIAL_DUPLICATES = [
    ("ast_nodes.py", "ast/ast_nodes.py"),  # Same concept, different locations
    ("ilr_translator.py", "ilr_translator_refactored.py"),  # Original vs refactored
    ("nlp_translator.py", "nlp_translator_refactored.py"),  # Original vs refactored
    ("grammar_plugin_validator.py", "grammar_plugin_validator_v2.py"),  # v1 vs v2
]


def analyze_current_structure(base_path: Path) -> Dict[str, List[str]]:
    """Analyze the current directory structure."""
    current_files = {}
    
    for item in base_path.iterdir():
        if item.is_file() and item.suffix == ".py":
            current_files[item.name] = "file"
        elif item.is_dir() and not item.name.startswith("__"):
            current_files[item.name] = "directory"
    
    return current_files


def create_reorganization_plan(base_path: Path) -> List[Tuple[str, str, str]]:
    """Create a plan for reorganizing files."""
    plan = []  # List of (action, source, destination)
    
    for new_dir, files in NEW_STRUCTURE.items():
        if new_dir.startswith("_"):
            continue  # Skip special categories
            
        for file_or_dir in files:
            source = base_path / file_or_dir
            
            if source.exists():
                if source.is_file():
                    dest = base_path / new_dir / file_or_dir
                    plan.append(("move_file", str(source), str(dest)))
                elif source.is_dir():
                    dest = base_path / new_dir / file_or_dir
                    plan.append(("move_dir", str(source), str(dest)))
    
    return plan


def print_analysis_report(base_path: Path):
    """Print an analysis report of the current structure."""
    print("=" * 70)
    print("CORE ENGINE STRUCTURE ANALYSIS REPORT")
    print("=" * 70)
    
    # Count files by category
    file_counts = {}
    total_files = 0
    
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                total_files += 1
                
                # Categorize based on filename patterns
                if "parser" in file.lower():
                    file_counts["Parsers"] = file_counts.get("Parsers", 0) + 1
                elif "translator" in file.lower():
                    file_counts["Translators"] = file_counts.get("Translators", 0) + 1
                elif "semantic" in file.lower():
                    file_counts["Semantic"] = file_counts.get("Semantic", 0) + 1
                elif "plugin" in file.lower() or "validator" in file.lower():
                    file_counts["Plugins"] = file_counts.get("Plugins", 0) + 1
                elif "ilr" in file.lower():
                    file_counts["ILR"] = file_counts.get("ILR", 0) + 1
                else:
                    file_counts["Other"] = file_counts.get("Other", 0) + 1
    
    print(f"\nTotal Python files: {total_files}")
    print("\nFile distribution by category:")
    for category, count in sorted(file_counts.items()):
        print(f"  {category}: {count}")
    
    print("\n" + "-" * 70)
    print("IDENTIFIED ISSUES:")
    print("-" * 70)
    
    print("\n1. DUPLICATE/DEPRECATED FILES:")
    for orig, refactored in POTENTIAL_DUPLICATES:
        orig_path = base_path / orig
        ref_path = base_path / refactored if "/" not in refactored else base_path / Path(refactored)
        if orig_path.exists() and ref_path.exists():
            print(f"   - {orig} vs {refactored}")
    
    print("\n2. FILES IN ROOT THAT SHOULD BE ORGANIZED:")
    root_files = [f for f in os.listdir(base_path) 
                  if f.endswith(".py") and f != "__init__.py" and f != "reorganize_structure.py"]
    for f in sorted(root_files)[:10]:  # Show first 10
        print(f"   - {f}")
    if len(root_files) > 10:
        print(f"   ... and {len(root_files) - 10} more")
    
    print("\n3. TEST FILES IN PRODUCTION CODE:")
    for f in NEW_STRUCTURE.get("_tests_to_move", []):
        if (base_path / f).exists():
            print(f"   - {f}")
    
    print("\n" + "-" * 70)
    print("PROPOSED NEW STRUCTURE:")
    print("-" * 70)
    
    for new_dir, files in sorted(NEW_STRUCTURE.items()):
        if not new_dir.startswith("_"):
            print(f"\n{new_dir}/")
            for f in sorted(files)[:5]:  # Show first 5 files
                print(f"   ├── {f}")
            if len(files) > 5:
                print(f"   └── ... and {len(files) - 5} more")


def execute_reorganization(base_path: Path, dry_run: bool = True):
    """Execute the reorganization plan."""
    plan = create_reorganization_plan(base_path)
    
    if dry_run:
        print("\n" + "=" * 70)
        print("DRY RUN - PROPOSED CHANGES:")
        print("=" * 70)
        
        for action, source, dest in plan[:10]:  # Show first 10 actions
            if action == "move_file":
                print(f"MOVE FILE: {Path(source).name}")
                print(f"  FROM: {source}")
                print(f"  TO:   {dest}")
            elif action == "move_dir":
                print(f"MOVE DIR: {Path(source).name}")
                print(f"  FROM: {source}")
                print(f"  TO:   {dest}")
            print()
        
        if len(plan) > 10:
            print(f"... and {len(plan) - 10} more operations")
            
        print("\nTo execute the reorganization, run with --execute flag")
    else:
        print("\n" + "=" * 70)
        print("EXECUTING REORGANIZATION...")
        print("=" * 70)
        
        # Create new directories
        for new_dir in NEW_STRUCTURE.keys():
            if not new_dir.startswith("_"):
                dir_path = base_path / new_dir
                dir_path.mkdir(exist_ok=True)
                print(f"Created directory: {new_dir}/")
        
        # Execute moves
        for action, source, dest in plan:
            try:
                dest_path = Path(dest)
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                
                if action == "move_file":
                    shutil.move(source, dest)
                    print(f"Moved: {Path(source).name} -> {Path(dest).parent.name}/")
                elif action == "move_dir":
                    shutil.move(source, dest)
                    print(f"Moved directory: {Path(source).name} -> {Path(dest).parent.name}/")
            except Exception as e:
                print(f"ERROR moving {source}: {e}")


if __name__ == "__main__":
    import sys
    
    base_path = Path(__file__).parent
    
    # Print analysis report
    print_analysis_report(base_path)
    
    # Check if we should execute
    if "--execute" in sys.argv:
        execute_reorganization(base_path, dry_run=False)
    else:
        execute_reorganization(base_path, dry_run=True)