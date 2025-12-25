#!/usr/bin/env python3
"""
Wave 20: Ladder Construction Algorithm Design
==============================================
Use local models to design the complete ladder generator.
Goal: Build the engine that produces ALL puzzle keys.
"""

import subprocess
import json
import os
from datetime import datetime

CONTEXT = """
# LADDER CONSTRUCTION: Design the Complete Generator

We have discovered most of the ladder formula. Your task: COMPLETE THE ALGORITHM.
The ladder formula IS the generator - no hidden seeds, no PRNG. Pure mathematics.

## VERIFIED COMPONENTS (Ground Truth)

### The Ladder Recurrence (100% verified for n=2 to n=70):
```
k[n] = 2*k[n-1] + 2^n - m[n]*k[d[n]]
```

### The Unified m-Formula (100% verified):
```
m[n] = (2^n - adj[n]) / k[d[n]]
where adj[n] = k[n] - 2*k[n-1]
```

### d-Minimization Rule (67/69 verified, 97%):
```
d[n] = argmin over all valid d of: m[n] = (2^n - adj[n]) / k[d]
```
Special cases: d[2]=2, d[3]=3 (bootstrap self-reference)

### Bootstrap (Mersenne Numbers):
```
k[1] = 1 = 2^1 - 1
k[2] = 3 = 2^2 - 1
k[3] = 7 = 2^3 - 1
```

### Transition at n=4:
```
k[4] = 8 = 2^3 (first power-of-2, not Mersenne)
adj[4] = k[4] - 2*k[3] = 8 - 14 = -6
d[4] = 1 (minimizes m[4])
m[4] = (2^4 - (-6)) / k[1] = 22
```

### ALL 82 Known Keys:
```python
KNOWN_KEYS = {
    1: 1, 2: 3, 3: 7, 4: 8, 5: 21, 6: 49, 7: 76, 8: 224, 9: 467, 10: 514,
    11: 1155, 12: 2683, 13: 5216, 14: 10544, 15: 26867, 16: 51510,
    17: 95823, 18: 198669, 19: 357535, 20: 863317,
    # ... continues to n=70 ...
    70: 970436974005023690481,
    75: 22538323240989823823367,
    80: 1105520030589234487939456,
    85: 21090315766411506144426920,
    90: 868012190417726402719548863,
    95: 25525831956644113617013748212,
    100: 868221233689326498340379183142,
    105: 29083230144918045706788529192435,
    110: 1090246098153987172547740458951748,
    115: 31464123230573852164273674364426950,
    120: 919343500840980333540511050618764323,
    125: 37650549717742544505774009877315221420,
    130: 1103873984953507439627945351144005829577
}
```

### Pattern Breaks (verified):
- n=17: adj[n] sign pattern breaks (was ++-++-..., becomes irregular)
- n=100: c[n] oscillation breaks (was DUDUDU, becomes UUDDUD)

### Multiplicative Structure (verified):
```
k[5] = k[2] * k[3] = 3 * 7 = 21
k[6] = k[3]^2 = 49
k[8] = 2^5 * k[3] = 32 * 7 = 224
k[11] = 3 * 5 * 7 * 11 = 1155
```

## THE MISSING PIECE

We can compute m[n] and d[n] FROM known keys, but we need to PREDICT them for UNKNOWN keys.

The challenge: Given k[1..n-1], how do we determine d[n] and m[n] to compute k[n]?

Current understanding:
- d[n] is chosen to minimize |m[n]|
- But this requires knowing k[n] first (circular!)
- There must be a FORWARD rule we haven't found

## YOUR TASK

Design the COMPLETE ladder construction algorithm:

1. **d[n] SELECTION RULE**: How is d[n] chosen BEFORE knowing k[n]?
   - Is it based on properties of n? (factors, primality, binary representation)
   - Is it based on properties of previous k-values?
   - Is there a deterministic formula?

2. **m[n] DETERMINATION**: Once d[n] is known, how is m[n] determined?
   - Is m[n] always the minimum possible?
   - Are there constraints on m[n]? (parity, divisibility, range)
   - How does m[n] relate to n or previous m-values?

3. **TRANSITION RULES**: What changes at n=4, n=17, n=100?
   - Different d-selection method?
   - Different m-constraints?
   - Different formula entirely?

4. **VERIFICATION**: Your algorithm must reproduce ALL 82 known keys exactly.

## THINK LIKE THE CREATOR

The puzzle was created in 2015. The creator needed a SIMPLE, DETERMINISTIC method.
- No external data (no hash of external strings)
- Pure mathematical construction
- Likely based on well-known number theory

Consider:
- Continued fractions and convergents
- Fibonacci/Lucas sequences
- Modular arithmetic patterns
- EC point multiplication properties
- Binary representation of n

## OUTPUT FORMAT

Provide a complete algorithm in pseudocode:
```
function generate_ladder(n_max):
    k[1] = 1
    k[2] = 3
    k[3] = 7

    for n = 4 to n_max:
        d[n] = <YOUR RULE HERE>
        m[n] = <YOUR RULE HERE>
        k[n] = 2*k[n-1] + 2^n - m[n]*k[d[n]]

    return k
```

Be SPECIFIC. Show the exact mathematical formulas.
Test your algorithm against known values and report accuracy.
"""

MODELS = [
    ("qwen3:8b", 600),
    ("phi4-reasoning:14b", 900),
    ("deepseek-r1:14b", 900),
    ("nemotron:latest", 900),
    ("qwq:32b", 1200)
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
    print("WAVE 20: LADDER CONSTRUCTION ALGORITHM DESIGN")
    print("Goal: Complete the generator that produces ALL puzzle keys")
    print("=" * 70)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"/home/rkh/ladder/swarm_outputs/wave20"
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
        preview = '\n'.join(lines[:50])
        if len(lines) > 50:
            preview += f"\n... [{len(lines) - 50} more lines]"
        print(preview)

    # Save synthesis
    synthesis = {
        'wave': 20,
        'focus': 'Ladder construction algorithm design',
        'goal': 'Complete the generator for ALL puzzle keys',
        'components_verified': [
            'Ladder recurrence: k[n] = 2*k[n-1] + 2^n - m[n]*k[d[n]]',
            'm-formula: m[n] = (2^n - adj[n]) / k[d[n]]',
            'd-minimization: 67/69 verified',
            'Bootstrap: k[1-3] = Mersenne numbers',
            'Transition: n=4 marks shift to iteration'
        ],
        'missing': 'd[n] selection rule for unknown keys',
        'responses': {k: v[:5000] for k, v in results.items()},
        'timestamp': timestamp
    }

    with open(f"{output_dir}/synthesis.json", 'w') as f:
        json.dump(synthesis, f, indent=2, default=str)

    print("\n" + "=" * 70)
    print(f"Results saved to {output_dir}/")
    print("=" * 70)


if __name__ == "__main__":
    main()
