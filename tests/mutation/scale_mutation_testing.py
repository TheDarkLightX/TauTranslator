#!/usr/bin/env python3
"""
Scaled Mutation Testing for TauTranslator Core Modules
=====================================================

Runs mutation testing across all working test modules to assess 
project-wide test quality following VibeArchitect principles.
"""

import os
import sys
import subprocess
import time
import json
import tempfile
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

class MutationTestRunner:
    """Handles mutation testing for multiple modules."""
    
    def __init__(self):
        self.base_dir = '~/TauTranslator'
        self.src_dir = f'{self.base_dir}/src'
        
        # Mapping of test modules to their corresponding source files
        self.test_module_mapping = {
            'tests/core_engine/ast_tests/test_boolean_literal_node_fixed.py': {
                'source': 'src/tau_translator_omega/core_engine/ast/ast_nodes.py',
                'description': 'Boolean Literal Node (Enhanced)',
                'expected_score': 85.0,  # Based on our previous testing
                'timeout': 120
            },
            'tests/core_engine/ast_tests/test_identifier_node.py': {
                'source': 'src/tau_translator_omega/core_engine/ast/ast_nodes.py',
                'description': 'Identifier Node (Original)',
                'expected_score': 75.0,
                'timeout': 120
            },
            'tests/core_engine/ast_tests/test_binary_op_node.py': {
                'source': 'src/tau_translator_omega/core_engine/ast/ast_nodes.py',
                'description': 'Binary Op Node (Original)',
                'expected_score': 70.0,
                'timeout': 120
            },
            'tests/core_engine/ast_tests/test_number_literal_node.py': {
                'source': 'src/tau_translator_omega/core_engine/ast/ast_nodes.py',
                'description': 'Number Literal Node (Original)',
                'expected_score': 70.0,
                'timeout': 120
            },
            'tests/core_engine/test_semantic_analyzer_refactored.py': {
                'source': 'src/tau_translator_omega/core_engine/semantic_analyzer.py',
                'description': 'Semantic Analyzer (Refactored)',
                'expected_score': 60.0,  # More complex module
                'timeout': 180
            },
            'tests/core_engine/ast_tests/test_boolean_literal_node_mutation_hardened.py': {
                'source': 'src/tau_translator_omega/core_engine/ast/ast_nodes.py',
                'description': 'Boolean Literal Node (Hardened)',
                'expected_score': 85.0,  # Hardened version should be high
                'timeout': 120
            },
            'tests/core_engine/cnl_parser/test_mock_parser.py': {
                'source': 'src/tau_translator_omega/core_engine/cnl_parser/mock_parser.py',
                'description': 'Mock CNL Parser',
                'expected_score': 70.0,
                'timeout': 150
            },
            'tests/core_engine/ebnf_parser/test_ebnf_parser.py': {
                'source': 'src/tau_translator_omega/core_engine/ebnf_parser/ebnf_parser.py',
                'description': 'EBNF Parser',
                'expected_score': 65.0,  # Complex parser
                'timeout': 180
            }
        }

    def create_mutmut_config(self, source_file, test_file):
        """Create a temporary mutmut config for the given source/test pair."""
        config_content = f"""[mutmut]
paths_to_mutate = {source_file}
backup = False
runner = PYTHONPATH={self.src_dir} python3 -m pytest {test_file} -x --tb=no --disable-warnings -q
tests_dir = tests/
"""
        return config_content

    def run_mutation_test(self, test_file, config):
        """Run mutation testing for a single test module."""
        print(f"🧬 Starting mutation testing: {config['description']}")
        
        start_time = time.time()
        
        # Create temporary config file
        config_content = self.create_mutmut_config(config['source'], test_file)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cfg', delete=False) as f:
            f.write(config_content)
            config_file = f.name
        
        try:
            # Set environment for mutmut
            env = os.environ.copy()
            env['MUTMUT_CONFIG_FILE'] = config_file
            
            # Run mutmut
            print(f"   Running mutmut on {config['source']}...")
            
            mutmut_result = subprocess.run([
                sys.executable, '-m', 'mutmut', 'run'
            ], 
            cwd=self.base_dir,
            env=env,
            capture_output=True, 
            text=True,
            timeout=config.get('timeout', 120)
            )
            
            # Get results
            results_result = subprocess.run([
                sys.executable, '-m', 'mutmut', 'results'
            ], 
            cwd=self.base_dir,
            env=env,
            capture_output=True, 
            text=True,
            timeout=30
            )
            
            # Parse results
            mutation_score = self.parse_mutation_score(results_result.stdout)
            
            test_time = time.time() - start_time
            
            result = {
                'test_file': test_file,
                'source_file': config['source'],
                'description': config['description'],
                'mutation_score': mutation_score,
                'expected_score': config['expected_score'],
                'test_time': test_time,
                'status': 'SUCCESS' if mutation_score is not None else 'FAILED',
                'mutmut_output': mutmut_result.stdout + mutmut_result.stderr,
                'results_output': results_result.stdout,
                'meets_expectation': mutation_score >= config['expected_score'] if mutation_score else False
            }
            
            # Clean up mutmut cache
            try:
                subprocess.run([sys.executable, '-m', 'mutmut', 'reset'], 
                             cwd=self.base_dir, env=env, capture_output=True, timeout=30)
            except:
                pass
            
            return result
            
        except subprocess.TimeoutExpired:
            return {
                'test_file': test_file,
                'source_file': config['source'],
                'description': config['description'],
                'mutation_score': None,
                'expected_score': config['expected_score'],
                'test_time': time.time() - start_time,
                'status': 'TIMEOUT',
                'mutmut_output': 'Test timed out',
                'results_output': '',
                'meets_expectation': False
            }
            
        except Exception as e:
            return {
                'test_file': test_file,
                'source_file': config['source'],
                'description': config['description'],
                'mutation_score': None,
                'expected_score': config['expected_score'],
                'test_time': time.time() - start_time,
                'status': 'ERROR',
                'mutmut_output': str(e),
                'results_output': '',
                'meets_expectation': False
            }
            
        finally:
            # Clean up config file
            try:
                os.unlink(config_file)
            except:
                pass

    def parse_mutation_score(self, results_output):
        """Parse mutation score from mutmut results output."""
        if not results_output:
            return None
            
        lines = results_output.split('\n')
        for line in lines:
            if 'mutants' in line.lower() and '%' in line:
                # Look for patterns like "mutation score: 85.7%"
                import re
                score_match = re.search(r'(\d+\.?\d*)%', line)
                if score_match:
                    return float(score_match.group(1))
                    
        # Alternative parsing - look for summary statistics
        for line in lines:
            if 'killed' in line.lower() and 'survived' in line.lower():
                # Parse killed/survived counts
                killed_match = re.search(r'(\d+)\s*killed', line, re.IGNORECASE)
                survived_match = re.search(r'(\d+)\s*survived', line, re.IGNORECASE)
                if killed_match and survived_match:
                    killed = int(killed_match.group(1))
                    survived = int(survived_match.group(1))
                    total = killed + survived
                    if total > 0:
                        return (killed / total) * 100
        
        return None

    def run_all_mutation_tests(self, max_workers=2):
        """Run mutation testing on all configured modules."""
        print("🧬 SCALED MUTATION TESTING FOR TAUTRANSLATOR")
        print("=" * 60)
        print(f"Testing {len(self.test_module_mapping)} modules with up to {max_workers} parallel workers")
        print()
        
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tests
            future_to_test = {
                executor.submit(self.run_mutation_test, test_file, config): (test_file, config)
                for test_file, config in self.test_module_mapping.items()
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_test):
                test_file, config = future_to_test[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    # Print immediate feedback
                    score = result['mutation_score']
                    expected = result['expected_score']
                    
                    if result['status'] == 'SUCCESS' and score is not None:
                        if score >= expected:
                            status_emoji = "✅"
                            status_text = f"PASS ({score:.1f}% ≥ {expected:.1f}%)"
                        else:
                            status_emoji = "⚠️"
                            status_text = f"BELOW TARGET ({score:.1f}% < {expected:.1f}%)"
                    else:
                        status_emoji = "❌"
                        status_text = f"FAILED ({result['status']})"
                    
                    print(f"{status_emoji} {config['description']}")
                    print(f"   Score: {status_text}")
                    print(f"   Time: {result['test_time']:.1f}s")
                    print()
                    
                except Exception as e:
                    error_result = {
                        'test_file': test_file,
                        'description': config['description'],
                        'mutation_score': None,
                        'status': 'EXCEPTION',
                        'test_time': 0,
                        'mutmut_output': str(e),
                        'meets_expectation': False
                    }
                    results.append(error_result)
                    print(f"❌ {config['description']}: EXCEPTION - {str(e)[:100]}")
                    print()
        
        return results

    def generate_comprehensive_report(self, results):
        """Generate comprehensive mutation testing report."""
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE MUTATION TESTING REPORT")
        print("=" * 60)
        
        # Calculate summary statistics
        successful_tests = [r for r in results if r['status'] == 'SUCCESS' and r['mutation_score'] is not None]
        failed_tests = [r for r in results if r['status'] != 'SUCCESS' or r['mutation_score'] is None]
        meeting_expectations = [r for r in results if r.get('meets_expectation', False)]
        
        total_tests = len(results)
        success_count = len(successful_tests)
        failed_count = len(failed_tests)
        meeting_count = len(meeting_expectations)
        
        # Overall scores
        if successful_tests:
            avg_mutation_score = sum(r['mutation_score'] for r in successful_tests) / len(successful_tests)
            max_mutation_score = max(r['mutation_score'] for r in successful_tests)
            min_mutation_score = min(r['mutation_score'] for r in successful_tests)
        else:
            avg_mutation_score = 0
            max_mutation_score = 0
            min_mutation_score = 0
        
        total_test_time = sum(r['test_time'] for r in results)
        
        print(f"📈 OVERALL STATISTICS:")
        print(f"   • Total Modules Tested: {total_tests}")
        print(f"   • Successful Tests: {success_count}/{total_tests} ({success_count/total_tests*100:.1f}%)")
        print(f"   • Meeting Expectations: {meeting_count}/{total_tests} ({meeting_count/total_tests*100:.1f}%)")
        print(f"   • Average Mutation Score: {avg_mutation_score:.1f}%")
        print(f"   • Best Mutation Score: {max_mutation_score:.1f}%")
        print(f"   • Worst Mutation Score: {min_mutation_score:.1f}%")
        print(f"   • Total Testing Time: {total_test_time:.1f} seconds")
        print()
        
        if successful_tests:
            print("✅ SUCCESSFUL MUTATION TESTS:")
            for result in sorted(successful_tests, key=lambda x: x['mutation_score'], reverse=True):
                score = result['mutation_score']
                expected = result['expected_score']
                meets = "✅" if score >= expected else "⚠️"
                print(f"   {meets} {result['description']}")
                print(f"      Score: {score:.1f}% (target: {expected:.1f}%)")
                print(f"      File: {result['source_file']}")
                print(f"      Time: {result['test_time']:.1f}s")
                print()
        
        if failed_tests:
            print("❌ FAILED MUTATION TESTS:")
            for result in failed_tests:
                print(f"   • {result['description']}")
                print(f"     Status: {result['status']}")
                print(f"     Error: {result['mutmut_output'][:100]}...")
                print()
        
        # Quality assessment
        print("🎯 PROJECT-WIDE QUALITY ASSESSMENT:")
        
        if avg_mutation_score >= 80 and meeting_count >= total_tests * 0.8:
            quality_level = "EXCELLENT"
            quality_emoji = "🟢"
            quality_desc = "Project meets VibeArchitect standards"
        elif avg_mutation_score >= 70 and meeting_count >= total_tests * 0.6:
            quality_level = "GOOD"
            quality_emoji = "🟡"
            quality_desc = "Project approaching VibeArchitect standards"
        elif avg_mutation_score >= 60:
            quality_level = "ACCEPTABLE"
            quality_emoji = "🟠"
            quality_desc = "Project needs improvement to meet standards"
        else:
            quality_level = "NEEDS WORK"
            quality_emoji = "🔴"
            quality_desc = "Major improvements needed"
        
        print(f"   {quality_emoji} Overall Quality: {quality_level}")
        print(f"   {quality_desc}")
        print(f"   Average Score: {avg_mutation_score:.1f}%")
        print()
        
        # Recommendations
        print("💡 RECOMMENDATIONS:")
        
        if quality_level == "EXCELLENT":
            print("   🏆 Excellent test quality! Ready for production deployment")
            print("   📈 Consider increasing mutation testing coverage to more modules")
        elif quality_level == "GOOD":
            print("   ✨ Good test quality - focus on improving weaker modules")
            print("   🎯 Target 80%+ mutation scores across all modules")
        else:
            print("   🔧 Improve test assertions and add property-based testing")
            print("   🧪 Add boundary value analysis and error scenario testing")
            print("   ⚡ Implement performance constraints in tests")
        
        if successful_tests:
            best_module = max(successful_tests, key=lambda x: x['mutation_score'])
            print(f"   🌟 Use '{best_module['description']}' ({best_module['mutation_score']:.1f}%) as template for other modules")
        
        return {
            'total_tests': total_tests,
            'successful_tests': success_count,
            'failed_tests': failed_count,
            'meeting_expectations': meeting_count,
            'avg_mutation_score': avg_mutation_score,
            'max_mutation_score': max_mutation_score,
            'min_mutation_score': min_mutation_score,
            'quality_level': quality_level,
            'total_time': total_test_time,
            'results': results
        }

def main():
    """Main execution function."""
    os.chdir('~/TauTranslator')
    
    runner = MutationTestRunner()
    
    print("⚡ Starting scaled mutation testing (this may take several minutes)...")
    print()
    
    # Run all mutation tests
    results = runner.run_all_mutation_tests(max_workers=2)
    
    # Generate comprehensive report
    summary = runner.generate_comprehensive_report(results)
    
    # Save detailed results
    timestamp = int(time.time())
    report_file = f'scaled_mutation_testing_report_{timestamp}.json'
    
    with open(report_file, 'w') as f:
        json.dump({
            'timestamp': time.time(),
            'summary': summary,
            'detailed_results': results
        }, f, indent=2)
    
    print(f"📁 Detailed report saved to: {report_file}")
    
    # Return success if average score meets minimum threshold
    return summary['avg_mutation_score'] >= 60

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)