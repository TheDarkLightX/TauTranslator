"""
Test suite for ConsensusRecognizer
==================================

Tests consensus and voting pattern recognition and translation capabilities.

Author: DarkLightX / Dana Edwards
"""

import pytest
from src.tau_translator_omega.lmql_engine.recognizers import (
    ConsensusRecognizer, RecognitionResult, RecognizerFactory
)


class TestConsensusRecognizer:
    """Test consensus pattern recognition."""
    
    @pytest.fixture
    def recognizer(self):
        """Create recognizer instance."""
        return ConsensusRecognizer()
    
    def test_recognizer_factory_creation(self):
        """Test creating recognizer via factory."""
        recognizer = RecognizerFactory.create_recognizer('consensus')
        assert isinstance(recognizer, ConsensusRecognizer)
    
    def test_majority_vote_recognition(self, recognizer):
        """Test recognizing majority voting pattern."""
        tau_text = "majority[t] := (voter1[t] + voter2[t] + voter3[t]) >= 2"
        result = recognizer.recognize(tau_text)
        
        assert result.recognized
        assert result.pattern_type == 'majority_vote'
        assert result.components['output_time'] == 't'
        assert result.components['voter1'] == 'voter1'
        assert result.components['voter2'] == 'voter2'
        assert result.components['voter3'] == 'voter3'
        assert result.confidence > 0.8
    
    def test_unanimous_recognition(self, recognizer):
        """Test recognizing unanimous decision pattern."""
        tau_text = "unanimous[t] := node1[t] & node2[t] & node3[t]"
        result = recognizer.recognize(tau_text)
        
        assert result.recognized
        assert result.pattern_type == 'unanimous'
        assert result.components['output_time'] == 't'
        assert result.components['voter1'] == 'node1'
        assert result.components['voter2'] == 'node2'
        assert result.components['voter3'] == 'node3'
    
    def test_majority_vote_to_tce_translation(self, recognizer):
        """Test translating majority vote to TCE."""
        tau_text = "majority[n] := (a[n] + b[n] + c[n]) >= 2"
        result = recognizer.recognize(tau_text)
        tce_output = recognizer.translate_to_tce(result)
        
        expected = ("The majority decision at time n is reached when "
                   "at least two of the following agree: a at time n, "
                   "b at time n, and c at time n.")
        assert tce_output == expected
    
    def test_unanimous_to_tce_translation(self, recognizer):
        """Test translating unanimous decision to TCE."""
        tau_text = "unanimous[t] := v1[t] & v2[t] & v3[t]"
        result = recognizer.recognize(tau_text)
        tce_output = recognizer.translate_to_tce(result)
        
        expected = ("Unanimous decision at time t requires "
                   "all of the following to agree: v1 at time t, "
                   "v2 at time t, and v3 at time t.")
        assert tce_output == expected
    
    def test_tce_to_tau_translation(self, recognizer):
        """Test translating back from TCE to Tau."""
        # First recognize a pattern
        tau_text = "majority[t] := (a[t] + b[t] + c[t]) >= 2"
        result = recognizer.recognize(tau_text)
        
        # Translate to Tau (should match original)
        tau_output = recognizer.translate_to_tau(result)
        assert tau_output == tau_text
    
    def test_non_matching_pattern(self, recognizer):
        """Test behavior with non-matching pattern."""
        tau_text = "not a consensus pattern"
        result = recognizer.recognize(tau_text)
        
        assert not result.recognized
        assert result.pattern_type == 'unknown'
        assert result.confidence == 0.0
    
    def test_complex_time_expressions(self, recognizer):
        """Test recognition with complex time expressions."""
        tau_text = "majority[t+1] := (input1[t-1] + input2[t] + input3[t+1]) >= 2"
        result = recognizer.recognize(tau_text)
        
        assert result.recognized
        assert result.pattern_type == 'majority_vote'
        assert result.components['output_time'] == 't+1'
        assert result.components['voter1_time'] == 't-1'
        assert result.components['voter2_time'] == 't'
        assert result.components['voter3_time'] == 't+1'
    
    def test_whitespace_variations(self, recognizer):
        """Test recognition with various whitespace."""
        tau_texts = [
            "majority[t]:=(a[t]+b[t]+c[t])>=2",  # No spaces
            "majority[t] :=  ( a[t]  +  b[t]  +  c[t] )  >=  2",  # Extra spaces
            "majority[t]\t:=\t(a[t]\t+\tb[t]\t+\tc[t])\t>=\t2",  # Tabs
        ]
        
        for tau_text in tau_texts:
            result = recognizer.recognize(tau_text)
            assert result.recognized
            assert result.pattern_type == 'majority_vote'
    
    def test_unanimous_with_more_voters(self, recognizer):
        """Test that unanimous pattern matches even with 4 voters (captures first 3)."""
        # This will match but only capture the first 3 voters
        tau_text = "unanimous[t] := v1[t] & v2[t] & v3[t] & v4[t]"
        result = recognizer.recognize(tau_text)
        
        assert result.recognized  # Pattern is flexible
        assert result.pattern_type == 'unanimous'
        # Only captures first 3 voters
        assert result.components['voter1'] == 'v1'
        assert result.components['voter2'] == 'v2'
        assert result.components['voter3'] == 'v3'
    
    def test_different_voter_names(self, recognizer):
        """Test recognition with different voter variable names."""
        test_cases = [
            "majority[t] := (sensor1[t] + sensor2[t] + sensor3[t]) >= 2",
            "unanimous[t] := replica_a[t] & replica_b[t] & replica_c[t]",
        ]
        
        for tau_text in test_cases:
            result = recognizer.recognize(tau_text)
            assert result.recognized