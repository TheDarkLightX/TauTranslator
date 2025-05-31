#!/usr/bin/env python3
"""Test the exact example you mentioned"""

import requests
import json

def test_frontend_api():
    """Test through the frontend API like user would see"""
    api_url = "http://localhost:3000/api/translate"
    
    print("=== Testing Your Example Through Frontend ===")
    
    # Test 1: TAU to ILR  
    print("\n1. TAU to ILR:")
    response1 = requests.post(api_url, json={
        "sourceText": "barberShaves(X) := p(X) = 0",
        "sourceLangKey": "TAU",
        "targetLangKey": "ILR"
    })
    
    if response1.status_code == 200:
        result1 = response1.json()
        print(f"   Input: barberShaves(X) := p(X) = 0")
        print(f"   Output: {result1['translatedText']}")
        ilr_text = result1['translatedText']
    else:
        print(f"   Failed: {response1.status_code}")
        return
    
    # Test 2: ILR to CNL
    print("\n2. ILR to CNL:")
    response2 = requests.post(api_url, json={
        "sourceText": ilr_text,
        "sourceLangKey": "ILR", 
        "targetLangKey": "CNL"
    })
    
    if response2.status_code == 200:
        result2 = response2.json()
        print(f"   Input: {ilr_text}")
        print(f"   Output: {result2['translatedText']}")
    else:
        print(f"   Failed: {response2.status_code}")

if __name__ == "__main__":
    test_frontend_api()