"""
Test the educational autocomplete core service directly.

This test verifies the educational autocomplete service works correctly.

Copyright: DarkLightX / Dana Edwards
"""

import sys
from pathlib import Path

# Add the backend path to sys.path for imports
sys.path.append(str(Path(__file__).parent))

from core.autocomplete import (
    EducationalAutocompleteService,
    AutocompleteConfiguration,
    SuggestionRequest,
    SpecificationContext,
    LanguageMode,
    DifficultyLevel,
    ContextType,
    CursorPosition
)
from core.result_enhanced import Success

def test_tau_educational_autocomplete():
    """Test TAU language educational autocomplete."""
    print("Testing TAU Educational Autocomplete")
    print("-" * 40)
    
    # Initialize service
    config = AutocompleteConfiguration(
        enable_tau_suggestions=True,
        enable_tce_suggestions=True,
        include_educational_hints=True,
        include_examples=True
    )
    service = EducationalAutocompleteService(config)
    
    # Create TAU context
    context = SpecificationContext(
        full_text="alw",
        cursor_position=CursorPosition(3),
        language_mode=LanguageMode.TAU,
        context_type=ContextType.TEMPORAL_CONSTRAINT,
        learning_level=DifficultyLevel.BEGINNER
    )
    
    # Create request
    request = SuggestionRequest(
        context=context,
        max_suggestions=5,
        include_templates=True,
        include_examples=True
    )
    
    # Get suggestions
    result = service.get_suggestions_async(request)
    
    if isinstance(result, Success):
        response = result.value
        print(f"✓ Success! Got {len(response.suggestions)} suggestions")
        
        if response.context_hint:
            print(f"\nContext Hint: {response.context_hint}")
        
        if response.learning_tip:
            print(f"Learning Tip: {response.learning_tip}")
        
        print(f"\nSuggestions:")
        for i, suggestion in enumerate(response.suggestions, 1):
            print(f"\n{i}. {suggestion.text}")
            print(f"   Category: {suggestion.category.value}")
            print(f"   Difficulty: {suggestion.difficulty.value}")
            print(f"   Description: {suggestion.description}")
            if suggestion.example:
                print(f"   Example: {suggestion.example}")
    else:
        print(f"✗ Error: {result.error_code} - {result.message}")

def test_tce_educational_autocomplete():
    """Test TCE language educational autocomplete."""
    print("\n\nTesting TCE Educational Autocomplete")
    print("-" * 40)
    
    # Initialize service
    service = EducationalAutocompleteService()
    
    # Create TCE context
    context = SpecificationContext(
        full_text="for all",
        cursor_position=CursorPosition(7),
        language_mode=LanguageMode.TCE,
        context_type=ContextType.QUANTIFIER_EXPRESSION,
        learning_level=DifficultyLevel.INTERMEDIATE
    )
    
    # Create request
    request = SuggestionRequest(
        context=context,
        max_suggestions=3
    )
    
    # Get suggestions
    result = service.get_suggestions_async(request)
    
    if isinstance(result, Success):
        response = result.value
        print(f"✓ Success! Got {len(response.suggestions)} suggestions")
        
        print(f"\nSuggestions:")
        for suggestion in response.suggestions:
            print(f"\n- {suggestion.display}")
            print(f"  Description: {suggestion.description}")
            if suggestion.tau_equivalent:
                print(f"  TAU Equivalent: {suggestion.tau_equivalent}")
            if suggestion.example:
                print(f"  Example: {suggestion.example}")
    else:
        print(f"✗ Error: {result.error_code} - {result.message}")

def test_context_aware_suggestions():
    """Test context-aware suggestions."""
    print("\n\nTesting Context-Aware Suggestions")
    print("-" * 40)
    
    service = EducationalAutocompleteService()
    
    # Test solver context
    contexts = [
        (
            "solve ",
            ContextType.SOLVER_COMMAND,
            "Solver context"
        ),
        (
            "forall x : ",
            ContextType.QUANTIFIER_EXPRESSION,
            "Quantifier context"
        ),
        (
            "output[t] = ",
            ContextType.STREAM_RULE,
            "Stream context"
        )
    ]
    
    for text, context_type, description in contexts:
        print(f"\n{description}: '{text}'")
        
        context = SpecificationContext(
            full_text=text,
            cursor_position=CursorPosition(len(text)),
            language_mode=LanguageMode.TAU,
            context_type=context_type,
            learning_level=DifficultyLevel.INTERMEDIATE
        )
        
        request = SuggestionRequest(context=context, max_suggestions=3)
        result = service.get_suggestions_async(request)
        
        if isinstance(result, Success):
            response = result.value
            print(f"  Suggestions: {[s.text for s in response.suggestions[:3]]}")
            if response.context_hint:
                print(f"  Hint: {response.context_hint}")

def test_translation_feature():
    """Test TCE to TAU translation."""
    print("\n\nTesting Translation Feature")
    print("-" * 40)
    
    service = EducationalAutocompleteService()
    
    translations = [
        ("for all x such that x > 0", LanguageMode.TCE, LanguageMode.TAU),
        ("it is always the case that", LanguageMode.TCE, LanguageMode.TAU)
    ]
    
    for text, from_lang, to_lang in translations:
        print(f"\nTranslating: '{text}'")
        print(f"From: {from_lang.value} → To: {to_lang.value}")
        
        result = service.translate_selection_async(text, from_lang, to_lang)
        
        if isinstance(result, Success):
            print(f"Result: {result.value}")
        else:
            print(f"Error: {result.message}")

if __name__ == "__main__":
    print("Educational Autocomplete Core Service Tests")
    print("=" * 50)
    
    test_tau_educational_autocomplete()
    test_tce_educational_autocomplete()
    test_context_aware_suggestions()
    test_translation_feature()
    
    print("\n\nAll tests completed!")