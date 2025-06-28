Module src.tau_translator_omega.core_engine.semantic.semantic_types
===================================================================
Semantic analysis types following the Intentional Disclosure Principle.

Domain types for semantic analysis with immutable data structures.

Copyright: DarkLightX / Dana Edwards

Functions
---------

`check_type_compatibility(type1: str, type2: str) ‑> bool`
:   Check if two type strings are compatible.

`create_type_info(type_str: str) ‑> src.tau_translator_omega.core_engine.semantic.semantic_types.TypeInfo`
:   Create TypeInfo from type string.

Classes
-------

`AnalysisContext(file_path: str | None = None, strict_mode: bool = False, type_inference_enabled: bool = True, max_errors: int = 100)`
:   Immutable context for semantic analysis.

    ### Instance variables

    `file_path: str | None`
    :

    `max_errors: int`
    :

    `strict_mode: bool`
    :

    `type_inference_enabled: bool`
    :

`ErrorCollector()`
:   Collects semantic errors during analysis.
    
    Initialize empty error collector.

    ### Methods

    `add_error(self, error: src.tau_translator_omega.core_engine.semantic.semantic_types.SemanticError) ‑> None`
    :   Add an error to the collection.

    `clear_errors(self) ‑> None`
    :   Clear all errors.

    `get_errors(self) ‑> List[src.tau_translator_omega.core_engine.semantic.semantic_types.SemanticError]`
    :   Get all collected errors.

    `has_errors(self) ‑> bool`
    :   Check if any errors have been collected.

`SemanticError(message: str, line_number: int | None = None, column_number: int | None = None, error_type: str = 'semantic')`
:   Immutable semantic error information.

    ### Instance variables

    `column_number: int | None`
    :

    `error_type: str`
    :

    `line_number: int | None`
    :

    `message: str`
    :

`Symbol(name: str, symbol_type: str, scope_level: int, var_type: str | None = None, attributes: Dict[str, Any] = None)`
:   Mutable symbol table entry.

    ### Instance variables

    `attributes: Dict[str, Any]`
    :

    `name: str`
    :

    `scope_level: int`
    :

    `symbol_type: str`
    :

    `var_type: str | None`
    :

`SymbolTable()`
:   Symbol table with scope management.
    
    Initialize empty symbol table.

    ### Methods

    `declare_symbol(self, symbol: src.tau_translator_omega.core_engine.semantic.semantic_types.Symbol) ‑> bool`
    :   Declare a symbol in current scope.

    `enter_scope(self) ‑> None`
    :   Enter a new scope.

    `exit_scope(self) ‑> None`
    :   Exit current scope.

    `get_scope_count(self) ‑> int`
    :   Get total number of scopes created.

    `get_symbol_count(self) ‑> int`
    :   Get total number of symbols declared.

    `lookup_symbol(self, name: str) ‑> src.tau_translator_omega.core_engine.semantic.semantic_types.Symbol | None`
    :   Look up symbol in all visible scopes.

`SymbolType(*args, **kwds)`
:   Types of symbols in the symbol table.

    ### Ancestors (in MRO)

    * builtins.str
    * enum.Enum

    ### Class variables

    `CONSTANT`
    :

    `FUNCTION`
    :

    `PREDICATE`
    :

    `TYPE`
    :

    `VARIABLE`
    :

`TypeInfo(base_type: str, is_array: bool = False, element_type: str | None = None)`
:   Immutable type information.

    ### Instance variables

    `base_type: str`
    :

    `element_type: str | None`
    :

    `is_array: bool`
    :

    ### Methods

    `is_compatible_with(self, other: TypeInfo) ‑> bool`
    :   Check if this type is compatible with another.

`ValidationRule(rule_id: str, description: str, severity: str)`
:   Immutable validation rule.

    ### Instance variables

    `description: str`
    :

    `rule_id: str`
    :

    `severity: str`
    :