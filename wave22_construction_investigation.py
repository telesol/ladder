#!/usr/bin/env python3
"""
Wave 22: Construction Investigation - Local AI Session

Orchestrator (Claude) has identified:
1. Bootstrap: k[1,2,3] = Mersenne (2^n - 1)
2. Multiplicative phase: n=4,5,6,8 built from previous
3. Prime resets: n=9,12 (primes 467, 2683)
4. Primorial: k[11] = 3×5×7×11
5. Coprime resets favor n ≡ 0 (mod 3)

MISSION FOR LOCAL MODELS:
Find what determines WHICH prime is chosen at reset positions.
- Why is k[9]=467 and not another prime in [256,511]?
- Why is k[12]=2683 and not another prime in [2048,4095]?
- Is there a pattern that lets us PREDICT the next prime?
"""

import subprocess
import sqlite3
import json
import time
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path("swarm_outputs/wave22_construction")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = Path("db/kh.db")

# Models optimized for this task
MODELS = {
    "mathematician": {
        "model": "qwq:32b",
        "timeout": 900,
        "role": "Number theorist specializing in prime selection and construction"
    },
    "pattern_finder": {
        "model": "deepseek-r1:14b",
        "timeout": 600,
        "role": "Pattern recognition specialist"
    },
    "coder": {
        "model": "qwen2.5-coder:32b",
        "timeout": 600,
        "role": "Hypothesis tester - write and run verification code"
    }
}

def load_data():
    """Load k values and compute derived sequences."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT puzzle_id, priv_hex FROM ground_truth WHERE priv_hex IS NOT NULL ORDER BY puzzle_id")
    rows = c.fetchall()
    conn.close()

    k = {pid: int(phex, 16) for pid, phex in rows}

    # Compute adj, m, d
    adj, m_vals, d_vals = {}, {}, {}
    for n in sorted(k.keys()):
        if n < 2 or (n-1) not in k:
            continue
        adj[n] = k[n] - 2 * k[n-1]
        numerator = (1 << n) - adj[n]
        best_d, best_m = 1, numerator
        for d in range(1, n):
            if d in k and k[d] and numerator % k[d] == 0:
                m = numerator // k[d]
                if abs(m) < abs(best_m):
                    best_m, best_d = m, d
        m_vals[n], d_vals[n] = best_m, best_d

    return k, adj, m_vals, d_vals

def get_primes_in_range(low, high):
    """Get all primes in range [low, high]."""
    def is_prime(n):
        if n < 2: return False
        if n == 2: return True
        if n % 2 == 0: return False
        for i in range(3, int(n**0.5) + 1, 2):
            if n % i == 0: return False
        return True
    return [p for p in range(low, high + 1) if is_prime(p)]

def build_prompt():
    """Build the investigation prompt."""
    k, adj, m_vals, d_vals = load_data()

    # Get primes in ranges for reset positions
    primes_9 = get_primes_in_range(256, 511)
    primes_12 = get_primes_in_range(2048, 4095)

    return f"""
BITCOIN PUZZLE CONSTRUCTION INVESTIGATION

== VERIFIED FACTS ==
k[1]=1, k[2]=3, k[3]=7 (Mersenne bootstrap: 2^n - 1)
k[4]=8=2³, k[5]=21=3×7, k[6]=49=7², k[8]=224=2⁵×7 (multiplicative)
k[9]=467 (PRIME, coprime with all previous)
k[11]=1155=3×5×7×11 (first 4 odd primes, primorial)
k[12]=2683 (PRIME, coprime with all previous)
k[15]=26867=67×401 (coprime with all previous, introduces new primes)

== THE MYSTERY ==
At "reset" positions (n=9, 12, 15...), k[n] is coprime with all previous.
For n=9: There are {len(primes_9)} primes in range [256,511].
  Actual k[9]=467. Why not 257, 263, 269, ... or 509?

For n=12: There are {len(primes_12)} primes in range [2048,4095].
  Actual k[12]=2683. Why not 2053, 2063, ... or 4093?

== RECURRENCE CONSTRAINT ==
k[n] = 2*k[n-1] + 2^n - m*k[d]
For k[9]: base = 2*224 + 512 = 960
  k[9] = 960 - m*k[d]
  Actual: 467 = 960 - 493*1 (d=1, m=493)

For k[12]: base = 2*2683 + 4096 = 5462... wait, that's wrong.
  Actually k[11]=1155, so base = 2*1155 + 4096 = 6406
  k[12] = 6406 - m*k[d]
  For k[12]=2683: 2683 = 6406 - m*k[d] → m*k[d] = 3723
  3723 = 3 × 1241, so d=2 (k[2]=3), m=1241 ✓

== YOUR MISSION ==
1. What pattern determines which prime is selected?
2. Is there a relationship between the prime and n?
3. Can we predict k[15] knowing it must be coprime?
4. Look at m values: m[9]=493, m[12]=1241. Pattern?

== KNOWN VALUES FOR REFERENCE ==
k values (n=1-20): {json.dumps({n: k[n] for n in range(1, 21) if n in k})}
adj values (n=2-20): {json.dumps({n: adj[n] for n in range(2, 21) if n in adj})}
m values (n=2-20): {json.dumps({n: m_vals[n] for n in range(2, 21) if n in m_vals})}
d values (n=2-20): {json.dumps({n: d_vals[n] for n in range(2, 21) if n in d_vals})}

== INSTRUCTIONS ==
Think step by step. Look for patterns in:
- The primes themselves (467, 2683)
- The m values at reset positions
- The relationship to previous k values
- Number theoretic properties (quadratic residues, etc.)

Mark findings with:
- "DISCOVERY:" for verified patterns
- "HYPOTHESIS:" for testable theories
- "TEST:" for code to verify
"""

def query_model(name, config, prompt):
    """Query a local model."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Querying {name}...")

    try:
        result = subprocess.run(
            ["ollama", "run", config["model"], f"{config['role']}\n\n{prompt}"],
            capture_output=True,
            text=True,
            timeout=config["timeout"]
        )

        response = result.stdout.strip()
        filename = OUTPUT_DIR / f"{name}_{datetime.now().strftime('%H%M%S')}.txt"
        with open(filename, "w") as f:
            f.write(f"=== {name.upper()} ===\n")
            f.write(f"Model: {config['model']}\n")
            f.write(f"Time: {datetime.now()}\n\n")
            f.write(response)

        print(f"  Completed ({len(response)} chars)")
        return response

    except subprocess.TimeoutExpired:
        print(f"  TIMEOUT after {config['timeout']}s")
        return None
    except Exception as e:
        print(f"  ERROR: {e}")
        return None

def run_investigation():
    """Run the investigation session."""
    print("="*60)
    print("WAVE 22: CONSTRUCTION INVESTIGATION")
    print("="*60)

    prompt = build_prompt()

    # Save prompt for reference
    with open(OUTPUT_DIR / "prompt.txt", "w") as f:
        f.write(prompt)

    print(f"\nPrompt saved to {OUTPUT_DIR}/prompt.txt")
    print(f"Starting model queries...\n")

    responses = {}
    for name, config in MODELS.items():
        responses[name] = query_model(name, config, prompt)
        time.sleep(2)

    # Extract findings
    print("\n" + "="*60)
    print("EXTRACTING FINDINGS")
    print("="*60)

    for name, response in responses.items():
        if not response:
            continue

        discoveries = []
        hypotheses = []

        for line in response.split('\n'):
            if 'DISCOVERY:' in line.upper():
                discoveries.append(line)
            if 'HYPOTHESIS:' in line.upper():
                hypotheses.append(line)

        if discoveries or hypotheses:
            print(f"\n{name}:")
            for d in discoveries[:3]:
                print(f"  {d[:100]}")
            for h in hypotheses[:3]:
                print(f"  {h[:100]}")

    print("\n" + "="*60)
    print(f"Session complete. Results in {OUTPUT_DIR}/")
    print("="*60)

if __name__ == "__main__":
    run_investigation()
