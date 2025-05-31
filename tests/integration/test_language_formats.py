#!/usr/bin/env python3
"""
TDD Tests for Language Format Translations
==========================================

These tests define the expected behavior for CNL and ILR translations.
Following TDD: Write failing tests first, then implement to make them pass.
"""

import pytest
import requests
import json

# Test data with expected translations
TRANSLATION_TEST_CASES = [
    {
        "name": "barber_paradox_tau_to_ilr",
        "source": "barberShaves(X) := p(X) = 0",
        "source_lang": "TAU",
        "target_lang": "ILR", 
        "expected": {
            "type": "definition",
            "predicate": "barberShaves",
            "variable": "X",
            "condition": {
                "type": "equality",
                "left": "p(X)",
                "operator": "equals",
                "right": "0"
            }
        }
    },
    {
        "name": "barber_paradox_ilr_to_cnl",
        "source": {
            "type": "definition",
            "predicate": "barberShaves", 
            "variable": "X",
            "condition": {
                "type": "equality",
                "left": "p(X)",
                "operator": "equals", 
                "right": "0"
            }
        },
        "source_lang": "ILR",
        "target_lang": "CNL",
        "expected": "Define barberShaves for any X where p of X equals 0."
    },
    {
        "name": "forall_statement_tau_to_cnl",
        "source": "forall x : P(x)",
        "source_lang": "TAU", 
        "target_lang": "CNL",
        "expected": "For every x, P of x holds."
    },
    {
        "name": "temporal_logic_tau_to_ilr",
        "source": "always (x & y)",
        "source_lang": "TAU",
        "target_lang": "ILR",
        "expected": {
            "type": "temporal",
            "operator": "always",
            "expression": {
                "type": "conjunction",
                "left": "x",
                "operator": "and",
                "right": "y"
            }
        }
    },
    {
        "name": "cnl_to_tau_conversion",
        "source": "For every x, if P of x then Q of x.",
        "source_lang": "CNL",
        "target_lang": "TAU", 
        "expected": "forall x : P(x) -> Q(x)"
    },
    {
        "name": "ilr_to_tau_conversion",
        "source": {
            "type": "quantifier",
            "quantifier": "forall",
            "variable": "x",
            "expression": {
                "type": "implication",
                "left": "P(x)",
                "operator": "implies",
                "right": "Q(x)"
            }
        },
        "source_lang": "ILR",
        "target_lang": "TAU",
        "expected": "forall x : P(x) -> Q(x)"
    }
]

class TestLanguageFormatTranslations:
    """Test suite for CNL and ILR translation formats"""
    
    @pytest.fixture
    def backend_url(self):
        """Backend URL for testing"""
        return "http://localhost:8003/translate"
    
    @pytest.fixture
    def api_url(self):
        """API URL for testing"""
        return "http://localhost:3000/api/translate"
    
    def test_tau_to_ilr_structure(self, backend_url):
        """Test TAU to ILR produces proper structured output"""
        response = requests.post(backend_url, json={
            "text": "barberShaves(X) := p(X) = 0",
            "direction": "tau_to_ilr"
        })
        
        assert response.status_code == 200
        result = response.json()
        
        # Should be valid JSON structure, not malformed text
        translated = result["translatedText"]
        if isinstance(translated, str):
            # If string, should be valid JSON
            ilr_data = json.loads(translated)
        else:
            ilr_data = translated
            
        assert ilr_data["type"] == "definition"
        assert ilr_data["predicate"] == "barberShaves"
        assert ilr_data["variable"] == "X"
        assert ilr_data["condition"]["type"] == "equality"
        assert ilr_data["condition"]["left"] == "p(X)"
        assert ilr_data["condition"]["operator"] == "equals"
        assert ilr_data["condition"]["right"] == "0"
    
    def test_ilr_to_cnl_natural_language(self, backend_url):
        """Test ILR to CNL produces natural controlled language"""
        ilr_input = {
            "type": "definition",
            "predicate": "barberShaves",
            "variable": "X", 
            "condition": {
                "type": "equality",
                "left": "p(X)",
                "operator": "equals",
                "right": "0"
            }
        }
        
        response = requests.post(backend_url, json={
            "text": json.dumps(ilr_input),
            "direction": "ilr_to_cnl"
        })
        
        assert response.status_code == 200
        result = response.json()
        translated = result["translatedText"]
        
        # Should be natural language, not malformed syntax
        assert "Define barberShaves" in translated
        assert "equals 0" in translated
        assert "such that=" not in translated  # No malformed syntax
        assert translated.endswith(".")  # Proper sentence
    
    def test_cnl_to_tau_conversion(self, backend_url):
        """Test CNL to TAU conversion"""
        response = requests.post(backend_url, json={
            "text": "For every x, if P of x then Q of x.",
            "direction": "cnl_to_tau"
        })
        
        assert response.status_code == 200
        result = response.json()
        translated = result["translatedText"]
        
        assert "forall x :" in translated
        assert "P(x) -> Q(x)" in translated
    
    def test_ilr_to_tau_conversion(self, backend_url):
        """Test ILR to TAU conversion"""
        ilr_input = {
            "type": "quantifier",
            "quantifier": "forall", 
            "variable": "x",
            "expression": {
                "type": "implication",
                "left": "P(x)",
                "operator": "implies",
                "right": "Q(x)"
            }
        }
        
        response = requests.post(backend_url, json={
            "text": json.dumps(ilr_input),
            "direction": "ilr_to_tau"
        })
        
        assert response.status_code == 200
        result = response.json()
        translated = result["translatedText"]
        
        assert translated == "forall x : P(x) -> Q(x)"
    
    @pytest.mark.parametrize("test_case", TRANSLATION_TEST_CASES)
    def test_all_translation_cases(self, backend_url, test_case):
        """Test all defined translation cases"""
        source_text = test_case["source"]
        if isinstance(source_text, dict):
            source_text = json.dumps(source_text)
            
        direction = f"{test_case['source_lang'].lower()}_to_{test_case['target_lang'].lower()}"
        
        response = requests.post(backend_url, json={
            "text": source_text,
            "direction": direction
        })
        
        assert response.status_code == 200
        result = response.json()
        translated = result["translatedText"]
        
        expected = test_case["expected"]
        if isinstance(expected, dict):
            if isinstance(translated, str):
                translated_data = json.loads(translated)
            else:
                translated_data = translated
            assert translated_data == expected
        else:
            assert translated == expected

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])