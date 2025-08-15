"""
Abstract base class for Large Language Model clients.

Defines the interface that all LLM clients must implement.

Author: DarkLightX / Dana Edwards
"""

from abc import ABC, abstractmethod
from returns.result import Result
from .domain_types import AppError


class LLMClient(ABC):
    """Abstract base class for LLM clients."""

    @abstractmethod
    async def query_async(self, prompt: str, **kwargs) -> Result[str, AppError]:
        """Sends a prompt to the LLM and returns the response asynchronously."""
        pass
