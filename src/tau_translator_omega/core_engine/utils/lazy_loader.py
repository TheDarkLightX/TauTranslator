"""
Lazy Loading System for Plugins and Grammar Files
================================================

Implements on-demand loading to improve startup performance.

Author: DarkLightX / Dana Edwards
"""

import os
import json
import importlib
from typing import Dict, Optional, Any, List, Callable
from pathlib import Path
import logging
from functools import lru_cache
import threading

logger = logging.getLogger(__name__)


class LazyGrammarLoader:
    """
    Lazy loader for grammar files.
    
    Features:
    - On-demand grammar loading
    - Caching of loaded grammars
    - Thread-safe loading
    - Memory management with eviction
    """
    
    def __init__(self, grammar_dir: str, max_cache_size: int = 10):
        """
        Initialize lazy grammar loader.
        
        Args:
            grammar_dir: Directory containing grammar files
            max_cache_size: Maximum grammars to keep in memory
        """
        self.grammar_dir = Path(grammar_dir)
        self._cache: Dict[str, str] = {}
        self._access_order: List[str] = []
        self._lock = threading.RLock()
        self.max_cache_size = max_cache_size
        self._load_count = 0
        
        # Scan available grammars without loading
        self._available_grammars = self._scan_grammars()
    
    def _scan_grammars(self) -> Dict[str, Path]:
        """Scan for available grammar files without loading them."""
        grammars = {}
        
        if not self.grammar_dir.exists():
            logger.warning(f"Grammar directory does not exist: {self.grammar_dir}")
            return grammars
        
        for file_path in self.grammar_dir.rglob("*.lark"):
            grammar_name = file_path.stem
            grammars[grammar_name] = file_path
            
        for file_path in self.grammar_dir.rglob("*.ebnf"):
            grammar_name = file_path.stem
            grammars[grammar_name] = file_path
            
        logger.info(f"Found {len(grammars)} grammar files")
        return grammars
    
    def get_grammar(self, name: str) -> Optional[str]:
        """
        Get grammar content by name, loading if necessary.
        
        Args:
            name: Grammar name (without extension)
            
        Returns:
            Grammar content or None if not found
        """
        with self._lock:
            # Check cache first
            if name in self._cache:
                # Move to end (most recently used)
                self._access_order.remove(name)
                self._access_order.append(name)
                return self._cache[name]
            
            # Load grammar if available
            if name not in self._available_grammars:
                logger.error(f"Grammar not found: {name}")
                return None
            
            grammar_path = self._available_grammars[name]
            try:
                with open(grammar_path, 'r') as f:
                    content = f.read()
                
                self._load_count += 1
                
                # Add to cache
                self._cache[name] = content
                self._access_order.append(name)
                
                # Evict if cache is full
                if len(self._cache) > self.max_cache_size:
                    self._evict_lru()
                
                logger.debug(f"Loaded grammar: {name}")
                return content
                
            except Exception as e:
                logger.error(f"Failed to load grammar {name}: {e}")
                return None
    
    def _evict_lru(self):
        """Evict least recently used grammar from cache."""
        if self._access_order:
            lru_name = self._access_order.pop(0)
            del self._cache[lru_name]
            logger.debug(f"Evicted grammar from cache: {lru_name}")
    
    def preload(self, names: List[str]) -> None:
        """
        Preload specific grammars.
        
        Args:
            names: List of grammar names to preload
        """
        for name in names:
            self.get_grammar(name)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get loader statistics."""
        with self._lock:
            return {
                'available_grammars': len(self._available_grammars),
                'cached_grammars': len(self._cache),
                'total_loads': self._load_count,
                'cache_size_bytes': sum(len(g) for g in self._cache.values())
            }
    
    def clear_cache(self) -> None:
        """Clear the grammar cache."""
        with self._lock:
            self._cache.clear()
            self._access_order.clear()


class LazyPluginLoader:
    """
    Lazy loader for plugins.
    
    Features:
    - On-demand plugin loading
    - Dependency resolution
    - Validation before loading
    - Plugin lifecycle management
    """
    
    def __init__(self, plugin_dirs: List[str]):
        """
        Initialize lazy plugin loader.
        
        Args:
            plugin_dirs: List of directories to scan for plugins
        """
        self.plugin_dirs = [Path(d) for d in plugin_dirs]
        self._plugins: Dict[str, Any] = {}
        self._manifests: Dict[str, Dict] = {}
        self._lock = threading.RLock()
        self._load_count = 0
        
        # Scan for available plugins
        self._scan_plugins()
    
    def _scan_plugins(self) -> None:
        """Scan for plugin manifests without loading plugins."""
        for plugin_dir in self.plugin_dirs:
            if not plugin_dir.exists():
                continue
                
            for manifest_path in plugin_dir.rglob("plugin.json"):
                try:
                    with open(manifest_path, 'r') as f:
                        manifest = json.load(f)
                    
                    plugin_id = manifest.get('id', manifest_path.parent.name)
                    self._manifests[plugin_id] = {
                        'manifest': manifest,
                        'path': manifest_path.parent,
                        'loaded': False
                    }
                    
                except Exception as e:
                    logger.error(f"Failed to read manifest {manifest_path}: {e}")
        
        logger.info(f"Found {len(self._manifests)} plugins")
    
    def get_plugin(self, plugin_id: str) -> Optional[Any]:
        """
        Get plugin by ID, loading if necessary.
        
        Args:
            plugin_id: Plugin identifier
            
        Returns:
            Plugin instance or None if not found
        """
        with self._lock:
            # Return if already loaded
            if plugin_id in self._plugins:
                return self._plugins[plugin_id]
            
            # Load plugin if available
            if plugin_id not in self._manifests:
                logger.error(f"Plugin not found: {plugin_id}")
                return None
            
            plugin_info = self._manifests[plugin_id]
            
            # Check if already marked as loaded but not in cache
            if plugin_info['loaded']:
                logger.warning(f"Plugin {plugin_id} was loaded but not cached")
                return None
            
            try:
                plugin = self._load_plugin(plugin_info)
                self._plugins[plugin_id] = plugin
                plugin_info['loaded'] = True
                self._load_count += 1
                
                logger.info(f"Loaded plugin: {plugin_id}")
                return plugin
                
            except Exception as e:
                logger.error(f"Failed to load plugin {plugin_id}: {e}")
                plugin_info['loaded'] = True  # Mark as attempted
                return None
    
    def _load_plugin(self, plugin_info: Dict) -> Any:
        """
        Load a plugin from its manifest.
        
        Args:
            plugin_info: Plugin information including manifest and path
            
        Returns:
            Loaded plugin instance
        """
        manifest = plugin_info['manifest']
        plugin_path = plugin_info['path']
        
        # Get entry point
        entry_point = manifest.get('entry_point', 'plugin.py')
        module_name = manifest.get('module_name', 'plugin')
        class_name = manifest.get('class_name', 'Plugin')
        
        # Add plugin directory to Python path temporarily
        import sys
        old_path = sys.path.copy()
        sys.path.insert(0, str(plugin_path))
        
        try:
            # Import module
            module = importlib.import_module(module_name)
            
            # Get plugin class
            plugin_class = getattr(module, class_name)
            
            # Instantiate plugin
            plugin = plugin_class()
            
            # Initialize if needed
            if hasattr(plugin, 'initialize'):
                plugin.initialize(manifest)
            
            return plugin
            
        finally:
            # Restore Python path
            sys.path = old_path
    
    def load_all(self) -> None:
        """Load all available plugins."""
        for plugin_id in list(self._manifests.keys()):
            self.get_plugin(plugin_id)
    
    def get_available_plugins(self) -> List[str]:
        """Get list of available plugin IDs."""
        return list(self._manifests.keys())
    
    def get_loaded_plugins(self) -> List[str]:
        """Get list of loaded plugin IDs."""
        with self._lock:
            return list(self._plugins.keys())
    
    def unload_plugin(self, plugin_id: str) -> bool:
        """
        Unload a plugin.
        
        Args:
            plugin_id: Plugin identifier
            
        Returns:
            True if unloaded, False otherwise
        """
        with self._lock:
            if plugin_id not in self._plugins:
                return False
            
            plugin = self._plugins[plugin_id]
            
            # Call cleanup if available
            if hasattr(plugin, 'cleanup'):
                try:
                    plugin.cleanup()
                except Exception as e:
                    logger.error(f"Error during plugin cleanup: {e}")
            
            # Remove from cache
            del self._plugins[plugin_id]
            
            # Update manifest
            if plugin_id in self._manifests:
                self._manifests[plugin_id]['loaded'] = False
            
            logger.info(f"Unloaded plugin: {plugin_id}")
            return True
    
    def get_stats(self) -> Dict[str, Any]:
        """Get loader statistics."""
        with self._lock:
            return {
                'available_plugins': len(self._manifests),
                'loaded_plugins': len(self._plugins),
                'total_loads': self._load_count
            }


class LazyLoaderManager:
    """
    Central manager for all lazy loading.
    
    Coordinates grammar and plugin loading with shared configuration.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize lazy loader manager.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        
        # Initialize loaders
        grammar_dir = config.get('grammar_dir', 'grammars')
        self.grammar_loader = LazyGrammarLoader(grammar_dir)
        
        plugin_dirs = config.get('plugin_dirs', ['plugins'])
        self.plugin_loader = LazyPluginLoader(plugin_dirs)
        
        # Preload critical resources if specified
        if 'preload' in config:
            self._preload_resources(config['preload'])
    
    def _preload_resources(self, preload_config: Dict[str, List[str]]) -> None:
        """Preload specified resources."""
        if 'grammars' in preload_config:
            self.grammar_loader.preload(preload_config['grammars'])
        
        if 'plugins' in preload_config:
            for plugin_id in preload_config['plugins']:
                self.plugin_loader.get_plugin(plugin_id)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive loading statistics."""
        return {
            'grammars': self.grammar_loader.get_stats(),
            'plugins': self.plugin_loader.get_stats()
        }