"""
Event Bus implementation for decoupled communication.
Enables loose coupling between core and infrastructure layers.

Copyright: DarkLightX/Dana Edwards
"""

import asyncio
import logging
from typing import Dict, List, Any, Callable, Set
from collections import defaultdict
import weakref

from ..core.domain_types import Result, Success, Failure
from ..core.interfaces import IEventBus


EventHandler = Callable[[Dict[str, Any]], asyncio.Future]


class InMemoryEventBus(IEventBus):
    """
    In-memory event bus implementation.
    Supports async event handling and weak references to prevent memory leaks.
    """
    
    def __init__(self):
        """Initialize event bus."""
        self.logger = logging.getLogger(__name__)
        self._handlers: Dict[str, Set[weakref.ref]] = defaultdict(set)
        self._lock = asyncio.Lock()
    
    async def publish_event_async(self, event_type: str, data: Dict[str, Any]) -> Result[None]:
        """
        Publish an event to all registered handlers.
        Handlers are called concurrently for performance.
        """
        async with self._lock:
            handlers = list(self._handlers.get(event_type, []))
        
        if not handlers:
            self.logger.debug(f"No handlers for event type: {event_type}")
            return Success(None)
        
        # Call all handlers concurrently
        tasks = []
        dead_refs = []
        
        for handler_ref in handlers:
            handler = handler_ref()
            if handler is None:
                # Handler was garbage collected
                dead_refs.append(handler_ref)
                continue
            
            # Create task for handler
            task = asyncio.create_task(self._call_handler(handler, event_type, data))
            tasks.append(task)
        
        # Clean up dead references
        if dead_refs:
            async with self._lock:
                for ref in dead_refs:
                    self._handlers[event_type].discard(ref)
        
        # Wait for all handlers to complete
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Log any exceptions
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    self.logger.error(
                        f"Handler error for event {event_type}: {result}",
                        exc_info=result
                    )
        
        return Success(None)
    
    async def subscribe_to_events_async(self, event_type: str, handler: EventHandler) -> Result[None]:
        """
        Subscribe a handler to events of a specific type.
        Uses weak references to prevent memory leaks.
        """
        if not callable(handler):
            return Failure("INVALID_HANDLER", "Handler must be callable")
        
        async with self._lock:
            # Create weak reference to handler
            handler_ref = weakref.ref(handler)
            self._handlers[event_type].add(handler_ref)
            
        self.logger.debug(f"Handler subscribed to event type: {event_type}")
        return Success(None)
    
    async def unsubscribe_from_events_async(self, event_type: str, handler: EventHandler) -> Result[None]:
        """Unsubscribe a handler from events."""
        async with self._lock:
            if event_type not in self._handlers:
                return Success(None)
            
            # Find and remove the handler reference
            to_remove = None
            for handler_ref in self._handlers[event_type]:
                if handler_ref() == handler:
                    to_remove = handler_ref
                    break
            
            if to_remove:
                self._handlers[event_type].discard(to_remove)
                
                # Clean up empty event types
                if not self._handlers[event_type]:
                    del self._handlers[event_type]
        
        self.logger.debug(f"Handler unsubscribed from event type: {event_type}")
        return Success(None)
    
    async def _call_handler(self, handler: EventHandler, event_type: str, data: Dict[str, Any]) -> None:
        """Call a single event handler with error handling."""
        try:
            # Check if handler is async
            if asyncio.iscoroutinefunction(handler):
                await handler(data)
            else:
                # Run sync handler in thread pool
                await asyncio.to_thread(handler, data)
                
        except Exception as e:
            self.logger.error(
                f"Error in handler for event {event_type}: {e}",
                exc_info=True
            )
    
    def get_handler_count(self, event_type: str) -> int:
        """Get number of handlers for an event type (for debugging/testing)."""
        return len(self._handlers.get(event_type, []))
    
    async def clear_all_handlers_async(self) -> Result[None]:
        """Clear all event handlers (useful for testing)."""
        async with self._lock:
            self._handlers.clear()
        return Success(None)