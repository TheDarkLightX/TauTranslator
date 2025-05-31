#!/usr/bin/env python3
"""Debug ILR to CNL translation"""

import requests
import json

# Test the exact ILR structure from TAU to ILR output
tau_input = "barberShaves(X) := p(X) = 0"

print("=== Step 1: TAU to ILR ===")
response1 = requests.post("http://localhost:8003/translate", json={
    "text": tau_input,
    "direction": "tau_to_ilr"
})

if response1.status_code == 200:
    result1 = response1.json()
    ilr_output = result1["translatedText"]
    print(f"TAU input: {tau_input}")
    print(f"ILR output: {ilr_output}")
    print(f"ILR type: {type(ilr_output)}")
    
    print("\n=== Step 2: ILR to CNL ===")
    response2 = requests.post("http://localhost:8003/translate", json={
        "text": ilr_output,
        "direction": "ilr_to_cnl"
    })
    
    if response2.status_code == 200:
        result2 = response2.json()
        cnl_output = result2["translatedText"]
        print(f"ILR input: {ilr_output}")
        print(f"CNL output: {cnl_output}")
    else:
        print(f"ILR to CNL failed: {response2.status_code} - {response2.text}")
else:
    print(f"TAU to ILR failed: {response1.status_code} - {response1.text}")

print("\n=== Test direct ILR input ===")
# Test with manually formatted ILR
manual_ilr = {
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

response3 = requests.post("http://localhost:8003/translate", json={
    "text": json.dumps(manual_ilr),
    "direction": "ilr_to_cnl"
})

if response3.status_code == 200:
    result3 = response3.json()
    cnl_output3 = result3["translatedText"]
    print(f"Manual ILR input: {json.dumps(manual_ilr)}")
    print(f"CNL output: {cnl_output3}")
else:
    print(f"Manual ILR to CNL failed: {response3.status_code} - {response3.text}")