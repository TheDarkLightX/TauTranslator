# Defines an enumeration of supported TGF preprocessor directives.

from enum import Enum

class PreprocessorDirective(Enum):
    """Enumerates the types of preprocessor directives."""
    # File inclusion
    INCLUDE = "include"

    # Macro definition and un-definition
    DEFINE = "define"
    UNDEF = "undef"

    # Conditional compilation
    IF = "if"
    IFDEF = "ifdef"
    IFNDEF = "ifndef"
    ELIF = "elif"
    ELSE = "else"
    ENDIF = "endif"

    # Pragmas (implementation-defined behavior)
    PRAGMA = "pragma"

    # Lark-specific or TGF-enhancement directives (examples)
    TOKEN = "token"        # For defining or aliasing tokens, e.g., @token IDENTIFIER: /[a-zA-Z_][a-zA-Z0-9_]*/
    IMPORT = "import"      # For importing Lark grammar elements, e.g., %import common.WS
    IGNORE = "ignore"      # For specifying terminals to ignore, e.g., %ignore WS

# Individual directive classes (can be used for type checking or specific handling if needed)
# For now, the enum values (strings) are used directly by the handler.

class IncludeDirective:
    pass

class DefineDirective:
    pass

class UndefDirective:
    pass

class IfDirective:
    pass

class IfDefDirective:
    pass

class IfNDefDirective:
    pass

class ElifDirective:
    pass

class ElseDirective:
    pass

class EndIfDirective:
    pass

class PragmaDirective:
    pass

class TokenDirective: # Corresponds to @token
    pass
