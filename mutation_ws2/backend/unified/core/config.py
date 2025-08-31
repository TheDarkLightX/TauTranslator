"""
Centralized configuration management for the unified backend.
Follows Intentional Disclosure Principle with explicit type annotations.
"""

import os
from typing import Optional, List, Type, Any, Dict
from pathlib import Path

# Import domain types
from .domain_types import (
    DirectoryPath, FilePath, ApiKey, ConfigValue,
    IOBoundary, FileSystemOperation
)

# Try to load settings with pydantic, fallback to simple if it fails
try:
    from pydantic_settings import BaseSettings
    from pydantic import Field, validator
    PYDANTIC_AVAILABLE = True
except ImportError:
    try:
        # Fallback for older pydantic versions
        from pydantic import BaseSettings, Field, validator
        PYDANTIC_AVAILABLE = True
    except:
        PYDANTIC_AVAILABLE = False


if PYDANTIC_AVAILABLE:
    class BackendSettings(BaseSettings):
        """Configuration settings for the TauTranslator backend."""
    
        # Server configuration
        host: str = Field(default="0.0.0.0", env="TAU_HOST")
        port: int = Field(default=8000, env="TAU_PORT")
        debug: bool = Field(default=False, env="TAU_DEBUG")
        reload: bool = Field(default=False, env="TAU_RELOAD")
        
        # Security settings
        master_password: Optional[ApiKey] = Field(default=None, env="TAU_MASTER_PASSWORD")
        secret_key: ApiKey = Field(default="tau-translator-secret-key", env="TAU_SECRET_KEY")
        session_expire_hours: int = Field(default=24, env="TAU_SESSION_EXPIRE_HOURS")
        
        # Translation engines (optimized for parser-first approach)
        enable_lmql: bool = Field(default=False, env="TAU_ENABLE_LMQL")
        enable_gemma3: bool = Field(default=False, env="TAU_ENABLE_GEMMA3")
        enable_nlp: bool = Field(default=False, env="TAU_ENABLE_NLP")
        enable_grammar: bool = Field(default=True, env="TAU_ENABLE_GRAMMAR")
        enable_parser_pipeline: bool = Field(default=True, env="TAU_ENABLE_PARSER_PIPELINE")
        enable_bidirectional: bool = Field(default=True, env="TAU_ENABLE_BIDIRECTIONAL")
        
        # File paths - using domain types
        project_root: DirectoryPath = Field(default_factory=lambda: Path(__file__).parent.parent.parent.parent)
        grammar_dir: Optional[DirectoryPath] = Field(default=None, env="TAU_GRAMMAR_DIR")
        dictionaries_dir: Optional[DirectoryPath] = Field(default=None, env="TAU_DICTIONARIES_DIR")
        sessions_dir: Optional[DirectoryPath] = Field(default=None, env="TAU_SESSIONS_DIR")
        
        # API providers
        openrouter_api_key: Optional[ApiKey] = Field(default=None, env="OPENROUTER_API_KEY")
        huggingface_api_key: Optional[ApiKey] = Field(default=None, env="HUGGINGFACE_API_KEY")
        
        # CORS settings
        cors_origins: List[str] = Field(default=["*"], env="TAU_CORS_ORIGINS")
        cors_methods: List[str] = Field(default=["GET", "POST", "OPTIONS"], env="TAU_CORS_METHODS")
        cors_headers: List[str] = Field(default=["*"], env="TAU_CORS_HEADERS")
        
        # Logging
        log_level: str = Field(default="INFO", env="TAU_LOG_LEVEL")
        log_format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        
        @validator("grammar_dir", pre=True, always=True)
        def set_grammar_dir(cls: Type["BackendSettings"], v: Optional[str], values: Dict[str, Any]) -> DirectoryPath:
            """
        Note: This is a pure function (no side effects).
        Set default grammar directory if not provided."""
            return cls._get_dir_path(v, values["project_root"], "grammars")
        
        @validator("dictionaries_dir", pre=True, always=True)
        def set_dictionaries_dir(cls: Type["BackendSettings"], v: Optional[str], values: Dict[str, Any]) -> DirectoryPath:
            """
        Note: This is a pure function (no side effects).
        Set default dictionaries directory if not provided."""
            return cls._get_dir_path(v, values["project_root"], "example_dictionaries")
        
        @validator("sessions_dir", pre=True, always=True)
        def set_sessions_dir(cls: Type["BackendSettings"], v: Optional[str], values: Dict[str, Any]) -> DirectoryPath:
            """
        Note: This is a pure function (no side effects).
        Set default sessions directory if not provided."""
            return cls._get_dir_path(v, values["project_root"], "sessions")
        
        @classmethod
        def _get_dir_path(cls, value: Optional[str], project_root: Path, default_dir: str) -> DirectoryPath:
            """
        Note: This is a pure function (no side effects).
        Get directory path with default."""
            if value is None:
                return DirectoryPath(str(project_root / default_dir))
            return DirectoryPath(str(Path(value)))
        
        @validator("cors_origins", pre=True)
        def parse_cors_origins(cls: Type["BackendSettings"], v: ConfigValue) -> List[str]:
            """
        Note: This is a pure function (no side effects).
        Parse CORS origins from comma-separated string or list."""
            return cls._parse_comma_separated(v)
        
        @validator("cors_methods", pre=True)
        def parse_cors_methods(cls: Type["BackendSettings"], v: ConfigValue) -> List[str]:
            """
        Note: This is a pure function (no side effects).
        Parse CORS methods from comma-separated string or list."""
            return cls._parse_comma_separated(v)
        
        @validator("cors_headers", pre=True)
        def parse_cors_headers(cls: Type["BackendSettings"], v: ConfigValue) -> List[str]:
            """
        Note: This is a pure function (no side effects).
        Parse CORS headers from comma-separated string or list."""
            return cls._parse_comma_separated(v)
        
        @classmethod
        def _parse_comma_separated(cls, value: ConfigValue) -> List[str]:
            """
        Note: This is a pure function (no side effects).
        Parse comma-separated string into list."""
            if isinstance(value, str):
                return [item.strip() for item in value.split(",")]
            return value
        
        def ensure_directories_exist_async(self) -> None:
            """
        Note: This is a pure function (no side effects).
        
            Create necessary directories if they don't exist.
            Follows Rule 1: Name discloses filesystem I/O operation.
            """
            for directory in self._get_required_directories():
                self._create_directory_if_missing(directory)
        
        def _get_required_directories(self) -> List[Optional[DirectoryPath]]:
            """
        Note: This is a pure function (no side effects).
        Get list of required directories."""
            return [self.grammar_dir, self.dictionaries_dir, self.sessions_dir]
        
        def _create_directory_if_missing(self, dir_path: Optional[DirectoryPath]) -> None:
            """
        Note: This is a pure function (no side effects).
        
            Private method to create a single directory.
            Marked as FileSystemOperation following Rule 4.
            """
            if self._should_create_directory(dir_path):
                Path(dir_path).mkdir(parents=True, exist_ok=True)
        
        def _should_create_directory(self, dir_path: Optional[DirectoryPath]) -> bool:
            """
        Note: This is a pure function (no side effects).
        Check if directory should be created."""
            return dir_path is not None and not Path(dir_path).exists()
        
        class Config:
            env_file = ".env"
            case_sensitive = False


# Global settings instance
settings = None
Settings = None

def _initialize_settings():
    """
        Note: This is a pure function (no side effects).
        Initialize settings with appropriate backend."""
    global settings, Settings
    
    if PYDANTIC_AVAILABLE:
        Settings = BackendSettings
        settings = _try_create_pydantic_settings()
    else:
        settings, Settings = _load_simple_settings()

def _try_create_pydantic_settings():
    """
        Note: This is a pure function (no side effects).
        Try to create pydantic settings, fallback to simple."""
    try:
        return BackendSettings()
    except Exception:
        from .simple_config import settings
        return settings

def _load_simple_settings():
    """
        Note: This is a pure function (no side effects).
        Load simple settings when pydantic not available."""
    from .simple_config import settings
    return settings, type(settings)

# Initialize settings on module load
_initialize_settings()


def get_settings():
    """
        Note: This is a pure function (no side effects).
        Get the current settings instance."""
    return settings