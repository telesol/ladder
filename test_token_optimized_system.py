#!/usr/bin/env python3
"""
Test script for the token-optimized autonomous system
Tests the system's ability to handle large contexts without interruption
"""

import asyncio
import json
import logging
import time
from datetime import datetime

from final_autonomous_system import FinalAutonomousSystem
from token_manager import get_token_manager
from ollama_integration import get_ollama_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TokenOptimizedSystemTester:
    """Test the autonomous system with token management"""
    
    def __init__(self):
        self.system = FinalAutonomousSystem()
        self.token_manager = get_token_manager("llama3.2", 8192)
        self.test_results = []
    
    async def test_large_context_handling(self):
        """Test handling of large contexts that would normally cause token limit issues"""
        logger.info("🧪 Testing large context handling...")
        
        # Create a very large test context that would exceed normal limits
        large_context = {
            'patterns': [],
            'solutions': [],
            'analysis': {},
            'historical_data': []
        }
        
        # Generate a large dataset that would normally cause token issues
        for i in range(1000):
            large_context['patterns'].append({
                'id': i,
                'name': f'Pattern_{i}',
                'description': f'This is a detailed description of pattern {i} with lots of mathematical data and analysis results that would normally consume many tokens in the context window. The pattern involves complex mathematical relationships and cryptographic principles that require extensive explanation and detailed analysis to fully understand the underlying structure and potential applications in bitcoin puzzle solving.',
                'data': {
                    'values': list(range(50)),
                    'calculations': [j * 2.5 + i for j in range(100)],
                    'metadata': {
                        'timestamp': datetime.now().isoformat(),
                        'complexity': 'high',
                        'confidence': 0.85 + (i % 15) * 0.01,
                        'related_patterns': list(range(max(0, i-5), min(1000, i+5)))
                    }
                }
            })
        
        # Test token counting
        context_str = json.dumps(large_context)
        token_count = self.token_manager.count_tokens(context_str)
        logger.info(f"📊 Large context token count: {token_count}")
        
        # Test optimization
        start_time = time.time()
        optimized_context = self.system._optimize_large_context(
            large_context, 
            "test_context",
            max_tokens=2000  # Force optimization
        )
        optimization_time = time.time() - start_time
        
        optimized_tokens = self.token_manager.count_tokens(json.dumps(optimized_context))
        logger.info(f"⚡ Optimization completed in {optimization_time:.2f}s")
        logger.info(f"📉 Tokens reduced from {token_count} to {optimized_tokens}")
        logger.info(f"📈 Compression ratio: {token_count/optimized_tokens:.2f}x")
        
        return {
            'test': 'large_context_handling',
            'original_tokens': token_count,
            'optimized_tokens': optimized_tokens,
            'compression_ratio': token_count/optimized_tokens,
            'optimization_time': optimization_time,
            'success': optimized_tokens < token_count
        }
    
    async def test_analysis_with_large_data(self):
        """Test the analysis system with large datasets"""
        logger.info("🔍 Testing analysis with large data...")
        
        # Create large analysis results that would normally cause issues
        analysis_data = {
            'patterns': [],
            'recommendations': [],
            'insights': [],
            'mathematical_relationships': []
        }
        
        # Generate extensive analysis data
        for i in range(500):
            analysis_data['patterns'].append({
                'type': 'mathematical',
                'confidence': 0.9,
                'description': f'Complex mathematical pattern {i} involving multiple variables and relationships that require detailed explanation and analysis to understand the full implications and potential applications in cryptographic problem solving.',
                'applications': ['bitcoin_puzzle', 'cryptography', 'mathematics'],
                'complexity_score': 8.5 + (i % 10) * 0.1
            })
            
            analysis_data['recommendations'].append({
                'priority': i % 5 + 1,
                'action': f'Implement advanced mathematical approach {i} with detailed analysis and verification steps',
                'expected_impact': 'high' if i % 3 == 0 else 'medium',
                'implementation_complexity': 'complex'
            })
        
        # Test the analysis optimization
        start_time = time.time()
        optimized_analysis = self.system._optimize_large_context(
            analysis_data,
            "analysis_results",
            max_tokens=3000
        )
        analysis_time = time.time() - start_time
        
        original_tokens = self.token_manager.count_tokens(json.dumps(analysis_data))
        optimized_tokens = self.token_manager.count_tokens(json.dumps(optimized_analysis))
        
        logger.info(f"📊 Analysis optimization completed in {analysis_time:.2f}s")
        logger.info(f"📉 Analysis tokens reduced from {original_tokens} to {optimized_tokens}")
        
        return {
            'test': 'analysis_with_large_data',
            'original_tokens': original_tokens,
            'optimized_tokens': optimized_tokens,
            'optimization_time': analysis_time,
            'success': optimized_tokens < original_tokens
        }
    
    async def test_ollama_integration_with_token_limits(self):
        """Test Ollama integration with token limit handling"""
        logger.info("🤖 Testing Ollama integration with token limits...")
        
        # Create a large prompt that would exceed limits
        large_prompt = """
        Analyze the following extensive mathematical dataset for Bitcoin puzzle solving:
        """ + "\n".join([
            f"Dataset {i}: Contains mathematical relationships involving prime numbers, "
            f"elliptic curve operations, and cryptographic hash functions with "
            f"complexity level {8.0 + (i % 20) * 0.1} and confidence score {0.8 + (i % 10) * 0.02}"
            for i in range(200)
        ])
        
        # Test with token limits
        token_count = self.token_manager.count_tokens(large_prompt)
        logger.info(f"📊 Large prompt token count: {token_count}")
        
        # Test generation with token management
        client = get_ollama_client()
        start_time = time.time()
        
        try:
            response = await client.generate(
                model="llama3.2",
                prompt=large_prompt,
                max_tokens=1024,
                temperature=0.7
            )
            generation_time = time.time() - start_time
            
            success = not response.startswith("Error") and len(response) > 0
            logger.info(f"⚡ Generation completed in {generation_time:.2f}s")
            logger.info(f"📤 Response length: {len(response)} characters")
            logger.info(f"✅ Success: {success}")
            
            return {
                'test': 'ollama_token_limits',
                'prompt_tokens': token_count,
                'response_length': len(response),
                'generation_time': generation_time,
                'success': success,
                'error': None if success else response
            }
            
        except Exception as e:
            logger.error(f"❌ Generation failed: {e}")
            return {
                'test': 'ollama_token_limits',
                'prompt_tokens': token_count,
                'success': False,
                'error': str(e)
            }
    
    async def test_continuous_operation(self):
        """Test continuous operation without token-related interruptions"""
        logger.info("🔄 Testing continuous operation...")
        
        start_time = time.time()
        iterations = 0
        errors = 0
        token_issues = 0
        
        # Run multiple iterations with large contexts
        for i in range(10):
            iterations += 1
            try:
                # Create large context for each iteration
                large_context = {
                    'iteration': i,
                    'data': [f"Large data point {j} with extensive mathematical analysis and cryptographic details" for j in range(100)],
                    'analysis': {
                        'patterns': [f'Pattern {k} with detailed description and mathematical relationships' for k in range(50)],
                        'recommendations': [f'Recommendation {l} with comprehensive implementation details' for l in range(30)]
                    }
                }
                
                # Test context optimization
                optimized = self.system._optimize_large_context(
                    large_context,
                    f"iteration_{i}",
                    max_tokens=1500
                )
                
                # Test with Ollama
                response = await self.system.ollama.generate(
                    model="llama3.2",
                    prompt=f"Analyze this optimized data: {json.dumps(optimized)}",
                    max_tokens=512
                )
                
                if response.startswith("Error") and "token" in response.lower():
                    token_issues += 1
                
            except Exception as e:
                errors += 1
                if "token" in str(e).lower():
                    token_issues += 1
                logger.warning(f"Iteration {i} error: {e}")
        
        total_time = time.time() - start_time
        
        logger.info(f"🔄 Continuous operation test completed:")
        logger.info(f"📊 Iterations: {iterations}")
        logger.info(f"⚡ Total time: {total_time:.2f}s")
        logger.info(f"❌ Errors: {errors}")
        logger.info(f"🎯 Token issues: {token_issues}")
        logger.info(f"✅ Success rate: {((iterations - errors) / iterations * 100):.1f}%")
        
        return {
            'test': 'continuous_operation',
            'iterations': iterations,
            'total_time': total_time,
            'errors': errors,
            'token_issues': token_issues,
            'success_rate': (iterations - errors) / iterations,
            'success': token_issues == 0 and errors < iterations * 0.2  # Allow 20% error rate
        }
    
    async def run_all_tests(self):
        """Run all token optimization tests"""
        logger.info("🚀 Starting comprehensive token optimization tests...")
        
        tests = [
            self.test_large_context_handling,
            self.test_analysis_with_large_data,
            self.test_ollama_integration_with_token_limits,
            self.test_continuous_operation
        ]
        
        results = []
        start_time = time.time()
        
        for test in tests:
            try:
                result = await test()
                results.append(result)
                logger.info(f"✅ {result['test']}: {'PASSED' if result['success'] else 'FAILED'}")
            except Exception as e:
                logger.error(f"❌ Test {test.__name__} failed with exception: {e}")
                results.append({
                    'test': test.__name__,
                    'success': False,
                    'error': str(e)
                })
        
        total_time = time.time() - start_time
        
        # Generate summary report
        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_tests': len(results),
            'passed_tests': sum(1 for r in results if r['success']),
            'failed_tests': sum(1 for r in results if not r['success']),
            'total_time': total_time,
            'detailed_results': results
        }
        
        # Save test report
        with open('token_optimization_test_report.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info("📋 Token optimization test report saved to token_optimization_test_report.json")
        logger.info(f"📊 Test Summary: {summary['passed_tests']}/{summary['total_tests']} tests passed")
        
        return summary

async def main():
    """Main test function"""
    tester = TokenOptimizedSystemTester()
    results = await tester.run_all_tests()
    
    if results['passed_tests'] == results['total_tests']:
        logger.info("🎉 All token optimization tests PASSED!")
        logger.info("✅ The system can now handle large contexts without token limit interruptions!")
    else:
        logger.warning(f"⚠️  {results['failed_tests']} tests failed. Review the results for improvements.")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())
