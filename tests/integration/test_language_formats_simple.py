#!/usr/bin/env python3
"""
TDD Tests for Language Format Translations - Simple Version
==========================================================

These tests define the expected behavior for CNL and ILR translations.
Following TDD: Write failing tests first, then implement to make them pass.
"""

import requests
import json

def test_current_backend_behavior():
    """Test what the current backend actually returns"""
    backend_url = "http://localhost:8003/translate"
    
    print("=== Testing Current Backend Behavior ===")
    
    # Test TAU to ILR (should fail with current backend)
    try:
        response = requests.post(backend_url, json={
            "text": "barberShaves(X) := p(X) = 0",
            "direction": "tau_to_ilr"
        })
        print(f"TAU to ILR Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"TAU to ILR Result: {result['translatedText']}")
        else:
            print(f"TAU to ILR Error: {response.text}")
    except Exception as e:
        print(f"TAU to ILR Exception: {e}")
    
    # Test ILR to CNL (should fail with current backend)
    try:
        response = requests.post(backend_url, json={
            "text": '{"type": "definition", "predicate": "barberShaves"}',
            "direction": "ilr_to_cnl"
        })
        print(f"ILR to CNL Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"ILR to CNL Result: {result['translatedText']}")
        else:
            print(f"ILR to CNL Error: {response.text}")
    except Exception as e:
        print(f"ILR to CNL Exception: {e}")
    
    # Test CNL to TAU (should fail with current backend)
    try:
        response = requests.post(backend_url, json={
            "text": "For every x, if P of x then Q of x.",
            "direction": "cnl_to_tau"
        })
        print(f"CNL to TAU Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"CNL to TAU Result: {result['translatedText']}")
        else:
            print(f"CNL to TAU Error: {response.text}")
    except Exception as e:
        print(f"CNL to TAU Exception: {e}")

def test_expected_behaviors():
    """Define what we expect the translations to produce"""
    print("\n=== Expected Translation Behaviors ===")
    
    test_cases = [
        {
            "name": "TAU to ILR",
            "input": "barberShaves(X) := p(X) = 0",
            "expected_structure": {
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
            "name": "ILR to CNL",
            "input": {
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
            "expected": "Define barberShaves for any X where p of X equals 0."
        },
        {
            "name": "CNL to TAU",
            "input": "For every x, if P of x then Q of x.",
            "expected": "forall x : P(x) -> Q(x)"
        }
    ]
    
    for case in test_cases:
        print(f"\n{case['name']}:")
        print(f"  Input: {case['input']}")
        if 'expected_structure' in case:
            print(f"  Expected Structure: {json.dumps(case['expected_structure'], indent=2)}")
        else:
            print(f"  Expected: {case['expected']}")

if __name__ == "__main__":
    test_current_backend_behavior()
    test_expected_behaviors()