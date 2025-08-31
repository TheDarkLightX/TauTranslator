"""
Configuration-Driven Pattern Loading System

Implements dynamic pattern loading with validation, compilation, and hot-reloading.
Follows Open/Closed Principle by making pattern addition configurable.

Author: DarkLightX / Dana Edwards
"""

import json
import yaml
import re
import logging
import threading
import time
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
from abc import ABC, abstractmethod
import hashlib


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
    id: str
    name: str
    pattern_type: PatternType
    direction: PatternDirection
    source_pattern: str
    target_pattern: str
    priority: int = 0
    enabled: bool = True
    description: Optional[str] = None
    examples: List[Tuple[str, str]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Compiled pattern for performance
    _compiled_pattern: Optional[Any] = field(default=None, init=False, repr=False)
    
    def compile_pattern(self) -> bool:
        """Compile the pattern for efficient matching."""
        try:
            if self.pattern_type == PatternType.REGEX:
                flags = re.IGNORECASE
                if self.metadata.get('case_sensitive', False):
                    flags = 0
                self._compiled_pattern = re.compile(self.source_pattern, flags)
            elif self.pattern_type == PatternType.LITERAL:
                # For literal patterns, store as-is for simple string replacement
                self._compiled_pattern = self.source_pattern
            elif self.pattern_type == PatternType.TEMPLATE:
                # Template patterns use string.Template format
                from string import Template
                self._compiled_pattern = Template(self.target_pattern)
            return True
        except Exception as e:
            logging.error(f"Failed to compile pattern {self.id}: {e}")
            return False
    
    def apply(self, text: str) -> Optional[str]:
        """Apply this pattern to text."""
        if not self.enabled or not self._compiled_pattern:
            return None
        
        try:
            if self.pattern_type == PatternType.REGEX:
                return self._compiled_pattern.sub(self.target_pattern, text)
            elif self.pattern_type == PatternType.LITERAL:
                return text.replace(self._compiled_pattern, self.target_pattern)
            elif self.pattern_type == PatternType.TEMPLATE:
                # Extract variables for template substitution
                # This would need more sophisticated implementation
                return self._compiled_pattern.safe_substitute()
            else:
                return None
        except Exception as e:
            logging.error(f"Error applying pattern {self.id}: {e}")
            return None
    
    def matches(self, text: str) -> bool:
        """Check if pattern matches the text."""
        if not self.enabled or not self._compiled_pattern:
            return False
        
        try:
            if self.pattern_type == PatternType.REGEX:
                return bool(self._compiled_pattern.search(text))
            elif self.pattern_type == PatternType.LITERAL:
                return self._compiled_pattern in text
            else:
                return False
        except Exception:
            return False
    
    def validate(self) -> List[str]:
        """Validate pattern rule and return any errors."""
        errors = []
        
        if not self.id:
            errors.append("Pattern ID is required")
        
        if not self.source_pattern:
            errors.append("Source pattern is required")
        
        if not self.target_pattern:
            errors.append("Target pattern is required")
        
        # Validate regex patterns
        if self.pattern_type == PatternType.REGEX:
            try:
                re.compile(self.source_pattern)
            except re.error as e:
                errors.append(f"Invalid regex pattern: {e}")
        
        # Validate examples if provided
        for i, (source, expected) in enumerate(self.examples):
            if not self.compile_pattern():
                continue
            
            result = self.apply(source)
            if result != expected:
                errors.append(f"Example {i+1} failed: expected '{expected}', got '{result}'")
        
        return errors


@dataclass
class PatternSet:
    """Collection of related patterns."""
    name: str
    version: str
    description: str
    patterns: List[PatternRule] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_pattern(self, pattern: PatternRule) -> None:
        """Add pattern to set."""
        self.patterns.append(pattern)
    
    def get_patterns(self, direction: Optional[PatternDirection] = None, enabled_only: bool = True) -> List[PatternRule]:
        """Get patterns filtered by direction and enabled status."""
        filtered = self.patterns
        
        if direction:
            filtered = [
                p for p in filtered 
                if p.direction == direction or p.direction == PatternDirection.BIDIRECTIONAL
            ]
        
        if enabled_only:
            filtered = [p for p in filtered if p.enabled]
        
        # Sort by priority (higher priority first)
        return sorted(filtered, key=lambda p: p.priority, reverse=True)
    
    def validate(self) -> List[str]:
        """Validate entire pattern set."""
        errors = []
        
        # Check for duplicate IDs
        pattern_ids = [p.id for p in self.patterns]
        duplicates = [pid for pid in set(pattern_ids) if pattern_ids.count(pid) > 1]
        if duplicates:
            errors.append(f"Duplicate pattern IDs: {duplicates}")
        
        # Validate individual patterns
        for pattern in self.patterns:
            pattern_errors = pattern.validate()
            if pattern_errors:
                errors.extend([f"Pattern {pattern.id}: {error}" for error in pattern_errors])
        
        return errors


class IPatternLoader(ABC):
    """Interface for pattern loaders."""
    
    @abstractmethod
    def load(self, source: Union[str, Path, Dict]) -> PatternSet:
        """Load patterns from source."""
        pass
    
    @abstractmethod
    def can_load(self, source: Union[str, Path, Dict]) -> bool:
        """Check if loader can handle this source."""
        pass


class JSONPatternLoader(IPatternLoader):
    """Loads patterns from JSON files."""
    
    def can_load(self, source: Union[str, Path, Dict]) -> bool:
        """Check if source is JSON."""
        if isinstance(source, dict):
            return True
        if isinstance(source, (str, Path)):
            path = Path(source)
            return path.suffix.lower() == '.json'
        return False
    
    def load(self, source: Union[str, Path, Dict]) -> PatternSet:
        """Load patterns from JSON."""
        if isinstance(source, dict):
            data = source
        else:
            with open(source, 'r', encoding='utf-8') as f:
                data = json.load(f)
        
        return self._parse_pattern_data(data)
    
    def _parse_pattern_data(self, data: Dict) -> PatternSet:
        """Parse pattern data into PatternSet."""
        pattern_set = PatternSet(
            name=data.get('name', 'Unknown'),
            version=data.get('version', '1.0.0'),
            description=data.get('description', ''),
            metadata=data.get('metadata', {})
        )
        
        for pattern_data in data.get('patterns', []):
            pattern = PatternRule(
                id=pattern_data['id'],
                name=pattern_data.get('name', pattern_data['id']),
                pattern_type=PatternType(pattern_data.get('type', 'regex')),
                direction=PatternDirection(pattern_data.get('direction', 'tce_to_tau')),
                source_pattern=pattern_data['source'],
                target_pattern=pattern_data['target'],
                priority=pattern_data.get('priority', 0),
                enabled=pattern_data.get('enabled', True),
                description=pattern_data.get('description'),
                examples=pattern_data.get('examples', []),
                metadata=pattern_data.get('metadata', {})
            )
            
            if pattern.compile_pattern():
                pattern_set.add_pattern(pattern)
        
        return pattern_set


class YAMLPatternLoader(IPatternLoader):
    """Loads patterns from YAML files."""
    
    def can_load(self, source: Union[str, Path, Dict]) -> bool:
        """Check if source is YAML."""
        if isinstance(source, (str, Path)):
            path = Path(source)
            return path.suffix.lower() in ['.yaml', '.yml']
        return False
    
    def load(self, source: Union[str, Path, Dict]) -> PatternSet:
        """Load patterns from YAML."""
        with open(source, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        # Reuse JSON parser for data processing
        json_loader = JSONPatternLoader()
        return json_loader._parse_pattern_data(data)


class PatternManager:
    """
    Manages pattern sets with hot-reloading and validation.
    
    Features:
    - Multiple pattern loaders
    - Hot-reloading of pattern files
    - Pattern validation and compilation
    - Performance metrics
    - Thread-safe operations
    """
    
    def __init__(self):
        self.pattern_sets: Dict[str, PatternSet] = {}
        self.loaders: List[IPatternLoader] = []
        self.file_watchers: Dict[Path, float] = {}  # file -> last_modified
        self.metrics: Dict[str, Any] = {
            'total_patterns': 0,
            'active_patterns': 0,
            'load_count': 0,
            'reload_count': 0,
            'validation_errors': 0
        }
        self._lock = threading.RLock()
        self.logger = logging.getLogger(__name__)
        
        # Register default loaders
        self.register_loader(JSONPatternLoader())
        self.register_loader(YAMLPatternLoader())
    
    def register_loader(self, loader: IPatternLoader) -> None:
        """Register a pattern loader."""
        self.loaders.append(loader)
        self.logger.debug(f"Registered pattern loader: {type(loader).__name__}")
    
    def load_pattern_set(self, source: Union[str, Path, Dict], name: Optional[str] = None) -> bool:
        """Load a pattern set from source."""
        with self._lock:
            try:
                # Find appropriate loader
                loader = self._find_loader(source)
                if not loader:
                    self.logger.error(f"No loader found for source: {source}")
                    return False
                
                # Load pattern set
                pattern_set = loader.load(source)
                
                # Validate pattern set
                errors = pattern_set.validate()
                if errors:
                    self.logger.error(f"Pattern validation errors: {errors}")
                    self.metrics['validation_errors'] += len(errors)
                    return False
                
                # Store pattern set
                set_name = name or pattern_set.name
                self.pattern_sets[set_name] = pattern_set
                
                # Set up file watching if source is a file
                if isinstance(source, (str, Path)):
                    file_path = Path(source)
                    if file_path.exists():
                        self.file_watchers[file_path] = file_path.stat().st_mtime
                
                # Update metrics
                self.metrics['load_count'] += 1
                self._update_pattern_metrics()
                
                self.logger.info(f"Loaded pattern set '{set_name}' with {len(pattern_set.patterns)} patterns")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to load pattern set: {e}")
                return False
    
    def reload_pattern_sets(self) -> int:
        """Reload all watched pattern files if they've changed."""
        reloaded_count = 0
        
        with self._lock:
            for file_path, last_modified in list(self.file_watchers.items()):
                try:
                    if not file_path.exists():
                        # File was deleted
                        del self.file_watchers[file_path]
                        continue
                    
                    current_modified = file_path.stat().st_mtime
                    if current_modified > last_modified:
                        # File was modified
                        if self.load_pattern_set(file_path):
                            self.file_watchers[file_path] = current_modified
                            reloaded_count += 1
                            self.metrics['reload_count'] += 1
                
                except Exception as e:
                    self.logger.error(f"Error checking file {file_path}: {e}")
        
        if reloaded_count > 0:
            self.logger.info(f"Reloaded {reloaded_count} pattern sets")
        
        return reloaded_count
    
    def get_patterns(
        self, 
        direction: Optional[PatternDirection] = None,
        pattern_set: Optional[str] = None,
        enabled_only: bool = True
    ) -> List[PatternRule]:
        """Get patterns filtered by criteria."""
        with self._lock:
            all_patterns = []
            
            # Determine which pattern sets to use
            if pattern_set:
                if pattern_set in self.pattern_sets:
                    sets_to_search = [self.pattern_sets[pattern_set]]
                else:
                    return []
            else:
                sets_to_search = self.pattern_sets.values()
            
            # Collect patterns from selected sets
            for pset in sets_to_search:
                patterns = pset.get_patterns(direction, enabled_only)
                all_patterns.extend(patterns)
            
            # Sort by priority (higher first)
            return sorted(all_patterns, key=lambda p: p.priority, reverse=True)
    
    def apply_patterns(self, text: str, direction: PatternDirection, max_patterns: Optional[int] = None) -> str:
        """Apply patterns to text in priority order."""
        patterns = self.get_patterns(direction, enabled_only=True)
        
        if max_patterns:
            patterns = patterns[:max_patterns]
        
        result = text
        applied_count = 0
        
        for pattern in patterns:
            if pattern.matches(result):
                new_result = pattern.apply(result)
                if new_result and new_result != result:
                    result = new_result
                    applied_count += 1
                    self.logger.debug(f"Applied pattern {pattern.id}: {pattern.name}")
        
        self.logger.debug(f"Applied {applied_count} patterns to transform text")
        return result
    
    def validate_all_patterns(self) -> Dict[str, List[str]]:
        """Validate all pattern sets and return errors."""
        errors = {}
        
        with self._lock:
            for set_name, pattern_set in self.pattern_sets.items():
                set_errors = pattern_set.validate()
                if set_errors:
                    errors[set_name] = set_errors
        
        return errors
    
    def get_pattern_by_id(self, pattern_id: str) -> Optional[PatternRule]:
        """Get pattern by ID."""
        with self._lock:
            for pattern_set in self.pattern_sets.values():
                for pattern in pattern_set.patterns:
                    if pattern.id == pattern_id:
                        return pattern
        return None
    
    def enable_pattern(self, pattern_id: str, enabled: bool = True) -> bool:
        """Enable or disable a pattern."""
        pattern = self.get_pattern_by_id(pattern_id)
        if pattern:
            pattern.enabled = enabled
            self._update_pattern_metrics()
            return True
        return False
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get pattern manager metrics."""
        with self._lock:
            return self.metrics.copy()
    
    def get_pattern_sets_info(self) -> Dict[str, Any]:
        """Get information about loaded pattern sets."""
        with self._lock:
            return {
                name: {
                    'version': pset.version,
                    'description': pset.description,
                    'pattern_count': len(pset.patterns),
                    'enabled_patterns': len([p for p in pset.patterns if p.enabled]),
                    'metadata': pset.metadata
                }
                for name, pset in self.pattern_sets.items()
            }
    
    def export_patterns(self, pattern_set_name: str, format: str = 'json') -> Optional[str]:
        """Export pattern set to string format."""
        if pattern_set_name not in self.pattern_sets:
            return None
        
        pattern_set = self.pattern_sets[pattern_set_name]
        
        data = {
            'name': pattern_set.name,
            'version': pattern_set.version,
            'description': pattern_set.description,
            'metadata': pattern_set.metadata,
            'patterns': [
                {
                    'id': p.id,
                    'name': p.name,
                    'type': p.pattern_type.value,
                    'direction': p.direction.value,
                    'source': p.source_pattern,
                    'target': p.target_pattern,
                    'priority': p.priority,
                    'enabled': p.enabled,
                    'description': p.description,
                    'examples': p.examples,
                    'metadata': p.metadata
                }
                for p in pattern_set.patterns
            ]
        }
        
        if format.lower() == 'json':
            return json.dumps(data, indent=2)
        elif format.lower() in ['yaml', 'yml']:
            return yaml.dump(data, default_flow_style=False)
        else:
            return None
    
    def _find_loader(self, source: Union[str, Path, Dict]) -> Optional[IPatternLoader]:
        """Find appropriate loader for source."""
        for loader in self.loaders:
            if loader.can_load(source):
                return loader
        return None
    
    def _update_pattern_metrics(self) -> None:
        """Update pattern metrics."""
        total_patterns = 0
        active_patterns = 0
        
        for pattern_set in self.pattern_sets.values():
            total_patterns += len(pattern_set.patterns)
            active_patterns += len([p for p in pattern_set.patterns if p.enabled])
        
        self.metrics['total_patterns'] = total_patterns
        self.metrics['active_patterns'] = active_patterns


# Global pattern manager instance
_global_pattern_manager = PatternManager()


def get_pattern_manager() -> PatternManager:
    """Get the global pattern manager."""
    return _global_pattern_manager