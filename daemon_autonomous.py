#!/usr/bin/env python3
"""
Autonomous Discovery Daemon - Runs 24/7 mathematical problem solving
No human input required - pure autonomous reasoning and experimentation
"""
import os
from log_integration import get_system_logger, get_ai_logger, get_memory_logger
import sys
import asyncio
import signal
import time
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.autonomous_orchestrator import AutonomousOrchestrator

class AutonomousDaemon:
    def __init__(self):
        self.orchestrator = None
        self.running = False
        self.start_time = None
        self.stats = {
            'total_iterations': 0,
            'successful_hypotheses': 0,
            'failed_hypotheses': 0,
            'breakthroughs': 0,
            'api_errors': 0
        }
    
    async def start(self):
        """Start the autonomous discovery daemon"""
        print("🚀 Starting Autonomous Mathematical Discovery Daemon")
        print("=" * 70)
        print("This system will run continuously, solving mathematical problems")
        print("without any human input required.")
        print("=" * 70)
        
        self.orchestrator = AutonomousOrchestrator()
        self.running = True
        self.start_time = datetime.now()
        
        print(f"✓ Initialized with model: {self.orchestrator.model}")
        print(f"✓ Max iterations: {self.orchestrator.max_iterations}")
        print(f"✓ Target: Derive formula for all unsolved puzzles")
        print(f"✓ Started at: {self.start_time}")
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        try:
            await self._run_autonomous_loop()
        except KeyboardInterrupt:
            print("\n🛑 Received interrupt signal")
        finally:
            await self._shutdown()
    
    async def _run_autonomous_loop(self):
        """Main autonomous discovery loop"""
        print("\n🔄 Entering autonomous discovery loop...")
        print("Press Ctrl+C to stop (graceful shutdown)")
        
        iteration = 0
        while self.running and iteration < self.orchestrator.max_iterations:
            try:
                iteration += 1
                self.stats['total_iterations'] += 1
                
                print(f"\n{'='*70}")
                print(f"🧠 Autonomous Iteration #{iteration}")
                print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"📊 Total runtime: {datetime.now() - self.start_time}")
                print(f"{'='*70}")
                
                # Run one autonomous reasoning cycle
                result = await self.orchestrator.autonomous_reasoning_cycle()
                
                # Update statistics
                if result['convergence'].get('convergence_status') == 'breakthrough_ready':
                    self.stats['breakthroughs'] += 1
                    print("🎯 BREAKTHROUGH DETECTED!")
                
                if result['verification'].get('verification_status') == 'valid':
                    self.stats['successful_hypotheses'] += 1
                else:
                    self.stats['failed_hypotheses'] += 1
                
                # Print current status
                self._print_status(result)
                
                # Check for solution convergence
                if result['convergence'].get('progress_indicator', 0) >= 0.95:
                    print("\n🎉 SOLUTION CONVERGENCE DETECTED!")
                    print("The autonomous system believes it has found a solution!")
                    await self._handle_solution_found(result)
                    break
                
                # Brief pause between iterations (configurable)
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f"⚠️  Error in iteration {iteration}: {e}")
                self.stats['api_errors'] += 1
                # Continue despite errors - autonomous systems should be resilient
                await asyncio.sleep(5)  # Longer pause on error
    
    def _print_status(self, result):
        """Print current iteration status"""
        print(f"\n📋 Current Status:")
        print(f"   Focus: {self.orchestrator.current_focus}")
        print(f"   Hypothesis: {result['hypothesis'].get('hypothesis_statement', 'Generating...')[:80]}...")
        print(f"   Convergence: {result['convergence'].get('convergence_status', 'Analyzing...')}")
        print(f"   Progress: {result['convergence'].get('progress_indicator', 0):.3f}")
        print(f"   Confidence: {result['convergence'].get('confidence', 0):.3f}")
        
        # Show task sequence if available
        if result['approach'].get('task_sequence'):
            tasks = result['approach']['task_sequence']
            print(f"   Tasks planned: {len(tasks)}")
            for i, task in enumerate(tasks[:3]):  # Show first 3 tasks
                print(f"     {i+1}. {task.get('agent', '?')} -> {task.get('type', '?')}")
        
        # Statistics
        print(f"\n📈 Statistics:")
        print(f"   Total iterations: {self.stats['total_iterations']}")
        print(f"   Successful hypotheses: {self.stats['successful_hypotheses']}")
        print(f"   Failed hypotheses: {self.stats['failed_hypotheses']}")
        print(f"   Breakthroughs: {self.stats['breakthroughs']}")
        print(f"   API errors: {self.stats['api_errors']}")
        
        # Knowledge base
        print(f"   Knowledge base: {len(self.orchestrator.knowledge_base)} insights")
        print(f"   Successful approaches: {len(self.orchestrator.successful_approaches)}")
        print(f"   Failed approaches: {len(self.orchestrator.failed_approaches)}")
    
    async def _handle_solution_found(self, result):
        """Handle when a solution is potentially found"""
        print(f"\n{'='*70}")
        print("🔍 SOLUTION VERIFICATION IN PROGRESS")
        print(f"{'='*70}")
        
        # Get detailed solution analysis
        hypothesis = result['hypothesis']
        approach = result['approach']
        
        print(f"Hypothesis: {hypothesis.get('hypothesis_statement', 'N/A')}")
        print(f"Mathematical formulation: {hypothesis.get('mathematical_formulation', 'N/A')}")
        print(f"Test methodology: {hypothesis.get('test_methodology', 'N/A')}")
        
        print(f"\nApproach: {approach.get('approach_name', 'N/A')}")
        print(f"Success criteria: {approach.get('success_criteria', 'N/A')}")
        
        # Final verification
        verification = result['verification']
        if verification.get('verification_status') == 'valid':
            print(f"\n✅ SOLUTION VERIFIED!")
            print(f"Confidence: {verification.get('confidence', 0):.3f}")
            print(f"Mathematical correctness: {verification.get('mathematical_errors', 'None')}")
            
            # Save solution details
            await self._save_solution(result)
        else:
            print(f"\n⚠️  Solution needs further verification")
            print(f"Status: {verification.get('verification_status')}")
            print(f"Issues: {verification.get('mathematical_errors', 'Unknown')}")
    
    async def _save_solution(self, result):
        """Save the discovered solution"""
        solution_file = f"solution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        solution_data = {
            'timestamp': datetime.now().isoformat(),
            'iteration': self.orchestrator.iteration_count,
            'hypothesis': result['hypothesis'],
            'approach': result['approach'],
            'verification': result['verification'],
            'learning': result['learning'],
            'convergence': result['convergence']
        }
        
        with open(solution_file, 'w') as f:
            import json
            json.dump(solution_data, f, indent=2)
        
        print(f"\n💾 Solution saved to: {solution_file}")
        print("The autonomous system has successfully discovered a mathematical solution!")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        print(f"\n🛑 Received signal {signum}")
        self.running = False
    
    async def _shutdown(self):
        """Graceful shutdown"""
        print(f"\n{'='*70}")
        print("🛑 AUTONOMOUS DAEMON SHUTDOWN")
        print(f"{'='*70}")
        
        runtime = datetime.now() - self.start_time
        print(f"Runtime: {runtime}")
        print(f"Total iterations: {self.stats['total_iterations']}")
        print(f"Successful hypotheses: {self.stats['successful_hypotheses']}")
        print(f"Failed hypotheses: {self.stats['failed_hypotheses']}")
        print(f"Breakthroughs: {self.stats['breakthroughs']}")
        print(f"API errors: {self.stats['api_errors']}")
        
        if self.orchestrator:
            print(f"Knowledge base: {len(self.orchestrator.knowledge_base)} insights")
            print(f"Final focus: {self.orchestrator.current_focus}")
        
        print("\n✅ Autonomous discovery daemon stopped gracefully")

async def main():
    daemon = AutonomousDaemon()
    await daemon.start()

if __name__ == "__main__":
    asyncio.run(main())
