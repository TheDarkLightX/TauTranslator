"""
Repository of linguistic patterns for requirement analysis.

Copyright: DarkLightX / Dana Edwards
"""

from typing import Dict, List, Tuple
from .domain_types import RequirementType


class PatternRepository:
    """Repository of linguistic patterns for requirement analysis."""
    
    @staticmethod
    def get_requirement_indicators() -> Dict[RequirementType, List[str]]:
        """Get indicators for each requirement type."""
        return {
            RequirementType.CONSTRAINT: ["must", "shall", "should", "required", "mandatory"],
            RequirementType.BEHAVIOR: ["when", "if", "upon", "during", "while"],
            RequirementType.PERFORMANCE: ["within", "seconds", "milliseconds", "response time", "throughput"],
            RequirementType.VALIDATION: ["validate", "verify", "check", "ensure", "confirm"],
            RequirementType.OUTPUT: ["output", "return", "display", "show", "report"],
            RequirementType.SECURITY: ["authenticate", "authorize", "secure", "access", "permission"],
            RequirementType.EXCEPTION: ["except", "unless", "however", "but", "special case"]
        }
    
    @staticmethod
    def get_quantifier_patterns() -> List[str]:
        """Get quantifier regex patterns."""
        return [
            r'\b(all|every|each|any|some|for all|for every)\b',
            r'\b(∀|∃|forall|exists)\b',
            r'\bfor\s+any\s+(\w+)\b'
        ]
    
    @staticmethod
    def get_conditional_patterns() -> List[str]:
        """Get conditional regex patterns."""
        return [
            r'\b(if|when|whenever|provided that|given that)\b',
            r'\b(then|implies|therefore|consequently)\b'
        ]
    
    @staticmethod
    def get_logical_operator_patterns() -> List[str]:
        """Get logical operator regex patterns."""
        return [
            r'\b(and|or|not|but|except|unless)\b',
            r'[∧∨¬→↔]'
        ]
    
    @staticmethod
    def get_temporal_patterns() -> List[str]:
        """Get temporal regex patterns."""
        return [
            r'\b(before|after|during|while|until|since)\b',
            r'\b(within \d+|in \d+|after \d+)\s*(seconds?|minutes?|hours?|milliseconds?)\b'
        ]
    
    @staticmethod
    def get_mathematical_patterns() -> List[Tuple[str, str]]:
        """Get mathematical constraint patterns."""
        return [
            (r'(\w+)\s+(?:is|equals?|=)\s+(\d+)', 'equality'),
            (r'(\w+)\s+(?:is\s+)?(?:greater\s+than?|>)\s+(\d+)', 'greater_than'),
            (r'(\w+)\s+(?:is\s+)?(?:less\s+than?|<)\s+(\d+)', 'less_than'),
            (r'(\w+)\s+(?:is\s+)?prime', 'prime'),
            (r'(\w+)\s+(?:is\s+)?even', 'even'),
            (r'(\w+)\s+(?:is\s+)?odd', 'odd')
        ]