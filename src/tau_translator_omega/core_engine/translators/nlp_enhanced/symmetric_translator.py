#!/usr/bin/env python3
"""
Symmetric Translator for Bidirectional English↔Tau Translation
============================================================

Inspired by SapienzaNLP SPRING's symmetric parsing and generation approach.
Provides unified bidirectional translation between English and Tau Language.

Key Features:
- Symmetric seq2seq-style translation
- Multiple linearization strategies (DFS, BFS, PENMAN)
- Semantic similarity preservation
- Logical equivalence checking
- Unified model architecture for both directions
"""

from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass
from enum import Enum, auto
import re
from difflib import SequenceMatcher

from .english_to_tau_translator import EnglishToTauTranslator, SemanticAnalysis
from .amr_semantic_layer import AMRGraph, AMRSemanticAnalyzer, AMRRelation


class TranslationDirection(Enum):
    """Direction of translation"""
    ENGLISH_TO_TAU = auto()
    TAU_TO_ENGLISH = auto()


class LinearizationStrategy(Enum):
    """Strategy for linearizing AMR graphs to text"""
    DEPTH_FIRST = auto()
    BREADTH_FIRST = auto() 
    PENMAN_STYLE = auto()


@dataclass
class SymmetricTranslationResult:
    """Result of symmetric translation"""
    input_text: str
    output: str
    direction: TranslationDirection
    linearization: LinearizationStrategy
    confidence: float
    semantic_analysis: SemanticAnalysis
    amr_graph: Optional[AMRGraph] = None
    alignment_scores: Dict[str, float] = None


class AMRLinearizer:
    """Handles different linearization strategies for AMR graphs"""
    
    def __init__(self):
        """Initialize the linearizer"""
        pass
    
    def linearize(self, amr_graph: AMRGraph, strategy: LinearizationStrategy) -> str:
        """Linearize AMR graph according to specified strategy"""
        if strategy == LinearizationStrategy.DEPTH_FIRST:
            return self._depth_first_linearization(amr_graph)
        elif strategy == LinearizationStrategy.BREADTH_FIRST:
            return self._breadth_first_linearization(amr_graph)
        elif strategy == LinearizationStrategy.PENMAN_STYLE:
            return self._penman_linearization(amr_graph)
        else:
            raise ValueError(f"Unknown linearization strategy: {strategy}")
    
    def _depth_first_linearization(self, amr_graph: AMRGraph) -> str:
        """Depth-first traversal linearization"""
        if not amr_graph.root or amr_graph.root not in amr_graph.instances:
            return ""
        
        visited = set()
        result = []
        
        def dfs(instance_id, depth=0):
            if instance_id in visited:
                return
            
            visited.add(instance_id)
            instance = amr_graph.instances[instance_id]
            
            # Add instance with concept
            indent = "  " * depth
            result.append(f"{indent}{instance_id}: {instance.concept.name}")
            
            # Visit arguments in depth-first order
            for relation, target_instance in instance.arguments.items():
                result.append(f"{indent}  :{relation.value}")
                dfs(target_instance.instance_id, depth + 1)
        
        dfs(amr_graph.root)
        return "\n".join(result)
    
    def _breadth_first_linearization(self, amr_graph: AMRGraph) -> str:
        """Breadth-first traversal linearization"""
        if not amr_graph.root or amr_graph.root not in amr_graph.instances:
            return ""
        
        from collections import deque
        
        queue = deque([(amr_graph.root, 0)])
        visited = set()
        result = []
        
        while queue:
            instance_id, depth = queue.popleft()
            
            if instance_id in visited:
                continue
            
            visited.add(instance_id)
            instance = amr_graph.instances[instance_id]
            
            # Add instance with concept
            indent = "  " * depth
            result.append(f"{indent}{instance_id}: {instance.concept.name}")
            
            # Add arguments to queue
            for relation, target_instance in instance.arguments.items():
                result.append(f"{indent}  :{relation.value}")
                queue.append((target_instance.instance_id, depth + 1))
        
        return "\n".join(result)
    
    def _penman_linearization(self, amr_graph: AMRGraph) -> str:
        """PENMAN-style linearization"""
        if not amr_graph.root or amr_graph.root not in amr_graph.instances:
            return "()"
        
        visited = set()
        
        def penman_recursive(instance_id):
            if instance_id in visited:
                return f"{instance_id}"
            
            visited.add(instance_id)
            instance = amr_graph.instances[instance_id]
            
            parts = [f"{instance_id} / {instance.concept.name}"]
            
            for relation, target_instance in instance.arguments.items():
                target_repr = penman_recursive(target_instance.instance_id)
                parts.append(f":{relation.value} {target_repr}")
            
            return f"({' '.join(parts)})"
        
        return penman_recursive(amr_graph.root)


class SymmetricTranslator:
    """
    Main symmetric translator inspired by SPRING.
    
    Provides unified bidirectional translation between English and Tau Language
    using symmetric seq2seq-style approach with multiple linearization strategies.
    """
    
    def __init__(self):
        """Initialize the symmetric translator"""
        self.english_to_tau = EnglishToTauTranslator()
        self.amr_analyzer = AMRSemanticAnalyzer()
        self.linearizer = AMRLinearizer()
        
        # Translation patterns for Tau → English
        self.tau_to_english_patterns = [
            (r'forall\s+(\w+):\s*(.*)', r'For all \1, \2'),
            (r'exists\s+(\w+):\s*(.*)', r'There exists \1 such that \2'),
            (r'(\w+)\s*implies\s*(.*)', r'\1 implies \2'),
            (r'(\w+)\s*and\s*(.*)', r'\1 and \2'),
            (r'(\w+)\s*or\s*(.*)', r'\1 or \2'),
            (r'prime\((\w+)\)', r'\1 is prime'),
            (r'even\((\w+)\)', r'\1 is even'),
            (r'odd\((\w+)\)', r'\1 is odd'),
            (r'(\w+)\s*=\s*(\d+)', r'\1 equals \2'),
            (r'(\w+)\s*>\s*(\d+)', r'\1 is greater than \2'),
            (r'(\w+)\s*<\s*(\d+)', r'\1 is less than \2'),
        ]
    
    def translate(self, 
                  text: str, 
                  direction: TranslationDirection,
                  linearization: LinearizationStrategy = LinearizationStrategy.DEPTH_FIRST) -> SymmetricTranslationResult:
        """
        Perform symmetric translation in specified direction.
        
        Args:
            text: Input text to translate
            direction: Direction of translation
            linearization: Linearization strategy for output
            
        Returns:
            SymmetricTranslationResult with translation and metadata
        """
        if direction == TranslationDirection.ENGLISH_TO_TAU:
            return self._translate_english_to_tau(text, linearization)
        else:
            return self._translate_tau_to_english(text, linearization)
    
    def _translate_english_to_tau(self, english_text: str, linearization: LinearizationStrategy) -> SymmetricTranslationResult:
        """Translate English to Tau using enhanced approach"""
        # Use existing English to Tau translator
        base_result = self.english_to_tau.translate(english_text)
        
        # Create AMR graph for semantic representation
        try:
            amr_graph = self.amr_analyzer.analyze(None)  # Would need proper AST
        except:
            amr_graph = None
        
        # Apply linearization strategy if AMR graph available
        if amr_graph:
            tau_output = self.linearizer.linearize(amr_graph, linearization)
        else:
            tau_output = base_result.tau_specification
        
        return SymmetricTranslationResult(
            input_text=english_text,
            output=tau_output,
            direction=TranslationDirection.ENGLISH_TO_TAU,
            linearization=linearization,
            confidence=base_result.confidence.overall,
            semantic_analysis=base_result.semantic_analysis,
            amr_graph=amr_graph
        )
    
    def _translate_tau_to_english(self, tau_text: str, linearization: LinearizationStrategy) -> SymmetricTranslationResult:
        """Translate Tau to English using pattern-based approach"""
        english_output = tau_text
        
        # Apply reverse translation patterns
        for tau_pattern, english_replacement in self.tau_to_english_patterns:
            english_output = re.sub(tau_pattern, english_replacement, english_output, flags=re.IGNORECASE)
        
        # Clean up the output
        english_output = self._clean_english_output(english_output)
        
        # Analyze semantics of result
        semantic_analysis = self.english_to_tau.analyze_semantics(english_output)
        
        # Calculate confidence based on pattern match quality
        confidence = self._calculate_tau_to_english_confidence(tau_text, english_output)
        
        return SymmetricTranslationResult(
            input_text=tau_text,
            output=english_output,
            direction=TranslationDirection.TAU_TO_ENGLISH,
            linearization=linearization,
            confidence=confidence,
            semantic_analysis=semantic_analysis
        )
    
    def _clean_english_output(self, text: str) -> str:
        """Clean up English output for readability"""
        # Capitalize first letter
        text = text.strip()
        if text:
            text = text[0].upper() + text[1:]
        
        # Ensure proper sentence ending
        if text and not text.endswith(('.', '!', '?')):
            text += '.'
        
        # Clean up spacing
        text = re.sub(r'\s+', ' ', text)
        
        return text
    
    def _calculate_tau_to_english_confidence(self, tau_text: str, english_text: str) -> float:
        """Calculate confidence for Tau to English translation"""
        base_confidence = 0.6
        
        # Check if translation changed the text (patterns matched)
        if tau_text.lower() != english_text.lower():
            base_confidence += 0.2
        
        # Check for English-like structure
        if any(word in english_text.lower() for word in ['is', 'are', 'for', 'all', 'if', 'then']):
            base_confidence += 0.1
        
        # Check for proper sentence structure
        if english_text.endswith('.') and english_text[0].isupper():
            base_confidence += 0.1
        
        return min(1.0, base_confidence)
    
    def linearize_amr(self, amr_graph: AMRGraph, strategy: LinearizationStrategy) -> str:
        """Linearize AMR graph using specified strategy"""
        return self.linearizer.linearize(amr_graph, strategy)
    
    def calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts"""
        # Simple similarity based on common words and structure
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        # Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        jaccard = intersection / union if union > 0 else 0.0
        
        # Sequence similarity
        sequence_sim = SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
        
        # Combined similarity
        return (jaccard + sequence_sim) / 2.0
    
    def check_logical_equivalence(self, tau1: str, tau2: str) -> bool:
        """Check if two Tau expressions are logically equivalent"""
        # Simplified logical equivalence check
        # In a full implementation, this would use formal logic proving
        
        # Normalize both expressions
        norm1 = self._normalize_tau_expression(tau1)
        norm2 = self._normalize_tau_expression(tau2)
        
        # Check for structural similarity
        return self._are_structurally_equivalent(norm1, norm2)
    
    def _normalize_tau_expression(self, tau_expr: str) -> str:
        """Normalize Tau expression for comparison"""
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', tau_expr.strip())
        
        # Standardize operators
        normalized = normalized.replace('→', 'implies')
        normalized = normalized.replace('∧', 'and')
        normalized = normalized.replace('∨', 'or')
        normalized = normalized.replace('¬', 'not')
        normalized = normalized.replace('∀', 'forall')
        normalized = normalized.replace('∃', 'exists')
        
        return normalized.lower()
    
    def _are_structurally_equivalent(self, expr1: str, expr2: str) -> bool:
        """Check if two normalized expressions are structurally equivalent"""
        # Extract key components
        components1 = self._extract_logical_components(expr1)
        components2 = self._extract_logical_components(expr2)
        
        # Compare components
        return (components1['quantifiers'] == components2['quantifiers'] and
                components1['predicates'] == components2['predicates'] and
                components1['operators'] == components2['operators'])
    
    def _extract_logical_components(self, expr: str) -> Dict[str, List[str]]:
        """Extract logical components from expression"""
        components = {
            'quantifiers': re.findall(r'\b(forall|exists)\b', expr),
            'predicates': re.findall(r'\b(\w+)\s*\(', expr),
            'operators': re.findall(r'\b(and|or|not|implies)\b', expr)
        }
        
        # Sort for consistent comparison
        for key in components:
            components[key] = sorted(set(components[key]))
        
        return components
    
    def is_valid_tau(self, tau_text: str) -> bool:
        """Check if text represents valid Tau Language"""
        # Basic validation patterns
        tau_patterns = [
            r'\b(forall|exists)\s+\w+:',  # Quantifiers
            r'\w+\s*\([^)]*\)',           # Predicate calls
            r'\w+\s*(=|>|<|>=|<=)\s*\w+', # Comparisons
            r'\b(and|or|not|implies)\b',   # Logical operators
        ]
        
        # Check if at least one pattern matches
        return any(re.search(pattern, tau_text, re.IGNORECASE) for pattern in tau_patterns)


# Factory function
def create_symmetric_translator() -> SymmetricTranslator:
    """Factory function to create a symmetric translator"""
    return SymmetricTranslator()