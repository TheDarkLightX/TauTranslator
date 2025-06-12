"""
Unit tests for Finite State Automaton (FSA) pattern matching engine.

Tests cover:
- Basic FSA operations
- Pattern compilation and matching
- Performance characteristics
- Thread safety
- Edge cases and error handling

Author: DarkLightX / Dana Edwards
"""

import pytest
import threading
import time
from typing import List, Set, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

from backend.unified.core.pattern_matching.fsa_engine import (
    FiniteStateAutomaton,
    FSAState,
    FSATransition,
    TransitionType,
    StateType,
    MatchResult,
    FSAPatternCompiler,
    OptimizedPatternMatcher,
    get_pattern_matcher
)


class TestFSATransition:
    """Test FSA transition functionality."""
    
    def test_character_transition_matches_exact(self):
        """Test that character transitions match exact characters."""
        transition = FSATransition(
            from_state=0,
            to_state=1,
            transition_type=TransitionType.CHARACTER,
            symbol='a'
        )
        
        assert transition.matches('a') is True
        assert transition.matches('b') is False
        assert transition.matches('') is False
        assert transition.matches('aa') is False
    
    def test_any_character_transition_matches_all(self):
        """Test that ANY_CHARACTER transitions match any character."""
        transition = FSATransition(
            from_state=0,
            to_state=1,
            transition_type=TransitionType.ANY_CHARACTER
        )
        
        assert transition.matches('a') is True
        assert transition.matches('z') is True
        assert transition.matches('1') is True
        assert transition.matches(' ') is True
        assert transition.matches('\n') is True
    
    def test_character_class_transition(self):
        """Test character class transitions."""
        transition = FSATransition(
            from_state=0,
            to_state=1,
            transition_type=TransitionType.CHARACTER_CLASS,
            character_class={'a', 'b', 'c'}
        )
        
        assert transition.matches('a') is True
        assert transition.matches('b') is True
        assert transition.matches('c') is True
        assert transition.matches('d') is False
        assert transition.matches('') is False
    
    def test_epsilon_transition_always_matches(self):
        """Test that epsilon transitions always match."""
        transition = FSATransition(
            from_state=0,
            to_state=1,
            transition_type=TransitionType.EPSILON
        )
        
        assert transition.matches('a') is True
        assert transition.matches('') is True
        assert transition.matches('xyz') is True
    
    def test_transition_immutability(self):
        """Test that FSATransition is immutable."""
        transition = FSATransition(
            from_state=0,
            to_state=1,
            transition_type=TransitionType.CHARACTER,
            symbol='a'
        )
        
        with pytest.raises(AttributeError):
            transition.from_state = 2
        
        with pytest.raises(AttributeError):
            transition.symbol = 'b'


class TestFSAState:
    """Test FSA state functionality."""
    
    def test_state_creation(self):
        """Test FSA state creation and initialization."""
        state = FSAState(
            state_id=0,
            state_type=StateType.START
        )
        
        assert state.state_id == 0
        assert state.state_type == StateType.START
        assert len(state.transitions) == 0
        assert state.pattern_id is None
        assert state.replacement is None
        assert state.priority == 0
        assert isinstance(state.metadata, dict)
    
    def test_add_transition(self):
        """Test adding transitions to a state."""
        state = FSAState(0, StateType.INTERMEDIATE)
        
        transition1 = FSATransition(0, 1, TransitionType.CHARACTER, symbol='a')
        transition2 = FSATransition(0, 2, TransitionType.CHARACTER, symbol='b')
        
        state.add_transition(transition1)
        state.add_transition(transition2)
        
        assert len(state.transitions) == 2
        assert transition1 in state.transitions
        assert transition2 in state.transitions
    
    def test_get_transitions_by_character(self):
        """Test getting transitions that match a character."""
        state = FSAState(0, StateType.INTERMEDIATE)
        
        # Add various types of transitions
        char_transition = FSATransition(0, 1, TransitionType.CHARACTER, symbol='a')
        any_transition = FSATransition(0, 2, TransitionType.ANY_CHARACTER)
        class_transition = FSATransition(
            0, 3, TransitionType.CHARACTER_CLASS, 
            character_class={'a', 'b', 'c'}
        )
        epsilon_transition = FSATransition(0, 4, TransitionType.EPSILON)
        
        state.add_transition(char_transition)
        state.add_transition(any_transition)
        state.add_transition(class_transition)
        state.add_transition(epsilon_transition)
        
        # Test matching 'a'
        matching_a = state.get_transitions('a')
        assert len(matching_a) == 4  # All transitions match 'a'
        
        # Test matching 'd'
        state_d = FSAState(5, StateType.INTERMEDIATE)
        state_d.add_transition(char_transition)
        state_d.add_transition(any_transition)
        state_d.add_transition(class_transition)
        state_d.add_transition(epsilon_transition)
        
        matching_d = state_d.get_transitions('d')
        # Only ANY_CHARACTER and EPSILON match 'd'
        assert len(matching_d) == 2


class TestFiniteStateAutomaton:
    """Test core FSA functionality."""
    
    def test_fsa_initialization(self):
        """Test FSA initialization."""
        fsa = FiniteStateAutomaton()
        
        assert len(fsa.states) == 0
        assert fsa.start_state is None
        assert len(fsa.current_states) == 0
        assert fsa.compiled is False
        assert len(fsa.transition_table) == 0
    
    def test_create_state(self):
        """Test state creation in FSA."""
        fsa = FiniteStateAutomaton()
        
        state_id1 = fsa.create_state(StateType.START)
        state_id2 = fsa.create_state(StateType.INTERMEDIATE)
        state_id3 = fsa.create_state(StateType.ACCEPTING)
        
        assert state_id1 == 0
        assert state_id2 == 1
        assert state_id3 == 2
        assert len(fsa.states) == 3
        
        assert fsa.states[state_id1].state_type == StateType.START
        assert fsa.states[state_id2].state_type == StateType.INTERMEDIATE
        assert fsa.states[state_id3].state_type == StateType.ACCEPTING
    
    def test_add_transition(self):
        """Test adding transitions to FSA."""
        fsa = FiniteStateAutomaton()
        
        # Add transition between non-existent states
        transition = FSATransition(0, 1, TransitionType.CHARACTER, symbol='a')
        fsa.add_transition(transition)
        
        # States should be created automatically
        assert 0 in fsa.states
        assert 1 in fsa.states
        assert len(fsa.states[0].transitions) == 1
        assert fsa.compiled is False  # Should mark as needing compilation
    
    def test_set_start_state(self):
        """Test setting the start state."""
        fsa = FiniteStateAutomaton()
        
        # Set start state for non-existent state
        fsa.set_start_state(0)
        assert fsa.start_state == 0
        assert 0 in fsa.states
        assert fsa.states[0].state_type == StateType.START
        
        # Change existing state to start state
        state_id = fsa.create_state(StateType.INTERMEDIATE)
        fsa.set_start_state(state_id)
        assert fsa.start_state == state_id
        assert fsa.states[state_id].state_type == StateType.START
    
    def test_mark_accepting(self):
        """Test marking states as accepting."""
        fsa = FiniteStateAutomaton()
        state_id = fsa.create_state()
        
        fsa.mark_accepting(state_id, "pattern1", "replacement1", priority=10)
        
        state = fsa.states[state_id]
        assert state.state_type == StateType.ACCEPTING
        assert state.pattern_id == "pattern1"
        assert state.replacement == "replacement1"
        assert state.priority == 10
    
    def test_simple_pattern_matching(self):
        """Test matching a simple pattern."""
        fsa = FiniteStateAutomaton()
        
        # Build FSA for pattern "abc"
        s0 = fsa.create_state(StateType.START)
        s1 = fsa.create_state()
        s2 = fsa.create_state()
        s3 = fsa.create_state(StateType.ACCEPTING)
        
        fsa.set_start_state(s0)
        fsa.add_transition(FSATransition(s0, s1, TransitionType.CHARACTER, symbol='a'))
        fsa.add_transition(FSATransition(s1, s2, TransitionType.CHARACTER, symbol='b'))
        fsa.add_transition(FSATransition(s2, s3, TransitionType.CHARACTER, symbol='c'))
        fsa.mark_accepting(s3, "abc_pattern", "MATCHED", priority=1)
        
        # Test matching
        match = fsa.match("abc")
        assert match is not None
        assert match.matched is True
        assert match.pattern_id == "abc_pattern"
        assert match.matched_text == "abc"
        assert match.start_pos == 0
        assert match.end_pos == 3
        
        # Test non-matching
        assert fsa.match("xyz") is None
        assert fsa.match("ab") is None
        assert fsa.match("abcd") is not None  # Should still match "abc"
    
    def test_pattern_matching_with_offset(self):
        """Test pattern matching starting from different positions."""
        fsa = FiniteStateAutomaton()
        
        # Build FSA for pattern "test"
        compiler = FSAPatternCompiler()
        fsa = compiler.compile_patterns([("test_pattern", "test", "TEST", 1)])
        
        text = "This is a test string"
        match = fsa.match(text)
        
        assert match is not None
        assert match.matched_text == "test"
        assert match.start_pos == 10
        assert match.end_pos == 14
    
    def test_find_all_matches(self):
        """Test finding all matches in text."""
        compiler = FSAPatternCompiler()
        fsa = compiler.compile_patterns([
            ("pattern1", "foo", "FOO", 1),
            ("pattern2", "bar", "BAR", 1)
        ])
        
        text = "foo bar foo bar"
        matches = fsa.find_all_matches(text)
        
        assert len(matches) == 4
        assert matches[0].matched_text == "foo"
        assert matches[1].matched_text == "bar"
        assert matches[2].matched_text == "foo"
        assert matches[3].matched_text == "bar"
    
    def test_replace_functionality(self):
        """Test pattern replacement."""
        compiler = FSAPatternCompiler()
        fsa = compiler.compile_patterns([
            ("pattern1", "foo", "FOO", 1),
            ("pattern2", "bar", "BAR", 1)
        ])
        
        text = "foo bar foo bar"
        result, count = fsa.replace(text)
        
        assert result == "FOO BAR FOO BAR"
        assert count == 4
    
    def test_replace_with_limit(self):
        """Test pattern replacement with limit."""
        compiler = FSAPatternCompiler()
        fsa = compiler.compile_patterns([
            ("pattern1", "test", "TEST", 1)
        ])
        
        text = "test test test"
        result, count = fsa.replace(text, max_replacements=2)
        
        assert result == "TEST TEST test"
        assert count == 2
    
    def test_epsilon_transitions(self):
        """Test FSA with epsilon transitions."""
        fsa = FiniteStateAutomaton()
        
        # Build FSA with epsilon transitions
        s0 = fsa.create_state(StateType.START)
        s1 = fsa.create_state()
        s2 = fsa.create_state()
        s3 = fsa.create_state(StateType.ACCEPTING)
        
        fsa.set_start_state(s0)
        
        # Path: s0 --ε--> s1 --a--> s2 --ε--> s3
        fsa.add_transition(FSATransition(s0, s1, TransitionType.EPSILON))
        fsa.add_transition(FSATransition(s1, s2, TransitionType.CHARACTER, symbol='a'))
        fsa.add_transition(FSATransition(s2, s3, TransitionType.EPSILON))
        fsa.mark_accepting(s3, "epsilon_pattern", "MATCHED", priority=1)
        
        # Should match single 'a'
        match = fsa.match("a")
        assert match is not None
        assert match.matched_text == "a"
    
    def test_wildcard_matching(self):
        """Test matching with wildcard (ANY_CHARACTER) transitions."""
        fsa = FiniteStateAutomaton()
        
        # Build FSA for pattern "a.b" where . is any character
        s0 = fsa.create_state(StateType.START)
        s1 = fsa.create_state()
        s2 = fsa.create_state()
        s3 = fsa.create_state(StateType.ACCEPTING)
        
        fsa.set_start_state(s0)
        fsa.add_transition(FSATransition(s0, s1, TransitionType.CHARACTER, symbol='a'))
        fsa.add_transition(FSATransition(s1, s2, TransitionType.ANY_CHARACTER))
        fsa.add_transition(FSATransition(s2, s3, TransitionType.CHARACTER, symbol='b'))
        fsa.mark_accepting(s3, "wildcard_pattern", "MATCHED", priority=1)
        
        # Should match "axb", "a1b", "a b", etc.
        assert fsa.match("axb") is not None
        assert fsa.match("a1b") is not None
        assert fsa.match("a b") is not None
        assert fsa.match("ab") is None  # No character between a and b
        assert fsa.match("axxb") is None  # Two characters between a and b
    
    def test_character_class_matching(self):
        """Test matching with character classes."""
        fsa = FiniteStateAutomaton()
        
        # Build FSA for pattern "[abc]x" 
        s0 = fsa.create_state(StateType.START)
        s1 = fsa.create_state()
        s2 = fsa.create_state(StateType.ACCEPTING)
        
        fsa.set_start_state(s0)
        fsa.add_transition(FSATransition(
            s0, s1, TransitionType.CHARACTER_CLASS,
            character_class={'a', 'b', 'c'}
        ))
        fsa.add_transition(FSATransition(s1, s2, TransitionType.CHARACTER, symbol='x'))
        fsa.mark_accepting(s2, "class_pattern", "MATCHED", priority=1)
        
        # Should match "ax", "bx", "cx"
        assert fsa.match("ax") is not None
        assert fsa.match("bx") is not None
        assert fsa.match("cx") is not None
        assert fsa.match("dx") is None
        assert fsa.match("x") is None


class TestFSAPatternCompiler:
    """Test FSA pattern compilation."""
    
    def test_compile_single_pattern(self):
        """Test compiling a single pattern."""
        compiler = FSAPatternCompiler()
        patterns = [("pattern1", "hello", "HELLO", 1)]
        
        fsa = compiler.compile_patterns(patterns)
        
        assert fsa is not None
        assert fsa.compiled is True
        assert len(fsa.states) == 6  # start + 5 characters
        
        match = fsa.match("hello world")
        assert match is not None
        assert match.matched_text == "hello"
        assert match.replacement == "HELLO"
    
    def test_compile_multiple_patterns(self):
        """Test compiling multiple patterns."""
        compiler = FSAPatternCompiler()
        patterns = [
            ("p1", "foo", "FOO", 2),
            ("p2", "bar", "BAR", 1),
            ("p3", "baz", "BAZ", 3)
        ]
        
        fsa = compiler.compile_patterns(patterns)
        
        # Test that all patterns are recognized
        assert fsa.match("foo") is not None
        assert fsa.match("bar") is not None
        assert fsa.match("baz") is not None
        
        # Test priority ordering
        # Create FSA with overlapping patterns
        patterns_overlap = [
            ("p1", "test", "TEST1", 1),
            ("p2", "test", "TEST2", 2),
            ("p3", "test", "TEST3", 3)
        ]
        
        fsa_overlap = compiler.compile_patterns(patterns_overlap)
        match = fsa_overlap.match("test")
        
        # Should return highest priority match
        assert match.priority == 3
        assert match.replacement == "TEST3"
    
    def test_compile_patterns_with_common_prefixes(self):
        """Test compiling patterns with common prefixes."""
        compiler = FSAPatternCompiler()
        patterns = [
            ("p1", "test", "TEST", 1),
            ("p2", "testing", "TESTING", 1),
            ("p3", "tested", "TESTED", 1)
        ]
        
        fsa = compiler.compile_patterns(patterns)
        
        # All patterns should work correctly
        assert fsa.match("test").matched_text == "test"
        assert fsa.match("testing").matched_text == "testing"
        assert fsa.match("tested").matched_text == "tested"
    
    def test_empty_pattern_list(self):
        """Test compiling empty pattern list."""
        compiler = FSAPatternCompiler()
        fsa = compiler.compile_patterns([])
        
        assert fsa is not None
        assert fsa.match("anything") is None


class TestOptimizedPatternMatcher:
    """Test the optimized pattern matcher."""
    
    def test_pattern_matcher_initialization(self):
        """Test pattern matcher initialization."""
        matcher = OptimizedPatternMatcher()
        
        assert matcher.fsa is None
        assert len(matcher.patterns) == 0
        assert matcher.compiled_hash is None
        assert matcher.match_count == 0
        assert matcher.total_match_time == 0.0
    
    def test_add_and_clear_patterns(self):
        """Test adding and clearing patterns."""
        matcher = OptimizedPatternMatcher()
        
        patterns = [
            ("p1", "foo", "FOO", 1),
            ("p2", "bar", "BAR", 2)
        ]
        
        matcher.add_patterns(patterns)
        assert len(matcher.patterns) == 2
        assert matcher.fsa is None  # Not compiled yet
        
        matcher.clear_patterns()
        assert len(matcher.patterns) == 0
        assert matcher.fsa is None
    
    def test_automatic_compilation(self):
        """Test automatic compilation on first match."""
        matcher = OptimizedPatternMatcher()
        
        patterns = [("p1", "test", "TEST", 1)]
        matcher.add_patterns(patterns)
        
        # Should compile automatically
        match = matcher.match("test string")
        assert match is not None
        assert match.matched_text == "test"
        assert matcher.fsa is not None
        assert matcher.compiled_hash is not None
    
    def test_compilation_caching(self):
        """Test that compilation is cached when patterns don't change."""
        matcher = OptimizedPatternMatcher()
        
        patterns = [("p1", "test", "TEST", 1)]
        matcher.add_patterns(patterns)
        
        # First compilation
        assert matcher.compile() is True
        first_hash = matcher.compiled_hash
        first_fsa = matcher.fsa
        
        # Second compilation should use cache
        assert matcher.compile() is True
        assert matcher.compiled_hash == first_hash
        assert matcher.fsa is first_fsa
        
        # Force recompilation
        assert matcher.compile(force=True) is True
        assert matcher.compiled_hash == first_hash  # Hash should be same
        assert matcher.fsa is not first_fsa  # But FSA object is new
    
    def test_thread_safety(self):
        """Test thread-safe operations."""
        matcher = OptimizedPatternMatcher()
        patterns = [
            ("p1", "thread", "THREAD", 1),
            ("p2", "safe", "SAFE", 1)
        ]
        matcher.add_patterns(patterns)
        
        results = []
        errors = []
        
        def worker(text: str, thread_id: int):
            try:
                for _ in range(100):
                    match = matcher.match(text)
                    if match:
                        results.append((thread_id, match.matched_text))
            except Exception as e:
                errors.append((thread_id, str(e)))
        
        # Run multiple threads
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for i in range(10):
                text = "thread safe" if i % 2 == 0 else "safe thread"
                futures.append(executor.submit(worker, text, i))
            
            for future in as_completed(futures):
                future.result()
        
        assert len(errors) == 0
        assert len(results) > 0
    
    def test_performance_metrics(self):
        """Test performance metric collection."""
        matcher = OptimizedPatternMatcher()
        patterns = [("p1", "test", "TEST", 1)]
        matcher.add_patterns(patterns)
        
        # Perform some matches
        for _ in range(10):
            matcher.match("test string")
        
        metrics = matcher.get_performance_metrics()
        
        assert metrics['total_matches'] == 10
        assert metrics['total_match_time'] > 0
        assert metrics['average_match_time'] > 0
        assert metrics['patterns_count'] == 1
        assert metrics['fsa_states'] > 0
        
        # Reset metrics
        matcher.reset_metrics()
        metrics = matcher.get_performance_metrics()
        assert metrics['total_matches'] == 0
        assert metrics['total_match_time'] == 0
    
    def test_find_all_and_replace(self):
        """Test find_all_matches and replace methods."""
        matcher = OptimizedPatternMatcher()
        patterns = [
            ("p1", "foo", "FOO", 1),
            ("p2", "bar", "BAR", 1)
        ]
        matcher.add_patterns(patterns)
        
        text = "foo and bar and foo"
        
        # Find all matches
        matches = matcher.find_all_matches(text)
        assert len(matches) == 3
        assert matches[0].matched_text == "foo"
        assert matches[1].matched_text == "bar"
        assert matches[2].matched_text == "foo"
        
        # Replace
        result, count = matcher.replace(text)
        assert result == "FOO and BAR and FOO"
        assert count == 3
        
        # Replace with limit
        result, count = matcher.replace(text, max_replacements=2)
        assert result == "FOO and BAR and foo"
        assert count == 2


class TestGlobalPatternMatcher:
    """Test the global pattern matcher instance."""
    
    def test_global_matcher_instance(self):
        """Test that global matcher is accessible and functional."""
        matcher = get_pattern_matcher()
        
        assert matcher is not None
        # Accept either the base OptimizedPatternMatcher or the hybrid implementation
        assert hasattr(matcher, 'add_patterns')
        assert hasattr(matcher, 'match')
        assert hasattr(matcher, 'find_all_matches')
        assert hasattr(matcher, 'replace')
        
        # Should be able to use it normally
        matcher.clear_patterns()
        matcher.add_patterns([("test", "hello", "HELLO", 1)])
        
        match = matcher.match("hello world")
        assert match is not None
        assert match.matched_text == "hello"


class TestPerformanceCharacteristics:
    """Test performance characteristics of the FSA engine."""
    
    def test_linear_time_complexity(self):
        """Test that matching has O(n) time complexity."""
        compiler = FSAPatternCompiler()
        
        # Create a simple pattern
        patterns = [("p1", "pattern", "PATTERN", 1)]
        fsa = compiler.compile_patterns(patterns)
        
        # Test with increasingly long texts
        times = []
        sizes = [1000, 2000, 4000, 8000]
        
        for size in sizes:
            text = "x" * size + "pattern"
            start_time = time.perf_counter()
            match = fsa.match(text)
            end_time = time.perf_counter()
            
            assert match is not None
            times.append(end_time - start_time)
        
        # Check that time increases roughly linearly
        # Allow for some variance due to system factors
        for i in range(1, len(times)):
            ratio = times[i] / times[i-1]
            size_ratio = sizes[i] / sizes[i-1]
            
            # Time should increase roughly proportionally to size
            # Allow 50% variance for system factors
            assert 0.5 * size_ratio <= ratio <= 3.0 * size_ratio
    
    def test_compilation_performance(self):
        """Test that compilation is efficient for multiple patterns."""
        compiler = FSAPatternCompiler()
        
        # Generate many patterns
        patterns = []
        for i in range(100):
            pattern = f"pattern{i:03d}"
            patterns.append((f"p{i}", pattern, pattern.upper(), i))
        
        start_time = time.perf_counter()
        fsa = compiler.compile_patterns(patterns)
        compile_time = time.perf_counter() - start_time
        
        # Compilation should be fast (< 100ms for 100 patterns)
        assert compile_time < 0.1
        
        # All patterns should work
        for i in range(10):  # Test a sample
            pattern = f"pattern{i:03d}"
            match = fsa.match(pattern)
            assert match is not None
            assert match.matched_text == pattern


class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error handling."""
    
    def test_empty_text_matching(self):
        """Test matching against empty text."""
        compiler = FSAPatternCompiler()
        fsa = compiler.compile_patterns([("p1", "test", "TEST", 1)])
        
        match = fsa.match("")
        assert match is None
        
        matches = fsa.find_all_matches("")
        assert len(matches) == 0
        
        result, count = fsa.replace("")
        assert result == ""
        assert count == 0
    
    def test_empty_pattern(self):
        """Test handling of empty patterns."""
        compiler = FSAPatternCompiler()
        fsa = compiler.compile_patterns([("p1", "", "EMPTY", 1)])
        
        # Empty pattern should create minimal FSA
        assert len(fsa.states) == 1  # Just start state which is also accepting
    
    def test_special_characters_in_patterns(self):
        """Test patterns with special characters."""
        compiler = FSAPatternCompiler()
        patterns = [
            ("p1", "test\n", "TEST_NEWLINE", 1),
            ("p2", "test\t", "TEST_TAB", 1),
            ("p3", "test ", "TEST_SPACE", 1)
        ]
        
        fsa = compiler.compile_patterns(patterns)
        
        assert fsa.match("test\n").replacement == "TEST_NEWLINE"
        assert fsa.match("test\t").replacement == "TEST_TAB"
        assert fsa.match("test ").replacement == "TEST_SPACE"
    
    def test_unicode_support(self):
        """Test Unicode character support."""
        compiler = FSAPatternCompiler()
        patterns = [
            ("p1", "café", "CAFE", 1),
            ("p2", "naïve", "NAIVE", 1),
            ("p3", "😀", "EMOJI", 1)
        ]
        
        fsa = compiler.compile_patterns(patterns)
        
        assert fsa.match("café").matched_text == "café"
        assert fsa.match("naïve").matched_text == "naïve"
        assert fsa.match("😀").matched_text == "😀"
    
    def test_very_long_patterns(self):
        """Test handling of very long patterns."""
        compiler = FSAPatternCompiler()
        
        # Create a very long pattern
        long_pattern = "a" * 1000
        patterns = [("p1", long_pattern, "LONG", 1)]
        
        fsa = compiler.compile_patterns(patterns)
        
        # Should handle long patterns efficiently
        match = fsa.match(long_pattern)
        assert match is not None
        assert match.matched_text == long_pattern
    
    def test_pattern_with_no_match(self):
        """Test behavior when no patterns match."""
        compiler = FSAPatternCompiler()
        fsa = compiler.compile_patterns([("p1", "xyz", "XYZ", 1)])
        
        text = "abc def ghi"
        match = fsa.match(text)
        assert match is None
        
        matches = fsa.find_all_matches(text)
        assert len(matches) == 0
        
        result, count = fsa.replace(text)
        assert result == text  # Unchanged
        assert count == 0