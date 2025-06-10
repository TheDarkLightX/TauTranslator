# Pattern Loader: The Castle's Library System

## Overview: The Master Librarian

The Pattern Loader is like a master librarian managing a vast collection of transformation recipes (patterns). It organizes, caches, and retrieves patterns from various sources - files, databases, or memory. Using the Repository pattern and dependency injection, it remains agnostic about where patterns are stored while providing fast, thread-safe access.

**File**: `backend/unified/core/pattern_loader.py`  
**Purpose**: Manages loading, caching, and retrieval of translation patterns  
**Architecture**: Repository pattern with caching and event-driven updates

---

## The Library Structure (Class Design)

### The Head Librarian: PatternLoader

```python
class PatternLoader:
    """
    Loads and manages translation patterns from various sources.
    Rule 3: Uses domain types for pattern management.
    Rule 4: Storage details hidden behind repository interface.
    """
    
    def __init__(
        self,
        pattern_repository: IPatternRepository,
        cache_repository: Optional[ICacheRepository] = None,
        event_bus: Optional[IEventBus] = None
    ):
        """Initialize with injected dependencies."""
        self.pattern_repository = pattern_repository
        self.cache = cache_repository or InMemoryCacheRepository()
        self.event_bus = event_bus or InMemoryEventBus()
        self.logger = logging.getLogger(__name__)
        
        # Thread safety
        self._lock = asyncio.Lock()
        self._pattern_cache: Dict[PatternId, Pattern] = {}
        
        # Subscribe to events
        if self.event_bus:
            self.event_bus.subscribe(
                EventType.PATTERN_UPDATED,
                self._handle_pattern_updated
            )
```

The initialization is like setting up a library:
1. **Repository**: Where the books (patterns) are physically stored
2. **Cache**: Quick-access shelves for popular books
3. **Event Bus**: The announcement system ("New book arrived!")
4. **Lock**: Only one person can reorganize shelves at a time

The event subscription means whenever a pattern is updated elsewhere, the librarian is notified to refresh their catalog.

---

## Pattern Loading: The Acquisition Process

### Loading Patterns from Files

```python
async def load_patterns_from_file_async(
    self,
    file_path: PatternFilePath,
    pattern_type: PatternType = PatternType.TRANSLATION
) -> Result[List[Pattern]]:
    """
    Load patterns from a file.
    Rule 1: Async operation explicitly named.
    Rule 2: Orchestrates file loading process.
    """
    try:
        # Check cache first
        cache_key = CacheKey(f"file_patterns_{file_path}_{pattern_type}")
        cached = await self._check_cache_async(cache_key)
        if isinstance(cached, Success):
            return cached
```

The librarian first checks if they've already cataloged this file - why read it again if we already know what's in it?

```python
        # Validate file path
        if not os.path.exists(file_path):
            return Failure("FILE_NOT_FOUND", f"Pattern file not found: {file_path}")
        
        # Load file content
        async with aiofiles.open(file_path, 'r') as f:
            content = await f.read()
        
        # Parse patterns based on file format
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext == '.json':
            patterns = await self._parse_json_patterns_async(content, pattern_type)
        elif file_ext == '.yaml' or file_ext == '.yml':
            patterns = await self._parse_yaml_patterns_async(content, pattern_type)
        elif file_ext == '.csv':
            patterns = await self._parse_csv_patterns_async(content, pattern_type)
        else:
            return Failure("UNSUPPORTED_FORMAT", f"Unsupported file format: {file_ext}")
```

Like a librarian who can read different languages:
- JSON: Modern structured format
- YAML: Human-friendly format
- CSV: Simple tabular format

### Parsing JSON Patterns

```python
async def _parse_json_patterns_async(
    self,
    content: str,
    pattern_type: PatternType
) -> Result[List[Pattern]]:
    """Parse patterns from JSON content."""
    try:
        data = json.loads(content)
        patterns = []
        
        # Handle different JSON structures
        if isinstance(data, dict) and "patterns" in data:
            pattern_list = data["patterns"]
        elif isinstance(data, list):
            pattern_list = data
        else:
            return Failure("INVALID_FORMAT", "JSON must contain 'patterns' key or be a list")
        
        # Convert to Pattern objects
        for item in pattern_list:
            pattern = self._create_pattern_from_dict(item, pattern_type)
            if isinstance(pattern, Success):
                patterns.append(pattern.value)
```

The parsing process is like translating a foreign catalog:
1. Decode the JSON format
2. Find where patterns are stored (might be nested)
3. Convert each entry to a Pattern object

---

## Pattern Creation: The Cataloging System

### Creating Pattern Objects

```python
def _create_pattern_from_dict(
    self,
    data: Dict[str, Any],
    pattern_type: PatternType
) -> Result[Pattern]:
    """Create a Pattern object from dictionary data."""
    try:
        # Validate required fields
        if "pattern" not in data:
            return Failure("MISSING_FIELD", "Pattern must have 'pattern' field")
        
        # Compile regex pattern
        try:
            compiled_pattern = re.compile(data["pattern"])
        except re.error as e:
            return Failure("INVALID_REGEX", f"Invalid regex pattern: {e}")
        
        # Create Pattern object
        pattern = Pattern(
            pattern_id=PatternId(data.get("id", str(uuid.uuid4()))),
            name=PatternName(data.get("name", "Unnamed Pattern")),
            pattern_type=pattern_type,
            source_pattern=compiled_pattern,
            target_template=data.get("replacement", ""),
            description=data.get("description", ""),
            examples=data.get("examples", []),
            metadata=PatternMetadata(
                created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
                updated_at=datetime.fromisoformat(data.get("updated_at", datetime.now().isoformat())),
                version=data.get("version", "1.0"),
                tags=set(data.get("tags", [])),
                author=data.get("author", "unknown")
            )
        )
```

Creating a pattern is like creating a detailed library card:
- **ID**: Unique catalog number
- **Name**: Human-readable title
- **Pattern**: The actual regex (compiled for efficiency)
- **Metadata**: When created, by whom, version info

### Pattern Validation

```python
        # Validate pattern works
        test_result = self._validate_pattern(pattern)
        if isinstance(test_result, Failure):
            return test_result
        
        return Success(pattern)
        
    except Exception as e:
        self.logger.error(f"Failed to create pattern: {e}")
        return Failure("PATTERN_CREATION_ERROR", str(e))

def _validate_pattern(self, pattern: Pattern) -> Result[None]:
    """Validate that a pattern is well-formed and functional."""
    try:
        # Test pattern matching
        test_text = "test input"
        match = pattern.source_pattern.search(test_text)
        
        # If pattern has groups, ensure replacement template is valid
        if pattern.source_pattern.groups > 0:
            if not pattern.target_template:
                return Failure("INVALID_TEMPLATE", "Pattern has groups but no replacement template")
        
        return Success(None)
    except Exception as e:
        return Failure("PATTERN_VALIDATION_ERROR", str(e))
```

Validation ensures patterns actually work - like testing a recipe before adding it to the cookbook.

---

## Caching System: The Quick-Access Shelves

### Cache Management

```python
async def _check_cache_async(self, cache_key: CacheKey) -> Result[Any]:
    """Check cache for stored result."""
    if not self.cache:
        return Failure("CACHE_DISABLED", "Cache not available")
    
    try:
        cached_value = await self.cache.get_async(cache_key)
        if cached_value is not None:
            self.logger.debug(f"Cache hit for key: {cache_key}")
            self.event_bus.publish(Event(
                type=EventType.CACHE_HIT,
                data={"key": str(cache_key)}
            ))
            return Success(cached_value)
        
        return Failure("CACHE_MISS", "No cached value found")
    except Exception as e:
        self.logger.warning(f"Cache check failed: {e}")
        return Failure("CACHE_ERROR", str(e))
```

The cache check is like looking for a book on the "frequently accessed" shelf before going to the main stacks.

### Storing in Cache

```python
async def _store_in_cache_async(
    self,
    cache_key: CacheKey,
    value: Any,
    ttl_seconds: Optional[int] = None
) -> None:
    """Store value in cache."""
    if not self.cache:
        return
    
    try:
        await self.cache.set_async(
            key=cache_key,
            value=value,
            ttl_seconds=ttl_seconds or 3600  # Default 1 hour
        )
        self.logger.debug(f"Cached value for key: {cache_key}")
    except Exception as e:
        self.logger.warning(f"Failed to cache value: {e}")
```

Caching is like putting popular books on easy-reach shelves with a note about when to return them to the main collection.

---

## Pattern Sets: The Collection Management

### Loading Pattern Sets

```python
async def load_pattern_set_async(
    self,
    set_name: PatternSetName
) -> Result[PatternSet]:
    """
    Load a named set of patterns.
    Pattern sets group related patterns together.
    """
    async with self._lock:
        # Check memory cache
        cache_key = CacheKey(f"pattern_set_{set_name}")
        if cache_key in self._pattern_cache:
            return Success(self._pattern_cache[cache_key])
        
        # Load from repository
        result = await self.pattern_repository.get_pattern_set_async(set_name)
        if isinstance(result, Failure):
            return result
        
        pattern_set = result.value
        
        # Cache in memory
        self._pattern_cache[cache_key] = pattern_set
        
        # Publish event
        self.event_bus.publish(Event(
            type=EventType.PATTERN_SET_LOADED,
            data={
                "set_name": str(set_name),
                "pattern_count": len(pattern_set.patterns)
            }
        ))
        
        return Success(pattern_set)
```

Pattern sets are like themed collections - "Medieval Transformations" or "Scientific Notations" - grouped for easy access.

---

## Event Handling: The Announcement System

### Handling Pattern Updates

```python
async def _handle_pattern_updated(self, event: Event) -> None:
    """Handle pattern update events."""
    try:
        pattern_id = PatternId(event.data.get("pattern_id"))
        
        # Invalidate caches
        async with self._lock:
            # Remove from memory cache
            keys_to_remove = [
                k for k in self._pattern_cache 
                if str(pattern_id) in str(k)
            ]
            for key in keys_to_remove:
                del self._pattern_cache[key]
        
        # Clear distributed cache entries
        if self.cache:
            await self.cache.delete_pattern_async(f"*{pattern_id}*")
        
        self.logger.info(f"Cleared caches for updated pattern: {pattern_id}")
        
    except Exception as e:
        self.logger.error(f"Failed to handle pattern update: {e}")
```

When a pattern is updated, the librarian must:
1. Remove old copies from quick-access shelves
2. Clear any cached information
3. Ensure next access gets fresh data

---

## Advanced Features

### Bulk Operations

```python
async def load_all_patterns_async(
    self,
    pattern_type: Optional[PatternType] = None
) -> Result[List[Pattern]]:
    """
    Load all available patterns of a given type.
    Rule 2: Orchestrates bulk loading with progress tracking.
    """
    patterns = []
    errors = []
    
    # Get all pattern sources from repository
    sources_result = await self.pattern_repository.list_pattern_sources_async()
    if isinstance(sources_result, Failure):
        return sources_result
    
    # Load from each source with progress tracking
    total_sources = len(sources_result.value)
    for idx, source in enumerate(sources_result.value):
        # Publish progress event
        self.event_bus.publish(Event(
            type=EventType.LOADING_PROGRESS,
            data={
                "current": idx + 1,
                "total": total_sources,
                "source": str(source)
            }
        ))
```

Bulk loading is like doing a complete library inventory - systematic and trackable.

### Thread-Safe Operations

```python
async def refresh_patterns_async(self) -> Result[None]:
    """
    Refresh all cached patterns from their sources.
    Thread-safe operation using async lock.
    """
    async with self._lock:
        self.logger.info("Refreshing all patterns...")
        
        # Clear all caches
        self._pattern_cache.clear()
        if self.cache:
            await self.cache.clear_async()
        
        # Reload commonly used pattern sets
        common_sets = ["basic_translation", "advanced_translation", "domain_specific"]
        for set_name in common_sets:
            await self.load_pattern_set_async(PatternSetName(set_name))
        
        self.event_bus.publish(Event(
            type=EventType.PATTERNS_REFRESHED,
            data={"timestamp": datetime.now().isoformat()}
        ))
        
        return Success(None)
```

The async lock ensures only one refresh happens at a time - like closing the library for inventory.

---

## Pattern Search: The Card Catalog

```python
async def search_patterns_async(
    self,
    query: str,
    pattern_type: Optional[PatternType] = None,
    tags: Optional[Set[str]] = None
) -> Result[List[Pattern]]:
    """
    Search for patterns matching criteria.
    Supports text search and tag filtering.
    """
    # Search in repository
    search_result = await self.pattern_repository.search_patterns_async(
        query=query,
        pattern_type=pattern_type,
        tags=tags
    )
    
    if isinstance(search_result, Failure):
        return search_result
    
    patterns = search_result.value
    
    # Rank results by relevance
    ranked_patterns = self._rank_search_results(patterns, query)
    
    return Success(ranked_patterns)

def _rank_search_results(
    self,
    patterns: List[Pattern],
    query: str
) -> List[Pattern]:
    """Rank patterns by relevance to query."""
    query_lower = query.lower()
    
    def relevance_score(pattern: Pattern) -> float:
        score = 0.0
        
        # Name match (highest weight)
        if query_lower in pattern.name.lower():
            score += 10.0
        
        # Description match
        if query_lower in pattern.description.lower():
            score += 5.0
        
        # Tag match
        for tag in pattern.metadata.tags:
            if query_lower in tag.lower():
                score += 3.0
        
        # Example match
        for example in pattern.examples:
            if query_lower in example.lower():
                score += 1.0
        
        return score
    
    return sorted(patterns, key=relevance_score, reverse=True)
```

The search system is like a smart card catalog that not only finds books but ranks them by relevance.

---

## Summary

The Pattern Loader demonstrates sophisticated design patterns:

1. **Repository Pattern**: Abstracts storage details behind interfaces
2. **Caching Strategy**: Multi-level caching for performance
3. **Event-Driven Updates**: Reactive cache invalidation
4. **Thread Safety**: Async locks prevent race conditions
5. **Type Safety**: Domain types throughout
6. **Search and Ranking**: Intelligent pattern discovery

Key features:
- **Format Agnostic**: Loads from JSON, YAML, CSV
- **Performance Optimized**: Caching and lazy loading
- **Thread-Safe**: Concurrent access handling
- **Event-Driven**: Reactive to system changes
- **Search Capable**: Find patterns by various criteria

The Pattern Loader acts as an intelligent librarian, managing a dynamic collection of transformation patterns while ensuring fast access, consistency, and reliability - essential for a high-performance translation system.