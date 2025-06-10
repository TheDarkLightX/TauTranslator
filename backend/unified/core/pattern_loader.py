"""
Configuration-Driven Pattern Loading System - Refactored with Clean Architecture

Implements dynamic pattern loading with validation, compilation, and hot-reloading.
Follows Open/Closed Principle and Rule 4 (Isolate Impurity in Infrastructure Layer).

Copyright: DarkLightX/Dana Edwards
"""

import re
import logging
import threading
import time
from typing import Dict, List, Optional, Any, Tuple, Union, Callable, Set
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
from abc import ABC, abstractmethod
import hashlib

from .domain_types import (
    PatternId, FilePath, Result, Success, Failure
)
from .interfaces import IPatternRepository, IEventBus, ICacheRepository


class PatternType(Enum):
    """Types of translation patterns."""
    REGEX = "regex"
    LITERAL = "literal"
    TEMPLATE = "template"
    FUNCTION = "function"


class PatternDirection(Enum):
    """Pattern translation directions."""
    TCE_TO_TAU = "tce_to_tau"
    TAU_TO_TCE = "tau_to_tce"
    BIDIRECTIONAL = "bidirectional"


@dataclass
class PatternRule:
    """Individual pattern translation rule."""
    id: PatternId
    name: str
    pattern_type: PatternType
    direction: PatternDirection
    source_pattern: str
    target_pattern: str
    priority: int = 0
    enabled: bool = True
    description: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    compiled_pattern: Optional[re.Pattern] = field(init=False, default=None)
    
    def __post_init__(self):
        """Compile regex patterns after initialization."""
        if self.pattern_type == PatternType.REGEX:
            try:
                self.compiled_pattern = re.compile(self.source_pattern)
            except re.error as e:
                logging.error(f"Failed to compile pattern {self.id}: {e}")


@dataclass
class PatternSet:
    """Collection of pattern rules."""
    id: str
    name: str
    version: str
    rules: List[PatternRule] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class PatternValidator:
    """Validates pattern rules for correctness."""
    
    def validate_pattern_rule(self, rule: PatternRule) -> Result[None]:
        """Validate a single pattern rule."""
        validations = [
            self._validate_pattern_id(rule.id),
            self._validate_pattern_syntax(rule),
            self._validate_pattern_type(rule),
            self._validate_priority(rule.priority)
        ]
        
        for validation in validations:
            if isinstance(validation, Failure):
                return validation
                
        return Success(None)
    
    def _validate_pattern_id(self, pattern_id: PatternId) -> Result[None]:
        """Validate pattern ID format."""
        if not pattern_id or len(pattern_id) < 3:
            return Failure("INVALID_PATTERN_ID", "Pattern ID must be at least 3 characters")
        return Success(None)
    
    def _validate_pattern_syntax(self, rule: PatternRule) -> Result[None]:
        """Validate pattern syntax based on type."""
        if rule.pattern_type == PatternType.REGEX:
            try:
                re.compile(rule.source_pattern)
            except re.error as e:
                return Failure("INVALID_REGEX", f"Invalid regex pattern: {e}")
                
        return Success(None)
    
    def _validate_pattern_type(self, rule: PatternRule) -> Result[None]:
        """Validate pattern type consistency."""
        if rule.pattern_type == PatternType.LITERAL and re.search(r'[.*+?^${}()|[\]\\]', rule.source_pattern):
            return Failure("INVALID_LITERAL", "Literal patterns should not contain regex characters")
        return Success(None)
    
    def _validate_priority(self, priority: int) -> Result[None]:
        """Validate priority is within acceptable range."""
        if priority < -1000 or priority > 1000:
            return Failure("INVALID_PRIORITY", "Priority must be between -1000 and 1000")
        return Success(None)


class PatternLoader:
    """
    Core pattern loading logic - pure business logic without I/O.
    Follows Rule 4: All I/O operations delegated to repositories.
    """
    
    def __init__(
        self,
        pattern_repository: IPatternRepository,
        cache_repository: ICacheRepository,
        event_bus: IEventBus
    ):
        """Initialize with injected dependencies."""
        self._pattern_repo = pattern_repository
        self._cache = cache_repository
        self._event_bus = event_bus
        self._validator = PatternValidator()
        self._loaded_patterns: Dict[str, PatternSet] = {}
        self._pattern_lock = threading.RLock()
        self.logger = logging.getLogger(__name__)
    
    async def load_patterns_from_source_async(self, source_path: FilePath) -> Result[PatternSet]:
        """
        Load patterns from a source via repository.
        Rule 1: Name explicitly indicates async I/O operation.
        Rule 2: Orchestrator pattern delegating to private methods.
        """
        # Check cache first
        cache_key = self._generate_cache_key(source_path)
        cached_result = await self._cache.get_cached_value_async(cache_key)
        
        if isinstance(cached_result, Success) and cached_result.value:
            return Success(cached_result.value)
        
        # Load from repository
        load_result = await self._pattern_repo.load_patterns_from_source_async(source_path)
        if isinstance(load_result, Failure):
            return load_result
        
        # Parse and validate patterns
        parse_result = self._parse_pattern_data(load_result.value, source_path)
        if isinstance(parse_result, Failure):
            return parse_result
        
        # Validate all rules
        validation_result = self._validate_pattern_set(parse_result.value)
        if isinstance(validation_result, Failure):
            return validation_result
        
        # Cache successful result
        await self._cache.set_cached_value_async(cache_key, parse_result.value, ttl_seconds=3600)
        
        # Store in memory
        self._store_pattern_set(parse_result.value)
        
        # Publish event
        await self._event_bus.publish_event_async(
            "patterns_loaded",
            {"pattern_set_id": parse_result.value.id, "source": source_path}
        )
        
        return Success(parse_result.value)
    
    def get_patterns_by_direction(self, direction: PatternDirection) -> List[PatternRule]:
        """Get all patterns for a specific direction."""
        with self._pattern_lock:
            patterns = []
            for pattern_set in self._loaded_patterns.values():
                for rule in pattern_set.rules:
                    if rule.enabled and (
                        rule.direction == direction or 
                        rule.direction == PatternDirection.BIDIRECTIONAL
                    ):
                        patterns.append(rule)
            
            # Sort by priority (higher priority first)
            return sorted(patterns, key=lambda r: r.priority, reverse=True)
    
    def apply_pattern_rules(
        self,
        text: str,
        direction: PatternDirection,
        max_iterations: int = 10
    ) -> str:
        """Apply pattern rules to transform text."""
        patterns = self.get_patterns_by_direction(direction)
        result = text
        
        for iteration in range(max_iterations):
            changed = False
            for rule in patterns:
                new_result = self._apply_single_rule(result, rule)
                if new_result != result:
                    result = new_result
                    changed = True
            
            if not changed:
                break
        
        return result
    
    async def watch_patterns_for_changes_async(self, source_path: FilePath) -> None:
        """
        Watch for pattern changes and reload when needed.
        Delegates file watching to repository.
        """
        await self._pattern_repo.watch_for_pattern_changes_async(source_path)
        
        # Set up event handler for changes
        async def handle_change(event_data: Dict[str, Any]) -> None:
            if event_data.get("path") == source_path:
                await self.load_patterns_from_source_async(source_path)
        
        await self._event_bus.subscribe_to_events_async("file_changed", handle_change)
    
    # --- Private Implementation Methods ---
    
    def _generate_cache_key(self, source_path: FilePath) -> str:
        """Generate cache key for pattern source."""
        return f"patterns:{hashlib.md5(source_path.encode()).hexdigest()}"
    
    def _parse_pattern_data(self, data: Dict[str, Any], source_path: FilePath) -> Result[PatternSet]:
        """Parse raw pattern data into PatternSet."""
        try:
            pattern_set = PatternSet(
                id=data.get("id", Path(source_path).stem),
                name=data.get("name", "Unknown Pattern Set"),
                version=data.get("version", "1.0.0"),
                metadata=data.get("metadata", {})
            )
            
            rules_data = data.get("rules", [])
            for rule_data in rules_data:
                rule = self._parse_pattern_rule(rule_data)
                if rule:
                    pattern_set.rules.append(rule)
            
            return Success(pattern_set)
            
        except Exception as e:
            return Failure("PARSE_ERROR", f"Failed to parse pattern data: {e}")
    
    def _parse_pattern_rule(self, rule_data: Dict[str, Any]) -> Optional[PatternRule]:
        """Parse a single pattern rule from data."""
        try:
            return PatternRule(
                id=PatternId(rule_data["id"]),
                name=rule_data["name"],
                pattern_type=PatternType(rule_data.get("type", "regex")),
                direction=PatternDirection(rule_data["direction"]),
                source_pattern=rule_data["source"],
                target_pattern=rule_data["target"],
                priority=rule_data.get("priority", 0),
                enabled=rule_data.get("enabled", True),
                description=rule_data.get("description"),
                metadata=rule_data.get("metadata", {})
            )
        except Exception as e:
            self.logger.error(f"Failed to parse rule: {e}")
            return None
    
    def _validate_pattern_set(self, pattern_set: PatternSet) -> Result[None]:
        """Validate all rules in a pattern set."""
        for rule in pattern_set.rules:
            validation_result = self._validator.validate_pattern_rule(rule)
            if isinstance(validation_result, Failure):
                return validation_result
        return Success(None)
    
    def _store_pattern_set(self, pattern_set: PatternSet) -> None:
        """Store pattern set in memory."""
        with self._pattern_lock:
            self._loaded_patterns[pattern_set.id] = pattern_set
    
    def _apply_single_rule(self, text: str, rule: PatternRule) -> str:
        """Apply a single pattern rule to text."""
        if rule.pattern_type == PatternType.REGEX and rule.compiled_pattern:
            return rule.compiled_pattern.sub(rule.target_pattern, text)
        elif rule.pattern_type == PatternType.LITERAL:
            return text.replace(rule.source_pattern, rule.target_pattern)
        else:
            return text