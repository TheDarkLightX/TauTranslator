"""
FSA Pattern Integration Module

Integrates the FSA engine with the pattern loading system for high-performance
pattern matching in the translation pipeline.

Author: DarkLightX / Dana Edwards
"""

import logging
import threading
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import asyncio

from ..pattern_loader import (
    PatternLoader,
    PatternRule,
    PatternType,
    PatternDirection,
    get_pattern_loader
)
from .fsa_engine import (
    OptimizedPatternMatcher,
    FSAPatternCompiler,
    get_pattern_matcher
)
from . import MatchResult


@dataclass
class FSAPatternAdapter:
    """Adapts PatternRule to FSA pattern format."""
    
    @staticmethod
    def convert_to_fsa_pattern(pattern_rule: PatternRule) -> Tuple[str, str, str, int]:
        """
        Convert PatternRule to FSA pattern tuple.
        
        Returns:
            Tuple of (pattern_id, source_pattern, replacement, priority)
        """
        # For now, we only handle literal and simple regex patterns
        if pattern_rule.pattern_type == PatternType.LITERAL:
            return (
                pattern_rule.id,
                pattern_rule.source_pattern,
                pattern_rule.target_pattern,
                pattern_rule.priority
            )
        elif pattern_rule.pattern_type == PatternType.REGEX:
            # FSA currently supports only literal patterns
            # In future, we could expand FSA to handle regex
            logging.warning(f"Regex pattern {pattern_rule.id} will be treated as literal")
            return (
                pattern_rule.id,
                pattern_rule.source_pattern,
                pattern_rule.target_pattern,
                pattern_rule.priority
            )
        else:
            # Template and function patterns not supported in FSA
            raise ValueError(f"Pattern type {pattern_rule.pattern_type} not supported in FSA")
    
    @staticmethod
    def can_use_fsa(pattern_rule: PatternRule) -> bool:
        """Check if pattern can be compiled to FSA."""
        # Currently support literal patterns and simple regex
        if pattern_rule.pattern_type == PatternType.LITERAL:
            return True
        elif pattern_rule.pattern_type == PatternType.REGEX:
            # Check if it's a simple regex that can be converted
            # For now, only support patterns without regex special chars
            special_chars = set('*+?{}()[]|\\^$.')
            return not any(char in pattern_rule.source_pattern for char in special_chars)
        return False


class FSAEnabledPatternManager:
    """
    Pattern manager that uses FSA for applicable patterns and falls back
    to traditional methods for complex patterns.
    """
    
    def __init__(self, pattern_loader: Optional[PatternLoader] = None):
        self.pattern_loader = pattern_loader or get_pattern_loader()
        self.fsa_matcher = get_pattern_matcher()
        self.adapter = FSAPatternAdapter()
        self.fsa_patterns: Dict[str, PatternRule] = {}
        self.regex_patterns: Dict[str, PatternRule] = {}
        self.logger = logging.getLogger(__name__)
        
        # Performance metrics
        self.fsa_matches = 0
        self.regex_matches = 0
    
    def sync_patterns(self, direction: Optional[PatternDirection] = None) -> None:
        """Synchronize patterns from PatternLoader to FSA."""
        # Clear existing patterns
        self.fsa_matcher.clear_patterns()
        self.fsa_patterns.clear()
        self.regex_patterns.clear()
        
        # Get all enabled patterns for the given direction, or all patterns if no direction
        if direction:
            patterns = self.pattern_loader.get_patterns_by_direction(direction)
        else:
            patterns = self.pattern_loader.get_all_patterns()
        
        fsa_patterns = []
        for pattern in patterns:
            if self.adapter.can_use_fsa(pattern):
                try:
                    fsa_pattern = self.adapter.convert_to_fsa_pattern(pattern)
                    fsa_patterns.append(fsa_pattern)
                    self.fsa_patterns[pattern.id] = pattern
                except ValueError:
                    self.regex_patterns[pattern.id] = pattern
            else:
                self.regex_patterns[pattern.id] = pattern
        
        # Load FSA patterns
        if fsa_patterns:
            self.fsa_matcher.add_patterns(fsa_patterns)
            self.logger.info(f"Loaded {len(fsa_patterns)} patterns into FSA engine")
        
        self.logger.info(f"Pattern distribution: {len(self.fsa_patterns)} FSA, {len(self.regex_patterns)} regex")
    
    def match(self, text: str) -> Optional[MatchResult]:
        """Find first match using FSA and regex patterns."""
        # Try FSA first (faster)
        fsa_match = self.fsa_matcher.match(text)
        if fsa_match:
            self.fsa_matches += 1
            return fsa_match
        
        # Fall back to regex patterns
        for pattern in self.regex_patterns.values():
            if pattern.matches(text):
                self.regex_matches += 1
                # Convert to MatchResult
                # NOTE: Simplified match result creation. Lacks precise start/end positions.
                return MatchResult(
                    pattern_id=pattern.id,
                    start_pos=0, # Placeholder
                    end_pos=len(text), # Placeholder
                    matched_text=text,  # This is simplified
                    replacement=pattern.target_pattern,
                    priority=pattern.priority
                )
        
        return None
    
    def find_all_matches(self, text: str) -> List[MatchResult]:
        """Find all matches using both FSA and regex patterns."""
        matches = []
        
        # Get FSA matches
        fsa_matches = self.fsa_matcher.find_all_matches(text)
        matches.extend(fsa_matches)
        self.fsa_matches += len(fsa_matches)
        
        # Get regex matches
        # Note: This is simplified and doesn't handle overlapping matches properly
        for pattern in self.regex_patterns.values():
            if pattern.matches(text):
                self.regex_matches += 1
                # NOTE: Simplified match result creation. Lacks precise start/end positions.
                matches.append(MatchResult(
                    pattern_id=pattern.id,
                    start_pos=0, # Placeholder
                    end_pos=len(text), # Placeholder
                    matched_text=text,
                    replacement=pattern.target_pattern,
                    priority=pattern.priority
                ))
        
        # Sort by priority
        matches.sort(key=lambda m: m.priority, reverse=True)
        return matches
    
    def replace(self, text: str, max_replacements: Optional[int] = None) -> Tuple[str, int]:
        """Replace patterns in text using FSA and regex."""
        # For now, use FSA replacements only
        # In production, we'd need to coordinate between FSA and regex replacements
        return self.fsa_matcher.replace(text, max_replacements)
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get combined performance metrics."""
        fsa_metrics = self.fsa_matcher.get_performance_metrics()
        
        total_matches = self.fsa_matches + self.regex_matches
        fsa_percentage = (self.fsa_matches / total_matches * 100) if total_matches > 0 else 0
        
        return {
            'fsa_metrics': fsa_metrics,
            'total_matches': total_matches,
            'fsa_matches': self.fsa_matches,
            'regex_matches': self.regex_matches,
            'fsa_percentage': fsa_percentage,
            'pattern_distribution': {
                'fsa': len(self.fsa_patterns),
                'regex': len(self.regex_patterns)
            }
        }
    
    async def reload_patterns_async(self) -> None:
        """Reload patterns from all sources and resync."""
        self.logger.info("Reloading all pattern sources...")
        # This requires knowledge of the sources, which PatternLoader abstracts away.
        # We assume a method on the repository to get all known source paths.
        # This is a conceptual implementation.
        if hasattr(self.pattern_loader._pattern_repo, 'get_known_sources'):
            source_paths = self.pattern_loader._pattern_repo.get_known_sources()
            for path in source_paths:
                await self.pattern_loader.load_patterns_from_source_async(path)
            await asyncio.to_thread(self.sync_patterns)
            self.logger.info(f"Resynced patterns after reloading {len(source_paths)} sources.")
        else:
            self.logger.warning("Pattern repository does not support getting known sources for reload.")


# Global FSA-enabled pattern manager
_global_fsa_pattern_manager: Optional[FSAEnabledPatternManager] = None
_global_fsa_lock = threading.Lock()


def get_fsa_pattern_manager() -> FSAEnabledPatternManager:
    """Get the global FSA-enabled pattern manager."""
    global _global_fsa_pattern_manager
    if _global_fsa_pattern_manager is None:
        with _global_fsa_lock:
            if _global_fsa_pattern_manager is None:
                _global_fsa_pattern_manager = FSAEnabledPatternManager()
    return _global_fsa_pattern_manager