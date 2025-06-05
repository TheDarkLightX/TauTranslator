"""
Test suite for StreamRecognizer
===============================

Tests stream pattern recognition and translation capabilities.

Author: DarkLightX / Dana Edwards
"""

import pytest
from src.tau_translator_omega.lmql_engine.recognizers import (
    StreamRecognizer, RecognitionResult, RecognizerFactory
)


class TestStreamRecognizer:
    """Test stream pattern recognition."""
    
    @pytest.fixture
    def recognizer(self):
        """Create recognizer instance."""
        return StreamRecognizer()
    
    def test_recognizer_factory_creation(self):
        """Test creating recognizer via factory."""
        recognizer = RecognizerFactory.create_recognizer('stream')
        assert isinstance(recognizer, StreamRecognizer)
    
    def test_input_file_stream_recognition(self, recognizer):
        """Test recognizing input file stream pattern."""
        tau_text = 'sbf input_data = ifile("data.txt")'
        result = recognizer.recognize(tau_text)
        
        assert result.recognized
        assert result.pattern_type == 'input_stream'
        assert result.components['stream_name'] == 'input_data'
        assert result.components['filename'] == 'data.txt'
        assert result.confidence > 0.9
    
    def test_output_file_stream_recognition(self, recognizer):
        """Test recognizing output file stream pattern."""
        tau_text = 'sbf results = ofile("output.log")'
        result = recognizer.recognize(tau_text)
        
        assert result.recognized
        assert result.pattern_type == 'output_stream'
        assert result.components['stream_name'] == 'results'
        assert result.components['filename'] == 'output.log'
    
    def test_console_stream_recognition(self, recognizer):
        """Test recognizing console stream pattern."""
        tau_text = 'sbf debug = console'
        result = recognizer.recognize(tau_text)
        
        assert result.recognized
        assert result.pattern_type == 'console_stream'
        assert result.components['stream_name'] == 'debug'
    
    def test_stream_assignment_recognition(self, recognizer):
        """Test recognizing stream assignment pattern."""
        tau_text = 'sbf output = input'
        result = recognizer.recognize(tau_text)
        
        assert result.recognized
        assert result.pattern_type == 'stream_assignment'
        assert result.components['target_stream'] == 'output'
        assert result.components['source_stream'] == 'input'
    
    def test_input_stream_to_tce_translation(self, recognizer):
        """Test translating input stream to TCE."""
        tau_text = 'sbf sensor_data = ifile("sensors.csv")'
        result = recognizer.recognize(tau_text)
        tce_output = recognizer.translate_to_tce(result)
        
        expected = 'Define input stream sensor_data that reads from file "sensors.csv".'
        assert tce_output == expected
    
    def test_output_stream_to_tce_translation(self, recognizer):
        """Test translating output stream to TCE."""
        tau_text = 'sbf log_file = ofile("system.log")'
        result = recognizer.recognize(tau_text)
        tce_output = recognizer.translate_to_tce(result)
        
        expected = 'Define output stream log_file that writes to file "system.log".'
        assert tce_output == expected
    
    def test_console_stream_to_tce_translation(self, recognizer):
        """Test translating console stream to TCE."""
        tau_text = 'sbf user_io = console'
        result = recognizer.recognize(tau_text)
        tce_output = recognizer.translate_to_tce(result)
        
        expected = 'Define console stream user_io for interactive input/output.'
        assert tce_output == expected
    
    def test_stream_assignment_to_tce_translation(self, recognizer):
        """Test translating stream assignment to TCE."""
        tau_text = 'sbf backup = main_stream'
        result = recognizer.recognize(tau_text)
        tce_output = recognizer.translate_to_tce(result)
        
        expected = 'Define stream backup as a copy of stream main_stream.'
        assert tce_output == expected
    
    def test_tce_to_tau_translation(self, recognizer):
        """Test translating back from TCE to Tau."""
        # First recognize a pattern
        tau_text = 'sbf data = ifile("input.dat")'
        result = recognizer.recognize(tau_text)
        
        # Translate to Tau (should match original)
        tau_output = recognizer.translate_to_tau(result)
        assert tau_output == tau_text
    
    def test_non_matching_pattern(self, recognizer):
        """Test behavior with non-matching pattern."""
        tau_text = "not a stream declaration"
        result = recognizer.recognize(tau_text)
        
        assert not result.recognized
        assert result.pattern_type == 'unknown'
        assert result.confidence == 0.0
    
    def test_whitespace_handling(self, recognizer):
        """Test recognition with various whitespace."""
        tau_texts = [
            'sbf input=ifile("data.txt")',  # No spaces
            'sbf  input  =  ifile( "data.txt" )',  # Extra spaces
            'sbf\tinput\t=\tifile("data.txt")',  # Tabs
        ]
        
        for tau_text in tau_texts:
            result = recognizer.recognize(tau_text)
            assert result.recognized
            assert result.pattern_type == 'input_stream'
            assert result.components['stream_name'] == 'input'
            assert result.components['filename'] == 'data.txt'
    
    def test_complex_filenames(self, recognizer):
        """Test recognition with complex filenames."""
        tau_text = 'sbf data = ifile("/path/to/file with spaces.txt")'
        result = recognizer.recognize(tau_text)
        
        assert result.recognized
        assert result.pattern_type == 'input_stream'
        assert result.components['filename'] == '/path/to/file with spaces.txt'
    
    def test_underscore_in_stream_names(self, recognizer):
        """Test stream names with underscores."""
        tau_text = 'sbf my_input_stream = ifile("data.bin")'
        result = recognizer.recognize(tau_text)
        
        assert result.recognized
        assert result.components['stream_name'] == 'my_input_stream'
    
    def test_multiple_stream_types(self, recognizer):
        """Test that all stream types are recognized."""
        test_cases = [
            ('sbf in = ifile("in.txt")', 'input_stream'),
            ('sbf out = ofile("out.txt")', 'output_stream'),
            ('sbf con = console', 'console_stream'),
            ('sbf copy = original', 'stream_assignment'),
        ]
        
        for tau_text, expected_type in test_cases:
            result = recognizer.recognize(tau_text)
            assert result.recognized
            assert result.pattern_type == expected_type