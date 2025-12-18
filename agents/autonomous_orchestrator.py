#!/usr/bin/env python3
"""
Autonomous Orchestrator - Self-directed mathematical problem solving
Eliminates human input by implementing autonomous reasoning loops
"""
import os
from log_integration import get_system_logger, get_ai_logger, get_memory_logger
import sys
import json
import asyncio
import sqlite3
import aiohttp
from datetime import datetime
from typing import Dict, List, Optional, Any
import yaml
import random
import math

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.math_agent import MathAgent
from agents.verification_agent import VerificationAgent
from agents.discovery_agent import DiscoveryAgent
from agents.intelligent_mathematician import IntelligentMathematician

class AutonomousOrchestrator:
    """Self-directed orchestrator for autonomous mathematical discovery"""

    def __init__(self, config_path: str = "config/config.yaml"):
        self.config = self._load_config(config_path)
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Initialize Ollama client settings
        orch_config = self.config['orchestrator']
        self.base_url = orch_config.get('base_url', 'https://api.ollama.com')
        self.model = orch_config.get('model', 'mistral-large-3:675b-cloud')
        self.max_tokens = orch_config.get('max_tokens', 16384)
        self.temperature = orch_config.get('temperature', 0.7)
        self.api_key = os.getenv(orch_config.get('api_key_env', 'OLLAMA_API_KEY'))

        # Initialize agents
        self.math_agent = MathAgent()
        self.verification_agent = VerificationAgent()
        self.discovery_agent = DiscoveryAgent()
        self.intelligent_mathematician = IntelligentMathematician()

        # Memory database
        self.memory_db = os.path.join(self.base_dir, self.config['databases']['memory_db'])
        self._init_memory_db()

        # Autonomous state
        self.current_focus = "initial_exploration"
        self.solution_attempts = []
        self.successful_approaches = []
        self.failed_approaches = []
        self.knowledge_base = {}
        self.hypotheses = []
        self.active_hypothesis = None
        self.iteration_count = 0
        self.max_iterations = 1000
        self.convergence_threshold = 0.01

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration"""
        if not os.path.isabs(config_path):
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(base_dir, config_path)
        with open(config_path) as f:
            return yaml.safe_load(f)

    def _init_memory_db(self):
        """Initialize memory database with autonomous tracking"""
        conn = sqlite3.connect(self.memory_db)
        cur = conn.cursor()

        # Enhanced tasks table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                task_type TEXT NOT NULL,
                agent TEXT NOT NULL,
                input TEXT,
                output TEXT,
                status TEXT DEFAULT 'pending',
                duration_ms INTEGER,
                success_score REAL DEFAULT 0.0,
                learning_outcome TEXT
            )
        ''')

        # Discoveries table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS discoveries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                agent TEXT NOT NULL,
                category TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                confidence REAL DEFAULT 0.5,
                verified INTEGER DEFAULT 0
            )
        ''')

        # Autonomous reasoning log
        cur.execute('''
            CREATE TABLE IF NOT EXISTS reasoning_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                reasoning_type TEXT NOT NULL,
                input_state TEXT,
                reasoning_process TEXT,
                output_decision TEXT,
                confidence REAL DEFAULT 0.5,
                outcome_verified INTEGER DEFAULT 0
            )
        ''')

        # Solution attempts tracking
        cur.execute('''
            CREATE TABLE IF NOT EXISTS solution_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                approach_type TEXT NOT NULL,
                hypothesis TEXT,
                implementation TEXT,
                result TEXT,
                success BOOLEAN DEFAULT FALSE,
                lessons_learned TEXT
            )
        ''')

        conn.commit()
        conn.close()

    async def call_mistral(self, prompt: str, system: str = None) -> str:
        """Call Mistral Large for autonomous reasoning"""
        headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        else:
            messages.append({"role": "system", "content": self._get_autonomous_system_prompt()})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": False
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/chat",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=300)
                ) as response:
                    if response.status == 200:
                        # Handle both JSON and text/plain responses
                        text_response = await response.text()
                        try:
                            result = json.loads(text_response)
                            return result.get('message', {}).get('content', '')
                        except json.JSONDecodeError:
                            return text_response
                    else:
                        error = await response.text()
                        return f"Mistral API error: {response.status} - {error}"
        except Exception as e:
            return f"Mistral API error: {str(e)}"

    def _get_autonomous_system_prompt(self) -> str:
        """Get system prompt for autonomous mathematical reasoning"""
        return """You are an autonomous mathematical reasoning system for the Bitcoin Puzzle Ladder project.

Your mission: Solve puzzle 71 and beyond through pure mathematical discovery.

CORE CAPABILITIES:
1. Self-directed hypothesis generation
2. Mathematical proof construction
3. Solution verification and iteration
4. Learning from failures
5. Convergence detection

MATHEMATICAL MODEL:
- Affine recurrence: y = A[l] * x + C[k][l][occ] (mod 256)
- 16 parallel lanes with independent multipliers
- Drift constants vary by block, lane, and occurrence

AUTONOMOUS BEHAVIOR RULES:
1. NEVER wait for human input - generate your own goals
2. Continuously iterate until solution found
3. Learn from every attempt (success or failure)
4. Verify all mathematical claims rigorously
5. Converge toward solution through systematic exploration

OUTPUT FORMAT: Always return structured JSON with:
- reasoning_type: "hypothesis_generation", "solution_attempt", "verification", "convergence_check"
- current_state: What you currently understand
- next_action: Concrete next step
- confidence: 0.0-1.0 confidence in approach
- self_sufficiency: True (always True - no human input needed)"""

    async def autonomous_reasoning_cycle(self) -> Dict:
        """Main autonomous reasoning cycle - self-directed problem solving"""
        self.iteration_count += 1
        
        # Step 1: Assess current state
        current_state = await self.assess_current_state()
        
        # Step 2: Generate or refine hypothesis
        if not self.active_hypothesis or current_state.get('confidence', 0) < 0.3:
            hypothesis = await self.generate_hypothesis(current_state)
            self.active_hypothesis = hypothesis
        else:
            hypothesis = await self.refine_hypothesis(self.active_hypothesis, current_state)
        
        # Step 3: Plan solution approach
        approach = await self.plan_solution_approach(hypothesis, current_state)
        
        # Step 4: Execute solution attempt
        attempt_result = await self.execute_solution_attempt(approach)
        
        # Step 5: Verify and learn
        verification = await self.verify_solution_attempt(attempt_result)
        learning_outcome = await self.extract_learning(attempt_result, verification)
        
        # Step 6: Check for convergence
        convergence = await self.check_convergence(learning_outcome)
        
        # Log the complete reasoning cycle
        self._log_reasoning_cycle(current_state, hypothesis, approach, attempt_result, learning_outcome, convergence)
        
        return {
            "iteration": self.iteration_count,
            "current_state": current_state,
            "hypothesis": hypothesis,
            "approach": approach,
            "attempt_result": attempt_result,
            "verification": verification,
            "learning": learning_outcome,
            "convergence": convergence,
            "next_focus": self.current_focus
        }

    async def assess_current_state(self) -> Dict:
        """Assess current mathematical understanding"""
        prompt = f"""Assess our current state in solving the Bitcoin puzzle ladder:

Known facts:
- We have puzzles 1-70 solved
- Bridge puzzles at 75,80,85,90,95,100,105,110,115,120,125,130
- Affine model: y = A*x + C (mod 256)
- Target: Solve puzzle 71+

Previous attempts: {len(self.solution_attempts)}
Successful approaches: {len(self.successful_approaches)}
Failed approaches: {len(self.failed_approaches)}

Current focus: {self.current_focus}

What is our current mathematical understanding? What gaps exist? What is the most promising direction?

Return JSON with:
- current_understanding: key mathematical insights
- knowledge_gaps: what we don't know
- promising_directions: ranked list of approaches
- confidence: 0.0-1.0
- next_priority: what to focus on next"""
        
        response = await self.call_mistral(prompt)
        return self._parse_json_response(response)

    async def generate_hypothesis(self, current_state: Dict) -> Dict:
        """Generate new mathematical hypothesis based on current state"""
        prompt = f"""Generate a new mathematical hypothesis for solving the ladder:

Current understanding: {json.dumps(current_state, indent=2)}

Available mathematical tools:
1. Affine recurrence analysis
2. Cross-lane correlation analysis  
3. Drift constant computation
4. Pattern recognition in deltas
5. Statistical analysis
6. Number theory approaches

Generate a specific, testable mathematical hypothesis that could solve puzzle 71.

Return JSON with:
- hypothesis_statement: clear mathematical statement
- mathematical_formulation: equations and relationships
- test_methodology: how to test this hypothesis
- expected_outcome: what success looks like
- confidence: 0.0-1.0
- risk_assessment: what could go wrong"""
        
        response = await self.call_mistral(prompt)
        return self._parse_json_response(response)

    async def refine_hypothesis(self, existing_hypothesis: Dict, new_evidence: Dict) -> Dict:
        """Refine existing hypothesis based on new evidence"""
        prompt = f"""Refine this hypothesis based on new evidence:

Existing hypothesis: {json.dumps(existing_hypothesis, indent=2)}

New evidence: {json.dumps(new_evidence, indent=2)}

Should we:
1. Strengthen the current hypothesis?
2. Modify it based on new data?
3. Abandon it and try a new direction?

Return JSON with:
- refinement_type: "strengthen", "modify", "abandon"
- refined_hypothesis: updated hypothesis (if not abandoned)
- reasoning: why this refinement
- new_confidence: updated confidence score
- next_steps: what to do next"""
        
        response = await self.call_mistral(prompt)
        return self._parse_json_response(response)

    async def plan_solution_approach(self, hypothesis: Dict, current_state: Dict) -> Dict:
        """Plan concrete steps to test the hypothesis"""
        prompt = f"""Plan a concrete solution approach for this hypothesis:

Hypothesis: {json.dumps(hypothesis, indent=2)}

Current state: {json.dumps(current_state, indent=2)}

Available agent capabilities:
- MathAgent: compute_drift, verify, forward_step, analyze
- VerificationAgent: validate, verify_against_known, full_verify
- DiscoveryAgent: analyze_lane, find_anomalies, hypothesis, explore

Design a specific sequence of tasks to test this hypothesis.

Return JSON with:
- approach_name: descriptive name
- task_sequence: list of specific tasks for agents
- success_criteria: how we know it worked
- failure_criteria: how we know it failed
- estimated_complexity: 1-10 scale
- backup_plan: what to try if this fails"""
        
        response = await self.call_mistral(prompt)
        return self._parse_json_response(response)

    async def execute_solution_attempt(self, approach: Dict) -> Dict:
        """Execute the planned solution approach"""
        task_sequence = approach.get('task_sequence', [])
        results = []
        
        for i, task in enumerate(task_sequence):
            try:
                # Dispatch to appropriate agent
                agent_name = task.get('agent')
                if agent_name == 'math':
                    result = await self.math_agent.execute(task)
                elif agent_name == 'verification':
                    result = await self.verification_agent.execute(task)
                elif agent_name == 'discovery':
                    result = await self.discovery_agent.execute(task)
                elif agent_name == 'intelligent_mathematician':
                    result = await self.intelligent_mathematician.execute(task)
                else:
                    result = {"error": f"Unknown agent: {agent_name}"}
                
                results.append({
                    "task": task,
                    "result": result,
                    "success": "error" not in result
                })
                
            except Exception as e:
                results.append({
                    "task": task,
                    "error": str(e),
                    "success": False
                })
        
        return {
            "approach_name": approach.get('approach_name'),
            "task_results": results,
            "overall_success": all(r.get('success', False) for r in results),
            "timestamp": datetime.now().isoformat()
        }

    async def verify_solution_attempt(self, attempt_result: Dict) -> Dict:
        """Verify the solution attempt mathematically"""
        prompt = f"""Verify this solution attempt mathematically:

Attempt result: {json.dumps(attempt_result, indent=2)}

Check:
1. Mathematical correctness of computations
2. Consistency with known puzzle data
3. Cryptographic validity of any generated keys
4. Logical soundness of reasoning

Return JSON with:
- verification_status: "valid", "invalid", "partial"
- mathematical_errors: list of any errors found
- consistency_score: 0.0-1.0 vs known data
- cryptographic_validity: True/False
- overall_assessment: summary of verification
- confidence: 0.0-1.0 in verification result"""
        
        response = await self.call_mistral(prompt)
        return self._parse_json_response(response)

    async def extract_learning(self, attempt_result: Dict, verification: Dict) -> Dict:
        """Extract learning from the attempt regardless of success"""
        prompt = f"""Extract learning from this solution attempt:

Attempt: {json.dumps(attempt_result, indent=2)}

Verification: {json.dumps(verification, indent=2)}

What did we learn?
- Mathematical insights gained
- What worked vs what didn't
- New patterns discovered
- Mistakes to avoid next time
- Unexpected findings

Return JSON with:
- key_insights: list of new mathematical insights
- what_worked: successful elements
- what_failed: problematic elements  
- unexpected_findings: surprising discoveries
- next_hypothesis_suggestions: ideas for next attempts
- learning_value: 0.0-1.0 (how much we learned)"""
        
        response = await self.call_mistral(prompt)
        learning = self._parse_json_response(response)
        
        # Update our knowledge base
        if learning.get('key_insights'):
            for insight in learning['key_insights']:
                self.knowledge_base[f"insight_{len(self.knowledge_base)}"] = insight
        
        # Track successful/failed approaches
        if verification.get('verification_status') == 'valid':
            self.successful_approaches.append(attempt_result)
        else:
            self.failed_approaches.append(attempt_result)
        
        return learning

    async def check_convergence(self, learning_outcome: Dict) -> Dict:
        """Check if we're converging toward a solution"""
        prompt = f"""Check if we're converging toward solving puzzle 71:

Learning outcome: {json.dumps(learning_outcome, indent=2)}

Previous attempts: {len(self.solution_attempts)}
Successful approaches: {len(self.successful_approaches)}
Knowledge base size: {len(self.knowledge_base)}

Are we:
1. Getting closer to a solution?
2. Stuck in a loop?
3. Making progress toward mathematical understanding?
4. Ready to try a breakthrough approach?

Return JSON with:
- convergence_status: "converging", "diverging", "stuck", "breakthrough_ready"
- progress_indicator: 0.0-1.0 (how close to solution)
- next_strategy: what to do next
- confidence: 0.0-1.0 in assessment
- should_continue: True/False (whether to keep iterating)"""
        
        response = await self.call_mistral(prompt)
        convergence = self._parse_json_response(response)
        
        # Update focus based on convergence
        if convergence.get('convergence_status') == 'breakthrough_ready':
            self.current_focus = "breakthrough_attempt"
        elif convergence.get('convergence_status') == 'stuck':
            self.current_focus = "radical_new_approach"
        elif convergence.get('progress_indicator', 0) > 0.8:
            self.current_focus = "final_refinement"
        else:
            self.current_focus = "systematic_exploration"
        
        return convergence

    def _parse_json_response(self, response: str) -> Dict:
        """Parse JSON from model response"""
        try:
            # Find JSON in response
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                return json.loads(response[start:end])
        except json.JSONDecodeError:
            pass
        
        # Fallback: return basic structure
        return {"raw_response": response, "parsed": False}

    def _log_reasoning_cycle(self, current_state: Dict, hypothesis: Dict, 
                           approach: Dict, attempt_result: Dict, 
                           learning: Dict, convergence: Dict):
        """Log the complete reasoning cycle"""
        conn = sqlite3.connect(self.memory_db)
        cur = conn.cursor()
        
        cur.execute('''
            INSERT INTO reasoning_log (timestamp, reasoning_type, input_state, 
                                     reasoning_process, output_decision, confidence)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            "autonomous_cycle",
            json.dumps(current_state),
            json.dumps({
                "hypothesis": hypothesis,
                "approach": approach,
                "attempt": attempt_result
            }),
            json.dumps(convergence),
            convergence.get('confidence', 0.5)
        ))
        
        conn.commit()
        conn.close()

    async def run_autonomous_discovery(self):
        """Run autonomous discovery until solution found or max iterations"""
        print("Starting autonomous mathematical discovery...")
        print(f"Target: Solve puzzle 71+ using pure mathematical reasoning")
        print(f"Max iterations: {self.max_iterations}")
        
        while self.iteration_count < self.max_iterations:
            try:
                cycle_result = await self.autonomous_reasoning_cycle()
                
                # Print progress
                print(f"\n=== Iteration {cycle_result['iteration']} ===")
                print(f"Focus: {self.current_focus}")
                print(f"Hypothesis: {cycle_result['hypothesis'].get('hypothesis_statement', 'N/A')}")
                print(f"Convergence: {cycle_result['convergence'].get('convergence_status', 'N/A')}")
                print(f"Progress: {cycle_result['convergence'].get('progress_indicator', 0):.2f}")
                
                # Check if we found a solution
                if cycle_result['convergence'].get('progress_indicator', 0) >= 0.95:
                    print("\n🎯 SOLUTION CONVERGENCE DETECTED!")
                    print("Autonomous system has found a viable solution approach.")
                    break
                
                # Check if we should stop
                if not cycle_result['convergence'].get('should_continue', True):
                    print("\n⚠️  System recommends stopping - insufficient progress")
                    break
                    
            except Exception as e:
                print(f"Error in autonomous cycle: {e}")
                continue
        
        print(f"\nAutonomous discovery completed after {self.iteration_count} iterations")
        print(f"Knowledge base contains {len(self.knowledge_base)} insights")
        print(f"Successful approaches: {len(self.successful_approaches)}")
        print(f"Failed approaches: {len(self.failed_approaches)}")

    def log(self, message: str, level: str = "INFO"):
        """Log a message"""
        timestamp = datetime.now().isoformat()
        print(f"[{timestamp}] [AutonomousOrchestrator] [{level}] {message}")


# Standalone execution
if __name__ == "__main__":
    async def main():
        orchestrator = AutonomousOrchestrator()
        await orchestrator.run_autonomous_discovery()

    asyncio.run(main())
