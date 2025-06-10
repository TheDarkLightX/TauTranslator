# Code Documentation Index

This directory contains detailed explanations of the refactored code modules following the Intentional Disclosure Principle. Each document uses metaphors and examples to make complex concepts accessible.

## Core Components

### 1. [Pattern Translator Explained](PATTERN_TRANSLATOR_EXPLAINED.md)
**The Language Alchemist** - Pattern-based translation engine that transforms expressions using regex rules.
- Pattern matching implementation
- Result type error handling
- Async method design
- Levenshtein distance algorithm

### 2. [Translation Manager Explained](MANAGER_EXPLAINED.md)
**The Master Conductor** - Orchestrates multiple translation engines with intelligent routing.
- Dependency injection
- Event-driven architecture
- Caching strategies
- Fallback mechanisms

### 3. [Authentication Core Explained](AUTH_CORE_EXPLAINED.md)
**The Vault Guardian** - Core authentication business logic with secure key management.
- API key generation and validation
- Session management
- Permission system with wildcards
- Security measures and hashing

### 4. [Authentication API Explained](AUTH_API_EXPLAINED.md)
**The Castle Gates** - FastAPI endpoints for authentication operations.
- Request/response models
- Dependency injection in API layer
- Error handling and translation
- Permission guards

### 5. [Configuration Explained](CONFIG_EXPLAINED.md)
**The Castle's Blueprint** - Type-safe configuration management with Pydantic.
- Settings validation
- Environment variable loading
- Resource limits
- Configuration inheritance

### 6. [Pattern Loader Explained](PATTERN_LOADER_EXPLAINED.md)
**The Master Librarian** - Manages loading and caching of translation patterns.
- Repository pattern
- Multi-format support (JSON, YAML, CSV)
- Thread-safe operations
- Search and ranking system

### 7. [Domain Types Explained](DOMAIN_TYPES_EXPLAINED.md)
**The Castle's Language** - Type system foundation with domain-specific types.
- NewType pattern
- Result types for error handling
- Domain modeling
- Type safety benefits

### 8. [Interfaces Explained](INTERFACES_EXPLAINED.md)
**The Sacred Scrolls of Agreement** - Contract definitions for clean architecture.
- Repository interfaces
- Event bus contract
- Dependency inversion
- Mock implementations

## Architecture Principles

All documented components follow the **Intentional Disclosure Principle** with four rules:

1. **Name for Consequence and Asynchronicity** - Async methods explicitly named with `_async` suffix
2. **Structure for Scannability** - Orchestrator pattern for high-level flow
3. **Maximize Disclosure via Type System** - Rich domain types instead of primitives
4. **Isolate Impurity** - Infrastructure separated behind interfaces

## Reading Guide

For newcomers to the codebase:
1. Start with [Domain Types](DOMAIN_TYPES_EXPLAINED.md) to understand the type system
2. Read [Interfaces](INTERFACES_EXPLAINED.md) to understand the contracts
3. Study individual components based on your area of focus
4. Reference [Configuration](CONFIG_EXPLAINED.md) for deployment settings

Each document includes:
- Overview with metaphors
- Line-by-line code explanations
- Design pattern discussions
- Practical examples
- Key takeaways