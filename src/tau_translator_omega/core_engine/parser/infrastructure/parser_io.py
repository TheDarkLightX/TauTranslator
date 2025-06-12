"""
Parser I/O infrastructure following the Intentional Disclosure Principle.

All I/O operations are isolated here, with explicit async naming
and complete error handling.

Copyright: DarkLightX / Dana Edwards
"""

import os
import asyncio
import importlib
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional, Type, List
from returns.result import Result, Success, Failure
from returns.future import FutureResult
from returns.io import IOResult

from ..domain.types import (
    GrammarPath, GrammarContent, TransformerClass, ModulePath,
    ClassName, ErrorMessage, CacheKey, ParseTree
)


class FileLoader:
    """Handles all file I/O operations."""
    
    async def load_grammar_file_async(self, path: GrammarPath) -> Result[GrammarContent, str]:
        """Load grammar file with explicit async I/O."""
        try:
            # Convert to Path for better error messages
            file_path = Path(str(path))
            
            if not file_path.exists():
                return Failure(f"Grammar file not found: {path}")
            
            if not file_path.is_file():
                return Failure(f"Grammar path is not a file: {path}")
            
            # Async file read
            content = await self._read_file_async(file_path)
            return Success(GrammarContent(content))
            
        except PermissionError:
            return Failure(f"Permission denied reading grammar file: {path}")
        except IOError as e:
            return Failure(f"I/O error reading grammar file: {e}")
        except Exception as e:
            return Failure(f"Unexpected error reading grammar file: {e}")
    
    async def _read_file_async(self, path: Path) -> str:
        """Async file read implementation."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._read_file_sync, path)
    
    def _read_file_sync(self, path: Path) -> str:
        """Synchronous file read."""
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def resolve_import_paths(self, base_path: GrammarPath, imports: List[str]) -> List[Path]:
        """Resolve import paths relative to grammar file."""
        base = Path(str(base_path)).parent
        resolved = []
        
        for import_path in imports:
            if os.path.isabs(import_path):
                resolved.append(Path(import_path))
            else:
                resolved.append(base / import_path)
        
        return resolved
    
    def compute_file_hash(self, content: GrammarContent) -> str:
        """Compute hash of file content for caching."""
        return hashlib.sha256(str(content).encode()).hexdigest()


class ModuleLoader:
    """Handles dynamic module loading."""
    
    async def load_transformer_class_async(
        self,
        module_path: ModulePath,
        class_name: ClassName
    ) -> Result[Type, str]:
        """Dynamically load transformer class."""
        try:
            # Import module
            module_result = await self._import_module_async(module_path)
            if isinstance(module_result, Failure):
                return module_result
            
            module = module_result.unwrap()
            
            # Get class from module
            if not hasattr(module, str(class_name)):
                return Failure(f"Class {class_name} not found in module {module_path}")
            
            transformer_class = getattr(module, str(class_name))
            
            # Validate it's a class
            if not isinstance(transformer_class, type):
                return Failure(f"{class_name} is not a class")
            
            return Success(transformer_class)
            
        except Exception as e:
            return Failure(f"Failed to load transformer class: {e}")
    
    async def _import_module_async(self, module_path: ModulePath) -> Result[Any, str]:
        """Async module import."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._import_module_sync,
            module_path
        )
    
    def _import_module_sync(self, module_path: ModulePath) -> Result[Any, str]:
        """Synchronous module import."""
        try:
            module = importlib.import_module(str(module_path))
            return Success(module)
        except ImportError as e:
            return Failure(f"Failed to import module {module_path}: {e}")
        except Exception as e:
            return Failure(f"Unexpected error importing module: {e}")
    
    def create_instance(self, cls: Type, args: Dict[str, Any] = None) -> Result[Any, str]:
        """Create instance of loaded class."""
        try:
            instance = cls(**(args or {}))
            return Success(instance)
        except TypeError as e:
            return Failure(f"Invalid arguments for class instantiation: {e}")
        except Exception as e:
            return Failure(f"Failed to instantiate class: {e}")


class PathResolver:
    """Resolves paths relative to project structure."""
    
    def __init__(self, project_root: Optional[Path] = None):
        """Initialize with project root."""
        self._project_root = project_root or self._find_project_root()
    
    def _find_project_root(self) -> Path:
        """Find project root by looking for marker files."""
        current = Path(__file__).resolve()
        
        # Walk up directory tree looking for project markers
        markers = ['pyproject.toml', 'setup.py', '.git']
        
        while current != current.parent:
            for marker in markers:
                if (current / marker).exists():
                    return current
            current = current.parent
        
        # Fallback to current directory
        return Path.cwd()
    
    def resolve_grammar_path(self, path: str) -> Path:
        """Resolve grammar path relative to project."""
        grammar_path = Path(path)
        
        if grammar_path.is_absolute():
            return grammar_path
        
        # Try relative to project root
        project_relative = self._project_root / grammar_path
        if project_relative.exists():
            return project_relative
        
        # Try relative to grammars directory
        grammars_dir = self._project_root / "grammars"
        grammar_relative = grammars_dir / grammar_path
        if grammar_relative.exists():
            return grammar_relative
        
        # Return original path
        return grammar_path
    
    def get_common_grammars_dir(self) -> Path:
        """Get directory for common grammar imports."""
        return (self._project_root / "src" / "tau_translator_omega" / 
                "core_engine" / "grammars")


class CacheManager:
    """Manages parser cache for memoization."""
    
    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize cache manager."""
        self._cache_dir = cache_dir or self._get_default_cache_dir()
        self._ensure_cache_dir_exists()
    
    def _get_default_cache_dir(self) -> Path:
        """Get default cache directory."""
        return Path.home() / ".tau_translator" / "parser_cache"
    
    def _ensure_cache_dir_exists(self) -> None:
        """Ensure cache directory exists."""
        self._cache_dir.mkdir(parents=True, exist_ok=True)
    
    async def get_cached_parse_tree_async(self, key: CacheKey) -> Result[Optional[ParseTree], str]:
        """Retrieve cached parse tree if available."""
        cache_file = self._get_cache_file_path(key)
        
        if not cache_file.exists():
            return Success(None)
        
        try:
            # Load cached data
            import pickle
            
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(
                None,
                self._load_cache_file,
                cache_file
            )
            
            # Validate cache version
            if data.get('version') != key.grammar_version:
                return Success(None)
            
            return Success(data.get('parse_tree'))
            
        except Exception as e:
            # Cache miss on error
            return Success(None)
    
    async def cache_parse_tree_async(
        self,
        key: CacheKey,
        tree: ParseTree
    ) -> Result[None, str]:
        """Cache parse tree for future use."""
        cache_file = self._get_cache_file_path(key)
        
        try:
            import pickle
            
            data = {
                'version': key.grammar_version,
                'parse_tree': tree,
                'cached_at': self._get_timestamp()
            }
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self._save_cache_file,
                cache_file,
                data
            )
            
            return Success(None)
            
        except Exception as e:
            # Caching failure is not critical
            return Success(None)
    
    def _get_cache_file_path(self, key: CacheKey) -> Path:
        """Get cache file path for key."""
        # Use first 16 chars of each hash for reasonable filename
        filename = f"{key.source_hash[:16]}_{key.parser_config_hash[:16]}.cache"
        return self._cache_dir / filename
    
    def _load_cache_file(self, path: Path) -> Dict[str, Any]:
        """Load cache file."""
        import pickle
        with open(path, 'rb') as f:
            return pickle.load(f)
    
    def _save_cache_file(self, path: Path, data: Dict[str, Any]) -> None:
        """Save cache file."""
        import pickle
        with open(path, 'wb') as f:
            pickle.dump(data, f)
    
    def _get_timestamp(self) -> float:
        """Get current timestamp."""
        import time
        return time.time()
    
    def clear_cache(self) -> Result[int, str]:
        """Clear all cached entries."""
        try:
            count = 0
            for cache_file in self._cache_dir.glob("*.cache"):
                cache_file.unlink()
                count += 1
            return Success(count)
        except Exception as e:
            return Failure(f"Failed to clear cache: {e}")


class LoggingService:
    """Centralized logging service for parser."""
    
    def __init__(self, logger_name: str = "parser"):
        """Initialize logging service."""
        import logging
        self._logger = logging.getLogger(logger_name)
    
    def log_info(self, message: str, **kwargs) -> None:
        """Log info message."""
        self._logger.info(message, extra=kwargs)
    
    def log_debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        self._logger.debug(message, extra=kwargs)
    
    def log_warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        self._logger.warning(message, extra=kwargs)
    
    def log_error(self, message: str, error: Optional[Exception] = None, **kwargs) -> None:
        """Log error message."""
        if error:
            self._logger.error(message, exc_info=error, extra=kwargs)
        else:
            self._logger.error(message, extra=kwargs)
    
    def log_parse_attempt(self, source_length: int, grammar_path: str) -> None:
        """Log parse attempt."""
        self.log_debug(
            "Attempting to parse source",
            source_length=source_length,
            grammar_path=grammar_path
        )
    
    def log_parse_success(self, duration_ms: float, node_count: int) -> None:
        """Log successful parse."""
        self.log_info(
            "Parse completed successfully",
            duration_ms=duration_ms,
            node_count=node_count
        )
    
    def log_parse_failure(self, error: str, location: Optional[str] = None) -> None:
        """Log parse failure."""
        self.log_error(
            "Parse failed",
            error=error,
            location=location
        )
    
    def log_cache_hit(self, key: CacheKey) -> None:
        """Log cache hit."""
        self.log_debug(
            "Cache hit for parse tree",
            source_hash=key.source_hash[:8],
            config_hash=key.parser_config_hash[:8]
        )
    
    def log_transformer_loaded(self, class_name: str) -> None:
        """Log transformer loaded."""
        self.log_info(
            "Transformer loaded successfully",
            transformer=class_name
        )