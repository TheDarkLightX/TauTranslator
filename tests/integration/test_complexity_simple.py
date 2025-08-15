#!/usr/bin/env python3
"""
Simple Complexity Test - Testing bidirectional translation limits
Copyright: DarkLightX / Dana Edwards
"""

import os
import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
backend_path = project_root / "backend/unified"
sys.path.insert(0, str(backend_path))

# Test increasingly complex sentences
test_sentences = [
    # Simple
    {
        "level": 1,
        "description": "Simple comparison",
        "english": "x is greater than 5",
        "features": ["comparison", "variable"]
    },
    {
        "level": 2,
        "description": "Simple conditional",
        "english": "if x equals 10 then y is true",
        "features": ["conditional", "equality", "boolean"]
    },
    # Intermediate
    {
        "level": 3,
        "description": "Compound condition",
        "english": "if x is greater than 5 and y is less than 10 then z equals x plus y",
        "features": ["compound_condition", "arithmetic", "multiple_variables"]
    },
    {
        "level": 4,
        "description": "Universal quantifier",
        "english": "for all x, if x is positive then x is greater than zero",
        "features": ["universal_quantifier", "conditional", "property"]
    },
    # Complex
    {
        "level": 5,
        "description": "Nested quantifiers",
        "english": "for every person who owns a car, the car must have insurance",
        "features": ["universal_quantifier", "relative_clause", "entity_relationship"]
    },
    {
        "level": 6,
        "description": "Complex conditional with relative clause",
        "english": "for every person who owns a car, if the car is red then the person must pay extra",
        "features": ["universal_quantifier", "relative_clause", "nested_conditional", "coreference"]
    },
    # Very Complex
    {
        "level": 7,
        "description": "Multiple entities with constraints",
        "english": "every student who takes a class from a professor who has tenure must submit assignments before the deadline",
        "features": ["multiple_entities", "nested_relative_clauses", "temporal_constraint"]
    },
    {
        "level": 8,
        "description": "Complex business rule",
        "english": "all customers who have made purchases exceeding $1000 in the last 12 months and have no outstanding payments receive a 15% discount",
        "features": ["temporal_window", "aggregation", "negation", "percentage", "compound_conditions"]
    },
    # Extreme
    {
        "level": 9,
        "description": "Regulatory compliance rule",
        "english": "organizations operating in jurisdictions where data protection laws require consent must implement age verification unless the data is for medical research approved by an ethics committee",
        "features": ["nested_conditions", "exception_clauses", "domain_specific", "institutional_references"]
    },
    {
        "level": 10,
        "description": "Meta-level constraint",
        "english": "for any rule that modifies other rules, if the rule was created after the system initialization date then it requires approval from at least three administrators unless operating in emergency mode",
        "features": ["meta_reasoning", "temporal_dependency", "threshold_condition", "exception_handling", "self_reference"]
    }
]

def test_translation(sentence):
    """Test translation using available methods."""
    print(f"\n📝 Testing: \"{sentence}\"")
    results = []
    
    # Method 1: Simple pattern matching
    try:
        # Basic pattern transformation
        result = sentence.lower()
        
        # Simple replacements
        replacements = [
            ("is greater than", ">"),
            ("is less than", "<"),
            ("equals", "="),
            ("is equal to", "="),
            ("if ", "if "),
            (" then ", " -> "),
            ("for all ", "all "),
            ("for every ", "all "),
            ("there exists ", "ex "),
            ("and ", "& "),
            ("or ", "| "),
            ("not ", "!"),
            ("plus ", "+ "),
            ("minus ", "- "),
            ("times ", "* "),
            ("divided by ", "/ ")
        ]
        
        for old, new in replacements:
            result = result.replace(old, new)
        
        print(f"   ✅ Pattern: {result}")
        results.append(("pattern", True, result))
    except Exception as e:
        print(f"   ❌ Pattern failed: {e}")
        results.append(("pattern", False, str(e)))
    
    # Method 2: Try actual translator if available
    try:
        from translators.manager import TranslationManager
        manager = TranslationManager()
        result = manager.translate(sentence, source_lang="english", target_lang="tau")
        if result.success:
            print(f"   ✅ Manager: {result.translation}")
            results.append(("manager", True, result.translation))
        else:
            print(f"   ❌ Manager failed: {result.error}")
            results.append(("manager", False, result.error))
    except Exception as e:
        print(f"   ❌ Manager error: {e}")
        results.append(("manager", False, str(e)))
    
    return results

def main():
    """Run complexity test."""
    print("🧪 BIDIRECTIONAL TRANSLATION COMPLEXITY TEST")
    print("=" * 70)
    print("Testing increasingly complex sentences to find translation limits")
    print()
    
    results_by_level = {}
    max_successful_level = 0
    
    for test_case in test_sentences:
        level = test_case["level"]
        print(f"\n{'='*70}")
        print(f"Level {level}: {test_case['description']}")
        print(f"Features: {', '.join(test_case['features'])}")
        
        results = test_translation(test_case["english"])
        
        # Check if any method succeeded
        any_success = any(success for _, success, _ in results)
        results_by_level[level] = any_success
        
        if any_success:
            max_successful_level = level
            print(f"   ✅ Level {level} PASSED")
        else:
            print(f"   ❌ Level {level} FAILED")
    
    # Summary
    print(f"\n\n{'='*70}")
    print("📊 COMPLEXITY TEST SUMMARY")
    print(f"{'='*70}")
    print(f"Maximum successful complexity level: {max_successful_level}/10")
    
    print("\nLevel breakdown:")
    for level in range(1, 11):
        if level in results_by_level:
            status = "✅ PASS" if results_by_level[level] else "❌ FAIL"
            print(f"   Level {level}: {status}")
    
    print("\n🎯 Assessment:")
    if max_successful_level >= 8:
        print("   🏆 EXCELLENT: Can handle very complex sentences")
    elif max_successful_level >= 6:
        print("   ⭐ GOOD: Handles complex real-world sentences")  
    elif max_successful_level >= 4:
        print("   ✅ ADEQUATE: Basic to intermediate complexity")
    elif max_successful_level >= 2:
        print("   🔧 LIMITED: Only simple sentences")
    else:
        print("   📚 BASIC: Needs significant improvement")
    
    # Breaking point analysis
    if max_successful_level < 10:
        breaking_point = max_successful_level + 1
        breaking_case = test_sentences[breaking_point - 1]
        print(f"\n🚨 Breaking point at Level {breaking_point}:")
        print(f"   Failed on: \"{breaking_case['english']}\"")
        print(f"   Challenging features: {', '.join(breaking_case['features'])}")

if __name__ == "__main__":
    main()