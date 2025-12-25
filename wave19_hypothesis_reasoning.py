#!/usr/bin/env python3
"""
Wave 19: Deep Reasoning About Construction Hypotheses
=====================================================
Have local models critically analyze and reason about our hypotheses.
"""

import subprocess
import json
import os
from datetime import datetime

CONTEXT = """
# DEEP REASONING: Validate or Refute Our Hypotheses

We have 82 solved Bitcoin puzzle keys. Based on analysis, we've formed several hypotheses.
Your task: CRITICALLY REASON about each hypothesis. Try to PROVE or DISPROVE it.

## THE DATA (Ground Truth)

### First 20 Keys (all verified):
```
k[1]  = 1
k[2]  = 3
k[3]  = 7
k[4]  = 8
k[5]  = 21
k[6]  = 49
k[7]  = 76
k[8]  = 224
k[9]  = 467
k[10] = 514
k[11] = 1155
k[12] = 2683
k[13] = 5216
k[14] = 10544
k[15] = 26867
k[16] = 51510
k[17] = 95823
k[18] = 198669
k[19] = 357535
k[20] = 863317
```

### Gap Puzzle Anchors (verified):
```
k[70]  = 970436974005023690481
k[75]  = 22538323240989823823367
k[80]  = 1105520030589234487939456
k[85]  = 21090315766411506144426920
k[90]  = 868012190417726402719548863
k[95]  = 25525831956644113617013748212
k[100] = 868221233689326498340379183142
k[105] = 29083230144918045706788529192435
k[110] = 1090246098153987172547740458951748
k[115] = 31464123230573852164273674364426950
k[120] = 919343500840980333540511050618764323
k[125] = 37650549717742544505774009877315221420
k[130] = 1103873984953507439627945351144005829577
```

### Known Recurrence Relation:
```
k[n] = 2*k[n-1] + 2^n - m[n]*k[d[n]]
```
Where d[n] is chosen to minimize m[n]. Verified for n=2 to n=70.

### Known Pattern Breaks:
- n=17: adj[n] sign pattern breaks (was ++-, becomes irregular)
- n=100: c[n] oscillation breaks (was DUDUDU, becomes UUDDUD)

---

## HYPOTHESES TO ANALYZE

### HYPOTHESIS 1: Mersenne Bootstrap
**Claim:** The first 3 keys are Mersenne numbers (2^n - 1).
```
k[1] = 1 = 2^1 - 1 ✓
k[2] = 3 = 2^2 - 1 ✓
k[3] = 7 = 2^3 - 1 ✓
```

**Questions:**
- Is this coincidence or intentional?
- Why would the puzzle creator use Mersenne numbers?
- Does this pattern extend in any way?

### HYPOTHESIS 2: Multiplicative Construction
**Claim:** Some keys are products of earlier keys.
```
k[5] = k[2] * k[3] = 3 * 7 = 21 ✓
k[6] = k[3]^2 = 7^2 = 49 ✓
k[8] = 2^5 * k[3] = 32 * 7 = 224 ✓
k[4] = 2^3 * k[1] = 8 * 1 = 8 ✓
```

**Questions:**
- Can ALL keys be expressed as products/powers of earlier keys?
- What about k[7] = 76? Is there a multiplicative formula?
- What about k[9] = 467 (prime)? How does it fit?
- Does this extend to higher keys?

### HYPOTHESIS 3: Transition at n=4
**Claim:** k[4] = 8 = 2^3 marks a transition from Mersenne to iterative.

**Questions:**
- Why 8 specifically?
- Is k[4] = 2^3 significant (first power-of-2 that's not Mersenne)?
- What changes at n=4 in the recurrence?

### HYPOTHESIS 4: Pattern Breaks are Algorithmic Transitions
**Claim:** Breaks at n=17 and n=100 indicate algorithm changes.
- n=17 = 2^4 + 1 (Fermat prime)
- n=100 = 10^2 (perfect square)

**Questions:**
- Is there a mathematical reason these numbers are special?
- What might change in the algorithm at these points?
- Are there other transition points we haven't found?

### HYPOTHESIS 5: Recurrence Describes, Doesn't Generate
**Claim:** The recurrence relation describes relationships between keys but doesn't uniquely determine them. The actual generation uses a different method (seed, PRNG, hash).

**Questions:**
- If true, what IS the generation method?
- How would we find the seed?
- Can we test this hypothesis?

---

## YOUR TASK

For each hypothesis:

1. **ANALYZE**: What evidence supports or contradicts it?
2. **EXTEND**: If true, what else would we expect to see?
3. **TEST**: How could we verify or falsify this hypothesis?
4. **CONCLUDE**: Is the hypothesis likely TRUE, FALSE, or UNCERTAIN?

Also consider:
- Are there ALTERNATIVE hypotheses we haven't considered?
- What's the SIMPLEST explanation that fits all data?
- What would the puzzle creator's MOTIVATION be?

Be rigorous. Show your reasoning. Don't just agree - CHALLENGE the hypotheses.
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
    print("WAVE 19: HYPOTHESIS REASONING")
    print("Critical analysis of our construction hypotheses")
    print("=" * 70)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"/home/rkh/ladder/swarm_outputs/wave19"
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
        preview = '\n'.join(lines[:35])
        if len(lines) > 35:
            preview += f"\n... [{len(lines) - 35} more lines]"
        print(preview)

    # Save synthesis
    synthesis = {
        'wave': 19,
        'focus': 'Critical reasoning about construction hypotheses',
        'hypotheses': [
            'Mersenne bootstrap (k[1-3] = 2^n - 1)',
            'Multiplicative construction',
            'Transition at n=4',
            'Pattern breaks are algorithmic transitions',
            'Recurrence describes but doesn\'t generate'
        ],
        'responses': {k: v[:4000] for k, v in results.items()},
        'timestamp': timestamp
    }

    with open(f"{output_dir}/synthesis.json", 'w') as f:
        json.dump(synthesis, f, indent=2, default=str)

    print("\n" + "=" * 70)
    print(f"Results saved to {output_dir}/")
    print("=" * 70)


if __name__ == "__main__":
    main()
