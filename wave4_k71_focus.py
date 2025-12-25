#!/usr/bin/env python3
"""
WAVE 4 K[71] FOCUS - Deriving the unsolved puzzle

Key wave3 insights to use:
1. m-sequence encodes y-coordinate signs via cumulative parity
2. adj[n] = k[n] - 2*k[n-1] has ++- pattern breaking at n=17
3. Gap ratios (75/70=231.84, 80/75=48.99) are non-trivial

GOAL: Derive k[71] using adj pattern and unified formula
"""
import subprocess
import threading
import time
from datetime import datetime
import os
import json

os.makedirs('/home/rkh/ladder/swarm_outputs/wave4', exist_ok=True)

with open('/home/rkh/ladder/data_for_csolver.json', 'r') as f:
    data = json.load(f)
M_SEQ = data['m_seq']
D_SEQ = data['d_seq']
ADJ_SEQ = data['adj_seq']
K_BASE = data['k_base']

# Key data for agents
K_70 = 970436974005023690481
K_75 = 22538323240989823823367

WAVE4_TASKS = {
    # Derive adj[71] pattern
    "deepseek_adj71": {
        "model": "deepseek-r1:14b",
        "timeout": 600,
        "prompt": f"""ADJ[71] DERIVATION

The unified formula is: m[n] = (2^n - adj[n]) / k[d[n]]
Where adj[n] = k[n] - 2*k[n-1]

Known adj values (n=2 to n=31):
{ADJ_SEQ}

Known facts:
- adj[n] sign pattern is ++- for n=2-16 (15 matches)
- Pattern BREAKS at n=17
- k[70] = {K_70}
- k[75] = {K_75}

Questions:
1. What is the pattern in adj[n] for n > 31?
2. Derive adj[71] using the established patterns
3. What constraints does m[71] = (2^71 - adj[71]) / k[d[71]] give?
4. Using k[75]/k[70] ≈ 23.22 per step, estimate k[71]

Show all work. Use exact integer arithmetic."""
    },

    # Y-sign constraint analysis
    "qwen_ysign": {
        "model": "qwen2.5-coder:32b",
        "timeout": 600,
        "prompt": f"""Y-COORDINATE SIGN CONSTRAINTS

Key insight: m-sequence encodes y-coordinate signs!
y_n = ε_n * sqrt(x_n^3 + 7) where ε_n = (-1)^(Σm[i])

m-sequence (n=2 to n=20):
{M_SEQ[:19]}

Cumulative sum parity pattern:
n=2: Σm=1 → ε=-1
n=3: Σm=2 → ε=+1
n=4: Σm=24 → ε=+1
...

Questions:
1. What is Σm[2..70]? What is ε_70?
2. If ε_71 flips, m[71] must be ODD
3. If ε_71 stays same, m[71] must be EVEN
4. What constraint does this put on k[71]?

Write Python code to:
1. Compute cumulative sum and ε_n for n=2 to 70
2. Analyze the sign flip pattern
3. Derive constraint on m[71] parity"""
    },

    # Gap interpolation
    "nemotron_gap": {
        "model": "nemotron-3-nano:30b-cloud",
        "timeout": 600,
        "prompt": f"""GAP INTERPOLATION FOR k[71]

Gap puzzle values exist at n=70, 75, 80 (no intermediate k-values)
This suggests a polynomial or closed-form relationship.

Given:
- k[70] = {K_70}
- k[75] = {K_75}

The growth factor per 5 steps:
- k[75]/k[70] = 23.2196...

If k[n] follows pattern k[n] = a * 2^n + b * f(n):
1. What are a, b, f(n)?
2. Interpolate k[71] using polynomial fit
3. Verify: k[71] should satisfy m[71] = (2^71 - adj[71]) / k[d[71]]

Use Lagrange interpolation or polynomial regression.
SHOW THE DERIVED VALUE FOR k[71]."""
    },

    # Direct k[71] construction
    "phi_direct": {
        "model": "phi3:3.8b",
        "timeout": 300,
        "prompt": f"""DIRECT k[71] CONSTRUCTION

Known:
- k[70] = {K_70} = 0x{K_70:x}
- k[75] = {K_75} = 0x{K_75:x}

Binary analysis:
- k[70] has {K_70.bit_length()} bits
- k[75] has {K_75.bit_length()} bits
- k[71] should have ~71 bits

From the ladder recurrence k[n] = 2*k[n-1] + 2^n - m[n]*k[d[n]]:
1. What is the most likely d[71] value?
2. What m[71] value minimizes the result?
3. Compute k[71] = 2*k[70] + 2^71 - m[71]*k[d[71]]

Test: Does the derived k[71] produce valid Bitcoin address matching puzzle #71?"""
    },
}

def run_task(name, config, output_dir):
    """Run a single AI task."""
    start = time.time()
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 Launching {name} ({config['model']})...")

    cmd = [
        "ollama", "run", config["model"],
        config["prompt"]
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=config.get("timeout", 300)
        )

        output_file = f"{output_dir}/{name}_{datetime.now().strftime('%H%M%S')}.txt"
        with open(output_file, 'w') as f:
            f.write(f"=== {name.upper()} ===\n")
            f.write(f"Model: {config['model']}\n")
            f.write(f"Elapsed: {time.time()-start:.1f}s\n")
            f.write(f"Timestamp: {datetime.now()}\n\n")
            f.write("=== RESPONSE ===\n")
            f.write(result.stdout)
            if result.stderr:
                f.write("\n\n=== STDERR ===\n")
                f.write(result.stderr)

        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ {name} done ({time.time()-start:.1f}s)")
        return True

    except subprocess.TimeoutExpired:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ⏱️ {name} timed out")
        return False
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ {name} error: {e}")
        return False

def main():
    output_dir = '/home/rkh/ladder/swarm_outputs/wave4'
    log_file = f"{output_dir}_log.txt"

    print("=" * 70)
    print("🎯 WAVE 4 K[71] FOCUS - Deriving the unsolved puzzle 🎯")
    print(f"Launching {len(WAVE4_TASKS)} tasks")
    print("=" * 70)

    with open(log_file, 'w') as f:
        f.write("=" * 70 + "\n")
        f.write("🎯 WAVE 4 K[71] FOCUS 🎯\n")
        f.write(f"Launching {len(WAVE4_TASKS)} tasks\n")
        f.write("=" * 70 + "\n\n")

    threads = []
    for name, config in WAVE4_TASKS.items():
        t = threading.Thread(target=run_task, args=(name, config, output_dir))
        t.start()
        threads.append(t)
        time.sleep(1)  # Stagger launches

    print(f"\n🚀 All {len(WAVE4_TASKS)} tasks launched!\n")

    # Monitor progress
    done = 0
    while done < len(WAVE4_TASKS):
        time.sleep(10)
        current_done = sum(1 for t in threads if not t.is_alive())
        if current_done > done:
            done = current_done
            with open(log_file, 'a') as f:
                f.write(f"[{datetime.now().strftime('%H:%M:%S')}] Progress: {done}/{len(WAVE4_TASKS)} done\n")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Progress: {done}/{len(WAVE4_TASKS)} done")

    # Wait for all threads
    for t in threads:
        t.join()

    print("\n" + "=" * 70)
    print("🏁 WAVE 4 COMPLETE!")
    print("=" * 70)

    with open(log_file, 'a') as f:
        f.write("\n" + "=" * 70 + "\n")
        f.write("🏁 WAVE 4 COMPLETE!\n")
        f.write("=" * 70 + "\n")

if __name__ == "__main__":
    main()
