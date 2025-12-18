#!/usr/bin/env python3
"""
ADVANCED EXAM BANK - Additional exploration tasks
Runs alongside continuous_exploration.py
"""

import requests
import json
import time
import os
from datetime import datetime

OLLAMA_URL = "http://localhost:11434/api/generate"

# Advanced exploration exams
ADVANCED_EXAMS = [
    # EXAM A1: k12 uniqueness investigation
    {
        "id": "exam_k12_uniqueness",
        "model": "qwq:32b",
        "prompt": """CRITICAL INVESTIGATION: WHY IS k12 UNIQUE?

k12 = 2683 has ONLY ONE formula in the entire search space:
    k12 = k8 × 12 - 5 = 224 × 12 - 5 = 2688 - 5 = 2683

All other keys have multiple formulas:
- k9=467 has 17 formulas
- k10=514 has 17 formulas
- k14=10544 has 15 formulas

QUESTIONS:
1. Is 2683 prime? Factor it completely.
2. What makes 2683 special mathematically?
3. Is there a relationship: k12 = f(12)? (index appears in formula)
4. k8×12 = 2688 = 2^7 × 21 = 2^7 × k5. Is this significant?
5. The offset -5 relates to what? k5=21, k4+k1=9...

CALCULATE:
- 2683 mod 7 = ?
- 2683 mod 11 = ?
- 2683 mod 13 = ?
- GCD(2683, k_i) for all i

Find what makes k12 mathematically SPECIAL."""
    },

    # EXAM A2: Ratio analysis between adjacent keys
    {
        "id": "exam_ratio_analysis",
        "model": "phi4-reasoning:14b",
        "prompt": """RATIO ANALYSIS BETWEEN ADJACENT KEYS

Calculate k_{n+1}/k_n for each pair:

k2/k1 = 3/1 = 3.000
k3/k2 = 7/3 = 2.333
k4/k3 = 8/7 = 1.143  <- ANOMALY (low ratio!)
k5/k4 = 21/8 = 2.625
k6/k5 = 49/21 = 2.333
k7/k6 = 76/49 = 1.551
k8/k7 = 224/76 = 2.947
k9/k8 = 467/224 = 2.085
k10/k9 = 514/467 = 1.101  <- ANOMALY (lowest ratio!)
k11/k10 = 1155/514 = 2.247
k12/k11 = 2683/1155 = 2.323
k13/k12 = 5216/2683 = 2.148
k14/k13 = 10544/5216 = 1.829

OBSERVATIONS:
1. k4/k3 and k10/k9 are ANOMALOUS (ratio < 1.2)
2. Most ratios are between 2.0 and 2.5
3. k4 = k3 + 1, k10 = k9 + 47

QUESTIONS:
1. Is there a pattern: anomalies at n=4, n=10, n=16?
2. Does ratio(n) follow a formula?
3. What predicts k15/k14? Should be ~1.55-2.5

Calculate expected k15 using ratio analysis."""
    },

    # EXAM A3: Divisibility chains
    {
        "id": "exam_divisibility_chains",
        "model": "qwq:32b",
        "prompt": """DIVISIBILITY CHAIN ANALYSIS

CHECK: Which keys divide which?

k1=1 divides all
k2=3: k5=21 divisible by 3 (21/3=7)
k3=7: k5=21 divisible by 7 (21/7=3), k6=49 divisible by 7
k4=8: k8=224 divisible by 8 (224/8=28)
k5=21: Does any larger key divide by 21?
k6=49: Does any larger key divide by 49?
k7=76: Does any larger key divide by 76?

CALCULATE:
k8/k2 = 224/3 = 74.67 (no)
k8/k4 = 224/8 = 28 (YES!)
k11/k3 = 1155/7 = 165 (YES!)
k11/k5 = 1155/21 = 55 (YES!)
k11/k11 = 1155/11 = 105 (YES by index!)
k12/k4 = 2683/8 = 335.375 (no)
k12/k2 = 2683/3 = 894.33 (no)

PATTERN: Keys divisible by their index?
k1/1 = 1, k4/4 = 2, k8/8 = 28, k11/11 = 105

Is k15/15 an integer? What does this predict?"""
    },

    # EXAM A4: Recurrence relation search
    {
        "id": "exam_recurrence_search",
        "model": "phi4-reasoning:14b",
        "prompt": """RECURRENCE RELATION SEARCH

Does k_n = f(k_{n-1}, k_{n-2}, ...) follow a pattern?

TRY: k_n = a*k_{n-1} + b*k_{n-2}

Test with k6, k7, k8:
k8 = a*k7 + b*k6
224 = a*76 + b*49
224 = 76a + 49b

Test with k7, k8, k9:
k9 = a*k8 + b*k7
467 = a*224 + b*76
467 = 224a + 76b

Solve system:
From first: 224 = 76a + 49b
From second: 467 = 224a + 76b

What are a, b? (May be non-integer)

ALSO TRY: k_n = a*k_{n-1} + b*k_{n-2} + c

If recurrence exists, predict k15, k16!"""
    },

    # EXAM A5: Three-key product formulas
    {
        "id": "exam_three_key_products",
        "model": "qwq:32b",
        "prompt": """THREE-KEY PRODUCT FORMULA SEARCH

We know two-key products:
- k5 = k2 × k3 = 3 × 7 = 21
- k10 = k3 × k7 - 18 = 7 × 76 - 18 = 514

Are there THREE-key products?

CALCULATE:
k2 × k3 × k4 = 3 × 7 × 8 = 168 (not a key)
k3 × k4 × k5 = 7 × 8 × 21 = 1176 ≈ k11=1155 (close!)
k4 × k5 × k6 = 8 × 21 × 49 = 8232 (not a key)

TRY: k_a × k_b × k_c ± C = k_n

k3 × k4 × k5 - 21 = 1176 - 21 = 1155 = k11! YES!
So: k11 = k3 × k4 × k5 - k5 = 7 × 8 × 21 - 21 = 1155

What other three-key formulas exist?

CHECK for k12, k13, k14:
k3 × k5 × k7 = 7 × 21 × 76 = 11172 (not k12, k13, k14)
k4 × k5 × k7 = 8 × 21 × 76 = 12768 (not a key)
k2 × k6 × k8 = 3 × 49 × 224 = 32928 (too big for k14)

Find three-key formulas!"""
    },

    # EXAM A6: Sum of previous keys
    {
        "id": "exam_sum_patterns",
        "model": "phi4-reasoning:14b",
        "prompt": """SUM PATTERNS IN KEYS

CALCULATE cumulative sums:
S1 = k1 = 1
S2 = k1 + k2 = 1 + 3 = 4
S3 = S2 + k3 = 4 + 7 = 11
S4 = S3 + k4 = 11 + 8 = 19
S5 = S4 + k5 = 19 + 21 = 40
S6 = S5 + k6 = 40 + 49 = 89
S7 = S6 + k7 = 89 + 76 = 165
S8 = S7 + k8 = 165 + 224 = 389
S9 = S8 + k9 = 389 + 467 = 856
S10 = S9 + k10 = 856 + 514 = 1370
S11 = S10 + k11 = 1370 + 1155 = 2525
S12 = S11 + k12 = 2525 + 2683 = 5208
S13 = S12 + k13 = 5208 + 5216 = 10973
S14 = S13 + k14 = 10973 + 10544 = 21517

QUESTIONS:
1. Is S_n related to k_{n+1}?
   S5 = 40, k6 = 49 (close!)
   S7 = 165, k8 = 224 (224 - 165 = 59)
   S10 = 1370, k11 = 1155 (S10 > k11!)

2. Any formula: k_n = S_{n-1} + C?

3. Is k15 ≈ S14 + C? What C?
   If k15 ≈ 21517 + C, and k15 ∈ [16384, 32767]
   Then C ∈ [-5133, 11250]

Find sum-based formulas!"""
    },

    # EXAM A7: Alternating pattern check
    {
        "id": "exam_alternating_patterns",
        "model": "qwq:32b",
        "prompt": """ALTERNATING PATTERN ANALYSIS

Separate keys by odd/even index:

ODD INDICES: k1=1, k3=7, k5=21, k7=76, k9=467, k11=1155, k13=5216
EVEN INDICES: k2=3, k4=8, k6=49, k8=224, k10=514, k12=2683, k14=10544

ODD sequence ratios:
k3/k1 = 7
k5/k3 = 3
k7/k5 = 3.62
k9/k7 = 6.14
k11/k9 = 2.47
k13/k11 = 4.99

EVEN sequence ratios:
k4/k2 = 2.67
k6/k4 = 6.125
k8/k6 = 4.57
k10/k8 = 2.29
k12/k10 = 5.22
k14/k12 = 3.93

QUESTIONS:
1. Do odd-indexed keys follow a different formula than even-indexed?
2. k15 (odd index) - what pattern applies?
3. k16 (even index) - what pattern applies?

Also check: odd indices have k_n = f(n) where n is odd
k1 = 1 = 1¹
k3 = 7 = ?
k5 = 21 = 3×7 = k2×k3
k7 = 76 = k2×9 + k6
k9 = 467 = ?
k11 = 1155 = k6×19 + k8
k13 = 5216 = ? (formula unknown)

Pattern for odd indices?"""
    },

    # EXAM A8: Digit sum analysis
    {
        "id": "exam_digit_sums",
        "model": "phi4-reasoning:14b",
        "prompt": """DIGIT SUM ANALYSIS (DIGITAL ROOT)

Calculate digit sums:
k1=1 → 1
k2=3 → 3
k3=7 → 7
k4=8 → 8
k5=21 → 2+1=3
k6=49 → 4+9=13 → 1+3=4
k7=76 → 7+6=13 → 1+3=4
k8=224 → 2+2+4=8
k9=467 → 4+6+7=17 → 1+7=8
k10=514 → 5+1+4=10 → 1+0=1
k11=1155 → 1+1+5+5=12 → 1+2=3
k12=2683 → 2+6+8+3=19 → 1+9=10 → 1
k13=5216 → 5+7+6+5=23 → 2+3=5
k14=10544 → 1+0+5+4+4=14 → 1+4=5

Digital roots: 1, 3, 7, 8, 3, 4, 4, 8, 8, 1, 3, 1, 5, 5

PATTERNS:
- Repeated 4s at k6, k7
- Repeated 8s at k8, k9
- Repeated 5s at k13, k14

QUESTIONS:
1. Is there a cycle in digital roots?
2. What should k15's digital root be?
3. Does digital root mod 9 reveal anything?

k_n mod 9:
k1=1, k2=3, k3=7, k4=8, k5=3, k6=4, k7=4, k8=8,
k9=8, k10=1, k11=3, k12=1, k13=5, k14=5

Next: k15 mod 9 = ?"""
    }
]

def stream_query(model, prompt, exam_id):
    """Query Ollama with streaming"""
    print(f"\n{'='*70}")
    print(f"ADVANCED EXAM: {exam_id}")
    print(f"Model: {model}")
    print(f"Started: {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*70}\n")

    full_response = ""
    start_time = time.time()

    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": model, "prompt": prompt, "stream": True},
            stream=True,
            timeout=None
        )

        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line)
                    token = data.get("response", "")
                    full_response += token
                    print(token, end="", flush=True)
                    if data.get("done"):
                        break
                except json.JSONDecodeError:
                    continue

    except Exception as e:
        print(f"\nError: {e}")
        return None, 0

    elapsed = time.time() - start_time
    print(f"\n\n{'='*70}")
    print(f"Completed: {datetime.now().strftime('%H:%M:%S')} ({elapsed:.1f}s)")
    print(f"Response: {len(full_response)} chars")
    print(f"{'='*70}")

    return full_response, elapsed

def save_result(exam_id, model, prompt, response, elapsed):
    """Save result to JSON file"""
    filename = f"/home/solo/LA/exam_results/advanced_{exam_id}_{datetime.now().strftime('%H%M%S')}.json"
    os.makedirs(os.path.dirname(filename), exist_ok=True)

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

def run_advanced_exams():
    """Run all advanced exams once"""
    print("="*70)
    print("ADVANCED EXAM BANK - STARTING")
    print(f"Total exams: {len(ADVANCED_EXAMS)}")
    print("="*70)

    for exam in ADVANCED_EXAMS:
        response, elapsed = stream_query(
            exam["model"],
            exam["prompt"],
            exam["id"]
        )

        if response:
            save_result(
                exam["id"],
                exam["model"],
                exam["prompt"],
                response,
                elapsed
            )

        # Brief pause between exams
        time.sleep(2)

    print(f"\n{'='*70}")
    print("ADVANCED EXAMS COMPLETE")
    print(f"{'='*70}")

if __name__ == "__main__":
    run_advanced_exams()
