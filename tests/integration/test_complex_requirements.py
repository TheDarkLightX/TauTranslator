#!/usr/bin/env python3
"""
Complex Multi-Sentence Requirements Test
=======================================
TDD tests for challenging, real-world requirements that push the system limits.
These tests are designed to fail initially and drive further development.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from tau_translator_omega.core_engine.nlp_enhanced.english_to_tau_translator import EnglishToTauTranslator
from tau_translator_omega.core_engine.nlp_enhanced.requirements_analyzer import RequirementsAnalyzer

def test_complex_cryptographic_system():
    """Test complex cryptographic system requirements (150+ words)"""
    
    requirement = """
    The cryptographic key management system shall implement a hierarchical key derivation 
    scheme based on PBKDF2 with SHA-256, where the master key must be derived from a user 
    passphrase of minimum 12 characters containing at least one uppercase letter, one 
    lowercase letter, one digit, and one special character. The system must generate 
    unique session keys for each authenticated user session, ensuring that no two sessions 
    share the same cryptographic material even if initiated simultaneously by the same user. 
    Furthermore, all encryption operations shall use AES-256 in GCM mode with a randomly 
    generated 96-bit initialization vector that is never reused within the same key context. 
    The system must implement perfect forward secrecy by automatically rotating session keys 
    every 15 minutes or after processing 1GB of data, whichever occurs first. Additionally, 
    key deletion must be cryptographically secure, overwriting memory locations with random 
    data at least three times before deallocation. In the event of a security breach detection, 
    the system shall immediately invalidate all active sessions and force re-authentication 
    of all users within 30 seconds.
    """
    
    print("🔐 Testing Complex Cryptographic System Requirements")
    print("=" * 70)
    print(f"Length: {len(requirement.split())} words")
    print(f"Sentences: {len(requirement.split('.'))}")
    
    analyzer = RequirementsAnalyzer()
    translator = EnglishToTauTranslator()
    
    # Extract requirements
    requirements = analyzer.extract_requirements(requirement)
    print(f"\n📊 Extracted {len(requirements)} requirements:")
    
    for i, req in enumerate(requirements, 1):
        print(f"  {i}. Type: {req.type.name}")
        print(f"     Category: {req.category}")
        print(f"     Entities: {req.entities[:5]}...")
        print(f"     Predicates: {req.predicates[:5]}...")
        print(f"     Quantification: {req.has_quantification}")
        print(f"     Conditionals: {req.logical_structure.has_conditionals}")
        print(f"     Temporal: {req.logical_structure.has_temporal}")
        print(f"     Confidence: {req.confidence:.2f}")
        print()
    
    # Translate to Tau
    result = translator.translate(requirement)
    
    print(f"🔄 Translation Result:")
    print(f"Overall Confidence: {result.confidence.overall:.2f}")
    print(f"Issues: {', '.join(result.confidence.issues) if result.confidence.issues else 'None'}")
    
    print(f"\n📝 Tau Specification:")
    print("```tau")
    print(result.tau_specification)
    print("```")
    
    return result

def test_complex_financial_trading_system():
    """Test complex financial trading system requirements (200+ words)"""
    
    requirement = """
    The high-frequency trading system must execute orders with latency not exceeding 50 
    microseconds from order receipt to market transmission, measured as the 99th percentile 
    across all trading sessions during peak market hours. The system shall implement 
    sophisticated risk management algorithms that continuously monitor portfolio exposure 
    in real-time, automatically rejecting any order that would cause the total position 
    size in any single security to exceed 5% of the portfolio's net asset value or result 
    in leverage exceeding 3:1 ratio. Market data processing must handle at least 100,000 
    price updates per second with guaranteed message ordering and no data loss, even during 
    extreme market volatility events such as flash crashes or circuit breaker activations. 
    The order management component shall support multiple order types including market, 
    limit, stop-loss, and algorithmic orders with complex conditional logic based on 
    technical indicators, volume-weighted average price calculations, and time-based 
    execution strategies. Furthermore, the system must maintain complete audit trails 
    for regulatory compliance, recording every order modification, cancellation, and 
    execution with nanosecond precision timestamps synchronized to UTC via GPS or atomic 
    clock references. In case of system failures, the failover mechanism must activate 
    within 10 milliseconds, transferring all active orders and positions to backup systems 
    without any trade disruption or data inconsistency. The system shall also implement 
    advanced anti-money laundering detection by analyzing trading patterns for suspicious 
    activities such as layering, spoofing, or wash trading, automatically flagging 
    transactions that deviate from established behavioral models.
    """
    
    print("\n💰 Testing Complex Financial Trading System Requirements")
    print("=" * 70)
    print(f"Length: {len(requirement.split())} words")
    print(f"Sentences: {len(requirement.split('.'))}")
    
    analyzer = RequirementsAnalyzer()
    translator = EnglishToTauTranslator()
    
    # Extract requirements
    requirements = analyzer.extract_requirements(requirement)
    print(f"\n📊 Extracted {len(requirements)} requirements:")
    
    for i, req in enumerate(requirements, 1):
        print(f"  {i}. Type: {req.type.name}")
        print(f"     Length: {len(req.raw_text.split())} words")
        print(f"     Entities: {len(req.entities)} found")
        print(f"     Predicates: {len(req.predicates)} found")
        print(f"     Formal Constraints: {len(req.formal_constraints)}")
        print(f"     Confidence: {req.confidence:.2f}")
    
    # Test document-level translation
    doc_result = translator.translate_document(requirement)
    
    print(f"\n📄 Document Translation Results:")
    print(f"Individual translations: {len(doc_result.individual_translations)}")
    print(f"Overall confidence: {doc_result.overall_confidence:.2f}")
    
    print(f"\n📝 Sample Tau Specifications (first 3):")
    for i, trans in enumerate(doc_result.individual_translations[:3], 1):
        print(f"\n{i}. Source: {trans.source_text[:80]}...")
        print(f"   Tau: {trans.tau_specification[:100]}...")
        print(f"   Confidence: {trans.confidence.overall:.2f}")
    
    return doc_result

def test_complex_medical_device_requirements():
    """Test complex medical device requirements with safety-critical constraints"""
    
    requirement = """
    The implantable cardiac defibrillator control software must continuously monitor the 
    patient's heart rhythm using a dual-chamber sensing algorithm that analyzes R-wave 
    morphology, RR interval variability, and atrial-ventricular conduction patterns with 
    a sampling rate of at least 1000 Hz and signal processing accuracy of ±2 milliseconds. 
    When ventricular tachycardia is detected based on heart rate exceeding 180 beats per 
    minute for more than 8 consecutive beats, or when ventricular fibrillation is identified 
    through frequency domain analysis showing dominant frequencies above 250 Hz with 
    amplitude irregularity exceeding 40% baseline variation, the device shall automatically 
    initiate appropriate therapy within 6 seconds of arrhythmia onset. The shock therapy 
    algorithm must calculate optimal energy levels between 5 and 40 joules based on patient-
    specific impedance measurements, previous therapy effectiveness, and current arrhythmia 
    characteristics, ensuring that energy delivery never exceeds safe limits that could 
    cause myocardial damage or device malfunction. Battery management is critical, as the 
    system must operate continuously for a minimum of 7 years under normal usage patterns, 
    providing low-battery warnings at least 3 months before reaching end-of-life, and 
    entering safe mode with basic monitoring capabilities even when battery capacity falls 
    below 10%. All diagnostic data including electrograms, therapy episodes, and system 
    status must be stored with timestamp accuracy and transmitted securely to external 
    monitoring systems using encryption standards compliant with HIPAA and FDA regulations. 
    The device software must undergo formal verification using model checking techniques 
    to prove absence of deadlocks, race conditions, and timing violations that could 
    compromise patient safety or device reliability.
    """
    
    print("\n⚕️ Testing Complex Medical Device Requirements")
    print("=" * 70)
    print(f"Length: {len(requirement.split())} words")
    print(f"Sentences: {len(requirement.split('.'))}")
    
    analyzer = RequirementsAnalyzer()
    translator = EnglishToTauTranslator()
    
    # Test requirements extraction
    requirements = analyzer.extract_requirements(requirement)
    
    print(f"\n📊 Requirements Analysis:")
    
    # Analyze requirement types
    type_counts = {}
    total_entities = set()
    total_predicates = set()
    total_confidence = 0
    
    for req in requirements:
        req_type = req.type.name
        type_counts[req_type] = type_counts.get(req_type, 0) + 1
        total_entities.update(req.entities)
        total_predicates.update(req.predicates)
        total_confidence += req.confidence
    
    print(f"  Total requirements extracted: {len(requirements)}")
    print(f"  Requirement types: {type_counts}")
    print(f"  Unique entities found: {len(total_entities)}")
    print(f"  Unique predicates found: {len(total_predicates)}")
    print(f"  Average confidence: {total_confidence/len(requirements):.2f}")
    
    # Test semantic analysis
    semantic_analysis = translator.analyze_semantics(requirement)
    print(f"\n🧠 Semantic Analysis:")
    print(f"  Predicates: {len(semantic_analysis.predicates)} ({semantic_analysis.predicates[:10]}...)")
    print(f"  Entities: {len(semantic_analysis.entities)} ({semantic_analysis.entities[:10]}...)")
    print(f"  Quantifiers: {semantic_analysis.quantifiers}")
    print(f"  Logical operators: {semantic_analysis.logical_operators}")
    print(f"  Temporal expressions: {semantic_analysis.temporal_expressions}")
    
    # Test translation
    result = translator.translate(requirement)
    
    print(f"\n📝 Translation Assessment:")
    print(f"  Overall confidence: {result.confidence.overall:.2f}")
    print(f"  Syntax confidence: {result.confidence.syntax:.2f}")
    print(f"  Semantic confidence: {result.confidence.semantics:.2f}")
    print(f"  Logic confidence: {result.confidence.logical_structure:.2f}")
    print(f"  Math confidence: {result.confidence.mathematical:.2f}")
    
    if result.confidence.issues:
        print(f"  Issues identified: {result.confidence.issues}")
    
    print(f"\n📋 Translation Notes:")
    for note in result.translation_notes:
        print(f"  • {note}")
    
    return result

def test_system_scalability_challenges():
    """Test how the system handles increasingly complex requirements"""
    
    print("\n🎯 Testing System Scalability Challenges")
    print("=" * 70)
    
    # Progressive complexity test
    simple_req = "The system must validate user input."
    
    medium_req = """
    The user authentication system must validate credentials using multi-factor 
    authentication, including password verification and biometric confirmation, 
    before granting access to sensitive data.
    """
    
    complex_req = """
    The distributed microservices architecture must implement circuit breaker patterns 
    with exponential backoff retry mechanisms, ensuring that when any downstream service 
    becomes unavailable or responds with latency exceeding 500 milliseconds, the calling 
    service automatically switches to cached responses or degraded functionality mode 
    while continuously monitoring service health through heartbeat mechanisms and 
    automatically restoring full functionality when services recover and demonstrate 
    stable performance for at least 60 seconds.
    """
    
    requirements = [
        ("Simple (12 words)", simple_req),
        ("Medium (34 words)", medium_req), 
        ("Complex (89 words)", complex_req)
    ]
    
    translator = EnglishToTauTranslator()
    
    for label, req_text in requirements:
        print(f"\n📊 {label}:")
        
        result = translator.translate(req_text)
        
        print(f"  Confidence: {result.confidence.overall:.2f}")
        print(f"  Tau length: {len(result.tau_specification)} chars")
        print(f"  Issues: {len(result.confidence.issues)}")
        print(f"  Predicates found: {len(result.semantic_analysis.predicates)}")
        print(f"  Entities found: {len(result.semantic_analysis.entities)}")
        
        # Show quality degradation
        if result.confidence.overall < 0.5:
            print("  ⚠️  Low confidence - system struggling with complexity")
        elif result.confidence.overall < 0.7:
            print("  📉 Moderate confidence - some information may be lost")
        else:
            print("  ✅ Good confidence - translation appears reliable")

def analyze_failure_patterns():
    """Analyze common failure patterns to guide TDD improvements"""
    
    print("\n🔍 Analyzing Failure Patterns for TDD Guidance")
    print("=" * 70)
    
    # Test specific challenging patterns
    challenging_patterns = [
        {
            "pattern": "Nested conditionals",
            "text": "If the user is authenticated and (has admin role or belongs to special group), then grant access, otherwise if guest access is enabled, provide limited functionality, else deny completely."
        },
        {
            "pattern": "Temporal sequences", 
            "text": "After receiving the request, validate within 100ms, then process for up to 5 seconds, subsequently cache results for 1 hour, and finally log completion status."
        },
        {
            "pattern": "Quantified constraints",
            "text": "For every transaction above $10,000, all approvers in the chain must digitally sign within their respective authority limits before processing."
        },
        {
            "pattern": "Exception handling",
            "text": "Under normal conditions apply standard validation, however during system maintenance bypass certain checks, except for security validations which must always execute regardless of system state."
        },
        {
            "pattern": "Mathematical relationships",
            "text": "The load balancer must distribute traffic such that no server receives more than 1.5 times the average load across all active servers, unless server capacity differs by more than 20%."
        }
    ]
    
    translator = EnglishToTauTranslator()
    analyzer = RequirementsAnalyzer()
    
    failures = []
    
    for pattern_info in challenging_patterns:
        print(f"\n🧪 Testing: {pattern_info['pattern']}")
        
        result = translator.translate(pattern_info['text'])
        requirements = analyzer.extract_requirements(pattern_info['text'])
        
        confidence = result.confidence.overall
        issues = len(result.confidence.issues)
        req_count = len(requirements)
        
        print(f"  Confidence: {confidence:.2f}")
        print(f"  Issues: {issues}")
        print(f"  Requirements extracted: {req_count}")
        
        if confidence < 0.6 or issues > 2:
            failures.append({
                'pattern': pattern_info['pattern'],
                'confidence': confidence,
                'issues': result.confidence.issues,
                'text': pattern_info['text']
            })
            print("  ❌ FAILURE - needs improvement")
        else:
            print("  ✅ PASS - acceptable quality")
    
    print(f"\n📈 Failure Analysis Summary:")
    print(f"  Patterns tested: {len(challenging_patterns)}")
    print(f"  Patterns failed: {len(failures)}")
    print(f"  Success rate: {((len(challenging_patterns) - len(failures)) / len(challenging_patterns) * 100):.1f}%")
    
    if failures:
        print(f"\n🎯 Areas needing TDD improvements:")
        for failure in failures:
            print(f"  • {failure['pattern']}: {failure['confidence']:.2f} confidence")
            for issue in failure['issues']:
                print(f"    - {issue}")
    
    return failures

def main():
    """Run all complex requirement tests"""
    print("🚀 Complex Multi-Sentence Requirements Testing")
    print("🧪 This is TDD Red Phase - expect failures that drive improvements!\n")
    
    try:
        test_complex_cryptographic_system()
        print("\n" + "="*70)
        
        test_complex_financial_trading_system() 
        print("\n" + "="*70)
        
        test_complex_medical_device_requirements()
        print("\n" + "="*70)
        
        test_system_scalability_challenges()
        print("\n" + "="*70)
        
        failures = analyze_failure_patterns()
        
        print(f"\n🎯 TDD Guidance Summary:")
        print(f"These tests reveal areas for improvement:")
        print(f"1. Multi-sentence context correlation")
        print(f"2. Complex temporal logic handling") 
        print(f"3. Nested conditional processing")
        print(f"4. Domain-specific vocabulary expansion")
        print(f"5. Cross-reference resolution")
        
        if failures:
            print(f"\n📋 Next TDD Iteration Should Address:")
            for failure in failures:
                print(f"• {failure['pattern']}")
        
    except Exception as e:
        print(f"❌ System failure during complex testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()