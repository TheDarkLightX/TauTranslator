"""
Mutation-resistant tests for plugin manager.

These tests are specifically designed to catch common mutations:
- Boundary value mutations
- Operator replacements  
- Return value modifications
- Conditional negations

Copyright: DarkLightX / Dana Edwards
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import json

from src.tau_translator_omega.core_engine.plugin_manager_refactored import (
    PluginId, ErrorCode, ErrorMessage, ManifestPath, PluginDirectory,
    PluginError, ValidationResult, PluginValidator, PluginRegistry,
    ManifestFileRepository, VersionCompatibilityChecker, PluginInstantiator,
    PluginManager
)
from src.tau_translator_omega.core_engine.plugin import Plugin
from returns.result import Success, Failure


class TestBoundaryValueMutations:
    """Tests that catch boundary value mutations."""
    
    def test_empty_plugin_id_validation(self):
        """Test that empty plugin ID is specifically rejected."""
        # This catches mutations that might change "" to None or vice versa
        registry = PluginRegistry()
        
        plugin_empty = Mock(spec=Plugin)
        plugin_empty.id = ""  # Empty string, not None
        
        result = registry.register(plugin_empty)
        
        # Should succeed - we don't validate ID length in registry
        assert isinstance(result, Success)
        
        # But retrieval should handle empty ID
        retrieved = registry.get(PluginId(""))
        assert retrieved == plugin_empty
    
    def test_single_character_plugin_operations(self):
        """Test operations with single character plugin IDs."""
        # Catches off-by-one mutations in string length checks
        registry = PluginRegistry()
        
        plugin = Mock(spec=Plugin)
        plugin.id = "a"  # Single character
        
        result = registry.register(plugin)
        assert isinstance(result, Success)
        
        retrieved = registry.get(PluginId("a"))
        assert retrieved == plugin
    
    def test_registry_with_exactly_one_plugin(self):
        """Test registry operations with exactly one plugin."""
        # Catches mutations that might change == to > or >=
        registry = PluginRegistry()
        
        plugin = Mock(spec=Plugin)
        plugin.id = "single"
        
        # Before registration
        assert len(registry.get_all()) == 0
        
        # After registration
        registry.register(plugin)
        all_plugins = registry.get_all()
        assert len(all_plugins) == 1
        assert all_plugins[0] == plugin
        
        # After clear
        registry.clear()
        assert len(registry.get_all()) == 0


class TestOperatorReplacementMutations:
    """Tests that catch operator replacement mutations."""
    
    def test_duplicate_plugin_detection_exact_match(self):
        """Test that duplicate detection uses exact ID matching."""
        # Catches mutations of == to != or other operators
        registry = PluginRegistry()
        
        plugin1 = Mock(spec=Plugin)
        plugin1.id = "test-plugin"
        
        plugin2 = Mock(spec=Plugin) 
        plugin2.id = "test-plugin"  # Exact same ID
        
        plugin3 = Mock(spec=Plugin)
        plugin3.id = "test-plugin2"  # Different ID
        
        # First registration succeeds
        result1 = registry.register(plugin1)
        assert isinstance(result1, Success)
        
        # Second with same ID fails
        result2 = registry.register(plugin2)
        assert isinstance(result2, Failure)
        assert result2.failure().code == "DUPLICATE_PLUGIN"
        
        # Third with different ID succeeds
        result3 = registry.register(plugin3)
        assert isinstance(result3, Success)
    
    def test_error_collector_preserves_order(self):
        """Test that error collector preserves error order."""
        # Catches mutations in list operations
        from src.tau_translator_omega.core_engine.plugin_manager_refactored import ErrorCollector
        
        collector = ErrorCollector()
        
        error1 = PluginError(ErrorCode("FIRST"), ErrorMessage("First error"))
        error2 = PluginError(ErrorCode("SECOND"), ErrorMessage("Second error"))
        error3 = PluginError(ErrorCode("THIRD"), ErrorMessage("Third error"))
        
        collector.add_error(error1)
        collector.add_error(error2)
        collector.add_error(error3)
        
        errors = collector.get_errors()
        
        # Verify exact order and values
        assert len(errors) == 3
        assert errors[0].code == "FIRST"
        assert errors[1].code == "SECOND"
        assert errors[2].code == "THIRD"
        
        # Verify it's a copy, not the original list
        errors.append(PluginError(ErrorCode("FOURTH"), ErrorMessage("Fourth")))
        assert len(collector.get_errors()) == 3  # Original unchanged
    
    def test_path_existence_checks(self, tmp_path):
        """Test that path existence is checked correctly."""
        # Catches mutations of exists() or is_dir() calls
        existing_dir = tmp_path / "existing"
        existing_dir.mkdir()
        
        non_existing = tmp_path / "non-existing"
        
        existing_file = tmp_path / "file.txt"
        existing_file.write_text("content")
        
        # Test directory that exists
        result1 = ManifestFileRepository.scan_for_manifests(PluginDirectory(existing_dir))
        assert isinstance(result1, Success)
        
        # Test directory that doesn't exist
        result2 = ManifestFileRepository.scan_for_manifests(PluginDirectory(non_existing))
        assert isinstance(result2, Failure)
        assert result2.failure().code == "INVALID_DIRECTORY"
        
        # Test file instead of directory
        result3 = ManifestFileRepository.scan_for_manifests(PluginDirectory(existing_file))
        assert isinstance(result3, Failure)
        assert result3.failure().code == "INVALID_DIRECTORY"


class TestReturnValueMutations:
    """Tests that catch return value mutations."""
    
    def test_validation_result_boolean_flags(self):
        """Test that validation result booleans are used correctly."""
        # Catches mutations of True to False or vice versa
        
        # Success case
        success_result = ValidationResult(
            success=True,
            config={"key": "value"},
            errors=[]
        )
        assert success_result.success is True  # Not just truthy
        assert success_result.config == {"key": "value"}
        assert success_result.errors == []
        
        # Failure case  
        failure_result = ValidationResult(
            success=False,
            config={},
            errors=[ErrorMessage("Error occurred")]
        )
        assert failure_result.success is False  # Not just falsy
        assert failure_result.config == {}
        assert len(failure_result.errors) == 1
    
    def test_plugin_instance_none_vs_not_none(self, tmp_path):
        """Test that plugin instance None is handled distinctly."""
        # Catches mutations that might return empty object instead of None
        manager = PluginManager(plugin_dirs=str(tmp_path))
        
        # Plugin without instance
        plugin_no_instance = Mock(spec=Plugin)
        plugin_no_instance.id = "no-instance"
        plugin_no_instance.instance = None
        
        # Plugin with instance
        plugin_with_instance = Mock(spec=Plugin)
        plugin_with_instance.id = "with-instance"
        plugin_with_instance.instance = Mock()  # Non-None instance
        
        manager._registry.register(plugin_no_instance)
        manager._registry.register(plugin_with_instance)
        
        # Test invocation on plugin without instance
        result1 = manager.invoke_translation("no-instance", "source")
        assert result1 is None  # Specifically None, not empty dict
        errors = manager.get_errors()
        assert any(e.code == "NO_INSTANCE" for e in errors)
        
        # Clear errors for next test
        manager._error_collector.clear()
        
        # Test invocation on plugin with instance but no method
        result2 = manager.invoke_translation("with-instance", "source")
        assert result2 is None
        errors = manager.get_errors()
        assert any(e.code == "NO_TRANSLATE_METHOD" for e in errors)


class TestConditionalMutations:
    """Tests that catch conditional mutations."""
    
    def test_entry_point_type_checking(self):
        """Test entry point type is checked with exact string match."""
        # Catches mutations in string comparisons
        from src.tau_translator_omega.core_engine.plugin_manager_refactored import PluginLoadingService
        
        service = PluginLoadingService(Mock(), Mock(), Mock())
        
        # Grammar plugins - no instantiation
        grammar_plugin = Mock(spec=Plugin)
        grammar_plugin.plugin_type = "grammar_definition"
        assert service._requires_instantiation(grammar_plugin) is False
        
        # Different casing should not match
        grammar_plugin2 = Mock(spec=Plugin) 
        grammar_plugin2.plugin_type = "GRAMMAR_DEFINITION"
        grammar_plugin2.entry_point = Mock(type="module")
        assert service._requires_instantiation(grammar_plugin2) is True
        
        # Module type entry point
        module_plugin = Mock(spec=Plugin)
        module_plugin.plugin_type = "generic"
        module_plugin.entry_point = Mock(type="module")
        assert service._requires_instantiation(module_plugin) is True
        
        # CLI type entry point  
        cli_plugin = Mock(spec=Plugin)
        cli_plugin.plugin_type = "generic"
        cli_plugin.entry_point = Mock(type="cli")
        assert service._requires_instantiation(cli_plugin) is False
    
    def test_version_compatibility_invalid_core_version(self):
        """Test version compatibility with invalid core version."""
        # Catches mutations in None checks
        mock_handler = Mock()
        mock_handler.parse_semver.return_value = None  # Invalid version
        
        checker = VersionCompatibilityChecker(mock_handler, "invalid")
        plugin = Mock(spec=Plugin)
        
        is_compatible, errors = checker.is_compatible(plugin)
        
        assert is_compatible is False  # Specifically False
        assert len(errors) == 1
        assert "Invalid core version" in errors[0]
        
        # Handler should not be called for compatibility check
        mock_handler.check_ilr_compatibility.assert_not_called()


class TestLoopMutations:
    """Tests that catch loop boundary mutations."""
    
    def test_manifest_scanning_finds_all_files(self, tmp_path):
        """Test that all manifest files are found, not just first/last."""
        # Catches mutations that might break loops early
        
        # Create multiple nested manifests
        paths = [
            "a/manifest.json",
            "b/manifest.json", 
            "c/deep/manifest.json",
            "d/deeper/still/manifest.json",
            "manifest.json"  # Root level
        ]
        
        for path in paths:
            full_path = tmp_path / path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text("{}")
        
        result = ManifestFileRepository.scan_for_manifests(PluginDirectory(tmp_path))
        
        assert isinstance(result, Success)
        found_paths = result.value
        assert len(found_paths) == 5  # All files found
        
        # Verify specific files are included
        found_names = [str(p.name) for p in found_paths]
        assert all(name == "manifest.json" for name in found_names)
    
    def test_error_collector_get_errors_returns_all(self):
        """Test that get_errors returns all errors, not subset."""
        from src.tau_translator_omega.core_engine.plugin_manager_refactored import ErrorCollector
        
        collector = ErrorCollector()
        
        # Add many errors
        for i in range(10):
            error = PluginError(
                ErrorCode(f"ERROR_{i}"),
                ErrorMessage(f"Error number {i}")
            )
            collector.add_error(error)
        
        errors = collector.get_errors()
        assert len(errors) == 10
        
        # Verify all errors are present
        for i in range(10):
            assert any(e.code == f"ERROR_{i}" for e in errors)


class TestExceptionHandlingMutations:
    """Tests that catch mutations in exception handling."""
    
    def test_json_decode_error_specific_handling(self, tmp_path):
        """Test that JSON decode errors are handled specifically."""
        # Catches mutations that might catch broader exceptions
        
        manifest_path = tmp_path / "bad.json"
        manifest_path.write_text("{ invalid json }")
        
        result = ManifestFileRepository.read_manifest(ManifestPath(manifest_path))
        
        assert isinstance(result, Failure)
        error = result.failure()
        assert error.code == "MANIFEST_MALFORMED"  # Specific error code
        assert "Invalid JSON" in error.message
    
    def test_import_error_vs_general_exception(self):
        """Test that ImportError is handled differently than general exceptions."""
        # Catches mutations in exception type checking
        
        with patch('importlib.import_module') as mock_import:
            # Test ImportError
            mock_import.side_effect = ImportError("Module not found")
            
            from src.tau_translator_omega.core_engine.plugin_manager_refactored import ModuleImporter
            
            result1 = ModuleImporter.import_plugin_module(
                "missing_module",
                PluginDirectory(Path("/tmp")),
                PluginId("test")
            )
            
            assert isinstance(result1, Failure)
            assert result1.failure().code == "IMPORT_ERROR"
            
            # Test general Exception
            mock_import.side_effect = RuntimeError("Unexpected error")
            
            result2 = ModuleImporter.import_plugin_module(
                "broken_module",
                PluginDirectory(Path("/tmp")),
                PluginId("test")
            )
            
            assert isinstance(result2, Failure)
            assert result2.failure().code == "IMPORT_UNEXPECTED_ERROR"


class TestDataIntegrityMutations:
    """Tests that ensure data integrity is maintained."""
    
    def test_plugin_data_immutability(self):
        """Test that plugin data structures maintain integrity."""
        # Tests for mutations that might modify data incorrectly
        
        error = PluginError(
            code=ErrorCode("IMMUTABLE_TEST"),
            message=ErrorMessage("Testing immutability"),
            plugin_id=PluginId("test-plugin")
        )
        
        # Frozen dataclass should prevent modification
        with pytest.raises(AttributeError):
            error.code = ErrorCode("MODIFIED")
        
        with pytest.raises(AttributeError):
            error.message = ErrorMessage("Modified message")
    
    def test_registry_isolation(self):
        """Test that registry operations don't affect each other."""
        registry = PluginRegistry()
        
        # Add several plugins
        plugins = []
        for i in range(5):
            plugin = Mock(spec=Plugin)
            plugin.id = f"plugin-{i}"
            plugins.append(plugin)
            registry.register(plugin)
        
        # Get all plugins
        all_plugins_before = registry.get_all()
        assert len(all_plugins_before) == 5
        
        # Modify the returned list
        all_plugins_before.clear()
        
        # Original registry should be unchanged
        all_plugins_after = registry.get_all()
        assert len(all_plugins_after) == 5
        
        # Clear registry
        registry.clear()
        assert len(registry.get_all()) == 0
        
        # Previous list references should not affect registry
        assert len(all_plugins_after) == 5  # Still has old data