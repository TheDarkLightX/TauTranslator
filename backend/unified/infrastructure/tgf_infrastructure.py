"""
TGF infrastructure layer following the Intentional Disclosure Principle.

Isolates all I/O operations, file system access, and external dependencies
from business logic according to IDP Rule 4.

Copyright: DarkLightX / Dana Edwards
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from ..core.result_enhanced import Result, Success, Failure

from ..domain.tgf_types import (
    TGFFilename, TGFContent, ConfigPath, GrammarDirectory,
    GrammarConfig, GrammarFileType, LoadedGrammar
)

logger = logging.getLogger(__name__)


class ConfigFileManager:
    """Handles all grammar configuration file I/O operations."""
    
    @staticmethod
    def load_config(config_path: ConfigPath) -> Result[List[GrammarConfig]]:
        """Load grammar configuration from file."""
        try:
            config_file = Path(config_path)
            if not config_file.exists():
                logger.warning(f"Grammar config file not found: {config_path}")
                return Success([])
            
            with open(config_file, 'r', encoding='utf-8') as f:
                raw_config = json.load(f)
            
            configs = [GrammarConfig.from_dict(item) for item in raw_config]
            logger.info(f"Loaded {len(configs)} grammar configurations")
            return Success(configs)
            
        except json.JSONDecodeError as e:
            return Failure(f"Invalid JSON in config file {config_path}: {e}")
        except PermissionError:
            return Failure(f"Permission denied reading config file: {config_path}")
        except Exception as e:
            return Failure(f"Error loading grammar config: {e}")
    
    @staticmethod
    def save_config(config_path: ConfigPath, configs: List[GrammarConfig]) -> Result[None]:
        """Save grammar configuration to file."""
        try:
            config_file = Path(config_path)
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            config_data = [config.to_dict() for config in configs]
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2)
            
            logger.info(f"Saved {len(configs)} grammar configurations")
            return Success(None)
            
        except PermissionError:
            return Failure(f"Permission denied writing config file: {config_path}")
        except Exception as e:
            return Failure(f"Error saving grammar config: {e}")


class GrammarFileReader:
    """Handles grammar file reading operations."""
    
    @staticmethod
    def read_grammar_file(grammar_dir: GrammarDirectory, filename: TGFFilename) -> Result[TGFContent]:
        """Read grammar file content with error handling."""
        try:
            filepath = Path(grammar_dir) / filename
            
            if not filepath.exists():
                return Failure(f"Grammar file not found: {filepath}")
            
            if not filepath.is_file():
                return Failure(f"Path is not a file: {filepath}")
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip():
                return Failure(f"Grammar file is empty: {filepath}")
            
            logger.info(f"Read grammar file: {filename} ({len(content)} characters)")
            return Success(TGFContent(content))
            
        except PermissionError:
            return Failure(f"Permission denied reading grammar file: {filename}")
        except UnicodeDecodeError:
            return Failure(f"Grammar file encoding error: {filename}")
        except Exception as e:
            return Failure(f"Failed to read grammar file {filename}: {e}")
    
    @staticmethod
    def get_file_info(grammar_dir: GrammarDirectory, filename: TGFFilename) -> Dict[str, Any]:
        """Get file information for validation."""
        filepath = Path(grammar_dir) / filename
        
        return {
            "exists": filepath.exists(),
            "is_file": filepath.is_file() if filepath.exists() else False,
            "size_bytes": filepath.stat().st_size if filepath.exists() else 0,
            "last_modified": filepath.stat().st_mtime if filepath.exists() else None,
            "extension": filepath.suffix.lower()
        }


class DirectoryValidator:
    """Validates directory structure and permissions."""
    
    @staticmethod
    def validate_grammar_directory(grammar_dir: GrammarDirectory) -> Result[str]:
        """Validate grammar directory exists and is accessible."""
        try:
            dir_path = Path(grammar_dir)
            
            if not dir_path.exists():
                return Failure(f"Grammar directory does not exist: {grammar_dir}")
            
            if not dir_path.is_dir():
                return Failure(f"Path is not a directory: {grammar_dir}")
            
            if not dir_path.stat().st_mode & 0o444:  # Check read permission
                return Failure(f"Grammar directory is not readable: {grammar_dir}")
            
            logger.debug(f"Grammar directory validated: {grammar_dir}")
            return Success(str(dir_path.resolve()))
            
        except Exception as e:
            return Failure(f"Error validating grammar directory {grammar_dir}: {e}")
    
    @staticmethod
    def validate_config_directory(config_path: ConfigPath) -> Result[str]:
        """Validate config file directory structure."""
        try:
            config_file = Path(config_path)
            config_dir = config_file.parent
            
            if not config_dir.exists():
                # Try to create directory
                config_dir.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created config directory: {config_dir}")
            
            if not config_dir.is_dir():
                return Failure(f"Config path parent is not a directory: {config_dir}")
            
            # Check write permissions
            if not config_dir.stat().st_mode & 0o222:
                return Failure(f"Config directory is not writable: {config_dir}")
            
            return Success(str(config_dir.resolve()))
            
        except Exception as e:
            return Failure(f"Error validating config directory: {e}")


class GrammarFileTypeDetector:
    """Detects and validates grammar file types."""
    
    @staticmethod
    def detect_file_type(filename: TGFFilename) -> GrammarFileType:
        """Detect grammar file type from filename."""
        extension = Path(filename).suffix.lower()
        
        try:
            return GrammarFileType(extension)
        except ValueError:
            # Default to TGF for unknown extensions
            logger.warning(f"Unknown grammar file type: {extension}, defaulting to TGF")
            return GrammarFileType.TGF
    
    @staticmethod
    def validate_file_type_support(file_type: GrammarFileType) -> bool:
        """Check if file type is supported for processing."""
        supported_types = {GrammarFileType.TGF, GrammarFileType.LARK}
        return file_type in supported_types


class LoadedGrammarFactory:
    """Factory for creating LoadedGrammar instances."""
    
    @staticmethod
    def create_loaded_grammar(
        filename: TGFFilename,
        content: TGFContent,
        is_active: bool = False
    ) -> LoadedGrammar:
        """Create LoadedGrammar instance from file data."""
        file_type = GrammarFileTypeDetector.detect_file_type(filename)
        
        return LoadedGrammar(
            filename=filename,
            original_name=str(filename),  # Can be customized later
            file_type=file_type,
            content=content,
            is_active=is_active
        )


class TGFFileScanner:
    """Scans directories for grammar files."""
    
    @staticmethod
    def scan_grammar_directory(grammar_dir: GrammarDirectory) -> Result[List[TGFFilename]]:
        """Scan directory for grammar files."""
        try:
            dir_path = Path(grammar_dir)
            
            if not dir_path.exists():
                return Failure(f"Directory does not exist: {grammar_dir}")
            
            # Define supported extensions
            supported_extensions = {'.tgf', '.lark', '.ebnf', '.g4'}
            
            grammar_files = []
            for file_path in dir_path.iterdir():
                if (file_path.is_file() and 
                    file_path.suffix.lower() in supported_extensions):
                    grammar_files.append(TGFFilename(file_path.name))
            
            grammar_files.sort()  # Sort alphabetically
            logger.info(f"Found {len(grammar_files)} grammar files in {grammar_dir}")
            return Success(grammar_files)
            
        except PermissionError:
            return Failure(f"Permission denied scanning directory: {grammar_dir}")
        except Exception as e:
            return Failure(f"Error scanning grammar directory: {e}")


class SystemPathResolver:
    """Resolves system paths and handles path-related operations."""
    
    @staticmethod
    def resolve_absolute_path(path: str) -> str:
        """Resolve to absolute path."""
        return str(Path(path).resolve())
    
    @staticmethod
    def get_project_root() -> Path:
        """Find project root directory."""
        current = Path(__file__).parent
        
        # Look for project indicators
        indicators = ['pyproject.toml', '.git', 'README.md', 'setup.py']
        
        while current != current.parent:
            if any((current / indicator).exists() for indicator in indicators):
                return current
            current = current.parent
        
        # Fallback to several levels up from this file
        return Path(__file__).parent.parent.parent.parent
    
    @staticmethod
    def resolve_grammar_directory(relative_path: str) -> GrammarDirectory:
        """Resolve grammar directory relative to project root."""
        project_root = SystemPathResolver.get_project_root()
        grammar_path = project_root / relative_path
        return GrammarDirectory(str(grammar_path))
    
    @staticmethod
    def resolve_config_path(relative_path: str) -> ConfigPath:
        """Resolve config file path relative to project root."""
        project_root = SystemPathResolver.get_project_root()
        config_path = project_root / relative_path
        return ConfigPath(str(config_path))


class FileSystemLockManager:
    """Manages file system locks for concurrent access."""
    
    def __init__(self):
        self._locks = {}
    
    def acquire_file_lock(self, filepath: str) -> bool:
        """Acquire lock for file access."""
        # Simple implementation - could use fcntl for real locking
        if filepath in self._locks:
            return False
        
        self._locks[filepath] = True
        return True
    
    def release_file_lock(self, filepath: str) -> None:
        """Release file lock."""
        self._locks.pop(filepath, None)
    
    def is_file_locked(self, filepath: str) -> bool:
        """Check if file is currently locked."""
        return filepath in self._locks


# Global instances for easy access
_file_lock_manager = FileSystemLockManager()

def get_file_lock_manager() -> FileSystemLockManager:
    """Get global file lock manager instance."""
    return _file_lock_manager