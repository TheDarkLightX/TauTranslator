# Authentication API: The Castle Gates

## Overview: The Public Interface to Security

The Authentication API is like the castle's main gate - it's where visitors (HTTP requests) meet the guards (authentication logic). This FastAPI router translates web requests into domain actions, ensuring proper validation and consistent responses. It's a pure orchestration layer following the Intentional Disclosure Principle.

**File**: `backend/unified/api/auth.py`  
**Purpose**: HTTP API endpoints for authentication operations  
**Architecture**: Clean API layer with dependency injection and domain separation

---

## The Gate Structure (Router Setup)

```python
router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"}
    }
)
```

This creates a specialized entrance with:
- **prefix**: All paths start with `/auth` (like "West Gate")
- **tags**: Grouped under "authentication" in API docs
- **responses**: Standard error responses pre-declared

---

## The Request Guards (Pydantic Models)

### Creating API Keys: The Application Form

```python
class CreateApiKeyRequest(BaseModel):
    """Request model for creating API key."""
    user_id: str
    key_name: str
    permissions: List[str] = Field(default_factory=list)
    
    @validator('key_name')
    def validate_key_name(cls, v):
        if not v or len(v) < 3:
            raise ValueError("Key name must be at least 3 characters")
        if len(v) > 100:
            raise ValueError("Key name too long")
        return v
```

Like an application form at the castle gate:
- **Fields**: What information we need
- **Validators**: Guards checking the form is filled correctly
- The validator ensures names aren't too short (hard to identify) or too long (unwieldy)

### The Response Scrolls

```python
class ApiKeyResponse(BaseModel):
    """Response model for API key creation."""
    api_key: str
    key_id: str
    message: str
    
    class Config:
        schema_extra = {
            "example": {
                "api_key": "sk_abcd1234...",
                "key_id": "550e8400-e29b-41d4-a716-446655440000",
                "message": "API key created successfully. Store it securely!"
            }
        }
```

The response is like an official scroll with:
- **api_key**: The actual key (shown only once!)
- **key_id**: Reference number for future management
- **message**: Instructions for the recipient
- **example**: What a real response looks like

---

## Dependency Injection: The Service Staff

```python
def get_auth_service() -> AuthenticationService:
    """Get authentication service instance."""
    from ..core.dependency_injection import get_container
    return get_container().create_authentication_service()
```

Rather than creating services directly, we request them from the DI container - like asking the castle's quartermaster for supplies rather than making them ourselves.

---

## The Main Gates (API Endpoints)

### Creating New Keys: The Ceremony

```python
@router.post(
    "/keys",
    response_model=ApiKeyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new API key",
    response_description="The newly created API key"
)
async def create_api_key_endpoint_async(
    request: CreateApiKeyRequest,
    auth_service: AuthenticationService = Depends(get_auth_service)
) -> ApiKeyResponse:
    """
    Create a new API key for a user.
    Rule 1: Endpoint name indicates async operation.
    Rule 2: Orchestrates request to service layer.
    """
```

The decorator is like posting a sign at the gate:
- **POST /keys**: The specific door to knock on
- **response_model**: What type of scroll you'll receive
- **status_code**: 201 means "Created successfully"

Let's trace through the full ceremony:

```python
    # Convert request to domain types
    user_id = UserId(request.user_id)
    key_name = KeyName(request.key_name)
    permissions = {Permission(p) for p in request.permissions}
    
    # Call service layer
    result = await auth_service.create_api_key_async(
        user_id=user_id,
        key_name=key_name,
        permissions=permissions
    )
    
    # Handle result
    if isinstance(result, Success):
        api_key_created = result.value
        return ApiKeyResponse(
            api_key=str(api_key_created.api_key),
            key_id=str(api_key_created.key_id),
            message="API key created successfully. Store it securely!"
        )
    else:
        # Convert domain failure to HTTP error
        raise_http_error_from_failure(result)
```

The flow is like a formal ceremony:
1. **Transform the Application**: Convert web data to domain types
2. **Submit to the Guardian**: Call the authentication service
3. **Handle the Response**: 
   - Success: Package the key in a nice scroll
   - Failure: Translate to appropriate HTTP error

### Validating Keys: The Identity Check

```python
@router.post(
    "/validate",
    response_model=ValidateResponse,
    summary="Validate API key"
)
async def validate_api_key_endpoint_async(
    api_key: str = Header(..., alias="X-API-Key"),
    auth_service: AuthenticationService = Depends(get_auth_service)
) -> ValidateResponse:
```

Notice the clever parameter:
```python
api_key: str = Header(..., alias="X-API-Key")
```

This extracts the API key from the `X-API-Key` header - like a guard checking for a badge on your lapel rather than asking you to present it.

### Session Management: The Day Pass System

```python
@router.post(
    "/sessions",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_session_endpoint_async(
    request: CreateSessionRequest,
    auth_service: AuthenticationService = Depends(get_auth_service)
) -> SessionResponse:
    """Create a new session for authenticated user."""
    # Implementation similar to API key creation
    # but returns a temporary session token
```

Sessions are like day passes - temporary access that expires.

---

## Error Handling: The Diplomatic Translators

### Converting Domain Errors to HTTP

```python
def raise_http_error_from_failure(failure: Failure) -> None:
    """Convert domain failure to HTTP exception."""
    error_map = {
        "INVALID_INPUT": (status.HTTP_400_BAD_REQUEST, "Invalid input"),
        "DUPLICATE_KEY_NAME": (status.HTTP_409_CONFLICT, "Key name already exists"),
        "USER_NOT_FOUND": (status.HTTP_404_NOT_FOUND, "User not found"),
        "UNAUTHORIZED": (status.HTTP_401_UNAUTHORIZED, "Unauthorized"),
        "FORBIDDEN": (status.HTTP_403_FORBIDDEN, "Forbidden"),
        "SESSION_EXPIRED": (status.HTTP_401_UNAUTHORIZED, "Session expired"),
        "INVALID_KEY_FORMAT": (status.HTTP_400_BAD_REQUEST, "Invalid API key format"),
    }
    
    status_code, default_message = error_map.get(
        failure.error_code,
        (status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal server error")
    )
    
    raise HTTPException(
        status_code=status_code,
        detail=failure.message or default_message
    )
```

This is like having diplomatic translators who convert internal castle language to visitor-friendly messages:
- **DUPLICATE_KEY_NAME** → 409 Conflict
- **SESSION_EXPIRED** → 401 Unauthorized
- Unknown errors → 500 Internal Server Error

### Consistent Error Responses

```python
@router.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle validation errors consistently."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Validation Error",
            "message": str(exc),
            "path": str(request.url.path)
        }
    )
```

All errors follow the same format - like using official letterhead for all castle correspondence.

---

## Advanced Patterns

### Dependency Injection in Action

```python
async def get_current_user(
    session_token: str = Header(..., alias="X-Session-Token"),
    auth_service: AuthenticationService = Depends(get_auth_service)
) -> AuthenticatedUser:
    """Get current user from session token."""
    result = await auth_service.validate_session_async(
        SessionToken(session_token)
    )
    
    if isinstance(result, Failure):
        raise_http_error_from_failure(result)
    
    return result.value.user
```

This creates a reusable dependency - other endpoints can use `Depends(get_current_user)` to automatically validate sessions.

### Permission Guards

```python
def require_permission(permission: str):
    """Create a dependency that checks for specific permission."""
    async def permission_checker(
        current_user: AuthenticatedUser = Depends(get_current_user),
        auth_service: AuthenticationService = Depends(get_auth_service)
    ):
        if not auth_service.has_permission(
            current_user.permissions,
            Permission(permission)
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required"
            )
        return current_user
    
    return permission_checker
```

Usage in endpoints:
```python
@router.delete("/keys/{key_id}")
async def revoke_api_key(
    key_id: str,
    user: AuthenticatedUser = Depends(require_permission("keys:delete"))
):
    # Only users with 'keys:delete' permission can access this
```

---

## The Complete Flow Example

Let's trace a complete API key creation:

1. **Client Request**:
```json
POST /auth/keys
{
    "user_id": "user123",
    "key_name": "Production Server",
    "permissions": ["read:data", "write:data"]
}
```

2. **Validation** (Pydantic):
   - Checks key_name length
   - Validates permission format

3. **Conversion** (API Layer):
```python
user_id = UserId(request.user_id)         # "user123" → UserId
key_name = KeyName(request.key_name)      # "Production Server" → KeyName
permissions = {Permission(p) for p in request.permissions}  # Set of Permissions
```

4. **Service Call** (Business Logic):
   - Generates secure key
   - Hashes for storage
   - Saves to repository
   - Publishes event

5. **Response Formation**:
```json
{
    "api_key": "sk_abcd1234...",
    "key_id": "550e8400-e29b-41d4-a716-446655440000",
    "message": "API key created successfully. Store it securely!"
}
```

---

## Design Principles in Action

### 1. Pure Orchestration
The API layer doesn't contain business logic - it only:
- Validates input format
- Converts types
- Calls services
- Formats responses

### 2. Explicit Async Naming
All async endpoints end with `_async`:
```python
async def create_api_key_endpoint_async(...)
async def validate_session_endpoint_async(...)
```

### 3. Type Safety Throughout
Domain types flow from request to response:
```python
request.user_id → UserId → service → response.user_id
```

### 4. Consistent Error Handling
All errors follow the same pattern, making client implementation easier.

---

## Summary

The Authentication API serves as a clean interface between HTTP and domain logic:

1. **Validates** incoming requests with Pydantic
2. **Transforms** web data to domain types
3. **Orchestrates** calls to business services
4. **Translates** results back to HTTP responses
5. **Guards** endpoints with permission checks

It exemplifies the Intentional Disclosure Principle by:
- Making async operations explicit in names
- Using type-safe domain objects
- Keeping the API layer thin and focused
- Providing clear, consistent responses

The result is an API that's easy to understand, test, and use - whether you're a developer integrating with it or an auditor reviewing its security.