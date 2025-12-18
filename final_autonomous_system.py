#!/usr/bin/env python3
"""
Final Autonomous Bitcoin Puzzle Solving System
==============================================

This is the ultimate autonomous system that combines:
- Intelligent analysis and pattern recognition
- Self-directed mathematical reasoning
- Continuous learning and adaptation
- 24/7 operation without human intervention
- Multiple solution strategies working in parallel

Perfect for pure mathematical problems requiring deep reasoning and calculation.
"""

import asyncio
from log_integration import get_system_logger, get_ai_logger, get_memory_logger
import json
import logging
import signal
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from agents.intelligent_analyzer import IntelligentAnalyzer
from agents.intelligent_mathematician import IntelligentMathematician
from agents.autonomous_orchestrator import AutonomousOrchestrator
from agents.math_agent import MathAgent
from agents.discovery_agent import DiscoveryAgent
from agents.verification_agent import VerificationAgent
from memory_system import MemorySystem
from ollama_integration import get_ollama_client, OllamaClient
from token_manager import get_token_manager, TokenManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('final_autonomous.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = get_system_logger().logger

class FinalAutonomousSystem:
    """The ultimate autonomous Bitcoin puzzle solving system."""
    
    def __init__(self):
        self.running = True
        self.memory = MemorySystem()
        self.ollama = get_ollama_client()
        
        # Initialize all specialized agents
        self.analyzer = IntelligentAnalyzer()
        self.mathematician = IntelligentMathematician()
        self.orchestrator = AutonomousOrchestrator()
        self.math_agent = MathAgent()
        self.discovery_agent = DiscoveryAgent()
        self.verification_agent = VerificationAgent()
        
        # System state
        self.solutions_found = []
        self.current_strategy = None
        self.performance_metrics = {
            'total_attempts': 0,
            'successful_solutions': 0,
            'failed_attempts': 0,
            'patterns_discovered': 0,
            'efficiency_score': 0.0
        }
        
        # Token management - use reasonable limits for cloud models
        self.token_manager = get_token_manager("mistral-large", 16384)
        self.max_context_tokens = 16384
        
        logger.info("� Final Autonomous System initialized")
    
    def _make_json_safe(self, obj: Any) -> Any:
        """Recursively convert an object to be JSON serializable."""
        if obj is None:
            return None
        elif isinstance(obj, bool):
            return obj  # bool is JSON serializable
        elif isinstance(obj, (int, float, str)):
            return obj
        elif isinstance(obj, dict):
            return {str(k): self._make_json_safe(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._make_json_safe(item) for item in obj]
        elif hasattr(obj, 'dtype'):  # numpy/pandas types
            return str(obj)
        else:
            return str(obj)

    def _optimize_large_context(self, data: Any, context_name: str, max_tokens: int = None) -> Any:
        """Optimize large contexts to prevent token limit issues."""
        if max_tokens is None:
            max_tokens = self.max_context_tokens * 0.7  # Use 70% of max for safety

        try:
            # First, make everything JSON-safe
            safe_data = self._make_json_safe(data)

            # Convert to string for token counting
            data_str = json.dumps(safe_data)
            current_tokens = self.token_manager.count_tokens(data_str)

            # If within limits, return the safe data
            if current_tokens <= max_tokens:
                return safe_data

            logger.warning(f"Large {context_name} context: {current_tokens} tokens, optimizing...")

            if isinstance(safe_data, dict):
                # Priority keys for analysis results - ordered by importance
                priority_keys = [
                    # High priority - core analysis
                    'executive_summary', 'success_likelihood', 'strategic_recommendations',
                    'next_steps', 'integrated_findings', 'patterns', 'recommendations',
                    # Medium priority - mathematical insights
                    'mathematical_insights', 'hypothesis', 'solution', 'results',
                    'mathematical_structure', 'patterns_and_insights',
                    # Lower priority - metadata
                    'name', 'description', 'pattern', 'success', 'data_inventory',
                    'historical_progress', 'available_approaches', 'knowledge_gaps'
                ]

                optimized = {}

                # Add keys by priority until we hit the limit
                for key in priority_keys:
                    if key in safe_data:
                        value = safe_data[key]
                        # Truncate large nested structures
                        if isinstance(value, list) and len(value) > 10:
                            value = value[:10] + [f"... and {len(safe_data[key]) - 10} more items"]
                        elif isinstance(value, dict) and len(str(value)) > 2000:
                            # Keep only first-level keys with truncated values
                            value = {k: (str(v)[:200] + "..." if len(str(v)) > 200 else v)
                                    for k, v in list(value.items())[:10]}
                        elif isinstance(value, str) and len(value) > 1000:
                            value = value[:1000] + "..."

                        test_data = {**optimized, key: value}
                        test_str = json.dumps(test_data)
                        test_tokens = self.token_manager.count_tokens(test_str)

                        if test_tokens <= max_tokens:
                            optimized[key] = value
                        else:
                            break  # Stop adding keys

                # Also include any remaining top-level keys not in priority list (truncated)
                for key in safe_data:
                    if key not in optimized:
                        value = safe_data[key]
                        if isinstance(value, (str, int, float, bool)) or value is None:
                            test_data = {**optimized, key: value}
                            test_str = json.dumps(test_data)
                            if self.token_manager.count_tokens(test_str) <= max_tokens:
                                optimized[key] = value

                final_tokens = self.token_manager.count_tokens(json.dumps(optimized))
                logger.info(f"Optimized {context_name} from {current_tokens} to {final_tokens} tokens ({len(optimized)} keys)")
                return optimized

            elif isinstance(safe_data, list):
                # Keep items until we hit the limit
                optimized = []
                for i, item in enumerate(safe_data):
                    test_list = optimized + [item]
                    if self.token_manager.count_tokens(json.dumps(test_list)) <= max_tokens * 0.9:
                        optimized.append(item)
                    else:
                        remaining = len(safe_data) - i
                        optimized.append(f"... and {remaining} more items")
                        break

                final_tokens = self.token_manager.count_tokens(json.dumps(optimized))
                logger.info(f"Optimized {context_name} list from {current_tokens} to {final_tokens} tokens")
                return optimized

            else:
                # For other types, truncate string representation
                str_data = str(safe_data)
                if len(str_data) > 2000:
                    str_data = str_data[:2000] + "..."
                return {"value": str_data, "type": type(data).__name__}

        except Exception as e:
            logger.error(f"Error optimizing {context_name} context: {e}")
            # Return a meaningful fallback with the error info
            return {
                "optimization_error": str(e),
                "context_name": context_name,
                "original_type": type(data).__name__,
                "partial_keys": list(data.keys())[:20] if isinstance(data, dict) else None
            }
    
    async def run_full_analysis(self) -> Dict[str, Any]:
        """Run comprehensive intelligent analysis of the entire system."""
        logger.info("🔍 Running full system analysis...")
        
        # Run intelligent mathematical analysis
        mathematical_analysis = await self.mathematician.execute({"type": "deep_analysis"})
        
        # Run pattern analysis - use the correct method name
        analysis_results = await self.analyzer.analyze_system()
        
        # Combine both analyses
        combined_analysis = {
            'mathematical_structure': mathematical_analysis,
            'patterns_and_insights': analysis_results,
            'integrated_findings': self._integrate_analyses(mathematical_analysis, analysis_results)
        }
        
        # Optimize large analysis results to prevent memory issues
        optimized_results = self._optimize_large_context(
            combined_analysis, 
            "analysis_results",
            self.max_context_tokens * 0.5  # Use 50% for analysis to leave room for other data
        )
        
        # Store analysis in memory for future reference - use correct method
        self.memory.store_intelligence('system_analysis', {
            'timestamp': datetime.now().isoformat(),
            'results': optimized_results,
            'patterns': optimized_results.get('patterns', []) if isinstance(optimized_results, dict) else [],
            'recommendations': optimized_results.get('recommendations', []) if isinstance(optimized_results, dict) else []
        })
        
        return optimized_results
    
    def _integrate_analyses(self, math_analysis: Dict, pattern_analysis: Dict) -> Dict[str, Any]:
        """Integrate mathematical and pattern analyses."""
        vulnerabilities = math_analysis.get('cryptographic_vulnerabilities', {})
        patterns = pattern_analysis.get('patterns', [])
        
        integrated = {
            'attack_recommendations': vulnerabilities.get('recommended_attacks', []),
            'vulnerability_severity': vulnerabilities.get('overall_security_level', 'unknown'),
            'pattern_attack_vectors': self._extract_attack_vectors_from_patterns(patterns),
            'confidence_score': self._calculate_confidence(math_analysis, pattern_analysis)
        }
        
        return integrated
    
    def _extract_attack_vectors_from_patterns(self, patterns: List) -> List[str]:
        """Extract potential attack vectors from discovered patterns."""
        attack_vectors = []
        for pattern in patterns:
            if isinstance(pattern, dict):
                name = pattern.get('name', '').lower()
                if 'weak' in name or 'vulnerability' in name or 'exploit' in name:
                    attack_vectors.append(pattern.get('description', 'Unknown attack vector'))
        return attack_vectors
    
    def _calculate_confidence(self, math_analysis: Dict, pattern_analysis: Dict) -> float:
        """Calculate confidence score based on both analyses."""
        math_confidence = 0.5  # Default
        if 'affine_properties' in math_analysis:
            suitability = math_analysis['affine_properties'].get('affine_model_suitability', 'unknown')
            if suitability in ['excellent', 'good']:
                math_confidence = 0.8
            elif suitability == 'moderate':
                math_confidence = 0.6
        
        pattern_confidence = min(len(pattern_analysis.get('patterns', [])) * 0.1, 0.5)
        
        return (math_confidence + pattern_confidence) / 2
    
    async def generate_strategies(self, analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate multiple solution strategies based on analysis."""
        logger.info("🎯 Generating solution strategies...")
        
        strategies = []
        
        # Get integrated findings
        integrated_findings = analysis_results.get('integrated_findings', {})
        
        # Strategy 1: Intelligent Mathematical Attack (Primary)
        hypothesis = await self.mathematician.generate_intelligent_hypothesis()
        if hypothesis and 'error' not in hypothesis:
            strategies.append({
                'name': 'intelligent_mathematical_attack',
                'priority': 1,
                'description': f"Execute intelligent attack: {hypothesis.get('hypothesis_type', 'unknown')}",
                'approach': hypothesis.get('approach', 'algebraic_attack'),
                'hypothesis': hypothesis,
                'expected_success_rate': hypothesis.get('success_probability', 0.5),
                'confidence': hypothesis.get('confidence', 0.5),
                'resources_needed': ['mathematician', 'math_agent', 'verification_agent'],
                'time_estimate': '1-3 hours'
            })
        
        # Strategy 2: Pattern-based mathematical approach (Secondary)
        if analysis_results.get('patterns_and_insights', {}).get('patterns'):
            strategies.append({
                'name': 'pattern_mathematics',
                'priority': 2,
                'description': 'Use discovered patterns for mathematical solutions',
                'approach': 'mathematical_pattern_matching',
                'expected_success_rate': 0.7,
                'resources_needed': ['math_agent', 'verification_agent'],
                'time_estimate': '2-4 hours'
            })
        
        # Strategy 3: Vulnerability exploitation (Tertiary)
        if integrated_findings.get('attack_recommendations'):
            strategies.append({
                'name': 'vulnerability_exploitation',
                'priority': 3,
                'description': 'Exploit identified cryptographic vulnerabilities',
                'approach': 'cryptographic_attack',
                'expected_success_rate': 0.6,
                'resources_needed': ['mathematician', 'verification_agent'],
                'time_estimate': '3-6 hours'
            })
        
        # Strategy 4: Discovery-based approach (Fallback)
        strategies.append({
            'name': 'discovery_exploration',
            'priority': 4,
            'description': 'Explore new mathematical territories',
            'approach': 'exploratory_discovery',
            'expected_success_rate': 0.3,
            'resources_needed': ['discovery_agent', 'math_agent'],
            'time_estimate': '6-12 hours'
        })
        
        return strategies
    
    async def execute_strategy(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific strategy autonomously."""
        # Silent execution - only log results, not starts
        
        self.current_strategy = strategy
        start_time = time.time()
        
        try:
            if strategy['name'] == 'intelligent_mathematical_attack':
                result = await self._execute_intelligent_mathematical_attack(strategy)
            elif strategy['name'] == 'pattern_mathematics':
                result = await self._execute_pattern_mathematics()
            elif strategy['name'] == 'vulnerability_exploitation':
                result = await self._execute_vulnerability_exploitation(strategy)
            elif strategy['name'] == 'discovery_exploration':
                result = await self._execute_discovery_exploration()
            else:
                result = {'success': False, 'error': 'Unknown strategy'}
            
            execution_time = time.time() - start_time
            result['execution_time'] = execution_time
            result['strategy'] = strategy['name']
            
            return result
            
        except Exception as e:
            logger.error(f"Strategy execution failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'execution_time': time.time() - start_time,
                'strategy': strategy['name']
            }
    
    async def _execute_intelligent_mathematical_attack(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Execute intelligent mathematical attack based on generated hypothesis."""
        # Silent - only log results
        
        hypothesis = strategy.get('hypothesis')
        if not hypothesis:
            return {'success': False, 'error': 'No hypothesis provided'}
        
        # Execute the intelligent attack
        attack_result = await self.mathematician.execute_intelligent_attack(hypothesis)
        
        if attack_result.get('success', True):  # Check if attack executed successfully
            # Try to develop solutions from attack results
            solutions = []
            
            if 'target_lanes' in attack_result:
                # Algebraic attack results
                target_lanes = attack_result['target_lanes']
                equations = attack_result.get('equations_setup', 0)
                
                # Use math agent to solve the equation system
                math_result = await self.math_agent.solve_mathematical_problem(
                    f"Solve algebraic system for lanes {target_lanes} with {equations} equations",
                    attack_result
                )
                
                if math_result.get('success'):
                    solutions.append(math_result.get('solution', {}))
            
            elif 'combined_signals' in attack_result:
                # Hybrid attack results
                combined_signals = attack_result['combined_signals']
                
                # Generate candidate solutions
                candidates = await self._generate_candidates_from_signals(combined_signals)
                
                # Verify and refine candidates
                for candidate in candidates[:5]:  # Top 5 candidates
                    verification = await self.verification_agent.verify_solution(candidate)
                    if verification.get('valid'):
                        solutions.append(candidate)
            
            return {
                'success': len(solutions) > 0,
                'solutions': solutions,
                'attack_type': attack_result.get('attack_type', 'unknown'),
                'hypothesis_type': hypothesis.get('hypothesis_type', 'unknown')
            }
        
        return {
            'success': False,
            'error': 'Attack execution failed',
            'attack_result': attack_result
        }
    
    async def _execute_vulnerability_exploitation(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Execute vulnerability exploitation strategy."""
        # Silent - only log results

        try:
            # Get vulnerability analysis using the execute method with proper task type
            vulnerabilities = await self.mathematician.execute({"type": "analyze_vulnerabilities"})

            solutions = []
            vulnerabilities_found = vulnerabilities.get('vulnerabilities_found', [])
            if vulnerabilities_found:
                for vulnerability in vulnerabilities_found[:3]:  # Top 3 vulnerabilities
                    if vulnerability.get('exploitability') in ['high', 'medium']:
                        # Create specific attack for this vulnerability
                        vuln_hypothesis = self._create_vulnerability_hypothesis(vulnerability)

                        # Execute attack
                        attack_result = await self.mathematician.execute_intelligent_attack(vuln_hypothesis)

                        if attack_result.get('success', True):
                            solutions.extend(attack_result.get('solutions', []))

            return {
                'success': len(solutions) > 0,
                'solutions': solutions,
                'vulnerabilities_exploited': len([v for v in vulnerabilities_found if v.get('exploitability') in ['high', 'medium']])
            }
        except Exception as e:
            logger.error(f"Vulnerability exploitation error: {e}")
            return {
                'success': False,
                'solutions': [],
                'vulnerabilities_exploited': 0,
                'error': str(e)
            }
    
    def _create_vulnerability_hypothesis(self, vulnerability: Dict) -> Dict[str, Any]:
        """Create attack hypothesis from vulnerability."""
        vuln_type = vulnerability.get('type', 'unknown')
        
        if vuln_type == 'weak_multipliers':
            return {
                'hypothesis_type': 'weak_multiplier_exploitation',
                'statement': f"Exploit {vulnerability.get('description', 'weak multipliers')}",
                'approach': 'algebraic_attack',
                'confidence': 0.7,
                'attack_steps': [
                    'Identify weak multiplier lanes',
                    'Set up algebraic equations',
                    'Solve equation system',
                    'Extend to remaining lanes'
                ],
                'expected_complexity': 'medium',
                'success_probability': 0.6
            }
        else:
            return {
                'hypothesis_type': 'general_vulnerability_exploitation',
                'statement': f"Exploit {vulnerability.get('description', 'vulnerability')}",
                'approach': 'targeted_attack',
                'confidence': 0.5,
                'attack_steps': ['Analyze vulnerability', 'Develop exploit', 'Test solution'],
                'expected_complexity': 'high',
                'success_probability': 0.4
            }
    
    async def _generate_candidates_from_signals(self, combined_signals: Dict) -> List[Dict]:
        """Generate candidate solutions from combined signals."""
        candidates = []
        prediction = combined_signals.get('combined_prediction', {})
        
        # Convert prediction to candidate solutions
        for key, confidence in prediction.items():
            if confidence > 0.5:  # Only high-confidence predictions
                candidates.append({
                    'type': 'signal_based',
                    'key': key,
                    'confidence': confidence,
                    'approach': 'hybrid_signal_combination'
                })
        
        return candidates
    
    async def _execute_pattern_mathematics(self) -> Dict[str, Any]:
        """Execute pattern-based mathematical strategy."""
        # Silent - only log results
        
        # Get stored patterns from memory
        intelligence = self.memory.retrieve_intelligence("system_analysis")
        patterns = intelligence.get('patterns', []) if intelligence else []
        
        if not patterns:
            logger.warning("No patterns found, switching to discovery mode")
            return await self._execute_discovery_exploration()
        
        solutions = []
        for pattern in patterns[:10]:  # Limit to top 10 patterns
            # Silent processing
            
            # Use math agent to work on this pattern
            math_result = await self.math_agent.solve_mathematical_problem(
                pattern.get('description', ''),
                pattern.get('data', {})
            )
            
            if math_result.get('success'):
                # Verify the solution
                verification = await self.verification_agent.verify_solution(
                    math_result.get('solution', {})
                )
                
                if verification.get('valid'):
                    solutions.append({
                        'pattern': pattern,
                        'solution': math_result.get('solution', {}),
                        'verification': verification
                    })
        
        return {
            'success': len(solutions) > 0,
            'solutions': solutions,
            'patterns_processed': len(patterns[:10])
        }
    
    async def _execute_discovery_exploration(self) -> Dict[str, Any]:
        """Execute discovery exploration strategy."""
        # Silent - only log results

        # Use discovery agent to explore new approaches
        try:
            # Use the correct method name: explore_new_approach (singular)
            discovery = await self.discovery_agent.explore_new_approach()

            solutions = []
            if discovery and discovery.get('approach'):
                # Test the discovery
                test_result = await self.math_agent.test_approach(discovery)
                if test_result.get('promising'):
                    # Develop full solution
                    solution = await self.math_agent.develop_solution(discovery)
                    if solution.get('success'):
                        solutions.append(solution)

            return {
                'success': len(solutions) > 0,
                'solutions': solutions,
                'discoveries_made': 1 if discovery else 0,
                'discovery': discovery
            }
        except Exception as e:
            logger.error(f"Discovery exploration error: {e}")
            return {
                'success': False,
                'solutions': [],
                'discoveries_made': 0,
                'error': str(e)
            }
    
    async def adaptive_learning_loop(self):
        """Main adaptive learning loop that runs continuously."""
        logger.info("🧠 Starting adaptive learning loop...")

        iteration = 0
        consecutive_errors = 0
        max_consecutive_errors = 3
        last_log_iteration = 0

        while self.running:
            iteration += 1

            try:
                # Phase 1: Intelligence Gathering
                analysis_results = await self.run_full_analysis()

                # Phase 2: Strategy Generation
                strategies = await self.generate_strategies(analysis_results)

                # Phase 3: Strategy Execution (try top 3 strategies)
                strategy_success = False
                for strategy in strategies[:3]:
                    result = await self.execute_strategy(strategy)

                    # Update performance metrics
                    self.performance_metrics['total_attempts'] += 1
                    if result.get('success'):
                        self.performance_metrics['successful_solutions'] += 1
                        self.solutions_found.extend(result.get('solutions', []))
                        # Only log successes - important!
                        logger.info(f"✅ Solution found! Strategy: {strategy['name']} | Total: {len(self.solutions_found)}")
                        strategy_success = True
                        consecutive_errors = 0
                    else:
                        self.performance_metrics['failed_attempts'] += 1

                    # Store results in memory (silent)
                    self.memory.store_intelligence(f"strategy_result_{iteration}_{strategy['name']}", {
                        'strategy': strategy,
                        'result': result,
                        'timestamp': datetime.now().isoformat()
                    })

                    # Extract learnings from this result
                    self._extract_learning_from_result(strategy, result)

                    # If we found solutions, focus on verification and refinement
                    if result.get('success'):
                        await self._refine_solutions(result.get('solutions', []))
                        break

                # Update efficiency score
                total = self.performance_metrics['total_attempts']
                if total > 0:
                    self.performance_metrics['efficiency_score'] = (
                        self.performance_metrics['successful_solutions'] / total
                    )

                # Log progress only every 10 iterations or on success
                if strategy_success or (iteration - last_log_iteration >= 10):
                    logger.info(f"📊 Iter {iteration} | Efficiency: {self.performance_metrics['efficiency_score']:.1%} | Solutions: {len(self.solutions_found)}")
                    last_log_iteration = iteration
                
                # Adaptive pause based on recent performance
                if strategy_success:
                    # Success - shorter pause
                    await asyncio.sleep(30)  # 30 seconds on success
                else:
                    # No success - longer pause for analysis
                    await asyncio.sleep(180)  # 3 minutes to analyze and recover
                
            except Exception as e:
                consecutive_errors += 1
                logger.error(f"Error in learning loop (consecutive errors: {consecutive_errors}): {e}")
                
                if consecutive_errors >= max_consecutive_errors:
                    logger.error(f"🚨 Too many consecutive errors ({consecutive_errors}), entering recovery mode")
                    # Extended pause for system recovery
                    await asyncio.sleep(600)  # 10 minutes recovery pause
                    consecutive_errors = 0  # Reset counter after recovery pause
                else:
                    # Progressive backoff based on error count
                    backoff_time = min(300 * consecutive_errors, 900)  # Max 15 minutes
                    logger.info(f"⏱️  Backing off for {backoff_time} seconds")
                    await asyncio.sleep(backoff_time)
    
    async def _refine_solutions(self, solutions: List[Dict[str, Any]]):
        """Refine and optimize found solutions."""
        # Only log if we have solutions to refine
        if solutions:
            logger.info(f"🔧 Refining {len(solutions)} solutions...")
        
        for solution in solutions:
            # Run verification
            verification = await self.verification_agent.verify_solution(solution)
            
            if verification.get('valid'):
                # Try to optimize
                optimization = await self.math_agent.optimize_solution(solution)
                
                if optimization.get('improved'):
                    logger.info("✨ Solution optimized!")
                    # Store optimized solution
                    self.memory.store_solution(optimization.get('optimized_solution'))

    def _extract_learning_from_result(self, strategy: Dict, result: Dict):
        """Extract learnings from strategy execution results."""
        try:
            strategy_name = strategy.get('name', 'unknown')
            success = result.get('success', False)

            # Record progress event
            self.memory.log_progress(
                event_type='strategy_execution',
                description=f"Executed {strategy_name}: {'SUCCESS' if success else 'FAILED'}",
                data={
                    'strategy': strategy_name,
                    'success': success,
                    'execution_time': result.get('execution_time', 0),
                    'solutions_count': len(result.get('solutions', []))
                },
                importance=8 if success else 3
            )

            # Extract insights based on result
            if success:
                # Learn from success
                solutions = result.get('solutions', [])
                if solutions:
                    self.memory.add_learning(
                        topic=f"successful_strategy_{strategy_name}",
                        insight=f"Strategy '{strategy_name}' produced {len(solutions)} solutions with approach: {strategy.get('approach', 'unknown')}",
                        confidence=0.8,
                        source='autonomous_system'
                    )

                    # Extract specific mathematical insights
                    for sol in solutions[:3]:  # Top 3 solutions
                        if isinstance(sol, dict) and 'mathematical_analysis' in sol:
                            self.memory.add_learning(
                                topic='mathematical_insight',
                                insight=f"Math solution found: {str(sol.get('problem', 'unknown'))[:200]}",
                                confidence=0.9,
                                source='math_agent'
                            )
            else:
                # Learn from failure
                error = result.get('error', 'Unknown failure')
                self.memory.add_learning(
                    topic=f"failed_strategy_{strategy_name}",
                    insight=f"Strategy '{strategy_name}' failed: {error[:200]}. Consider alternative approaches.",
                    confidence=0.5,
                    source='autonomous_system'
                )

            # Update efficiency metrics as learning
            total = self.performance_metrics['total_attempts']
            if total > 0 and total % 10 == 0:  # Every 10 attempts
                efficiency = self.performance_metrics['efficiency_score']
                self.memory.add_learning(
                    topic='system_efficiency',
                    insight=f"After {total} attempts: {efficiency:.1%} success rate. Solutions found: {len(self.solutions_found)}",
                    confidence=0.95,
                    source='performance_metrics'
                )

        except Exception as e:
            logger.debug(f"Learning extraction error: {e}")

    def _assess_progress(self) -> Dict[str, Any]:
        """Assess overall system progress and generate recommendations."""
        try:
            # Get metrics
            total_attempts = self.performance_metrics['total_attempts']
            successful = self.performance_metrics['successful_solutions']
            efficiency = self.performance_metrics['efficiency_score']
            solutions_count = len(self.solutions_found)

            # Get learnings and discoveries
            learnings = self.memory.get_learnings()
            discoveries = self.memory.get_discoveries()

            # Calculate trend (if we have history)
            progress_data = self.memory.get_progress_summary(limit=100)
            recent_successes = sum(1 for p in progress_data if p.get('data', {}).get('success', False))
            recent_total = len(progress_data)
            recent_rate = recent_successes / recent_total if recent_total > 0 else 0

            # Generate assessment
            assessment = {
                'timestamp': datetime.now().isoformat(),
                'overall_progress': {
                    'total_attempts': total_attempts,
                    'successful_solutions': successful,
                    'efficiency_score': efficiency,
                    'solutions_found': solutions_count
                },
                'learning_status': {
                    'total_learnings': len(learnings),
                    'high_confidence_learnings': len([l for l in learnings if l.get('confidence', 0) >= 0.8]),
                    'total_discoveries': len(discoveries),
                    'verified_discoveries': len([d for d in discoveries if d.get('verified', False)])
                },
                'trend': {
                    'recent_success_rate': recent_rate,
                    'improving': recent_rate > efficiency if total_attempts > 10 else None
                },
                'recommendations': []
            }

            # Generate recommendations
            if efficiency < 0.1:
                assessment['recommendations'].append("Low efficiency - consider reviewing strategy priorities")
            if len(learnings) < 5:
                assessment['recommendations'].append("Few learnings recorded - system may not be extracting insights")
            if recent_rate < efficiency and total_attempts > 20:
                assessment['recommendations'].append("Performance declining - review recent failures for patterns")
            if solutions_count == 0 and total_attempts > 50:
                assessment['recommendations'].append("No solutions yet - consider expanding search space or adjusting parameters")

            return assessment

        except Exception as e:
            logger.error(f"Progress assessment error: {e}")
            return {'error': str(e)}

    def save_final_report(self):
        """Save comprehensive final report."""
        report = {
            'timestamp': datetime.now().isoformat(),
            'solutions_found': len(self.solutions_found),
            'performance_metrics': self.performance_metrics,
            'final_solutions': self.solutions_found[-10:] if self.solutions_found else [],  # Last 10 solutions
            'system_stats': {
                'total_iterations': self.performance_metrics['total_attempts'],
                'success_rate': self.performance_metrics['efficiency_score'],
                'patterns_discovered': self.performance_metrics['patterns_discovered']
            }
        }
        
        with open('final_autonomous_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info("📋 Final report saved to final_autonomous_report.json")
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"🛑 Received signal {signum}, shutting down gracefully...")
        self.running = False
        self.save_final_report()
        sys.exit(0)
    
    async def run(self):
        """Main entry point for the autonomous system."""
        logger.info("🚀 Starting Final Autonomous Bitcoin Puzzle Solving System")
        logger.info("🧠 This system will run continuously, learning and adapting...")
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        try:
            # Run the adaptive learning loop
            await self.adaptive_learning_loop()
            
        except KeyboardInterrupt:
            logger.info("🛑 Shutdown requested by user")
        finally:
            self.save_final_report()
            logger.info("✅ Final Autonomous System shutdown complete")

async def main():
    """Main entry point."""
    system = FinalAutonomousSystem()
    await system.run()

if __name__ == "__main__":
    asyncio.run(main())
