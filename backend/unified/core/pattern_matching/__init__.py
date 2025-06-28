"""
Pattern Matching Package

High-performance pattern matching using Finite State Automata (FSA).
Provides 50-70% faster pattern matching compared to traditional regex approaches.

Uses Aho-Corasick algorithm for optimal O(n + m) complexity on multiple patterns.

Author: DarkLightX / Dana Edwards
"""

from .fsa_engine import (
    # Core FSA components
    FiniteStateAutomaton,
    FSAState,
    FSATransition,
    StateType,
    TransitionType,
    # Pattern compilation
    FSAPatternCompiler,
    # Optimized matcher
    OptimizedPatternMatcher,
    get_pattern_matcher,
)

from .types import MatchResult

# Optimized Aho-Corasick implementation
from .fsa_engine_optimized import (
    AhoCorasickFSA,
    OptimizedFSAPatternCompiler,
    OptimizedPatternMatcher as AhoCorasickPatternMatcher,
)

# Integration with pattern loader
from .fsa_pattern_integration import (
    FSAPatternAdapter,
    FSAEnabledPatternManager,
    get_fsa_pattern_manager,
)

__all__ = [
    # Core FSA
    'FiniteStateAutomaton',
    'FSAState', 
    'FSATransition',
    'StateType',
    'TransitionType',
    'MatchResult',
    'FSAPatternCompiler',
    'OptimizedPatternMatcher',
    'get_pattern_matcher',
    
    # Optimized implementation
    'AhoCorasickFSA',
    'OptimizedFSAPatternCompiler',
    'AhoCorasickPatternMatcher',
    
    # Integration
    'FSAPatternAdapter',
    'FSAEnabledPatternManager',
    'get_fsa_pattern_manager',
]