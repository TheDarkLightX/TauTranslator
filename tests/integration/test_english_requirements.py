#!/usr/bin/env python3
"""
Test English Requirements to Tau Translation
==========================================
Real-world test of the enhanced NLP capabilities.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from tau_translator_omega.core_engine.nlp_enhanced.english_to_tau_translator import EnglishToTauTranslator
from tau_translator_omega.core_engine.nlp_enhanced.requirements_analyzer import RequirementsAnalyzer

def test_real_requirements():
    """Test with real English requirements paragraphs"""
    
    translator = EnglishToTauTranslator()
    analyzer = RequirementsAnalyzer()
    
    # Real requirements examples
    requirements_examples = [
        {
            "title": "Prime Number Validator",
            "text": """
            The system must validate that any input number is a prime number. 
            For all integers greater than 1, a number is prime if it has exactly 
            two distinct positive divisors: 1 and itself. The system shall reject 
            any number that is not prime and display an appropriate error message.
            """
        },
        {
            "title": "User Authentication",
            "text": """
            Every user who attempts to access the system must be authenticated. 
            If the user provides valid credentials and their account is active, 
            then access shall be granted. Otherwise, access must be denied and 
            the attempt logged for security purposes.
            """
        },
        {
            "title": "Performance Requirements",
            "text": """
            The system must process all requests within 100 milliseconds. 
            For any operation that takes longer than this threshold, the system 
            should return a timeout error. Additionally, the system must handle 
            at least 1000 concurrent users without degradation.
            """
        }
    ]
    
    print("🚀 Testing English Requirements to Tau Translation\n")
    
    for req_example in requirements_examples:
        print(f"📋 {req_example['title']}")
        print("=" * 50)
        
        # Extract requirements
        requirements = analyzer.extract_requirements(req_example['text'])
        print(f"📊 Extracted {len(requirements)} requirements:")
        
        for i, req in enumerate(requirements, 1):
            print(f"  {i}. Type: {req.type.name}")
            print(f"     Entities: {req.entities[:3]}...")
            print(f"     Predicates: {req.predicates[:3]}...")
            print(f"     Confidence: {req.confidence:.2f}")
            print(f"     Has quantification: {req.has_quantification}")
        
        print(f"\n🔄 Translating to Tau...")
        
        # Translate to Tau
        result = translator.translate(req_example['text'])
        
        print(f"📝 Tau Specification:")
        print("```tau")
        print(result.tau_specification)
        print("```")
        
        print(f"\n📈 Translation Quality:")
        print(f"  Overall Confidence: {result.confidence.overall:.2f}")
        print(f"  Syntax: {result.confidence.syntax:.2f}")
        print(f"  Semantics: {result.confidence.semantics:.2f}")
        print(f"  Logical Structure: {result.confidence.logical_structure:.2f}")
        print(f"  Mathematical: {result.confidence.mathematical:.2f}")
        
        if result.confidence.issues:
            print(f"  Issues: {', '.join(result.confidence.issues)}")
        
        print(f"\n🧠 Semantic Analysis:")
        print(f"  Predicates: {result.semantic_analysis.predicates}")
        print(f"  Entities: {result.semantic_analysis.entities}")
        print(f"  Quantifiers: {result.semantic_analysis.quantifiers}")
        print(f"  Logical Operators: {result.semantic_analysis.logical_operators}")
        
        if result.translation_notes:
            print(f"\n📋 Notes: {', '.join(result.translation_notes)}")
        
        print("\n" + "="*70 + "\n")

def test_document_translation():
    """Test complete document translation"""
    
    translator = EnglishToTauTranslator()
    
    document = """
    System Requirements for Secure Database Access
    
    1. Authentication Requirements
    Every user attempting to access the database must provide valid credentials.
    The system shall authenticate users before granting any access privileges.
    
    2. Authorization Rules  
    For all authenticated users, access permissions must be verified before
    allowing database operations. Users can only access data they are authorized to view.
    
    3. Data Integrity Constraints
    All data inserted into the database must be validated. If any data violates 
    integrity constraints, the operation shall be rejected and an error returned.
    
    4. Audit Requirements
    The system must log all database access attempts, successful or failed,
    with timestamp and user information for security auditing purposes.
    """
    
    print("📄 Testing Complete Document Translation")
    print("=" * 50)
    
    doc_result = translator.translate_document(document)
    
    print(f"📊 Document Statistics:")
    print(f"  Individual translations: {len(doc_result.individual_translations)}")
    print(f"  Overall confidence: {doc_result.overall_confidence:.2f}")
    print(f"  Traceability entries: {len(doc_result.traceability_map)}")
    
    print(f"\n📝 Complete Tau Specification:")
    print("```tau")
    print(doc_result.tau_specification)
    print("```")
    
    print(f"\n🔗 Traceability Map:")
    for source, tau in doc_result.traceability_map.items():
        print(f"  '{source}' → '{tau}'")

if __name__ == "__main__":
    test_real_requirements()
    print("\n")
    test_document_translation()