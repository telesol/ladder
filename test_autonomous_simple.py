#!/usr/bin/env python3
"""
Simple test of the autonomous system - runs a few iterations to demonstrate self-directed problem solving
"""
import sys
import asyncio
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.autonomous_orchestrator import AutonomousOrchestrator

async def test_autonomous_system():
    """Test the autonomous system with a few iterations"""
    print("🚀 Testing Autonomous Mathematical Discovery System")
    print("=" * 60)
    
    # Initialize orchestrator
    orch = AutonomousOrchestrator()
    print(f"✓ Initialized with model: {orch.model}")
    print(f"✓ Max iterations: {orch.max_iterations}")
    print(f"✓ Target: Derive formula for all puzzles")
    
    print("\n" + "=" * 60)
    print("Starting autonomous reasoning cycles...")
    print("=" * 60)
    
    # Run a few iterations to demonstrate autonomous operation
    for i in range(3):
        print(f"\n🔍 Iteration {i+1}")
        print("-" * 30)
        
        try:
            result = await orch.autonomous_reasoning_cycle()
            
            print(f"Focus: {orch.current_focus}")
            print(f"Hypothesis: {result['hypothesis'].get('hypothesis_statement', 'Generating...')[:100]}...")
            print(f"Convergence: {result['convergence'].get('convergence_status', 'Analyzing...')}")
            print(f"Progress: {result['convergence'].get('progress_indicator', 0):.2f}")
            
            # Show what agents are doing
            if result['approach'].get('task_sequence'):
                tasks = result['approach']['task_sequence']
                print(f"Tasks planned: {len(tasks)}")
                for j, task in enumerate(tasks[:2]):  # Show first 2 tasks
                    print(f"  {j+1}. {task.get('agent', '?')} -> {task.get('type', '?')}")
            
        except Exception as e:
            print(f"⚠️  Error in iteration: {e}")
            continue
    
    print("\n" + "=" * 60)
    print("🎯 Autonomous Test Summary")
    print("=" * 60)
    print(f"✓ Completed {orch.iteration_count} autonomous iterations")
    print(f"✓ Knowledge base: {len(orch.knowledge_base)} insights")
    print(f"✓ Successful approaches: {len(orch.successful_approaches)}")
    print(f"✓ Failed approaches: {len(orch.failed_approaches)}")
    print(f"✓ Final focus: {orch.current_focus}")
    
    print("\n🔄 System is now ready for full autonomous operation!")
    print("Run 'python daemon_autonomous.py' to start 24/7 autonomous discovery")

if __name__ == "__main__":
    asyncio.run(test_autonomous_system())
