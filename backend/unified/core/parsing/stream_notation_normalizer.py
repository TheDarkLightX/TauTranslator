"""
Stream Notation Normalizer - Ensures consistent stream notation.
Transforms various stream descriptions to compact notation.

Copyright: DarkLightX / Dana Edwards
"""

import re
from typing import Optional, Tuple, List
from backend.unified.core.domain.parser_types import (
    StreamReference, TimeExpression, TimeIndex,
    TemporalParsingError
)
from backend.unified.core.parsing.mathematical_expression_parser import (
    MathematicalExpressionParser
)


class StreamNotationNormalizer:
    """
    Ensures consistent stream notation - pure transformation.
    Converts various forms of stream references to compact notation.
    """
    
    def __init__(self):
        """Initialize normalizer with patterns and math parser."""
        self._compile_patterns()
        self.math_parser = MathematicalExpressionParser()
    
    def _compile_patterns(self) -> None:
        """Compile regex patterns for stream identification."""
        self.patterns = {
            # "output stream 1 at time t"
            'full_stream': re.compile(
                r'(output|input)\s+(?:stream\s+)?(\d+)\s+at\s+(?:time\s+)?(.+?)(?:\s|$)',
                re.IGNORECASE
            ),
            # "output 1 at t plus 1"
            'compact_stream': re.compile(
                r'(output|input)\s+(\d+)\s+at\s+(.+?)(?:\s|$)',
                re.IGNORECASE
            ),
            # "o1[t]" or "i2[t-1]"
            'notation_stream': re.compile(
                r'([oi])(\d+)\[([^\]]+)\]'
            ),
            # Stream without explicit time
            'simple_stream': re.compile(
                r'(output|input)\s+(?:stream\s+)?(\d+)(?:\s|$)',
                re.IGNORECASE
            )
        }
    
    def normalize_stream_reference_to_compact_notation(
        self,
        stream_desc: str
    ) -> StreamReference:
        """
        Transforms stream descriptions to StreamReference.
        Examples:
          'output stream 1 at time t' -> StreamReference -> 'o1[t]'
          'input 2 at t plus 1' -> StreamReference -> 'i2[t+1]'
        """
        stream_ref = self._parse_stream_description(stream_desc)
        
        if not stream_ref:
            raise TemporalParsingError(f"Cannot parse stream reference: {stream_desc}")
        
        return stream_ref
    
    def _parse_stream_description(self, desc: str) -> Optional[StreamReference]:
        """Parse various forms of stream descriptions."""
        desc = desc.strip()
        
        # Try each pattern in order of specificity
        
        # Already in notation form
        match = self.patterns['notation_stream'].match(desc)
        if match:
            stream_type = 'input' if match.group(1) == 'i' else 'output'
            stream_num = int(match.group(2))
            time_expr = self._parse_time_expression(match.group(3))
            return StreamReference(stream_type, stream_num, time_expr)
        
        # Full stream description
        match = self.patterns['full_stream'].search(desc)
        if match:
            stream_type = match.group(1).lower()
            stream_num = int(match.group(2))
            time_str = match.group(3)
            time_expr = self._parse_time_expression(time_str)
            return StreamReference(stream_type, stream_num, time_expr)
        
        # Compact stream description
        match = self.patterns['compact_stream'].search(desc)
        if match:
            stream_type = match.group(1).lower()
            stream_num = int(match.group(2))
            time_str = match.group(3)
            time_expr = self._parse_time_expression(time_str)
            return StreamReference(stream_type, stream_num, time_expr)
        
        # Simple stream without time (assume current time 't')
        match = self.patterns['simple_stream'].search(desc)
        if match:
            stream_type = match.group(1).lower()
            stream_num = int(match.group(2))
            time_expr = TimeExpression(base=TimeIndex('t'))
            return StreamReference(stream_type, stream_num, time_expr)
        
        return None
    
    def _parse_time_expression(self, time_str: str) -> TimeExpression:
        """Parse time expression using math parser."""
        time_str = time_str.strip()
        
        # Handle simple 't'
        if time_str == 't':
            return TimeExpression(base=TimeIndex('t'))
        
        # Use math parser for complex expressions
        return self.math_parser.parse_time_expression_to_ast(time_str)
    
    def normalize_stream_in_text(self, text: str) -> str:
        """
        Find and normalize all stream references in text.
        Returns text with stream references replaced by compact notation.
        """
        result = text
        
        # Find all stream patterns and replace with compact notation
        stream_patterns = [
            (self.patterns['full_stream'], self._replace_full_stream),
            (self.patterns['compact_stream'], self._replace_compact_stream),
            (self.patterns['simple_stream'], self._replace_simple_stream)
        ]
        
        for pattern, replacer in stream_patterns:
            result = pattern.sub(replacer, result)
        
        return result
    
    def _replace_full_stream(self, match: re.Match) -> str:
        """Replace full stream description with compact notation."""
        try:
            stream_ref = StreamReference(
                stream_type=match.group(1).lower(),
                stream_number=int(match.group(2)),
                time=self._parse_time_expression(match.group(3))
            )
            return stream_ref.to_notation()
        except Exception:
            return match.group(0)  # Keep original on error
    
    def _replace_compact_stream(self, match: re.Match) -> str:
        """Replace compact stream description with notation."""
        try:
            stream_ref = StreamReference(
                stream_type=match.group(1).lower(),
                stream_number=int(match.group(2)),
                time=self._parse_time_expression(match.group(3))
            )
            return stream_ref.to_notation()
        except Exception:
            return match.group(0)
    
    def _replace_simple_stream(self, match: re.Match) -> str:
        """Replace simple stream with default time notation."""
        try:
            stream_ref = StreamReference(
                stream_type=match.group(1).lower(),
                stream_number=int(match.group(2)),
                time=TimeExpression(base=TimeIndex('t'))
            )
            return stream_ref.to_notation()
        except Exception:
            return match.group(0)
    
    def extract_all_stream_references(self, text: str) -> List[StreamReference]:
        """Extract all stream references from text."""
        references = []
        
        # Check each pattern
        for pattern_name, pattern in self.patterns.items():
            if pattern_name == 'notation_stream':
                # Special handling for notation pattern
                for match in pattern.finditer(text):
                    stream_type = 'input' if match.group(1) == 'i' else 'output'
                    stream_num = int(match.group(2))
                    time_expr = self._parse_time_expression(match.group(3))
                    references.append(StreamReference(stream_type, stream_num, time_expr))
            else:
                # Other patterns
                for match in pattern.finditer(text):
                    try:
                        desc = match.group(0)
                        ref = self._parse_stream_description(desc)
                        if ref:
                            references.append(ref)
                    except Exception:
                        continue
        
        return references