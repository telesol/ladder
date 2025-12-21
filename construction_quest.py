#!/usr/bin/env python3
"""
CONSTRUCTION QUEST - Understanding the Ladder Source
Not "what is k[71]?" but "what BUILDS the ladder?"
"""

import subprocess
import json
from datetime import datetime

# Cloud models for deep thinking
CLOUD_MODELS = [
    "deepseek-v3.1:671b-cloud",
    "nemotron-3-nano:30b-cloud"
]

# The fundamental question - CONSTRUCTION
CONSTRUCTION_PROMPTS = {
    "deepseek_construct": {
        "model": "deepseek-v3.1:671b-cloud",
        "prompt": """CONSTRUCTION PROBLEM - Build the Ladder

You have a sequence of 160 private keys k[1]...k[160] for Bitcoin addresses.
74 values are known (k[1]-k[70], k[75], k[80], k[85], k[90]).

KNOWN FACTS:
1. k[1]=1, k[2]=3, k[3]=7 (Mersenne-like: 2^n - 1)
2. k[4]=8=2^3 (exact power of 2)
3. k[5]=21=3×7, k[6]=49=7², k[8]=224=32×7
4. Recurrence exists: k[n] = 2*k[n-1] + adj[n]
5. m[n] = (2^n - adj[n]) / k[d[n]] where d[n] minimizes m[n]
6. Gap puzzles exist WITHOUT intermediate values

THE KEY INSIGHT:
Gap puzzles (75,80,85,90) exist without 71-74. This PROVES a direct formula.

CONSTRUCTION QUESTION:
If YOU were designing this puzzle, what mathematical generator would you use?

Consider:
1. PRNG: What seed + algorithm produces k[1..70]?
2. Continued Fractions: k[n] from convergents of what constant?
3. EC Operations: k[n] as scalar from what curve operation?
4. Modular: k[n] mod what hidden modulus?
5. Combinatorial: k[n] as C(f(n), g(n))?

Don't predict k[71]. CONSTRUCT the generator.
What MATH builds this ladder?""",
        "timeout": 1800
    },
    
    "nemotron_reverse": {
        "model": "nemotron-3-nano:30b-cloud",
        "prompt": """REVERSE ENGINEERING CHALLENGE

Known k-sequence (first 15 values):
k = [1, 3, 7, 8, 21, 49, 76, 224, 467, 514, 1155, 2683, 5216, 10544, 26867]

Properties observed:
- k[1,2,3] = 2^n - 1 (Mersenne numbers)
- k[4] = 2^3 (power of 2)
- k[5] = k[2] × k[3] = 3 × 7 = 21
- k[6] = k[3]² = 49
- k[8] = 32 × k[3] = 224

CHALLENGE: What SINGLE mathematical generator could produce ALL these values?

Think like the puzzle creator:
- Simple rule that produces complex output
- Must work for n=1 to n=160
- Must allow computing k[75] without k[71..74]

Propose a CONSTRUCTION formula, not a prediction.
Test your formula against k[1..15].""",
        "timeout": 900
    }
}

def run_model(model, prompt, timeout=600):
    """Run a model and return response"""
    try:
        result = subprocess.run(
            ["ollama", "run", model],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.stdout
    except subprocess.TimeoutExpired:
        return "TIMEOUT"
    except Exception as e:
        return f"ERROR: {e}"

def main():
    print("=" * 60)
    print("CONSTRUCTION QUEST - Understanding the Ladder Source")
    print("Not 'what is k[71]?' but 'what BUILDS the ladder?'")
    print("=" * 60)
    print()
    
    results = {}
    
    for task_id, config in CONSTRUCTION_PROMPTS.items():
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Launching {task_id}...")
        response = run_model(config["model"], config["prompt"], config.get("timeout", 600))
        
        # Save result
        result_file = f"/home/solo/ladder/result_construct_{task_id}.txt"
        with open(result_file, 'w') as f:
            f.write(f"=== {task_id} ===\n")
            f.write(f"Model: {config['model']}\n")
            f.write(f"Timestamp: {datetime.now()}\n\n")
            f.write("=== PROMPT ===\n")
            f.write(config["prompt"])
            f.write("\n\n=== RESPONSE ===\n")
            f.write(response)
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Completed {task_id}")
        print(f"  -> Saved to {result_file}")
        results[task_id] = result_file
    
    print()
    print("=" * 60)
    print("CONSTRUCTION QUEST COMPLETE")
    print("=" * 60)
    
    return results

if __name__ == "__main__":
    main()
