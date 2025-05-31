#!/usr/bin/env python3
"""
Verify TDD Improvements
======================
Test that our fixes actually improved the complex requirements handling.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from tau_translator_omega.core_engine.nlp_enhanced.english_to_tau_translator import EnglishToTauTranslator

def test_improvements():
    """Test the specific improvements made through TDD"""
    
    translator = EnglishToTauTranslator()
    
    # The exact failing case from complex testing
    failing_case = "For every transaction above $10,000, all approvers in the chain must digitally sign within their respective authority limits before processing."
    
    print("🧪 Testing Previously Failing Quantified Constraint")
    print("=" * 60)
    print(f"Text: {failing_case}")
    
    result = translator.translate(failing_case)
    
    print(f"\n📊 Before Fix:")
    print(f"  Confidence: 0.57 (FAIL)")
    print(f"  Issues: 'No predicates identified', 'No entities identified'")
    
    print(f"\n📊 After Fix:")
    print(f"  Confidence: {result.confidence.overall:.2f}")
    print(f"  Issues: {result.confidence.issues if result.confidence.issues else 'None'}")
    
    print(f"\n🧠 Semantic Analysis Results:")
    print(f"  Predicates: {len(result.semantic_analysis.predicates)} found")
    print(f"    {result.semantic_analysis.predicates}")
    print(f"  Entities: {len(result.semantic_analysis.entities)} found") 
    print(f"    {result.semantic_analysis.entities}")
    print(f"  Quantifiers: {result.semantic_analysis.quantifiers}")
    print(f"  Logical Operators: {result.semantic_analysis.logical_operators}")
    
    # Test other complex cases that should now work better
    complex_cases = [
        "The cryptographic key management system shall implement hierarchical derivation.",
        "Market data processing must handle at least 100,000 price updates per second.",
        "Cardiac monitoring devices must detect arrhythmia patterns with high accuracy.",
        "Portfolio exposure must not exceed leverage ratio limits during volatile conditions."
    ]
    
    print(f"\n🎯 Testing Additional Complex Cases:")
    print("=" * 60)
    
    for i, case in enumerate(complex_cases, 1):
        result = translator.translate(case)
        print(f"\n{i}. {case[:50]}...")
        print(f"   Confidence: {result.confidence.overall:.2f}")
        print(f"   Predicates: {len(result.semantic_analysis.predicates)}")
        print(f"   Entities: {len(result.semantic_analysis.entities)}")
        
        status = "✅ GOOD" if result.confidence.overall > 0.7 else ("⚠️ FAIR" if result.confidence.overall > 0.6 else "❌ POOR")
        print(f"   Status: {status}")

def test_scalability_improvement():
    """Test that scalability issues are improved"""
    
    translator = EnglishToTauTranslator()
    
    # Test the complex requirement that had degraded performance
    complex_req = """
    The distributed microservices architecture must implement circuit breaker patterns 
    with exponential backoff retry mechanisms, ensuring that when any downstream service 
    becomes unavailable or responds with latency exceeding 500 milliseconds, the calling 
    service automatically switches to cached responses or degraded functionality mode 
    while continuously monitoring service health through heartbeat mechanisms and 
    automatically restoring full functionality when services recover and demonstrate 
    stable performance for at least 60 seconds.
    """
    
    print(f"\n📈 Scalability Test (89 words)")
    print("=" * 60)
    
    result = translator.translate(complex_req)
    
    print(f"Previous Results:")
    print(f"  Confidence: 0.62")
    print(f"  Issues: 2")
    print(f"  Predicates: 0")
    print(f"  Entities: 0")
    
    print(f"\nImproved Results:")
    print(f"  Confidence: {result.confidence.overall:.2f}")
    print(f"  Issues: {len(result.confidence.issues)}")
    print(f"  Predicates: {len(result.semantic_analysis.predicates)}")
    print(f"  Entities: {len(result.semantic_analysis.entities)}")
    
    improvement = result.confidence.overall - 0.62
    print(f"\n📊 Improvement: {improvement:+.2f} ({improvement/0.62*100:+.1f}%)")
    
    if improvement > 0:
        print("✅ TDD improvements successful!")
    else:
        print("❌ TDD improvements not effective")

if __name__ == "__main__":
    test_improvements()
    test_scalability_improvement()