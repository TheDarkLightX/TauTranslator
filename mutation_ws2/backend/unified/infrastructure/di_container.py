"""
Dependency Injection Container for Clean Architecture.
Wires together core business logic with infrastructure implementations.

Copyright: DarkLightX/Dana Edwards
"""

from typing import Dict, Any, Optional
from pathlib import Path
import logging

from ..core.interfaces import (
    IPatternRepository, IAuthenticationRepository,
    IGrammarRepository, IResourceMonitor,
    ICacheRepository, IEventBus
)
from ..core.pattern_loader import PatternLoader
from ..core.auth import AuthenticationService

from .repositories.file_pattern_repository import FilePatternRepository
from .repositories.file_auth_repository import FileAuthenticationRepository
from .repositories.memory_cache_repository import MemoryCacheRepository
from .event_bus import InMemoryEventBus


class DIContainer:
    """
    Dependency Injection Container following Rule 4.
    Centralizes the wiring of infrastructure to core business logic.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize container with configuration."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._singletons: Dict[str, Any] = {}
        
        # Initialize infrastructure components
        self._initialize_infrastructure()
    
    def _initialize_infrastructure(self) -> None:
        """Initialize all infrastructure components."""
        # Event Bus (shared across components)
        self._singletons["event_bus"] = InMemoryEventBus()
        
        # Cache Repository
        self._singletons["cache_repository"] = MemoryCacheRepository(
            max_size=self.config.get("cache_max_size", 1000),
            ttl_seconds=self.config.get("cache_ttl", 3600)
        )
        
        # Pattern Repository
        self._singletons["pattern_repository"] = FilePatternRepository(
            event_bus=self.get_event_bus()
        )
        
        # Authentication Repository
        auth_dir = Path(self.config.get("auth_data_dir", "./data/auth"))
        self._singletons["auth_repository"] = FileAuthenticationRepository(
            base_dir=auth_dir
        )
    
    # --- Repository Getters ---
    
    def get_pattern_repository(self) -> IPatternRepository:
        """Get pattern repository instance."""
        return self._singletons["pattern_repository"]
    
    def get_auth_repository(self) -> IAuthenticationRepository:
        """Get authentication repository instance."""
        return self._singletons["auth_repository"]
    
    def get_cache_repository(self) -> ICacheRepository:
        """Get cache repository instance."""
        return self._singletons["cache_repository"]
    
    def get_event_bus(self) -> IEventBus:
        """Get event bus instance."""
        return self._singletons["event_bus"]
    
    # --- Service Factory Methods ---
    
    def create_pattern_loader(self) -> PatternLoader:
        """
        Create PatternLoader with injected dependencies.
        This is where core business logic meets infrastructure.
        """
        return PatternLoader(
            pattern_repository=self.get_pattern_repository(),
            cache_repository=self.get_cache_repository(),
            event_bus=self.get_event_bus()
        )
    
    def create_authentication_service(self) -> "AuthenticationService":
        """Create AuthenticationService with injected dependencies."""
        return AuthenticationService(
            auth_repository=self.get_auth_repository(),
            event_bus=self.get_event_bus(),
            master_password=self.config.get("master_password"),
            session_expire_hours=self.config.get("session_expire_hours", 24)
        )
    
    # --- Configuration Methods ---
    
    def configure_for_testing(self) -> None:
        """Configure container for testing with mock implementations."""
        from .repositories.mock_repositories import (
            MockPatternRepository,
            MockAuthRepository,
            MockCacheRepository
        )
        
        # Replace with mock implementations
        self._singletons["pattern_repository"] = MockPatternRepository()
        self._singletons["auth_repository"] = MockAuthRepository()
        self._singletons["cache_repository"] = MockCacheRepository()
        
        self.logger.info("Container configured for testing with mock repositories")
    
    def configure_for_production(self) -> None:
        """Configure container for production with appropriate implementations."""
        # Could switch to Redis cache, PostgreSQL, etc.
        # For now, using file-based implementations
        pass


# Global container instance
_container: Optional[DIContainer] = None


def initialize_container(config: Dict[str, Any]) -> DIContainer:
    """Initialize the global DI container."""
    global _container
    _container = DIContainer(config)
    return _container


def get_container() -> DIContainer:
    """Get the global DI container."""
    if _container is None:
        raise RuntimeError("DI container not initialized. Call initialize_container first.")
    return _container


def create_pattern_loader() -> PatternLoader:
    """Convenience function to create PatternLoader."""
    return get_container().create_pattern_loader()


def create_auth_service() -> "AuthenticationService":
    """Convenience function to create AuthenticationService."""
    return get_container().create_authentication_service()