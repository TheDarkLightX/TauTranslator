"""
Centralized configuration management for the unified backend.
Follows Intentional Disclosure Principle with explicit type annotations.

Copyright: DarkLightX/Dana Edwards
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
            """Set default grammar directory if not provided."""
            if v is None:
                return DirectoryPath(str(values["project_root"] / "grammars"))
            return DirectoryPath(str(Path(v)))
        
        @validator("dictionaries_dir", pre=True, always=True)
        def set_dictionaries_dir(cls: Type["BackendSettings"], v: Optional[str], values: Dict[str, Any]) -> DirectoryPath:
            """Set default dictionaries directory if not provided."""
            if v is None:
                return DirectoryPath(str(values["project_root"] / "example_dictionaries"))
            return DirectoryPath(str(Path(v)))
        
        @validator("sessions_dir", pre=True, always=True)
        def set_sessions_dir(cls: Type["BackendSettings"], v: Optional[str], values: Dict[str, Any]) -> DirectoryPath:
            """Set default sessions directory if not provided."""
            if v is None:
                return DirectoryPath(str(values["project_root"] / "sessions"))
            return DirectoryPath(str(Path(v)))
        
        @validator("cors_origins", pre=True)
        def parse_cors_origins(cls: Type["BackendSettings"], v: ConfigValue) -> List[str]:
            """Parse CORS origins from comma-separated string or list."""
            if isinstance(v, str):
                return [origin.strip() for origin in v.split(",")]
            return v
        
        @validator("cors_methods", pre=True)
        def parse_cors_methods(cls: Type["BackendSettings"], v: ConfigValue) -> List[str]:
            """Parse CORS methods from comma-separated string or list."""
            if isinstance(v, str):
                return [method.strip() for method in v.split(",")]
            return v
        
        @validator("cors_headers", pre=True)
        def parse_cors_headers(cls: Type["BackendSettings"], v: ConfigValue) -> List[str]:
            """Parse CORS headers from comma-separated string or list."""
            if isinstance(v, str):
                return [header.strip() for header in v.split(",")]
            return v
        
        def ensure_directories_exist_async(self) -> None:
            """
            Create necessary directories if they don't exist.
            Follows Rule 1: Name discloses filesystem I/O operation.
            """
            self._create_directory_if_missing(self.grammar_dir)
            self._create_directory_if_missing(self.dictionaries_dir)
            self._create_directory_if_missing(self.sessions_dir)
        
        def _create_directory_if_missing(self, dir_path: Optional[DirectoryPath]) -> None:
            """
            Private method to create a single directory.
            Marked as FileSystemOperation following Rule 4.
            """
            if dir_path and not Path(dir_path).exists():
                Path(dir_path).mkdir(parents=True, exist_ok=True)
        
        class Config:
            env_file = ".env"
            case_sensitive = False


# Global settings instance
if PYDANTIC_AVAILABLE:
    Settings = BackendSettings  # Alias for compatibility
    try:
        settings = BackendSettings()
    except Exception as e:
        # Fallback to simple settings if pydantic fails
        from .simple_config import settings
else:
    # Use simple settings if pydantic not available
    from .simple_config import settings
    Settings = type(settings)  # Use the type of simple settings


def get_settings():
    """Get the current settings instance."""
    return settings