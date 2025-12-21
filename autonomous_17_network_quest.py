#!/usr/bin/env python3
"""
Autonomous Deep-Think Quest: 17-Network & Direct Formula

Two critical questions:
1. How does the 17-network extend to large n?
2. Gap puzzles PROVE k[n] = f(n) exists - what is it?

Launch multiple models in parallel for deep exploration.
"""
import subprocess
import threading
import time
from datetime import datetime
import os

# Create output directory
os.makedirs('/home/rkh/ladder/quest_outputs', exist_ok=True)

TASKS = {
    "deepseek": {
        "model": "deepseek-v3.1:671b-cloud",
        "prompt": """CRITICAL MATH PUZZLE - Deep Reasoning Required

The Bitcoin puzzle uses a hidden formula k[n] = f(n).

PROVEN FACTS:
1. Gap puzzles (k[75], k[80], k[85], k[90]) exist WITHOUT k[71-74]
   This PROVES a DIRECT formula f(n) must exist

2. The 17-network pattern for n=9,11,12:
   m[9] = 17 × p[10]   where p[10] is the 10th prime
   m[11] = 17 × p[30]  where 30 = 11 + m[6] = 11 + 19
   m[12] = 17 × p[21]  where 21 = 12 + m[5] = 12 + 9

3. For n=24,48,67: m[n]/17 is COMPOSITE, not prime

4. Building blocks: m[4]=22 (π convergent), m[6]=19, m[7]=50, m[8]=23

QUESTION:
What direct formula f(n) could generate k[n] for ANY n?
The formula must work for both consecutive (n=1-70) and gap (n=75,80,85,90) puzzles.

Consider:
- Continued fraction convergents
- PRNG with known seed
- Piecewise functions with transitions
- Recursive relationships on m-values

Think deeply. Show step-by-step reasoning. What mathematical structure unifies these patterns?""",
        "timeout": 1800  # 30 min
    },

    "qwen": {
        "model": "qwen2.5-coder:32b",
        "prompt": """MATHEMATICAL DETECTIVE WORK

Puzzle sequence k[n] follows:
k[n] = 2*k[n-1] + 2^n - m[n]*k[d[n]]

BUT gap puzzles (k[75] without k[71-74]) prove this is DERIVED, not SOURCE.

17-NETWORK DISCOVERY:
For n=9,11,12: m[n] = 17 × prime(n + m[earlier])
- m[9] = 17 × p[9+1] = 17 × 29 = 493 ✓
- m[11] = 17 × p[11+19] = 17 × 113 = 1921 ✓
- m[12] = 17 × p[12+9] = 17 × 73 = 1241 ✓

For n=24,48,67: The cofactor m[n]/17 is composite.

TASK:
1. What determines which indices join the 17-network?
2. How does the formula change for large n?
3. What connects the building blocks 22, 19, 50, 23, 17?

These are continued fraction convergents of π, e, √3.
What underlying mathematical structure generates them?

Show your reasoning step by step.""",
        "timeout": 600  # 10 min
    },

    "mistral": {
        "model": "mistral-large-3:675b-cloud",
        "prompt": """EC LADDER CONSTRUCTION PUZZLE

The Bitcoin puzzle points P[n] = k[n] × G follow:
P[n] = 2*P[n-1] + 2^n × G - m[n] × P[d[n]]

d[n] distribution: d=1 (43.5%), d=2 (29%), d=3-8 (27.5%)

Gap offsets ALTERNATE:
k[75] - 32*k[70] = -8.78 × k[70] (NEGATIVE)
k[80] - 32*k[75] = +17.05 × k[75] (POSITIVE)
k[85] - 32*k[80] = -12.92 × k[80] (NEGATIVE)
k[90] - 32*k[85] = +9.16 × k[85] (POSITIVE)

The 17-network uses factor 17 (Fermat prime 2^4 + 1) at indices 9,11,12,24,48,67.

QUESTION:
What elliptic curve construction could produce this alternating pattern?
Is there a group-theoretic explanation for the 17-network?

Think about:
- EC point multiplication patterns
- Fermat prime significance (17 = F_2)
- Group order relationships

Show mathematical reasoning.""",
        "timeout": 1200  # 20 min
    }
}

def run_model(name, config):
    """Run a model task and save output."""
    model = config["model"]
    prompt = config["prompt"]
    timeout = config["timeout"]
    output_file = f"/home/rkh/ladder/quest_outputs/{name}_{datetime.now().strftime('%H%M%S')}.txt"

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Launching {name} ({model})...")

    try:
        result = subprocess.run(
            ['ollama', 'run', model, prompt],
            capture_output=True,
            text=True,
            timeout=timeout
        )

        with open(output_file, 'w') as f:
            f.write(f"=== {name.upper()} OUTPUT ===\n")
            f.write(f"Model: {model}\n")
            f.write(f"Timestamp: {datetime.now()}\n\n")
            f.write("=== PROMPT ===\n")
            f.write(prompt[:500] + "...\n\n")
            f.write("=== RESPONSE ===\n")
            f.write(result.stdout if result.stdout else "No output")
            if result.stderr:
                f.write(f"\n\n=== STDERR ===\n{result.stderr}")

        print(f"[{datetime.now().strftime('%H:%M:%S')}] {name} completed -> {output_file}")
        return output_file

    except subprocess.TimeoutExpired:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {name} timed out after {timeout}s")
        return None
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {name} error: {e}")
        return None

if __name__ == "__main__":
    print("=" * 70)
    print("AUTONOMOUS 17-NETWORK QUEST")
    print("Launching parallel deep-think agents")
    print("=" * 70)
    print()

    # Launch all models in parallel threads
    threads = []
    for name, config in TASKS.items():
        t = threading.Thread(target=run_model, args=(name, config))
        t.start()
        threads.append(t)
        time.sleep(2)  # Stagger launches

    # Wait for all to complete
    for t in threads:
        t.join()

    print()
    print("=" * 70)
    print("All agents completed. Check quest_outputs/ for results.")
    print("=" * 70)
