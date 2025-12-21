#!/usr/bin/env python3
"""
Autonomous Local GPU Models - Complementary to Cloud Models
Running on RTX 4060 8GB while cloud models do heavy lifting.
"""
import subprocess
import time
from datetime import datetime

# Local mini models (fit in 8GB VRAM)
TASKS = [
    {
        "model": "phi3:mini",
        "id": "phi3_17network",
        "prompt": """The 17-NETWORK pattern in Bitcoin puzzle:

VERIFIED:
- m[9] = 17 × 29 = 493 (29 is 10th prime, and 9+1=10)
- m[11] = 17 × 113 = 1921 (113 is 30th prime, and 11+19=30)
- m[12] = 17 × 73 = 1241 (73 is 21st prime, and 12+9=21)

Pattern: m[n] = 17 × prime(n + m[earlier])

Question: What determines "earlier"? For n=9: earlier=2 (m[2]=1), n=11: earlier=6 (m[6]=19), n=12: earlier=5 (m[5]=9).

Find the rule that selects which earlier index to use."""
    },
    {
        "model": "qwen2.5:3b",
        "id": "qwen_modular",
        "prompt": """m-sequence modular structure:

Known m-values: m[4]=22, m[5]=9, m[6]=19, m[7]=50, m[8]=23, m[9]=493, m[10]=19

Observations:
- m[4]=22 ≈ 22/7 × 7 (π convergent)
- m[6]=m[10]=19 (repeat!)
- m[8]+m[2] = 23+1 = 24 = 4!

Look for modular arithmetic patterns.
What is m[n] mod 17? mod 19? mod 23?
Find any recurring cycle or structure."""
    },
    {
        "model": "gemma2:2b",
        "id": "gemma_position",
        "prompt": """Position anomaly analysis in Bitcoin puzzle:

Keys near minimum of their range:
- k[4] = 8, position 0.00% (exactly at minimum 2^3)
- k[10] = 514, position 0.39%
- k[69] = solved FAST, position 0.72%

These "anchored" keys are at specific positions.

Question: What mathematical property causes certain k[n] to be near 2^(n-1)?
Is there a formula for which n values have this property?"""
    },
]

def run_task(task):
    model = task["model"]
    task_id = task["id"]
    prompt = task["prompt"]
    output_file = f"/home/solo/ladder/result_local_{task_id}.txt"

    print(f"[{datetime.now()}] Starting {task_id} on {model}...")

    try:
        result = subprocess.run(
            ['ollama', 'run', model, prompt],
            capture_output=True,
            text=True,
            timeout=300  # 5 min for small models
        )

        with open(output_file, 'w') as f:
            f.write(f"=== {task_id} ===\n")
            f.write(f"Model: {model}\n")
            f.write(f"Timestamp: {datetime.now()}\n\n")
            f.write("=== PROMPT ===\n")
            f.write(prompt + "\n\n")
            f.write("=== RESPONSE ===\n")
            f.write(result.stdout if result.stdout else "No output")

        print(f"[{datetime.now()}] Completed {task_id} -> {output_file}")
        return True

    except subprocess.TimeoutExpired:
        print(f"[{datetime.now()}] {task_id} timed out")
        return False
    except Exception as e:
        print(f"[{datetime.now()}] {task_id} error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("AUTONOMOUS LOCAL GPU DISPATCH")
    print("Models: phi3:mini, qwen2.5:3b, gemma2:2b")
    print("GPU: RTX 4060 8GB (local)")
    print("=" * 60)
    print()

    for i, task in enumerate(TASKS):
        print(f"\n--- Task {i+1}/{len(TASKS)} ---")
        success = run_task(task)
        if success:
            print(f"Task completed. Pausing 3s...")
            time.sleep(3)

    print("\n" + "=" * 60)
    print("All local tasks complete. Check result_local_*.txt files.")
    print("=" * 60)
