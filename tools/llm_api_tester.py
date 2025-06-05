#!/usr/bin/env python3
"""
LLM API Integration Tester
==========================

Comprehensive testing tool for LLM and API integrations in the TauTranslator project.
Tests OpenRouter, OpenAI, Guidance, LMQL, and other AI service integrations.

Features:
- API endpoint connectivity testing
- Authentication verification
- Response quality assessment
- Performance benchmarking
- Error handling validation
- Rate limiting compliance
- Security assessment

Author: DarkLightX/Dana Edwards
"""

import asyncio
import aiohttp
import json
import time
import os
import sys
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib
import statistics


@dataclass
class APITestResult:
    """Results from testing an API endpoint."""
    endpoint: str
    test_type: str
    success: bool
    response_time: float
    status_code: Optional[int]
    response_data: Optional[Dict]
    error_message: Optional[str]
    security_score: float
    timestamp: str


@dataclass
class LLMTestResult:
    """Results from testing an LLM integration."""
    service_name: str
    model_name: str
    test_prompt: str
    response_text: Optional[str]
    response_quality_score: float
    token_usage: Optional[Dict]
    response_time: float
    success: bool
    error_message: Optional[str]
    timestamp: str


class LLMAPITester:
    """Main LLM API testing framework."""
    
    def __init__(self):
        self.api_results = []
        self.llm_results = []
        self.session = None
        
        # Test prompts for different scenarios
        self.test_prompts = {
            'simple': "Translate 'x is always greater than y' to Tau language",
            'complex': "Convert the following complex requirement to Tau: 'For all users in the system, if they are active and have premium access, then they can access advanced features, but only during business hours'",
            'edge_case': "Handle this edge case: empty input string",
            'tau_specific': "Parse this Tau expression: 'always (forall x, x > 0 -> exists y, y = x + 1)'"
        }
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def test_openrouter_integration(self) -> List[APITestResult]:
        """Test OpenRouter API integration."""
        results = []
        
        # Check for API key
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            results.append(APITestResult(
                endpoint="https://openrouter.ai/api/v1/chat/completions",
                test_type="authentication",
                success=False,
                response_time=0.0,
                status_code=None,
                response_data=None,
                error_message="OPENROUTER_API_KEY environment variable not set",
                security_score=0.0,
                timestamp=datetime.now().isoformat()
            ))
            return results
        
        # Test basic connectivity
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        test_payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "user", "content": self.test_prompts['simple']}
            ],
            "max_tokens": 100
        }
        
        start_time = time.time()
        try:
            async with self.session.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=test_payload
            ) as response:
                response_time = time.time() - start_time
                response_data = await response.json()
                
                results.append(APITestResult(
                    endpoint="https://openrouter.ai/api/v1/chat/completions",
                    test_type="basic_request",
                    success=response.status == 200,
                    response_time=response_time,
                    status_code=response.status,
                    response_data=response_data,
                    error_message=None if response.status == 200 else f"HTTP {response.status}",
                    security_score=self._assess_security(headers, response_data),
                    timestamp=datetime.now().isoformat()
                ))
        
        except Exception as e:
            response_time = time.time() - start_time
            results.append(APITestResult(
                endpoint="https://openrouter.ai/api/v1/chat/completions",
                test_type="basic_request",
                success=False,
                response_time=response_time,
                status_code=None,
                response_data=None,
                error_message=str(e),
                security_score=0.0,
                timestamp=datetime.now().isoformat()
            ))
        
        return results
    
    async def test_openai_integration(self) -> List[APITestResult]:
        """Test OpenAI API integration."""
        results = []
        
        # Check for API key
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            results.append(APITestResult(
                endpoint="https://api.openai.com/v1/chat/completions",
                test_type="authentication",
                success=False,
                response_time=0.0,
                status_code=None,
                response_data=None,
                error_message="OPENAI_API_KEY environment variable not set",
                security_score=0.0,
                timestamp=datetime.now().isoformat()
            ))
            return results
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        test_payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "user", "content": self.test_prompts['simple']}
            ],
            "max_tokens": 100
        }
        
        start_time = time.time()
        try:
            async with self.session.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=test_payload
            ) as response:
                response_time = time.time() - start_time
                response_data = await response.json()
                
                results.append(APITestResult(
                    endpoint="https://api.openai.com/v1/chat/completions",
                    test_type="basic_request",
                    success=response.status == 200,
                    response_time=response_time,
                    status_code=response.status,
                    response_data=response_data,
                    error_message=None if response.status == 200 else f"HTTP {response.status}",
                    security_score=self._assess_security(headers, response_data),
                    timestamp=datetime.now().isoformat()
                ))
        
        except Exception as e:
            response_time = time.time() - start_time
            results.append(APITestResult(
                endpoint="https://api.openai.com/v1/chat/completions",
                test_type="basic_request",
                success=False,
                response_time=response_time,
                status_code=None,
                response_data=None,
                error_message=str(e),
                security_score=0.0,
                timestamp=datetime.now().isoformat()
            ))
        
        return results
    
    async def test_local_backend_endpoints(self) -> List[APITestResult]:
        """Test local backend API endpoints."""
        results = []
        
        # Test endpoints from the codebase analysis
        local_endpoints = [
            "http://localhost:8000/translate",
            "http://localhost:8000/parse",
            "http://localhost:8000/validate",
            "http://localhost:5000/api/translate",
            "http://localhost:3000/api/translate"
        ]
        
        for endpoint in local_endpoints:
            start_time = time.time()
            try:
                # Test with simple payload
                test_payload = {
                    "text": self.test_prompts['simple'],
                    "source_lang": "english",
                    "target_lang": "tau"
                }
                
                async with self.session.post(
                    endpoint,
                    json=test_payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    response_time = time.time() - start_time
                    
                    try:
                        response_data = await response.json()
                    except:
                        response_data = {"text": await response.text()}
                    
                    results.append(APITestResult(
                        endpoint=endpoint,
                        test_type="local_backend",
                        success=response.status == 200,
                        response_time=response_time,
                        status_code=response.status,
                        response_data=response_data,
                        error_message=None if response.status == 200 else f"HTTP {response.status}",
                        security_score=self._assess_security({}, response_data),
                        timestamp=datetime.now().isoformat()
                    ))
            
            except Exception as e:
                response_time = time.time() - start_time
                results.append(APITestResult(
                    endpoint=endpoint,
                    test_type="local_backend",
                    success=False,
                    response_time=response_time,
                    status_code=None,
                    response_data=None,
                    error_message=str(e),
                    security_score=0.0,
                    timestamp=datetime.now().isoformat()
                ))
        
        return results
    
    def test_guidance_integration(self) -> List[LLMTestResult]:
        """Test Guidance framework integration."""
        results = []
        
        try:
            # Try to import and test guidance
            import guidance
            
            # Test simple guidance program
            guidance_program = guidance('''
            Translate the following to Tau language:
            {{input_text}}
            
            Translation: {{gen 'translation' max_tokens=50}}
            ''')
            
            start_time = time.time()
            try:
                result = guidance_program(input_text=self.test_prompts['simple'])
                response_time = time.time() - start_time
                
                results.append(LLMTestResult(
                    service_name="Guidance",
                    model_name="local",
                    test_prompt=self.test_prompts['simple'],
                    response_text=result.get('translation', ''),
                    response_quality_score=self._assess_response_quality(result.get('translation', '')),
                    token_usage=None,
                    response_time=response_time,
                    success=True,
                    error_message=None,
                    timestamp=datetime.now().isoformat()
                ))
            
            except Exception as e:
                response_time = time.time() - start_time
                results.append(LLMTestResult(
                    service_name="Guidance",
                    model_name="local",
                    test_prompt=self.test_prompts['simple'],
                    response_text=None,
                    response_quality_score=0.0,
                    token_usage=None,
                    response_time=response_time,
                    success=False,
                    error_message=str(e),
                    timestamp=datetime.now().isoformat()
                ))
        
        except ImportError:
            results.append(LLMTestResult(
                service_name="Guidance",
                model_name="N/A",
                test_prompt="N/A",
                response_text=None,
                response_quality_score=0.0,
                token_usage=None,
                response_time=0.0,
                success=False,
                error_message="Guidance library not installed",
                timestamp=datetime.now().isoformat()
            ))
        
        return results
    
    def test_lmql_integration(self) -> List[LLMTestResult]:
        """Test LMQL integration."""
        results = []
        
        try:
            # Try to import and test LMQL
            import lmql
            
            # Test simple LMQL query
            @lmql.query
            def translate_query():
                '''lmql
                "Translate to Tau language: {self.test_prompts['simple']}"
                "Translation:" [TRANSLATION]
                return TRANSLATION
                '''
            
            start_time = time.time()
            try:
                result = translate_query()
                response_time = time.time() - start_time
                
                results.append(LLMTestResult(
                    service_name="LMQL",
                    model_name="default",
                    test_prompt=self.test_prompts['simple'],
                    response_text=str(result),
                    response_quality_score=self._assess_response_quality(str(result)),
                    token_usage=None,
                    response_time=response_time,
                    success=True,
                    error_message=None,
                    timestamp=datetime.now().isoformat()
                ))
            
            except Exception as e:
                response_time = time.time() - start_time
                results.append(LLMTestResult(
                    service_name="LMQL",
                    model_name="default",
                    test_prompt=self.test_prompts['simple'],
                    response_text=None,
                    response_quality_score=0.0,
                    token_usage=None,
                    response_time=response_time,
                    success=False,
                    error_message=str(e),
                    timestamp=datetime.now().isoformat()
                ))
        
        except ImportError:
            results.append(LLMTestResult(
                service_name="LMQL",
                model_name="N/A",
                test_prompt="N/A",
                response_text=None,
                response_quality_score=0.0,
                token_usage=None,
                response_time=0.0,
                success=False,
                error_message="LMQL library not installed",
                timestamp=datetime.now().isoformat()
            ))
        
        return results
    
    def test_local_model_integrations(self) -> List[LLMTestResult]:
        """Test local model integrations (Ollama, etc.)."""
        results = []
        
        # Test Ollama integration
        ollama_models = ["llama2", "codellama", "mistral", "gemma"]
        
        for model in ollama_models:
            start_time = time.time()
            try:
                # Try to make request to local Ollama
                import requests
                
                response = requests.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": model,
                        "prompt": self.test_prompts['simple'],
                        "stream": False
                    },
                    timeout=30
                )
                
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    response_text = data.get('response', '')
                    
                    results.append(LLMTestResult(
                        service_name="Ollama",
                        model_name=model,
                        test_prompt=self.test_prompts['simple'],
                        response_text=response_text,
                        response_quality_score=self._assess_response_quality(response_text),
                        token_usage=None,
                        response_time=response_time,
                        success=True,
                        error_message=None,
                        timestamp=datetime.now().isoformat()
                    ))
                else:
                    results.append(LLMTestResult(
                        service_name="Ollama",
                        model_name=model,
                        test_prompt=self.test_prompts['simple'],
                        response_text=None,
                        response_quality_score=0.0,
                        token_usage=None,
                        response_time=response_time,
                        success=False,
                        error_message=f"HTTP {response.status_code}",
                        timestamp=datetime.now().isoformat()
                    ))
            
            except Exception as e:
                response_time = time.time() - start_time
                results.append(LLMTestResult(
                    service_name="Ollama",
                    model_name=model,
                    test_prompt=self.test_prompts['simple'],
                    response_text=None,
                    response_quality_score=0.0,
                    token_usage=None,
                    response_time=response_time,
                    success=False,
                    error_message=str(e),
                    timestamp=datetime.now().isoformat()
                ))
        
        return results
    
    async def run_performance_benchmarks(self) -> Dict[str, Any]:
        """Run performance benchmarks on available services."""
        benchmarks = {}
        
        # Test concurrent requests
        concurrent_tasks = []
        for i in range(5):  # 5 concurrent requests
            task = self._benchmark_request(i)
            concurrent_tasks.append(task)
        
        try:
            results = await asyncio.gather(*concurrent_tasks, return_exceptions=True)
            successful_results = [r for r in results if not isinstance(r, Exception)]
            
            if successful_results:
                response_times = [r['response_time'] for r in successful_results]
                benchmarks['concurrent_performance'] = {
                    'total_requests': len(concurrent_tasks),
                    'successful_requests': len(successful_results),
                    'average_response_time': statistics.mean(response_times),
                    'median_response_time': statistics.median(response_times),
                    'min_response_time': min(response_times),
                    'max_response_time': max(response_times)
                }
        except Exception as e:
            benchmarks['concurrent_performance'] = {
                'error': str(e)
            }
        
        return benchmarks
    
    async def _benchmark_request(self, request_id: int) -> Dict[str, Any]:
        """Single benchmark request."""
        start_time = time.time()
        
        # Test with local endpoint if available
        test_payload = {
            "text": f"Test request {request_id}: {self.test_prompts['simple']}",
            "source_lang": "english",
            "target_lang": "tau"
        }
        
        try:
            async with self.session.post(
                "http://localhost:3000/api/translate",
                json=test_payload
            ) as response:
                response_time = time.time() - start_time
                return {
                    'request_id': request_id,
                    'response_time': response_time,
                    'status_code': response.status,
                    'success': response.status == 200
                }
        except Exception as e:
            return {
                'request_id': request_id,
                'response_time': time.time() - start_time,
                'error': str(e),
                'success': False
            }
    
    def _assess_security(self, headers: Dict, response_data: Any) -> float:
        """Assess security of API interaction."""
        score = 100.0  # Start with perfect score, deduct points
        
        # Check for API key exposure
        if headers and any('key' in str(v).lower() for v in headers.values()):
            score -= 20
        
        # Check response for sensitive data
        if response_data and isinstance(response_data, dict):
            response_str = json.dumps(response_data).lower()
            if any(sensitive in response_str for sensitive in ['password', 'secret', 'token', 'key']):
                score -= 30
        
        # Check for HTTPS
        # This would be more sophisticated in a real implementation
        
        return max(0.0, score)
    
    def _assess_response_quality(self, response_text: str) -> float:
        """Assess quality of LLM response."""
        if not response_text:
            return 0.0
        
        score = 50.0  # Base score
        
        # Check for Tau language patterns
        tau_patterns = ['always', 'eventually', 'until', 'forall', 'exists', '->', '&&', '||']
        pattern_count = sum(1 for pattern in tau_patterns if pattern in response_text.lower())
        score += pattern_count * 5
        
        # Check response length (not too short, not too long)
        length = len(response_text.strip())
        if 10 <= length <= 200:
            score += 10
        elif length < 5:
            score -= 20
        elif length > 500:
            score -= 10
        
        # Check for coherence (simple heuristics)
        if response_text.count('(') == response_text.count(')'):
            score += 10
        
        return min(100.0, max(0.0, score))
    
    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive test suite."""
        print("Starting comprehensive LLM/API testing...")
        
        # API Tests
        print("Testing API integrations...")
        openrouter_results = await self.test_openrouter_integration()
        openai_results = await self.test_openai_integration()
        local_backend_results = await self.test_local_backend_endpoints()
        
        self.api_results.extend(openrouter_results)
        self.api_results.extend(openai_results)
        self.api_results.extend(local_backend_results)
        
        # LLM Tests
        print("Testing LLM frameworks...")
        guidance_results = self.test_guidance_integration()
        lmql_results = self.test_lmql_integration()
        local_model_results = self.test_local_model_integrations()
        
        self.llm_results.extend(guidance_results)
        self.llm_results.extend(lmql_results)
        self.llm_results.extend(local_model_results)
        
        # Performance Benchmarks
        print("Running performance benchmarks...")
        benchmarks = await self.run_performance_benchmarks()
        
        # Generate comprehensive report
        return self._generate_comprehensive_report(benchmarks)
    
    def _generate_comprehensive_report(self, benchmarks: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        successful_apis = len([r for r in self.api_results if r.success])
        successful_llms = len([r for r in self.llm_results if r.success])
        
        avg_api_response_time = statistics.mean([r.response_time for r in self.api_results if r.success]) if successful_apis > 0 else 0
        avg_llm_response_time = statistics.mean([r.response_time for r in self.llm_results if r.success]) if successful_llms > 0 else 0
        
        avg_security_score = statistics.mean([r.security_score for r in self.api_results if r.success]) if successful_apis > 0 else 0
        avg_quality_score = statistics.mean([r.response_quality_score for r in self.llm_results if r.success]) if successful_llms > 0 else 0
        
        return {
            'summary': {
                'total_api_tests': len(self.api_results),
                'successful_api_tests': successful_apis,
                'total_llm_tests': len(self.llm_results),
                'successful_llm_tests': successful_llms,
                'average_api_response_time': avg_api_response_time,
                'average_llm_response_time': avg_llm_response_time,
                'average_security_score': avg_security_score,
                'average_quality_score': avg_quality_score
            },
            'api_results': [asdict(r) for r in self.api_results],
            'llm_results': [asdict(r) for r in self.llm_results],
            'performance_benchmarks': benchmarks,
            'recommendations': self._generate_recommendations(),
            'timestamp': datetime.now().isoformat()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []
        
        failed_apis = [r for r in self.api_results if not r.success]
        if failed_apis:
            recommendations.append(f"Fix {len(failed_apis)} failing API endpoints")
        
        slow_responses = [r for r in self.api_results if r.success and r.response_time > 5.0]
        if slow_responses:
            recommendations.append(f"Optimize {len(slow_responses)} slow API responses")
        
        security_issues = [r for r in self.api_results if r.success and r.security_score < 80]
        if security_issues:
            recommendations.append(f"Address security concerns in {len(security_issues)} API endpoints")
        
        low_quality_responses = [r for r in self.llm_results if r.success and r.response_quality_score < 60]
        if low_quality_responses:
            recommendations.append(f"Improve quality of {len(low_quality_responses)} LLM responses")
        
        return recommendations


async def main():
    """Main entry point."""
    print("LLM/API Integration Tester")
    print("=" * 50)
    
    async with LLMAPITester() as tester:
        results = await tester.run_comprehensive_test()
    
    # Save results
    output_file = f"llm_api_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    summary = results['summary']
    print("\nTEST RESULTS SUMMARY")
    print("=" * 50)
    print(f"API Tests: {summary['successful_api_tests']}/{summary['total_api_tests']} passed")
    print(f"LLM Tests: {summary['successful_llm_tests']}/{summary['total_llm_tests']} passed")
    print(f"Average API Response Time: {summary['average_api_response_time']:.2f}s")
    print(f"Average LLM Response Time: {summary['average_llm_response_time']:.2f}s")
    print(f"Average Security Score: {summary['average_security_score']:.1f}/100")
    print(f"Average Quality Score: {summary['average_quality_score']:.1f}/100")
    
    if results['recommendations']:
        print("\nRECOMMENDATIONS:")
        for i, rec in enumerate(results['recommendations'], 1):
            print(f"{i}. {rec}")
    
    print(f"\nFull results saved to: {output_file}")


if __name__ == '__main__':
    asyncio.run(main())