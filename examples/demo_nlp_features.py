#!/usr/bin/env python3
"""
Demo of Working NLP Features
============================

Demonstrates the complete NLP enhancement system:
1. Auto-complete suggestions while typing
2. Enhanced English output variants
3. Vocabulary search and exploration
4. Context-aware suggestions
"""

from nlp_integration import NLPTranslationService

def demo_autocomplete():
    """Demo auto-complete functionality"""
    print("🤖 AUTO-COMPLETE DEMO")
    print("=" * 50)
    
    nlp = NLPTranslationService()
    
    test_inputs = [
        "",  # Empty start
        "For",  # Partial word
        "For all x",  # After quantifier
        "For all x such that",  # After "such that"
        "x and",  # Logical operator
        "always",  # Temporal context
        "Define barber"  # Definition pattern
    ]
    
    for input_text in test_inputs:
        print(f"\nInput: '{input_text}'")
        suggestions = nlp.get_autocomplete_suggestions(input_text, max_suggestions=3)
        
        for i, suggestion in enumerate(suggestions, 1):
            print(f"  {i}. {suggestion['text']}")
            print(f"     Type: {suggestion['type']} | {suggestion['description']}")

def demo_enhanced_english():
    """Demo enhanced English output generation"""
    print("\n\n📝 ENHANCED ENGLISH VARIANTS DEMO")
    print("=" * 50)
    
    nlp = NLPTranslationService()
    
    # Test with complex CNL input
    cnl_text = "Define paradox for b as: there exists b such that for all X, barber(b, X)."
    
    print(f"Original CNL: {cnl_text}")
    print("\nEnhanced Variants:")
    
    enhanced = nlp.enhance_translation_output(cnl_text, num_variants=3)
    
    for i, variant in enumerate(enhanced["variants"], 1):
        print(f"\n{i}. Style: {variant['style'].title()} | Formality: {variant['formality'].title()}")
        print(f"   Text: {variant['text']}")
        print(f"   Confidence: {variant['confidence']:.1f}")

def demo_vocabulary_search():
    """Demo vocabulary search functionality"""
    print("\n\n🔍 VOCABULARY SEARCH DEMO")  
    print("=" * 50)
    
    nlp = NLPTranslationService()
    
    search_terms = ["exists", "and", "always"]
    
    for term in search_terms:
        print(f"\nSearching for: '{term}'")
        results = nlp.search_vocabulary(term)
        
        for result in results[:2]:  # Show top 2 results
            print(f"  📖 {result['key']} ({result['category']})")
            print(f"     Canonical: {result['canonical']}")
            print(f"     Variants: {', '.join(result['variants'][:3])}")
            if result['examples']:
                print(f"     Example: {result['examples'][0]}")

def demo_translation_enhancement():
    """Demo complete translation enhancement workflow"""
    print("\n\n🔄 TRANSLATION ENHANCEMENT WORKFLOW")
    print("=" * 50)
    
    nlp = NLPTranslationService()
    
    # Simulate TAU → Enhanced English pipeline
    tau_input = "paradox(b) := ex b all X barber(b, X)"
    
    print(f"Original TAU: {tau_input}")
    
    # Get enhanced translation with variants
    result = nlp.translate_with_variants(
        tau_input, 
        source="TAU", 
        target="PLAIN_ENGLISH", 
        num_variants=3
    )
    
    print(f"\nBase Translation: {result['original']}")
    print("\nNatural Language Variants:")
    
    for i, variant in enumerate(result["variants"], 1):
        print(f"\n{i}. {variant['text']}")
        print(f"   Style: {variant['style']} | Formality: {variant['formality']}")

def demo_real_world_scenario():
    """Demo a real-world usage scenario"""
    print("\n\n🌍 REAL-WORLD SCENARIO: User Writing Requirements")
    print("=" * 60)
    
    nlp = NLPTranslationService()
    
    # Simulate user typing step by step
    typing_sequence = [
        "For",
        "For all",
        "For all users",
        "For all users such that",
        "For all users such that they are active"
    ]
    
    print("Simulating user typing with auto-complete:")
    
    for step, text in enumerate(typing_sequence, 1):
        print(f"\nStep {step}: User types '{text}'")
        suggestions = nlp.get_autocomplete_suggestions(text, max_suggestions=2)
        
        if suggestions:
            print("  Auto-complete suggestions:")
            for suggestion in suggestions:
                print(f"    → {suggestion['text']}")
        else:
            print("  No suggestions (user is on their own!)")
    
    # Final translation
    final_text = "For all users such that they are active, the system should respond quickly."
    print(f"\nFinal requirement: {final_text}")
    print("\nThis would translate to formal logic and provide enhanced variants!")

if __name__ == "__main__":
    print("🧠 NLP FEATURES DEMONSTRATION")
    print("Built using Test-Driven Development (TDD)")
    print("=" * 60)
    
    demo_autocomplete()
    demo_enhanced_english()
    demo_vocabulary_search()
    demo_translation_enhancement()
    demo_real_world_scenario()
    
    print("\n\n✨ SUMMARY")
    print("=" * 30)
    print("✅ Auto-complete for requirements writing")
    print("✅ Multiple natural language variants")
    print("✅ Domain-specific vocabulary")
    print("✅ Context-aware suggestions")
    print("✅ Enhanced user experience")
    print("\nReady for integration with TauTranslator web interface! 🚀")