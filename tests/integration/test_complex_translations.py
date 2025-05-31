#!/usr/bin/env python3
"""
Test Complex Translations
========================

Test the translator with larger, more complex Tau specifications.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from production_translator import ProductionTranslator

# Complex Tau examples
COMPLEX_TAU_EXAMPLES = [
    # 1. Multi-line function with temporal logic
    """
    sbf input_stream = ifile("sensor_data.txt")
    sbf output_stream = ofile("processed_data.txt")
    
    r sensor_valid[t] = input_stream[t] > 0 & input_stream[t] < 100
    r sensor_average[t] = (input_stream[t] + input_stream[t-1] + input_stream[t-2]) / 3
    
    always sensor_valid[t] -> output_stream[t] = sensor_average[t]
    sometimes sensor_valid[t] & sensor_average[t] > 50
    """,
    
    # 2. Logic gates specification
    """
    # AND gate with temporal behavior
    r and_gate[t] = i1[t] & i2[t]
    
    # OR gate with delay
    r or_gate[t] = i1[t-1] | i2[t-1]
    
    # XOR gate
    r xor_gate[t] = i1[t] + i2[t]
    
    # Complex expression
    r output[t] = (and_gate[t] | or_gate[t]) & ~xor_gate[t]
    
    always output[t] -> status[t] = 1
    """,
    
    # 3. State machine specification
    """
    # Traffic light controller
    r red_light[0] = 1
    r yellow_light[0] = 0
    r green_light[0] = 0
    
    r red_light[t] = green_light[t-1] & timer[t-1] > 30
    r yellow_light[t] = red_light[t-1] & timer[t-1] > 60 | green_light[t-1] & timer[t-1] > 30
    r green_light[t] = yellow_light[t-1] & timer[t-1] > 5
    
    always (red_light[t] + yellow_light[t] + green_light[t]) = 1
    """
]

# Complex TCE examples
COMPLEX_TCE_EXAMPLES = [
    # 1. Natural language requirements
    """
    Define a system that monitors temperature sensors.
    The temperature reading at any time must be between 0 and 100 degrees.
    Calculate the moving average using the last three readings.
    Always output the average when the reading is valid.
    Sometimes the average exceeds 50 degrees.
    """,
    
    # 2. Business logic specification
    """
    When a customer places an order, check inventory levels.
    If inventory is sufficient, approve the order immediately.
    If inventory is low but above zero, flag for review.
    If inventory is zero, reject the order.
    Always maintain audit trail of decisions.
    """,
    
    # 3. Safety requirements
    """
    The emergency stop button must always override all other controls.
    When pressed, the system must halt within 100 milliseconds.
    After emergency stop, manual reset is required.
    Never allow automatic restart after emergency stop.
    Log all emergency events with timestamp.
    """
]

def test_complex_translations():
    """Test translator with complex examples."""
    translator = ProductionTranslator()
    
    print("=" * 80)
    print("TESTING COMPLEX TAU TO TCE TRANSLATIONS")
    print("=" * 80)
    
    for i, tau_example in enumerate(COMPLEX_TAU_EXAMPLES, 1):
        print(f"\n--- Example {i}: Complex Tau Specification ---")
        print("INPUT (Tau):")
        print(tau_example.strip())
        print("\nOUTPUT (TCE):")
        
        result = translator.translate(tau_example, "tau_to_tce")
        if result["success"]:
            print(result["output"])
            print(f"\nConfidence: {result.get('confidence', 'N/A')}")
            print(f"Patterns detected: {result.get('patterns', [])}")
        else:
            print(f"ERROR: {result.get('error', 'Unknown error')}")
        
        print("-" * 80)
    
    print("\n" + "=" * 80)
    print("TESTING COMPLEX TCE TO TAU TRANSLATIONS")
    print("=" * 80)
    
    for i, tce_example in enumerate(COMPLEX_TCE_EXAMPLES, 1):
        print(f"\n--- Example {i}: Natural Language Requirements ---")
        print("INPUT (TCE):")
        print(tce_example.strip())
        print("\nOUTPUT (Tau):")
        
        result = translator.translate(tce_example, "tce_to_tau")
        if result["success"]:
            print(result["output"])
            print(f"\nConfidence: {result.get('confidence', 'N/A')}")
        else:
            print(f"ERROR: {result.get('error', 'Unknown error')}")
        
        print("-" * 80)

if __name__ == "__main__":
    test_complex_translations()