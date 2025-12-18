#!/usr/bin/env python3
"""
Test script for the offline autonomous system
Tests all agents without Ollama API dependency
"""
import asyncio
import json
import sys
import traceback
from datetime import datetime

# Import offline agents
from agents.intelligent_mathematician import IntelligentMathematician
from agents.intelligent_analyzer import IntelligentAnalyzer
from agents.discovery_agent_offline import DiscoveryAgentOffline
from agents.verification_agent_offline import VerificationAgentOffline

async def test_intelligent_mathematician():
    """Test the intelligent mathematician agent"""
    print("=" * 60)
    print("Testing Intelligent Mathematician Agent")
    print("=" * 60)
    
    try:
        agent = IntelligentMathematician()
        print("✓ Intelligent Mathematician initialized")
        
        # Test algebraic exploitation approach
        approach = {
            "type": "algebraic_exploitation",
            "target_lanes": [0, 1, 2, 3],
            "method": "backward_solving",
            "expected_complexity": 1000
        }
        
        result = await agent.execute({
            "type": "test_approach",
            "approach": approach
        })
        
        print(f"✓ Algebraic exploitation test result:")
        print(json.dumps(result, indent=2))
        
        # Test mathematical problem solving
        problem = "Solve the Bitcoin puzzle ladder using algebraic exploitation on weak A-multiplier lanes"
        context = {"target_lane": 0, "method": "backward_solving"}
        
        result = await agent.execute({
            "type": "solve",
            "description": problem,
            "context_data": context
        })
        
        print(f"✓ Mathematical problem solving result:")
        print(json.dumps(result, indent=2))
        
        return True
        
    except Exception as e:
        print(f"✗ Intelligent Mathematician test failed: {e}")
        traceback.print_exc()
        return False

async def test_intelligent_analyzer():
    """Test the intelligent analyzer agent"""
    print("=" * 60)
    print("Testing Intelligent Analyzer Agent")
    print("=" * 60)
    
    try:
        agent = IntelligentAnalyzer()
        print("✓ Intelligent Analyzer initialized")
        
        # Test system analysis
        result = await agent.analyze_system()
        print(f"✓ System analysis result:")
        print(json.dumps(result, indent=2))
        
        # Test pattern discovery
        data = {
            "lane_data": {"lane": 0},
            "search_for_anomalies": True
        }
        
        result = await agent.execute({
            "type": "discover_patterns",
            "data": data
        })
        
        print(f"✓ Pattern discovery result:")
        print(json.dumps(result, indent=2))
        
        return True
        
    except Exception as e:
        print(f"✗ Intelligent Analyzer test failed: {e}")
        traceback.print_exc()
        return False

async def test_discovery_agent():
    """Test the discovery agent (offline version)"""
    print("=" * 60)
    print("Testing Discovery Agent (Offline)")
    print("=" * 60)
    
    try:
        agent = DiscoveryAgentOffline()
        print("✓ Discovery Agent Offline initialized")
        
        # Test lane analysis
        result = agent.analyze_lane_patterns(0)
        print(f"✓ Lane 0 analysis result:")
        print(json.dumps(result, indent=2))
        
        # Test anomaly detection
        anomalies = agent.find_anomalies()
        print(f"✓ Found {len(anomalies)} anomalies")
        
        # Test new approach exploration
        result = await agent.explore_new_approach()
        print(f"✓ New approach exploration result:")
        print(json.dumps(result, indent=2))
        
        return True
        
    except Exception as e:
        print(f"✗ Discovery Agent test failed: {e}")
        traceback.print_exc()
        return False

async def test_verification_agent():
    """Test the verification agent (offline version)"""
    print("=" * 60)
    print("Testing Verification Agent (Offline)")
    print("=" * 60)
    
    try:
        agent = VerificationAgentOffline()
        print("✓ Verification Agent Offline initialized")
        
        # Test bit length verification
        result = agent.verify_bit_length(66)
        print(f"✓ Bit length verification result:")
        print(json.dumps(result, indent=2))
        
        # Test affine parameter verification
        A_matrix = [[1 if i == j else 0 for j in range(16)] for i in range(16)]
        C_constants = [[[0 for occ in range(4)] for lane in range(16)] for block in range(16)]
        result = agent.verify_affine_parameters(A_matrix, C_constants)
        print(f"✓ Affine parameters verification result:")
        print(json.dumps(result, indent=2))
        
        # Test approach verification
        approach = {
            "type": "algebraic_exploitation",
            "target_lanes": [0, 1, 2, 3],
            "method": "backward_solving",
            "expected_complexity": 1000
        }
        
        result = await agent.verify_approach(approach)
        print(f"✓ Approach verification result:")
        print(json.dumps(result, indent=2))
        
        return True
        
    except Exception as e:
        print(f"✗ Verification Agent test failed: {e}")
        traceback.print_exc()
        return False

async def test_algebraic_exploitation_workflow():
    """Test the complete algebraic exploitation workflow"""
    print("=" * 60)
    print("Testing Algebraic Exploitation Workflow")
    print("=" * 60)
    
    try:
        # Initialize agents
        mathematician = IntelligentMathematician()
        discovery = DiscoveryAgentOffline()
        verification = VerificationAgentOffline()
        
        print("✓ All agents initialized")
        
        # Step 1: Discover patterns in weak lanes
        print("\nStep 1: Discovering patterns in weak lanes...")
        lane_analysis = discovery.analyze_lane_patterns(0)
        print(f"Lane 0 analysis: {lane_analysis}")
        
        # Step 2: Generate hypothesis for algebraic exploitation
        print("\nStep 2: Generating hypothesis...")
        observation = f"Lane 0 shows pattern: {lane_analysis['most_common_delta']} most common delta"
        hypothesis = await discovery.generate_hypothesis(observation)
        print(f"Generated hypothesis: {hypothesis}")
        
        # Step 3: Develop algebraic exploitation approach
        print("\nStep 3: Developing algebraic exploitation approach...")
        approach = {
            "type": "algebraic_exploitation",
            "target_lanes": [0, 1, 2, 3],
            "method": "backward_solving",
            "expected_complexity": 1000,
            "based_on_hypothesis": hypothesis["hypothesis"]
        }
        
        # Step 4: Verify the approach
        print("\nStep 4: Verifying approach...")
        verification_result = await verification.verify_approach(approach)
        print(f"Approach verification: {verification_result}")
        
        # Step 5: Test the approach
        print("\nStep 5: Testing approach...")
        test_result = await mathematician.execute({
            "type": "test_approach",
            "approach": approach
        })
        print(f"Approach test result: {test_result}")
        
        # Step 6: Develop solution if approach is promising
        if test_result.get("promising", False):
            print("\nStep 6: Developing solution...")
            solution_result = await mathematician.execute({
                "type": "develop_solution",
                "approach": approach
            })
            print(f"Solution development: {solution_result}")
            
            # Step 7: Verify the complete solution
            print("\nStep 7: Verifying complete solution...")
            if solution_result.get("success", False):
                solution_verification = await verification.verify_solution({
                    "approach": approach,
                    "implementation": solution_result.get("solution", {}),
                    "test_results": test_result
                })
                print(f"Solution verification: {solution_verification}")
        
        return True
        
    except Exception as e:
        print(f"✗ Algebraic exploitation workflow test failed: {e}")
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    print("Starting Offline Autonomous System Tests")
    print(f"Test started at: {datetime.now().isoformat()}")
    print()
    
    test_results = {
        "intelligent_mathematician": False,
        "intelligent_analyzer": False,
        "discovery_agent": False,
        "verification_agent": False,
        "algebraic_exploitation_workflow": False
    }
    
    # Run individual agent tests
    test_results["intelligent_mathematician"] = await test_intelligent_mathematician()
    test_results["intelligent_analyzer"] = await test_intelligent_analyzer()
    test_results["discovery_agent"] = await test_discovery_agent()
    test_results["verification_agent"] = await test_verification_agent()
    
    # Run workflow test
    test_results["algebraic_exploitation_workflow"] = await test_algebraic_exploitation_workflow()
    
    # Summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(test_results.values())
    total = len(test_results)
    
    print(f"Tests passed: {passed}/{total}")
    print(f"Success rate: {passed/total*100:.1f}%")
    
    for test_name, result in test_results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name}: {status}")
    
    if passed == total:
        print("\n🎉 All tests passed! The offline system is working correctly.")
        print("The algebraic exploitation approach can be tested without external API dependencies.")
        return 0
    else:
        print(f"\n❌ {total - passed} tests failed. Check the error messages above.")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
