#!/usr/bin/env python3
"""
Reorganize the core_engine directory structure for better modularity.

This script:
1. Creates a new directory structure
2. Moves files to appropriate directories
3. Removes duplicates (keeping refactored versions)
4. Extracts demo code from production files
5. Creates backups before changes
6. Generates a change report
"""

import os
import shutil
import json
import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Set
import argparse
import hashlib

PROJECT_ROOT = Path(__file__).resolve().parent.parent

class CoreEngineReorganizer:
    def __init__(self, base_path: str, dry_run: bool = False):
        self.base_path = Path(base_path)
        self.core_engine_path = self.base_path / "src" / "tau_translator_omega" / "core_engine"
        self.tests_path = self.base_path / "tests"
        self.scripts_path = self.base_path / "scripts"
        self.dry_run = dry_run
        self.changes_log = []
        self.backup_dir = None
        
        # Define the new directory structure
        self.new_dirs = {
            "ast": "AST-related modules",
            "parsers": "Parser implementations",
            "translators": "Translation engines",
            "semantic": "Semantic analysis",
            "ilr": "ILR (Intermediate Language Representation)",
            "plugins": "Plugin system",
            "preprocessing": "Preprocessor and directives",
            "utils": "Utility modules",
            "config": "Configuration modules"
        }
        
        # File mapping rules
        self.file_mappings = {
            "ast": ["ast_nodes.py", "ast_visitor.py", "expression_builders.py"],
            "parsers": [
                "parser_refactored.py", "enhanced_parser.py", "grammar_driven_parser.py",
                "parser.py", "incremental_parser.py", "cnl_parser", "ebnf_parser",
                "parser"  # directory
            ],
            "translators": [
                "core_translator.py", "ilr_translator.py", "nlp_translator_refactored.py",
                "nlp_translator.py", "tce_tau_translator.py", "tce_tau_transformer.py",
                "symmetric_translator.py", "english_to_tau_translator.py",
                "translator_factory.py"
            ],
            "semantic": [
                "semantic_analyzer.py", "semantic_analyzer_core.py", 
                "semantic_analyzer_refactored.py", "amr_semantic_layer.py"
            ],
            "ilr": [
                "ilr_nodes.py", "ilr_config.py", "ilr_pattern_handlers.py",
                "ilr_pattern_analyzer_refactored.py", "ilr_pattern_analyzer.py",
                "ilr_patterns.py"
            ],
            "plugins": [
                "plugin_manager.py", "plugin_manager_refactored.py",
                "generic_plugin_validator.py", "grammar_plugin_validator.py",
                "grammar_plugin_validator_v2.py", "plugin_registry.py"
            ],
            "preprocessing": [
                "preprocessor_directives.py", "preprocessor_errors.py",
                "preprocessor.py"
            ],
            "utils": [
                "bloom_filter.py", "lazy_loader.py", "logging_config.py",
                "validation_pipeline.py", "reorganize_structure.py"
            ],
            "config": ["config.py", "ilr_config.py", "logging_config.py"]
        }
        
        # Files to remove (duplicates/old versions)
        self.files_to_remove = {
            "parser.py": "parser_refactored.py",
            "semantic_analyzer.py": "semantic_analyzer_refactored.py",
            "plugin_manager.py": "plugin_manager_refactored.py",
            "ilr_pattern_analyzer.py": "ilr_pattern_analyzer_refactored.py",
            "nlp_translator.py": "nlp_translator_refactored.py",
            "requirements_analyzer.py": "requirements_analyzer_refactored.py"
        }
        
        # Demo/test code patterns to extract
        self.demo_patterns = [
            "if __name__ == '__main__':",
            "def demo_",
            "def test_demo_",
            "# Demo:",
            "# Example usage:"
        ]

    def create_backup(self):
        """Create a backup of the current state."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = self.base_path / f"backups/core_engine_backup_{timestamp}"
        
        if not self.dry_run:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            shutil.copytree(
                self.core_engine_path,
                self.backup_dir / "core_engine",
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store")
            )
            
        self.changes_log.append({
            "action": "backup_created",
            "location": str(self.backup_dir)
        })
        print(f"{'[DRY RUN] ' if self.dry_run else ''}Created backup at: {self.backup_dir}")

    def create_new_structure(self):
        """Create the new directory structure."""
        for dir_name, description in self.new_dirs.items():
            new_dir = self.core_engine_path / dir_name
            if not self.dry_run:
                new_dir.mkdir(exist_ok=True)
                # Create __init__.py
                (new_dir / "__init__.py").touch()
            
            self.changes_log.append({
                "action": "directory_created",
                "path": str(new_dir),
                "description": description
            })
            print(f"{'[DRY RUN] ' if self.dry_run else ''}Created directory: {new_dir}")

    def get_file_hash(self, file_path: Path) -> str:
        """Get MD5 hash of a file for duplicate detection."""
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()

    def find_duplicates(self) -> Dict[str, List[Path]]:
        """Find duplicate files based on content hash."""
        hash_map = {}
        for file_path in self.core_engine_path.rglob("*.py"):
            if file_path.is_file():
                file_hash = self.get_file_hash(file_path)
                if file_hash not in hash_map:
                    hash_map[file_hash] = []
                hash_map[file_hash].append(file_path)
        
        # Return only duplicates
        return {h: files for h, files in hash_map.items() if len(files) > 1}

    def extract_demo_code(self, file_path: Path) -> str:
        """Extract demo/test code from a file."""
        with open(file_path, 'r') as f:
            content = f.read()
        
        demo_lines = []
        in_demo = False
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if any(pattern in line for pattern in self.demo_patterns):
                in_demo = True
            
            if in_demo:
                demo_lines.append(line)
                
            # Stop at the next function/class definition
            if in_demo and i > 0 and (line.startswith('def ') or line.startswith('class ')):
                if not any(pattern in line for pattern in self.demo_patterns):
                    break
        
        return '\n'.join(demo_lines) if demo_lines else ""

    def move_file(self, source: Path, dest_dir: str):
        """Move a file to the destination directory."""
        dest_path = self.core_engine_path / dest_dir / source.name
        
        if not self.dry_run:
            # Extract demo code first if present
            demo_code = self.extract_demo_code(source)
            if demo_code:
                demo_file = self.scripts_path / "demos" / f"demo_{source.stem}.py"
                demo_file.parent.mkdir(exist_ok=True)
                with open(demo_file, 'w') as f:
                    f.write(f"#!/usr/bin/env python3\n")
                    f.write(f'"""Demo code extracted from {source.name}"""\n\n')
                    f.write(demo_code)
                
                self.changes_log.append({
                    "action": "demo_extracted",
                    "source": str(source),
                    "demo_file": str(demo_file)
                })
            
            # Move the file
            shutil.move(str(source), str(dest_path))
        
        self.changes_log.append({
            "action": "file_moved",
            "source": str(source),
            "destination": str(dest_path)
        })
        print(f"{'[DRY RUN] ' if self.dry_run else ''}Moved {source.name} to {dest_dir}/")

    def move_test_files(self):
        """Move test files to the tests directory."""
        test_patterns = ["test_*.py", "*_test.py", "*_tests.py"]
        
        for pattern in test_patterns:
            for test_file in self.core_engine_path.rglob(pattern):
                if test_file.is_file():
                    # Determine test type
                    if "unit" in str(test_file):
                        dest_dir = self.tests_path / "unit"
                    elif "integration" in str(test_file):
                        dest_dir = self.tests_path / "integration"
                    else:
                        dest_dir = self.tests_path / "unit"  # default
                    
                    if not self.dry_run:
                        dest_dir.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(test_file), str(dest_dir / test_file.name))
                    
                    self.changes_log.append({
                        "action": "test_moved",
                        "source": str(test_file),
                        "destination": str(dest_dir / test_file.name)
                    })
                    print(f"{'[DRY RUN] ' if self.dry_run else ''}Moved test {test_file.name} to {dest_dir}")

    def reorganize_files(self):
        """Reorganize files according to the mapping rules."""
        # First, handle duplicates
        duplicates = self.find_duplicates()
        for file_hash, files in duplicates.items():
            # Keep the refactored version or the newest one
            files_sorted = sorted(files, key=lambda f: "refactored" in f.name, reverse=True)
            keep_file = files_sorted[0]
            
            for file_path in files_sorted[1:]:
                if not self.dry_run:
                    file_path.unlink()
                self.changes_log.append({
                    "action": "duplicate_removed",
                    "file": str(file_path),
                    "kept": str(keep_file)
                })
                print(f"{'[DRY RUN] ' if self.dry_run else ''}Removed duplicate: {file_path.name}")
        
        # Move files to appropriate directories
        for dest_dir, file_patterns in self.file_mappings.items():
            for pattern in file_patterns:
                # Handle both files and directories
                for item in self.core_engine_path.glob(pattern):
                    if item.is_file() and item.parent == self.core_engine_path:
                        self.move_file(item, dest_dir)
                    elif item.is_dir() and dest_dir == "parsers":
                        # Move parser directories
                        dest_path = self.core_engine_path / dest_dir / item.name
                        if not self.dry_run:
                            shutil.move(str(item), str(dest_path))
                        self.changes_log.append({
                            "action": "directory_moved",
                            "source": str(item),
                            "destination": str(dest_path)
                        })
                        print(f"{'[DRY RUN] ' if self.dry_run else ''}Moved directory {item.name} to {dest_dir}/")
        
        # Handle nlp_enhanced directory separately
        nlp_dir = self.core_engine_path / "nlp_enhanced"
        if nlp_dir.exists():
            dest_dir = self.core_engine_path / "translators" / "nlp_enhanced"
            if not self.dry_run:
                shutil.move(str(nlp_dir), str(dest_dir))
            self.changes_log.append({
                "action": "directory_moved",
                "source": str(nlp_dir),
                "destination": str(dest_dir)
            })
            print(f"{'[DRY RUN] ' if self.dry_run else ''}Moved nlp_enhanced/ to translators/")

    def update_imports(self):
        """Update import statements in all Python files."""
        # This is a complex operation that would need careful handling
        # For now, we'll just log what needs to be done
        self.changes_log.append({
            "action": "imports_need_update",
            "note": "Run update_imports_after_cleanup.py after reorganization"
        })
        print("\nNote: Import statements will need to be updated. Run update_imports_after_cleanup.py")

    def generate_report(self):
        """Generate a detailed report of all changes."""
        report_path = self.base_path / "reports" / f"reorganization_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = {
            "timestamp": datetime.datetime.now().isoformat(),
            "dry_run": self.dry_run,
            "backup_location": str(self.backup_dir) if self.backup_dir else None,
            "changes": self.changes_log,
            "summary": {
                "directories_created": len([c for c in self.changes_log if c["action"] == "directory_created"]),
                "files_moved": len([c for c in self.changes_log if c["action"] == "file_moved"]),
                "tests_moved": len([c for c in self.changes_log if c["action"] == "test_moved"]),
                "duplicates_removed": len([c for c in self.changes_log if c["action"] == "duplicate_removed"]),
                "demos_extracted": len([c for c in self.changes_log if c["action"] == "demo_extracted"])
            }
        }
        
        if not self.dry_run:
            report_path.parent.mkdir(exist_ok=True)
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
        
        print(f"\n{'[DRY RUN] ' if self.dry_run else ''}Report saved to: {report_path}")
        print("\nSummary:")
        for key, value in report["summary"].items():
            print(f"  {key.replace('_', ' ').title()}: {value}")

    def run(self):
        """Execute the reorganization process."""
        print(f"Starting core_engine reorganization {'[DRY RUN]' if self.dry_run else ''}")
        print(f"Base path: {self.base_path}")
        print(f"Core engine path: {self.core_engine_path}\n")
        
        # Step 1: Create backup
        self.create_backup()
        
        # Step 2: Create new directory structure
        print("\nCreating new directory structure...")
        self.create_new_structure()
        
        # Step 3: Move test files
        print("\nMoving test files...")
        self.move_test_files()
        
        # Step 4: Reorganize files
        print("\nReorganizing files...")
        self.reorganize_files()
        
        # Step 5: Note about imports
        self.update_imports()
        
        # Step 6: Generate report
        print("\nGenerating report...")
        self.generate_report()
        
        if self.dry_run:
            print("\n[DRY RUN COMPLETE] No actual changes were made.")
            print("Run without --dry-run to execute the reorganization.")
        else:
            print("\nReorganization complete!")
            print(f"Backup created at: {self.backup_dir}")
            print("\nNext steps:")
            print("1. Run update_imports_after_cleanup.py to fix import statements")
            print("2. Run tests to ensure everything still works")
            print("3. Review the reorganization report")

def main():
    parser = argparse.ArgumentParser(description="Reorganize core_engine directory structure")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform a dry run without making actual changes"
    )
    parser.add_argument(
        "--base-path",
        type=str,
        default=str(PROJECT_ROOT),
        help="Base path of the TauTranslator project"
    )
    
    args = parser.parse_args()
    
    reorganizer = CoreEngineReorganizer(args.base_path, args.dry_run)
    reorganizer.run()

if __name__ == "__main__":
    main()