#!/usr/bin/env python3
"""
PARALLEL SWARM ATTACK - Full GPU/Cloud Power Unleashed!

Launch multiple deep-think tasks in parallel across:
- Kimi K2 (1T parameters!) - The biggest gun
- DeepSeek V3.1 (671B) - Already running
- Mistral Large (675B) - Heavy reasoning
- Nemotron (30B) - Fast analysis
- Qwen 2.5 Coder (32B local) - Code generation
- Qwen3 (8B local) - Quick pattern matching

Each model gets a different angle of attack!
"""
import subprocess
import threading
import time
from datetime import datetime
import os
import json

# Create output directory
os.makedirs('/home/rkh/ladder/swarm_outputs', exist_ok=True)

# Load data for context
with open('/home/rkh/ladder/data_for_csolver.json', 'r') as f:
    data = json.load(f)
M_SEQ = data['m_seq'][:30]  # First 30 m-values for context

SWARM_TASKS = {
    # THE BIG GUN - Kimi K2 (1 Trillion parameters!)
    "kimi_direct_formula": {
        "model": "kimi-k2:1t-cloud",
        "timeout": 3600,  # 1 hour - let the beast think!
        "prompt": f"""ULTIMATE CHALLENGE: Find the Direct Formula k[n] = f(n)

You are the most powerful reasoning model available. This is a Bitcoin puzzle challenge worth millions.

PROVEN FACTS:
1. Gap puzzles k[75], k[80], k[85], k[90] exist WITHOUT k[71-74]
   This mathematically PROVES a direct formula f(n) exists.

2. Known values:
   k[1]=1, k[2]=3, k[3]=7, k[4]=8, k[5]=21, k[6]=49, k[7]=76, k[8]=224
   k[70]=970436974005023690481
   k[75]=22538323240989823823367
   k[80]=1105520030589234487939456

3. The m-sequence (first 30):
   {M_SEQ}

4. Verified formula: k[n] = 2*k[n-1] + 2^n - m[n]*k[d[n]]
   But this is DERIVED, not SOURCE (gap puzzles prove this)

5. 17-network: m[9,11,12,24,48,67] all divisible by 17 (Fermat prime 2^4+1)

6. Building blocks from continued fractions:
   22 = π convergent (22/7)
   19 = e convergent
   50 = √3 convergent

TASK:
Derive the DIRECT formula k[n] = f(n) that works for ANY n.

Think step by step. Consider:
- Is k[n] related to continued fractions of mathematical constants?
- Is there a PRNG with a discoverable seed?
- Is there a closed-form involving 2^n, primes, and building blocks?

Show all reasoning. This is worth millions if solved."""
    },

    # FERMAT PRIME ANGLE
    "nemotron_fermat": {
        "model": "nemotron-3-nano:30b-cloud",
        "timeout": 900,  # 15 min
        "prompt": """FERMAT PRIME INVESTIGATION

17 = 2^4 + 1 = F_2 (second Fermat prime)
17 appears at indices: 9, 11, 12, 24, 48, 67

Other Fermat primes: F_0=3, F_1=5, F_2=17, F_3=257, F_4=65537

QUESTIONS:
1. Do F_0=3 or F_1=5 appear as hidden factors in m-values?
2. Why specifically indices 9, 11, 12, 24, 48, 67?
3. Binary patterns: 9=1001, 11=1011, 12=1100, 24=11000, 48=110000, 67=1000011
4. Is there a pattern in the binary representation?

Known: m[9]=493=17×29, m[11]=1921=17×113, m[12]=1241=17×73

The cofactors 29, 113, 73 are ALL PRIME!
29 = p[10], 113 = p[30], 73 = p[21]

Formula discovered: m[n] = 17 × p[n + m[earlier]]

What determines "earlier"? What's the complete pattern?"""
    },

    # CONTINUED FRACTION DEEP DIVE
    "qwen_cf": {
        "model": "qwen2.5-coder:32b",
        "timeout": 600,  # 10 min
        "prompt": """CONTINUED FRACTION ANALYSIS

Building blocks in m-sequence:
- m[4] = 22 = numerator of π convergent 22/7
- m[6] = 19 = appears in e continued fraction
- m[7] = 50 = appears in √3 continued fraction
- m[8] = 23 = ?

π = [3; 7, 15, 1, 292, 1, 1, 1, 2, 1, 3, 1, 14, ...]
Convergents: 3/1, 22/7, 333/106, 355/113, ...

e = [2; 1, 2, 1, 1, 4, 1, 1, 6, 1, 1, 8, ...]
Convergents: 2/1, 3/1, 8/3, 11/4, 19/7, ...

√3 = [1; 1, 2, 1, 2, 1, 2, ...]
Convergents: 1/1, 2/1, 5/3, 7/4, 19/11, 26/15, 45/26, 71/41, ...
Wait: 19 appears! And 26, 45, 71...

TASK:
1. Map ALL m[2] through m[10] to continued fraction convergents
2. Which constants generate them? (π, e, √2, √3, φ, ln2?)
3. Is there a pattern in which convergent index is used?
4. Can we predict m[71] from continued fractions?

Write Python code to test this."""
    },

    # PRNG SEED SEARCH
    "qwen3_prng": {
        "model": "qwen3:8b",
        "timeout": 300,  # 5 min
        "prompt": """PRNG SEED SEARCH

k-sequence: 1, 3, 7, 8, 21, 49, 76, 224, 467, 514, 1155, 2683, 5216, 10544, 26867

This looks like it could come from a seeded PRNG.

Common PRNGs:
1. LCG: X[n+1] = (a*X[n] + c) mod m
2. LFSR: shift register with XOR feedback
3. Mersenne Twister: twisted GFSR
4. Xorshift: XOR with bit shifts

TASK:
Can you find parameters (a, c, m) for LCG that produces these first values?

Or find LFSR taps that match?

The sequence starts 1, 3, 7 which are 2^n - 1 (Mersenne numbers).
Then 8 = 2^3, which breaks the pattern.

What if seed = some hash of "Bitcoin puzzle"?

Think creatively about possible PRNG structures."""
    },

    # ISOGENY VOLCANO
    "mistral_isogeny": {
        "model": "mistral:7b",
        "timeout": 600,  # 10 min
        "prompt": """ISOGENY VOLCANO HYPOTHESIS

Previous analysis suggested 17-network might be a 17-isogeny graph.

In elliptic curve cryptography:
- Isogenies are morphisms between elliptic curves
- Isogeny graphs form "volcano" structures
- The crater level contains curves with the same endomorphism ring

17 is a prime, so there exist 17-isogenies between curves.

QUESTIONS:
1. If secp256k1 has a 17-isogeny to another curve, what's that curve?
2. Could the puzzle keys be generated by walking an isogeny graph?
3. The indices 9, 11, 12, 24, 48, 67 - do they correspond to steps in an isogeny walk?

Note: 24 = 2×12 and 48 = 2×24 (doubling pattern)
67 - 48 = 19 (m[6]!)

Is there a connection between isogeny degree and m-values?"""
    },

    # PHASE TRANSITION ANALYSIS
    "phi_phase": {
        "model": "phi3:3.8b",
        "timeout": 300,  # 5 min
        "prompt": """PHASE TRANSITION AT n=17

The sign pattern of adj[n] = k[n] - 2*k[n-1] follows ++- for n=2-16.
At n=17, this pattern BREAKS.

17 is special because:
- 17 = 2^4 + 1 (Fermat prime F_2)
- 17 = 2^16 + 1 has 2^16 = 65536 (16-bit boundary)
- k[17] = 95823 = 3^4 × 7 × 13^2 (highly structured!)

QUESTIONS:
1. Why does the algorithm change at exactly n=17?
2. Is 17 a "phase boundary" in the construction?
3. What about n=257 (next Fermat prime F_3)?
4. Could there be phase transitions at every Fermat prime?

The Bitcoin puzzle has 160 levels.
Fermat primes in range: 3, 5, 17, 257 (but 257 > 160)
So only F_0, F_1, F_2 matter.

What changes at these boundaries?"""
    },
}

def run_task(name, config):
    """Run a single model task."""
    model = config["model"]
    prompt = config["prompt"]
    timeout = config["timeout"]
    output_file = f"/home/rkh/ladder/swarm_outputs/{name}_{datetime.now().strftime('%H%M%S')}.txt"

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
    print("🔥 PARALLEL SWARM ATTACK - FULL POWER UNLEASHED! 🔥")
    print(f"Launching {len(SWARM_TASKS)} tasks across cloud + local models")
    print("=" * 70)
    print()

    # Launch ALL tasks in parallel!
    threads = []
    for name, config in SWARM_TASKS.items():
        t = threading.Thread(target=run_task, args=(name, config))
        t.start()
        threads.append((name, t))
        time.sleep(1)  # Brief stagger to prevent API collisions

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
    print("🏁 SWARM COMPLETE! Check swarm_outputs/ for results.")
    print("=" * 70)
