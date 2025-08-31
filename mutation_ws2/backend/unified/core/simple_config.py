"""
Simple configuration for testing without pydantic dependencies.

Author: DarkLightX / Dana Edwards
"""

import os
from pathlib import Path


class SimpleSettings:
    """Simple settings without pydantic dependency."""
    
    def __init__(self):
        # Application info
        self.project_name = "TauTranslator"
        self.version = "0.1.0"
        
        # Server configuration
        self.host = os.getenv("TAU_HOST", "0.0.0.0")
        self.port = int(os.getenv("TAU_PORT", "8000"))
        self.debug = os.getenv("TAU_DEBUG", "False").lower() == "true"
        self.reload = os.getenv("TAU_RELOAD", "False").lower() == "true"
        
        # Security settings
        self.master_password = os.getenv("TAU_MASTER_PASSWORD")
        self.secret_key = os.getenv("TAU_SECRET_KEY", "tau-translator-secret-key")
        self.session_expire_hours = int(os.getenv("TAU_SESSION_EXPIRE_HOURS", "24"))
        
        # Translation engines (optimized for parser-first approach)
        self.enable_lmql = os.getenv("TAU_ENABLE_LMQL", "False").lower() == "true"  # Disabled by default for stability
        self.enable_gemma3 = os.getenv("TAU_ENABLE_GEMMA3", "False").lower() == "true"
        self.enable_nlp = os.getenv("TAU_ENABLE_NLP", "False").lower() == "true"  # Disabled by default for stability
        self.enable_grammar = os.getenv("TAU_ENABLE_GRAMMAR", "True").lower() == "true"  # Parser-first approach
        self.enable_parser_pipeline = os.getenv("TAU_ENABLE_PARSER_PIPELINE", "True").lower() == "true"  # Full pipeline
        self.enable_bidirectional = os.getenv("TAU_ENABLE_BIDIRECTIONAL", "True").lower() == "true"  # Bidirectional translation
        
        # File paths
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.grammar_dir = Path(os.getenv("TAU_GRAMMAR_DIR", str(self.project_root / "grammars")))
        self.dictionaries_dir = Path(os.getenv("TAU_DICTIONARIES_DIR", str(self.project_root / "example_dictionaries")))
        self.sessions_dir = Path(os.getenv("TAU_SESSIONS_DIR", str(self.project_root / "sessions")))
        
        # API providers
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.huggingface_api_key = os.getenv("HUGGINGFACE_API_KEY")
        
        # CORS settings
        cors_origins = os.getenv("TAU_CORS_ORIGINS", "*")
        self.cors_origins = [o.strip() for o in cors_origins.split(",")]
        cors_methods = os.getenv("TAU_CORS_METHODS", "GET,POST,OPTIONS")
        self.cors_methods = [m.strip() for m in cors_methods.split(",")]
        cors_headers = os.getenv("TAU_CORS_HEADERS", "*")
        self.cors_headers = [h.strip() for h in cors_headers.split(",")]
        
        # Logging
        self.log_level = os.getenv("TAU_LOG_LEVEL", "INFO")
        self.log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    def ensure_directories(self):
        """Create necessary directories if they don't exist."""
        for dir_path in [self.grammar_dir, self.dictionaries_dir, self.sessions_dir]:
            if dir_path and not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = SimpleSettings()