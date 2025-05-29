import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Set, Union

from .preprocessor_errors import PreprocessorError, CircularIncludeError, MacroExpansionError, ConditionalDirectiveError, IncludeFileNotFoundError
from .tgf_directive_handler import TGFDirectiveHandler


# Define regex patterns as constants at the module level or class level
SINGLE_LINE_COMMENT_RE = re.compile(r"//.*")
MULTI_LINE_COMMENT_START_RE = re.compile(r"/\*.*?", re.DOTALL) # Non-greedy match for start
MULTI_LINE_COMMENT_END_RE = re.compile(r".*?\*/", re.DOTALL)   # Non-greedy match for end
DIRECTIVE_RE = re.compile(r"^\s*([#@])([a-zA-Z_][a-zA-Z0-9_]*)(.*)")


class TGFPreprocessor:
    IDENTIFIER_RE = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$") # Class attribute for IDENTIFIER_RE
    MAX_MACRO_EXPANSION_DEPTH = 100 # Protection against deep/infinite macro recursion

    def __init__(self, initial_input: Union[str, Path], base_path: Optional[Path] = None):
        self.initial_input = initial_input

        # Determine base_path for the instance. This can be overridden per preprocess call.
        if isinstance(self.initial_input, Path) and self.initial_input.is_file():
            default_base = self.initial_input.parent
        else:
            default_base = Path.cwd()
        self.base_path = base_path if base_path is not None else default_base

        self.directive_handler = TGFDirectiveHandler(self) # Create handler, pass self

        # _current_run_base_path will be set at the start of each preprocess call
        self._current_run_base_path: Path = self.base_path 

        self._reset_for_new_input() # Initialize all mutable processing state

    def _reset_for_new_input(self):
        """Resets the preprocessor state for new input processing."""
        # Initialize TGFPreprocessor's own state first
        self.lark_grammar_lines: Set[str] = set()
        self.macros: Dict[str, Tuple[Optional[List[str]], str]] = {}
        self.visited_files: Set[Path] = set() # Tracks files already processed in an include chain for current top-level file
        self.current_processing_path_stack: List[Path] = [] # Tracks include stack for circular dependency detection
        self.current_line_number: int = 0
        self.line_buffer: str = "" # For handling line continuations (lines ending with '\')
        self._in_multiline_comment: bool = False # Tracks if currently inside a /* ... */ block
        self._macro_expansion_counts: Dict[str, int] = {} # For preventing macro recursion
        
        # Per-rule parsing state (if these are indeed preprocessor-level, not handler level)
        self.current_rule_lines: List[str] = []
        self._current_rule_body_lines: List[str] = [] # Consider if this is still needed or part of handler
        self.current_rule_original_name: Optional[str] = None
        self._current_rule_lhs: Optional[str] = None

        # Reset directive_handler's state by calling its own method
        if hasattr(self, 'directive_handler') and self.directive_handler:
            self.directive_handler.reset_state()
        # else: # Should not happen if __init__ is correct
            # Logger.warning("Directive handler not initialized when trying to reset its state")

    def preprocess(self, input_content: Optional[Union[str, Path]] = None, base_path_override: Optional[Path] = None) -> str:
        """Main method to preprocess the TGF input and return the final Lark grammar string."""
        try:
            # Determine the base path for resolving relative includes and other path-dependent operations.
            if base_path_override:
                self._current_run_base_path = base_path_override.resolve()
            elif isinstance(input_content, Path):
                # If input is a file, its directory is the base path
                self._current_run_base_path = input_content.resolve().parent
            elif self.base_path: # Initial base_path from constructor
                self._current_run_base_path = self.base_path.resolve()
            else:
                # Fallback if no other base path can be determined (e.g. string input without base_path_override)
                # This might mean relative includes are not possible or will be resolved against CWD.
                self._current_run_base_path = Path.cwd()

            # Determine the source of the input content (string or file path)
            current_input_source: Union[str, Path]
            if isinstance(input_content, str):
                current_input_source = input_content
            elif isinstance(input_content, Path):
                current_input_source = input_content.resolve()
            elif self.initial_input: # Fallback to initial_input from constructor if no input_content
                current_input_source = self.initial_input
            else:
                raise ValueError("No input content or initial input path provided for preprocessing.")

            self._reset_for_new_input() # Ensure clean state for each run

            # The to_lark method will use current_input_source and self._current_run_base_path
            processed_grammar = self.to_lark(current_input_source)
            return processed_grammar
        except PreprocessorError as e:
            print(f"DEBUG TGFPP: preprocess caught PreprocessorError: {type(e).__name__}: {e}") # ADDED FOR DEBUG
            raise # Re-raise the original PreprocessorError
        except Exception as e:
            raise PreprocessorError(f"An unexpected error occurred during preprocessing: {e}") from e

    def to_lark(self, current_input_source: Union[str, Path]) -> str:
        """Converts the TGF input (after macro expansion and directive handling) to a Lark-compatible grammar string."""
        try:
            content: str
            initial_processing_path: Path # The Path object representing the current top-level input source

            if isinstance(current_input_source, str):
                content = current_input_source
                # For string input, create a conceptual path for error reporting and context
                # It won't exist on disk, but helps maintain consistency in processing logic.
                initial_processing_path = self._current_run_base_path / "_direct_content.tgf_" 
            elif isinstance(current_input_source, Path):
                # Ensure the path is absolute and resolved for consistency
                resolved_path = current_input_source.resolve()
                if not resolved_path.exists():
                    raise IncludeFileNotFoundError(str(resolved_path), [str(resolved_path.parent)]) # Use IncludeFileNotFoundError for consistency
                content = resolved_path.read_text(encoding='utf-8')
                initial_processing_path = resolved_path
            else:
                # This case should ideally be caught by type checking or earlier validation
                raise TypeError("Input for to_lark must be a string or a Path object.")

            self._process_tgf_block(content.splitlines(), initial_processing_path)
            return "\n".join(sorted(list(self.lark_grammar_lines))) # Ensure consistent output order
        except PreprocessorError as e:
            print(f"DEBUG TGFPP: to_lark caught PreprocessorError: {type(e).__name__}: {e}") # ADDED FOR DEBUG
            raise  # Re-raises PreprocessorError and its children
        except Exception as e:
            raise PreprocessorError(f"An unexpected error occurred during TGF to_lark conversion: {e}") from e

    def _resolve_include_path(self, filename: str, current_file_path: Path) -> Path:
        if not filename:
            raise ValueError("Filename cannot be empty for include resolution")
        
        if Path(filename).is_absolute():
            return Path(filename).resolve()
        
        # Resolve relative to the dir of the file that contains the @use directive
        # If current_file_path is a file, use its parent. If it's a dir (e.g. initial base_path), use it directly.
        base_for_relative: Path # Type hint for clarity
        if current_file_path.name == "_direct_content.tgf_" and current_file_path.parent == self._current_run_base_path:
            # This handles the case where current_file_path is the synthetic path for string input.
            # Its "directory" for relative includes is _current_run_base_path.
            base_for_relative = self._current_run_base_path
        elif current_file_path.is_file(): # Path.is_file() checks for actual file existence
            base_for_relative = current_file_path.parent
        elif current_file_path.is_dir(): # Path.is_dir() checks for actual directory existence
            base_for_relative = current_file_path
        else:
            # Fallback for a current_file_path that doesn't exist (and isn't the synthetic one).
            # This might occur if a non-existent file path was passed as input_source to preprocess().
            # Default to its parent, assuming it's a file-like path concept.
            base_for_relative = current_file_path.parent
        
        target_file_path = (base_for_relative / filename).resolve()
        
        return target_file_path

    def _process_tgf_block(self, tgf_lines_iterable: List[str], current_file_path: Path):
        """
        Parses TGF directives and transforms TGF rules from a block of lines 
        into Lark-compatible grammar lines.
        Handles line continuations (backslash at EOL) before further processing.
        """
        
        line_buffer = ""
        
        self.current_processing_path_stack.append(current_file_path)
        try:
            for line_content in tgf_lines_iterable:
                stripped_line_for_check = line_content.rstrip()
                
                if stripped_line_for_check.endswith('\\'):
                    line_buffer += line_content[:len(stripped_line_for_check)-1]
                else:
                    line_buffer += line_content
                    self._process_line(line_buffer, current_file_path) 
                    line_buffer = "" 
        
            if line_buffer:
                self._process_line(line_buffer, current_file_path) 
        
            # Ensure the last rule in the current block (e.g., file or end of input) is finalized.
            self._finalize_current_rule()
        finally:
            if self.current_processing_path_stack and self.current_processing_path_stack[-1] == current_file_path:
                self.current_processing_path_stack.pop()

    def _process_line(self, line: str, current_file_context_path: Path):
        """Processes a single line from the TGF input."""
        original_line = line 
        line_content = line.strip()

        if self._in_multiline_comment:
            match_end_comment = MULTI_LINE_COMMENT_END_RE.match(line)
            if match_end_comment:
                self._in_multiline_comment = False
                line = line[len(match_end_comment.group(0)):] # Process rest of the line
                if not line.strip(): return
            else:
                return # Still inside multiline comment

        # Handle start of multiline comment if not already in one
        match_start_comment = MULTI_LINE_COMMENT_START_RE.match(line)
        if match_start_comment and not self._in_multiline_comment:
            # Check if it's also a single-line multiline comment (e.g. /* comment */)
            match_end_comment_inline = MULTI_LINE_COMMENT_END_RE.match(line[len(match_start_comment.group(0)):])
            if match_end_comment_inline:
                # It's a /* ... */ on a single line. Remove it and process the rest.
                line = line[len(match_start_comment.group(0)) + len(match_end_comment_inline.group(0)):]
                if not line.strip(): return
            else:
                self._in_multiline_comment = True
                # Process content before /*, if any
                line = line[:line.find("/*")]
                if not line.strip(): return # Nothing before the comment start on this line
        
        # Single line comment removal (must be after multiline check for cases like /* // */)
        line = SINGLE_LINE_COMMENT_RE.sub("", line).strip()

        if not line:
            return # Line is empty or became empty after comment removal

        if not self.is_current_block_active():
            return # Skip processing this line (directive or potential rule start)

        directive_match = DIRECTIVE_RE.match(line)
        if directive_match:
            # Always process conditional directives themselves, as they alter the active state.
            # Other directives and rules are subject to is_current_block_active().
            directive_name = directive_match.group(2).lower()
            directive_args_str = directive_match.group(3).strip()
            
            # Conditional directives that modify the stack MUST be processed regardless of current active state.
            conditional_control_directives = ["if", "ifdef", "ifndef", "elif", "else", "endif"]
            if directive_name in conditional_control_directives:
                self._finalize_current_rule() # Finalize any pending rule before processing directive
                self.directive_handler.handle_directive(directive_name, directive_args_str, current_file_context_path)
                return # Directive handled

            # For other directives and all rule processing, check if the current block is active.
            self._finalize_current_rule() # Finalize any pending rule before processing directive
            self.directive_handler.handle_directive(directive_name, directive_args_str, current_file_context_path)
            return # Directive handled

        # If not a directive, it could be a rule or continuation.
        # This part is only reached if the block is active (or no conditionals are in play).
        # Try to match common rule definition patterns (arrow or colon)
        match_arrow = re.compile(r'^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:::=|-\>|→)\s*(.*)').match(line)
        match_colon = re.compile(r'^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*(.*)').match(line)
        
        match = match_arrow or match_colon

        if match:
            self._finalize_current_rule() # Finalize any previous rule

            self.current_rule_original_name = match.group(1).strip()
            self._current_rule_lhs = self.current_rule_original_name # Initially, LHS is the original name
            rule_body_part = match.group(2).strip()
            
            self.current_rule_lines = [line] # Start new rule capture
            self._current_rule_body_lines = [rule_body_part] 
        else:
            # This line is not a directive, comment, rule start, or rule continuation.
            # It could be an invalid line or something to be preserved as is.
            # For now, if not part of a rule, add to lark_grammar_lines.
            # This behavior might need refinement based on TGF spec for non-rule, non-directive lines.
            if not self.current_rule_original_name:
                 self.lark_grammar_lines.add(line)

        try:
            # If it's a directive, handle it
            if self.directive_handler.is_directive(line_content):
                self.directive_handler.handle_directive(line_content, current_file_context_path)
            else:
                # Regular grammar line, add to current rule if one is active
                if self.current_rule_name:
                    self.current_rule_lines.append(line)
        except PreprocessorError as e:
            print(f"DEBUG TGFPP: _process_line caught PreprocessorError: {type(e).__name__}: {e}") # ADDED FOR DEBUG
            raise
        except Exception as e:
            # Log unexpected errors before wrapping them
            # print(f"Unexpected error in _process_line: {e}")
            raise PreprocessorError(f"An unexpected error occurred during line processing: {e}") from e

    def _finalize_current_rule(self):
        """Processes the accumulated lines for the current rule and adds it to the grammar."""
        if not self.current_rule_original_name or not self.current_rule_lines:
            return

        final_lhs_to_use = (self._current_rule_lhs or self.current_rule_original_name).strip()
        
        # Process the first line of the rule to separate LHS and RHS
        first_line_content = self.current_rule_lines[0]
        match = re.compile(r'^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:::=|-\>|→)\s*(.*)').match(first_line_content) or \
                re.compile(r'^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*(.*)').match(first_line_content)

        if not match:
            # This should not happen if current_rule_original_name is set, as it implies a rule start was detected.
            # If it does, treat all lines as raw lines to be macro-expanded and added.
            for line_content in self.current_rule_lines:
                self.lark_grammar_lines.add(self._expand_macros_in_line(line_content.strip()))
            self._reset_current_rule_state()
            return

        # Extract the original RHS part from the first line using match.start(2)
        # group(2) is the RHS in the regex patterns.
        rhs_first_part_original = first_line_content[match.start(2):].strip()
        expanded_rhs_first_part = self._expand_macros_in_line(rhs_first_part_original)
        
        self.lark_grammar_lines.add(f"{final_lhs_to_use}: {expanded_rhs_first_part}")

        # Process subsequent lines (continuations or alternatives)
        for line_content in self.current_rule_lines[1:]:
            # These lines are entirely part of the RHS (e.g., "| B", "  C")
            # They should be stripped of leading/trailing whitespace specific to the line itself,
            # then macro-expanded, and added.
            # Lark handles indentation for continuations if the line itself is indented.
            # If it starts with '|', that should be preserved.
            expanded_continuation_line = self._expand_macros_in_line(line_content.strip())
            self.lark_grammar_lines.add(expanded_continuation_line)
        
        self._reset_current_rule_state()

    def _reset_current_rule_state(self):
        """Resets the state variables for tracking the current rule."""
        self.current_rule_lines = []
        self._current_rule_body_lines = [] # Still populated by _process_line, consider removing if not used elsewhere
        self.current_rule_original_name = None
        self._current_rule_lhs = None

    def is_current_block_active(self) -> bool:
        """Determines if the current lines should be processed or skipped based on conditional directives."""
        if not self.directive_handler.conditional_stack:
            return True # No conditionals active, always process
        # If any level in the stack is marked as not potentially_active, then this block is skipped.
        for is_potentially_active, _ in self.directive_handler.conditional_stack:
            if not is_potentially_active:
                return False
        return True

    def _expand_macros_in_line(self, text: str) -> str:
        """Expands simple parameter-less macros in a line of text."""
        # This is a simplified version. A more robust version would handle word boundaries,
        # parameterized macros, and avoid partial replacements or recursion issues.
        # It should also respect the order of definition or a defined precedence.
        # For now, iterate and replace. This might need to be smarter to avoid
        # re-expanding parts of an already expanded macro, or to handle chained macros.
        # A common approach is to repeatedly scan and replace until no more expansions occur.
        
        # Simple textual replacement for parameter-less macros
        # Sort by length of macro name descending to replace longer matches first (e.g., AB before A)
        sorted_macro_names = sorted(
            [name for name, (params, _) in self.macros.items() if params is None],
            key=len,
            reverse=True
        )

        expanded_text = text
        for name in sorted_macro_names:
            _params, body = self.macros[name]
            expanded_text = re.sub(r'\b' + re.escape(name) + r'\b', body, expanded_text)
        return expanded_text

    def _include_file(self, file_path_str: str, current_file_context_path: Path):
        """Includes and processes a TGF file specified by @use directive."""
        
        include_path = Path(file_path_str)
        if not include_path.is_absolute():
            # Resolve relative to the dir of the file that contains the @use directive
            # If current_file_path is a file, use its parent. If it's a dir (e.g. initial base_path), use it directly.
            base_for_relative: Path # Type hint for clarity
            if current_file_context_path.name == "_direct_content.tgf_" and current_file_context_path.parent == self._current_run_base_path:
                # This handles the case where current_file_path is the synthetic path for string input.
                # Its "directory" for relative includes is _current_run_base_path.
                base_for_relative = self._current_run_base_path
            elif current_file_context_path.is_file(): # Path.is_file() checks for actual file existence
                base_for_relative = current_file_context_path.parent
            elif current_file_context_path.is_dir(): # Path.is_dir() checks for actual directory existence
                base_for_relative = current_file_context_path
            else:
                # Fallback for a current_file_path that doesn't exist (and isn't the synthetic one).
                # This might occur if a non-existent file path was passed as input_source to preprocess().
                # Default to its parent, assuming it's a file-like path concept.
                base_for_relative = current_file_context_path.parent
            
            target_file_path = (base_for_relative / include_path).resolve()
        else:
            target_file_path = include_path.resolve()

        if target_file_path in self.current_processing_path_stack:
            raise CircularIncludeError(f"Circular include detected: '{target_file_path}' is already in processing stack: {self.current_processing_path_stack}")

        if target_file_path in self.visited_files:
            # File has already been processed, skip to avoid re-processing
            return

        if not target_file_path.exists():
            # For the error message, show the directory from which the relative include was attempted
            search_dir_for_error_msg = base_for_relative if not include_path.is_absolute() else target_file_path.parent
            raise IncludeFileNotFoundError(str(include_path), [str(search_dir_for_error_msg)])

        # Add to visited files BEFORE processing its content
        self.visited_files.add(target_file_path)

        try:
            included_content = target_file_path.read_text(encoding='utf-8').splitlines()
            # Process the block of the included file. 
            # This will correctly manage the current_processing_path_stack for the new context.
            self._process_tgf_block(included_content, target_file_path)
        except PreprocessorError:
            raise
        except Exception as e: # This will catch errors from read_text or _process_tgf_block
            # Handle exceptions during included file processing, e.g., permission errors or errors within the included file's directives
            # Adding a comment to the grammar output might be one way to signal this
            self.lark_grammar_lines.add(f"// Error during processing of included file {target_file_path}: {type(e).__name__} - {e}")
            # Depending on desired strictness, might re-raise or wrap in a custom PreprocessorError

    def _handle_macro_definition(self, line_content: str, current_file_context_path: Path):
        match = self.MACRO_DEFINITION_RE.match(line_content)
