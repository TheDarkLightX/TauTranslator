# Configuration System: The Castle's Blueprint

## Overview: The Master Architect's Plans

The Configuration system is like the master architect's blueprints for the castle. It defines how every room should be built, where the secret passages go, and what materials to use. Using Pydantic's powerful validation, it ensures that the castle is always built according to specification, catching any construction errors before they become problems.

**File**: `backend/unified/core/config.py`  
**Purpose**: Type-safe configuration management with validation and environment support  
**Architecture**: Pydantic-based settings with hierarchical configuration

---

## The Blueprint Collection (Configuration Classes)

### The Foundation: BaseSettings

```python
class Settings(BaseSettings):
    """
    Application settings with validation and environment variable support.
    Follows Rule 3: Maximum disclosure through type system.
    """
    
    # Application
    app_name: str = "TauTranslator"
    version: str = "2.0.0"
    debug: bool = False
    environment: str = Field(
        default="development",
        regex="^(development|staging|production)$"
    )
```

This is like the foundation specifications:
- **app_name**: What we're building (the castle's name)
- **version**: Which architectural revision
- **debug**: Whether to show construction scaffolding
- **environment**: Building for practice, testing, or real use

The `Field` with regex ensures environment is exactly one of three values - like specifying that doors must be oak, pine, or steel, nothing else.

### The Server Wing

```python
    # Server
    host: str = "0.0.0.0"
    port: int = Field(default=8000, ge=1, le=65535)
    workers: int = Field(default=4, ge=1)
    reload: bool = False
```

Server configuration with smart constraints:
```python
port: int = Field(default=8000, ge=1, le=65535)
```
This ensures the port is between 1 and 65535 - like specifying that castle gates must be between human-height and siege-engine-height, not microscopic or skyscraper-tall.

### The Security Vault

```python
    # Security
    secret_key: str = Field(
        default=..., 
        env="SECRET_KEY",
        min_length=32
    )
    api_key_header: str = "X-API-Key"
    session_header: str = "X-Session-Token"
    cors_origins: List[str] = ["http://localhost:3000"]
    master_password: Optional[str] = Field(default=None, env="MASTER_PASSWORD")
```

Security settings with special handling:
- **secret_key**: Required (`default=...`), from environment, minimum 32 characters
- **cors_origins**: Which neighboring castles can visit
- **master_password**: Optional, loaded from environment for extra security

### The Translation Workshop

```python
    # Translation
    default_translation_direction: str = "to_tau"
    enable_pattern_translation: bool = True
    enable_llm_translation: bool = True
    translation_timeout: float = Field(default=30.0, gt=0)
    max_translation_length: int = Field(default=10000, gt=0)
```

Translation settings with validation:
```python
translation_timeout: float = Field(default=30.0, gt=0)
```
The `gt=0` ensures timeout is positive - you can't have negative time!

### The Performance Tuning

```python
    # Performance  
    cache_enabled: bool = True
    cache_ttl: int = Field(default=3600, ge=0)  # seconds
    cache_max_size: int = Field(default=1000, ge=1)
    
    @validator('cache_ttl')
    def validate_cache_ttl(cls, v, values):
        """Ensure cache TTL makes sense when cache is enabled."""
        if values.get('cache_enabled') and v == 0:
            raise ValueError("Cache TTL must be > 0 when cache is enabled")
        return v
```

The validator is like a building inspector:
- If cache is enabled, TTL (time-to-live) must be positive
- Can't have a cache that expires instantly!

---

## The Resource Management Plans

### Resource Limits Configuration

```python
class ResourceLimits(BaseModel):
    """Resource limits for translation operations."""
    
    max_cpu_percent: float = Field(default=80.0, ge=0, le=100)
    max_memory_percent: float = Field(default=80.0, ge=0, le=100)
    max_concurrent_translations: int = Field(default=10, ge=1)
    
    @validator('max_cpu_percent', 'max_memory_percent')
    def validate_percentages(cls, v):
        """Ensure percentages are reasonable."""
        if v < 10:
            raise ValueError("Resource limit too low, minimum 10%")
        return v
```

Like setting castle resource quotas:
- Can't use more than 100% (physically impossible)
- Can't set limits below 10% (too restrictive to function)

### Database Specifications

```python
class DatabaseSettings(BaseModel):
    """Database configuration."""
    
    url: str = Field(
        default="sqlite:///./tau_translator.db",
        env="DATABASE_URL"
    )
    echo: bool = False
    pool_size: int = Field(default=5, ge=1)
    max_overflow: int = Field(default=10, ge=0)
    
    @property
    def async_url(self) -> str:
        """Convert sync URL to async URL for async drivers."""
        if self.url.startswith("sqlite"):
            return self.url.replace("sqlite:", "sqlite+aiosqlite:")
        elif self.url.startswith("postgresql"):
            return self.url.replace("postgresql:", "postgresql+asyncpg:")
        return self.url
```

The `async_url` property is clever - it automatically converts database URLs to their async equivalents, like having blueprints that automatically adjust for different construction methods.

---

## Environment Variable Magic

### The Env File Settings

```python
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
        # Custom field behavior
        fields = {
            'secret_key': {
                'env': ['SECRET_KEY', 'APP_SECRET_KEY']
            }
        }
```

This configuration tells Pydantic:
- Look for `.env` file for settings
- Case doesn't matter (SECRET_KEY = secret_key)
- Check multiple environment names for secret_key

### Loading From Environment

```python
# In .env file:
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=postgresql://user:pass@localhost/dbname
REDIS_URL=redis://localhost:6379

# Automatically loaded into Settings
```

---

## The Manager's Configuration

### Translation Manager Config

```python
@dataclass
class ManagerConfig:
    """Configuration for translation manager."""
    
    # Cache settings
    cache_enabled: bool = True
    cache_ttl_seconds: int = 3600
    cache_max_size: int = 1000
    
    # Resource limits
    max_cpu_percent: float = 80.0
    max_memory_percent: float = 80.0
    
    # Behavior settings
    enable_fallback: bool = True
    collect_statistics: bool = True
    
    # Timeouts
    translation_timeout_seconds: float = 30.0
    cache_timeout_seconds: float = 1.0
    
    @classmethod
    def from_settings(cls, settings: Settings) -> 'ManagerConfig':
        """Create from application settings."""
        return cls(
            cache_enabled=settings.cache_enabled,
            cache_ttl_seconds=settings.cache_ttl,
            cache_max_size=settings.cache_max_size,
            max_cpu_percent=settings.resource_limits.max_cpu_percent,
            max_memory_percent=settings.resource_limits.max_memory_percent,
            enable_fallback=settings.enable_translation_fallback,
            collect_statistics=settings.enable_statistics,
            translation_timeout_seconds=settings.translation_timeout
        )
```

The `from_settings` method is like a translator that converts master blueprints into specific construction plans for the translation manager.

---

## Simple Settings for Compatibility

### The Simplified Interface

```python
class SimpleSettings:
    """Simple settings class for backward compatibility."""
    
    def __init__(self):
        # Try to load from environment
        self.host = os.getenv("HOST", "0.0.0.0")
        self.port = int(os.getenv("PORT", "8000"))
        self.debug = os.getenv("DEBUG", "").lower() in ("true", "1", "yes")
        
        # API settings
        self.api_base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
        self.api_timeout = int(os.getenv("API_TIMEOUT", "30"))
        
        # Add project_name for compatibility
        self.project_name = "TauTranslator"
```

This provides a simpler interface for legacy code - like maintaining old castle entrances while building new ones.

---

## Configuration Factory Functions

### Getting Settings

```python
def get_settings() -> Settings:
    """
    Get application settings (singleton pattern).
    Loads from environment and .env file.
    """
    global _settings
    
    if _settings is None:
        _settings = Settings()
        
        # Log configuration (hide sensitive values)
        logger.info(f"Loaded configuration for environment: {_settings.environment}")
        logger.debug(f"Debug mode: {_settings.debug}")
        logger.debug(f"Cache enabled: {_settings.cache_enabled}")
        
    return _settings
```

This implements the singleton pattern - like having one master copy of the blueprints that everyone references.

### Configuration Validation Example

```python
try:
    settings = Settings(
        port=70000,  # Invalid! 
        cache_ttl=-1  # Invalid!
    )
except ValidationError as e:
    print(e.json(indent=2))
    # {
    #   "loc": ["port"],
    #   "msg": "ensure this value is less than or equal to 65535",
    #   "type": "value_error.number.not_le"
    # }
```

Pydantic catches configuration errors early - like a building inspector rejecting plans before construction begins.

---

## Advanced Patterns

### Computed Properties

```python
@property
def redis_enabled(self) -> bool:
    """Check if Redis is configured."""
    return bool(self.redis_url and self.redis_url != "disabled")

@property
def is_production(self) -> bool:
    """Check if running in production."""
    return self.environment == "production"
```

Properties compute derived values - like calculating total castle area from room dimensions.

### Settings Inheritance

```python
class DevelopmentSettings(Settings):
    """Development-specific settings."""
    debug: bool = True
    reload: bool = True
    
class ProductionSettings(Settings):
    """Production-specific settings."""
    debug: bool = False
    workers: int = Field(default=8, ge=1)
```

Different blueprints for different purposes - development castle has more windows (debug=True), production castle has more guards (workers=8).

---

## Summary

The Configuration system provides:

1. **Type Safety**: Every setting has a declared type
2. **Validation**: Constraints ensure sensible values
3. **Environment Support**: Easy deployment configuration
4. **Documentation**: Each field documents its purpose
5. **Flexibility**: Multiple ways to provide values

Key patterns demonstrated:

- **Pydantic Models**: Automatic validation and parsing
- **Field Constraints**: `ge`, `le`, `regex` for boundaries
- **Validators**: Custom business logic validation
- **Environment Loading**: Secure secret management
- **Computed Properties**: Derived configuration values
- **Singleton Pattern**: One source of truth

The result is a configuration system that catches errors early, documents itself, and makes deployment configuration straightforward - essential for a production-ready application.