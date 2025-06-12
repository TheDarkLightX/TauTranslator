"""
Refactored TGF Grammar Loader following the Intentional Disclosure Principle.

This module orchestrates TGF grammar loading operations using the clean architecture layers:
- Domain: TGF services (business logic)
- Infrastructure: TGF infrastructure (I/O operations)
- All methods follow IDP Rule 2 (≤10 lines).

Copyright: DarkLightX / Dana Edwards
"""

from typing import Dict, List, Optional, Any
from returns.result import Result, Success, Failure

from ..domain.tgf_service import (
    TGFParsingService, LarkConversionService, GrammarManagementService,
    ConfigManagementService
)
from ..domain.tgf_types import (
    TGFFilename, GrammarLoaderConfig, LoadedGrammar, GrammarLoadingState,
    LarkGrammar, LarkConversionResult
)
from ..infrastructure.tgf_infrastructure import (
    DirectoryValidator, TGFFileScanner, SystemPathResolver
)


class TGFGrammarLoaderRefactored:
    """Orchestrates TGF grammar loading and management operations."""
    
    def __init__(self, grammar_dir: Optional[str] = None, config_file: Optional[str] = None):
        self._config = self._create_loader_config(grammar_dir, config_file)
        self._grammar_service = GrammarManagementService(self._config)
        self._config_service = ConfigManagementService(self._config)
        self._state: Optional[GrammarLoadingState] = None
    
    def load_all_grammars_async(self) -> Result[GrammarLoadingState, str]:
        """Load all grammars from configuration and directory scan."""
        # Validate directory structure
        validation_result = self._validate_directories()
        if isinstance(validation_result, Failure):
            return validation_result
        
        # Load configuration
        config_result = self._config_service.load_grammar_configs()
        if isinstance(config_result, Failure):
            return Failure(config_result.failure())
        
        # Load grammars
        grammars = {}
        configs = config_result.unwrap()
        
        for config in configs:
            grammar_result = self._grammar_service.load_single_grammar(config.filename)
            if isinstance(grammar_result, Success):
                grammar = grammar_result.unwrap().with_active_status(config.is_active)
                grammars[str(config.filename)] = grammar
        
        self._state = self._grammar_service.create_loading_state(grammars)
        return Success(self._state)
    
    def load_grammar_file_async(self, filename: str) -> Result[LoadedGrammar, str]:
        """Load a specific grammar file."""
        result = self._grammar_service.load_single_grammar(TGFFilename(filename))
        if isinstance(result, Success):
            grammar = result.unwrap()
            self._update_state_with_grammar(grammar)
            return Success(grammar)
        
        return result
    
    def get_active_grammar(self) -> Optional[LoadedGrammar]:
        """Get the currently active grammar."""
        if self._state and self._state.has_active_grammar:
            return self._state.active_grammar
        return None
    
    def set_active_grammar_async(self, filename: str) -> Result[bool, str]:
        """Set a grammar as active and update configuration."""
        if not self._state:
            return Failure("No grammars loaded")
        
        # Update grammar states
        result = self._grammar_service.activate_grammar(
            self._state.loaded_grammars, TGFFilename(filename)
        )
        if isinstance(result, Failure):
            return Failure(result.failure())
        
        # Update internal state
        updated_grammars = result.unwrap()
        self._state = self._grammar_service.create_loading_state(updated_grammars)
        
        # Save configuration
        save_result = self._config_service.save_grammar_state(self._state)
        if isinstance(save_result, Failure):
            return Failure(save_result.failure())
        
        return Success(True)
    
    def get_grammar_for_parser_async(self) -> Result[str, str]:
        """Get active grammar in Lark format for parser use."""
        if not self._state:
            return Failure("No grammars loaded")
        
        result = self._grammar_service.get_active_grammar_for_parser(self._state)
        if isinstance(result, Success):
            return Success(str(result.unwrap()))
        
        return Failure(result.failure())
    
    def convert_grammar_to_lark_async(self, filename: str) -> Result[LarkConversionResult, str]:
        """Convert specific grammar to Lark format."""
        if not self._state or filename not in self._state.loaded_grammars:
            return Failure(f"Grammar not found: {filename}")
        
        grammar = self._state.loaded_grammars[filename]
        conversion_service = LarkConversionService()
        result = conversion_service.convert_to_lark(grammar)
        
        return Success(result)
    
    def get_loading_state(self) -> Optional[GrammarLoadingState]:
        """Get current loading state."""
        return self._state
    
    def get_engine_info(self) -> Dict[str, Any]:
        """Get comprehensive engine information."""
        if not self._state:
            return {"engine_type": "tgf_loader", "loaded": False}
        
        return {
            "engine_type": "tgf_loader",
            "loaded": True,
            **self._state.to_summary_dict(),
            "config": {
                "grammar_directory": self._config.grammar_directory,
                "config_file": self._config.config_file_path
            }
        }
    
    def scan_available_grammars_async(self) -> Result[List[str], str]:
        """Scan directory for available grammar files."""
        scan_result = TGFFileScanner.scan_grammar_directory(self._config.grammar_directory)
        if isinstance(scan_result, Success):
            filenames = scan_result.unwrap()
            return Success([str(filename) for filename in filenames])
        
        return Failure(scan_result.failure())
    
    # Private helper methods (all ≤10 lines following IDP Rule 2)
    
    def _create_loader_config(self, grammar_dir: Optional[str], config_file: Optional[str]) -> GrammarLoaderConfig:
        """Create loader configuration with path resolution."""
        if grammar_dir and config_file:
            return GrammarLoaderConfig(
                grammar_directory=grammar_dir,
                config_file_path=config_file
            )
        
        return GrammarLoaderConfig.create_default()
    
    def _validate_directories(self) -> Result[None, str]:
        """Validate required directories exist and are accessible."""
        # Validate grammar directory
        grammar_result = DirectoryValidator.validate_grammar_directory(
            self._config.grammar_directory
        )
        if isinstance(grammar_result, Failure):
            return Failure(grammar_result.failure())
        
        # Validate config directory
        config_result = DirectoryValidator.validate_config_directory(
            self._config.config_file_path
        )
        if isinstance(config_result, Failure):
            return Failure(config_result.failure())
        
        return Success(None)
    
    def _update_state_with_grammar(self, grammar: LoadedGrammar) -> None:
        """Update internal state with new grammar."""
        if not self._state:
            grammars = {str(grammar.filename): grammar}
            self._state = self._grammar_service.create_loading_state(grammars)
        else:
            updated_grammars = dict(self._state.loaded_grammars)
            updated_grammars[str(grammar.filename)] = grammar
            self._state = self._grammar_service.create_loading_state(updated_grammars)


class TGFGrammarLoaderFactory:
    """Factory for creating TGF grammar loader instances."""
    
    @staticmethod
    def create_loader(grammar_dir: Optional[str] = None, 
                     config_file: Optional[str] = None) -> TGFGrammarLoaderRefactored:
        """Create a new TGF grammar loader instance."""
        return TGFGrammarLoaderRefactored(grammar_dir, config_file)
    
    @staticmethod
    def create_default_loader() -> TGFGrammarLoaderRefactored:
        """Create loader with default configuration."""
        return TGFGrammarLoaderRefactored()
    
    @staticmethod
    async def create_initialized_loader_async(
        grammar_dir: Optional[str] = None,
        config_file: Optional[str] = None
    ) -> Result[TGFGrammarLoaderRefactored, str]:
        """Create and initialize a TGF grammar loader."""
        loader = TGFGrammarLoaderFactory.create_loader(grammar_dir, config_file)
        
        load_result = loader.load_all_grammars_async()
        if isinstance(load_result, Success):
            return Success(loader)
        else:
            return Failure(load_result.failure())


class LegacyTGFLoaderAdapter:
    """Adapter to maintain compatibility with existing code."""
    
    def __init__(self, refactored_loader: TGFGrammarLoaderRefactored):
        self._loader = refactored_loader
    
    def load_grammar_config(self) -> List[Dict[str, Any]]:
        """Legacy grammar config loading (synchronous)."""
        state = self._loader.get_loading_state()
        if state:
            return state.get_grammar_list()
        return []
    
    def load_all_grammars(self) -> int:
        """Legacy load all grammars (synchronous)."""
        result = self._loader.load_all_grammars_async()
        if isinstance(result, Success):
            return result.unwrap().total_loaded
        return 0
    
    def load_grammar_file(self, filename: str) -> Optional[Dict[str, Any]]:
        """Legacy single grammar loading (synchronous)."""
        result = self._loader.load_grammar_file_async(filename)
        if isinstance(result, Success):
            grammar = result.unwrap()
            return grammar.get_display_info()
        return None
    
    def get_active_grammar(self) -> Optional[Dict[str, Any]]:
        """Get active grammar info (legacy format)."""
        grammar = self._loader.get_active_grammar()
        if grammar:
            return grammar.get_display_info()
        return None
    
    def set_active_grammar(self, filename: str) -> bool:
        """Legacy set active grammar (synchronous)."""
        result = self._loader.set_active_grammar_async(filename)
        return isinstance(result, Success) and result.unwrap()
    
    def get_grammar_for_parser(self) -> Optional[str]:
        """Legacy get grammar for parser (synchronous)."""
        result = self._loader.get_grammar_for_parser_async()
        if isinstance(result, Success):
            return result.unwrap()
        return None


# Global instance management for backward compatibility
_global_loader: Optional[TGFGrammarLoaderRefactored] = None

def get_tgf_grammar_loader() -> TGFGrammarLoaderRefactored:
    """Get or create the global TGF grammar loader instance."""
    global _global_loader
    if _global_loader is None:
        _global_loader = TGFGrammarLoaderFactory.create_default_loader()
        # Initialize asynchronously in background
        _global_loader.load_all_grammars_async()
    return _global_loader

def reset_global_loader() -> None:
    """Reset the global loader instance (for testing)."""
    global _global_loader
    _global_loader = None