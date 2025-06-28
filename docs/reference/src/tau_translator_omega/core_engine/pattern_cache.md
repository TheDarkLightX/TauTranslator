Module src.tau_translator_omega.core_engine.pattern_cache
=========================================================
Pattern cache for compiled regex patterns.
Provides efficient caching and reuse of compiled regex patterns.

Author: DarkLightX / Dana Edwards

Functions
---------

`clear_cache()`
:   Clear the global pattern cache.

`get_cache_stats() ‑> Dict[str, int]`
:   Get statistics from the global pattern cache.

`get_pattern(pattern_str: str, flags: int = 0) ‑> Pattern`
:   Get a compiled regex pattern using the global cache.
    
    Args:
        pattern_str: The regex pattern string
        flags: Optional regex flags
        
    Returns:
        Compiled regex pattern

`precompile_patterns(patterns: Dict[str, str], flags: int = 0)`
:   Precompile patterns using the global cache.

Classes
-------

`PatternCache(max_size: int = 1024)`
:   Thread-safe cache for compiled regex patterns.
    
    This cache prevents redundant compilation of regex patterns,
    which improves performance especially for frequently used patterns.
    
    Initialize the pattern cache.
    
    Args:
        max_size: Maximum number of patterns to cache (default: 1024)

    ### Methods

    `clear(self)`
    :   Clear all cached patterns.

    `get_pattern(self, pattern_str: str, flags: int = 0) ‑> Pattern`
    :   Get a compiled regex pattern from cache or compile and cache it.
        
        Args:
            pattern_str: The regex pattern string
            flags: Optional regex flags (e.g., re.IGNORECASE)
            
        Returns:
            Compiled regex pattern

    `get_stats(self) ‑> Dict[str, int]`
    :   Get cache statistics.
        
        Returns:
            Dictionary with cache statistics

    `precompile_patterns(self, patterns: Dict[str, str], flags: int = 0)`
    :   Precompile a dictionary of patterns for better startup performance.
        
        Args:
            patterns: Dictionary mapping pattern names to pattern strings
            flags: Optional regex flags to apply to all patterns