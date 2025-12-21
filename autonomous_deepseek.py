#!/usr/bin/env python3
"""
Autonomous DeepSeek task dispatch - split into focused questions.
Let the 671B model think deeply without rushing.
"""
import subprocess
import os
import time
from datetime import datetime

TASKS = [
    {
        "id": "task1_prng_lcg",
        "prompt": """Analyze this sequence for LCG (Linear Congruential Generator) patterns:

k[1]=1, k[2]=3, k[3]=7, k[4]=8, k[5]=21, k[6]=49, k[7]=76, k[8]=224

LCG formula: X[n+1] = (a*X[n] + c) mod m

Can you find values of a, c, m that generate this sequence?
Show your mathematical reasoning step by step."""
    },
    {
        "id": "task2_recurrence",
        "prompt": """The sequence follows: k[n] = 2*k[n-1] + adj[n]

Where adj values are:
adj[2]=1, adj[3]=1, adj[4]=-6, adj[5]=5, adj[6]=7, adj[7]=-22, adj[8]=72

Find a formula for adj[n]. What mathematical structure produces these values?
Consider: Fibonacci, continued fractions, or modular arithmetic."""
    },
    {
        "id": "task3_m_sequence",  
        "prompt": """The m-sequence is defined by: m[n] = (2^n - adj[n]) / k[d[n]]

Known values:
m[4]=22, m[5]=9, m[6]=19, m[7]=50, m[8]=23, m[9]=493, m[10]=19

Note: m[4]=22 relates to π (22/7), m[6]=m[10]=19.
17 appears in factorizations: m[9]=17×29, m[11]=17×113, m[12]=17×73

What generates m[n]? Why does 17 appear so often?"""
    },
    {
        "id": "task4_direct_formula",
        "prompt": """Gap puzzles k[75], k[80], k[85], k[90] exist WITHOUT intermediate values.
This proves k[n] = f(n) for some direct formula.

k[70] = 970436974005023690481
k[75] = 22538323240989823823367
k[80] = 1105520030589234487939456

The ratio k[75]/k[70] = 23.22, k[80]/k[75] = 49.05

What direct formula k[n] = f(n) could produce these values?
Consider polynomial, exponential with modulation, or piecewise functions."""
    },
]

def run_task(task):
    """Run a single task with DeepSeek, no timeout."""
    task_id = task["id"]
    prompt = task["prompt"]
    output_file = f"/home/solo/ladder/result_{task_id}.txt"
    
    print(f"[{datetime.now()}] Starting {task_id}...")
    
    try:
        # Run without timeout - let it think
        result = subprocess.run(
            ['ollama', 'run', 'deepseek-v3.1:671b-cloud', prompt],
            capture_output=True,
            text=True,
            timeout=1800  # 30 minutes max
        )
        
        with open(output_file, 'w') as f:
            f.write(f"=== {task_id} ===\n")
            f.write(f"Timestamp: {datetime.now()}\n\n")
            f.write("=== PROMPT ===\n")
            f.write(prompt + "\n\n")
            f.write("=== RESPONSE ===\n")
            f.write(result.stdout if result.stdout else "No output")
            if result.stderr:
                f.write("\n\n=== STDERR ===\n")
                f.write(result.stderr)
        
        print(f"[{datetime.now()}] Completed {task_id} -> {output_file}")
        return True
        
    except subprocess.TimeoutExpired:
        print(f"[{datetime.now()}] {task_id} timed out after 30 min")
        return False
    except Exception as e:
        print(f"[{datetime.now()}] {task_id} error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("AUTONOMOUS DEEPSEEK TASK DISPATCH")
    print("Running focused tasks sequentially, letting model think deeply")
    print("=" * 60)
    print()
    
    for i, task in enumerate(TASKS):
        print(f"\n--- Task {i+1}/{len(TASKS)} ---")
        success = run_task(task)
        if success:
            print(f"Task completed. Pausing 10s before next...")
            time.sleep(10)
        else:
            print(f"Task failed, continuing to next...")
    
    print("\n" + "=" * 60)
    print("All tasks dispatched. Check result_*.txt files.")
    print("=" * 60)
