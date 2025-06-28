Module src.tau_translator_omega.core_engine.result_enhanced
===========================================================
Enhanced Result type with monadic operations for functional composition.
Enables railway-oriented programming and eliminates nested conditionals.

Functions
---------

`compose(*functions)`
:   Compose functions from right to left.

`failure(error_code: str, message: str, details: dict | None = None) ‑> src.tau_translator_omega.core_engine.result_enhanced.Failure`
:   Create a failure result.

`pipe(*functions)`
:   Pipe functions from left to right.

`sequence(results: list[src.tau_translator_omega.core_engine.result_enhanced.Result[~T]]) ‑> src.tau_translator_omega.core_engine.result_enhanced.Result[list[~T]]`
:   Convert list of Results to Result of list, failing on first failure.

`success(value: ~T) ‑> src.tau_translator_omega.core_engine.result_enhanced.Success[~T]`
:   Create a success result.

`traverse(items: list[~T], func: Callable[[~T], src.tau_translator_omega.core_engine.result_enhanced.Result[~U]]) ‑> src.tau_translator_omega.core_engine.result_enhanced.Result[list[~U]]`
:   Apply function returning Result to each item, collecting results.

`try_catch(func: Callable[[], ~T], error_code: str = 'EXCEPTION') ‑> src.tau_translator_omega.core_engine.result_enhanced.Result[~T]`
:   Convert exception-throwing function to Result.

Classes
-------

`Failure(error_code: str, message: str, details: dict | None = None)`
:   Represents a failed operation result.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.result_enhanced.Result
    * abc.ABC
    * typing.Generic

    ### Instance variables

    `details: dict | None`
    :

    `error_code: str`
    :

    `message: str`
    :

    ### Methods

    `filter(self, predicate: Callable[[Any], bool], error_code: str = 'FILTER_FAILED') ‑> src.tau_translator_omega.core_engine.result_enhanced.Failure`
    :   Propagate failure unchanged.

    `flat_map(self, func: Callable[[Any], src.tau_translator_omega.core_engine.result_enhanced.Result[Any]]) ‑> src.tau_translator_omega.core_engine.result_enhanced.Failure`
    :   Propagate failure unchanged.

    `fold(self, on_success: Callable[[Any], ~U], on_failure: Callable[[ForwardRef('Failure')], ~U]) ‑> ~U`
    :   Apply failure function to self.

    `map(self, func: Callable[[Any], Any]) ‑> src.tau_translator_omega.core_engine.result_enhanced.Failure`
    :   Propagate failure unchanged.

    `or_else(self, default: ~T | Callable[[], ~T]) ‑> ~T`
    :   Return the default value.

    `to_optional(self) ‑> None`
    :   Convert to None.

`Result()`
:   Base Result type supporting monadic operations.

    ### Ancestors (in MRO)

    * abc.ABC
    * typing.Generic

    ### Descendants

    * src.tau_translator_omega.core_engine.result_enhanced.Failure
    * src.tau_translator_omega.core_engine.result_enhanced.Success

    ### Methods

    `filter(self, predicate: Callable[[~T], bool], error_code: str = 'FILTER_FAILED') ‑> src.tau_translator_omega.core_engine.result_enhanced.Result[~T]`
    :   Filter success values, converting false predicates to failures.

    `flat_map(self, func: Callable[[~T], ForwardRef('Result[U]')]) ‑> src.tau_translator_omega.core_engine.result_enhanced.Result[~U]`
    :   Chain operations that return Results.

    `fold(self, on_success: Callable[[~T], ~U], on_failure: Callable[[ForwardRef('Failure')], ~U]) ‑> ~U`
    :   Handle both success and failure cases with single expression.

    `is_failure(self) ‑> bool`
    :   Check if this is a failure result.

    `is_success(self) ‑> bool`
    :   Check if this is a success result.

    `map(self, func: Callable[[~T], ~U]) ‑> src.tau_translator_omega.core_engine.result_enhanced.Result[~U]`
    :   Transform success value, propagate failure.

    `or_else(self, default: ~T | Callable[[], ~T]) ‑> ~T`
    :   Provide default value for failure cases.

    `recover(self, recovery: Callable[[ForwardRef('Failure')], ~T]) ‑> src.tau_translator_omega.core_engine.result_enhanced.Result[~T]`
    :   Attempt to recover from failure.

    `to_optional(self) ‑> ~T | None`
    :   Convert to Optional, losing error information.

`Success(value: ~T)`
:   Represents a successful operation result.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.result_enhanced.Result
    * abc.ABC
    * typing.Generic

    ### Instance variables

    `value: ~T`
    :

    ### Methods

    `filter(self, predicate: Callable[[~T], bool], error_code: str = 'FILTER_FAILED') ‑> src.tau_translator_omega.core_engine.result_enhanced.Result[~T]`
    :   Filter success value.

    `fold(self, on_success: Callable[[~T], ~U], on_failure: Callable[[ForwardRef('Failure')], ~U]) ‑> ~U`
    :   Apply success function to value.

    `map(self, func: Callable[[~T], ~U]) ‑> src.tau_translator_omega.core_engine.result_enhanced.Result[~U]`
    :   Transform the success value.

    `or_else(self, default: ~T | Callable[[], ~T]) ‑> ~T`
    :   Return the success value.

    `recover(self, recovery: Callable[[ForwardRef('Failure')], ~T]) ‑> src.tau_translator_omega.core_engine.result_enhanced.Result[~T]`
    :   No recovery needed for success.

    `to_optional(self) ‑> ~T | None`
    :   Convert to Some.