#!/usr/bin/env python3
"""
Wave 21: Local Model Academic Collaboration
============================================
Using reliable local models for peer-review discovery.
"""

import subprocess
import json
import os
from datetime import datetime

OUTPUT_DIR = "/home/rkh/ladder/swarm_outputs/wave21_collab"
os.makedirs(OUTPUT_DIR, exist_ok=True)

SHARED_DATA = """
## VERIFIED DATA

### Recurrence (100% verified n=2-70):
k[n] = 2*k[n-1] + 2^n - m[n]*k[d[n]]

### d-minimization (100% verified):
d[n] always minimizes |m[n]|

### Bootstrap:
k[1]=1, k[2]=3, k[3]=7 (Mersenne 2^n-1)

### First 20 keys:
n:  1  2  3   4   5   6   7    8    9   10    11    12    13     14     15     16      17      18      19      20
k:  1  3  7   8  21  49  76  224  467  514  1155  2683  5216  10544  26867  51510  95823  198669  357535  863317

### d[n] for n=2-30:
d: 1,1,1,2,2,2,4,1,7,1,2,1,4,1,4,1,1,1,1,2,2,1,4,1,1,2,1,1,4

### Multiplicative patterns:
k[4]=2^3, k[5]=k[2]*k[3], k[6]=k[3]^2, k[8]=2^5*k[3], k[11]=3*5*7*11

### THE PROBLEM:
Given k[1..n-1], infinitely many (d,m,k[n]) are valid.
ACTUAL k[n] satisfies d-minimization, but finding it requires knowing k[n] first.
QUESTION: What property selects the ACTUAL k[n]?
"""


def query(model: str, prompt: str, timeout: int = 300) -> str:
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


# ========== SPECIALIST PROMPTS ==========

MATH_PROMPT = SHARED_DATA + """
## ROLE: NUMBER THEORIST

Analyze the mathematical structure:
1. What determines d[n]? Look at when d=1 vs d=2 vs d=4 etc.
2. Is there a pattern in which n have simple multiplicative k[n]?
3. What's the growth rate? Eigenvalue structure?
4. Could continued fractions or Diophantine approximation be involved?

Propose specific mathematical hypotheses. Show derivations.
"""

STATS_PROMPT = SHARED_DATA + """
## ROLE: STATISTICIAN

Analyze patterns in the data:
1. Distribution of c[n] = k[n]/2^n - is it biased?
2. Correlation of d[n] with n mod 4, n mod 8, primality
3. Trailing zeros distribution in k[n]
4. How "random" vs "structured" is the sequence?

Provide specific statistical observations.
"""

CODE_PROMPT = SHARED_DATA + """
## ROLE: CODE GENERATOR

Write Python code to test hypotheses:

```python
# Load data
k = {1:1, 2:3, 3:7, 4:8, 5:21, 6:49, 7:76, 8:224, 9:467, 10:514,
     11:1155, 12:2683, 13:5216, 14:10544, 15:26867, 16:51510,
     17:95823, 18:198669, 19:357535, 20:863317}

# Your analysis code here
```

Test:
1. Can d[n] be predicted from properties of n alone?
2. Can k[n] be expressed as combinations of earlier k-values?
3. Binary representation patterns

Output COMPLETE runnable code.
"""

CRITIC_PROMPT = SHARED_DATA + """
## ROLE: DEVIL'S ADVOCATE

Challenge all assumptions:
1. Could k[n] be essentially random (hash/PRNG)?
2. What would DISPROVE a simple formula exists?
3. Is the multiplicative structure coincidental?
4. Minimum info needed to determine k[n]?

Be skeptical. Propose alternative explanations.
"""


def main():
    print("="*60)
    print("WAVE 21: LOCAL MODEL COLLABORATION")
    print("="*60)

    results = {}

    # Phase 1: Specialists
    tasks = [
        ("qwq:32b", "mathematician", MATH_PROMPT, 600),
        ("nemotron:latest", "statistician", STATS_PROMPT, 600),
        ("qwen2.5-coder:32b", "coder", CODE_PROMPT, 600),
        ("deepseek-r1:14b", "critic", CRITIC_PROMPT, 600),
    ]

    for model, role, prompt, timeout in tasks:
        print(f"\n>>> {role.upper()} ({model})...")
        resp = query(model, prompt, timeout)
        save(f"phase1_{role}", resp)
        results[role] = resp[:8000]
        print(resp[:1500] + "\n..." if len(resp) > 1500 else resp)

    # Save synthesis
    with open(f"{OUTPUT_DIR}/phase1_all.json", 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n{'='*60}")
    print(f"Results saved to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
