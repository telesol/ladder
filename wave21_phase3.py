#!/usr/bin/env python3
"""
Wave 21 Phase 3: Local Models Attack the Selection Mystery
What property selects the ACTUAL k[n] among infinitely many valid candidates?
"""

import subprocess
import os
from datetime import datetime

OUTPUT_DIR = "/home/rkh/ladder/swarm_outputs/wave21_collab"

BREAKTHROUGH_CONTEXT = """
## WAVE 21 BREAKTHROUGHS (Use These Facts)

### VERIFIED 100% (n=2-70):
1. Recurrence: k[n] = 2*k[n-1] + 2^n - m[n]*k[d[n]]
2. adj[n] = k[n] - 2*k[n-1]
3. m[n] = (2^n - adj[n]) / k[d[n]]  ← MUST BE INTEGER
4. d[n] minimizes |m[n]| among d where k[d] divides (2^n - adj[n])

### KEY INSIGHT:
- m[n] must be INTEGER (QWQ discovery)
- This restricts which d values are valid
- Among valid d's, pick minimal |m|

### THE UNSOLVED MYSTERY:
Given k[1..n-1], infinitely many k[n] satisfy the recurrence with some (d,m).
Each candidate k[n] has its own valid (d,m) pair.
What property SELECTS the actual k[n]?

### WHAT WE RULED OUT:
- NOT the smallest k[n] in [2^(n-1), 2^n) - fails for n≥5
- NOT the k[n] with globally smallest |m| - every n could have |m|=3 but doesn't
- NOT predictable from n alone - 55% max accuracy

### ACTUAL DATA (first 20):
n:   1   2   3    4    5    6    7     8     9    10     11     12     13      14      15      16       17       18       19       20
k:   1   3   7    8   21   49   76   224   467   514   1155   2683   5216   10544   26867   51510    95823   198669   357535   863317
d:   -   1   1    1    2    2    2     4     1     7      1      2      1       4       1       4        1        1        1        1
m:   -   3   7   22    9   19   50    23   493    19   1921   1241   8342    2034   26989    8470   138269   255121   564091   900329

### c[n] = k[n]/2^n (position in range):
Mean: 0.754, fairly uniform 0.5 to 0.99
"""

# Task 1: QWQ analyzes adj[n] sequence patterns
ADJ_ANALYSIS_PROMPT = BREAKTHROUGH_CONTEXT + """

## YOUR TASK: ANALYZE adj[n] SEQUENCE

The adj[n] values determine everything:
adj = [1, 1, -6, 5, 7, -22, 72, 19, -420, 127, 373, -150, 112, 5779, -2224, -7197, 7023, -39803, 148247]

Questions:
1. Is there a pattern in adj[n]? Sign pattern? Growth rate?
2. adj[n] = k[n] - 2*k[n-1]. What determines whether adj > 0 or adj < 0?
3. Can adj[n] be predicted from adj[1..n-1]?
4. If we knew adj[n], we could compute k[n] = 2*k[n-1] + adj[n]. So what determines adj[n]?

Look for:
- Periodicity
- Relationship to n (mod something)
- Relationship to previous adj values
- Mathematical structure (continued fractions, eigenvalues, etc.)

Be specific and mathematical. Derive relationships.
"""

# Task 2: Nemotron tests statistical hypotheses
STATS_HYPOTHESIS_PROMPT = BREAKTHROUGH_CONTEXT + """

## YOUR TASK: STATISTICAL HYPOTHESIS TESTING

Test these hypotheses about what selects k[n]:

H1: k[n] is chosen to maximize some entropy measure
H2: k[n] is the median of valid candidates (not smallest, not largest)
H3: k[n] minimizes deviation from some target ratio k[n]/k[n-1]
H4: k[n] is related to c[n-1] (position of previous key)

For each hypothesis:
1. State the mathematical formulation
2. How would you test it?
3. What data would support/refute it?

Also analyze:
- Autocorrelation of adj[n] sequence
- Distribution of k[n]/k[n-1] ratios
- Any clustering in c[n] values?

Provide specific statistical tests and what they suggest.
"""

# Task 3: Deepseek-r1 reasons about the construction
CONSTRUCTION_PROMPT = BREAKTHROUGH_CONTEXT + """

## YOUR TASK: THINK LIKE THE PUZZLE CREATOR

You created this puzzle in 2015. You needed to:
1. Generate 160 private keys deterministically
2. Each key k[n] must be in range [2^(n-1), 2^n)
3. The keys should satisfy the recurrence we discovered

HOW would you construct them?

Consider:
A) Start with a seed and use PRNG - but user says "no hidden seed"
B) Use a mathematical formula based only on n
C) Build iteratively from k[1..3] using some rule
D) Use cryptographic constants (π, e, curve parameters)

The recurrence k[n] = 2*k[n-1] + 2^n - m*k[d] is a DESCRIPTION.
What is the GENERATION method?

Key observations:
- k[1]=1, k[2]=3, k[3]=7 are Mersenne (2^n - 1)
- k[4]=8=2^3 breaks the Mersenne pattern
- k[5]=21=3*7=k[2]*k[3] (multiplicative!)
- k[6]=49=7^2=k[3]^2 (square!)
- k[8]=224=32*7=2^5*k[3]

Propose a CONSTRUCTION ALGORITHM that could generate these values.
"""

# Task 4: Coder generates test code
CODE_GENERATION_PROMPT = BREAKTHROUGH_CONTEXT + """

## YOUR TASK: GENERATE TEST CODE

Write Python code to test the following hypotheses:

1. **Continued Fraction Hypothesis**:
   Is adj[n] related to convergents of some irrational number?

2. **Eigenvalue Hypothesis**:
   The sequence might come from a linear recurrence with eigenvalues.
   Fit k[n] = A*λ1^n + B*λ2^n and find λ1, λ2.

3. **Multiplicative Build Hypothesis**:
   For each n, check if k[n] can be written as a product/power of earlier k values.
   Count how often this works.

4. **Binary Pattern Hypothesis**:
   Analyze Hamming weight of k[n]. Is there a pattern?

Output COMPLETE, RUNNABLE Python code with:
```python
import sqlite3
conn = sqlite3.connect('/home/rkh/ladder/db/kh.db')
# Load k values...
# Run tests...
# Print results...
```
"""


def query(model: str, prompt: str, timeout: int = 900) -> str:
    try:
        r = subprocess.run(["ollama", "run", model, prompt],
                          capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip()
    except subprocess.TimeoutExpired:
        return f"[TIMEOUT {timeout}s]"
    except Exception as e:
        return f"[ERROR: {e}]"


def save(name: str, content: str):
    path = f"{OUTPUT_DIR}/{name}.txt"
    with open(path, 'w') as f:
        f.write(f"=== {name.upper()} ===\nTime: {datetime.now()}\n\n{content}")
    print(f"Saved: {path}")
    return path


def main():
    print("="*70)
    print("WAVE 21 PHASE 3: ATTACK THE SELECTION MYSTERY")
    print("="*70)

    tasks = [
        ("qwq:32b", "phase3_adj_analysis", ADJ_ANALYSIS_PROMPT, 1200),
        ("nemotron:latest", "phase3_stats_hypothesis", STATS_HYPOTHESIS_PROMPT, 900),
        ("deepseek-r1:14b", "phase3_construction", CONSTRUCTION_PROMPT, 900),
        ("qwen2.5-coder:32b", "phase3_test_code", CODE_GENERATION_PROMPT, 600),
    ]

    for model, name, prompt, timeout in tasks:
        print(f"\n>>> {model}: {name}...")
        response = query(model, prompt, timeout)
        save(name, response)

        # Preview
        lines = response.split('\n')
        print('\n'.join(lines[:30]))
        if len(lines) > 30:
            print(f"\n... [{len(lines)-30} more lines]")

    print("\n" + "="*70)
    print("Phase 3 complete. Check outputs in", OUTPUT_DIR)


if __name__ == "__main__":
    main()
