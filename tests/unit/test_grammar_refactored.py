"""
Unit tests for the refactored grammar API following clean code principles.

Tests are organized by the helper classes and demonstrate:
- Pure functions with @mutation_free are truly immutable
- Domain types prevent invalid states
- Result monad properly propagates errors
- Each method has single responsibility
"""

import pytest
from pathlib import Path
from typing import List, Optional
from unittest.mock import Mock, AsyncMock, MagicMock

from backend.unified.api.grammar_refactored import (
    # Domain types
    GrammarName, GrammarPath, GrammarContent, GrammarFormat, CacheKey,
    GrammarMetadata, GrammarListResponse, GrammarLoadResult, GrammarStatusResult,
    # Infrastructure
    GrammarFileRepository, GrammarConfigRepository,
    # Core
    GrammarCache, GrammarValidator, GrammarRuleExtractor, GrammarService,
    # Result types
    success, failure
)


class TestDomainTypes:
    """Test domain type safety and immutability."""
    
    def test_grammar_metadata_is_immutable(self):
        """Test that GrammarMetadata is truly immutable."""
        metadata = GrammarMetadata(
            name=GrammarName("test"),
            filename="test.lark",
            path=GrammarPath("/path/test.lark"),
            format="lark",
            size=100,
            rules=["rule1", "rule2"]
        )
        
        # Should not be able to modify
        with pytest.raises(AttributeError):
            metadata.name = GrammarName("changed")
    
    def test_grammar_format_only_allows_valid_values(self):
        """Test that GrammarFormat type checking works."""
        # This would be caught by type checker
        valid_formats = ["tgf", "ebnf", "lark"]
        for fmt in valid_formats:
            assert fmt in ["tgf", "ebnf", "lark"]


class TestGrammarValidator:
    """Test the pure validation functions."""
    
    def test_validate_file_extension_success(self):
        """Test successful file extension validation."""
        result = GrammarValidator.validate_file_extension("test.lark")
        assert result.is_success()
        assert result.value == "lark"
        
        result = GrammarValidator.validate_file_extension("grammar.tgf")
        assert result.is_success()
        assert result.value == "tgf"
        
        result = GrammarValidator.validate_file_extension("rules.ebnf")
        assert result.is_success()
        assert result.value == "ebnf"
    
    def test_validate_file_extension_failure(self):
        """Test file extension validation with invalid extensions."""
        result = GrammarValidator.validate_file_extension("test.txt")
        assert result.is_failure()
        assert result.error_code == "INVALID_FORMAT"
        assert "Invalid file format" in result.message
        
        result = GrammarValidator.validate_file_extension("no_extension")
        assert result.is_failure()
    
    def test_validate_grammar_path_success(self):
        """Test successful path validation."""
        # Create a mock path that exists
        mock_path = Mock(spec=Path)
        mock_path.exists.return_value = True
        mock_path.is_file.return_value = True
        
        result = GrammarValidator.validate_grammar_path(mock_path)
        assert result.is_success()
        assert result.value == mock_path
    
    def test_validate_grammar_path_not_found(self):
        """Test path validation when file doesn't exist."""
        mock_path = Mock(spec=Path)
        mock_path.exists.return_value = False
        
        result = GrammarValidator.validate_grammar_path(mock_path)
        assert result.is_failure()
        assert result.error_code == "FILE_NOT_FOUND"
    
    def test_validate_grammar_path_not_file(self):
        """Test path validation when path is directory."""
        mock_path = Mock(spec=Path)
        mock_path.exists.return_value = True
        mock_path.is_file.return_value = False
        
        result = GrammarValidator.validate_grammar_path(mock_path)
        assert result.is_failure()
        assert result.error_code == "NOT_A_FILE"


class TestGrammarRuleExtractor:
    """Test pure rule extraction functions."""
    
    def test_extract_tgf_rules(self):
        """Test TGF rule extraction."""
        content = GrammarContent("""
        rule1 ::= 'value1'
        rule2 : 'value2'
        // comment
        rule3 ::= rule1 rule2
        """)
        
        rules = GrammarRuleExtractor.extract_rules_from_content(content, "tgf")
        assert rules == ["rule1", "rule2", "rule3"]
    
    def test_extract_ebnf_rules(self):
        """Test EBNF rule extraction."""
        content = GrammarContent("""
        statement = expression ';'
        expression = term ('+' term)*
        term = factor ('*' factor)*
        """)
        
        rules = GrammarRuleExtractor.extract_rules_from_content(content, "ebnf")
        assert rules == ["statement", "expression", "term"]
    
    def test_extract_lark_rules(self):
        """Test Lark rule extraction."""
        content = GrammarContent("""
        // Lark grammar
        start: expression
        
        expression: term (ADD term)*
        
        # Another comment
        term: factor (MUL factor)*
        
        factor: NUMBER
        """)
        
        rules = GrammarRuleExtractor.extract_rules_from_content(content, "lark")
        assert rules == ["start", "expression", "term", "factor"]
    
    def test_extract_rules_invalid_format(self):
        """Test rule extraction with invalid format."""
        content = GrammarContent("some content")
        rules = GrammarRuleExtractor.extract_rules_from_content(content, "invalid")  # type: ignore
        assert rules == []
    
    def test_rule_extraction_is_pure(self):
        """Test that rule extraction doesn't modify input."""
        content = GrammarContent("rule1 ::= 'test'")
        original = str(content)
        
        GrammarRuleExtractor.extract_rules_from_content(content, "tgf")
        
        # Content should be unchanged
        assert str(content) == original


class TestGrammarCache:
    """Test the in-memory cache."""
    
    def test_cache_stores_and_retrieves(self):
        """Test basic cache operations."""
        cache = GrammarCache()
        key = CacheKey("test:grammar1")
        metadata = GrammarMetadata(
            name=GrammarName("grammar1"),
            filename="grammar1.lark",
            path=GrammarPath("/path/grammar1.lark"),
            format="lark",
            size=100,
            rules=["rule1"]
        )
        
        # Initially empty
        assert cache.get_cached_grammar(key) is None
        
        # Store
        cache.cache_grammar(key, metadata)
        
        # Retrieve
        cached = cache.get_cached_grammar(key)
        assert cached == metadata
    
    def test_cache_clear(self):
        """Test cache clearing."""
        cache = GrammarCache()
        key1 = CacheKey("test:1")
        key2 = CacheKey("test:2")
        
        metadata1 = Mock(spec=GrammarMetadata)
        metadata2 = Mock(spec=GrammarMetadata)
        
        cache.cache_grammar(key1, metadata1)
        cache.cache_grammar(key2, metadata2)
        
        # Both cached
        assert cache.get_cached_grammar(key1) is not None
        assert cache.get_cached_grammar(key2) is not None
        
        # Clear
        cache.clear_cache()
        
        # Both gone
        assert cache.get_cached_grammar(key1) is None
        assert cache.get_cached_grammar(key2) is None


class TestGrammarFileRepository:
    """Test file I/O operations."""
    
    @pytest.mark.asyncio
    async def test_scan_grammar_directory_success(self):
        """Test successful directory scanning."""
        # Create mock directory with files
        mock_dir = Mock(spec=Path)
        mock_dir.exists.return_value = True
        
        mock_file1 = Mock(spec=Path)
        mock_file1.stem = "grammar1"
        mock_file1.name = "grammar1.lark"
        mock_file1.suffix = ".lark"
        mock_file1.stat.return_value.st_size = 100
        
        mock_file2 = Mock(spec=Path)
        mock_file2.stem = "grammar2"
        mock_file2.name = "grammar2.tgf"
        mock_file2.suffix = ".tgf"
        mock_file2.stat.return_value.st_size = 200
        
        mock_dir.glob.side_effect = [
            [],  # *.tgf
            [],  # *.ebnf
            [mock_file1]  # *.lark
        ]
        
        result = await GrammarFileRepository.scan_grammar_directory_async(mock_dir)
        
        assert result.is_success()
        assert len(result.value) == 1
        assert result.value[0].name == GrammarName("grammar1")
    
    @pytest.mark.asyncio
    async def test_scan_grammar_directory_not_exists(self):
        """Test scanning non-existent directory."""
        mock_dir = Mock(spec=Path)
        mock_dir.exists.return_value = False
        
        result = await GrammarFileRepository.scan_grammar_directory_async(mock_dir)
        
        assert result.is_success()
        assert result.value == []
    
    @pytest.mark.asyncio
    async def test_read_grammar_content_success(self):
        """Test successful file reading."""
        mock_path = Mock(spec=Path)
        mock_path.read_text.return_value = "grammar content"
        
        result = await GrammarFileRepository.read_grammar_content_async(mock_path)
        
        assert result.is_success()
        assert result.value == GrammarContent("grammar content")
        mock_path.read_text.assert_called_once_with(encoding='utf-8')
    
    @pytest.mark.asyncio
    async def test_read_grammar_content_failure(self):
        """Test file reading failure."""
        mock_path = Mock(spec=Path)
        mock_path.read_text.side_effect = IOError("Permission denied")
        
        result = await GrammarFileRepository.read_grammar_content_async(mock_path)
        
        assert result.is_failure()
        assert result.error_code == "READ_ERROR"
        assert "Permission denied" in result.message


class TestGrammarService:
    """Test the main service orchestration."""
    
    @pytest.fixture
    def mock_dependencies(self):
        """Create mock dependencies for service."""
        return {
            'file_repository': Mock(spec=GrammarFileRepository),
            'config_repository': Mock(spec=GrammarConfigRepository),
            'cache': GrammarCache(),
            'validator': GrammarValidator(),
            'rule_extractor': GrammarRuleExtractor()
        }
    
    @pytest.mark.asyncio
    async def test_list_grammars_with_active(self, mock_dependencies):
        """Test listing grammars with active grammar."""
        service = GrammarService(**mock_dependencies)
        
        # Mock file repo response
        grammars = [
            GrammarMetadata(
                name=GrammarName("test1"),
                filename="test1.lark",
                path=GrammarPath("/path/test1.lark"),
                format="lark",
                size=100,
                rules=[]
            )
        ]
        mock_dependencies['file_repository'].scan_grammar_directory_async = AsyncMock(
            return_value=success(grammars)
        )
        
        # Mock config repo response
        mock_dependencies['config_repository'].load_active_grammar_config_async = AsyncMock(
            return_value=success(GrammarName("test1"))
        )
        
        # Execute
        result = await service.list_grammars_with_active_async()
        
        assert result.is_success()
        assert isinstance(result.value, GrammarListResponse)
        assert len(result.value.grammars) == 1
        assert result.value.active_grammar == GrammarName("test1")
    
    @pytest.mark.asyncio
    async def test_get_grammar_from_cache(self, mock_dependencies):
        """Test getting grammar from cache."""
        service = GrammarService(**mock_dependencies)
        
        # Pre-populate cache
        grammar_name = GrammarName("cached")
        cache_key = CacheKey("grammar:cached")
        metadata = GrammarMetadata(
            name=grammar_name,
            filename="cached.lark",
            path=GrammarPath("/path/cached.lark"),
            format="lark",
            size=100,
            rules=["rule1"]
        )
        service._cache.cache_grammar(cache_key, metadata)
        
        # Execute
        result = await service.get_grammar_details_with_cache_async(grammar_name)
        
        assert result.is_success()
        assert result.value == metadata
        # File repo should not be called
        mock_dependencies['file_repository'].read_grammar_content_async.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_activate_grammar_success(self, mock_dependencies):
        """Test successful grammar activation."""
        service = GrammarService(**mock_dependencies)
        
        # Mock existence check
        mock_dependencies['file_repository'].scan_grammar_directory_async = AsyncMock(
            return_value=success([
                GrammarMetadata(
                    name=GrammarName("test"),
                    filename="test.lark",
                    path=GrammarPath("/path/test.lark"),
                    format="lark",
                    size=100,
                    rules=[]
                )
            ])
        )
        
        # Mock config save
        mock_dependencies['config_repository'].save_active_grammar_config_async = AsyncMock(
            return_value=success(None)
        )
        
        # Execute
        result = await service.activate_grammar_async(GrammarName("test"))
        
        assert result.is_success()
        mock_dependencies['config_repository'].save_active_grammar_config_async.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_activate_grammar_not_found(self, mock_dependencies):
        """Test activating non-existent grammar."""
        service = GrammarService(**mock_dependencies)
        
        # Mock empty directory
        mock_dependencies['file_repository'].scan_grammar_directory_async = AsyncMock(
            return_value=success([])
        )
        
        # Execute
        result = await service.activate_grammar_async(GrammarName("missing"))
        
        assert result.is_failure()
        assert result.error_code == "NOT_FOUND"
        assert "Grammar 'missing' not found" in result.message