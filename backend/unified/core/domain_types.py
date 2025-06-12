"""
Domain type definitions for TauTranslator following Intentional Disclosure Principle
Copyright: DarkLightX/Dana Edwards
"""

from typing import NewType, TypeVar, Union, List, Dict, Optional, Any, Generic
from pathlib import Path
from enum import Enum


# Core Domain Types
TranslationId = NewType("TranslationId", str)
UserId = NewType("UserId", str) 
SessionId = NewType("SessionId", str)
GrammarId = NewType("GrammarId", str)
DictionaryId = NewType("DictionaryId", str)
PatternId = NewType("PatternId", str)

# File System Types
FilePath = NewType("FilePath", str)
DirectoryPath = NewType("DirectoryPath", str)
GrammarPath = NewType("GrammarPath", Path)
DictionaryPath = NewType("DictionaryPath", Path)

# Network Types
Url = NewType("Url", str)
ApiKey = NewType("ApiKey", str)
Email = NewType("Email", str)

# Translation Types
SourceText = NewType("SourceText", str)
TargetText = NewType("TargetText", str)
TranslationResult = NewType("TranslationResult", Dict[str, Any])

# Configuration Types
ConfigValue = Union[str, int, float, bool, List[str], Dict[str, Any]]
ConfigKey = NewType("ConfigKey", str)

# Status Enums
class TranslationStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CACHED = "cached"

class EngineType(Enum):
    PATTERN = "pattern"
    NLP = "nlp"
    GRAMMAR = "grammar"
    LMQL = "lmql"
    HYBRID = "hybrid"

class CacheStrategy(Enum):
    NONE = "none"
    MEMORY = "memory"
    REDIS = "redis"
    DISK = "disk"

# Type Variables for Generics
T = TypeVar('T')
TInput = TypeVar('TInput')
TOutput = TypeVar('TOutput')

# Import enhanced Result types
from .result_enhanced import Result, Success, Failure, success, failure, sequence, traverse, try_catch

# I/O Operation Markers
class IOBoundary:
    """Marker class for I/O operations following Rule 4."""
    pass

class DatabaseOperation(IOBoundary):
    """Marks database I/O operations."""
    pass

class FileSystemOperation(IOBoundary):
    """Marks file system I/O operations."""
    pass

class NetworkOperation(IOBoundary):
    """Marks network I/O operations."""
    pass