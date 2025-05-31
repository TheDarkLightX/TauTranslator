#!/usr/bin/env python3
"""Test TAU to Plain English translation specifically"""

import requests

def test_tau_to_plain_english():
    """Test the exact case you mentioned"""
    api_url = "http://localhost:3000/api/translate"
    
    print("🧪 Testing TAU → Plain English")
    print("=" * 40)
    
    # Test the problematic sentence
    tau_input = "paradox(b) := ex b all X barber(b, X)"
    
    print(f"Input TAU: {tau_input}")
    
    response = requests.post(api_url, json={
        "sourceText": tau_input,
        "sourceLangKey": "TAU",
        "targetLangKey": "PLAIN_ENGLISH"
    })
    
    if response.status_code == 200:
        result = response.json()
        output = result['translatedText']
        print(f"Output Plain English: {output}")
        
        # Check for problems
        if "such that=" in output:
            print("❌ FAIL: Contains malformed 'such that=' syntax")
            return False
        elif output.startswith("The logical statement is:"):
            print("❌ FAIL: Still showing raw JSON instead of natural language")
            return False
        elif "Define" in output and "there exists" in output:
            print("✅ PASS: Proper natural language output!")
            return True
        else:
            print(f"⚠️  UNKNOWN: Output format not recognized")
            return False
    else:
        print(f"❌ FAIL: API error {response.status_code}")
        return False

if __name__ == "__main__":
    test_tau_to_plain_english()