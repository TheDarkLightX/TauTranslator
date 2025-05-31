#!/usr/bin/env python3
"""Test complex sentences through the working translation system"""

import requests
import json

def test_sentence(sentence, description):
    """Test a sentence through various translation paths"""
    api_url = "http://localhost:3000/api/translate"
    
    print(f"\n=== {description} ===")
    print(f"Original TAU: {sentence}")
    
    # TAU → ILR
    response1 = requests.post(api_url, json={
        "sourceText": sentence,
        "sourceLangKey": "TAU",
        "targetLangKey": "ILR"
    })
    
    if response1.status_code == 200:
        result1 = response1.json()
        ilr_output = result1['translatedText']
        print(f"\nILR Structure:")
        # Pretty print the JSON
        try:
            ilr_json = json.loads(ilr_output)
            print(json.dumps(ilr_json, indent=2))
        except:
            print(ilr_output)
        
        # ILR → CNL
        response2 = requests.post(api_url, json={
            "sourceText": ilr_output,
            "sourceLangKey": "ILR",
            "targetLangKey": "CNL"
        })
        
        if response2.status_code == 200:
            result2 = response2.json()
            cnl_output = result2['translatedText']
            print(f"\nCNL (Natural Language):")
            print(f"  {cnl_output}")
            
            # CNL → TAU (round trip test)
            response3 = requests.post(api_url, json={
                "sourceText": cnl_output,
                "sourceLangKey": "CNL",
                "targetLangKey": "TAU"
            })
            
            if response3.status_code == 200:
                result3 = response3.json()
                tau_output = result3['translatedText']
                print(f"\nRound-trip TAU:")
                print(f"  {tau_output}")
                
                # Check if round-trip is similar
                if tau_output.strip() == sentence.strip():
                    print("  ✅ Perfect round-trip!")
                else:
                    print("  ⚠️ Round-trip differs (expected for complex expressions)")
            else:
                print(f"  ❌ CNL→TAU failed: {response3.status_code}")
        else:
            print(f"  ❌ ILR→CNL failed: {response2.status_code}")
    else:
        print(f"  ❌ TAU→ILR failed: {response1.status_code}")

def main():
    print("🧪 Testing Complex TAU Sentences")
    print("=" * 50)
    
    # Test the sentences you provided
    test_sentence(
        "barber(X, Y) := X = Y'",
        "Barber Definition with Complement"
    )
    
    test_sentence(
        "paradox(b) := ex b all X barber(b, X)",
        "Paradox with Existential and Universal Quantifiers"
    )
    
    # Test some additional complex cases
    test_sentence(
        "forall x : P(x) -> Q(x)",
        "Universal Quantifier with Implication"
    )
    
    test_sentence(
        "always (eventually P)",
        "Nested Temporal Logic"
    )

if __name__ == "__main__":
    main()