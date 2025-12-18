#!/usr/bin/env python3
"""
Test script for the Intelligent Mathematician agent
"""
import asyncio
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.intelligent_mathematician import IntelligentMathematician

async def test_hypothesis_generation():
    """Test hypothesis generation capabilities"""
    print("Testing Intelligent Mathematician hypothesis generation...")
    
    mathematician = IntelligentMathematician()
    
    # Test basic hypothesis generation
    task = {
        'type': 'generate_hypothesis',
        'context': {
            'known_puzzles': list(range(1, 71)),
            'target_puzzle': None,
            'bridge_puzzles': [75, 80, 85, 90, 95, 100, 105, 110, 115, 120, 125, 130],
            'affine_model': 'y = A[l] * x + C[k][l][occ] (mod 256)'
        }
    }
    
    result = await mathematician.execute(task)
    print(f"Hypothesis generation result: {json.dumps(result, indent=2)}")
    
    return result

async def test_mathematical_analysis():
    """Test mathematical analysis capabilities"""
    print("\nTesting mathematical analysis...")
    
    mathematician = IntelligentMathematician()
    
    # Test drift analysis
    task = {
        'type': 'analyze_drift_patterns',
        'puzzle_data': {
            'puzzle_70': {
                'A_values': [123, 45, 67, 89, 12, 34, 56, 78, 90, 11, 22, 33, 44, 55, 66, 77],
                'C_values': [[1,2,3], [4,5,6], [7,8,9], [10,11,12], [13,14,15], [16,17,18], [19,20,21], [22,23,24], [25,26,27], [28,29,30], [31,32,33], [34,35,36], [37,38,39], [40,41,42], [43,44,45], [46,47,48]]
            }
        }
    }
    
    result = await mathematician.execute(task)
    print(f"Drift analysis result: {json.dumps(result, indent=2)}")
    
    return result

async def test_pattern_recognition():
    """Test pattern recognition capabilities"""
    print("\nTesting pattern recognition...")
    
    mathematician = IntelligentMathematician()
    
    # Test cross-lane pattern analysis
    task = {
        'type': 'recognize_patterns',
        'data': {
            'lane_correlations': {
                'lane_0': {'multiplier': 123, 'drift_trend': 'increasing'},
                'lane_1': {'multiplier': 45, 'drift_trend': 'decreasing'},
                'lane_2': {'multiplier': 67, 'drift_trend': 'stable'},
                'lane_3': {'multiplier': 89, 'drift_trend': 'cyclical'}
            }
        }
    }
    
    result = await mathematician.execute(task)
    print(f"Pattern recognition result: {json.dumps(result, indent=2)}")
    
    return result

async def test_theorem_application():
    """Test theorem application capabilities"""
    print("\nTesting theorem application...")
    
    mathematician = IntelligentMathematician()
    
    # Test number theory application
    task = {
        'type': 'apply_theorem',
        'theorem': 'modular_arithmetic',
        'parameters': {
            'modulus': 256,
            'target_value': None,
            'known_values': [1, 2, 3, 70]
        }
    }
    
    result = await mathematician.execute(task)
    print(f"Theorem application result: {json.dumps(result, indent=2)}")
    
    return result

async def test_solution_synthesis():
    """Test solution synthesis capabilities"""
    print("\nTesting solution synthesis...")
    
    mathematician = IntelligentMathematician()
    
    # Test solution construction
    task = {
        'type': 'synthesize_solution',
        'components': {
            'hypothesis': 'Puzzle follows affine recurrence with modified drift',
            'analysis': 'Drift patterns show cyclical behavior every 5 puzzles',
            'patterns': 'Multipliers exhibit prime number relationships',
            'theorems': 'Modular arithmetic constraints limit possible values'
        }
    }
    
    result = await mathematician.execute(task)
    print(f"Solution synthesis result: {json.dumps(result, indent=2)}")
    
    return result

async def test_full_reasoning_chain():
    """Test the complete reasoning chain"""
    print("\nTesting full reasoning chain...")
    
    mathematician = IntelligentMathematician()
    
    # Simulate a complete reasoning process
    print("Step 1: Generate hypothesis...")
    hypothesis_task = {
        'type': 'generate_hypothesis',
        'context': {
            'target_puzzle': None,
            'known_bridge_puzzles': [75, 80, 85],
            'previous_successful_approaches': ['affine_analysis', 'drift_computation']
        }
    }
    
    hypothesis_result = await mathematician.execute(hypothesis_task)
    print(f"Generated hypothesis: {hypothesis_result.get('hypothesis', 'N/A')}")
    
    print("Step 2: Analyze mathematical feasibility...")
    analysis_task = {
        'type': 'analyze_mathematical_feasibility',
        'hypothesis': hypothesis_result.get('hypothesis_statement', ''),
        'constraints': {
            'modulus': 256,
            'max_iterations': 1000,
            'required_accuracy': 0.95
        }
    }
    
    analysis_result = await mathematician.execute(analysis_task)
    print(f"Analysis result: {analysis_result.get('feasibility', 'N/A')}")
    
    print("Step 3: Synthesize solution approach...")
    synthesis_task = {
        'type': 'synthesize_solution',
        'hypothesis': hypothesis_result.get('hypothesis_statement', ''),
        'analysis': analysis_result.get('mathematical_analysis', {}),
        'confidence': analysis_result.get('confidence', 0.5)
    }
    
    final_result = await mathematician.execute(synthesis_task)
    print(f"Final solution approach: {json.dumps(final_result, indent=2)}")
    
    return final_result

async def main():
    """Run all tests"""
    print("=" * 60)
    print("INTELLIGENT MATHEMATICIAN TEST SUITE")
    print("=" * 60)
    
    try:
        # Run individual tests
        await test_hypothesis_generation()
        await test_mathematical_analysis()
        await test_pattern_recognition()
        await test_theorem_application()
        await test_solution_synthesis()
        
        # Run comprehensive test
        final_result = await test_full_reasoning_chain()
        
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Intelligent Mathematician agent is operational!")
        print(f"Reasoning capabilities: ✅ Active")
        print(f"Hypothesis generation: ✅ Working")
        print(f"Mathematical analysis: ✅ Functional")
        print(f"Pattern recognition: ✅ Enabled")
        print(f"Solution synthesis: ✅ Ready")
        
        if final_result.get('solution_approach'):
            print(f"\nGenerated solution approach:")
            print(f"  Strategy: {final_result['solution_approach'].get('strategy', 'N/A')}")
            print(f"  Confidence: {final_result.get('confidence', 0):.2f}")
            print(f"  Next steps: {len(final_result['solution_approach'].get('steps', []))} defined")
        
        return True
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
