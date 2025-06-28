Module src.tau_translator_omega.core_engine.utils.lazy_loader
=============================================================
Lazy Loading System for Plugins and Grammar Files
================================================

Implements on-demand loading to improve startup performance.

Author: DarkLightX / Dana Edwards

Classes
-------

`LazyGrammarLoader(grammar_dir: str, max_cache_size: int = 10)`
:   Lazy loader for grammar files.
    
    Features:
    - On-demand grammar loading
    - Caching of loaded grammars
    - Thread-safe loading
    - Memory management with eviction
    
    Initialize lazy grammar loader.
    
    Args:
        grammar_dir: Directory containing grammar files
        max_cache_size: Maximum grammars to keep in memory

    ### Methods

    `clear_cache(self) ‑> None`
    :   Clear the grammar cache.

    `get_grammar(self, name: str) ‑> str | None`
    :   Get grammar content by name, loading if necessary.
        
        Args:
            name: Grammar name (without extension)
            
        Returns:
            Grammar content or None if not found

    `get_stats(self) ‑> Dict[str, Any]`
    :   Get loader statistics.

    `preload(self, names: List[str]) ‑> None`
    :   Preload specific grammars.
        
        Args:
            names: List of grammar names to preload

`LazyLoaderManager(config: Dict[str, Any])`
:   Central manager for all lazy loading.
    
    Coordinates grammar and plugin loading with shared configuration.
    
    Initialize lazy loader manager.
    
    Args:
        config: Configuration dictionary

    ### Methods

    `get_stats(self) ‑> Dict[str, Any]`
    :   Get comprehensive loading statistics.

`LazyPluginLoader(plugin_dirs: List[str])`
:   Lazy loader for plugins.
    
    Features:
    - On-demand plugin loading
    - Dependency resolution
    - Validation before loading
    - Plugin lifecycle management
    
    Initialize lazy plugin loader.
    
    Args:
        plugin_dirs: List of directories to scan for plugins

    ### Methods

    `get_available_plugins(self) ‑> List[str]`
    :   Get list of available plugin IDs.

    `get_loaded_plugins(self) ‑> List[str]`
    :   Get list of loaded plugin IDs.

    `get_plugin(self, plugin_id: str) ‑> Any | None`
    :   Get plugin by ID, loading if necessary.
        
        Args:
            plugin_id: Plugin identifier
            
        Returns:
            Plugin instance or None if not found

    `get_stats(self) ‑> Dict[str, Any]`
    :   Get loader statistics.

    `load_all(self) ‑> None`
    :   Load all available plugins.

    `unload_plugin(self, plugin_id: str) ‑> bool`
    :   Unload a plugin.
        
        Args:
            plugin_id: Plugin identifier
            
        Returns:
            True if unloaded, False otherwise