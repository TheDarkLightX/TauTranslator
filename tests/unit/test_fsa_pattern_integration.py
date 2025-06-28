"""
Integration tests for FSA pattern matching with pattern loader.

Tests the integration between the FSA engine and the pattern loading system.

Author: DarkLightX / Dana Edwards
"""

import pytest
import json
import asyncio
import tempfile
from pathlib import Path
from typing import Dict, List

from backend.unified.core.pattern_loader import (
    PatternLoader,
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
from backend.unified.infrastructure.repositories.file_pattern_repository import FilePatternRepository
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


@pytest.mark.asyncio
class TestAsyncFSAEnabledPatternManager:
    """Test FSA-enabled pattern manager with async operations."""

    @pytest.fixture
    def temp_pattern_file(self):
        """Create a temporary pattern file."""
        pattern_data = {
            "name": "Test Patterns", "version": "1.0.0",
            "description": "A set of patterns for testing.",
            "rules": [
                {"id": "literal1", "name": "Hello", "type": "literal", "direction": "tce_to_tau", "source": "hello", "target": "HELLO", "priority": 10, "enabled": True},
                {"id": "literal2", "name": "World", "type": "literal", "direction": "tce_to_tau", "source": "world", "target": "WORLD", "priority": 5, "enabled": True},
                {"id": "regex1", "name": "Complex Regex", "type": "regex", "direction": "tce_to_tau", "source": "test.*pattern", "target": "COMPLEX", "priority": 1, "enabled": True}
            ]
        }
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(pattern_data, f)
            temp_path = Path(f.name)
        yield temp_path
        temp_path.unlink()

    async def test_sync_patterns(self, temp_pattern_file):
        """Test synchronizing patterns from loader to FSA."""
        repo = FilePatternRepository()
        loader = PatternLoader(pattern_repository=repo)
        manager = FSAEnabledPatternManager(pattern_loader=loader)
        await loader.load_patterns_from_source_async(temp_pattern_file)
        manager.sync_patterns()
        assert len(manager.fsa_patterns) == 2
        assert len(manager.regex_patterns) == 1

    async def test_match_with_fsa_patterns(self, temp_pattern_file):
        """Test matching using FSA patterns."""
        repo = FilePatternRepository()
        loader = PatternLoader(pattern_repository=repo)
        manager = FSAEnabledPatternManager(pattern_loader=loader)
        await loader.load_patterns_from_source_async(temp_pattern_file)
        manager.sync_patterns()
        match = manager.match("hello there")
        assert match and match.pattern_id == "literal1"

    async def test_match_with_regex_fallback(self, temp_pattern_file):
        """Test falling back to regex when FSA doesn't match."""
        repo = FilePatternRepository()
        loader = PatternLoader(pattern_repository=repo)
        manager = FSAEnabledPatternManager(pattern_loader=loader)
        await loader.load_patterns_from_source_async(temp_pattern_file)
        manager.sync_patterns()
        match = manager.match("this is a test pattern")
        assert match and match.pattern_id == "regex1"

    async def test_reload_patterns(self, temp_pattern_file, monkeypatch):
        """Test pattern reloading."""
        repo = FilePatternRepository()
        loader = PatternLoader(pattern_repository=repo)
        manager = FSAEnabledPatternManager(pattern_loader=loader)
        
        initial_load_result = await loader.load_patterns_from_source_async(str(temp_pattern_file))
        assert initial_load_result.is_success(), f"Initial pattern load failed: {initial_load_result}"

        # Check the specific PatternSet loaded from the temp file
        loaded_pattern_set = loader.get_pattern_set(temp_pattern_file.stem)
        assert loaded_pattern_set is not None, f"PatternSet for id '{temp_pattern_file.stem}' not found in loader."
        assert len(loaded_pattern_set.rules) == 3, f"Expected 3 rules in initial PatternSet, got {len(loaded_pattern_set.rules)}."
        initial_rule_ids = {rule.id for rule in loaded_pattern_set.rules}
        assert {"literal1", "literal2", "regex1"}.issubset(initial_rule_ids), f"Initial rules missing. Got: {initial_rule_ids}"

        manager.sync_patterns()
        initial_fsa_count = len(manager.fsa_patterns)

        # Modify the pattern file on disk
        with open(temp_pattern_file, 'r+') as f:
            data = json.load(f)
            data['rules'].append({"id": "literal3", "name": "New", "type": "literal", "direction": "tce_to_tau", "source": "new", "target": "NEW", "priority": 1, "enabled": True})
            f.seek(0)
            json.dump(data, f)
            f.truncate()

        # Manually trigger the loader to re-read the modified file
        reload_result = await loader.load_patterns_from_source_async(str(temp_pattern_file))
        assert reload_result.is_success(), f"Pattern reload failed: {reload_result}"

        # Check the specific PatternSet again after reload
        updated_pattern_set = loader.get_pattern_set(temp_pattern_file.stem)
        assert updated_pattern_set is not None, f"PatternSet for id '{temp_pattern_file.stem}' not found after reload."
        assert len(updated_pattern_set.rules) == 4, f"Expected 4 rules after reload, got {len(updated_pattern_set.rules)}."
        rule_ids_after_reload = {rule.id for rule in updated_pattern_set.rules}
        assert "literal3" in rule_ids_after_reload, "Newly added rule 'literal3' not found in reloaded PatternSet."

        # Manually trigger the manager to resync with the loader's updated patterns
        await asyncio.to_thread(manager.sync_patterns)
        assert len(manager.fsa_patterns) == initial_fsa_count + 1
        assert "literal3" in manager.fsa_patterns

    async def test_direction_filtering(self, temp_pattern_file):
        """Test pattern filtering by direction."""
        repo = FilePatternRepository()
        loader = PatternLoader(pattern_repository=repo)
        manager = FSAEnabledPatternManager(pattern_loader=loader)
        await loader.load_patterns_from_source_async(temp_pattern_file)
        manager.sync_patterns(direction=PatternDirection.TCE_TO_TAU)
        assert len(manager.fsa_patterns) == 2
        assert len(manager.regex_patterns) == 1
        manager.sync_patterns(direction=PatternDirection.TAU_TO_TCE)
        assert len(manager.fsa_patterns) == 0
        assert len(manager.regex_patterns) == 0


class TestGlobalFSAPatternManager:
    """Test global FSA pattern manager instance."""

    @pytest.mark.asyncio
    async def test_global_instance_access(self, monkeypatch):
        """Test accessing global FSA pattern manager."""
        # Reset the global instance for a clean test
        from backend.unified.core.pattern_matching import fsa_pattern_integration
        fsa_pattern_integration._global_fsa_pattern_manager = None
        
        manager = get_fsa_pattern_manager()
        
        assert manager is not None
        assert isinstance(manager, FSAEnabledPatternManager)
        
        # It should be a singleton
        manager2 = get_fsa_pattern_manager()
        assert manager is manager2

        # Clear any existing patterns
        manager.sync_patterns()
        assert not manager.fsa_patterns
        assert not manager.regex_patterns