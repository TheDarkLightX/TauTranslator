# Defines custom exception types for the TGF preprocessor.

class PreprocessorError(Exception):
    """Base class for all preprocessor-related errors."""
    pass

class IncludeFileNotFoundError(PreprocessorError):
    """Raised when an included file cannot be found."""
    def __init__(self, filename: str, search_paths: list[str]):
        self.filename = filename
        self.search_paths = search_paths
        super().__init__(f"Include file '{filename}' not found. Searched in: {search_paths}")

class CircularIncludeError(PreprocessorError):
    """Raised when a circular include dependency is detected."""
    def __init__(self, filename: str, include_stack: list[str]):
        self.filename = filename
        self.include_stack = include_stack
        super().__init__(f"Circular include detected: '{filename}' is already in the include stack {include_stack}")

class MacroDefinitionError(PreprocessorError):
    """Raised for errors during macro definition (e.g., redefinition, invalid syntax)."""
    pass

class MacroExpansionError(PreprocessorError):
    """Raised for errors during macro expansion (e.g., too many arguments, recursion depth exceeded)."""
    pass

class ConditionalDirectiveError(PreprocessorError):
    """Raised for errors related to conditional directives (e.g., mismatched #endif, invalid expression)."""
    pass
