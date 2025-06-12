"""
Integration tests for FSA pattern matching with pattern loader.

Tests the integration between the FSA engine and the pattern loading system.

Author: DarkLightX / Dana Edwards
"""

import pytest
import json
import tempfile
from pathlib import Path
from typing import Dict, List

from backend.unified.core.pattern_loader import (
    PatternManager,
    PatternRule,
    PatternType,
    PatternDirection,
    PatternSet
)
from backend.unified.core.pattern_matching.fsa_pattern_integration import (
    FSAPatternAdapter,
    FSAEnabledPatternManager,
    get_fsa_pattern_manager
)
from backend.unified.core.pattern_matching import MatchResult


class TestFSAPatternAdapter:
    """Test FSA pattern adapter functionality."""
    
    def test_convert_literal_pattern(self):
        """Test converting literal pattern to FSA format."""
        pattern = PatternRule(
            id="test1",
            name="Test Pattern",
            pattern_type=PatternType.LITERAL,
            direction=PatternDirection.TCE_TO_TAU,
            source_pattern="hello",
            target_pattern="HELLO",
            priority=5
        )
        
        adapter = FSAPatternAdapter()
        fsa_pattern = adapter.convert_to_fsa_pattern(pattern)
        
        assert fsa_pattern == ("test1", "hello", "HELLO", 5)
    
    def test_convert_simple_regex_pattern(self):
        """Test converting simple regex pattern to FSA format."""
        pattern = PatternRule(
            id="test2",
            name="Simple Regex",
            pattern_type=PatternType.REGEX,
            direction=PatternDirection.TCE_TO_TAU,
            source_pattern="world",  # Simple pattern without regex chars
            target_pattern="WORLD",
            priority=3
        )
        
        adapter = FSAPatternAdapter()
        fsa_pattern = adapter.convert_to_fsa_pattern(pattern)
        
        assert fsa_pattern == ("test2", "world", "WORLD", 3)
    
    def test_can_use_fsa_literal(self):
        """Test checking if literal patterns can use FSA."""
        pattern = PatternRule(
            id="test3",
            name="Literal Pattern",
            pattern_type=PatternType.LITERAL,
            direction=PatternDirection.TCE_TO_TAU,
            source_pattern="foo",
            target_pattern="FOO",
            priority=1
        )
        
        adapter = FSAPatternAdapter()
        assert adapter.can_use_fsa(pattern) is True
    
    def test_can_use_fsa_simple_regex(self):
        """Test checking if simple regex can use FSA."""
        adapter = FSAPatternAdapter()
        
        # Simple pattern without regex chars
        simple_pattern = PatternRule(
            id="test4",
            name="Simple",
            pattern_type=PatternType.REGEX,
            direction=PatternDirection.TCE_TO_TAU,
            source_pattern="simple",
            target_pattern="SIMPLE",
            priority=1
        )
        assert adapter.can_use_fsa(simple_pattern) is True
        
        # Complex pattern with regex chars
        complex_pattern = PatternRule(
            id="test5",
            name="Complex",
            pattern_type=PatternType.REGEX,
            direction=PatternDirection.TCE_TO_TAU,
            source_pattern="test.*pattern",
            target_pattern="COMPLEX",
            priority=1
        )
        assert adapter.can_use_fsa(complex_pattern) is False
    
    def test_unsupported_pattern_types(self):
        """Test that template and function patterns are not supported."""
        adapter = FSAPatternAdapter()
        
        template_pattern = PatternRule(
            id="test6",
            name="Template",
            pattern_type=PatternType.TEMPLATE,
            direction=PatternDirection.TCE_TO_TAU,
            source_pattern="${var}",
            target_pattern="TEMPLATE",
            priority=1
        )
        
        assert adapter.can_use_fsa(template_pattern) is False
        
        with pytest.raises(ValueError):
            adapter.convert_to_fsa_pattern(template_pattern)


class TestFSAEnabledPatternManager:
    """Test FSA-enabled pattern manager."""
    
    @pytest.fixture
    def temp_pattern_file(self):
        """Create a temporary pattern file."""
        pattern_data = {
            "name": "Test Patterns",
            "version": "1.0.0",
            "description": "Test pattern set",
            "patterns": [
                {
                    "id": "literal1",
                    "name": "Literal Pattern 1",
                    "type": "literal",
                    "direction": "tce_to_tau",
                    "source": "hello",
                    "target": "HELLO",
                    "priority": 10,
                    "enabled": True
                },
                {
                    "id": "literal2",
                    "name": "Literal Pattern 2",
                    "type": "literal",
                    "direction": "tce_to_tau",
                    "source": "world",
                    "target": "WORLD",
                    "priority": 5,
                    "enabled": True
                },
                {
                    "id": "regex1",
                    "name": "Complex Regex",
                    "type": "regex",
                    "direction": "tce_to_tau",
                    "source": "test.*pattern",
                    "target": "REGEX_MATCH",
                    "priority": 3,
                    "enabled": True
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(pattern_data, f)
            temp_path = Path(f.name)
        
        yield temp_path
        temp_path.unlink()
    
    def test_sync_patterns(self, temp_pattern_file):
        """Test synchronizing patterns from loader to FSA."""
        # Create a new manager to avoid global state issues
        manager = FSAEnabledPatternManager()
        
        # Load patterns
        manager.pattern_manager.load_pattern_set(temp_pattern_file, "test_set")
        
        # Sync patterns
        manager.sync_patterns()
        
        # Check pattern distribution
        assert len(manager.fsa_patterns) == 2  # Two literal patterns
        assert len(manager.regex_patterns) == 1  # One complex regex
        
        assert "literal1" in manager.fsa_patterns
        assert "literal2" in manager.fsa_patterns
        assert "regex1" in manager.regex_patterns
    
    def test_match_with_fsa_patterns(self, temp_pattern_file):
        """Test matching using FSA patterns."""
        manager = FSAEnabledPatternManager()
        manager.pattern_manager.load_pattern_set(temp_pattern_file, "test_set")
        manager.sync_patterns()
        
        # Test FSA match
        match = manager.match("hello world")
        assert match is not None
        assert match.pattern_id == "literal1"
        assert match.matched_text == "hello"
        assert match.replacement == "HELLO"
        assert manager.fsa_matches == 1
        assert manager.regex_matches == 0
    
    def test_match_with_regex_fallback(self, temp_pattern_file):
        """Test falling back to regex when FSA doesn't match."""
        manager = FSAEnabledPatternManager()
        manager.pattern_manager.load_pattern_set(temp_pattern_file, "test_set")
        manager.sync_patterns()
        
        # Test regex match
        text = "test something pattern"
        match = manager.match(text)
        assert match is not None
        assert match.pattern_id == "regex1"
        assert match.replacement == "REGEX_MATCH"
        assert manager.fsa_matches == 0
        assert manager.regex_matches == 1
    
    def test_find_all_matches(self, temp_pattern_file):
        """Test finding all matches with both FSA and regex."""
        manager = FSAEnabledPatternManager()
        manager.pattern_manager.load_pattern_set(temp_pattern_file, "test_set")
        manager.sync_patterns()
        
        text = "hello world and test some pattern"
        matches = manager.find_all_matches(text)
        
        # Should find at least 2 matches (hello, world)
        assert len(matches) >= 2
        
        # Check that matches are sorted by priority
        priorities = [m.priority for m in matches]
        assert priorities == sorted(priorities, reverse=True)
    
    def test_replace_functionality(self, temp_pattern_file):
        """Test pattern replacement."""
        manager = FSAEnabledPatternManager()
        manager.pattern_manager.load_pattern_set(temp_pattern_file, "test_set")
        manager.sync_patterns()
        
        text = "hello world hello"
        result, count = manager.replace(text)
        
        assert result == "HELLO WORLD HELLO"
        assert count == 3
    
    def test_performance_metrics(self, temp_pattern_file):
        """Test performance metric collection."""
        manager = FSAEnabledPatternManager()
        manager.pattern_manager.load_pattern_set(temp_pattern_file, "test_set")
        manager.sync_patterns()
        
        # Perform some matches
        manager.match("hello")
        manager.match("world")
        manager.match("test pattern here")
        
        metrics = manager.get_performance_metrics()
        
        assert metrics['total_matches'] == 3
        assert metrics['fsa_matches'] == 2
        assert metrics['regex_matches'] == 1
        assert metrics['fsa_percentage'] == pytest.approx(66.67, 0.01)
        assert metrics['pattern_distribution']['fsa'] == 2
        assert metrics['pattern_distribution']['regex'] == 1
    
    def test_reload_patterns(self, temp_pattern_file):
        """Test pattern reloading."""
        manager = FSAEnabledPatternManager()
        manager.pattern_manager.load_pattern_set(temp_pattern_file, "test_set")
        manager.sync_patterns()
        
        initial_fsa_count = len(manager.fsa_patterns)
        
        # Modify the pattern file
        with open(temp_pattern_file, 'r') as f:
            data = json.load(f)
        
        # Add a new pattern
        data['patterns'].append({
            "id": "literal3",
            "name": "New Pattern",
            "type": "literal",
            "direction": "tce_to_tau",
            "source": "new",
            "target": "NEW",
            "priority": 1,
            "enabled": True
        })
        
        with open(temp_pattern_file, 'w') as f:
            json.dump(data, f)
        
        # Reload patterns
        manager.reload_patterns()
        
        # Check that new pattern was loaded
        assert len(manager.fsa_patterns) == initial_fsa_count + 1
        assert "literal3" in manager.fsa_patterns
    
    def test_direction_filtering(self, temp_pattern_file):
        """Test pattern filtering by direction."""
        manager = FSAEnabledPatternManager()
        
        # Add bidirectional pattern
        bidirectional_data = {
            "name": "Bidirectional Patterns",
            "version": "1.0.0",
            "description": "Test bidirectional patterns",
            "patterns": [
                {
                    "id": "bi1",
                    "name": "Bidirectional Pattern",
                    "type": "literal",
                    "direction": "bidirectional",
                    "source": "test",
                    "target": "TEST",
                    "priority": 1,
                    "enabled": True
                }
            ]
        }
        
        manager.pattern_manager.load_pattern_set(bidirectional_data, "bidirectional_set")
        manager.pattern_manager.load_pattern_set(temp_pattern_file, "test_set")
        
        # Sync with specific direction
        manager.sync_patterns(PatternDirection.TCE_TO_TAU)
        
        # Should include all TCE_TO_TAU and bidirectional patterns
        assert len(manager.fsa_patterns) >= 3  # 2 from temp_file + 1 bidirectional
        assert "bi1" in manager.fsa_patterns


class TestGlobalFSAPatternManager:
    """Test global FSA pattern manager instance."""
    
    def test_global_instance_access(self):
        """Test accessing global FSA pattern manager."""
        manager = get_fsa_pattern_manager()
        
        assert manager is not None
        assert isinstance(manager, FSAEnabledPatternManager)
        
        # Clear any existing patterns
        manager.fsa_matcher.clear_patterns()
        manager.fsa_patterns.clear()
        manager.regex_patterns.clear()
        
        # Should be able to use it
        simple_patterns = [
            ("p1", "test", "TEST", 1)
        ]
        manager.fsa_matcher.add_patterns(simple_patterns)
        
        match = manager.fsa_matcher.match("test string")
        assert match is not None
        assert match.matched_text == "test"