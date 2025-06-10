# Authentication Core: The Vault Guardian

## Overview: The Master of Keys

Imagine a medieval castle with a sophisticated vault system. The Authentication Service is the Vault Guardian who manages access to the castle's treasures. They issue special keys (API keys), create temporary passes (sessions), and maintain a ledger of who has access to what. This guardian follows strict protocols to ensure only authorized individuals can enter.

**File**: `backend/unified/core/auth.py`  
**Purpose**: Core authentication business logic with clean architecture  
**Architecture**: Domain-driven design with repository pattern and event system

---

## The Guardian's Chambers (Class Structure)

### The Main Guardian: AuthenticationService
```python
class AuthenticationService:
    """
    Core authentication service implementing business logic.
    Rule 3: Uses domain types for maximum disclosure.
    Rule 4: Infrastructure injected, not created.
    """
    
    def __init__(
        self,
        auth_repository: IAuthenticationRepository,
        event_bus: IEventBus,
        master_password: Optional[str] = None,
        session_expire_hours: int = 24
    ):
        """Initialize with injected dependencies."""
        self.auth_repository = auth_repository
        self.event_bus = event_bus
        self.master_password = master_password or self._generate_default_master()
        self.session_expire_hours = session_expire_hours
        self.logger = logging.getLogger(__name__)
```

**The Appointment Ceremony**: When the Guardian takes office:
1. **Receives the Key Storage** (`auth_repository`): Where to keep the keys
2. **Gets the Communication System** (`event_bus`): How to announce events
3. **Sets the Master Password**: The ultimate key to the kingdom
4. **Defines Session Length**: How long temporary passes last

The Guardian doesn't create these tools - they're provided (dependency injection), making the Guardian adaptable to different castles.

---

## The Key Creation Ceremony

### Creating New API Keys
```python
async def create_api_key_async(
    self,
    user_id: UserId,
    key_name: KeyName,
    permissions: Set[Permission]
) -> Result[ApiKeyCreated]:
    """
    Create a new API key for a user.
    Rule 1: Name explicitly indicates async operation.
    Rule 2: Orchestrates the key creation flow.
    """
    # Validate inputs
    validation = self._validate_key_creation_inputs(user_id, key_name, permissions)
    if isinstance(validation, Failure):
        return validation
```

**The Key Forging Process** begins with validation - like checking if the person requesting the key has proper identification.

```python
    # Generate unique key
    api_key = self._generate_secure_api_key()
    key_hash = self._hash_api_key(api_key)
    
    # Create domain object
    api_key_record = ApiKeyRecord(
        key_id=KeyId(str(uuid.uuid4())),
        user_id=user_id,
        key_name=key_name,
        key_hash=key_hash,
        permissions=permissions,
        created_at=datetime.utcnow(),
        last_used=None,
        is_active=True
    )
```

**Forging the Key**:
1. **Generate Raw Key**: Create a unique, unguessable key
2. **Create Hash**: Like taking a wax impression - store only the impression, not the key
3. **Prepare the Ledger Entry**: Document all key details

```python
    # Persist to repository
    save_result = await self.auth_repository.save_api_key_async(api_key_record)
    if isinstance(save_result, Failure):
        return save_result
    
    # Publish event
    self.event_bus.publish(Event(
        type=EventType.API_KEY_CREATED,
        data={
            "user_id": str(user_id),
            "key_name": str(key_name),
            "permissions": [str(p) for p in permissions]
        }
    ))
```

**Recording and Announcing**:
1. **Store in Vault**: Save the key record securely
2. **Make Announcement**: "A new key has been forged!"
3. **Return the Key**: Give the actual key only to the requester

### The Key Generation Magic
```python
def _generate_secure_api_key(self) -> ApiKey:
    """Generate a cryptographically secure API key."""
    # Use secrets module for cryptographic randomness
    random_bytes = secrets.token_bytes(32)
    
    # Encode as URL-safe base64
    key_string = base64.urlsafe_b64encode(random_bytes).decode('utf-8').rstrip('=')
    
    # Add prefix for easy identification
    return ApiKey(f"sk_{key_string}")
```

**The Cryptographic Forge**:
1. **Gather Entropy**: Use true randomness (32 bytes = 256 bits)
2. **Encode Safely**: Make it URL-friendly
3. **Add Identifier**: Prefix with "sk_" so it's recognizable as a secret key

---

## The Authentication Gates

### Validating API Keys
```python
async def validate_api_key_async(
    self,
    api_key: ApiKey
) -> Result[AuthenticatedUser]:
    """
    Validate an API key and return authenticated user info.
    Rule 1: Async operation clearly indicated.
    """
    # Check key format
    if not self._is_valid_key_format(api_key):
        return Failure("INVALID_KEY_FORMAT", "API key format is invalid")
```

**The Gatekeeper's Check**: Like examining a key before trying it in a lock.

```python
    # Look up all keys and check hashes
    all_keys = await self.auth_repository.get_all_api_keys_async()
    if isinstance(all_keys, Failure):
        return all_keys
    
    # Find matching key by comparing hashes
    key_hash = self._hash_api_key(api_key)
    matching_key = None
    
    for key_record in all_keys.value:
        if secrets.compare_digest(key_record.key_hash, key_hash):
            matching_key = key_record
            break
```

**The Verification Process**:
1. **Retrieve All Keys**: Get all key impressions from the vault
2. **Hash the Presented Key**: Make an impression of the provided key
3. **Compare Securely**: Use `compare_digest` to prevent timing attacks
4. **Find the Match**: Like finding which lock the key fits

### Timing Attack Prevention
```python
if secrets.compare_digest(key_record.key_hash, key_hash):
```

This is crucial security: `compare_digest` takes the same time regardless of where the strings differ, preventing attackers from guessing keys by measuring response times.

---

## Session Management: The Temporary Pass System

### Creating Sessions
```python
async def create_session_async(
    self,
    user_id: UserId,
    metadata: Optional[Dict[str, Any]] = None
) -> Result[SessionCreated]:
    """
    Create a new session for authenticated user.
    Rule 2: Orchestrates session creation flow.
    """
    # Generate session token
    session_token = self._generate_session_token()
    expires_at = datetime.utcnow() + timedelta(hours=self.session_expire_hours)
```

**The Temporary Pass**: Like issuing a day pass at a castle:
1. **Create Unique Token**: Generate an unforgeable pass
2. **Set Expiration**: Determine when the pass expires
3. **Record in Ledger**: Keep track of active passes

### Session Validation
```python
async def validate_session_async(
    self,
    session_token: SessionToken
) -> Result[SessionInfo]:
    """Validate a session token and return session info."""
    # Retrieve session
    session_result = await self.auth_repository.get_session_async(session_token)
    if isinstance(session_result, Failure):
        if session_result.error_code == "SESSION_NOT_FOUND":
            self._publish_invalid_session_event(session_token)
        return session_result
    
    session = session_result.value
    
    # Check expiration
    if session.expires_at < datetime.utcnow():
        # Clean up expired session
        await self.auth_repository.delete_session_async(session_token)
        self._publish_session_expired_event(session)
        return Failure("SESSION_EXPIRED", "Session has expired")
```

**The Pass Inspection**:
1. **Find the Pass Record**: Look up in the ledger
2. **Check Expiration Date**: Is it still valid?
3. **Clean Up If Expired**: Remove expired passes
4. **Grant or Deny Entry**: Based on validity

---

## Permission System: The Authority Ledger

### Checking Permissions
```python
def has_permission(
    self,
    user_permissions: Set[Permission],
    required_permission: Permission
) -> bool:
    """
    Check if user has required permission.
    Supports wildcard permissions (e.g., 'admin:*').
    """
    # Direct match
    if required_permission in user_permissions:
        return True
    
    # Check wildcard permissions
    for user_perm in user_permissions:
        if self._matches_wildcard_permission(str(user_perm), str(required_permission)):
            return True
    
    return False
```

**The Authority Check**: Like checking if someone's badge allows access to a specific room:
1. **Direct Match**: "Do they have this exact permission?"
2. **Wildcard Check**: "Do they have a master key?" (e.g., `admin:*` matches `admin:users`)

### Wildcard Permission Matching
```python
def _matches_wildcard_permission(self, pattern: str, permission: str) -> bool:
    """Check if a wildcard pattern matches a permission."""
    # Convert wildcard pattern to regex
    # admin:* -> admin:.*
    # *:read -> .*:read
    regex_pattern = pattern.replace('*', '.*')
    regex_pattern = f"^{regex_pattern}$"
    
    try:
        return bool(re.match(regex_pattern, permission))
    except re.error:
        self.logger.warning(f"Invalid permission pattern: {pattern}")
        return False
```

**The Master Key System**: 
- `admin:*` is like a master key for all admin doors
- `*:read` is like a skeleton key that opens any room for reading
- Converts wildcards to regex patterns for flexible matching

---

## Security Measures: The Guardian's Protocols

### Password Hashing
```python
def _hash_api_key(self, api_key: ApiKey) -> str:
    """Hash an API key for storage."""
    # Use SHA-256 with salt from master password
    hasher = hashlib.sha256()
    hasher.update(api_key.encode('utf-8'))
    hasher.update(self.master_password.encode('utf-8'))
    return hasher.hexdigest()
```

**The Wax Seal Process**:
1. **Take the Key**: Original API key
2. **Add Master Salt**: Mix with master password
3. **Create Impression**: Generate one-way hash
4. **Store Only Impression**: Never store the actual key

### Secure Token Generation
```python
def _generate_session_token(self) -> SessionToken:
    """Generate a secure session token."""
    # 32 bytes = 256 bits of entropy
    random_bytes = secrets.token_bytes(32)
    token_string = base64.urlsafe_b64encode(random_bytes).decode('utf-8').rstrip('=')
    return SessionToken(f"sess_{token_string}")
```

Using `secrets` module ensures cryptographic randomness - like using a quantum dice instead of regular dice.

---

## Event System: The Castle's Herald

### Publishing Events
```python
self.event_bus.publish(Event(
    type=EventType.API_KEY_CREATED,
    data={
        "user_id": str(user_id),
        "key_name": str(key_name),
        "permissions": [str(p) for p in permissions]
    }
))
```

**The Herald's Announcements**: Every significant action is announced:
- "A new key has been created!"
- "Someone tried an invalid key!"
- "A session has expired!"

This allows other castle systems to react without direct coupling.

---

## Design Principles

### 1. Domain Types for Safety
Instead of passing around raw strings, we use specific types:
```python
UserId, ApiKey, SessionToken, Permission, KeyName
```
Like using labeled containers instead of unmarked boxes - prevents mixing up a user ID with an API key.

### 2. Result Pattern for Errors
```python
Result[ApiKeyCreated]  # Either Success(data) or Failure(error)
```
Like a delivery that either contains the package (Success) or a note explaining why it couldn't be delivered (Failure).

### 3. Repository Pattern
The service doesn't know if keys are stored in memory, database, or carved in stone - it just knows it can save and retrieve them.

### 4. Event-Driven Architecture
Components communicate through events rather than direct calls, like a castle where different departments communicate via the herald rather than directly.

---

## Summary: The Security Architecture

The Authentication Service exemplifies secure, clean architecture:

1. **Separation of Concerns**: Business logic separate from storage
2. **Type Safety**: Domain types prevent confusion
3. **Security First**: Proper hashing, timing attack prevention
4. **Event-Driven**: Loose coupling through events
5. **Testability**: All dependencies injected
6. **Explicit Async**: Clear about what operations might take time

The Guardian protects the castle through:
- Unforgeable keys (cryptographic randomness)
- Secure storage (one-way hashing)
- Temporary passes (session management)
- Flexible permissions (wildcard support)
- Audit trail (event system)

All while maintaining clean code that's easy to understand, test, and extend.

Copyright: DarkLightX/Dana Edwards