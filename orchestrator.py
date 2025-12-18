#!/usr/bin/env python3
"""
MAESTRO ORCHESTRATOR
====================
Coordinates A-Solver, B-Solver, and C-Solver for formula derivation.
Saves all insights to the agent memory system.
Goal: Derive the key generation formula using ALL 74 known keys.
"""
import sys
sys.path.insert(0, '/home/solo/LA')

import requests
import json
import time
from datetime import datetime
from agent_memory import AgentMemory
import puzzle_config  # Central config - no hardcoding

# Initialize memory
memory = AgentMemory()

# Agent configurations
AGENTS = {
    'a-solver': {'model': 'qwen3-vl:8b', 'timeout': 120, 'specialty': 'Fast analysis, wallet forensics'},
    'b-solver': {'model': 'phi4-reasoning:14b', 'timeout': 300, 'specialty': 'Deep reasoning, anomalies'},
    'c-solver': {'model': 'qwq:32b', 'timeout': 600, 'specialty': 'Prediction, synthesis'}
}

# All data from DB via puzzle_config
KEYS = puzzle_config.KEYS  # All 74 known keys
UNSOLVED = puzzle_config.UNSOLVED  # All 86 targets

def query_agent(agent_id: str, prompt: str) -> dict:
    """Query an agent and save to memory"""
    config = AGENTS[agent_id]
    print(f"\n{'='*60}")
    print(f"[{agent_id.upper()}] {config['specialty']}")
    print(f"{'='*60}")

    t0 = time.time()
    try:
        resp = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": config['model'], "prompt": prompt, "stream": False},
            timeout=config['timeout']
        )
        response = resp.json().get("response", "") if resp.status_code == 200 else f"Error: {resp.status_code}"
    except requests.exceptions.Timeout:
        response = "TIMEOUT - agent needs Oracle mode for this query"
    except Exception as e:
        response = f"Error: {e}"

    elapsed = time.time() - t0

    # Save to memory
    memory.save_agent_message(agent_id, 'user', prompt[:500], len(prompt)//4, 0)
    memory.save_agent_message(agent_id, 'assistant', response[:2000], len(response)//4, elapsed)

    print(f"Time: {elapsed:.1f}s")
    print(f"Response ({len(response)} chars):")
    print(response[:1500] + "..." if len(response) > 1500 else response)

    return {'agent': agent_id, 'response': response, 'time': elapsed}

def extract_insights(agent_id: str, response: str, category: str):
    """Extract and save key insights from response"""
    # Look for key findings
    insights = []

    keywords = {
        'position': ['minimum', 'maximum', 'first', 'last', '%', 'position'],
        'divisibility': ['divisible', 'factor', 'prime', '11', '71'],
        'pattern': ['pattern', 'relationship', 'correlation', 'regime'],
        'prediction': ['predict', 'likely', 'search', 'focus', 'region']
    }

    for cat, words in keywords.items():
        if any(w.lower() in response.lower() for w in words):
            # Extract relevant sentence
            for sentence in response.split('.'):
                if any(w.lower() in sentence.lower() for w in words):
                    insight = sentence.strip()[:200]
                    if len(insight) > 20:
                        memory.add_agent_insight(
                            agent_id=agent_id,
                            category=cat,
                            insight=insight,
                            confidence=0.7,
                            source_query=category,
                            tags=[cat, 'formula']
                        )
                        insights.append(insight)
                        break

    return insights

def run_orchestrated_analysis():
    """Run coordinated multi-agent analysis"""
    print("="*70)
    print("MAESTRO ORCHESTRATOR - Multi-Agent Formula Derivation")
    print("="*70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target: k71 in range [{puzzle_config.get_puzzle_range(71)[0]:,}, {puzzle_config.get_puzzle_range(71)[1]:,}]")
    print(f"Range size: {puzzle_config.get_puzzle_range(71)[1] - puzzle_config.get_puzzle_range(71)[0] + 1:,} values")

    results = {}

    # ========== PHASE 1: A-SOLVER Quick Analysis ==========
    print("\n" + "="*70)
    print("PHASE 1: A-SOLVER QUICK ANALYSIS")
    print("="*70)

    # Task 1.1: Position analysis
    r1 = query_agent('a-solver', f"""You are A-Solver for Bitcoin puzzle analysis.

Known positions in their bit ranges:
- k69 at 0.72% (near minimum) - solved quickly!
- k70 at 64.4% (mid-range)
- k4 at 0% (minimum), k3 at 100% (maximum)
- k10 at 0.39% (near minimum)

k71 range: [{puzzle_config.get_puzzle_range(71)[0]}, {puzzle_config.get_puzzle_range(71)[1]}]
k70 = {KEYS.get(70, 0)}

Question: Based on position patterns, where should we focus search for k71?
Calculate the actual value ranges for:
1. First 1% of range (like k69)
2. First 5% of range
3. Middle 50% of range

Give specific numeric bounds.""")
    results['position_analysis'] = r1
    extract_insights('a-solver', r1['response'], 'position')

    # Task 1.2: Divisibility check
    r2 = query_agent('a-solver', f"""A-Solver divisibility analysis.

Patterns found:
- k11 = 1155 = 3×5×7×11 (divisible by 11, the puzzle number!)
- k69 divisible by 11 (not 69)
- k4 divisible by 4, k8 by 8

For k71:
1. Should k71 be divisible by 71? (71 is prime)
2. Should k71 be divisible by 11?
3. What other factors should we check?

k71 range: [{puzzle_config.get_puzzle_range(71)[0]}, {puzzle_config.get_puzzle_range(71)[1]}]
How many values in this range are divisible by 71?
How many by 11?""")
    results['divisibility'] = r2
    extract_insights('a-solver', r2['response'], 'divisibility')

    # ========== PHASE 2: B-SOLVER Deep Reasoning ==========
    print("\n" + "="*70)
    print("PHASE 2: B-SOLVER DEEP REASONING")
    print("="*70)

    r3 = query_agent('b-solver', f"""You are B-Solver, a deep reasoning AI (phi4-reasoning).

CONTEXT:
- 70 puzzles solved, searching for k71
- k69 found at position 0.72% (solved FAST because searchers focused on low positions)
- k70 at 64.4% position
- Historical anomalies: k3→k4 delta=0.125 (LOW), k56→k57 delta=1.305 (HIGH)
- Early keys (k1-k6) have math relations: k5=k2×k3=21, k6=k3²=49
- After k6, keys appear pseudorandom

k71 range: [{puzzle_config.get_puzzle_range(71)[0]}, {puzzle_config.get_puzzle_range(71)[1]}]
k70 = {KEYS.get(70, 0)}
k69 = {KEYS.get(69, 0)}

TASK: Deep analysis
1. What is the expected delta pattern from k70 to k71?
2. Given k69 was near minimum and k70 is mid-range, what does alternation suggest for k71?
3. Synthesize all patterns into a search recommendation.

Think step by step. Use <think> blocks for reasoning.""")
    results['deep_reasoning'] = r3
    extract_insights('b-solver', r3['response'], 'deep_analysis')

    # ========== PHASE 3: SYNTHESIS ==========
    print("\n" + "="*70)
    print("PHASE 3: MAESTRO SYNTHESIS")
    print("="*70)

    # Collect all insights
    all_insights = memory.get_agent_insights(min_confidence=0.0)

    print("\nCollected Insights:")
    for i, insight in enumerate(all_insights, 1):
        print(f"  {i}. [{insight['agent_id']}] {insight['category']}: {insight['insight'][:80]}...")

    # Generate search recommendations
    print("\n" + "="*70)
    print("SEARCH RECOMMENDATIONS FOR k71")
    print("="*70)

    recommendations = []

    # Based on k69 pattern (0.72%)
    low_1pct_start = puzzle_config.get_puzzle_range(71)[0]
    low_1pct_end = puzzle_config.get_puzzle_range(71)[0] + (puzzle_config.get_puzzle_range(71)[1] - puzzle_config.get_puzzle_range(71)[0]) // 100
    recommendations.append({
        'priority': 1,
        'region': 'First 1% (like k69)',
        'start': low_1pct_start,
        'end': low_1pct_end,
        'rationale': 'k69 was at 0.72%, k4 at 0%, k10 at 0.39%'
    })

    # Divisibility by 11 candidates
    first_div_11 = ((puzzle_config.get_puzzle_range(71)[0] // 11) + 1) * 11
    recommendations.append({
        'priority': 2,
        'region': 'First div-by-11 in range',
        'start': first_div_11,
        'end': first_div_11 + 11 * 1000000,
        'rationale': 'k69 divisible by 11, k11=3×5×7×11'
    })

    # Divisibility by 71 candidates
    first_div_71 = ((puzzle_config.get_puzzle_range(71)[0] // 71) + 1) * 71
    recommendations.append({
        'priority': 3,
        'region': 'First div-by-71 in range',
        'start': first_div_71,
        'end': first_div_71 + 71 * 100000,
        'rationale': '71 is prime, could follow k11 pattern'
    })

    for rec in recommendations:
        print(f"\nPriority {rec['priority']}: {rec['region']}")
        print(f"  Range: [{rec['start']:,}, {rec['end']:,}]")
        print(f"  Rationale: {rec['rationale']}")

    # Save to shared knowledge
    memory.add_shared_knowledge(
        fact_type='search_recommendation',
        fact=f"k71 high-priority search: first 1% of range [{low_1pct_start}, {low_1pct_end}]",
        discovered_by='maestro',
        confidence=0.8,
        metadata=json.dumps(recommendations)
    )

    # Save results
    output = {
        'timestamp': datetime.now().isoformat(),
        'results': {k: {'response': v['response'][:2000], 'time': v['time']} for k, v in results.items()},
        'recommendations': recommendations,
        'insights_count': len(all_insights)
    }

    with open('/home/solo/LA/orchestrator_results.json', 'w') as f:
        json.dump(output, f, indent=2)

    print("\n" + "="*70)
    print("ORCHESTRATION COMPLETE")
    print("="*70)
    print(f"Results saved to: orchestrator_results.json")
    print(f"Insights in memory: {len(all_insights)}")

    # Final stats
    stats = memory.get_statistics()
    print(f"\nMemory Stats:")
    print(f"  Total conversations: {stats['total_conversations']}")
    print(f"  Total insights: {stats['total_insights']}")
    print(f"  Shared knowledge: {stats['shared_knowledge_count']}")

    return output


if __name__ == "__main__":
    run_orchestrated_analysis()
