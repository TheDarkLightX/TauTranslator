"""
Centralized configuration management for the unified backend.

Provides environment-based configuration with validation and type safety.

Author: DarkLightX / Dana Edwards
"""

import os
from typing import Optional, List
from pathlib import Path

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
    master_password: Optional[str] = Field(default=None, env="TAU_MASTER_PASSWORD")
    secret_key: str = Field(default="tau-translator-secret-key", env="TAU_SECRET_KEY")
    session_expire_hours: int = Field(default=24, env="TAU_SESSION_EXPIRE_HOURS")
    
    # Translation engines (optimized for parser-first approach)
    enable_lmql: bool = Field(default=False, env="TAU_ENABLE_LMQL")  # Disabled by default for stability
    enable_gemma3: bool = Field(default=False, env="TAU_ENABLE_GEMMA3")
    enable_nlp: bool = Field(default=False, env="TAU_ENABLE_NLP")  # Disabled by default for stability  
    enable_grammar: bool = Field(default=True, env="TAU_ENABLE_GRAMMAR")  # Parser-first approach
    
    # File paths
    project_root: Path = Field(default_factory=lambda: Path(__file__).parent.parent.parent.parent)
    grammar_dir: Optional[Path] = Field(default=None, env="TAU_GRAMMAR_DIR")
    dictionaries_dir: Optional[Path] = Field(default=None, env="TAU_DICTIONARIES_DIR")
    sessions_dir: Optional[Path] = Field(default=None, env="TAU_SESSIONS_DIR")
    
    # API providers
    openrouter_api_key: Optional[str] = Field(default=None, env="OPENROUTER_API_KEY")
    huggingface_api_key: Optional[str] = Field(default=None, env="HUGGINGFACE_API_KEY")
    
    # CORS settings
    cors_origins: List[str] = Field(default=["*"], env="TAU_CORS_ORIGINS")
    cors_methods: List[str] = Field(default=["GET", "POST", "OPTIONS"], env="TAU_CORS_METHODS")
    cors_headers: List[str] = Field(default=["*"], env="TAU_CORS_HEADERS")
    
    # Logging
    log_level: str = Field(default="INFO", env="TAU_LOG_LEVEL")
    log_format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    @validator("grammar_dir", pre=True, always=True)
    def set_grammar_dir(cls, v, values):
        if v is None:
            return values["project_root"] / "grammars"
        return Path(v)
    
    @validator("dictionaries_dir", pre=True, always=True)
    def set_dictionaries_dir(cls, v, values):
        if v is None:
            return values["project_root"] / "example_dictionaries"
        return Path(v)
    
    @validator("sessions_dir", pre=True, always=True)
    def set_sessions_dir(cls, v, values):
        if v is None:
            return values["project_root"] / "sessions"
        return Path(v)
    
    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("cors_methods", pre=True)
    def parse_cors_methods(cls, v):
        if isinstance(v, str):
            return [method.strip() for method in v.split(",")]
        return v
    
    @validator("cors_headers", pre=True)
    def parse_cors_headers(cls, v):
        if isinstance(v, str):
            return [header.strip() for header in v.split(",")]
        return v
    
    def ensure_directories(self):
        """Create necessary directories if they don't exist."""
        for dir_path in [self.grammar_dir, self.dictionaries_dir, self.sessions_dir]:
            if dir_path and not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
if PYDANTIC_AVAILABLE:
    try:
        settings = BackendSettings()
    except:
        # Fallback to simple settings if pydantic fails
        from .simple_config import settings
else:
    # Use simple settings if pydantic not available
    from .simple_config import settings