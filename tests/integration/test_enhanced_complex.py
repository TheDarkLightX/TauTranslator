#!/usr/bin/env python3
"""Test the enhanced complex expression handling"""

import requests
import json

def test_complex_paradox():
    """Test the complex paradox expression"""
    api_url = "http://localhost:3000/api/translate"
    
    print("🧪 Testing Enhanced Complex Expression Handling")
    print("=" * 50)
    
    # Test the problematic sentence
    tau_input = "paradox(b) := ex b all X barber(b, X)"
    
    print(f"Original TAU: {tau_input}")
    
    # TAU → ILR
    print("\n1. TAU → ILR:")
    response1 = requests.post(api_url, json={
        "sourceText": tau_input,
        "sourceLangKey": "TAU",
        "targetLangKey": "ILR"
    })
    
    if response1.status_code == 200:
        result1 = response1.json()
        ilr_output = result1['translatedText']
        print("   Result:")
        try:
            ilr_json = json.loads(ilr_output)
            print(json.dumps(ilr_json, indent=4))
        except:
            print(f"   {ilr_output}")
        
        # ILR → CNL
        print("\n2. ILR → CNL:")
        response2 = requests.post(api_url, json={
            "sourceText": ilr_output,
            "sourceLangKey": "ILR",
            "targetLangKey": "CNL"
        })
        
        if response2.status_code == 200:
            result2 = response2.json()
            cnl_output = result2['translatedText']
            print(f"   Result: {cnl_output}")
        else:
            print(f"   ❌ Failed: {response2.status_code}")
    else:
        print(f"   ❌ Failed: {response1.status_code}")
    
    # Also test TAU → Plain English directly
    print("\n3. TAU → Plain English:")
    response3 = requests.post(api_url, json={
        "sourceText": tau_input,
        "sourceLangKey": "TAU", 
        "targetLangKey": "PLAIN_ENGLISH"
    })
    
    if response3.status_code == 200:
        result3 = response3.json()
        english_output = result3['translatedText']
        print(f"   Result: {english_output}")
    else:
        print(f"   ❌ Failed: {response3.status_code}")

if __name__ == "__main__":
    test_complex_paradox()