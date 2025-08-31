"""
Configuration-Driven Pattern Loading System - Refactored with 10-line method rule
  
Implements dynamic pattern loading with validation, compilation, and hot-reloading.
All methods follow the 10-line maximum rule for clean code.
 
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
    AppError,
    PatternId,
    FilePath,
    Result,
    Success,
    Failure,
)
from .interfaces import IPatternRepository, IEventBus, ICacheRepository
from .functional_utils import guard, guard_not_none
import asyncio


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
            self._compile_pattern()
    
    def _compile_pattern(self):
        """Compile regex pattern safely."""
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


# Validation Helper Classes
class PatternIdValidator:
    """Validates pattern IDs."""
    
    @staticmethod
    def validate(pattern_id: PatternId) -> Result[None, AppError]:
        """Validate pattern ID format."""
        if not pattern_id or len(pattern_id) < 3:
            return Failure(AppError(error_code="INVALID_PATTERN_ID", message="Pattern ID must be at least 3 characters"))
        return Success(None)


class PatternSyntaxValidator:
    """Validates pattern syntax."""
    
    @staticmethod
    def validate_regex(pattern: str) -> Result[None, AppError]:
        """Validate regex pattern syntax."""
        try:
            re.compile(pattern)
            return Success(None)
        except re.error as e:
            return Failure(AppError(error_code="INVALID_REGEX", message=f"Invalid regex pattern: {e}"))
    
    @staticmethod
    def validate_literal(pattern: str) -> Result[None, AppError]:
        """Validate literal pattern doesn't contain regex chars."""
        if re.search(r'[.*+?^${}()|[\]\\]', pattern):
            return Failure(AppError(error_code="INVALID_LITERAL", message="Literal patterns should not contain regex characters"))
        return Success(None)


class PatternPriorityValidator:
    """Validates pattern priority values."""
    
    @staticmethod
    def validate(priority: int) -> Result[None, AppError]:
        """Validate priority is within acceptable range."""
        if priority < -1000 or priority > 1000:
            return Failure(AppError(error_code="INVALID_PRIORITY", message="Priority must be between -1000 and 1000"))
        return Success(None)


class PatternValidator:
    """Validates pattern rules for correctness."""
    
    def __init__(self):
        """Initialize validators."""
        self._id_validator = PatternIdValidator()
        self._syntax_validator = PatternSyntaxValidator()
        self._priority_validator = PatternPriorityValidator()
    
    def validate_pattern_rule(self, rule: PatternRule) -> Result[None, AppError]:
        """Validate a single pattern rule."""
        return self._run_validations(rule)
    
    def _run_validations(self, rule: PatternRule) -> Result[None, AppError]:
        """Run all validations on rule."""
        validators = [
            lambda: self._id_validator.validate(rule.id),
            lambda: self._validate_pattern_syntax(rule),
            lambda: self._validate_pattern_type(rule),
            lambda: self._priority_validator.validate(rule.priority)
        ]
        return self._execute_validators(validators)
    
    def _execute_validators(self, validators: List[Callable]) -> Result[None, AppError]:
        """Execute validators in sequence."""
        for validator in validators:
            result = validator()
            if isinstance(result, Failure):
                return result
        return Success(None)
    
    def _validate_pattern_syntax(self, rule: PatternRule) -> Result[None, AppError]:
        """Validate pattern syntax based on type."""
        if rule.pattern_type == PatternType.REGEX:
            return self._syntax_validator.validate_regex(rule.source_pattern)
        return Success(None)
    
    def _validate_pattern_type(self, rule: PatternRule) -> Result[None, AppError]:
        """Validate pattern type consistency."""
        if rule.pattern_type == PatternType.LITERAL:
            return self._syntax_validator.validate_literal(rule.source_pattern)
        return Success(None)


# Pattern Loading Helper Classes
class PatternCacheManager:
    """Manages pattern caching."""
    
    def __init__(self, cache_repository: ICacheRepository):
        """Initialize with cache repository."""
        self._cache = cache_repository
    
    @staticmethod
    def generate_cache_key(source_path: FilePath) -> str:
        """Generate cache key for pattern source."""
        return f"patterns:{hashlib.md5(source_path.encode()).hexdigest()}"
    
    async def get_cached_patterns(self, source_path: FilePath) -> Result[Optional[PatternSet], AppError]:
        """Get cached patterns if available."""
        cache_key = self.generate_cache_key(source_path)
        return await self._cache.get_cached_value_async(cache_key)
    
    async def cache_patterns(self, source_path: FilePath, pattern_set: PatternSet) -> None:
        """Cache pattern set."""
        cache_key = self.generate_cache_key(source_path)
        await self._cache.set_cached_value_async(cache_key, pattern_set, ttl_seconds=3600)


class PatternEventPublisher:
    """Publishes pattern-related events."""
    
    def __init__(self, event_bus: IEventBus):
        """Initialize with event bus."""
        self._event_bus = event_bus
    
    async def publish_patterns_loaded(self, pattern_set_id: str, source: FilePath) -> None:
        """Publish patterns loaded event."""
        await self._event_bus.publish_event_async(
            "patterns_loaded",
            {"pattern_set_id": pattern_set_id, "source": source}
        )
    
    async def setup_file_watch_handler(self, source_path: FilePath, reload_callback: Callable) -> None:
        """Set up file change event handler."""
        async def handle_change(event_data: Dict[str, Any]) -> None:
            if event_data.get("path") == source_path:
                await reload_callback(source_path)
        await self._event_bus.subscribe_to_events_async("file_changed", handle_change)


class PatternParser:
    """Parses pattern data structures."""
    
    def __init__(self):
        """Initialize parser."""
        self.logger = logging.getLogger(__name__)
    
    def parse_pattern_set(self, data: Dict[str, Any], source_path: FilePath) -> Result[PatternSet, AppError]:
        """Parse raw pattern data into PatternSet."""
        try:
            pattern_set = self._create_pattern_set(data, source_path)
            return self._populate_rules(pattern_set, data)
        except Exception as e:
            return Failure(AppError(error_code="PARSE_ERROR", message=f"Failed to parse pattern data: {e}"))
    
    def _create_pattern_set(self, data: Dict[str, Any], source_path: FilePath) -> PatternSet:
        """Create pattern set from data."""
        return PatternSet(
            id=data.get("id", Path(source_path).stem),
            name=data.get("name", "Unknown Pattern Set"),
            version=data.get("version", "1.0.0"),
            metadata=data.get("metadata", {})
        )
    
    def _populate_rules(self, pattern_set: PatternSet, data: Dict[str, Any]) -> Result[PatternSet, AppError]:
        """Populate pattern set with rules."""
        rules_data = data.get("rules", [])
        for rule_data in rules_data:
            rule = self._parse_single_rule(rule_data)
            if rule:
                pattern_set.rules.append(rule)
        return Success(pattern_set)
    
    def _parse_single_rule(self, rule_data: Dict[str, Any]) -> Optional[PatternRule]:
        """Parse a single pattern rule from data."""
        try:
            return self._create_rule_from_data(rule_data)
        except Exception as e:
            self.logger.error(f"Failed to parse rule: {e}")
            return None
    
    def _create_rule_from_data(self, rule_data: Dict[str, Any]) -> PatternRule:
        """Create PatternRule from rule data."""
        base_attrs = self._extract_base_attributes(rule_data)
        optional_attrs = self._extract_optional_attributes(rule_data)
        return PatternRule(**base_attrs, **optional_attrs)
    
    def _extract_base_attributes(self, rule_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract required rule attributes."""
        return {
            "id": PatternId(rule_data["id"]),
            "name": rule_data["name"],
            "pattern_type": PatternType(rule_data.get("type", "regex")),
            "direction": PatternDirection(rule_data["direction"]),
            "source_pattern": rule_data["source"],
            "target_pattern": rule_data["target"]
        }
    
    def _extract_optional_attributes(self, rule_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract optional rule attributes."""
        return {
            "priority": rule_data.get("priority", 0),
            "enabled": rule_data.get("enabled", True),
            "description": rule_data.get("description"),
            "metadata": rule_data.get("metadata", {})
        }


class PatternApplicator:
    """Applies pattern rules to text."""
    
    @staticmethod
    def apply_single_rule(text: str, rule: PatternRule) -> str:
        """Apply a single pattern rule to text."""
        if rule.pattern_type == PatternType.REGEX and rule.compiled_pattern:
            return rule.compiled_pattern.sub(rule.target_pattern, text)
        elif rule.pattern_type == PatternType.LITERAL:
            return text.replace(rule.source_pattern, rule.target_pattern)
        else:
            return text
    
    @staticmethod
    def apply_rules_iteratively(
        text: str, patterns: List[PatternRule], max_iterations: int = 10
    ) -> str:
        """Apply pattern rules iteratively until no changes."""
        return PatternApplicator._iterate_until_stable(text, patterns, max_iterations)
    
    @staticmethod
    def _iterate_until_stable(text: str, patterns: List[PatternRule], max_iterations: int) -> str:
        """Iterate pattern application until stable."""
        result = text
        for _ in range(max_iterations):
            new_result = PatternApplicator._apply_one_iteration(result, patterns)
            if not PatternApplicator._has_changed(result, new_result):
                break
            result = new_result
        return result
    
    @staticmethod
    def _has_changed(old_text: str, new_text: str) -> bool:
        """Check if text has changed."""
        return old_text != new_text
    
    @staticmethod
    def _apply_one_iteration(text: str, patterns: List[PatternRule]) -> str:
        """Apply all patterns once."""
        result = text
        for rule in patterns:
            result = PatternApplicator.apply_single_rule(result, rule)
        return result


class PatternFilter:
    """Filters patterns based on criteria."""
    
    @staticmethod
    def filter_by_direction(
        patterns: List[PatternRule], direction: PatternDirection
    ) -> List[PatternRule]:
        """Filter patterns by direction."""
        return [
            rule for rule in patterns
            if rule.enabled and PatternFilter._matches_direction(rule, direction)
        ]
    
    @staticmethod
    def _matches_direction(rule: PatternRule, direction: PatternDirection) -> bool:
        """Check if rule matches direction."""
        return (
            rule.direction == direction or 
            rule.direction == PatternDirection.BIDIRECTIONAL
        )
    
    @staticmethod
    def sort_by_priority(patterns: List[PatternRule]) -> List[PatternRule]:
        """Sort patterns by priority (higher first)."""
        return sorted(patterns, key=lambda r: r.priority, reverse=True)


class PatternLoader:
    """
    Core pattern loading logic - refactored with 10-line method rule.
    All methods are ≤10 lines following clean code principles.
    """

    def __init__(
        self,
        pattern_repository: IPatternRepository,
        cache_repository: Optional[ICacheRepository] = None,
        event_bus: Optional[IEventBus] = None,
        logger: Optional[logging.Logger] = None
    ):
        """Initialize with injected dependencies."""
        self._init_core_components(pattern_repository, cache_repository, event_bus)
        self._init_helpers()
        self._init_state(logger)

    def _init_core_components(self, pattern_repo, cache_repo, event_bus):
        """Initialize core repository components."""
        self._pattern_repo = pattern_repo
        self._cache_manager = PatternCacheManager(cache_repo) if cache_repo else None
        self._event_publisher = PatternEventPublisher(event_bus) if event_bus else None

    def _init_helpers(self):
        """Initialize helper components."""
        self._validator = PatternValidator()
        self._parser = PatternParser()
        self._applicator = PatternApplicator()
        self._filter = PatternFilter()

    def _init_state(self, logger: Optional[logging.Logger]):
        """Initialize internal state."""
        self._loaded_patterns: Dict[str, PatternSet] = {}
        self._pattern_lock = threading.RLock()
        self.logger = logger or logging.getLogger(__name__)

    async def load_patterns_from_source_async(self, source_path: FilePath) -> Result[PatternSet, AppError]:
        """Load patterns from source with caching."""
        cached = await self._try_load_from_cache(source_path)
        if cached.is_success() and cached.value:
            self.logger.debug(f"Loaded patterns from cache for {source_path}")
            return Success(cached.value)
        self.logger.debug(f"Cache miss for {source_path}, loading from repository.")
        return await self._load_and_cache_patterns(source_path)

    async def _try_load_from_cache(self, source_path: FilePath) -> Result[Optional[PatternSet], AppError]:
        """Try to load patterns from cache if available."""
        if not self._cache_manager:
            return Success(None)
        return await self._cache_manager.get_cached_patterns(source_path)

    async def _load_and_cache_patterns(self, source_path: FilePath) -> Result[PatternSet, AppError]:
        """Load patterns from repository and cache them."""
        result = await self._load_from_repository(source_path)
        if result.is_success():
            await self._process_loaded_patterns(source_path, result.value)
        return result

    async def _load_from_repository(self, source_path: FilePath) -> Result[PatternSet, AppError]:
        """Load and parse patterns from repository."""
        load_result = await self._pattern_repo.load_patterns_from_source_async(source_path)
        if load_result.is_failure():
            return load_result
        return await self._parse_and_validate(load_result.value, source_path)

    async def _parse_and_validate(self, data: Dict[str, Any], source_path: FilePath) -> Result[PatternSet, AppError]:
        """Parse data and validate pattern set, offloading CPU-bound work."""
        # Offload parsing to a separate thread
        parse_result = await asyncio.to_thread(self._parser.parse_pattern_set, data, source_path)
        if parse_result.is_failure():
            return parse_result

        pattern_set_object = parse_result.value

        # Offload validation to a separate thread
        # Note: _validate_and_return itself is synchronous and calls _validate_all_rules.
        validation_result = await asyncio.to_thread(self._validate_and_return, pattern_set_object)
        return validation_result

    def _validate_and_return(self, pattern_set: PatternSet) -> Result[PatternSet, AppError]:
        """Validate pattern set and return result. This is a synchronous method."""
        validation = self._validate_all_rules(pattern_set)
        if validation.is_failure():
            return validation
        return Success(pattern_set)

    def _validate_all_rules(self, pattern_set: PatternSet) -> Result[None, AppError]:
        """Validate all rules in pattern set."""
        for rule in pattern_set.rules:
            result = self._validator.validate_pattern_rule(rule)
            if result.is_failure():
                return result
        return Success(None)

    async def _process_loaded_patterns(self, source_path: FilePath, pattern_set: PatternSet) -> None:
        """Process successfully loaded patterns."""
        if self._cache_manager:
            await self._cache_manager.cache_patterns(source_path, pattern_set)
        self._store_in_memory(pattern_set)
        if self._event_publisher:
            await self._event_publisher.publish_patterns_loaded(pattern_set.id, source_path)

    def _store_in_memory(self, pattern_set: PatternSet) -> None:
        """Store pattern set in memory."""
        with self._pattern_lock:
            self._loaded_patterns[pattern_set.id] = pattern_set
            self.logger.info(f"Stored pattern set '{pattern_set.id}' in memory.")

    def get_patterns_by_direction(self, direction: PatternDirection) -> List[PatternRule]:
        """Get all patterns for a specific direction."""
        with self._pattern_lock:
            all_patterns = self._collect_all_patterns()
            filtered = self._filter.filter_by_direction(all_patterns, direction)
            return self._filter.sort_by_priority(filtered)

    def get_all_patterns(self) -> List[PatternRule]:
        """Get all loaded patterns, sorted by priority."""
        with self._pattern_lock:
            all_patterns = self._collect_all_patterns()
            return self._filter.sort_by_priority(all_patterns)

    def get_pattern_set(self, pattern_set_id: str) -> Optional[PatternSet]:
        """Retrieve a loaded pattern set by its ID."""
        with self._pattern_lock:
            return self._loaded_patterns.get(pattern_set_id)

    def _collect_all_patterns(self) -> List[PatternRule]:
        """Collect all patterns from loaded sets."""
        patterns = []
        for pattern_set in self._loaded_patterns.values():
            patterns.extend(pattern_set.rules)
        return patterns

    def apply_pattern_rules(
        self, text: str, direction: PatternDirection, max_iterations: int = 10
    ) -> str:
        """Apply pattern rules to transform text."""
        patterns = self.get_patterns_by_direction(direction)
        return self._applicator.apply_rules_iteratively(text, patterns, max_iterations)

    async def watch_patterns_for_changes_async(self, source_path: FilePath) -> None:
        """Watch for pattern changes and reload when needed."""
        await self._pattern_repo.watch_for_pattern_changes_async(source_path)
        if self._event_publisher:
            await self._event_publisher.setup_file_watch_handler(
                source_path, self.load_patterns_from_source_async
            )


# Singleton instance
_pattern_loader_instance: Optional[PatternLoader] = None
_pattern_loader_lock = threading.Lock()


def get_pattern_loader() -> PatternLoader:
    """Get the singleton PatternLoader instance."""
    global _pattern_loader_instance
    if _pattern_loader_instance is None:
        with _pattern_loader_lock:
            if _pattern_loader_instance is None:
                from ..infrastructure.repositories.file_pattern_repository import FilePatternRepository
                
                # Create with default file repository, no cache or event bus
                pattern_repo = FilePatternRepository()
                _pattern_loader_instance = PatternLoader(pattern_repository=pattern_repo)
    
    return _pattern_loader_instance