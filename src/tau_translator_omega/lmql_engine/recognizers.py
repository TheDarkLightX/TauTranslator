"""
Pattern Recognizers for Specialized Tau Constructs
=================================================

Implements specialized recognizers for various Tau language patterns
including arithmetic, streaming, logic gates, consensus, and temporal operations.

Author: DarkLightX / Dana Edwards
"""

import re
import logging
from typing import Dict, List, Tuple, Optional, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

# Import pattern cache for efficient regex compilation
from ..core_engine.pattern_cache import get_pattern, precompile_patterns

logger = logging.getLogger(__name__)


@dataclass
class RecognitionResult:
    """Result of pattern recognition."""
    recognized: bool
    pattern_type: str
    components: Dict[str, Any]
    confidence: float
    translation_hint: Optional[str] = None


class PatternRecognizer(ABC):
    """Abstract base class for pattern recognizers."""
    
    @abstractmethod
    def recognize(self, text: str) -> RecognitionResult:
        """Recognize pattern in text."""
        pass
    
    @abstractmethod
    def translate_to_tce(self, result: RecognitionResult) -> str:
        """Translate recognized pattern to TCE."""
        pass
    
    @abstractmethod
    def translate_to_tau(self, result: RecognitionResult) -> str:
        """Translate recognized pattern to Tau."""
        pass


class BinaryArithmeticRecognizer(PatternRecognizer):
    """
    Recognizes binary arithmetic patterns like adders and multipliers.
    
    Examples:
    - adder[n] := i1[n] + i2[n]
    - multiplier[n] := i1[n] * i2[n]
    - full_adder with carry operations
    """
    
    def __init__(self):
        self._patterns = self._initialize_patterns()
        # Precompile all patterns for better performance
        precompile_patterns(self._patterns)
    
    def _initialize_patterns(self) -> Dict[str, str]:
        """Initialize arithmetic pattern definitions."""
        return {
            # Simple binary operations
            'simple_adder': r'([a-zA-Z_][a-zA-Z0-9_]*)\[([^]]+)\]\s*:=\s*([a-zA-Z0-9_]+)\[([^]]+)\]\s*\+\s*([a-zA-Z0-9_]+)\[([^]]+)\]',
            'simple_multiplier': r'([a-zA-Z_][a-zA-Z0-9_]*)\[([^]]+)\]\s*:=\s*([a-zA-Z0-9_]+)\[([^]]+)\]\s*\*\s*([a-zA-Z0-9_]+)\[([^]]+)\]',
            'simple_subtractor': r'([a-zA-Z_][a-zA-Z0-9_]*)\[([^]]+)\]\s*:=\s*([a-zA-Z0-9_]+)\[([^]]+)\]\s*-\s*([a-zA-Z0-9_]+)\[([^]]+)\]',
            
            # Full adder with carry
            'full_adder_sum': r'([a-zA-Z_][a-zA-Z0-9_]*)\[([^]]+)\]\s*:=\s*([a-zA-Z0-9_]+)\[([^]]+)\]\s*\+\s*([a-zA-Z0-9_]+)\[([^]]+)\]\s*\+\s*([a-zA-Z0-9_]+)\[([^]]+)\]',
            'full_adder_carry': r'carry_out\[([^]]+)\]\s*:=\s*\(\s*([a-zA-Z0-9_]+)\[([^]]+)\]\s*&\s*([a-zA-Z0-9_]+)\[([^]]+)\]\s*\)\s*\|\s*\(\s*carry_in\[([^]]+)\]\s*&\s*\(\s*([a-zA-Z0-9_]+)\[([^]]+)\]\s*\+\s*([a-zA-Z0-9_]+)\[([^]]+)\]\s*\)\s*\)',
            
            # Accumulator pattern
            'accumulator': r'([a-zA-Z_][a-zA-Z0-9_]*)\[([^]]+)\]\s*:=\s*([a-zA-Z_][a-zA-Z0-9_]*)\[([^]]+)\]\s*\+\s*([a-zA-Z0-9_]+)\[([^]]+)\]',
            
            # Modulo arithmetic
            'modulo_op': r'([a-zA-Z_][a-zA-Z0-9_]*)\[([^]]+)\]\s*:=\s*([a-zA-Z0-9_]+)\[([^]]+)\]\s*%\s*([a-zA-Z0-9_]+)\[([^]]+)\]',
            
            # Bitwise operations
            'bitwise_and': r'([a-zA-Z_][a-zA-Z0-9_]*)\[([^]]+)\]\s*:=\s*([a-zA-Z0-9_]+)\[([^]]+)\]\s*&\s*([a-zA-Z0-9_]+)\[([^]]+)\]',
            'bitwise_or': r'([a-zA-Z_][a-zA-Z0-9_]*)\[([^]]+)\]\s*:=\s*([a-zA-Z0-9_]+)\[([^]]+)\]\s*\|\s*([a-zA-Z0-9_]+)\[([^]]+)\]',
            'bitwise_xor': r'([a-zA-Z_][a-zA-Z0-9_]*)\[([^]]+)\]\s*:=\s*([a-zA-Z0-9_]+)\[([^]]+)\]\s*\^\s*([a-zA-Z0-9_]+)\[([^]]+)\]',
        }
    
    def recognize(self, text: str) -> RecognitionResult:
        """Recognize binary arithmetic patterns in text."""
        text = text.strip()
        
        # Try patterns in a specific order - more specific patterns first
        pattern_order = [
            'full_adder_sum', 'full_adder_carry',  # Most specific
            'accumulator',  # Has self-reference, check before simple ops
            'simple_adder', 'simple_multiplier', 'simple_subtractor',
            'modulo_op', 'bitwise_and', 'bitwise_or', 'bitwise_xor'
        ]
        
        for pattern_name in pattern_order:
            if pattern_name not in self._patterns:
                continue
            pattern_regex = self._patterns[pattern_name]
            # Use cached compiled pattern
            compiled_pattern = get_pattern(pattern_regex)
            match = compiled_pattern.match(text)
            if match:
                groups = match.groups()
                
                if pattern_name == 'simple_adder':
                    return RecognitionResult(
                        recognized=True,
                        pattern_type='adder',
                        components={
                            'output': groups[0],
                            'output_time': groups[1],
                            'input1': groups[2],
                            'input1_time': groups[3],
                            'input2': groups[4],
                            'input2_time': groups[5]
                        },
                        confidence=0.95,
                        translation_hint='binary_addition'
                    )
                
                elif pattern_name == 'simple_multiplier':
                    return RecognitionResult(
                        recognized=True,
                        pattern_type='multiplier',
                        components={
                            'output': groups[0],
                            'output_time': groups[1],
                            'input1': groups[2],
                            'input1_time': groups[3],
                            'input2': groups[4],
                            'input2_time': groups[5]
                        },
                        confidence=0.95,
                        translation_hint='binary_multiplication'
                    )
                
                elif pattern_name == 'accumulator':
                    # Check if it's truly an accumulator (same variable on both sides)
                    if groups[0] == groups[2]:
                        return RecognitionResult(
                            recognized=True,
                            pattern_type='accumulator',
                            components={
                                'accumulator': groups[0],
                                'current_time': groups[1],
                                'accumulator_prev': groups[2],
                                'prev_time': groups[3],
                                'input': groups[4],
                                'input_time': groups[5]
                            },
                            confidence=0.9,
                            translation_hint='accumulation'
                        )
                
                elif pattern_name == 'full_adder_sum':
                    return RecognitionResult(
                        recognized=True,
                        pattern_type='full_adder_sum',
                        components={
                            'sum': groups[0],
                            'sum_time': groups[1],
                            'a': groups[2],
                            'a_time': groups[3],
                            'b': groups[4],
                            'b_time': groups[5],
                            'carry_in': groups[6],
                            'carry_time': groups[7]
                        },
                        confidence=0.9,
                        translation_hint='full_adder_sum'
                    )
                
                elif pattern_name == 'simple_subtractor':
                    return RecognitionResult(
                        recognized=True,
                        pattern_type='subtractor',
                        components={
                            'output': groups[0],
                            'output_time': groups[1],
                            'input1': groups[2],
                            'input1_time': groups[3],
                            'input2': groups[4],
                            'input2_time': groups[5]
                        },
                        confidence=0.95,
                        translation_hint='binary_subtraction'
                    )
                
                elif pattern_name == 'modulo_op':
                    return RecognitionResult(
                        recognized=True,
                        pattern_type='modulo',
                        components={
                            'output': groups[0],
                            'output_time': groups[1],
                            'input1': groups[2],
                            'input1_time': groups[3],
                            'input2': groups[4],
                            'input2_time': groups[5]
                        },
                        confidence=0.9,
                        translation_hint='modulo_operation'
                    )
                
                elif pattern_name.startswith('bitwise_'):
                    op_type = pattern_name.split('_')[1]  # and, or, xor
                    return RecognitionResult(
                        recognized=True,
                        pattern_type=f'bitwise_{op_type}',
                        components={
                            'output': groups[0],
                            'output_time': groups[1],
                            'input1': groups[2],
                            'input1_time': groups[3],
                            'input2': groups[4],
                            'input2_time': groups[5]
                        },
                        confidence=0.9,
                        translation_hint=f'bitwise_{op_type}_operation'
                    )
        
        # No pattern matched
        return RecognitionResult(
            recognized=False,
            pattern_type='unknown',
            components={},
            confidence=0.0
        )
    
    def translate_to_tce(self, result: RecognitionResult) -> str:
        """Translate recognized pattern to TCE."""
        if not result.recognized:
            return ""
        
        c = result.components
        
        if result.pattern_type == 'adder':
            return f"The {c['output']} at time {c['output_time']} equals {c['input1']} at time {c['input1_time']} plus {c['input2']} at time {c['input2_time']}."
        
        elif result.pattern_type == 'multiplier':
            return f"The {c['output']} at time {c['output_time']} equals {c['input1']} at time {c['input1_time']} times {c['input2']} at time {c['input2_time']}."
        
        elif result.pattern_type == 'accumulator':
            return f"The {c['accumulator']} at time {c['current_time']} equals {c['accumulator_prev']} at time {c['prev_time']} plus {c['input']} at time {c['input_time']}."
        
        elif result.pattern_type == 'full_adder_sum':
            return f"The {c['sum']} at time {c['sum_time']} equals {c['a']} at time {c['a_time']} plus {c['b']} at time {c['b_time']} plus {c['carry_in']} at time {c['carry_time']}."
        
        elif result.pattern_type == 'subtractor':
            return f"The {c['output']} at time {c['output_time']} equals {c['input1']} at time {c['input1_time']} minus {c['input2']} at time {c['input2_time']}."
        
        elif result.pattern_type == 'modulo':
            return f"The {c['output']} at time {c['output_time']} equals {c['input1']} at time {c['input1_time']} modulo {c['input2']} at time {c['input2_time']}."
        
        elif result.pattern_type.startswith('bitwise_'):
            op_word = {
                'bitwise_and': 'bitwise AND',
                'bitwise_or': 'bitwise OR',
                'bitwise_xor': 'bitwise XOR'
            }.get(result.pattern_type, result.pattern_type)
            return f"The {c['output']} at time {c['output_time']} equals {c['input1']} at time {c['input1_time']} {op_word} {c['input2']} at time {c['input2_time']}."
        
        return ""
    
    def translate_to_tau(self, result: RecognitionResult) -> str:
        """Translate recognized pattern to Tau."""
        if not result.recognized:
            return ""
        
        c = result.components
        
        if result.pattern_type == 'adder':
            return f"{c['output']}[{c['output_time']}] := {c['input1']}[{c['input1_time']}] + {c['input2']}[{c['input2_time']}]"
        
        elif result.pattern_type == 'multiplier':
            return f"{c['output']}[{c['output_time']}] := {c['input1']}[{c['input1_time']}] * {c['input2']}[{c['input2_time']}]"
        
        elif result.pattern_type == 'accumulator':
            return f"{c['accumulator']}[{c['current_time']}] := {c['accumulator_prev']}[{c['prev_time']}] + {c['input']}[{c['input_time']}]"
        
        elif result.pattern_type == 'full_adder_sum':
            return f"{c['sum']}[{c['sum_time']}] := {c['a']}[{c['a_time']}] + {c['b']}[{c['b_time']}] + {c['carry_in']}[{c['carry_time']}]"
        
        elif result.pattern_type == 'subtractor':
            return f"{c['output']}[{c['output_time']}] := {c['input1']}[{c['input1_time']}] - {c['input2']}[{c['input2_time']}]"
        
        elif result.pattern_type == 'modulo':
            return f"{c['output']}[{c['output_time']}] := {c['input1']}[{c['input1_time']}] % {c['input2']}[{c['input2_time']}]"
        
        elif result.pattern_type == 'bitwise_and':
            return f"{c['output']}[{c['output_time']}] := {c['input1']}[{c['input1_time']}] & {c['input2']}[{c['input2_time']}]"
        
        elif result.pattern_type == 'bitwise_or':
            return f"{c['output']}[{c['output_time']}] := {c['input1']}[{c['input1_time']}] | {c['input2']}[{c['input2_time']}]"
        
        elif result.pattern_type == 'bitwise_xor':
            return f"{c['output']}[{c['output_time']}] := {c['input1']}[{c['input1_time']}] ^ {c['input2']}[{c['input2_time']}]"
        
        return ""


class StreamRecognizer(PatternRecognizer):
    """
    Recognizes stream I/O patterns.
    
    Examples:
    - input_file(n) from "./data.txt"
    - output_file(n) to "./results.txt"
    - console_stream(n) from STDIN
    """
    
    def __init__(self):
        self._patterns = self._initialize_patterns()
        # Precompile all patterns
        precompile_patterns(self._patterns)
    
    def _initialize_patterns(self) -> Dict[str, str]:
        """Initialize stream pattern definitions."""
        return {
            # Input patterns
            'input_file': r'([a-zA-Z_][a-zA-Z0-9_]*)\s*\(\s*([^)]+)\s*\)\s+from\s+"([^"]+)"',
            'input_stdin': r'([a-zA-Z_][a-zA-Z0-9_]*)\s*\(\s*([^)]+)\s*\)\s+from\s+STDIN',
            'input_sensor': r'([a-zA-Z_][a-zA-Z0-9_]*)\s*\(\s*([^)]+)\s*\)\s+from\s+sensor\s+"([^"]+)"',
            
            # Output patterns
            'output_file': r'([a-zA-Z_][a-zA-Z0-9_]*)\s*\(\s*([^)]+)\s*\)\s+to\s+"([^"]+)"',
            'output_stdout': r'([a-zA-Z_][a-zA-Z0-9_]*)\s*\(\s*([^)]+)\s*\)\s+to\s+STDOUT',
            'output_device': r'([a-zA-Z_][a-zA-Z0-9_]*)\s*\(\s*([^)]+)\s*\)\s+to\s+device\s+"([^"]+)"',
            
            # Bidirectional patterns
            'pipe_stream': r'([a-zA-Z_][a-zA-Z0-9_]*)\s*\(\s*([^)]+)\s*\)\s+pipe\s+"([^"]+)"',
            'socket_stream': r'([a-zA-Z_][a-zA-Z0-9_]*)\s*\(\s*([^)]+)\s*\)\s+socket\s+"([^"]+)"',
        }
    
    def recognize(self, text: str) -> RecognitionResult:
        """Recognize stream I/O patterns in text."""
        text = text.strip()
        
        for pattern_name, pattern_regex in self._patterns.items():
            compiled_pattern = get_pattern(pattern_regex)
            match = compiled_pattern.match(text)
            if match:
                groups = match.groups()
                
                if pattern_name == 'input_file':
                    return RecognitionResult(
                        recognized=True,
                        pattern_type='input_file_stream',
                        components={
                            'stream_name': groups[0],
                            'time_var': groups[1],
                            'file_path': groups[2]
                        },
                        confidence=0.95,
                        translation_hint='file_input'
                    )
                
                elif pattern_name == 'output_file':
                    return RecognitionResult(
                        recognized=True,
                        pattern_type='output_file_stream',
                        components={
                            'stream_name': groups[0],
                            'time_var': groups[1],
                            'file_path': groups[2]
                        },
                        confidence=0.95,
                        translation_hint='file_output'
                    )
                
                elif pattern_name == 'input_stdin':
                    return RecognitionResult(
                        recognized=True,
                        pattern_type='stdin_stream',
                        components={
                            'stream_name': groups[0],
                            'time_var': groups[1]
                        },
                        confidence=0.95,
                        translation_hint='stdin_input'
                    )
                
                elif pattern_name == 'output_stdout':
                    return RecognitionResult(
                        recognized=True,
                        pattern_type='stdout_stream',
                        components={
                            'stream_name': groups[0],
                            'time_var': groups[1]
                        },
                        confidence=0.95,
                        translation_hint='stdout_output'
                    )
                
                elif pattern_name == 'input_sensor':
                    return RecognitionResult(
                        recognized=True,
                        pattern_type='sensor_stream',
                        components={
                            'stream_name': groups[0],
                            'time_var': groups[1],
                            'sensor_id': groups[2]
                        },
                        confidence=0.9,
                        translation_hint='sensor_input'
                    )
        
        return RecognitionResult(
            recognized=False,
            pattern_type='unknown',
            components={},
            confidence=0.0
        )
    
    def translate_to_tce(self, result: RecognitionResult) -> str:
        """Translate recognized pattern to TCE."""
        if not result.recognized:
            return ""
        
        c = result.components
        
        if result.pattern_type == 'input_file_stream':
            return f"The stream {c['stream_name']} at time {c['time_var']} reads from file \"{c['file_path']}\"."
        
        elif result.pattern_type == 'output_file_stream':
            return f"The stream {c['stream_name']} at time {c['time_var']} writes to file \"{c['file_path']}\"."
        
        elif result.pattern_type == 'stdin_stream':
            return f"The stream {c['stream_name']} at time {c['time_var']} reads from standard input."
        
        elif result.pattern_type == 'stdout_stream':
            return f"The stream {c['stream_name']} at time {c['time_var']} writes to standard output."
        
        elif result.pattern_type == 'sensor_stream':
            return f"The stream {c['stream_name']} at time {c['time_var']} reads from sensor \"{c['sensor_id']}\"."
        
        return ""
    
    def translate_to_tau(self, result: RecognitionResult) -> str:
        """Translate recognized pattern to Tau."""
        if not result.recognized:
            return ""
        
        c = result.components
        
        if result.pattern_type == 'input_file_stream':
            return f"{c['stream_name']}({c['time_var']}) from \"{c['file_path']}\""
        
        elif result.pattern_type == 'output_file_stream':
            return f"{c['stream_name']}({c['time_var']}) to \"{c['file_path']}\""
        
        elif result.pattern_type == 'stdin_stream':
            return f"{c['stream_name']}({c['time_var']}) from STDIN"
        
        elif result.pattern_type == 'stdout_stream':
            return f"{c['stream_name']}({c['time_var']}) to STDOUT"
        
        elif result.pattern_type == 'sensor_stream':
            return f"{c['stream_name']}({c['time_var']}) from sensor \"{c['sensor_id']}\""
        
        return ""


class LogicGateRecognizer(PatternRecognizer):
    """
    Recognizes logic gate patterns.
    
    Examples:
    - and_gate[t] := a[t] & b[t]
    - or_gate[t] := a[t] | b[t]
    - not_gate[t] := ~a[t]
    """
    
    def __init__(self):
        self._patterns = self._initialize_patterns()
        # Precompile all patterns
        precompile_patterns(self._patterns)
    
    def _initialize_patterns(self) -> Dict[str, str]:
        """Initialize logic gate pattern definitions."""
        return {
            # Basic gates
            'and_gate': r'([a-zA-Z_][a-zA-Z0-9_]*)\[([^]]+)\]\s*:=\s*([a-zA-Z0-9_]+)\[([^]]+)\]\s*&\s*([a-zA-Z0-9_]+)\[([^]]+)\]',
            'or_gate': r'([a-zA-Z_][a-zA-Z0-9_]*)\[([^]]+)\]\s*:=\s*([a-zA-Z0-9_]+)\[([^]]+)\]\s*\|\s*([a-zA-Z0-9_]+)\[([^]]+)\]',
            'not_gate': r'([a-zA-Z_][a-zA-Z0-9_]*)\[([^]]+)\]\s*:=\s*~\s*([a-zA-Z0-9_]+)\[([^]]+)\]',
            'xor_gate': r'([a-zA-Z_][a-zA-Z0-9_]*)\[([^]]+)\]\s*:=\s*([a-zA-Z0-9_]+)\[([^]]+)\]\s*\^\s*([a-zA-Z0-9_]+)\[([^]]+)\]',
            
            # Compound gates
            'nand_gate': r'([a-zA-Z_][a-zA-Z0-9_]*)\[([^]]+)\]\s*:=\s*~\s*\(\s*([a-zA-Z0-9_]+)\[([^]]+)\]\s*&\s*([a-zA-Z0-9_]+)\[([^]]+)\]\s*\)',
            'nor_gate': r'([a-zA-Z_][a-zA-Z0-9_]*)\[([^]]+)\]\s*:=\s*~\s*\(\s*([a-zA-Z0-9_]+)\[([^]]+)\]\s*\|\s*([a-zA-Z0-9_]+)\[([^]]+)\]\s*\)',
            
            # Multi-input variations
            'and3_gate': r'([a-zA-Z_][a-zA-Z0-9_]*)\[([^]]+)\]\s*:=\s*([a-zA-Z0-9_]+)\[([^]]+)\]\s*&\s*([a-zA-Z0-9_]+)\[([^]]+)\]\s*&\s*([a-zA-Z0-9_]+)\[([^]]+)\]',
            'or3_gate': r'([a-zA-Z_][a-zA-Z0-9_]*)\[([^]]+)\]\s*:=\s*([a-zA-Z0-9_]+)\[([^]]+)\]\s*\|\s*([a-zA-Z0-9_]+)\[([^]]+)\]\s*\|\s*([a-zA-Z0-9_]+)\[([^]]+)\]',
        }
    
    def recognize(self, text: str) -> RecognitionResult:
        """Recognize logic gate patterns in text."""
        text = text.strip()
        
        for pattern_name, pattern_regex in self._patterns.items():
            compiled_pattern = get_pattern(pattern_regex)
            match = compiled_pattern.match(text)
            if match:
                groups = match.groups()
                
                if pattern_name == 'and_gate':
                    return RecognitionResult(
                        recognized=True,
                        pattern_type='and_gate',
                        components={
                            'output': groups[0],
                            'output_time': groups[1],
                            'input1': groups[2],
                            'input1_time': groups[3],
                            'input2': groups[4],
                            'input2_time': groups[5]
                        },
                        confidence=0.95,
                        translation_hint='logic_and'
                    )
                
                elif pattern_name == 'or_gate':
                    return RecognitionResult(
                        recognized=True,
                        pattern_type='or_gate',
                        components={
                            'output': groups[0],
                            'output_time': groups[1],
                            'input1': groups[2],
                            'input1_time': groups[3],
                            'input2': groups[4],
                            'input2_time': groups[5]
                        },
                        confidence=0.95,
                        translation_hint='logic_or'
                    )
                
                elif pattern_name == 'not_gate':
                    return RecognitionResult(
                        recognized=True,
                        pattern_type='not_gate',
                        components={
                            'output': groups[0],
                            'output_time': groups[1],
                            'input': groups[2],
                            'input_time': groups[3]
                        },
                        confidence=0.95,
                        translation_hint='logic_not'
                    )
                
                elif pattern_name == 'xor_gate':
                    return RecognitionResult(
                        recognized=True,
                        pattern_type='xor_gate',
                        components={
                            'output': groups[0],
                            'output_time': groups[1],
                            'input1': groups[2],
                            'input1_time': groups[3],
                            'input2': groups[4],
                            'input2_time': groups[5]
                        },
                        confidence=0.95,
                        translation_hint='logic_xor'
                    )
                
                elif pattern_name == 'nand_gate':
                    return RecognitionResult(
                        recognized=True,
                        pattern_type='nand_gate',
                        components={
                            'output': groups[0],
                            'output_time': groups[1],
                            'input1': groups[2],
                            'input1_time': groups[3],
                            'input2': groups[4],
                            'input2_time': groups[5]
                        },
                        confidence=0.9,
                        translation_hint='logic_nand'
                    )
                
                elif pattern_name == 'nor_gate':
                    return RecognitionResult(
                        recognized=True,
                        pattern_type='nor_gate',
                        components={
                            'output': groups[0],
                            'output_time': groups[1],
                            'input1': groups[2],
                            'input1_time': groups[3],
                            'input2': groups[4],
                            'input2_time': groups[5]
                        },
                        confidence=0.9,
                        translation_hint='logic_nor'
                    )
        
        return RecognitionResult(
            recognized=False,
            pattern_type='unknown',
            components={},
            confidence=0.0
        )
    
    def translate_to_tce(self, result: RecognitionResult) -> str:
        """Translate recognized pattern to TCE."""
        if not result.recognized:
            return ""
        
        c = result.components
        
        if result.pattern_type == 'and_gate':
            return f"The {c['output']} at time {c['output_time']} equals {c['input1']} at time {c['input1_time']} AND {c['input2']} at time {c['input2_time']}."
        
        elif result.pattern_type == 'or_gate':
            return f"The {c['output']} at time {c['output_time']} equals {c['input1']} at time {c['input1_time']} OR {c['input2']} at time {c['input2_time']}."
        
        elif result.pattern_type == 'not_gate':
            return f"The {c['output']} at time {c['output_time']} equals NOT {c['input']} at time {c['input_time']}."
        
        elif result.pattern_type == 'xor_gate':
            return f"The {c['output']} at time {c['output_time']} equals {c['input1']} at time {c['input1_time']} XOR {c['input2']} at time {c['input2_time']}."
        
        elif result.pattern_type == 'nand_gate':
            return f"The {c['output']} at time {c['output_time']} equals NOT ({c['input1']} at time {c['input1_time']} AND {c['input2']} at time {c['input2_time']})."
        
        elif result.pattern_type == 'nor_gate':
            return f"The {c['output']} at time {c['output_time']} equals NOT ({c['input1']} at time {c['input1_time']} OR {c['input2']} at time {c['input2_time']})."
        
        return ""
    
    def translate_to_tau(self, result: RecognitionResult) -> str:
        """Translate recognized pattern to Tau."""
        if not result.recognized:
            return ""
        
        c = result.components
        
        if result.pattern_type == 'and_gate':
            return f"{c['output']}[{c['output_time']}] := {c['input1']}[{c['input1_time']}] & {c['input2']}[{c['input2_time']}]"
        
        elif result.pattern_type == 'or_gate':
            return f"{c['output']}[{c['output_time']}] := {c['input1']}[{c['input1_time']}] | {c['input2']}[{c['input2_time']}]"
        
        elif result.pattern_type == 'not_gate':
            return f"{c['output']}[{c['output_time']}] := ~{c['input']}[{c['input_time']}]"
        
        elif result.pattern_type == 'xor_gate':
            return f"{c['output']}[{c['output_time']}] := {c['input1']}[{c['input1_time']}] ^ {c['input2']}[{c['input2_time']}]"
        
        elif result.pattern_type == 'nand_gate':
            return f"{c['output']}[{c['output_time']}] := ~({c['input1']}[{c['input1_time']}] & {c['input2']}[{c['input2_time']}])"
        
        elif result.pattern_type == 'nor_gate':
            return f"{c['output']}[{c['output_time']}] := ~({c['input1']}[{c['input1_time']}] | {c['input2']}[{c['input2_time']}])"
        
        return ""


class ConsensusRecognizer(PatternRecognizer):
    """
    Recognizes consensus and voting patterns.
    
    Examples:
    - majority_vote[t] := majority(votes[t])
    - unanimous[t] := all_agree(members[t])
    """
    
    def __init__(self):
        self._patterns = self._initialize_patterns()
        # Precompile all patterns
        precompile_patterns(self._patterns)
    
    def _initialize_patterns(self) -> Dict[str, str]:
        """Initialize consensus pattern definitions."""
        return {
            # Voting patterns
            'majority_vote': r'([a-zA-Z_][a-zA-Z0-9_]*)\[([^]]+)\]\s*:=\s*majority\s*\(\s*([a-zA-Z0-9_]+)\[([^]]+)\]\s*\)',
            'unanimous_vote': r'([a-zA-Z_][a-zA-Z0-9_]*)\[([^]]+)\]\s*:=\s*unanimous\s*\(\s*([a-zA-Z0-9_]+)\[([^]]+)\]\s*\)',
            'threshold_vote': r'([a-zA-Z_][a-zA-Z0-9_]*)\[([^]]+)\]\s*:=\s*threshold\s*\(\s*([a-zA-Z0-9_]+)\[([^]]+)\]\s*,\s*([0-9.]+)\s*\)',
            
            # Agreement patterns
            'all_agree': r'([a-zA-Z_][a-zA-Z0-9_]*)\[([^]]+)\]\s*:=\s*all_agree\s*\(\s*([a-zA-Z0-9_]+)\[([^]]+)\]\s*\)',
            'any_agree': r'([a-zA-Z_][a-zA-Z0-9_]*)\[([^]]+)\]\s*:=\s*any_agree\s*\(\s*([a-zA-Z0-9_]+)\[([^]]+)\]\s*\)',
            
            # Quorum patterns
            'quorum_met': r'([a-zA-Z_][a-zA-Z0-9_]*)\[([^]]+)\]\s*:=\s*quorum\s*\(\s*([a-zA-Z0-9_]+)\[([^]]+)\]\s*,\s*([0-9]+)\s*\)',
        }
    
    def recognize(self, text: str) -> RecognitionResult:
        """Recognize consensus patterns in text."""
        text = text.strip()
        
        for pattern_name, pattern_regex in self._patterns.items():
            compiled_pattern = get_pattern(pattern_regex)
            match = compiled_pattern.match(text)
            if match:
                groups = match.groups()
                
                if pattern_name == 'majority_vote':
                    return RecognitionResult(
                        recognized=True,
                        pattern_type='majority_vote',
                        components={
                            'result': groups[0],
                            'result_time': groups[1],
                            'votes': groups[2],
                            'votes_time': groups[3]
                        },
                        confidence=0.9,
                        translation_hint='majority_voting'
                    )
                
                elif pattern_name == 'unanimous_vote':
                    return RecognitionResult(
                        recognized=True,
                        pattern_type='unanimous_vote',
                        components={
                            'result': groups[0],
                            'result_time': groups[1],
                            'votes': groups[2],
                            'votes_time': groups[3]
                        },
                        confidence=0.9,
                        translation_hint='unanimous_decision'
                    )
                
                elif pattern_name == 'threshold_vote':
                    return RecognitionResult(
                        recognized=True,
                        pattern_type='threshold_vote',
                        components={
                            'result': groups[0],
                            'result_time': groups[1],
                            'votes': groups[2],
                            'votes_time': groups[3],
                            'threshold': groups[4]
                        },
                        confidence=0.85,
                        translation_hint='threshold_voting'
                    )
                
                elif pattern_name == 'all_agree':
                    return RecognitionResult(
                        recognized=True,
                        pattern_type='all_agree',
                        components={
                            'result': groups[0],
                            'result_time': groups[1],
                            'members': groups[2],
                            'members_time': groups[3]
                        },
                        confidence=0.9,
                        translation_hint='full_agreement'
                    )
        
        return RecognitionResult(
            recognized=False,
            pattern_type='unknown',
            components={},
            confidence=0.0
        )
    
    def translate_to_tce(self, result: RecognitionResult) -> str:
        """Translate recognized pattern to TCE."""
        if not result.recognized:
            return ""
        
        c = result.components
        
        if result.pattern_type == 'majority_vote':
            return f"The {c['result']} at time {c['result_time']} equals the majority of {c['votes']} at time {c['votes_time']}."
        
        elif result.pattern_type == 'unanimous_vote':
            return f"The {c['result']} at time {c['result_time']} equals unanimous agreement of {c['votes']} at time {c['votes_time']}."
        
        elif result.pattern_type == 'threshold_vote':
            return f"The {c['result']} at time {c['result_time']} equals threshold vote of {c['votes']} at time {c['votes_time']} with threshold {c['threshold']}."
        
        elif result.pattern_type == 'all_agree':
            return f"The {c['result']} at time {c['result_time']} is true if all {c['members']} at time {c['members_time']} agree."
        
        return ""
    
    def translate_to_tau(self, result: RecognitionResult) -> str:
        """Translate recognized pattern to Tau."""
        if not result.recognized:
            return ""
        
        c = result.components
        
        if result.pattern_type == 'majority_vote':
            return f"{c['result']}[{c['result_time']}] := majority({c['votes']}[{c['votes_time']}])"
        
        elif result.pattern_type == 'unanimous_vote':
            return f"{c['result']}[{c['result_time']}] := unanimous({c['votes']}[{c['votes_time']}])"
        
        elif result.pattern_type == 'threshold_vote':
            return f"{c['result']}[{c['result_time']}] := threshold({c['votes']}[{c['votes_time']}], {c['threshold']})"
        
        elif result.pattern_type == 'all_agree':
            return f"{c['result']}[{c['result_time']}] := all_agree({c['members']}[{c['members_time']}])"
        
        return ""


class TemporalRecognizer(PatternRecognizer):
    """
    Recognizes temporal patterns.
    
    Examples:
    - delay(signal, 5)
    - advance(signal, 3)
    - eventually(condition)
    - always(invariant)
    """
    
    def __init__(self):
        self._patterns = self._initialize_patterns()
        # Precompile all patterns
        precompile_patterns(self._patterns)
    
    def _initialize_patterns(self) -> Dict[str, str]:
        """Initialize temporal pattern definitions."""
        return {
            # Delay/advance patterns
            'delay': r'([a-zA-Z_][a-zA-Z0-9_]*)\[([^]]+)\]\s*:=\s*delay\s*\(\s*([a-zA-Z0-9_]+)\[([^]]+)\]\s*,\s*([0-9]+)\s*\)',
            'advance': r'([a-zA-Z_][a-zA-Z0-9_]*)\[([^]]+)\]\s*:=\s*advance\s*\(\s*([a-zA-Z0-9_]+)\[([^]]+)\]\s*,\s*([0-9]+)\s*\)',
            
            # Temporal logic patterns
            'eventually': r'([a-zA-Z_][a-zA-Z0-9_]*)\[([^]]+)\]\s*:=\s*eventually\s*\(\s*([a-zA-Z0-9_]+)\[([^]]+)\]\s*\)',
            'always': r'([a-zA-Z_][a-zA-Z0-9_]*)\[([^]]+)\]\s*:=\s*always\s*\(\s*([a-zA-Z0-9_]+)\[([^]]+)\]\s*\)',
            'until': r'([a-zA-Z_][a-zA-Z0-9_]*)\[([^]]+)\]\s*:=\s*([a-zA-Z0-9_]+)\[([^]]+)\]\s+until\s+([a-zA-Z0-9_]+)\[([^]]+)\]',
            
            # Time window patterns
            'within': r'([a-zA-Z_][a-zA-Z0-9_]*)\[([^]]+)\]\s*:=\s*within\s*\(\s*([a-zA-Z0-9_]+)\[([^]]+)\]\s*,\s*([0-9]+)\s*,\s*([0-9]+)\s*\)',
            
            # Temporal implication
            'implies_next': r'([a-zA-Z_][a-zA-Z0-9_]*)\[([^]]+)\]\s*:=\s*([a-zA-Z0-9_]+)\[([^]]+)\]\s*=>\s*next\s+([a-zA-Z0-9_]+)\[([^]]+)\]',
        }
    
    def recognize(self, text: str) -> RecognitionResult:
        """Recognize temporal patterns in text."""
        text = text.strip()
        
        for pattern_name, pattern_regex in self._patterns.items():
            compiled_pattern = get_pattern(pattern_regex)
            match = compiled_pattern.match(text)
            if match:
                groups = match.groups()
                
                if pattern_name == 'delay':
                    return RecognitionResult(
                        recognized=True,
                        pattern_type='delay',
                        components={
                            'output': groups[0],
                            'output_time': groups[1],
                            'signal': groups[2],
                            'signal_time': groups[3],
                            'delay_amount': groups[4]
                        },
                        confidence=0.9,
                        translation_hint='signal_delay'
                    )
                
                elif pattern_name == 'advance':
                    return RecognitionResult(
                        recognized=True,
                        pattern_type='advance',
                        components={
                            'output': groups[0],
                            'output_time': groups[1],
                            'signal': groups[2],
                            'signal_time': groups[3],
                            'advance_amount': groups[4]
                        },
                        confidence=0.9,
                        translation_hint='signal_advance'
                    )
                
                elif pattern_name == 'eventually':
                    return RecognitionResult(
                        recognized=True,
                        pattern_type='eventually',
                        components={
                            'result': groups[0],
                            'result_time': groups[1],
                            'condition': groups[2],
                            'condition_time': groups[3]
                        },
                        confidence=0.85,
                        translation_hint='temporal_eventually'
                    )
                
                elif pattern_name == 'always':
                    return RecognitionResult(
                        recognized=True,
                        pattern_type='always',
                        components={
                            'result': groups[0],
                            'result_time': groups[1],
                            'invariant': groups[2],
                            'invariant_time': groups[3]
                        },
                        confidence=0.85,
                        translation_hint='temporal_always'
                    )
                
                elif pattern_name == 'implies_next':
                    return RecognitionResult(
                        recognized=True,
                        pattern_type='implies_next',
                        components={
                            'result': groups[0],
                            'result_time': groups[1],
                            'antecedent': groups[2],
                            'antecedent_time': groups[3],
                            'consequent': groups[4],
                            'consequent_time': groups[5]
                        },
                        confidence=0.8,
                        translation_hint='temporal_implication'
                    )
        
        return RecognitionResult(
            recognized=False,
            pattern_type='unknown',
            components={},
            confidence=0.0
        )
    
    def translate_to_tce(self, result: RecognitionResult) -> str:
        """Translate recognized pattern to TCE."""
        if not result.recognized:
            return ""
        
        c = result.components
        
        if result.pattern_type == 'delay':
            return f"The {c['output']} at time {c['output_time']} equals {c['signal']} at time {c['signal_time']} delayed by {c['delay_amount']} time units."
        
        elif result.pattern_type == 'advance':
            return f"The {c['output']} at time {c['output_time']} equals {c['signal']} at time {c['signal_time']} advanced by {c['advance_amount']} time units."
        
        elif result.pattern_type == 'eventually':
            return f"The {c['result']} at time {c['result_time']} is true if {c['condition']} at time {c['condition_time']} eventually becomes true."
        
        elif result.pattern_type == 'always':
            return f"The {c['result']} at time {c['result_time']} is true if {c['invariant']} at time {c['invariant_time']} is always true."
        
        elif result.pattern_type == 'implies_next':
            return f"The {c['result']} at time {c['result_time']} is true if {c['antecedent']} at time {c['antecedent_time']} implies {c['consequent']} at time {c['consequent_time']} in the next time step."
        
        return ""
    
    def translate_to_tau(self, result: RecognitionResult) -> str:
        """Translate recognized pattern to Tau."""
        if not result.recognized:
            return ""
        
        c = result.components
        
        if result.pattern_type == 'delay':
            return f"{c['output']}[{c['output_time']}] := delay({c['signal']}[{c['signal_time']}], {c['delay_amount']})"
        
        elif result.pattern_type == 'advance':
            return f"{c['output']}[{c['output_time']}] := advance({c['signal']}[{c['signal_time']}], {c['advance_amount']})"
        
        elif result.pattern_type == 'eventually':
            return f"{c['result']}[{c['result_time']}] := eventually({c['condition']}[{c['condition_time']}])"
        
        elif result.pattern_type == 'always':
            return f"{c['result']}[{c['result_time']}] := always({c['invariant']}[{c['invariant_time']}])"
        
        elif result.pattern_type == 'implies_next':
            return f"{c['result']}[{c['result_time']}] := {c['antecedent']}[{c['antecedent_time']}] => next {c['consequent']}[{c['consequent_time']}]"
        
        return ""


class RecognizerFactory:
    """Factory for creating recognizer instances."""
    
    _recognizers = {
        'arithmetic': BinaryArithmeticRecognizer,
        'stream': StreamRecognizer,
        'logic_gate': LogicGateRecognizer,
        'consensus': ConsensusRecognizer,
        'temporal': TemporalRecognizer,
    }
    
    @classmethod
    def create_recognizer(cls, recognizer_type: str) -> PatternRecognizer:
        """Create a recognizer instance by type."""
        recognizer_class = cls._recognizers.get(recognizer_type)
        if not recognizer_class:
            raise ValueError(f"Unknown recognizer type: {recognizer_type}")
        return recognizer_class()
    
    @classmethod
    def get_all_recognizers(cls) -> Dict[str, PatternRecognizer]:
        """Get instances of all available recognizers."""
        return {
            name: recognizer_class() 
            for name, recognizer_class in cls._recognizers.items()
        }
    
    @classmethod
    def recognize_any(cls, text: str) -> List[Tuple[str, RecognitionResult]]:
        """
        Try to recognize text using all available recognizers.
        
        Returns:
            List of tuples (recognizer_type, result) for successful recognitions
        """
        results = []
        recognizers = cls.get_all_recognizers()
        
        for recognizer_type, recognizer in recognizers.items():
            result = recognizer.recognize(text)
            if result.recognized:
                results.append((recognizer_type, result))
        
        return results