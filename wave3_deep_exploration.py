#!/usr/bin/env python3
"""
WAVE 3 DEEP EXPLORATION - Gap Puzzles and CM Theory

Key discoveries to build on:
1. Transition trigger: m[n] = d[n-1] × k[n-1] + 1 works for n=4,5
2. m[11] = 2^11 - 127 (Mersenne M_7)
3. 17-network uses j values from d[j]=2 set
4. CM angle: secp256k1 has j-invariant 0, supersingular properties
"""
import subprocess
import threading
import time
from datetime import datetime
import os
import json

os.makedirs('/home/rkh/ladder/swarm_outputs/wave3', exist_ok=True)

with open('/home/rkh/ladder/data_for_csolver.json', 'r') as f:
    data = json.load(f)
M_SEQ = data['m_seq']
D_SEQ = data['d_seq']

# Gap puzzle data (from MEMORY.md)
GAP_PUZZLES = {
    75: {'k': 22538323240989823823367, 'k_prev_gap': None},
    80: {'k': 1105520030589234487939456, 'k_70': 970436974005023690481},
    85: {'k': None, 'note': 'Unknown'},
    90: {'k': None, 'note': 'Unknown'},
}

WAVE3_TASKS = {
    # Gap puzzle offset analysis
    "qwen_gap_offset": {
        "model": "qwen2.5-coder:32b",
        "timeout": 600,
        "prompt": """GAP PUZZLE OFFSET ANALYSIS

Gap puzzles exist at n = 75, 80, 85, 90 WITHOUT intermediate k-values!
This PROVES a direct formula k[n] = f(n) must exist.

Known values:
- k[70] = 970436974005023690481
- k[75] = 22538323240989823823367
- k[80] = 1105520030589234487939456

Compute:
1. Ratio k[75]/k[70] and k[80]/k[75]
2. Expected ratio if pattern is 2^5 per 5 steps
3. Offset = actual - expected

The offset pattern might reveal the direct formula!

Write Python code to analyze these ratios and offsets."""
    },

    # d[j]=2 pattern deep dive
    "mistral_d2_pattern": {
        "model": "mistral:7b",
        "timeout": 600,
        "prompt": """D[J]=2 PATTERN ANALYSIS

In the 17-network, the prime index formula uses j where d[j]=2:
- n=9 uses j=2: prime_idx = 9 + m[2] = 9 + 1 = 10
- n=11 uses j=6: prime_idx = 11 + m[6] = 11 + 19 = 30
- n=12 uses j=5: prime_idx = 12 + m[5] = 12 + 9 = 21

d[j]=2 occurs at j = [2, 5, 6, 7, 12, 21, 22, 27, 36, 38...]

QUESTIONS:
1. Why is j=2 used for n=9, j=6 for n=11, j=5 for n=12?
2. The order is {2,6,5} not {2,5,6} - why the permutation?
3. What j-value would be used for n=24, 48, 67?
4. Is there a selection rule: j = f(n, previous_j)?

Derive the j-selection rule."""
    },

    # Mersenne subtraction pattern
    "phi_mersenne": {
        "model": "phi3:3.8b",
        "timeout": 300,
        "prompt": """MERSENNE SUBTRACTION PATTERN

Discovered pattern: m[n] = 2^n - M_k where M_k = 2^k - 1

Known matches:
- m[2] = 2^2 - (2^2-1) = 4 - 3 = 1
- m[3] = 2^3 - (2^3-1) = 8 - 7 = 1
- m[11] = 2^11 - (2^7-1) = 2048 - 127 = 1921

Notice: for m[2] and m[3], k=n (same exponent)
But for m[11], k=7 ≠ 11 (different exponent!)

QUESTIONS:
1. Why does m[11] use k=7 instead of k=11?
2. Is 7 special because k[3] = 7?
3. Are there other m[n] = 2^n - M_k patterns?
4. What determines which Mersenne to subtract?

Test m[12] through m[20] for this pattern."""
    },

    # Direct formula hypothesis
    "qwen3_direct": {
        "model": "qwen3:8b",
        "timeout": 300,
        "prompt": """DIRECT FORMULA HYPOTHESIS

The transition trigger formula works for n=4,5:
- m[4] = d[3] × k[3] + 1 = 3 × 7 + 1 = 22
- m[5] = d[4] × k[4] + 1 = 1 × 8 + 1 = 9

After n=5, the formula breaks.

HYPOTHESIS: There are MULTIPLE formulas that switch at boundaries.

Boundaries might be:
- Powers of 2 (4, 8, 16, 32...)
- Fermat primes (3, 5, 17, 257...)
- Fibonacci numbers (2, 3, 5, 8, 13...)

TASK:
1. What formula applies for n=6 to n=16?
2. Does a new formula start at n=17 (Fermat prime)?
3. Is the formula periodic or phase-based?

Build a piecewise formula hypothesis."""
    },

    # CM class number connection
    "deepseek_class": {
        "model": "deepseek-r1:14b",
        "timeout": 1200,
        "prompt": """CM CLASS NUMBER INVESTIGATION

Prime cofactors in 17-network: 29, 113, 73

In Complex Multiplication theory, class numbers of imaginary quadratic
fields determine curve properties.

QUESTIONS:
1. Are 29, 113, 73 class numbers of Q(sqrt(-D)) for some D?
2. Does secp256k1's CM field have class number involving these primes?
3. Is there a connection: 17 × prime_cofactor = m[n]?
4. Could the puzzle use CM-based key generation?

This could explain why certain primes appear as cofactors.
Investigate the algebraic number theory angle."""
    },

    # EC point multiplication pattern
    "nemotron_ec": {
        "model": "nemotron-3-nano:30b-cloud",
        "timeout": 900,
        "prompt": """EC POINT MULTIPLICATION PATTERN

The ladder formula: P[n] = 2*P[n-1] + 2^n*G - m[n]*P[d[n]]

This resembles double-and-add with subtraction correction.

Key insight: k[n] is the x-coordinate of P[n] = k[n]*G

QUESTIONS:
1. Can we express k[n] directly from the curve equation?
2. For secp256k1: y² = x³ + 7
3. If P[n] = (x_n, y_n), what's the pattern in x_n?
4. Does the m-sequence encode something about y-coordinates?

The gap puzzles suggest a closed-form exists.
Derive it from EC point arithmetic."""
    },
}

def run_task(name, config):
    model = config["model"]
    prompt = config["prompt"]
    timeout = config["timeout"]
    output_file = f"/home/rkh/ladder/swarm_outputs/wave3/{name}_{datetime.now().strftime('%H%M%S')}.txt"

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

        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ {name} done ({elapsed:.1f}s)")
        return True

    except subprocess.TimeoutExpired:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ⏰ {name} timeout")
        return False
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ {name} error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("🌊 WAVE 3 DEEP EXPLORATION - Gap Puzzles & CM Theory 🌊")
    print(f"Launching {len(WAVE3_TASKS)} tasks")
    print("=" * 70)
    print()

    threads = []
    for name, config in WAVE3_TASKS.items():
        t = threading.Thread(target=run_task, args=(name, config))
        t.start()
        threads.append((name, t))
        time.sleep(1)

    print(f"\n🚀 All {len(threads)} tasks launched!\n")

    completed = 0
    while completed < len(threads):
        time.sleep(10)
        completed = sum(1 for _, t in threads if not t.is_alive())
        running = len(threads) - completed
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Progress: {completed}/{len(threads)} done")

    for _, t in threads:
        t.join()

    print()
    print("=" * 70)
    print("🏁 WAVE 3 COMPLETE!")
    print("=" * 70)
