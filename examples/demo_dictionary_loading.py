#!/usr/bin/env python3
"""
Demo of Custom Dictionary Loading System
========================================

Demonstrates the complete dictionary management system:
1. Loading different file formats (JSON, YAML, CSV)
2. Managing multiple dictionaries
3. Auto-complete with custom terms
4. Domain-specific vocabulary integration
"""

import os
from dictionary_manager import DictionaryManager
from nlp_integration import NLPTranslationService

def demo_dictionary_loading():
    """Demo loading different dictionary formats"""
    print("📚 DICTIONARY LOADING DEMO")
    print("=" * 50)
    
    dict_manager = DictionaryManager()
    
    # Get example dictionary paths
    examples_dir = "example_dictionaries"
    json_file = os.path.join(examples_dir, "agile_requirements.json")
    yaml_file = os.path.join(examples_dir, "security_domain.yaml")
    csv_file = os.path.join(examples_dir, "simple_terms.csv")
    
    print("\n1. Loading JSON Dictionary (Agile Requirements)")
    if os.path.exists(json_file):
        result = dict_manager.load_dictionary_file(json_file)
        print(f"   Result: {result.message}")
        print(f"   Entries loaded: {result.entries_loaded}")
    else:
        print(f"   ⚠️  Example file not found: {json_file}")
    
    print("\n2. Loading YAML Dictionary (Security Domain)")
    if os.path.exists(yaml_file):
        result = dict_manager.load_dictionary_file(yaml_file)
        print(f"   Result: {result.message}")
        print(f"   Entries loaded: {result.entries_loaded}")
    else:
        print(f"   ⚠️  Example file not found: {yaml_file}")
    
    print("\n3. Loading CSV Dictionary (Simple Terms)")
    if os.path.exists(csv_file):
        result = dict_manager.load_dictionary_file(csv_file)
        print(f"   Result: {result.message}")
        print(f"   Entries loaded: {result.entries_loaded}")
    else:
        print(f"   ⚠️  Example file not found: {csv_file}")
    
    return dict_manager

def demo_dictionary_management(dict_manager):
    """Demo dictionary management operations"""
    print("\n\n🔧 DICTIONARY MANAGEMENT DEMO")
    print("=" * 50)
    
    print("\n1. Listing All Loaded Dictionaries:")
    dictionaries = dict_manager.list_dictionaries()
    for dict_info in dictionaries:
        status = "✅ Enabled" if dict_info["enabled"] else "❌ Disabled"
        print(f"   📖 {dict_info['name']} ({dict_info['format']}) - {dict_info['entries_count']} entries {status}")
        if dict_info.get('metadata', {}).get('description'):
            print(f"      Description: {dict_info['metadata']['description']}")
    
    print(f"\n2. Total Dictionaries Loaded: {len(dictionaries)}")
    
    # Demo enable/disable
    if len(dictionaries) > 1:
        test_dict = next((d for d in dictionaries if d['name'] != 'default'), None)
        if test_dict:
            dict_name = test_dict['name']
            print(f"\n3. Disabling Dictionary: {dict_name}")
            result = dict_manager.set_dictionary_enabled(dict_name, False)
            print(f"   {result.message}")
            
            print(f"\n4. Re-enabling Dictionary: {dict_name}")
            result = dict_manager.set_dictionary_enabled(dict_name, True)
            print(f"   {result.message}")

def demo_custom_vocabulary_in_autocomplete(dict_manager):
    """Demo how custom dictionaries enhance auto-complete"""
    print("\n\n🤖 CUSTOM VOCABULARY IN AUTO-COMPLETE")
    print("=" * 50)
    
    # Create NLP service with our loaded dictionaries
    nlp_service = NLPTranslationService()
    nlp_service.dictionary_manager = dict_manager
    nlp_service.refresh_vocabulary()
    
    # Test various terms that should come from custom dictionaries
    test_terms = [
        "user",          # Should include "user story" from agile dictionary
        "auth",          # Should include "authentication" from security dictionary  
        "system",        # Should include "system ready" from simple terms
        "data",          # Should include "data processed" from simple terms
        "secure"         # Should include security terms
    ]
    
    for term in test_terms:
        print(f"\n📝 Auto-complete suggestions for '{term}':")
        suggestions = nlp_service.get_autocomplete_suggestions(term, max_suggestions=4)
        
        if suggestions:
            for i, suggestion in enumerate(suggestions, 1):
                category = suggestion.get('type', 'unknown')
                print(f"   {i}. {suggestion['text']} ({category})")
        else:
            print("   No suggestions found")

def demo_vocabulary_search(dict_manager):
    """Demo vocabulary search with custom dictionaries"""
    print("\n\n🔍 VOCABULARY SEARCH WITH CUSTOM TERMS")
    print("=" * 50)
    
    nlp_service = NLPTranslationService()
    nlp_service.dictionary_manager = dict_manager
    nlp_service.refresh_vocabulary()
    
    search_terms = ["story", "security", "authentication", "data"]
    
    for term in search_terms:
        print(f"\n🔎 Searching for '{term}':")
        results = nlp_service.search_vocabulary(term)
        
        if results:
            for result in results[:3]:  # Show top 3 results
                print(f"   📖 {result['key']} ({result['category']})")
                print(f"      {result['canonical']}")
                if result.get('context'):
                    print(f"      Context: {result['context']}")
        else:
            print("   No matches found")

def demo_enhanced_translation_with_custom_terms():
    """Demo enhanced translation using custom vocabulary"""
    print("\n\n🔄 ENHANCED TRANSLATION WITH CUSTOM VOCABULARY")
    print("=" * 50)
    
    # Example requirements using custom vocabulary
    test_requirements = [
        "As a user story, authentication must be verified",
        "When user authenticated and data valid, system responds",
        "For security vulnerability prevention, all data encrypted"
    ]
    
    nlp_service = NLPTranslationService()
    
    for requirement in test_requirements:
        print(f"\nRequirement: {requirement}")
        
        # This would normally go through the full translation pipeline
        # For demo, show how it would be enhanced
        enhanced = nlp_service.enhance_translation_output(
            f"The system shall ensure that {requirement.lower()}", 
            num_variants=2
        )
        
        print("Enhanced variants:")
        for i, variant in enumerate(enhanced["variants"], 1):
            print(f"   {i}. {variant['text']}")

def demo_real_world_scenario():
    """Demo a complete real-world usage scenario"""
    print("\n\n🌍 REAL-WORLD SCENARIO: Agile Team Using Custom Dictionary")
    print("=" * 70)
    
    print("""
Scenario: An agile development team loads their custom requirements 
dictionary and uses the enhanced auto-complete to write user stories.
""")
    
    # Simulate loading team's custom dictionary
    dict_manager = DictionaryManager()
    
    print("\n1. Team loads their agile requirements dictionary...")
    examples_dir = "example_dictionaries" 
    json_file = os.path.join(examples_dir, "agile_requirements.json")
    
    if os.path.exists(json_file):
        result = dict_manager.load_dictionary_file(json_file)
        print(f"   ✅ {result.message}")
        
        # Integrate with NLP service
        nlp_service = NLPTranslationService()
        nlp_service.dictionary_manager = dict_manager
        nlp_service.refresh_vocabulary()
        
        print("\n2. Team member starts typing a user story...")
        typing_sequence = [
            "As a",
            "As a user",
            "As a user story",
            "As a user story specifies"
        ]
        
        for step, text in enumerate(typing_sequence, 1):
            print(f"\n   Step {step}: Types '{text}'")
            suggestions = nlp_service.get_autocomplete_suggestions(text, max_suggestions=2)
            if suggestions:
                print("   💡 Smart suggestions:")
                for suggestion in suggestions:
                    print(f"      → {suggestion['text']}")
        
        print("\n3. Final enhanced requirement:")
        final_req = "As a user story specifies functionality, acceptance criteria must be defined"
        print(f"   📝 {final_req}")
        
        print("\n4. System provides multiple natural language variants:")
        enhanced = nlp_service.enhance_translation_output(final_req, num_variants=2)
        for i, variant in enumerate(enhanced["variants"], 1):
            print(f"   {i}. {variant['text']} (Style: {variant['style']})")
    
    else:
        print(f"   ⚠️  Demo dictionary not found at {json_file}")

if __name__ == "__main__":
    print("📚 CUSTOM DICTIONARY LOADING SYSTEM DEMO")
    print("Built using Test-Driven Development (TDD)")
    print("=" * 60)
    
    # Run all demos
    dict_manager = demo_dictionary_loading()
    demo_dictionary_management(dict_manager)
    demo_custom_vocabulary_in_autocomplete(dict_manager)
    demo_vocabulary_search(dict_manager)
    demo_enhanced_translation_with_custom_terms()
    demo_real_world_scenario()
    
    print("\n\n✨ DICTIONARY SYSTEM SUMMARY")
    print("=" * 40)
    print("✅ Multiple file format support (JSON, YAML, CSV)")
    print("✅ Dictionary validation and error handling")
    print("✅ Enable/disable and management operations")
    print("✅ Seamless integration with auto-complete")
    print("✅ Domain-specific vocabulary enhancement")
    print("✅ Real-time vocabulary refresh")
    print("\n🚀 Ready for web interface integration!")