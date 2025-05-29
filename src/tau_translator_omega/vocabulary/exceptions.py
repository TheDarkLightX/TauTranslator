# Custom exceptions for the vocabulary module

class VocabularyError(Exception):
    """Base class for vocabulary exceptions."""
    pass

class EntityTypeNotFoundError(VocabularyError):
    """Raised when an entity type is not found."""
    pass

class FieldNotFoundError(VocabularyError):
    """Raised when a field is not found within an entity type."""
    pass
