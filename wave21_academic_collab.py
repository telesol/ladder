#!/usr/bin/env python3
"""
Wave 21: Academic Collaboration Framework
==========================================
Multi-agent peer-review loop to discover the ladder construction algorithm.

Roles:
- CLOUD THEORISTS (kimi-k2:1t, mistral-large:675b, deepseek-v3.1:671b): Deep reasoning
- QWQ:32b - Mathematical structure specialist
- QWEN-CODER:32b - PySR symbolic regression code generator
- NEMOTRON:latest - Statistical analytics
- MISTRAL-LARGE:675b - Cross-checker and verifier
"""

import subprocess
import json
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

OUTPUT_DIR = "/home/rkh/ladder/swarm_outputs/wave21_collab"

# Shared context for all models
SHARED_CONTEXT = """
# BITCOIN PUZZLE LADDER: Academic Collaboration

## VERIFIED FACTS (Ground Truth)

### The Ladder Recurrence (100% verified for n=2 to n=70):
```
k[n] = 2*k[n-1] + 2^n - m[n]*k[d[n]]
```

### d-Minimization Rule (100% verified):
```
d[n] is ALWAYS chosen to minimize |m[n]|
```

### Bootstrap (Mersenne):
```
k[1] = 1 = 2^1 - 1
k[2] = 3 = 2^2 - 1
k[3] = 7 = 2^3 - 1
```

### Multiplicative Structure (verified):
```
k[4] = 2^3 * k[1] = 8
k[5] = k[2] * k[3] = 21
k[6] = k[3]^2 = 49
k[8] = 2^5 * k[3] = 224
k[11] = 3*5*7*11 = 1155
```

### First 20 Keys:
```
k[1]=1, k[2]=3, k[3]=7, k[4]=8, k[5]=21, k[6]=49, k[7]=76, k[8]=224,
k[9]=467, k[10]=514, k[11]=1155, k[12]=2683, k[13]=5216, k[14]=10544,
k[15]=26867, k[16]=51510, k[17]=95823, k[18]=198669, k[19]=357535, k[20]=863317
```

### The Problem:
- The recurrence DESCRIBES relationships but is UNDERDETERMINED for forward generation
- Given k[1..n-1], there are INFINITELY many valid (d, m, k[n]) tuples
- The ACTUAL k[n] satisfies d-minimization, but we can't find it without knowing k[n] first
- QUESTION: What property makes the ACTUAL k[n] values special among all valid candidates?

### Pattern Breaks:
- n=17: adj[n] sign pattern breaks (Fermat prime 2^4+1)
- n=100: c[n] oscillation pattern breaks (perfect square 10^2)

### Known d[n] sequence (n=2 to 30):
d = [1,1,1,2,2,2,4,1,7,1,2,1,4,1,4,1,1,1,1,2,2,1,4,1,1,2,1,1,4]
"""


def query_model(model_name: str, prompt: str, timeout: int = 600) -> str:
    """Query a single model."""
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


def save_report(model_name: str, role: str, content: str):
    """Save a model's report."""
    safe_name = model_name.replace(":", "_").replace("/", "_")
    filepath = f"{OUTPUT_DIR}/{role}_{safe_name}.txt"
    with open(filepath, 'w') as f:
        f.write(f"=== {model_name.upper()} - {role.upper()} ===\n")
        f.write(f"Time: {datetime.now().isoformat()}\n\n")
        f.write(content)
    print(f"  Saved: {filepath}")
    return filepath


# ============== PHASE 1: SPECIALIZED RESEARCH ==============

THEORIST_PROMPT = SHARED_CONTEXT + """

## YOUR ROLE: THEORETICAL PHYSICIST / NUMBER THEORIST

You are investigating what PROPERTY distinguishes the actual k[n] values from all other valid candidates.

THINK DEEPLY about:
1. What mathematical property could the puzzle creator have used to SELECT k[n]?
2. Why do some k[n] have simple multiplicative forms (k[5]=3*7) while others don't?
3. Is there a connection to elliptic curve cryptography (secp256k1)?
4. Could continued fractions, Diophantine approximation, or modular arithmetic be involved?
5. What's special about the prime k-values (k[9]=467, k[12]=2683)?

Propose 3-5 TESTABLE hypotheses about what makes actual k[n] special.
Be specific and mathematical. Show your reasoning.
"""

QWQ_MATH_PROMPT = SHARED_CONTEXT + """

## YOUR ROLE: PURE MATHEMATICIAN

Focus on the MATHEMATICAL STRUCTURE of the k-sequence.

Analyze:
1. The relationship between d[n] and properties of n (primes, powers, binary representation)
2. Why does d[n]=1 occur for 46% of values? What's common about those n?
3. The transition at n=4 from Mersenne to iterative - what changes algebraically?
4. Can you find a CLOSED FORM or GENERATING FUNCTION for the sequence?
5. What's the growth rate? Is it related to eigenvalues of some matrix?

Derive any mathematical relationships you can. Be rigorous.
"""

CODER_PROMPT = SHARED_CONTEXT + """

## YOUR ROLE: COMPUTATIONAL MATHEMATICIAN

Generate Python code using PySR (symbolic regression) to discover formulas.

Write code that:
1. Uses PySR to find symbolic expressions for d[n] as a function of n and previous values
2. Uses PySR to find expressions relating k[n] to previous k-values
3. Tests if k[n] can be expressed as simple combinations of earlier k-values
4. Searches for patterns in the binary representation of k[n]

Output COMPLETE, RUNNABLE Python code. Include:
- Data loading from the database
- PySR model fitting
- Analysis of discovered equations
- Verification against known values

Use: from pysr import PySRRegressor
"""

ANALYTICS_PROMPT = SHARED_CONTEXT + """

## YOUR ROLE: DATA SCIENTIST / STATISTICIAN

Perform statistical analysis on the k-sequence.

Analyze:
1. Distribution of k[n] / 2^(n-1) (position in range) - is it uniform? biased?
2. Correlation between d[n] and properties of n (mod 4, mod 8, primality, etc.)
3. Distribution of trailing zeros in k[n] - any pattern?
4. Autocorrelation in the d[n] sequence
5. Entropy analysis - how "random" does k[n] appear?

Provide specific statistical measures and what they suggest about the generation method.
"""

VERIFIER_PROMPT = SHARED_CONTEXT + """

## YOUR ROLE: PEER REVIEWER / DEVIL'S ADVOCATE

Your job is to CRITICALLY EVALUATE and find flaws.

Consider:
1. What evidence would DISPROVE that k[n] is generated by a simple formula?
2. Could k[n] simply be random values that happen to satisfy the recurrence?
3. What's the minimum information needed to uniquely determine k[n]?
4. Are there MULTIPLE valid solutions for each gap, or is the actual k[n] unique in some way?
5. Could the puzzle creator have used a PRNG or hash function?

Be skeptical. Challenge assumptions. Propose alternative explanations.
"""


def run_phase1():
    """Phase 1: Independent specialized research."""
    print("\n" + "="*70)
    print("PHASE 1: INDEPENDENT SPECIALIZED RESEARCH")
    print("="*70)

    tasks = [
        # Cloud theorists
        ("kimi-k2:1t-cloud", "theorist", THEORIST_PROMPT, 900),
        ("deepseek-v3.1:671b-cloud", "theorist", THEORIST_PROMPT, 900),

        # Local specialists
        ("qwq:32b", "mathematician", QWQ_MATH_PROMPT, 1200),
        ("qwen2.5-coder:32b", "coder", CODER_PROMPT, 900),
        ("nemotron:latest", "analyst", ANALYTICS_PROMPT, 900),

        # Verifier
        ("mistral-large-3:675b-cloud", "verifier", VERIFIER_PROMPT, 900),
    ]

    results = {}

    for model, role, prompt, timeout in tasks:
        print(f"\n>>> Querying {model} as {role}...")
        response = query_model(model, prompt, timeout)
        filepath = save_report(model, role, response)
        results[f"{role}_{model}"] = {
            "model": model,
            "role": role,
            "response": response[:10000],  # Truncate for JSON
            "filepath": filepath
        }

        # Print preview
        lines = response.split('\n')
        preview = '\n'.join(lines[:20])
        print(preview)
        if len(lines) > 20:
            print(f"... [{len(lines)-20} more lines]")

    return results


# ============== PHASE 2: PEER REVIEW ==============

def create_review_prompt(reports: dict) -> str:
    """Create a prompt for peer review."""
    summaries = []
    for key, data in reports.items():
        summary = f"### {data['role'].upper()} ({data['model']}):\n"
        summary += data['response'][:3000] + "\n...\n"
        summaries.append(summary)

    return SHARED_CONTEXT + """

## YOUR ROLE: PEER REVIEWER

Below are reports from your colleagues. Review them critically.

""" + "\n".join(summaries) + """

## YOUR TASK:
1. What are the STRONGEST insights from each report?
2. What CONTRADICTIONS exist between reports?
3. What CONSENSUS emerges about the generation method?
4. What experiments should we run to resolve disagreements?
5. What is the MOST LIKELY explanation for how k[n] is generated?

Synthesize the findings into actionable next steps.
"""


def run_phase2(phase1_results: dict):
    """Phase 2: Peer review of Phase 1 findings."""
    print("\n" + "="*70)
    print("PHASE 2: PEER REVIEW")
    print("="*70)

    review_prompt = create_review_prompt(phase1_results)

    # Have QWQ and Nemotron review
    reviewers = [
        ("qwq:32b", 1200),
        ("nemotron:latest", 900),
    ]

    review_results = {}

    for model, timeout in reviewers:
        print(f"\n>>> {model} reviewing all reports...")
        response = query_model(model, review_prompt, timeout)
        filepath = save_report(model, "reviewer", response)
        review_results[model] = {
            "response": response,
            "filepath": filepath
        }

        # Print preview
        lines = response.split('\n')
        print('\n'.join(lines[:30]))

    return review_results


def main():
    print("="*70)
    print("WAVE 21: ACADEMIC COLLABORATION FRAMEWORK")
    print("Multi-agent peer-review to discover ladder construction")
    print("="*70)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Phase 1
    phase1_results = run_phase1()

    # Save Phase 1 synthesis
    with open(f"{OUTPUT_DIR}/phase1_synthesis.json", 'w') as f:
        json.dump({k: {**v, 'response': v['response'][:5000]}
                   for k, v in phase1_results.items()}, f, indent=2)

    # Phase 2
    phase2_results = run_phase2(phase1_results)

    # Save Phase 2 synthesis
    with open(f"{OUTPUT_DIR}/phase2_synthesis.json", 'w') as f:
        json.dump(phase2_results, f, indent=2, default=str)

    print("\n" + "="*70)
    print(f"All reports saved to {OUTPUT_DIR}/")
    print("="*70)


if __name__ == "__main__":
    main()
