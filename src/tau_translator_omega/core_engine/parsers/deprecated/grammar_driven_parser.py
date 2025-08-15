"""
Grammar-Driven Parser for Dynamic Tau Translation
=================================================

This module implements a parser that uses user-provided grammar files
to perform translation between Tau and natural language.

Author: DarkLightX / Dana Edwards
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from returns.result import Result, Success, Failure

from lark import Lark, Tree, Token, Transformer, Visitor
from lark.exceptions import LarkError, UnexpectedInput

from pathlib import Path
from ...infrastructure.grammar_io import GrammarRepository
from ...grammar_processing import TGFGrammarService, LoadedGrammar
from ...ast.ast_nodes import ASTNode, IdentifierNode, LiteralNode

logger = logging.getLogger(__name__)


class TranslationMode(Enum):
    """Direction of translation"""
    TAU_TO_NATURAL = "tau_to_natural"
    NATURAL_TO_TAU = "natural_to_tau"


@dataclass
class ParseResult:
    """Result of grammar-driven parsing"""
    success: bool
    ast: Optional[Tree] = None
    error: Optional[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


@dataclass
class TranslationRule:
    """Rule for translating between parse tree and natural language"""
    rule_name: str
    pattern: str
    template: str
    variables: List[str]
    priority: int = 0


class GrammarDrivenTransformer(Transformer):
    """Transforms parse trees based on loaded grammar rules"""
    
    def __init__(self, grammar: LoadedGrammar, mode: TranslationMode):
        self.grammar = grammar
        self.mode = mode
        self.translation_rules = self._build_translation_rules()
    
    def _build_translation_rules(self) -> Dict[str, TranslationRule]:
        """Build translation rules from grammar"""
        rules = {}
        
        # For each grammar rule, create a translation template
        for rule_name, rule_def in self.grammar.rules.items():
            # Simple heuristic-based template generation
            # In a real system, these would be loaded from configuration
            
            if rule_name == 'solve_command':
                rules[rule_name] = TranslationRule(
                    rule_name=rule_name,
                    pattern="solve {constraint}",
                    template="Find values that satisfy: {constraint}",
                    variables=["constraint"]
                )
            elif rule_name == 'rule_definition':
                rules[rule_name] = TranslationRule(
                    rule_name=rule_name,
                    pattern="r {name}[{time}] = {expression}",
                    template="Rule {name} at time {time} equals {expression}",
                    variables=["name", "time", "expression"]
                )
            elif rule_name == 'stream_declaration':
                rules[rule_name] = TranslationRule(
                    rule_name=rule_name,
                    pattern="sbf {name} = {source}",
                    template="Stream {name} is defined as {source}",
                    variables=["name", "source"]
                )
            # Add more rule templates as needed
            
        return rules
    
    def transform_tree(self, tree: Tree) -> str:
        """Transform a parse tree into target format"""
        if self.mode == TranslationMode.TAU_TO_NATURAL:
            return self._tree_to_natural(tree)
        else:
            return self._tree_to_tau(tree)
    
    def _tree_to_natural(self, tree: Tree) -> str:
        """Convert parse tree to natural language"""
        if tree.data in self.translation_rules:
            rule = self.translation_rules[tree.data]
            # Extract values from tree children
            values = {}
            for i, child in enumerate(tree.children):
                if i < len(rule.variables):
                    var_name = rule.variables[i]
                    if isinstance(child, Tree):
                        values[var_name] = self._tree_to_natural(child)
                    else:
                        values[var_name] = str(child)
            
            # Apply template
            result = rule.template
            for var, val in values.items():
                result = result.replace(f"{{{var}}}", val)
            return result
        
        # Default handling for unknown rules
        if len(tree.children) == 1 and isinstance(tree.children[0], Token):
            return str(tree.children[0])
        
        # Recursively process children
        parts = []
        for child in tree.children:
            if isinstance(child, Tree):
                parts.append(self._tree_to_natural(child))
            else:
                parts.append(str(child))
        
        return " ".join(parts)
    
    def _tree_to_tau(self, tree: Tree) -> str:
        """Convert parse tree to Tau syntax"""
        # This is the inverse of _tree_to_natural
        # Implementation would depend on the specific grammar
        return str(tree.pretty())  # Placeholder


try:
    # Preferred location (package-level lmql_engine)
    from ....lmql_engine.translation_strategies import TranslationStrategy
except Exception:  # pragma: no cover - fallback for older paths
    # Legacy relative path used during refactors
    from ...lmql_engine.translation_strategies import TranslationStrategy


class GrammarDrivenParser:
    """
    Parser that uses dynamically loaded grammars for translation.
    
    This parser can adapt to different Tau dialects or language variations
    by loading different grammar files.
    """
    
    def __init__(self, grammar_service: Optional[TGFGrammarService] = None):
        self.lark_parser: Optional[Lark] = None
        self.current_grammar: Optional[LoadedGrammar] = None
        self.initialization_error_reason: Optional[str] = "Parser not yet initialized."

        if grammar_service:
            self.grammar_service = grammar_service
        else:
            # The parser is in core_engine/parsers, grammars are in core_engine/parsers/grammars
            grammar_dir = Path(__file__).parent / "grammars"
            
            # Config file is at the project root's /config directory
            project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
            config_file = project_root / "config" / "grammar-files.json"

            self.grammar_service = TGFGrammarService(
                GrammarRepository(grammar_dir, config_file)
            )

        # Attempt to load all grammars from the repository via the service
        load_all_result = self.grammar_service.load_and_parse_all_grammars()

        if isinstance(load_all_result, Failure):
            err_msg = f"TGFGrammarService failed to load and parse all grammars: {load_all_result.failure()}"
            logger.error(err_msg)
            self.initialization_error_reason = err_msg
            # Potentially, the service might still have an active grammar if one was set before this failure,
            # or if it defaults to one despite failing to load others. So, we continue to check.

        # Check for an active grammar directly from the attribute
        grammar_to_set = self.grammar_service.active_grammar
        if grammar_to_set is not None:
            if self.set_grammar(grammar_to_set):
                logger.info(f"GrammarDrivenParser initialized successfully with active grammar: {grammar_to_set.filename}")
                # If load_all_result failed earlier but we successfully set an active grammar, 
                # the parser might still be usable with this specific grammar.
                # We keep the initialization_error_reason from load_all_result if it exists, as a warning.
                if isinstance(load_all_result, Failure) and not self.initialization_error_reason:
                    self.initialization_error_reason = f"Warning: Active grammar '{grammar_to_set.filename}' set, but failed to load all other grammars: {load_all_result.failure()}"
                elif isinstance(load_all_result, Success): # Clear any prior generic init error if all loaded fine and active is set
                    self.initialization_error_reason = None 
            else:
                # set_grammar already logs and sets its own initialization_error_reason
                logger.warning(f"GrammarDrivenParser: Failed to set active grammar '{grammar_to_set.filename}' after loading. Reason: {self.initialization_error_reason}")
        else: # No active grammar found in the service
            self.current_grammar = None
            no_active_reason = "TGFGrammarService has no active grammar set."
            if isinstance(load_all_result, Failure):
                self.initialization_error_reason = f"Failed to load any grammars ({load_all_result.failure()}) and {no_active_reason}"
            else:
                self.initialization_error_reason = no_active_reason
            logger.warning(f"GrammarDrivenParser initialized without an active grammar. Reason: {self.initialization_error_reason}")

    def _initialize_parser(self):
        """Initialize parser with active grammar"""
        logger.info("CASCADE_DEBUG: Entering _initialize_parser")
        if not self.current_grammar:
            logger.error("Cannot initialize parser without an active grammar.")
            return

        try:
            # Get grammar in Lark format
            grammar_data_tuple = self.grammar_service.get_grammar_for_parser()
            if not grammar_data_tuple:
                logger.error(f"Could not get grammar data for {self.current_grammar.filename} from grammar service.")
                return

            lark_grammar_str, diagnostic_str = grammar_data_tuple

            # Use print for high visibility, bypassing potential logger issues
            print(f"CASCADE_DIAGNOSTIC_INFO_FROM_PARSER:\n{diagnostic_str}")
            print(f"CASCADE_LARK_GRAMMAR_STRING_TO_LARK:\n{lark_grammar_str}")
        
            # Create parser
            logger.info(f"CASCADE_DEBUG: Initializing Lark with start='s' (hardcoded) using grammar:\n{lark_grammar_str}")
            self.lark_parser = Lark(
                lark_grammar_str,
                start='start',  # Use 'start' for .lark grammars like minimal_logic_gates.lark
                parser='lalr',    # Revert to LALR parser
                debug=True,
                keep_all_tokens=True
            )
            
        except LarkError as e:
            # Ensure we print the grammar that caused the failure
            if 'lark_grammar_str' in locals() and 'diagnostic_str' in locals():
                print(f"CASCADE_DIAGNOSTIC_INFO_ON_LARK_ERROR:\n{diagnostic_str}")
                print(f"CASCADE_LARK_GRAMMAR_STRING_ON_LARK_ERROR:\n{lark_grammar_str}")
        
            err_msg = f"Failed to initialize Lark parser with {self.current_grammar.filename}: {e}"
            logger.error(err_msg)
            self.lark_parser = None
            self.initialization_error_reason = err_msg
        except Exception as e: # Catch-all
            err_msg = f"Unexpected error initializing Lark parser with {self.current_grammar.filename}: {e}"
            print(f"Unexpected error initializing Lark parser with {self.current_grammar.filename}: {e}")
            logger.error(err_msg)
            self.lark_parser = None
            self.initialization_error_reason = err_msg
            raise # Re-raising the exception

    def set_grammar(self, grammar: LoadedGrammar) -> bool:
        """Set the grammar to use for parsing"""
        self.current_grammar = grammar
        self.initialization_error_reason = None # Clear previous error before attempting to init parser
        self._initialize_parser() 
        
        if self.lark_parser:
            logger.info(f"Successfully set and initialized grammar: {grammar.filename}")
            self.initialization_error_reason = None # Explicitly clear on success
            return True
        else:
            # _initialize_parser should have set initialization_error_reason if it failed.
            # If it's still None here, it means _initialize_parser didn't run or had an issue not setting it.
            if not self.initialization_error_reason:
                 self.initialization_error_reason = f"Lark parser failed to initialize for {grammar.filename} for an unknown reason after setting it."
            logger.error(f"Failed to set grammar '{grammar.filename}' due to Lark parser initialization failure. Reason: {self.initialization_error_reason}")
            return False

    def parse(self, text: str, mode: TranslationMode = TranslationMode.TAU_TO_NATURAL) -> ParseResult:
        """Parse text using current grammar"""
        if not self.lark_parser:
            logger.warning("GrammarDrivenParser.parse called but lark_parser is not initialized.")
            return ParseResult(
                success=False,
                error=self.initialization_error_reason or "Parser not initialized. Load or switch to a valid grammar."
            )

        try:
            # Parse the input
            project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
            tree = self.lark_parser.parse(text)
            
            # The GrammarDrivenTransformer is more for the translation step, 
            # not raw parsing. The raw AST is usually desired from a 'parse' method.
            # If transformation is needed here, it should be optional or a different method.
            
            return ParseResult(
                success=True,
                ast=tree # Return the raw AST from Lark
            )
            
        except UnexpectedInput as e:
            # Provide helpful error message
            context = e.get_context(text) if hasattr(e, 'get_context') else "(context unavailable)"
            error_msg = f"Parse error at line {e.line}, column {e.column}: {context}"
            if hasattr(e, 'allowed') and e.allowed:
                 # Sort for consistent error messages and handle non-string elements if any
                 allowed_terminals = sorted([str(t) for t in e.allowed])
                 error_msg += f"\nExpected one of: {', '.join(allowed_terminals)}"
            
            logger.debug(f"GrammarDrivenParser UnexpectedInput: {error_msg}")
            return ParseResult(
                success=False,
                error=error_msg,
                ast=None # Explicitly None on error
            )
        except LarkError as e: # Catch other Lark errors (e.g., UnexpectedToken, VisitError)
            logger.error(f"GrammarDrivenParser LarkError: {e}")
            return ParseResult(
                success=False,
                error=f"Lark parsing error: {e}",
                ast=None
            )
        except Exception as e:
            logger.exception("Unexpected error during parsing")
            return ParseResult(
                success=False,
                error=f"Internal error: {str(e)}"
            )
    
    def translate(self, text: str, source_lang: str, target_lang: str) -> Tuple[bool, str]:
        """High-level translation interface"""
        # Determine translation mode
        if source_lang.lower() == "tau" and target_lang.lower() in ["english", "natural"]:
            mode = TranslationMode.TAU_TO_NATURAL
        elif source_lang.lower() in ["english", "natural"] and target_lang.lower() == "tau":
            mode = TranslationMode.NATURAL_TO_TAU
        else:
            return False, f"Unsupported translation: {source_lang} to {target_lang}"
        
        # Parse and transform
        result = self.parse(text, mode)
        
        if result.success:
            # Get transformed output
            transformer = GrammarDrivenTransformer(self.current_grammar, mode)
            output = transformer.transform_tree(result.ast)
            return True, output
        else:
            return False, result.error or "Translation failed"
    
    def get_available_grammars(self) -> List[str]:
        """Get list of available grammar files"""
        return list(self.grammar_service.loaded_grammars.keys())
    
    def switch_grammar(self, filename: str) -> bool:
        """Switch to a different grammar"""
        result = self.grammar_service.set_active_grammar(filename)
        if result.is_success():
            grammar = self.grammar_service.active_grammar
            if grammar:
                return self.set_grammar(grammar)
            else:
                logger.error(f"Successfully set active grammar to '{filename}' but failed to retrieve it.")
                return False
        else:
            logger.error(f"Failed to switch grammar to '{filename}': {result.failure()}")
            return False
    
    def validate_grammar(self, grammar_content: str) -> Tuple[bool, Optional[str]]:
        """Validate a grammar without loading it"""
        try:
            # Try to create a parser with the grammar
            test_parser = Lark(
                grammar_content,
                start='program',
                parser='lalr'
            )
            return True, None
        except LarkError as e:
            return False, str(e)
    
    def get_grammar_info(self) -> Optional[Dict[str, Any]]:
        """Get information about current grammar"""
        if not self.current_grammar:
            return None
        
        return {
            'filename': self.current_grammar.filename,
            'type': self.current_grammar.type,
            'num_rules': len(self.current_grammar.rules),
            'num_terminals': len(self.current_grammar.terminals),
            'num_non_terminals': len(self.current_grammar.non_terminals),
            'is_active': self.current_grammar.is_active
        }


class GrammarDrivenTranslationStrategy(TranslationStrategy):
    """
    Translation strategy that uses grammar-driven parsing.
    
    This can be used as an alternative to pattern-based translation
    when a formal grammar is available.
    """
    
    def __init__(self):
        super().__init__()
        self.parser = GrammarDrivenParser()
    
    def translate(self, source_text: str, source_lang: str = "tau", 
                  target_lang: str = "english") -> Dict[str, Any]:
        """Translate using grammar-driven approach"""
        success, result = self.parser.translate(source_text, source_lang, target_lang)
        
        return {
            'success': success,
            'output': result if success else '',
            'error': result if not success else None,
            'method': 'grammar-driven',
            'grammar': self.parser.get_grammar_info()
        }
    
    def is_available(self) -> bool:
        """Check if grammar-driven translation is available."""
        # Availability depends on the parser having an initialized Lark parser.
        return self.parser.lark_parser is not None

    def get_availability_reason(self) -> str:
        """Returns a string explaining why the strategy is not available, if applicable."""
        if self.is_available():
            return "Grammar-driven strategy is available."
        return self.parser.initialization_error_reason or "Parser not initialized or failed to initialize."


# Example usage and testing
def demonstrate_grammar_driven_parser():
    """Demonstrate the grammar-driven parser"""
    # Initialize parser
    parser = GrammarDrivenParser()
    
    # Check available grammars
    print("Available grammars:", parser.get_available_grammars())
    
    # Example Tau expression
    tau_expr = "solve x > 5 & x < 10"
    
    # Try to parse
    result = parser.parse(tau_expr)
    
    if result.success:
        print(f"Parse successful!")
        print(f"AST: {result.ast.pretty() if result.ast else 'None'}")
    else:
        print(f"Parse failed: {result.error}")
    
    # Try translation
    success, translated = parser.translate(tau_expr, "tau", "english")
    if success:
        print(f"Translation: {translated}")
    else:
        print(f"Translation failed: {translated}")


if __name__ == "__main__":
    demonstrate_grammar_driven_parser()