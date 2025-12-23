#!/usr/bin/env python3
"""
Wave 18: Strategic Planning with Local Models
==============================================
Given the corrected 82-key dataset and pattern breaks, what's our best approach?
"""

import subprocess
import json
import os
from datetime import datetime

CONTEXT = """
# STRATEGIC PLANNING: What's Our Best Approach Now?

## Current Situation (CORRECTED DATA - December 2024)

### We Now Have 82 Solved Puzzles:
- k[1] to k[70]: All solved (consecutive)
- k[75], k[80], k[85], k[90]: Solved (gap anchors)
- k[95], k[100], k[105], k[110], k[115], k[120], k[125], k[130]: NEW! Just added!

### Critical Discovery: Pattern Break at n=100
The c[n] oscillation pattern we thought was perfect alternation is NOT:

```
Direction sequence (5-step intervals, 70→130):
  DUDUDUUUDDUD

Breakdown:
  n=70-100:  DUDUDU  (perfect DOWN-UP alternation)
  n=100-130: UUDDUD  (IRREGULAR - breaks at n=100!)
```

This is analogous to the adj[n] sign pattern breaking at n=17.

### The Underdetermination Problem
- Recurrence: k[n] = 2*k[n-1] + 2^n - m[n]*k[d[n]]
- Without constraints: 81,246+ valid candidates for k[71] alone
- The recurrence describes RELATIONSHIPS, not a GENERATOR
- We need the construction SEED or ALGORITHM

### What We Know Works:
1. d[n] minimization rule (67/69 verified for n≤70)
2. First 3 keys are Mersenne: k[1]=1, k[2]=3, k[3]=7
3. Multiplicative structure: k[5]=k[2]*k[3], k[6]=k[3]², k[8]=2⁵*k[3]
4. Pattern breaks at n=17 (Fermat prime) and n=100

### 12 Bounded Gaps to Solve:
| Gap | Range | Direction | Unknowns |
|-----|-------|-----------|----------|
| A | 70→75 | DOWN | k[71-74] |
| B | 75→80 | UP | k[76-79] |
| C | 80→85 | DOWN | k[81-84] |
| D | 85→90 | UP | k[86-89] |
| E | 90→95 | DOWN | k[91-94] |
| F | 95→100 | UP | k[96-99] |
| G | 100→105 | UP | k[101-104] ← Pattern break! |
| H | 105→110 | UP | k[106-109] |
| I | 110→115 | DOWN | k[111-114] |
| J | 115→120 | DOWN | k[116-119] |
| K | 120→125 | UP | k[121-124] |
| L | 125→130 | DOWN | k[126-129] |

Plus 30 unbounded puzzles: k[131] to k[160]

## Your Task: Strategic Planning

Given this corrected picture, answer these questions:

### 1. PRIORITY ORDERING
Which gaps should we attack first and why?
- Is Gap A (71-74) still the best target?
- Or should we focus on pattern break at n=100?
- What about the higher gaps with more anchor data?

### 2. PATTERN BREAK ANALYSIS
The pattern breaks at n=17 and n=100. What do these have in common?
- n=17 = 2^4 + 1 (Fermat prime)
- n=100 = 2^2 * 5^2 (not prime, but special?)
- What might n=17 and n=100 tell us about the construction?

### 3. CONSTRUCTION ALGORITHM
Given 82 data points, can we now reverse-engineer the seed?
- Hash-based: k[n] = hash(seed || n)?
- PRNG-based: k[n] = PRNG(seed, n)?
- Number-theoretic: continued fractions, Euclidean-like?

### 4. VERIFICATION APPROACH
With 82 known keys, we can:
- Test any proposed construction algorithm
- If it matches 82/82, high confidence it's correct
- What tests would you run?

### 5. RECOMMENDED NEXT STEPS
Give specific, actionable recommendations:
- What code should we write?
- What patterns should we search for?
- What external resources might help?

Be SPECIFIC. We need a concrete plan, not vague suggestions.
"""

MODELS = [
    ("qwen3:8b", 300),
    ("phi4-reasoning:14b", 600),
    ("deepseek-r1:14b", 600),
    ("nemotron:latest", 600),
    ("qwq:32b", 900)
]

def query_model(model_name: str, prompt: str, timeout: int = 600) -> str:
    try:
        result = subprocess.run(
            ["ollama", "run", model_name, prompt],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return f"[TIMEOUT after {timeout}s]"
    except Exception as e:
        return f"[ERROR: {str(e)}]"


def main():
    print("=" * 70)
    print("WAVE 18: STRATEGIC PLANNING")
    print("What's our best approach with the corrected 82-key dataset?")
    print("=" * 70)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"/home/rkh/ladder/swarm_outputs/wave18"
    os.makedirs(output_dir, exist_ok=True)

    results = {}

    for model, timeout in MODELS:
        print(f"\n{'=' * 60}")
        print(f"Querying: {model} (timeout: {timeout}s)")
        print(f"{'=' * 60}")

        response = query_model(model, CONTEXT, timeout=timeout)

        model_safe = model.replace(":", "_").replace("/", "_")
        with open(f"{output_dir}/{model_safe}.txt", 'w') as f:
            f.write(f"=== {model.upper()} ===\n")
            f.write(f"Time: {datetime.now().isoformat()}\n\n")
            f.write(response)

        results[model] = response

        lines = response.split('\n')
        preview = '\n'.join(lines[:30])
        if len(lines) > 30:
            preview += f"\n... [{len(lines) - 30} more lines]"
        print(preview)

    # Save synthesis
    synthesis = {
        'wave': 18,
        'focus': 'Strategic planning with corrected 82-key dataset',
        'key_questions': [
            'Priority ordering of gaps',
            'Pattern break analysis (n=17, n=100)',
            'Construction algorithm reverse-engineering',
            'Verification approach',
            'Recommended next steps'
        ],
        'responses': {k: v[:3000] for k, v in results.items()},
        'timestamp': timestamp
    }

    with open(f"{output_dir}/synthesis.json", 'w') as f:
        json.dump(synthesis, f, indent=2, default=str)

    print("\n" + "=" * 70)
    print(f"Results saved to {output_dir}/")
    print("=" * 70)


if __name__ == "__main__":
    main()
