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

from lark import Lark, Tree, Token, Transformer, Visitor
from lark.exceptions import LarkError, UnexpectedInput

from .tgf_grammar_loader import TGFGrammarLoader, LoadedGrammar, get_grammar_loader
from .ast.ast_nodes import ASTNode, IdentifierNode, BooleanLiteralNode, NumberLiteralNode

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


class GrammarDrivenParser:
    """
    Parser that uses dynamically loaded grammars for translation.
    
    This parser can adapt to different Tau dialects or language variations
    by loading different grammar files.
    """
    
    def __init__(self, grammar_loader: Optional[TGFGrammarLoader] = None):
        self.grammar_loader = grammar_loader or get_grammar_loader()
        self.parser: Optional[Lark] = None
        self.current_grammar: Optional[LoadedGrammar] = None
        self._initialize_parser()
    
    def _initialize_parser(self):
        """Initialize parser with active grammar"""
        grammar = self.grammar_loader.get_active_grammar()
        if grammar:
            self.set_grammar(grammar)
    
    def set_grammar(self, grammar: LoadedGrammar) -> bool:
        """Set the grammar to use for parsing"""
        try:
            # Get grammar in Lark format
            lark_grammar = self.grammar_loader.get_grammar_for_parser()
            if not lark_grammar:
                logger.error(f"Could not convert grammar {grammar.filename} to parser format")
                return False
            
            # Create parser
            self.parser = Lark(
                lark_grammar,
                start='program',  # Default start rule
                parser='lalr',    # Use LALR for better performance
                debug=True
            )
            
            self.current_grammar = grammar
            logger.info(f"Initialized parser with grammar: {grammar.filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing parser with grammar {grammar.filename}: {e}")
            return False
    
    def parse(self, text: str, mode: TranslationMode = TranslationMode.TAU_TO_NATURAL) -> ParseResult:
        """Parse text using current grammar"""
        if not self.parser or not self.current_grammar:
            return ParseResult(
                success=False,
                error="No grammar loaded"
            )
        
        try:
            # Parse the input
            tree = self.parser.parse(text)
            
            # Transform based on mode
            transformer = GrammarDrivenTransformer(self.current_grammar, mode)
            result = transformer.transform_tree(tree)
            
            return ParseResult(
                success=True,
                ast=tree
            )
            
        except UnexpectedInput as e:
            # Provide helpful error message
            error_msg = f"Parse error at line {e.line}, column {e.column}: {e}"
            if hasattr(e, 'allowed') and e.allowed:
                error_msg += f"\nExpected one of: {', '.join(e.allowed)}"
            
            return ParseResult(
                success=False,
                error=error_msg
            )
            
        except LarkError as e:
            return ParseResult(
                success=False,
                error=f"Grammar error: {str(e)}"
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
        return list(self.grammar_loader.loaded_grammars.keys())
    
    def switch_grammar(self, filename: str) -> bool:
        """Switch to a different grammar"""
        if self.grammar_loader.set_active_grammar(filename):
            grammar = self.grammar_loader.get_active_grammar()
            if grammar:
                return self.set_grammar(grammar)
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


class GrammarDrivenTranslationStrategy:
    """
    Translation strategy that uses grammar-driven parsing.
    
    This can be used as an alternative to pattern-based translation
    when a formal grammar is available.
    """
    
    def __init__(self):
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
        """Check if grammar-driven translation is available"""
        return self.parser.current_grammar is not None


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