# Domain Types: The Castle's Language

## Overview: Speaking Precisely

Domain types are like creating a precise language for your castle. Instead of saying "bring me that thing," you say "bring me the Golden Scepter from the Treasury." Each type has a specific meaning and purpose, preventing confusion and errors. This is the foundation of type-driven development and the Intentional Disclosure Principle.

**File**: `backend/unified/core/domain_types.py`  
**Purpose**: Define precise types for all domain concepts  
**Architecture**: NewType pattern with Result types for error handling

---

## The Type System Foundation

### Creating Domain-Specific Types

```python
from typing import NewType, Union, List, Set, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

# Text types
SourceText = NewType('SourceText', str)
TargetText = NewType('TargetText', str)

# Identification types  
UserId = NewType('UserId', str)
ApiKey = NewType('ApiKey', str)
SessionToken = NewType('SessionToken', str)
KeyId = NewType('KeyId', str)
KeyName = NewType('KeyName', str)
Permission = NewType('Permission', str)
```

These NewTypes are like name tags at a formal event:
- **SourceText**: "Hello, I'm the original text to be translated"
- **TargetText**: "Hello, I'm the translated result"
- **ApiKey**: "Hello, I'm a secret key (handle with care!)"

The beauty is you can't accidentally use a UserId where an ApiKey is expected - the type system catches it!

### Why NewType Instead of Aliases?

```python
# Type alias (weak typing)
UserIdAlias = str  # Can accidentally pass any string

# NewType (strong typing)
UserId = NewType('UserId', str)  # Must explicitly create UserId

# Usage:
user_id = UserId("user123")  # Explicit conversion required
```

---

## The Result Pattern: Success or Failure

### The Railway Track Model

```python
@dataclass(frozen=True)
class Success:
    """Represents a successful operation result."""
    value: Any
    
@dataclass(frozen=True)
class Failure:
    """Represents a failed operation result."""
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None

# Result type is either Success or Failure
Result = Union[Success, Failure]
```

Imagine a train that can only travel on two tracks:
- **Success Track**: Carries cargo (the value)
- **Failure Track**: Carries an explanation of why it couldn't deliver

The `frozen=True` makes these immutable - once a result is created, it can't be changed, ensuring reliability.

### Using Result Types

```python
def divide(a: float, b: float) -> Result[float]:
    """Example of Result pattern usage."""
    if b == 0:
        return Failure("DIVISION_BY_ZERO", "Cannot divide by zero")
    return Success(a / b)

# Usage:
result = divide(10, 2)
if isinstance(result, Success):
    print(f"Answer: {result.value}")  # Answer: 5.0
else:
    print(f"Error: {result.message}")
```

---

## Translation Domain Types

### Translation Status Enum

```python
class TranslationStatus(Enum):
    """Status of a translation operation."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress" 
    COMPLETED = "completed"
    FAILED = "failed"
    CACHED = "cached"
```

Like tracking a package:
- **PENDING**: Order placed, waiting to start
- **IN_PROGRESS**: Package is being prepared
- **COMPLETED**: Delivered successfully
- **FAILED**: Delivery failed
- **CACHED**: Using previous delivery (faster!)

### Translation Direction

```python
class TranslationDirection(Enum):
    """Direction of translation."""
    TO_TAU = "to_tau"          # Natural language to Tau
    TO_TCE = "to_tce"          # Natural language to TCE
    TAU_TO_TCE = "tau_to_tce"  # Tau to TCE
    TCE_TO_TAU = "tce_to_tau"  # TCE to Tau
    
    @property
    def is_to_formal(self) -> bool:
        """Check if translating to formal language."""
        return self in [self.TO_TAU, self.TO_TCE]
    
    @property
    def reverse(self) -> 'TranslationDirection':
        """Get the reverse direction."""
        reverses = {
            self.TO_TAU: self.TO_TCE,
            self.TO_TCE: self.TO_TAU,
            self.TAU_TO_TCE: self.TCE_TO_TAU,
            self.TCE_TO_TAU: self.TAU_TO_TCE
        }
        return reverses.get(self, self)
```

The direction enum includes helper properties - like a compass that not only points north but can tell you which way is south.

### Translation Context

```python
@dataclass
class TranslationContext:
    """Context information for translation requests."""
    preferred_engine: Optional[str] = None
    confidence_threshold: float = 0.7
    include_alternatives: bool = False
    max_alternatives: int = 3
    timeout_seconds: float = 30.0
    options: Dict[str, Any] = field(default_factory=dict)
    
    def with_option(self, key: str, value: Any) -> 'TranslationContext':
        """Create new context with additional option."""
        new_options = self.options.copy()
        new_options[key] = value
        return TranslationContext(
            preferred_engine=self.preferred_engine,
            confidence_threshold=self.confidence_threshold,
            include_alternatives=self.include_alternatives,
            max_alternatives=self.max_alternatives,
            timeout_seconds=self.timeout_seconds,
            options=new_options
        )
```

Context is like instructions with a package:
- "Prefer FedEx" (preferred_engine)
- "Must be 70% sure it's correct" (confidence_threshold)
- "Include other options" (include_alternatives)

The `with_option` method creates a new context with added options - immutability pattern!

---

## Pattern Domain Types

### Pattern Components

```python
PatternId = NewType('PatternId', str)
PatternName = NewType('PatternName', str)
PatternFilePath = NewType('PatternFilePath', str)
PatternSetName = NewType('PatternSetName', str)

class PatternType(Enum):
    """Type of pattern for categorization."""
    TRANSLATION = "translation"
    VALIDATION = "validation"
    NORMALIZATION = "normalization"
    EXTRACTION = "extraction"

@dataclass
class PatternMetadata:
    """Metadata about a pattern."""
    created_at: datetime
    updated_at: datetime
    version: str
    tags: Set[str]
    author: str
    usage_count: int = 0
    success_rate: float = 1.0
```

Patterns are like recipes in our cookbook:
- **PatternId**: Recipe number
- **PatternType**: Is it for main course, dessert, etc.?
- **PatternMetadata**: Who wrote it, when, how popular

### The Pattern Class

```python
@dataclass
class Pattern:
    """A translation or transformation pattern."""
    pattern_id: PatternId
    name: PatternName
    pattern_type: PatternType
    source_pattern: re.Pattern  # Compiled regex
    target_template: str
    description: str
    examples: List[Tuple[str, str]]  # (input, output) pairs
    metadata: PatternMetadata
    
    def apply(self, text: str) -> Optional[str]:
        """Apply pattern to text."""
        match = self.source_pattern.search(text)
        if match:
            # Use groups in replacement
            return self.source_pattern.sub(self.target_template, text)
        return None
    
    @property
    def complexity(self) -> int:
        """Estimate pattern complexity."""
        # Count regex special characters as complexity indicator
        special_chars = r'.*+?{}[]()|\\'
        return sum(1 for char in self.source_pattern.pattern if char in special_chars)
```

The Pattern class includes:
- **apply**: Actually use the recipe
- **complexity**: How difficult is this recipe? (More regex symbols = more complex)

---

## Authentication Domain Types

### API Key Management

```python
@dataclass
class ApiKeyRecord:
    """Complete API key record for storage."""
    key_id: KeyId
    user_id: UserId
    key_name: KeyName
    key_hash: str  # Never store actual key!
    permissions: Set[Permission]
    created_at: datetime
    last_used: Optional[datetime]
    is_active: bool
    
    def has_permission(self, required: Permission) -> bool:
        """Check if key has specific permission."""
        return required in self.permissions or self._has_wildcard_permission(required)
    
    def _has_wildcard_permission(self, required: Permission) -> bool:
        """Check wildcard permissions like 'admin:*'."""
        required_str = str(required)
        for perm in self.permissions:
            perm_str = str(perm)
            if perm_str.endswith(':*'):
                prefix = perm_str[:-2]
                if required_str.startswith(prefix + ':'):
                    return True
        return False
```

API keys are like castle keys:
- **key_hash**: We store the key's impression, not the key itself
- **permissions**: Which doors this key can open
- **has_permission**: Smart checking including master keys (wildcards)

### Session Information

```python
@dataclass
class SessionInfo:
    """Information about an active session."""
    session_token: SessionToken
    user_id: UserId
    created_at: datetime
    expires_at: datetime
    metadata: Dict[str, Any]
    
    @property
    def is_expired(self) -> bool:
        """Check if session has expired."""
        return datetime.utcnow() > self.expires_at
    
    @property
    def time_remaining(self) -> timedelta:
        """Get time until expiration."""
        return max(self.expires_at - datetime.utcnow(), timedelta(0))
```

Sessions are like temporary visitor passes:
- **is_expired**: Has the pass expired?
- **time_remaining**: How long until it expires?

---

## Cache Domain Types

### Cache Key System

```python
CacheKey = NewType('CacheKey', str)

@dataclass
class CacheEntry:
    """Entry in the cache system."""
    key: CacheKey
    value: Any
    created_at: datetime
    expires_at: Optional[datetime]
    hit_count: int = 0
    
    @property
    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    @property
    def age(self) -> timedelta:
        """Get age of cache entry."""
        return datetime.utcnow() - self.created_at
    
    def record_hit(self) -> None:
        """Record a cache hit."""
        self.hit_count += 1
```

Cache entries are like library book reservations:
- **expires_at**: When the reservation expires
- **hit_count**: How many times someone asked for this book
- **age**: How long it's been reserved

---

## Event System Types

### Event Infrastructure

```python
class EventType(Enum):
    """Types of system events."""
    # Authentication events
    API_KEY_CREATED = "auth.api_key.created"
    API_KEY_REVOKED = "auth.api_key.revoked"
    SESSION_CREATED = "auth.session.created"
    SESSION_EXPIRED = "auth.session.expired"
    
    # Translation events
    TRANSLATION_STARTED = "translation.started"
    TRANSLATION_COMPLETED = "translation.completed"
    TRANSLATION_FAILED = "translation.failed"
    
    # Pattern events
    PATTERN_LOADED = "pattern.loaded"
    PATTERN_UPDATED = "pattern.updated"
    PATTERN_SET_LOADED = "pattern.set_loaded"
    
    # Cache events
    CACHE_HIT = "cache.hit"
    CACHE_MISS = "cache.miss"
    CACHE_EXPIRED = "cache.expired"

@dataclass
class Event:
    """System event for event-driven architecture."""
    type: EventType
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source: Optional[str] = None
    
    def matches_pattern(self, pattern: str) -> bool:
        """Check if event type matches wildcard pattern."""
        import fnmatch
        return fnmatch.fnmatch(self.type.value, pattern)
```

Events are like castle announcements:
- **type**: What kind of announcement
- **data**: The details
- **timestamp**: When it was announced
- **matches_pattern**: Can filter announcements by pattern

---

## Type Safety Benefits

### Preventing Errors at Compile Time

```python
# Without domain types - error prone
def authenticate(key: str, token: str) -> bool:
    # Easy to mix up parameters!
    pass

# With domain types - self-documenting and safe
def authenticate(api_key: ApiKey, session_token: SessionToken) -> bool:
    # Cannot accidentally swap parameters
    pass

# This would cause a type error:
# authenticate(session_token, api_key)  # Type checker catches this!
```

### Self-Documenting Code

```python
# Unclear
def process(text1: str, text2: str, direction: str) -> str:
    pass

# Crystal clear
def translate(
    source: SourceText,
    target: TargetText, 
    direction: TranslationDirection
) -> Result[TranslationResult]:
    pass
```

---

## Summary

The domain types system provides:

1. **Type Safety**: Catch errors before runtime
2. **Self-Documentation**: Types explain purpose
3. **Domain Modeling**: Code reflects business concepts
4. **Error Handling**: Result pattern for explicit success/failure
5. **Immutability**: Frozen dataclasses prevent accidental mutation

Key patterns:
- **NewType**: Create distinct types from primitives
- **Result Pattern**: Explicit error handling without exceptions
- **Enums**: Constrain values to valid options
- **Dataclasses**: Structured data with helper methods
- **Properties**: Computed values that stay fresh

This type system forms the foundation of a robust, maintainable application where the compiler helps prevent errors and the code clearly expresses business intent.