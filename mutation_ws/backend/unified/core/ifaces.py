"""
Interfaces for core application components.

Defines the contracts for services like caching and event handling.

Author: DarkLightX / Dana Edwards
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Callable

from returns.result import Result

from .domain_types import AppError, TranslationEvent


class ICacheRepository(ABC):
    """Interface for a cache repository."""

    @abstractmethod
    async def get_cached_value_async(self, key: str) -> Result[Optional[Any], AppError]:
        pass

    @abstractmethod
    async def set_cached_value_async(self, key: str, value: Any, ttl_seconds: int) -> Result[None, AppError]:
        pass


class IEventBus(ABC):
    """Interface for an event bus."""

    @abstractmethod
    def publish(self, event: TranslationEvent) -> Result[None, AppError]:
        pass

    @abstractmethod
    def subscribe(self, event_type: str, handler: Callable) -> Result[None, AppError]:
        pass
