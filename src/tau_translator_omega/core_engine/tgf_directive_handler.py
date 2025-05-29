import re
from pathlib import Path
from typing import TYPE_CHECKING, Optional, List, Tuple

if TYPE_CHECKING:
    from .tgf_preprocessor import TgfPreprocessor

from .preprocessor_directives import PreprocessorDirective, IncludeDirective, DefineDirective, UndefDirective, PragmaDirective, TokenDirective, IfDirective, IfDefDirective, IfNDefDirective, ElifDirective, ElseDirective, EndIfDirective
from .preprocessor_errors import IncludeFileNotFoundError, CircularIncludeError, MacroDefinitionError, ConditionalDirectiveError

class TGFDirectiveHandler:
    def __init__(self, preprocessor: 'TgfPreprocessor'):
        self.preprocessor = preprocessor
        self.directive_mapping = {
            PreprocessorDirective.INCLUDE.value: self._handle_include,
            PreprocessorDirective.DEFINE.value: self._handle_define,
            PreprocessorDirective.UNDEF.value: self._handle_undef,
            PreprocessorDirective.PRAGMA.value: self._handle_pragma,
            PreprocessorDirective.TOKEN.value: self._handle_token,
            # Conditional Directives
            PreprocessorDirective.IF.value: self._handle_if,
            PreprocessorDirective.IFDEF.value: self._handle_ifdef,
            PreprocessorDirective.IFNDEF.value: self._handle_ifndef,
            PreprocessorDirective.ELIF.value: self._handle_elif,
            PreprocessorDirective.ELSE.value: self._handle_else,
            PreprocessorDirective.ENDIF.value: self._handle_endif,
        }
        self.conditional_stack: List[Tuple[bool, bool]] = []

    def reset_state(self):
        """Resets the internal state of the directive handler, e.g., for a new preprocessing run."""
        self.conditional_stack = []

    def handle_directive(self, directive_name: str, args_str: str, current_file_path: Path):
        # Ensure directive_name is lowercased to match keys in directive_mapping
        handler_method = self.directive_mapping.get(directive_name.lower())
        if handler_method:
            handler_method(args_str, current_file_path)
        else:
            # Optionally, log or raise an error for unknown directives
            self.preprocessor.lark_grammar_lines.add(f"// Unknown directive: #{directive_name} {args_str}")

    def _parse_define_args(self, args_str: str) -> tuple[str, Optional[list[str]], str]:
        """Parses the arguments for a #define directive."""
        # Pattern for #define NAME body or #define NAME(params) body
        define_pattern = re.compile(r"^([a-zA-Z_][a-zA-Z0-9_]*)(?:\(([^)]*)\))?\s*(.*)")
        match = define_pattern.match(args_str)
        if match:
            name, params_str, body = match.groups()
            parameters = [p.strip() for p in params_str.split(',')] if params_str else None
            body = body.strip() # Macro body is typically used as-is, including internal whitespace
            return name, parameters, body
        else:
            raise MacroDefinitionError(f"Malformed #define directive arguments: {args_str}")

    def _handle_include(self, args_str: str, current_file_path: Path):
        filename_match = re.match(r'"(.*?)"|<(.*?)>', args_str)
        if filename_match:
            filename = filename_match.group(1) or filename_match.group(2)
            if filename:
                try:
                    self.preprocessor._include_file(filename, current_file_path)
                except (IncludeFileNotFoundError, CircularIncludeError) as e:
                    # Propagate these specific errors, as tests expect them
                    raise e
                except Exception as e:
                    # For other unexpected errors during include, add a comment or log
                    self.preprocessor.lark_grammar_lines.add(f"// Error processing include for '{filename}': {type(e).__name__} - {e}")
            else:
                self.preprocessor.lark_grammar_lines.add(f"// Malformed #include (empty filename): {args_str}")
        else:
             self.preprocessor.lark_grammar_lines.add(f"// Malformed #include (invalid format): {args_str}")

    def _handle_define(self, args_str: str, current_file_path: Path):
        try:
            name, parameters, body = self._parse_define_args(args_str)
            self.preprocessor.macros[name] = (parameters, body)
        except MacroDefinitionError as e:
            # Handle or log the error, e.g., by adding a comment to output or raising further
            self.preprocessor.lark_grammar_lines.add(f"// Error in #define: {e}")
            # Optionally re-raise or handle as per error policy

    def _handle_undef(self, args_str: str, current_file_path: Path):
        macro_name = args_str.strip()
        if self.preprocessor.IDENTIFIER_RE.fullmatch(macro_name):
            if macro_name in self.preprocessor.macros:
                del self.preprocessor.macros[macro_name]
        else:
            self.preprocessor.lark_grammar_lines.add(f"// Malformed #undef: {args_str}")
        pass

    def _handle_pragma(self, args_str: str, current_file_path: Path):
        # Pragmas are implementation-defined. For now, just acknowledge.
        self.preprocessor.lark_grammar_lines.add(f"// #pragma {args_str}")
        pass

    def _handle_token(self, args_str: str, current_file_path: Path):
        # Handles @token directive, e.g., @token IDENTIFIER: "some_regex"
        # This is a placeholder. Actual implementation would modify rule LHS or manage token aliases.
        self.preprocessor.lark_grammar_lines.add(f"// @token {args_str}")
        pass

    def _evaluate_condition(self, condition: str) -> bool:
        # For now, only supports defined(MACRO) or MACRO checks
        # A more robust expression parser would be needed for complex conditions.
        stripped_condition = condition.strip()
        if stripped_condition.startswith("defined(") and stripped_condition.endswith(")"):
            macro_name = stripped_condition[len("defined("):-1].strip()
            return macro_name in self.preprocessor.macros
        elif self.preprocessor.IDENTIFIER_RE.fullmatch(stripped_condition): # Check if it's a bare macro name
            # Treat bare macro as true if defined and non-empty, or non-zero if it looks like a number
            # This part is highly simplified. A real preprocessor might evaluate to 0 or 1.
            if stripped_condition in self.preprocessor.macros:
                _params, body = self.preprocessor.macros[stripped_condition]
                if body.strip(): # Non-empty body treated as true
                    # Potentially try to interpret body as a number for 0/non-0 check
                    try:
                        return int(body.strip()) != 0
                    except ValueError:
                        return True # Non-numeric, non-empty body is true
                return False # Empty body is false
            return False # Undefined macro is false
        else:
            raise ConditionalDirectiveError(f"Unsupported condition syntax in #if: {condition}")

    def _handle_if(self, args_str: str, current_file_path: Path):
        condition_true = self._evaluate_condition(args_str)
        parent_block_active = self.preprocessor.is_current_block_active()
        # This new block is active if its condition is true AND its parent context is active.
        self.conditional_stack.append((condition_true and parent_block_active, condition_true))

    def _handle_ifdef(self, args_str: str, current_file_path: Path):
        macro_name = args_str.strip()
        if not self.preprocessor.IDENTIFIER_RE.fullmatch(macro_name):
            raise ConditionalDirectiveError(f"Invalid macro name in #ifdef: {macro_name}")
        condition_true = macro_name in self.preprocessor.macros
        parent_block_active = self.preprocessor.is_current_block_active()
        self.conditional_stack.append((condition_true and parent_block_active, condition_true))

    def _handle_ifndef(self, args_str: str, current_file_path: Path):
        macro_name = args_str.strip()
        if not self.preprocessor.IDENTIFIER_RE.fullmatch(macro_name):
            raise ConditionalDirectiveError(f"Invalid macro name in #ifndef: {macro_name}")
        condition_true = macro_name not in self.preprocessor.macros
        parent_block_active = self.preprocessor.is_current_block_active()
        self.conditional_stack.append((condition_true and parent_block_active, condition_true))

    def _handle_elif(self, args_str: str, current_file_path: Path):
        if not self.conditional_stack:
            raise ConditionalDirectiveError("#elif without matching #if/ifdef/ifndef")
        
        _prev_block_active_overall, prev_branch_executed_in_current_block = self.conditional_stack[-1]

        if prev_branch_executed_in_current_block:
            # A previous #if or #elif in this block was true, so this #elif is false regardless of its condition
            self.conditional_stack[-1] = (False, True) # block becomes inactive, true branch still considered executed
        else:
            condition_true = self._evaluate_condition(args_str)
            
            is_parent_context_globally_active = True
            if len(self.conditional_stack) > 1:
                for is_parent_potentially_active, _ in self.conditional_stack[:-1]: # Check all parent blocks
                    if not is_parent_potentially_active:
                        is_parent_context_globally_active = False
                        break
            
            current_elif_active = condition_true and is_parent_context_globally_active
            self.conditional_stack[-1] = (current_elif_active, current_elif_active) # Update based on this #elif

    def _handle_else(self, args_str: str, current_file_path: Path):
        if not self.conditional_stack:
            raise ConditionalDirectiveError("#else without matching #if/ifdef/ifndef")

        _prev_block_active_overall, prev_branch_executed_in_current_block = self.conditional_stack[-1]

        if prev_branch_executed_in_current_block:
            # A previous #if or #elif in this block was true, so this #else is false.
            self.conditional_stack[-1] = (False, True)
        else:
            # No previous #if or #elif in this block was true. This #else branch becomes active if its parent context is active.
            is_parent_context_globally_active = True
            if len(self.conditional_stack) > 1:
                for is_parent_potentially_active, _ in self.conditional_stack[:-1]:
                    if not is_parent_potentially_active:
                        is_parent_context_globally_active = False
                        break
            self.conditional_stack[-1] = (is_parent_context_globally_active, True) # Else is active, mark true branch as executed

    def _handle_endif(self, args_str: str, current_file_path: Path):
        if not self.conditional_stack:
            raise ConditionalDirectiveError("#endif without matching #if/ifdef/ifndef")
        self.conditional_stack.pop()

# Regex for a simple identifier, used for macro names and parameters
# IDENTIFIER_RE = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]*") # This was the old module-level global, now accessed via preprocessor instance
