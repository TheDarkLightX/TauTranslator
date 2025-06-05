#!/usr/bin/env python3
"""
Repository Organization Tool
===========================

A tool for organizing the TauTranslator repository structure according to best practices.
Moves files to appropriate directories and creates a clean, maintainable structure.

Author: DarklightX (Dana Edwards)
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Tuple
import json


class RepositoryOrganizer:
    """Tool for organizing repository structure"""
    
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.moves_made = []
        self.dry_run = True
        
    def organize_repository(self, dry_run: bool = True) -> Dict[str, List[str]]:
        """Organize the repository structure"""
        self.dry_run = dry_run
        
        organization_plan = {
            'scripts_moved': [],
            'tools_moved': [],
            'examples_moved': [],
            'config_moved': [],
            'tests_moved': [],
            'docs_moved': [],
            'deprecated_moved': [],
            'errors': []
        }
        
        print(f"🔧 {'Planning' if dry_run else 'Executing'} repository organization...")
        
        # Create necessary directories
        self._ensure_directories()
        
        # Organize different types of files
        organization_plan['scripts_moved'] = self._organize_scripts()
        organization_plan['tools_moved'] = self._organize_tools()
        organization_plan['examples_moved'] = self._organize_examples()
        organization_plan['config_moved'] = self._organize_config_files()
        organization_plan['tests_moved'] = self._organize_test_files()
        organization_plan['docs_moved'] = self._organize_documentation()
        organization_plan['deprecated_moved'] = self._organize_deprecated_files()
        
        return organization_plan
    
    def _ensure_directories(self) -> None:
        """Create necessary directory structure"""
        directories = [
            'scripts',
            'tools',
            'examples', 
            'config',
            'docs/archived',
            'deprecated',
            'archive'
        ]
        
        for dir_path in directories:
            full_path = self.root_path / dir_path
            if not self.dry_run:
                full_path.mkdir(parents=True, exist_ok=True)
                print(f"  📁 Created directory: {dir_path}")
            else:
                print(f"  📁 Would create directory: {dir_path}")
    
    def _organize_scripts(self) -> List[str]:
        """Organize script files"""
        script_patterns = [
            'start_*.py',
            'launch_*.py',
            'setup_*.py',
            'compile_*.py',
            'create_*.py',
            'install_*.py',
            'uninstall.sh',
            'start_*.sh'
        ]
        
        moved_files = []
        scripts_dir = self.root_path / 'scripts'
        
        for pattern in script_patterns:
            for file_path in self.root_path.glob(pattern):
                if file_path.is_file() and file_path.parent == self.root_path:
                    target = scripts_dir / file_path.name
                    if self._move_file(file_path, target):
                        moved_files.append(file_path.name)
        
        return moved_files
    
    def _organize_tools(self) -> List[str]:
        """Organize development tools"""
        tool_patterns = [
            'dev_tools.py',
            'code_quality_tool.py',
            'analyze_*.py',
            'debug_*.py',
            'validate_*.py',
            'check_*.py'
        ]
        
        moved_files = []
        tools_dir = self.root_path / 'tools'
        
        for pattern in tool_patterns:
            for file_path in self.root_path.glob(pattern):
                if file_path.is_file() and file_path.parent == self.root_path:
                    target = tools_dir / file_path.name
                    if self._move_file(file_path, target):
                        moved_files.append(file_path.name)
        
        return moved_files
    
    def _organize_examples(self) -> List[str]:
        """Organize example files"""
        example_patterns = [
            'demo_*.py',
            'example_*.py',
            'advanced_examples.py',
            'ui_*.py'
        ]
        
        moved_files = []
        examples_dir = self.root_path / 'examples'
        
        for pattern in example_patterns:
            for file_path in self.root_path.glob(pattern):
                if file_path.is_file() and file_path.parent == self.root_path:
                    target = examples_dir / file_path.name
                    if self._move_file(file_path, target):
                        moved_files.append(file_path.name)
        
        return moved_files
    
    def _organize_config_files(self) -> List[str]:
        """Organize configuration files"""
        config_files = [
            'provider_config.py',
            'logging_config.py',
            '.env.example',
            'docker-compose.yml',
            'Dockerfile',
            'pyproject.toml',
            'pytest.ini'
        ]
        
        moved_files = []
        config_dir = self.root_path / 'config'
        
        for file_name in config_files:
            file_path = self.root_path / file_name
            if file_path.exists() and file_path.is_file():
                target = config_dir / file_name
                if self._move_file(file_path, target):
                    moved_files.append(file_name)
        
        return moved_files
    
    def _organize_test_files(self) -> List[str]:
        """Organize test files that are in root"""
        test_patterns = [
            'test_*.py',
            'manual_*.py'
        ]
        
        moved_files = []
        tests_dir = self.root_path / 'tests' / 'integration'
        
        # Ensure integration test directory exists
        if not self.dry_run:
            tests_dir.mkdir(parents=True, exist_ok=True)
        
        for pattern in test_patterns:
            for file_path in self.root_path.glob(pattern):
                if file_path.is_file() and file_path.parent == self.root_path:
                    # Skip if it's already a proper test name
                    if file_path.name.startswith('test_'):
                        target = tests_dir / file_path.name
                    else:
                        target = tests_dir / f"test_{file_path.name}"
                    
                    if self._move_file(file_path, target):
                        moved_files.append(file_path.name)
        
        return moved_files
    
    def _organize_documentation(self) -> List[str]:
        """Organize documentation files"""
        doc_patterns = [
            '*.md',
            '*.rst',
            '*.txt'
        ]
        
        moved_files = []
        docs_dir = self.root_path / 'docs'
        archived_dir = docs_dir / 'archived'
        
        # Define which docs should stay in root
        keep_in_root = {
            'README.md',
            'CHANGELOG.md',
            'LICENSE',
            'LICENSE.txt',
            'CONTRIBUTING.md'
        }
        
        for pattern in doc_patterns:
            for file_path in self.root_path.glob(pattern):
                if (file_path.is_file() and 
                    file_path.parent == self.root_path and 
                    file_path.name not in keep_in_root):
                    
                    # Move comprehensive docs to archived
                    if any(keyword in file_path.name.upper() for keyword in 
                          ['COMPLETE', 'COMPREHENSIVE', 'FINAL', 'ENHANCED']):
                        target = archived_dir / file_path.name
                    else:
                        target = docs_dir / file_path.name
                    
                    if self._move_file(file_path, target):
                        moved_files.append(file_path.name)
        
        return moved_files
    
    def _organize_deprecated_files(self) -> List[str]:
        """Move deprecated/old files"""
        deprecated_patterns = [
            'old_*.py',
            'legacy_*.py',
            'backup_*.py',
            '*_old.py',
            '*_backup.py',
            'working_*.py'  # These seem to be working copies
        ]
        
        moved_files = []
        deprecated_dir = self.root_path / 'deprecated'
        
        for pattern in deprecated_patterns:
            for file_path in self.root_path.glob(pattern):
                if file_path.is_file() and file_path.parent == self.root_path:
                    target = deprecated_dir / file_path.name
                    if self._move_file(file_path, target):
                        moved_files.append(file_path.name)
        
        return moved_files
    
    def _move_file(self, source: Path, target: Path) -> bool:
        """Move a file from source to target"""
        try:
            if self.dry_run:
                print(f"  📄 Would move: {source.name} → {target.relative_to(self.root_path)}")
                return True
            else:
                # Ensure target directory exists
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(source), str(target))
                print(f"  📄 Moved: {source.name} → {target.relative_to(self.root_path)}")
                return True
        except Exception as e:
            print(f"  ❌ Error moving {source.name}: {e}")
            return False
    
    def generate_gitignore_updates(self) -> List[str]:
        """Generate recommendations for .gitignore updates"""
        recommendations = [
            "# Development tools outputs",
            "quality_analysis_results.json",
            "code_analysis_results.json",
            "execution_traces.json",
            "",
            "# Temporary files",
            "debug.log",
            "tau_translator.log",
            "*.log",
            "",
            "# Cache directories", 
            "__pycache__/",
            ".pytest_cache/",
            ".coverage",
            "",
            "# IDE files",
            ".vscode/",
            ".idea/",
            "*.swp",
            "*.swo",
            "",
            "# Virtual environments",
            "venv/",
            "env/",
            ".venv/",
            "",
            "# Build artifacts",
            "build/",
            "dist/",
            "*.egg-info/",
            "",
            "# Node modules (for PWA)",
            "pwa/node_modules/",
            "pwa/.next/",
            "",
            "# Model files",
            "models/*",
            "!models/.gitkeep",
            "",
            "# Session files",
            "sessions/*",
            "",
            "# Logs directory",
            "logs/*"
        ]
        
        return recommendations


def main():
    """Main function to organize repository"""
    project_root = Path(__file__).parent
    
    print("🗂️  TauTranslator Repository Organization")
    print("=" * 60)
    
    organizer = RepositoryOrganizer(project_root)
    
    # First, run a dry run to see what would happen
    print("\n📋 DRY RUN - Planning organization...")
    dry_run_results = organizer.organize_repository(dry_run=True)
    
    # Show summary
    total_moves = sum(len(files) for files in dry_run_results.values() if isinstance(files, list))
    print(f"\n📊 Organization Summary:")
    print(f"  Scripts to move: {len(dry_run_results['scripts_moved'])}")
    print(f"  Tools to move: {len(dry_run_results['tools_moved'])}")  
    print(f"  Examples to move: {len(dry_run_results['examples_moved'])}")
    print(f"  Config files to move: {len(dry_run_results['config_moved'])}")
    print(f"  Test files to move: {len(dry_run_results['tests_moved'])}")
    print(f"  Docs to move: {len(dry_run_results['docs_moved'])}")
    print(f"  Deprecated files to move: {len(dry_run_results['deprecated_moved'])}")
    print(f"  Total files to move: {total_moves}")
    
    # Ask for confirmation (auto-proceed if in non-interactive mode)
    try:
        response = input(f"\n❓ Proceed with organizing {total_moves} files? (y/N): ")
        proceed = response.lower() in ['y', 'yes']
    except EOFError:
        # Non-interactive mode, proceed automatically
        print(f"\n🤖 Non-interactive mode detected. Proceeding with organization...")
        proceed = True
    
    if proceed:
        print("\n🚀 Executing organization plan...")
        actual_results = organizer.organize_repository(dry_run=False)
        
        # Save organization report
        report = {
            'dry_run_plan': dry_run_results,
            'actual_execution': actual_results,
            'gitignore_recommendations': organizer.generate_gitignore_updates()
        }
        
        report_file = project_root / 'organization_report.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n✅ Organization complete! Report saved to: {report_file}")
        
        # Show .gitignore recommendations
        print(f"\n📝 Recommended .gitignore additions:")
        print("-" * 40)
        for line in organizer.generate_gitignore_updates()[:20]:
            print(line)
        
    else:
        print("\n❌ Organization cancelled.")
        
        # Still save the dry run results for reference
        report_file = project_root / 'organization_plan.json'
        with open(report_file, 'w') as f:
            json.dump(dry_run_results, f, indent=2)
        
        print(f"💾 Organization plan saved to: {report_file}")


if __name__ == "__main__":
    main()