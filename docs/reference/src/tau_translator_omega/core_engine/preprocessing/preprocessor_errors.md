Module src.tau_translator_omega.core_engine.preprocessing.preprocessor_errors
=============================================================================

Classes
-------

`CircularIncludeError(filename: str, include_stack: list[str])`
:   Raised when a circular include dependency is detected.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.preprocessing.preprocessor_errors.PreprocessorError
    * builtins.Exception
    * builtins.BaseException

`ConditionalDirectiveError(*args, **kwargs)`
:   Raised for errors related to conditional directives (e.g., mismatched #endif, invalid expression).

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.preprocessing.preprocessor_errors.PreprocessorError
    * builtins.Exception
    * builtins.BaseException

`IncludeFileNotFoundError(filename: str, search_paths: list[str])`
:   Raised when an included file cannot be found.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.preprocessing.preprocessor_errors.PreprocessorError
    * builtins.Exception
    * builtins.BaseException

`MacroDefinitionError(*args, **kwargs)`
:   Raised for errors during macro definition (e.g., redefinition, invalid syntax).

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.preprocessing.preprocessor_errors.PreprocessorError
    * builtins.Exception
    * builtins.BaseException

`MacroExpansionError(*args, **kwargs)`
:   Raised for errors during macro expansion (e.g., too many arguments, recursion depth exceeded).

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.preprocessing.preprocessor_errors.PreprocessorError
    * builtins.Exception
    * builtins.BaseException

`PreprocessorError(*args, **kwargs)`
:   Base class for all preprocessor-related errors.

    ### Ancestors (in MRO)

    * builtins.Exception
    * builtins.BaseException

    ### Descendants

    * src.tau_translator_omega.core_engine.preprocessing.preprocessor_errors.CircularIncludeError
    * src.tau_translator_omega.core_engine.preprocessing.preprocessor_errors.ConditionalDirectiveError
    * src.tau_translator_omega.core_engine.preprocessing.preprocessor_errors.IncludeFileNotFoundError
    * src.tau_translator_omega.core_engine.preprocessing.preprocessor_errors.MacroDefinitionError
    * src.tau_translator_omega.core_engine.preprocessing.preprocessor_errors.MacroExpansionError