#!/usr/bin/env python3
"""
Cleanup script to organize duplicate implementations and clean the codebase.

This script will:
1. Move experimental/duplicate files to an experiments folder
2. Clean build artifacts (actually delete these)
3. Archive old implementations
4. Keep a record of what was moved

Copyright: DarkLightX/Dana Edwards
"""

import os
import shutil
import sys
from pathlib import Path
from datetime import datetime
import json

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class CodebaseCleanup:
    """Handles cleanup of duplicate files and reorganization."""
    
    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        self.project_root = project_root
        self.experiments_dir = self.project_root / "experiments"
        self.deleted_files = []
        self.moved_files = []
        self.errors = []
        
    def run(self):
        """Execute the cleanup process."""
        print(f"🧹 TauTranslator Codebase Organization")
        print(f"Mode: {'DRY RUN' if self.dry_run else 'ACTUAL CLEANUP'}")
        print(f"Experiments directory: {self.experiments_dir}\n")
        
        # Create experiments directory structure if needed
        if not self.dry_run:
            self.experiments_dir.mkdir(exist_ok=True)
        
        # Phase 1: Clean build artifacts
        print("Phase 1: Cleaning build artifacts...")
        self.clean_build_artifacts()
        
        # Phase 2: Move experimental refactored files
        print("\nPhase 2: Moving experimental refactored files to experiments folder...")
        self.move_refactored_files()
        
        # Phase 3: Move old UI implementations
        print("\nPhase 3: Moving old UI implementations to experiments folder...")
        self.move_old_ui_files()
        
        # Phase 4: Move duplicate FSA engines
        print("\nPhase 4: Moving duplicate FSA engines to experiments folder...")
        self.move_duplicate_fsa_engines()
        
        # Phase 5: Move old security implementations
        print("\nPhase 5: Moving old security implementations to experiments folder...")
        self.move_old_security_files()
        
        # Phase 6: Clean up old core engine
        print("\nPhase 6: Archiving old core engine...")
        self.archive_old_core_engine()
        
        # Summary
        self.print_summary()
        
    def move_file(self, file_path: Path, category: str, reason: str):
        """Move a file to experiments folder with proper organization."""
        try:
            if file_path.exists():
                relative_path = file_path.relative_to(self.project_root)
                dest_path = self.experiments_dir / category / relative_path
                
                print(f"  📦 {relative_path} -> experiments/{category}/{relative_path}")
                print(f"     Reason: {reason}")
                
                if not self.dry_run:
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(file_path), str(dest_path))
                    
                self.moved_files.append({
                    'source': str(relative_path),
                    'destination': f"experiments/{category}/{relative_path}",
                    'reason': reason
                })
        except Exception as e:
            self.errors.append(f"Error moving {file_path}: {e}")
            
    def delete_file(self, file_path: Path, reason: str):
        """Delete a file with backup."""
        try:
            if file_path.exists():
                print(f"  ❌ {file_path.relative_to(self.project_root)} - {reason}")
                self.backup_file(file_path)
                if not self.dry_run:
                    file_path.unlink()
                self.deleted_files.append(str(file_path.relative_to(self.project_root)))
        except Exception as e:
            self.errors.append(f"Error deleting {file_path}: {e}")
            
    def delete_directory(self, dir_path: Path, reason: str):
        """Delete a directory with backup."""
        try:
            if dir_path.exists() and dir_path.is_dir():
                print(f"  📁 {dir_path.relative_to(self.project_root)}/ - {reason}")
                if not self.dry_run:
                    backup_path = self.backup_dir / dir_path.relative_to(self.project_root)
                    shutil.copytree(dir_path, backup_path)
                    shutil.rmtree(dir_path)
                self.deleted_files.append(f"{dir_path.relative_to(self.project_root)}/")
        except Exception as e:
            self.errors.append(f"Error deleting {dir_path}: {e}")
    
    def clean_build_artifacts(self):
        """Remove build artifacts and cache directories."""
        artifacts = [
            "build",
            "dist", 
            "mutants",
            ".pytest_cache",
            "htmlcov",
            ".coverage",
            "*.egg-info"
        ]
        
        for artifact in artifacts:
            for path in self.project_root.glob(f"**/{artifact}"):
                # Skip node_modules and venv directories
                if any(part in path.parts for part in ['node_modules', 'venv', 'venv_bdd']):
                    continue
                if path.is_dir():
                    self.delete_directory(path, "Build artifact")
                else:
                    self.delete_file(path, "Build artifact")
                    
        # Clean __pycache__ directories
        for cache_dir in self.project_root.glob("**/__pycache__"):
            if any(part in cache_dir.parts for part in ['node_modules', 'venv', 'venv_bdd']):
                continue
            self.delete_directory(cache_dir, "Python cache")
    
    def move_refactored_files(self):
        """Move experimental refactored implementations to experiments."""
        refactored_files = [
            "backend/unified/translators/pattern_translator_refactored.py",
            "backend/unified/translators/manager_refactored.py",
            "backend/unified/core/config_refactored.py",
            "backend/unified/core/pattern_loader_refactored.py",
            "backend/unified/api/auth_refactored.py",
            # Test files for refactored code
            "tests/unit/test_pattern_translator_refactored.py",
            "tests/unit/test_auth_refactored.py",
            "tests/unit/test_pattern_loader_refactored.py",
        ]
        
        for file_path in refactored_files:
            self.move_file(
                self.project_root / file_path, 
                "refactored_implementations",
                "Experimental implementation following Intentional Disclosure Principle"
            )
    
    def move_old_ui_files(self):
        """Move old desktop UI implementations to experiments."""
        ui_files = [
            ("ui/tau_translator_desktop_qt.py", "PyQt6 implementation - most feature-rich"),
            ("ui/tau_translator_desktop_tkinter.py", "Tkinter professional version"), 
            ("ui/tau_translator_desktop_modern.py", "Tkinter modern design"),
            ("ui/tau_translator_desktop_legacy.py", "Tkinter legacy/basic version"),
            ("ui/gui_comparison.py", "UI comparison tool"),
            ("ui/comprehensive_qt_integration_test.py", "Qt integration test")
        ]
        
        for file_path, description in ui_files:
            self.move_file(
                self.project_root / file_path, 
                "ui_implementations",
                description
            )
    
    def move_duplicate_fsa_engines(self):
        """Move FSA engine variants to experiments."""
        fsa_variants = [
            ("backend/unified/core/pattern_matching/fsa_engine_fast.py", "Fast implementation variant"),
            ("backend/unified/core/pattern_matching/fsa_engine_hybrid.py", "Hybrid approach variant"),
            ("backend/unified/core/pattern_matching/fsa_engine_optimized.py", "Optimized variant")
        ]
        
        for file_path, description in fsa_variants:
            self.move_file(
                self.project_root / file_path,
                "fsa_variants",
                description
            )
    
    def move_old_security_files(self):
        """Move old security/API manager implementations to experiments."""
        security_dir = self.project_root / "security"
        if security_dir.exists():
            print(f"  📁 Moving entire security/ directory to experiments/")
            if not self.dry_run:
                dest_dir = self.experiments_dir / "old_security_implementations" / "security"
                dest_dir.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(security_dir), str(dest_dir))
            self.moved_files.append({
                'source': 'security/',
                'destination': 'experiments/old_security_implementations/security/',
                'reason': 'Old security implementation (now integrated in core.auth)'
            })
    
    def archive_old_core_engine(self):
        """Move the old core engine to experiments."""
        old_engine = self.project_root / "src/tau_translator_omega"
        if old_engine.exists():
            print(f"  📦 Moving old core engine to experiments/")
            if not self.dry_run:
                dest_path = self.experiments_dir / "old_core_engine" / "tau_translator_omega"
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(old_engine), str(dest_path))
            self.moved_files.append({
                'source': 'src/tau_translator_omega/',
                'destination': 'experiments/old_core_engine/tau_translator_omega/',
                'reason': 'Legacy core engine (superseded by backend/unified)'
            })
    
    def print_summary(self):
        """Print cleanup summary."""
        print(f"\n{'='*60}")
        print(f"Organization Summary")
        print(f"{'='*60}")
        print(f"Files deleted (build artifacts): {len(self.deleted_files)}")
        print(f"Files moved to experiments: {len(self.moved_files)}")
        
        if self.moved_files:
            print(f"\n📦 Moved to experiments folder:")
            # Group by category
            categories = {}
            for move in self.moved_files:
                cat = move['destination'].split('/')[1]
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(move['source'])
            
            for cat, files in categories.items():
                print(f"\n  {cat}:")
                for f in files[:5]:  # Show first 5
                    print(f"    - {f}")
                if len(files) > 5:
                    print(f"    ... and {len(files) - 5} more")
        
        if self.errors:
            print(f"\n❌ Errors encountered: {len(self.errors)}")
            for error in self.errors:
                print(f"  - {error}")
                
        if self.dry_run:
            print(f"\n⚠️  This was a DRY RUN. No files were actually moved.")
            print(f"To perform actual organization, run with --execute flag")
            
            # Save organization plan
            plan_file = self.project_root / "organization_plan.json"
            with open(plan_file, 'w') as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "files_to_delete": self.deleted_files,
                    "files_to_move": self.moved_files,
                    "errors": self.errors
                }, f, indent=2)
            print(f"\nOrganization plan saved to: {plan_file}")
        else:
            print(f"\n✅ Organization completed!")
            print(f"Experiments folder created at: {self.experiments_dir}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Clean up TauTranslator codebase")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually perform the cleanup (default is dry run)"
    )
    
    args = parser.parse_args()
    
    cleanup = CodebaseCleanup(dry_run=not args.execute)
    cleanup.run()


if __name__ == "__main__":
    main()