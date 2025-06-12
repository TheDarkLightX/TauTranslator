"""
Refactored ILR Pattern Analyzer Module
======================================

This module contains a refactored version of the _analyze_pattern function
with reduced cyclomatic complexity by extracting sub-functions.

Author: DarkLightX / Dana Edwards
"""

import re
from typing import Tuple, Dict, Any, Optional


class ILRPatternAnalyzer:
    """Analyzes text patterns for ILR translation."""
    
    def analyze_pattern(self, text: str) -> Tuple[str, Dict[str, Any]]:
        """Analyze text to determine pattern type and extract data."""
        
        # Try pattern analyzers in order
        analyzers = [
            self._analyze_function_definition,
            self._analyze_sbf_declaration,
            self._analyze_stream_rule,
            self._analyze_temporal_operator,
            self._analyze_predicate_definition,
            self._analyze_define_function,
            self._analyze_stream_output,
            self._analyze_quantification,
            self._analyze_conditional,
            self._analyze_boolean_operation,
            self._analyze_negation,
            self._analyze_assignment,
        ]
        
        for analyzer in analyzers:
            result = analyzer(text)
            if result is not None:
                return result
        
        # If no pattern matches, return assertion type
        return "assertion", {"text": text}
    
    def _analyze_function_definition(self, text: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        """Analyze direct function definition: 'halfAdderSum(a, b) := a xor b'."""
        if ":=" not in text:
            return None
        
        parts = text.split(":=", 1)
        if len(parts) != 2:
            return None
        
        left = parts[0].strip()
        right = parts[1].strip()
        
        # Check if left side looks like a function
        if not ("(" in left and left.endswith(")")):
            return None
        
        func_match = re.match(r'(\w+)\(([^)]*)\)', left)
        if not func_match:
            return None
        
        func_name = func_match.group(1)
        params_str = func_match.group(2)
        params = [p.strip() for p in params_str.split(',') if p.strip()]
        
        return "function_definition", {
            "name": func_name,
            "params": params,
            "body": right
        }
    
    def _analyze_sbf_declaration(self, text: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        """Analyze SBF (Standard Bit Format) stream declarations."""
        if not text.startswith("sbf "):
            return None
        
        # Input stream: "sbf i1 = input file(\"input1.in\")"
        match = re.match(r'sbf (\w+) = input file\(\\?"([^"\\]+)\\?"\)', text)
        if match:
            return "sbf_input", {
                "name": match.group(1),
                "file": match.group(2)
            }
        
        # Output stream: "sbf o1 = output file(\"and.out\")"
        match = re.match(r'sbf (\w+) = output file\(\\?"([^"\\]+)\\?"\)', text)
        if match:
            return "sbf_output", {
                "name": match.group(1),
                "file": match.group(2)
            }
        
        return None
    
    def _analyze_stream_rule(self, text: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        """Analyze stream rules: 'rule o1[t] = i1[t] and i2[t]'."""
        if not text.startswith("rule "):
            return None
        
        match = re.match(r'rule (.+)', text)
        if match:
            return "stream_rule", {
                "rule": match.group(1)
            }
        
        return None
    
    def _analyze_temporal_operator(self, text: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        """Analyze temporal operators: 'always (o1[t] equals (i1[t] and i2[t]))'."""
        if not text.startswith("always "):
            return None
        
        match = re.match(r'always \((.+)\)', text)
        if match:
            return "temporal_always", {
                "condition": match.group(1)
            }
        
        return None
    
    def _analyze_predicate_definition(self, text: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        """Analyze predicate definition: 'define predicate bottom(x) as x = 0'."""
        if not text.startswith("define predicate "):
            return None
        
        match = re.match(r'define predicate (\w+)\((\w+)\) as (.+)', text)
        if match:
            return "predicate_definition", {
                "name": match.group(1),
                "param": match.group(2),
                "body": match.group(3)
            }
        
        return None
    
    def _analyze_define_function(self, text: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        """Analyze function definition: 'define function halfAdderSum(a, b) as a xor b'."""
        if not text.startswith("define function "):
            return None
        
        match = re.match(r'define function (\w+)\(([^)]+)\) as (.+)', text)
        if match:
            params = [p.strip() for p in match.group(2).split(',')]
            return "function_definition", {
                "name": match.group(1),
                "params": params,
                "body": match.group(3)
            }
        
        return None
    
    def _analyze_stream_output(self, text: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        """Analyze stream output: 'output 1 at time t = 0'."""
        if not text.startswith("output "):
            return None
        
        match = re.match(r'output (\d+) at time t = (\d+)', text)
        if match:
            return "stream_output", {
                "stream_num": int(match.group(1)),
                "time": int(match.group(2))
            }
        
        return None
    
    def _analyze_quantification(self, text: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        """Analyze universal and existential quantification."""
        # Universal quantification: "for every x such that x > 0"
        if text.startswith("for every ") or text.startswith("for all "):
            match = re.match(r'for (?:every|all) (\w+) such that (.+)', text)
            if match:
                return "universal_quantification", {
                    "variable": match.group(1),
                    "condition": match.group(2)
                }
        
        # Existential quantification: "there exists x such that x = y"
        if text.startswith("there exists "):
            match = re.match(r'there exists (\w+) such that (.+)', text)
            if match:
                return "existential_quantification", {
                    "variable": match.group(1),
                    "condition": match.group(2)
                }
        
        return None
    
    def _analyze_conditional(self, text: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        """Analyze conditional: 'if x > 5 then valid(x)'."""
        if not (text.startswith("if ") and " then " in text):
            return None
        
        match = re.match(r'if (.+) then (.+)', text)
        if match:
            return "conditional", {
                "condition": match.group(1),
                "consequence": match.group(2)
            }
        
        return None
    
    def _analyze_boolean_operation(self, text: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        """Analyze boolean operations: 'x and y or z'."""
        if " and " in text or " or " in text:
            return "boolean_operation", {"expression": text}
        
        return None
    
    def _analyze_negation(self, text: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        """Analyze negation: 'not x'."""
        if text.startswith("not "):
            return "negation", {"expression": text[4:]}
        
        return None
    
    def _analyze_assignment(self, text: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        """Analyze assignment: 'x = 5'."""
        if "=" not in text:
            return None
        
        # Exclude comparisons
        if any(op in text for op in [">", "<", "!="]):
            return None
        
        parts = text.split("=", 1)
        if len(parts) == 2:
            return "assignment", {
                "variable": parts[0].strip(),
                "value": parts[1].strip()
            }
        
        return None


# Wrapper function for compatibility
def refactored_analyze_pattern(text: str) -> Tuple[str, Dict[str, Any]]:
    """Wrapper function to maintain compatibility."""
    analyzer = ILRPatternAnalyzer()
    return analyzer.analyze_pattern(text)