#!/usr/bin/env python3
"""
CONTINUOUS FORMULA EXPLORATION - Non-stop orchestration
Runs B-Solver and C-Solver in parallel on different exploration tasks
Updated: Uses ALL 74 known keys from database
"""

import requests
import json
import time
import os
from datetime import datetime
import puzzle_config  # Central config - all data from DB

OLLAMA_URL = "http://localhost:11434/api/generate"

# Known keys for reference - loaded from DB
KEYS = puzzle_config.KEYS  # All 74 known keys

# Build key strings for prompts
LOW_KEYS = {k: v for k, v in KEYS.items() if k <= 20}
MID_KEYS = {k: v for k, v in KEYS.items() if 20 < k <= 65}
HIGH_KEYS = {k: v for k, v in KEYS.items() if k >= 66}

LOW_KEYS_STR = ", ".join([f"k{k}={v}" for k, v in sorted(LOW_KEYS.items())])
HIGH_KEYS_STR = ", ".join([f"k{k}={v}" for k, v in sorted(HIGH_KEYS.items())])

# EXAM BANK - Updated to use ALL 74 keys
EXAMS = [
    # EXAM 1: Full dataset ratio analysis
    {
        "id": "exam_full_ratio_analysis",
        "model": "qwq:32b",
        "prompt": f"""FULL DATASET RATIO ANALYSIS - 74 Known Keys

We have 74 keys: k1-k70 (consecutive) plus k75, k80, k85, k90.

LOW KEYS (k1-k20):
{LOW_KEYS_STR}

HIGH KEYS (k66-k70, k75, k80, k85, k90):
{HIGH_KEYS_STR}

TASK: Analyze ratios across the ENTIRE dataset.

1. Calculate k(n+1)/k(n) for all consecutive pairs from k1 to k70
2. Group by puzzle number mod 16 (the "lane" structure)
3. Do keys in the same lane share ratio patterns?
4. Compare low key ratios vs high key ratios

CRITICAL: Find patterns that hold across ALL 74 keys, not just k1-k14.

Show calculations."""
    },

    # EXAM 2: Bridge analysis k65 to k66
    {
        "id": "exam_bridge_k65_k66",
        "model": "phi4-reasoning:14b",
        "prompt": f"""BRIDGE ANALYSIS: k65 → k66

We have a complete sequence k1-k65, then k66-k70.

k65 = {KEYS.get(65, 'unknown')}
k66 = {KEYS.get(66, 'unknown')}

QUESTIONS:
1. What is the ratio k66/k65?
2. What is the expected ratio if purely exponential (should be ~2)?
3. What is the "position" of k65 and k66 in their respective bit ranges?
4. Does the formula pattern from k1-k14 extend to k65?

Check if verified formulas apply:
- k5 = k2 × k3 (products of earlier keys)
- k6 = k3² (squares)
- k8 = k5×13 - k6 (linear combinations)

Can similar patterns explain k65 or k66?"""
    },

    # EXAM 3: Lane-based analysis (mod 16)
    {
        "id": "exam_lane_analysis",
        "model": "qwq:32b",
        "prompt": f"""LANE ANALYSIS - Keys grouped by n mod 16

The puzzle has a "lane" structure based on n mod 16.

LANE 0 (n=16,32,48,64): k16={KEYS.get(16)}, k32={KEYS.get(32)}, k48={KEYS.get(48)}, k64={KEYS.get(64)}
LANE 1 (n=1,17,33,49,65): k1={KEYS.get(1)}, k17={KEYS.get(17)}, k33={KEYS.get(33)}, k49={KEYS.get(49)}, k65={KEYS.get(65)}
LANE 2 (n=2,18,34,50,66): k2={KEYS.get(2)}, k18={KEYS.get(18)}, k34={KEYS.get(34)}, k50={KEYS.get(50)}, k66={KEYS.get(66)}

TASK:
1. For each lane, calculate the ratio between consecutive members
2. Is there a consistent multiplier per lane?
3. Check the "A multiplier" hypothesis: k(n+16) = A * k(n) + C
4. Find A and C for each lane

This is critical for predicting unsolved keys."""
    },

    # EXAM 4: Recurrence relation search
    {
        "id": "exam_recurrence_search",
        "model": "phi4-reasoning:14b",
        "prompt": f"""RECURRENCE RELATION SEARCH

With 70 consecutive keys (k1-k70), we can test recurrence relations.

TEST: k(n) = a*k(n-1) + b*k(n-2) + c

Using k1-k5 to find a, b, c:
k3 = a*k2 + b*k1 + c → 7 = 3a + b + c
k4 = a*k3 + b*k2 + c → 8 = 7a + 3b + c
k5 = a*k4 + b*k3 + c → 21 = 8a + 7b + c

Solve this system. Then verify against k6-k70.

Also test:
- k(n) = a*k(n-1) + b*k(n-2) (no constant)
- k(n) = a*k(n-1) + b*n + c (index-dependent)
- k(n) = k(n-1) + k(n-2) + f(n) (Fibonacci-like with correction)

Find the formula that reproduces ALL 70 consecutive keys."""
    },

    # EXAM 5: PRNG reconstruction
    {
        "id": "exam_prng_reconstruction",
        "model": "qwq:32b",
        "prompt": f"""PRNG RECONSTRUCTION ATTEMPT

The puzzle creator likely used a deterministic method. Common PRNGs:
- Linear Congruential Generator: x(n+1) = (a*x(n) + c) mod m
- Xorshift
- Mersenne Twister
- BBS (Blum Blum Shub)

DATA: First 20 keys
{LOW_KEYS_STR}

TASK:
1. Test LCG: Can we find a, c, m such that k(n+1) = (a*k(n) + c) mod m?
2. Check differences: d(n) = k(n+1) - k(n). Is there a pattern?
3. Check second differences: d2(n) = d(n+1) - d(n)
4. Look for the seed value and generation parameters

If LCG, the formula would let us generate ALL keys from the seed."""
    },

    # EXAM 6: Position pattern analysis
    {
        "id": "exam_position_patterns",
        "model": "phi4-reasoning:14b",
        "prompt": f"""POSITION PATTERN ANALYSIS

Each key k(n) is in range [2^(n-1), 2^n - 1].
Position = (k(n) - 2^(n-1)) / (2^(n-1))

HIGH KEY POSITIONS:
k66 = {KEYS.get(66)} → position in 66-bit range
k67 = {KEYS.get(67)} → position in 67-bit range
k68 = {KEYS.get(68)} → position in 68-bit range
k69 = {KEYS.get(69)} → position in 69-bit range (was 0.72% - near minimum!)
k70 = {KEYS.get(70)} → position in 70-bit range

Calculate exact positions for k66-k70.

LOW KEY POSITIONS:
k1-k14 positions vary: k3=100% (max), k4=0% (min), k10=0.39%

QUESTION: Is there a pattern in positions?
- Do positions alternate high/low?
- Is position related to n mod something?
- Can we predict positions for unsolved keys?"""
    },

    # EXAM 7: GCD and divisibility patterns
    {
        "id": "exam_gcd_patterns",
        "model": "qwq:32b",
        "prompt": f"""GCD AND DIVISIBILITY ANALYSIS - Full Dataset

Known: k11 = 1155 = 3×5×7×11 (divisible by 11 = puzzle number!)

CHECK ALL 74 KEYS:
1. Is k(n) divisible by n? Check all.
2. Is k(n) divisible by small primes (2,3,5,7,11,13)?
3. Calculate GCD(k(n), k(m)) for various pairs
4. Look for common factors across keys

SPECIFIC CHECKS:
- GCD(k66, k67) = ?
- GCD(k69, 11) = ? (We know k69 is divisible by 11)
- Are there other keys divisible by their index?

LOW KEYS: {LOW_KEYS_STR}

This could reveal the underlying structure."""
    },

    # EXAM 8: Difference sequence analysis
    {
        "id": "exam_difference_sequences",
        "model": "phi4-reasoning:14b",
        "prompt": f"""DIFFERENCE SEQUENCE ANALYSIS

First differences: D1(n) = k(n+1) - k(n)
Second differences: D2(n) = D1(n+1) - D1(n)

Calculate D1 and D2 for k1-k20:

k1=1, k2=3, k3=7, k4=8, k5=21, k6=49, k7=76, k8=224,
k9=467, k10=514, k11=1155, k12=2683, k13=5216, k14=10544,
k15={KEYS.get(15)}, k16={KEYS.get(16)}, k17={KEYS.get(17)},
k18={KEYS.get(18)}, k19={KEYS.get(19)}, k20={KEYS.get(20)}

D1: 2, 4, 1, 13, 28, 27, 148, 243, 47, 641, ...

ANALYZE:
1. Is D1 sequence following a pattern?
2. Is D2 more regular than D1?
3. Do differences relate to puzzle index n?
4. Can we predict D1(70) = k71 - k70?

k70 = {KEYS.get(70)}
k71 range = [2^70, 2^71-1]"""
    }
]

def stream_query(model, prompt, exam_id):
    """Query Ollama with streaming"""
    print(f"\n{'='*70}")
    print(f"EXAM: {exam_id}")
    print(f"Model: {model}")
    print(f"Started: {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*70}\n")

    full_response = ""
    try:
        resp = requests.post(
            OLLAMA_URL,
            json={"model": model, "prompt": prompt, "stream": True},
            stream=True,
            timeout=None  # No timeout for deep reasoning
        )

        for line in resp.iter_lines():
            if line:
                try:
                    data = json.loads(line)
                    token = data.get("response", "")
                    full_response += token
                    print(token, end="", flush=True)
                    if data.get("done"):
                        break
                except json.JSONDecodeError:
                    pass

    except Exception as e:
        print(f"\nError: {e}")
        full_response = f"Error: {e}"

    elapsed = time.time()
    print(f"\n\n{'='*70}")
    print(f"Completed: {datetime.now().strftime('%H:%M:%S')}")
    print(f"Response length: {len(full_response)} chars")

    return full_response, elapsed

def save_result(exam_id, model, prompt, response, elapsed):
    """Save result to JSON file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"/home/solo/LA/exploration_{exam_id}_{timestamp}.json"

    with open(filename, 'w') as f:
        json.dump({
            "exam_id": exam_id,
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "prompt": prompt,
            "response": response,
            "elapsed_seconds": elapsed
        }, f, indent=2)

    print(f"Saved: {filename}")
    return filename

def run_continuous():
    """Run exams continuously"""
    print("="*70)
    print("CONTINUOUS FORMULA EXPLORATION - STARTING")
    print(f"Using {len(KEYS)} known keys from database")
    print(f"Total exams in bank: {len(EXAMS)}")
    print("="*70)

    cycle = 0
    while True:
        cycle += 1
        print(f"\n{'#'*70}")
        print(f"# CYCLE {cycle} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'#'*70}")

        for exam in EXAMS:
            response, elapsed = stream_query(
                exam["model"],
                exam["prompt"],
                exam["id"]
            )

            save_result(
                exam["id"],
                exam["model"],
                exam["prompt"],
                response,
                elapsed
            )

            # Brief pause between exams
            time.sleep(5)

        print(f"\nCycle {cycle} complete. Starting next cycle...")
        time.sleep(30)  # Pause between cycles

if __name__ == "__main__":
    run_continuous()
