#!/usr/bin/env python3
"""
Wave 21 Phase 2: Cross-Review Synthesis
Models review each other's findings to find consensus.
"""

import subprocess
import os
from datetime import datetime

OUTPUT_DIR = "/home/rkh/ladder/swarm_outputs/wave21_collab"

# Phase 1 summaries for cross-review
PHASE1_SUMMARY = """
## PHASE 1 FINDINGS TO REVIEW

### STATISTICIAN FINDINGS:
- c[n] = k[n]/2^n has mean ~0.535 (slight upward bias)
- d[n] has weak negative correlation with n mod 8 (ρ ≈ -0.227)
- 60% of k[n] have NO trailing zeros
- Sequence balances structure and randomness

### CODER FINDINGS:
- d[n] prediction from n alone: FAILS (only 55% accuracy)
- Multiplicative structure LIMITED to k[4,5,6,8]
- k[4]=2^3*k[1], k[5]=k[2]*k[3], k[6]=k[3]^2, k[8]=2^5*k[3]
- Trailing zeros: 47.6% of keys are ODD

### CRITIC FINDINGS (Deepseek-r1):
- For n=4, naively d=3 gives smallest |m|=3.14, but actual d=1
- This suggests d-minimization has additional constraints
- Critic wrongly concluded k[n]=2^n-1 (fails at n=4)
- KEY INSIGHT: The d[n] values don't match simple |m| minimization

### CODE ANALYSIS RESULTS:
- Mod-based d[n] prediction: 55.2% accuracy
- Hamming-based d[n] prediction: 55.2% accuracy
- d[n] CANNOT be predicted from n properties alone
"""

SHARED_CONTEXT = """
## VERIFIED FACTS (Ground Truth)

### The Ladder Recurrence (100% verified n=2-70):
k[n] = 2*k[n-1] + 2^n - m[n]*k[d[n]]

### d-Minimization Rule (100% verified):
d[n] ALWAYS minimizes |m[n]| - but this requires knowing k[n] first!

### Bootstrap (Mersenne):
k[1]=1, k[2]=3, k[3]=7 (2^n - 1)

### First 20 Keys:
k: 1, 3, 7, 8, 21, 49, 76, 224, 467, 514, 1155, 2683, 5216, 10544, 26867, 51510, 95823, 198669, 357535, 863317

### d[n] for n=2-30:
d: 1,1,1,2,2,2,4,1,7,1,2,1,4,1,4,1,1,1,1,2,2,1,4,1,1,2,1,1,4

### THE PROBLEM:
Given k[1..n-1], infinitely many (d,m,k[n]) tuples satisfy the recurrence.
The ACTUAL k[n] satisfies d-minimization, but we can't find it without knowing k[n] first.
QUESTION: What property makes the ACTUAL k[n] special?
"""

REVIEW_PROMPT = SHARED_CONTEXT + PHASE1_SUMMARY + """

## YOUR TASK: CROSS-REVIEW SYNTHESIS

You've seen the findings from all Phase 1 specialists. Now:

1. **CONTRADICTIONS**: What findings conflict? How to resolve them?

2. **CONSENSUS**: What do ALL specialists agree on?

3. **KEY INSIGHT**: The critic found that naive d-minimization doesn't match.
   For n=4, choosing d=3 gives |m|=22/7≈3.14, but actual d[4]=1 gives |m|=22.
   WHY does the actual sequence use d=1 instead of d=3?

4. **THE MISSING CONSTRAINT**: What property could select k[n]?
   - NOT just from properties of n (coder proved 55% accuracy max)
   - NOT simple multiplicative (only works for k[4,5,6,8])
   - MUST produce natural trailing zeros (47.6% ODD)

5. **TESTABLE HYPOTHESIS**: Propose ONE specific test to run.

Be specific and mathematical. What is the ACTUAL construction method?
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
    return path


def main():
    print("="*70)
    print("WAVE 21 PHASE 2: CROSS-REVIEW SYNTHESIS")
    print("="*70)

    # Use two different models for cross-review
    reviewers = [
        ("nemotron:latest", 900),
        ("qwq:32b", 1200),
    ]

    for model, timeout in reviewers:
        print(f"\n>>> {model} reviewing all Phase 1 findings...")
        response = query(model, REVIEW_PROMPT, timeout)
        filepath = save(f"phase2_review_{model.replace(':','_')}", response)
        print(f"Saved: {filepath}")

        # Print preview
        lines = response.split('\n')
        print('\n'.join(lines[:40]))
        if len(lines) > 40:
            print(f"\n... [{len(lines)-40} more lines]")

    print("\n" + "="*70)
    print("Phase 2 complete. Synthesis saved.")


if __name__ == "__main__":
    main()
