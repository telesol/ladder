#!/usr/bin/env python3
"""
WAVE 2 SWARM ATTACK - Refined Hypotheses Based on Wave 1 Discoveries

Wave 1 Key Discoveries:
1. 17-network has TWO PHASES: prime cofactors (9,11,12) vs composite (24,48,67)
2. Index differences contain m-values: 12-11=m[2], 67-48=m[6]
3. Nemotron's recursive formula was WRONG
4. Bootstrap phase: k[1-3] are Mersenne, then transition at n=4
5. Self-referential: m[7] = m[3]^2 + 1, m[8] = m[4] + 1
"""
import subprocess
import threading
import time
from datetime import datetime
import os
import json

# Create output directory
os.makedirs('/home/rkh/ladder/swarm_outputs/wave2', exist_ok=True)

# Load data for context
with open('/home/rkh/ladder/data_for_csolver.json', 'r') as f:
    data = json.load(f)
M_SEQ = data['m_seq'][:30]
D_SEQ = data['d_seq'][:30]

# Known 17-network data
NETWORK_17 = {
    9: {'m': 493, 'cofactor': 29, 'cofactor_prime_idx': 10},
    11: {'m': 1921, 'cofactor': 113, 'cofactor_prime_idx': 30},
    12: {'m': 1241, 'cofactor': 73, 'cofactor_prime_idx': 21},
    24: {'m': 1693268, 'cofactor': 99604, 'factors': '2^2 × 37 × 673'},
    48: {'m': 329601320238553, 'cofactor': 19388312955209, 'factors': '11 × 1762573905019'},
    67: {'m': 35869814695994276026, 'cofactor': 2109989099764369178, 'factors': '2 × 31 × 179 × 15053 × 12630264037'},
}

WAVE2_TASKS = {
    # Deep investigation of prime index pattern
    "qwen_prime_indices": {
        "model": "qwen2.5-coder:32b",
        "timeout": 600,
        "prompt": f"""PRIME INDEX PATTERN IN 17-NETWORK

For n=9,11,12 the cofactors of m[n]/17 are PRIME with these prime indices:
- n=9: cofactor 29 = p[10]
- n=11: cofactor 113 = p[30]
- n=12: cofactor 73 = p[21]

Prime indices: 10, 30, 21

QUESTIONS:
1. What's the relationship between n and the prime index?
2. Is there a formula: prime_index = f(n, previous_n, m[n])?
3. Test: prime_index = n + something?

Observations:
- 10 = 9 + 1
- 30 = 11 + 19 (19 = m[6]!)
- 21 = 12 + 9 (9 = first 17-network index!)

HYPOTHESIS: prime_index[t] = n[t] + n[t-k] for some k?

Write Python code to find the exact pattern."""
    },

    # Self-reference deep dive
    "mistral_self_ref": {
        "model": "mistral:7b",
        "timeout": 600,
        "prompt": f"""SELF-REFERENTIAL M-VALUE FORMULAS

Known self-referential formulas:
- m[7] = m[3]^2 + 1 = 49 + 1 = 50 ✓
- m[8] = m[4] + 1 = 22 + 1 = 23 ✓

Index differences in 17-network:
- 12 - 11 = 1 = m[2]
- 67 - 48 = 19 = m[6]

First 10 m-values: {M_SEQ[:10]}

QUESTIONS:
1. Can ALL m-values be expressed as functions of earlier m-values?
2. What operators are used? (+, -, ×, ^, mod?)
3. Is there a tree structure where m[n] = f(m[ancestors])?

Try to find formulas for m[9] through m[15]."""
    },

    # Two-phase transition
    "phi_phase_transition": {
        "model": "phi3:3.8b",
        "timeout": 300,
        "prompt": f"""TWO-PHASE 17-NETWORK TRANSITION

Phase 1 (n=9,11,12): Cofactors are PRIME
Phase 2 (n=24,48,67): Cofactors are COMPOSITE

Binary patterns:
- Phase 1: 1001, 1011, 1100 (irregular)
- Phase 2: 11000, 110000 (doubling + trailing zeros), then 1000011 (breaks)

The transition from Phase 1 to Phase 2 happens between n=12 and n=24.
Gap: 24 - 12 = 12 = 2 × 6 = 4 × 3

QUESTIONS:
1. Why does the cofactor structure change?
2. Is n=12 a critical threshold?
3. What's special about 12? (12 = 3 × 4 = 2^2 × 3)
4. How does this relate to Fermat prime 17 = 2^4 + 1?

Analyze the phase transition."""
    },

    # Continued fraction building blocks
    "qwen3_building": {
        "model": "qwen3:8b",
        "timeout": 300,
        "prompt": f"""BUILDING BLOCK HYPOTHESIS

Known building blocks from continued fractions:
- 22 = π convergent numerator (22/7)
- 19 = e convergent (19/7) or √3 (19/11)
- 7 = π convergent denominator (22/7)

m-values 2-10: {M_SEQ[:9]}

Self-referential building:
- m[7] = m[3]^2 + 1 = 7^2 + 1 = 50
- m[8] = m[4] + 1 = 22 + 1 = 23

TASK:
Try to express ALL of m[2]-m[10] using ONLY these operations on building blocks 1, 7, 19, 22:
- Addition (+)
- Multiplication (×)
- Power (^)
- Offset (+1, -1)

Can the building blocks reconstruct the sequence?"""
    },

    # Bootstrap to modulated transition
    "nemotron_bootstrap": {
        "model": "nemotron-3-nano:30b-cloud",
        "timeout": 900,
        "prompt": f"""BOOTSTRAP TO MODULATION TRANSITION

PROVEN:
- k[1] = 1 = 2^1 - 1 (Mersenne)
- k[2] = 3 = 2^2 - 1 (Mersenne)
- k[3] = 7 = 2^3 - 1 (Mersenne)
- k[4] = 8 = 2^3 (BREAKS pattern, = power of 2 exactly)

Bootstrap formula: k[n] = 2*k[n-1] + 1 works for n=1,2,3
At n=4: expected 15, got 8

The m-values:
- m[2] = m[3] = 1 (bootstrap)
- m[4] = 22 (π convergent - first non-trivial!)

d-values:
- d[2] = 2 (self-reference!)
- d[3] = 3 (self-reference!)
- d[4] = 1 (normal)

QUESTIONS:
1. What exactly triggers the transition at n=4?
2. Is there a "mode switch" where d changes from self-ref to normal?
3. Is 22 (π) specifically chosen to produce k[4] = 8 = 2^3?
4. Is the goal to hit powers of 2 at specific positions?

Derive the transition mechanism."""
    },

    # CM (Complex Multiplication) angle
    "deepseek_cm": {
        "model": "deepseek-r1:14b",
        "timeout": 1200,
        "prompt": f"""COMPLEX MULTIPLICATION (CM) HYPOTHESIS

The puzzle uses secp256k1 curve. We're investigating if the k-sequence
relates to CM (Complex Multiplication) theory of elliptic curves.

Known:
- secp256k1 has j-invariant 0 (supersingular-like properties)
- CM curves have special endomorphism rings
- 17 = 2^4 + 1 is a Fermat prime appearing as hidden factor

Key observations:
- 17-network indices: 9, 11, 12, 24, 48, 67
- Early cofactors are prime: 29, 113, 73
- Late cofactors are composite

QUESTIONS:
1. In CM theory, what role does 17 play for curves with j=0?
2. Could the prime cofactors 29, 113, 73 be related to class numbers?
3. Is there a CM interpretation of the bootstrap (Mersenne) phase?
4. How might isogeny degree relate to the index doubling (24, 48)?

This is worth millions if the CM angle is correct."""
    },
}

def run_task(name, config):
    """Run a single model task."""
    model = config["model"]
    prompt = config["prompt"]
    timeout = config["timeout"]
    output_file = f"/home/rkh/ladder/swarm_outputs/wave2/{name}_{datetime.now().strftime('%H%M%S')}.txt"

    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 Launching {name} ({model})...")

    try:
        start = time.time()
        result = subprocess.run(
            ['ollama', 'run', model, prompt],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        elapsed = time.time() - start

        with open(output_file, 'w') as f:
            f.write(f"=== {name.upper()} ===\n")
            f.write(f"Model: {model}\n")
            f.write(f"Elapsed: {elapsed:.1f}s\n")
            f.write(f"Timestamp: {datetime.now()}\n\n")
            f.write("=== RESPONSE ===\n")
            f.write(result.stdout if result.stdout else "No output")
            if result.stderr:
                f.write(f"\n\n=== STDERR ===\n{result.stderr[:500]}")

        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ {name} done ({elapsed:.1f}s) -> {output_file}")
        return True

    except subprocess.TimeoutExpired:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ⏰ {name} timeout after {timeout}s")
        return False
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ {name} error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("🌊 WAVE 2 SWARM ATTACK - Refined Hypotheses! 🌊")
    print(f"Launching {len(WAVE2_TASKS)} tasks based on Wave 1 discoveries")
    print("=" * 70)
    print()

    # Launch ALL tasks in parallel!
    threads = []
    for name, config in WAVE2_TASKS.items():
        t = threading.Thread(target=run_task, args=(name, config))
        t.start()
        threads.append((name, t))
        time.sleep(1)  # Brief stagger

    print(f"\n🚀 All {len(threads)} tasks launched! Waiting for completion...\n")

    # Monitor progress
    completed = 0
    while completed < len(threads):
        time.sleep(10)
        completed = sum(1 for _, t in threads if not t.is_alive())
        running = len(threads) - completed
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Progress: {completed}/{len(threads)} done, {running} running")

    # Wait for all
    for _, t in threads:
        t.join()

    print()
    print("=" * 70)
    print("🏁 WAVE 2 COMPLETE! Check swarm_outputs/wave2/ for results.")
    print("=" * 70)
