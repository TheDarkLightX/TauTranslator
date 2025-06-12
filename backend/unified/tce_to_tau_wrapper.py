"""
TCE to Tau Wrapper - Fixes compatibility issues
Copyright: DarkLightX/Dana Edwards
"""

from typing import Any, List
from dataclasses import dataclass
import copy

from src.tau_translator_omega.core_engine.tce_tau_translator import TCETauTranslator, TranslationResult


class TCEToTauWrapper:
    """Wrapper that fixes compatibility issues in TCE to Tau translation."""
    
    def __init__(self):
        self.translator = TCETauTranslator()
    
    def translate(self, ast_node: Any) -> TranslationResult:
        """Translate AST node to Tau, fixing known issues."""
        # Fix SentenceNode issue where content is not iterable
        if type(ast_node).__name__ == 'SentenceNode':
            # Create a copy to avoid mutating original
            ast_node = copy.deepcopy(ast_node)
            ast_node = self._fix_sentence_node(ast_node)
        
        return self.translator.translate(ast_node)
    
    def _fix_sentence_node(self, node: Any) -> Any:
        """Fix SentenceNode to ensure content is iterable."""
        if hasattr(node, 'content'):
            # If content is not a list, make it one
            if not isinstance(node.content, list):
                node.content = [node.content]
            # Also handle case where content might be None
            elif node.content is None:
                node.content = []
        
        return node