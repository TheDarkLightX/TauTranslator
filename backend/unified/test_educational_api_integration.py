"""
Test the educational autocomplete API integration.

This test verifies the integration between the educational autocomplete
service and the API layer.

Copyright: DarkLightX / Dana Edwards
"""

import sys
from pathlib import Path

# Add the backend path to sys.path for imports
sys.path.append(str(Path(__file__).parent))

# Direct test without API imports - test the core service
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

def test_basic_educational_request():
    """Test basic educational autocomplete request."""
    request = EducationalAutocompleteRequest(
        text="alw",
        language_mode=EducationalLanguageMode.TAU,
        learning_level=LearningLevel.BEGINNER,
        include_examples=True,
        include_explanations=True,
        include_hints=True,
        max_suggestions=5
    )
    
    print(f"Testing request: {request}")
    
    # Process request (without actual NLP service)
    result = _educational_adapter.process_request_async(request, None)
    
    # Since this is synchronous, we need to await the result
    import asyncio
    result = asyncio.run(result)
    
    if isinstance(result, Success):
        print("\n✓ Success! Response:")
        response = result.value
        
        print(f"\nEducational Mode: {response.get('educational_mode', False)}")
        print(f"Language Mode: {response.get('language_mode', 'N/A')}")
        print(f"Learning Level: {response.get('learning_level', 'N/A')}")
        print(f"Context Hint: {response.get('context_hint', 'N/A')}")
        print(f"Learning Tip: {response.get('learning_tip', 'N/A')}")
        
        print(f"\nSuggestions ({len(response['suggestions'])}):")
        for i, suggestion in enumerate(response['suggestions'], 1):
            print(f"\n{i}. {suggestion['text']}")
            print(f"   Category: {suggestion['category']}")
            print(f"   Difficulty: {suggestion['difficulty']}")
            if 'explanation' in suggestion:
                print(f"   Explanation: {suggestion['explanation']}")
            if 'example' in suggestion:
                print(f"   Example: {suggestion['example']}")
            if 'tau_equivalent' in suggestion:
                print(f"   TAU Equivalent: {suggestion['tau_equivalent']}")
    else:
        print(f"\n✗ Error: {result.message}")

def test_tce_mode():
    """Test TCE mode autocomplete."""
    request = EducationalAutocompleteRequest(
        text="for all",
        language_mode=EducationalLanguageMode.TCE,
        learning_level=LearningLevel.INTERMEDIATE,
        include_examples=True,
        max_suggestions=3
    )
    
    print(f"\n\nTesting TCE request: {request.text}")
    
    import asyncio
    result = asyncio.run(_educational_adapter.process_request_async(request, None))
    
    if isinstance(result, Success):
        print("\n✓ Success! TCE Response:")
        response = result.value
        
        print(f"\nSuggestions:")
        for suggestion in response['suggestions']:
            print(f"\n- {suggestion['display']}")
            if 'tau_equivalent' in suggestion:
                print(f"  TAU: {suggestion['tau_equivalent']}")

def test_legacy_mode():
    """Test backward compatibility with legacy mode."""
    request = EducationalAutocompleteRequest(
        text="alw",
        # No educational features requested
        include_examples=False,
        include_explanations=False,
        include_hints=False
    )
    
    print(f"\n\nTesting legacy request (no educational features)")
    
    import asyncio
    result = asyncio.run(_educational_adapter.process_request_async(request, None))
    
    if isinstance(result, Success):
        print("\n✓ Success! Legacy Response:")
        response = result.value
        print(f"Source: {response['source']}")
        print(f"Educational Mode: {response.get('educational_mode', False)}")
        print(f"Suggestions: {len(response['suggestions'])}")
        for s in response['suggestions'][:3]:
            print(f"  - {s['text']} ({s['type']})")

if __name__ == "__main__":
    print("Educational Autocomplete API Integration Tests")
    print("=" * 50)
    
    test_basic_educational_request()
    test_tce_mode()
    test_legacy_mode()
    
    print("\n\nAll tests completed!")