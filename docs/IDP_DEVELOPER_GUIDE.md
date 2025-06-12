# Intentional Disclosure Principle (IDP) Developer Guide

## Introduction

This guide helps developers maintain and extend the TauTranslator codebase following the Intentional Disclosure Principle (IDP). By following these guidelines, you ensure code remains maintainable, testable, and easy to understand.

## The Four IDP Rules

### Rule 1: Name for Consequence and Asynchronicity

**Principle**: Method names should clearly indicate what they do and whether they're asynchronous.

**Guidelines**:
```python
# ✅ Good - Clear consequence and async indication
async def load_plugins_from_directory_async(self, directory: Path) -> Result[List[Plugin], str]:
    pass

# ❌ Bad - Unclear what happens, no async suffix
async def process(self, d):
    pass
```

**Naming Conventions**:
- Async methods: `method_name_async`
- Factories: `create_*` or `build_*`
- Validators: `validate_*` or `is_valid_*`
- Converters: `*_to_*` (e.g., `tgf_to_lark`)
- Private helpers: `_helper_method`

### Rule 2: Structure for Scannability (≤10 Lines)

**Principle**: Every method must be 10 lines or fewer, making code easy to scan and understand.

**Decomposition Strategies**:

1. **Extract Validation**
```python
# ✅ Good - Validation extracted
async def create_user_async(self, data: UserData) -> Result[User, str]:
    validation_result = self._validate_user_data(data)
    if isinstance(validation_result, Failure):
        return validation_result
    
    user = self._build_user_entity(data)
    save_result = await self._save_user_async(user)
    
    if isinstance(save_result, Failure):
        return save_result
        
    return Success(user)

def _validate_user_data(self, data: UserData) -> Result[None, str]:
    if not data.email:
        return Failure("Email is required")
    if not self._is_valid_email(data.email):
        return Failure("Invalid email format")
    return Success(None)
```

2. **Pipeline Pattern**
```python
# ✅ Good - Clear pipeline of operations
async def process_translation_async(self, text: str) -> Result[str, str]:
    return await (self._validate_input_async(text)
                  .flat_map_async(self._parse_text_async)
                  .flat_map_async(self._translate_async)
                  .map_async(self._format_output))
```

3. **Early Returns**
```python
# ✅ Good - Guard clauses reduce nesting
def calculate_discount(self, user: User, amount: Money) -> Money:
    if not user.is_premium:
        return Money(0)
    
    if amount.value < 100:
        return Money(amount.value * 0.05)
    
    if amount.value < 1000:
        return Money(amount.value * 0.10)
        
    return Money(amount.value * 0.15)
```

### Rule 3: Maximize Disclosure via Type System

**Principle**: Use domain types instead of primitives to make code self-documenting.

**Domain Types Pattern**:
```python
# ✅ Good - Domain types provide clarity
from typing import NewType
from dataclasses import dataclass

UserId = NewType("UserId", str)
EmailAddress = NewType("EmailAddress", str)
Money = NewType("Money", float)

@dataclass(frozen=True)
class User:
    id: UserId
    email: EmailAddress
    balance: Money
    
# Usage makes intent clear
def transfer_funds(from_user: UserId, to_user: UserId, amount: Money) -> Result[None, str]:
    pass
```

**Avoid Primitive Obsession**:
```python
# ❌ Bad - What do these strings and floats represent?
def process_order(user_id: str, product_id: str, price: float, discount: float):
    pass

# ✅ Good - Types make intent clear
def process_order(user: UserId, product: ProductId, price: Money, discount: Percentage):
    pass
```

### Rule 4: Isolate Impurity in Infrastructure Layer

**Principle**: Separate pure business logic from I/O operations.

**Clean Architecture Pattern**:
```
module_refactored.py (Orchestration Layer)
├── domain/
│   ├── module_types.py (Immutable Domain Types)
│   └── module_service.py (Pure Business Logic)
└── infrastructure/
    └── module_infrastructure.py (I/O Operations)
```

**Example Structure**:
```python
# domain/user_service.py - Pure business logic
class UserService:
    def calculate_loyalty_points(self, purchases: List[Purchase]) -> LoyaltyPoints:
        """Pure function - no I/O, no side effects"""
        total = sum(p.amount for p in purchases)
        return LoyaltyPoints(int(total * 0.1))

# infrastructure/user_repository.py - I/O operations
class UserRepository:
    async def load_user_async(self, user_id: UserId) -> Result[User, str]:
        """Impure - database I/O"""
        try:
            data = await self._db.query(f"SELECT * FROM users WHERE id = {user_id}")
            return Success(User.from_dict(data))
        except DBError as e:
            return Failure(f"Database error: {e}")
```

## Refactoring Workflow

### 1. Analyze Current Code
```bash
# Use the code quality tool
python tools/enhanced_code_quality_tool.py --file path/to/module.py
```

### 2. Create Domain Types
```python
# module_types.py
from typing import NewType
from dataclasses import dataclass

ModuleId = NewType("ModuleId", str)
ConfigPath = NewType("ConfigPath", str)

@dataclass(frozen=True)
class ModuleConfig:
    id: ModuleId
    path: ConfigPath
    enabled: bool = True
```

### 3. Extract Infrastructure
```python
# module_infrastructure.py
class ConfigFileLoader:
    @staticmethod
    def load_config(path: ConfigPath) -> Result[ModuleConfig, str]:
        """All file I/O isolated here"""
        try:
            with open(path) as f:
                data = json.load(f)
            return Success(ModuleConfig.from_dict(data))
        except Exception as e:
            return Failure(f"Failed to load config: {e}")
```

### 4. Create Pure Service Layer
```python
# module_service.py
class ModuleService:
    def process_config(self, config: ModuleConfig) -> ProcessedConfig:
        """Pure business logic - no I/O"""
        # All methods ≤10 lines
        validated = self._validate_config(config)
        normalized = self._normalize_paths(validated)
        return self._apply_defaults(normalized)
```

### 5. Orchestrate in Main Module
```python
# module_refactored.py
class ModuleRefactored:
    def __init__(self):
        self._service = ModuleService()
        
    async def initialize_async(self, config_path: str) -> Result[None, str]:
        config_result = ConfigFileLoader.load_config(ConfigPath(config_path))
        if isinstance(config_result, Failure):
            return config_result
            
        processed = self._service.process_config(config_result.unwrap())
        return await self._apply_configuration_async(processed)
```

## Testing Strategies

### 1. Test Pure Functions Directly
```python
def test_calculate_discount():
    service = PricingService()
    result = service.calculate_discount(
        Money(100), 
        DiscountCode("SAVE10")
    )
    assert result == Money(90)
```

### 2. Mock Infrastructure at Boundaries
```python
@patch('module.infrastructure.ConfigFileLoader.load_config')
def test_module_initialization(mock_load):
    mock_load.return_value = Success(test_config)
    module = ModuleRefactored()
    result = asyncio.run(module.initialize_async("test.json"))
    assert isinstance(result, Success)
```

### 3. Integration Tests for I/O
```python
async def test_real_file_loading():
    # Test actual I/O separately
    with tempfile.NamedTemporaryFile() as f:
        f.write(b'{"key": "value"}')
        f.flush()
        result = await FileLoader.load_json_async(f.name)
        assert result.unwrap()["key"] == "value"
```

## Common Patterns

### Result Monad for Error Handling
```python
from returns.result import Result, Success, Failure

async def safe_operation_async(data: InputData) -> Result[OutputData, str]:
    try:
        validated = validate(data)
        processed = await process_async(validated)
        return Success(processed)
    except ValidationError as e:
        return Failure(f"Validation failed: {e}")
    except ProcessingError as e:
        return Failure(f"Processing failed: {e}")
```

### Builder Pattern for Complex Objects
```python
class QueryBuilder:
    def __init__(self):
        self._conditions = []
        self._limit = None
        
    def where(self, condition: Condition) -> 'QueryBuilder':
        self._conditions.append(condition)
        return self
        
    def limit(self, count: int) -> 'QueryBuilder':
        self._limit = count
        return self
        
    def build(self) -> Query:
        return Query(self._conditions, self._limit)
```

### Repository Pattern for Data Access
```python
class UserRepository:
    async def find_by_id_async(self, user_id: UserId) -> Result[User, str]:
        pass
        
    async def save_async(self, user: User) -> Result[None, str]:
        pass
        
    async def delete_async(self, user_id: UserId) -> Result[None, str]:
        pass
```

## Code Review Checklist

- [ ] All methods ≤10 lines?
- [ ] Async methods end with `_async`?
- [ ] Domain types instead of primitives?
- [ ] I/O isolated in infrastructure layer?
- [ ] Error handling uses Result[T]?
- [ ] Immutable data structures (frozen dataclasses)?
- [ ] Clear method names indicating consequence?
- [ ] Tests cover pure logic and I/O separately?

## Tools and Scripts

### Check Method Length
```bash
# Find methods over 10 lines
python tools/analyze_method_lengths.py src/
```

### Measure Complexity
```bash
# Get complexity metrics
python tools/enhanced_code_quality_tool.py --file module.py
```

### Generate Refactoring Plan
```bash
# Create refactoring suggestions
python tools/craftsmanship_refactoring_toolkit.py analyze module.py
```

## Conclusion

Following IDP principles creates code that is:
- **Readable**: Anyone can understand what code does
- **Maintainable**: Easy to modify and extend
- **Testable**: Pure functions and clear boundaries
- **Reliable**: Type safety and explicit error handling

Remember: Good code is written for humans to read, not just computers to execute.