#!/usr/bin/env python3
"""
Autonomous Nemotron task dispatch - complementary to DeepSeek.
Focus on different aspects.
"""
import subprocess
import time
from datetime import datetime

TASKS = [
    {
        "id": "nem_binary",
        "prompt": """Binary pattern analysis of Bitcoin puzzle k-sequence:

k[1]=1 (binary: 1)
k[2]=3 (binary: 11)
k[3]=7 (binary: 111)
k[4]=8 (binary: 1000)
k[5]=21 (binary: 10101)
k[6]=49 (binary: 110001)
k[7]=76 (binary: 1001100)
k[8]=224 (binary: 11100000)

Observations:
- k[1,2,3] are all-ones (Mersenne: 2^n-1)
- k[4] = 2^3 (single bit)
- k[10] = 514 = 1000000010 (only 2 bits)

What bit manipulation formula could generate this? Look for XOR, shift, or mask patterns."""
    },
    {
        "id": "nem_d_pattern",
        "prompt": """The d[n] sequence determines which divisor minimizes m[n].

d-sequence for n=50-70:
[1, 3, 1, 1, 1, 1, 1, 5, 2, 1, 8, 2, 2, 1, 2, 5, 8, 2, 1, 5, 2]

Patterns found:
- d=1 appears 42.9% (most common)
- d=2 appears 28.6%
- For n ≡ 2 (mod 3): d=1 appears 71.4%

What determines d[n]? Is there a formula d[n] = g(n)?"""
    },
    {
        "id": "nem_constants",
        "prompt": """Mathematical constants in Bitcoin puzzle:

m[4] = 22 (π ≈ 22/7)
m[6] = 19 (√3 convergent)
k[2] = 3 (e ≈ 2.718...)
k[3] = 7 (π ≈ 22/7)

Prime 17 (Fermat prime 2^4+1) appears in:
- m[9] = 17 × 29
- m[11] = 17 × 113
- m[12] = 17 × 73
- Phase transition at n=17

How are these constants embedded? What's the connection to 17?"""
    },
]

def run_task(task):
    task_id = task["id"]
    prompt = task["prompt"]
    output_file = f"/home/solo/ladder/result_{task_id}.txt"
    
    print(f"[{datetime.now()}] Starting {task_id}...")
    
    try:
        result = subprocess.run(
            ['ollama', 'run', 'nemotron-3-nano:30b-cloud', prompt],
            capture_output=True,
            text=True,
            timeout=900  # 15 min for smaller model
        )
        
        with open(output_file, 'w') as f:
            f.write(f"=== {task_id} ===\n")
            f.write(f"Timestamp: {datetime.now()}\n\n")
            f.write("=== RESPONSE ===\n")
            f.write(result.stdout if result.stdout else "No output")
        
        print(f"[{datetime.now()}] Completed {task_id}")
        return True
        
    except Exception as e:
        print(f"[{datetime.now()}] {task_id} error: {e}")
        return False

if __name__ == "__main__":
    print("AUTONOMOUS NEMOTRON DISPATCH")
    for task in TASKS:
        run_task(task)
        time.sleep(5)
    print("Done.")
