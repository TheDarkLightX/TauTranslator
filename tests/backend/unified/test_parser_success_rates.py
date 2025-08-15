"""
Comprehensive Parser Success Rate Tests
Tests all parser implementations against various complexity levels.

Copyright: DarkLightX / Dana Edwards
"""

import sys
import time
from typing import List, Dict, Tuple, Any
from dataclasses import dataclass
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from tce_parser_v1_01 import TCEParserV101
    from tce_parser_v1_51 import TCEParserV151  
    from tce_parser_semantic import TCEParserSemanticV2
    print("✅ Successfully imported basic parsers")
except ImportError as e:
    print(f"❌ Import error for basic parsers: {e}")
    # Create mock parsers for testing
    class MockParser:
        def parse(self, text): return f"mock_parse({text})"
    
    TCEParserV101 = MockParser
    TCEParserV151 = MockParser
    TCEParserSemanticV2 = MockParser


@dataclass
class TestCase:
    """Test case for parser evaluation."""
    sentence: str
    expected_type: str
    complexity: str
    description: str


@dataclass
class ParserResult:
    """Result from parser test."""
    success: bool
    output: str
    time_ms: float
    error: str = ""


@dataclass
class TestResults:
    """Comprehensive test results."""
    parser_name: str
    total_tests: int
    successful: int
    failed: int
    success_rate: float
    avg_time_ms: float
    complexity_breakdown: Dict[str, float]


# === TEST CASES ===

def create_test_cases() -> List[TestCase]:
    """Create comprehensive test cases."""
    return [
        # Simple quantified statements
        TestCase("all people are happy", "quantified", "simple", "Basic universal quantifier"),
        TestCase("every car is red", "quantified", "simple", "Universal with property"),
        TestCase("some customers own cars", "quantified", "simple", "Existential quantifier"),
        
        # Temporal statements
        TestCase("when customers purchase items, they receive receipts", "temporal", "medium", "Basic temporal logic"),
        TestCase("while systems process requests, users wait", "temporal", "medium", "Concurrent temporal"),
        TestCase("after payments complete, orders ship", "temporal", "medium", "Sequential temporal"),
        
        # Modal statements
        TestCase("customers must pay before ordering", "modal", "medium", "Necessity modal"),
        TestCase("users can modify their profiles", "modal", "simple", "Possibility modal"),
        TestCase("systems should validate all inputs", "modal", "medium", "Recommendation modal"),
        
        # Complex quantified
        TestCase("for every customer who owns a car, the customer must have insurance", "quantified", "complex", "Nested quantified with condition"),
        TestCase("all employees who work remotely need laptop access", "quantified", "complex", "Complex conditional quantifier"),
        TestCase("most systems that process payments require encryption", "quantified", "complex", "Fuzzy quantifier with condition"),
        
        # Causal relationships
        TestCase("system failures cause user complaints", "causal", "medium", "Simple causation"),
        TestCase("poor performance leads to customer dissatisfaction", "causal", "medium", "Complex causation"),
        TestCase("security breaches result in data loss", "causal", "medium", "Direct consequence"),
        
        # Complex temporal
        TestCase("when users log in during peak hours, while systems are under load, response times increase", "temporal", "complex", "Nested temporal conditions"),
        TestCase("before customers can purchase items, after they create accounts, they must verify emails", "temporal", "complex", "Sequential temporal chain"),
        
        # Complex modal combinations
        TestCase("all users who must authenticate should provide valid credentials and may use two-factor authentication", "modal", "complex", "Mixed modal requirements"),
        TestCase("systems that can process payments must validate transactions and should log all activities", "modal", "complex", "Nested modal obligations"),
        
        # Edge cases and challenging sentences
        TestCase("the red car that belongs to customers who live in cities must be insured", "complex", "complex", "Multiple nested clauses"),
        TestCase("whenever systems experience high load during business hours, administrators should monitor performance metrics", "complex", "complex", "Complex temporal-modal combination"),
        TestCase("all customers whose accounts have been verified and who have made purchases can access premium features", "complex", "complex", "Multiple conditions with conjunction"),
        
        # Semantic consistency tests
        TestCase("cars think about philosophy", "invalid", "simple", "Semantic inconsistency - inanimate subject"),
        TestCase("books drive to the store", "invalid", "simple", "Semantic inconsistency - impossible action"),
        TestCase("houses sleep peacefully", "invalid", "simple", "Semantic inconsistency - anthropomorphism"),
        
        # Boundary cases
        TestCase("", "empty", "simple", "Empty input"),
        TestCase("a", "minimal", "simple", "Single word"),
        TestCase("this is a very long sentence with many words that tests the parser's ability to handle complex grammatical structures and nested clauses", "complex", "complex", "Very long sentence"),
    ]


# === PARSER TESTING FUNCTIONS ===

def test_single_parser(parser, parser_name: str, test_cases: List[TestCase]) -> TestResults:
    """Test single parser against all test cases."""
    results = []
    
    print(f"\n🔍 Testing {parser_name}...")
    
    for i, test_case in enumerate(test_cases):
        print(f"  [{i+1:2d}/{len(test_cases)}] {test_case.sentence[:50]}{'...' if len(test_case.sentence) > 50 else ''}")
        
        result = run_single_test(parser, parser_name, test_case)
        results.append(result)
    
    return calculate_test_results(parser_name, test_cases, results)


def run_single_test(parser, parser_name: str, test_case: TestCase) -> ParserResult:
    """Run single test case."""
    try:
        start_time = time.time()
        
        # Call appropriate parse method based on parser type
        if hasattr(parser, 'parse'):
            if parser_name == "EnhancedParser":
                # Enhanced parser returns EnhancedParseResult
                parse_result = parser.parse(test_case.sentence)
                output = parse_result.parsed_text
                success = parse_result.confidence > 0.3
            elif parser_name in ["GradientDescentParser", "HybridParser"]:
                # Plugin parsers need context
                context = ParseContext(original_text=test_case.sentence, preprocessed_text=test_case.sentence)
                result = parser.process(test_case.sentence, context)
                if hasattr(result, 'unwrap'):
                    output = result.unwrap() if result.is_success() else str(result.failure())
                    success = result.is_success()
                else:
                    output = str(result)
                    success = "error" not in output.lower()
            else:
                # Regular parsers
                output = parser.parse(test_case.sentence)
                success = output != test_case.sentence and len(output) > 0
        else:
            output = "Parser has no parse method"
            success = False
        
        end_time = time.time()
        time_ms = (end_time - start_time) * 1000
        
        return ParserResult(
            success=success,
            output=output,
            time_ms=time_ms
        )
        
    except Exception as e:
        return ParserResult(
            success=False,
            output="",
            time_ms=0.0,
            error=str(e)
        )


def calculate_test_results(parser_name: str, test_cases: List[TestCase], results: List[ParserResult]) -> TestResults:
    """Calculate comprehensive test results."""
    successful = sum(1 for r in results if r.success)
    failed = len(results) - successful
    success_rate = (successful / len(results)) * 100 if results else 0.0
    avg_time = sum(r.time_ms for r in results) / len(results) if results else 0.0
    
    # Calculate complexity breakdown
    complexity_breakdown = {}
    complexity_groups = {}
    
    for test_case, result in zip(test_cases, results):
        complexity = test_case.complexity
        if complexity not in complexity_groups:
            complexity_groups[complexity] = {'total': 0, 'successful': 0}
        
        complexity_groups[complexity]['total'] += 1
        if result.success:
            complexity_groups[complexity]['successful'] += 1
    
    for complexity, stats in complexity_groups.items():
        complexity_breakdown[complexity] = (stats['successful'] / stats['total']) * 100
    
    return TestResults(
        parser_name=parser_name,
        total_tests=len(results),
        successful=successful,
        failed=failed,
        success_rate=success_rate,
        avg_time_ms=avg_time,
        complexity_breakdown=complexity_breakdown
    )


# === RESULTS REPORTING ===

def print_detailed_results(all_results: List[TestResults]):
    """Print detailed test results."""
    print("\n" + "="*80)
    print("🎯 COMPREHENSIVE PARSER SUCCESS RATE ANALYSIS")
    print("="*80)
    
    # Overall results table
    print(f"\n📊 OVERALL RESULTS")
    print("-" * 80)
    print(f"{'Parser':<20} {'Success Rate':<12} {'Successful':<10} {'Failed':<8} {'Avg Time (ms)':<12}")
    print("-" * 80)
    
    for result in sorted(all_results, key=lambda x: x.success_rate, reverse=True):
        print(f"{result.parser_name:<20} {result.success_rate:>8.1f}%    {result.successful:>6d}     {result.failed:>4d}     {result.avg_time_ms:>8.2f}")
    
    # Complexity breakdown
    print(f"\n🔬 SUCCESS RATE BY COMPLEXITY")
    print("-" * 80)
    
    complexities = ['simple', 'medium', 'complex']
    
    print(f"{'Parser':<20}", end="")
    for complexity in complexities:
        print(f"{complexity.capitalize():<10}", end="")
    print()
    print("-" * 80)
    
    for result in all_results:
        print(f"{result.parser_name:<20}", end="")
        for complexity in complexities:
            rate = result.complexity_breakdown.get(complexity, 0.0)
            print(f"{rate:>6.1f}%   ", end="")
        print()
    
    # Winner analysis
    print(f"\n🏆 WINNER ANALYSIS")
    print("-" * 80)
    
    best_overall = max(all_results, key=lambda x: x.success_rate)
    fastest = min(all_results, key=lambda x: x.avg_time_ms)
    
    print(f"🥇 Best Overall Success Rate: {best_overall.parser_name} ({best_overall.success_rate:.1f}%)")
    print(f"⚡ Fastest Parser: {fastest.parser_name} ({fastest.avg_time_ms:.2f}ms avg)")
    
    # Complex sentence champions
    complex_rates = {r.parser_name: r.complexity_breakdown.get('complex', 0.0) for r in all_results}
    best_complex = max(complex_rates.items(), key=lambda x: x[1])
    print(f"🧠 Best at Complex Sentences: {best_complex[0]} ({best_complex[1]:.1f}%)")


def run_comprehensive_tests():
    """Run comprehensive parser tests."""
    print("🚀 Starting Comprehensive Parser Success Rate Tests")
    print("="*60)
    
    # Create test cases
    test_cases = create_test_cases()
    print(f"📝 Created {len(test_cases)} test cases")
    
    # Initialize all parsers
    parsers = {
        "MinimalParser": TCEParserV101(),
        "ExtensibleParser": TCEParserV151(),
        "SemanticParser": TCEParserSemanticV2(),
        "EnhancedParser": create_enhanced_tce_parser(),
        "GradientDescentParser": create_gradient_descent_parser(),
        "HybridParser": create_hybrid_parser()
    }
    
    print(f"🔧 Initialized {len(parsers)} parsers")
    
    # Run tests for each parser
    all_results = []
    
    for parser_name, parser in parsers.items():
        try:
            results = test_single_parser(parser, parser_name, test_cases)
            all_results.append(results)
        except Exception as e:
            print(f"❌ Error testing {parser_name}: {e}")
            # Create dummy results
            all_results.append(TestResults(
                parser_name=parser_name,
                total_tests=len(test_cases),
                successful=0,
                failed=len(test_cases),
                success_rate=0.0,
                avg_time_ms=0.0,
                complexity_breakdown={}
            ))
    
    # Print comprehensive results
    print_detailed_results(all_results)
    
    return all_results


if __name__ == "__main__":
    run_comprehensive_tests()