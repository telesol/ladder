#!/usr/bin/env python3
"""
PARALLEL ANALYSIS - Dispatch to multiple models simultaneously
"""
import subprocess
import os
from datetime import datetime
import threading
import queue

TASKS = [
    # CF Hypothesis
    {
        "id": "cf_analysis",
        "model": "qwen2.5:7b",
        "prompt": """CONTINUED FRACTION CONSTRUCTION HYPOTHESIS

k-sequence first 15: [1, 3, 7, 8, 21, 49, 76, 224, 467, 514, 1155, 2683, 5216, 10544, 26867]

OBSERVATION: k[1,2,4,5] are Fibonacci. Fibonacci = convergents of φ.

HYPOTHESIS: Each k[n] comes from continued fraction convergent of some constant.

Constants to check:
- φ = (1+√5)/2: convergents are Fibonacci
- π: convergents [3, 22/7, 333/106, 355/113...]
- e: convergents [2, 3, 8/3, 11/4, 19/7...]
- √2: convergents [1, 3/2, 7/5, 17/12...]
- √3: convergents [1, 2, 5/3, 7/4, 19/11...]

For each k[n], find which constant's convergent matches.
Build mapping: n → constant → convergent_index"""
    },
    
    # PRNG Hypothesis  
    {
        "id": "prng_analysis",
        "model": "phi3:mini",
        "prompt": """PRNG RECONSTRUCTION

k-sequence: [1, 3, 7, 8, 21, 49, 76, 224, 467, 514, 1155, 2683, 5216, 10544]

Test if this is output of PRNG:

1. LCG: x[n+1] = (a*x[n] + c) mod m
   - Try to find a, c, m that generate k[1..14]
   
2. LFSR: Linear Feedback Shift Register
   - Check XOR patterns between consecutive k values
   
3. Mersenne Twister seed
   - Could there be a seed that produces this?

4. Custom PRNG with Fibonacci state
   - k[n] = F(state[n]) where state evolves

Find the PRNG parameters if they exist."""
    },
    
    # EC Construction
    {
        "id": "ec_analysis", 
        "model": "gemma2:2b",
        "prompt": """ELLIPTIC CURVE CONSTRUCTION

k[n] are Bitcoin private keys on secp256k1.

Known formula: k[n] = 2*k[n-1] + adj[n]

This looks like EC point doubling!
P[n] = 2*P[n-1] + correction

HYPOTHESIS: k[n] is the x-coordinate of EC point P[n] where:
P[n] = n*G + f(n)*H for some function f and point H

Check:
1. Is k[n] = x(n*G) for generator G? NO - but maybe modified
2. Is there a pattern in k[n] mod p (secp256k1 prime)?
3. Do consecutive k values satisfy EC addition formulas?

Find the EC construction rule."""
    },
    
    # Gap puzzle analysis
    {
        "id": "gap_analysis",
        "model": "qwen2.5:3b", 
        "prompt": """GAP PUZZLE CONSTRUCTION

Gap puzzles: k[75], k[80], k[85], k[90] are known WITHOUT k[71-74].

k[70] = 970436974005023690481
k[75] = 22538323240989823823367
k[80] = 1105520030589234487939456
k[85] = 21077271849966862665561984
k[90] = 872954957

Wait, k[90] seems wrong. Let me recalculate.

QUESTION: What pattern connects gap puzzles?
- All are divisible by Fermat primes (3, 5, 17)?
- Same Fibonacci/Lucas construction applies?
- Is there f(n) that works for n=70,75,80,85,90?

Find the direct formula k[n] = f(n) that works for gap puzzles."""
    }
]

def run_model(task_id, model, prompt, results_queue):
    """Run a single model task"""
    try:
        result = subprocess.run(
            ["ollama", "run", model],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=180
        )
        response = result.stdout
        
        # Save to file
        filename = f"/home/solo/ladder/result_parallel_{task_id}.txt"
        with open(filename, 'w') as f:
            f.write(f"=== {task_id} ===\n")
            f.write(f"Model: {model}\n")
            f.write(f"Time: {datetime.now()}\n\n")
            f.write("=== RESPONSE ===\n")
            f.write(response)
        
        results_queue.put((task_id, "SUCCESS", filename))
    except subprocess.TimeoutExpired:
        results_queue.put((task_id, "TIMEOUT", None))
    except Exception as e:
        results_queue.put((task_id, f"ERROR: {e}", None))

def main():
    print("=" * 60)
    print("PARALLEL ANALYSIS - Launching 4 tasks simultaneously")
    print("=" * 60)
    print()
    
    results_queue = queue.Queue()
    threads = []
    
    for task in TASKS:
        print(f"[LAUNCH] {task['id']} on {task['model']}")
        t = threading.Thread(
            target=run_model,
            args=(task['id'], task['model'], task['prompt'], results_queue)
        )
        t.start()
        threads.append(t)
    
    print()
    print("Waiting for results...")
    print()
    
    # Wait for all threads
    for t in threads:
        t.join()
    
    # Collect results
    print("=" * 60)
    print("RESULTS")
    print("=" * 60)
    while not results_queue.empty():
        task_id, status, filename = results_queue.get()
        print(f"{task_id}: {status}")
        if filename:
            print(f"  -> {filename}")
    
    print()
    print("All parallel tasks complete!")

if __name__ == "__main__":
    main()
