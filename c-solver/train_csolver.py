#!/usr/bin/env python3
"""
C-Solver Training Script
Model: qwq:32b (Alibaba QwQ - 19GB reasoning model)
Focus: Prediction, Synthesis, Advanced Reasoning
Target: 8/10 certification
"""
import requests
import json
import time
import sys
from datetime import datetime

MODEL = "qwq:32b"
TIMEOUT = 300  # QwQ needs time for step-by-step reasoning

def ask_ollama(prompt, timeout=TIMEOUT):
    """Ask QwQ with appropriate timeout"""
    try:
        resp = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": MODEL, "prompt": prompt, "stream": False},
            timeout=timeout
        )
        if resp.status_code == 200:
            return resp.json().get("response", "")
        return f"Error: {resp.status_code}"
    except requests.exceptions.Timeout:
        return "TIMEOUT"
    except Exception as e:
        return f"Error: {e}"

def check_keywords(response, keywords):
    """Check if response contains required keywords"""
    found = [k for k in keywords if k.lower() in response.lower()]
    missing = [k for k in keywords if k.lower() not in response.lower()]
    pct = len(found) / len(keywords) * 100 if keywords else 0
    return {"found": found, "missing": missing, "pct": pct, "passed": pct >= 50}

def main():
    print("=" * 70)
    print("C-SOLVER TRAINING - qwq:32b")
    print("Focus: Prediction, Synthesis, Advanced Reasoning")
    print("=" * 70)
    print(f"Model: {MODEL}")
    print(f"Timeout: {TIMEOUT}s per exercise")
    print(f"Start: {datetime.now().strftime('%H:%M:%S')}")
    print()

    results = {}

    # ============ LEVEL 1: FOUNDATION ============
    print("=" * 70)
    print("LEVEL 1: MATHEMATICAL FOUNDATION")
    print("=" * 70)

    # 1.1 Range Calculation
    print("\n[1.1] Range Calculation...")
    sys.stdout.flush()
    t0 = time.time()
    r = ask_ollama("""For Bitcoin puzzle N, key k_N is in range [2^(N-1), 2^N - 1].
Calculate the exact range for N=71.
What is 2^70? What is 2^71 - 1?
Show your calculation step by step.""")
    print(f"  Time: {time.time()-t0:.1f}s")
    print(f"  Response: {r[:500]}...")
    e = check_keywords(r, ["2^70", "2^71", "range", "1180591620717411303424"])
    results["1.1"] = e
    print(f"  Score: {e['pct']:.0f}% {'PASS' if e['passed'] else 'FAIL'}")

    # 1.2 Position Formula
    print("\n[1.2] Position Formula...")
    sys.stdout.flush()
    t0 = time.time()
    r = ask_ollama("""Position% = (k_N - 2^(N-1)) / (2^N - 1 - 2^(N-1)) × 100

Given k69 = 297274491920375905804
Calculate k69's position in its 69-bit range.
Show all steps. Is it near minimum, middle, or maximum?""")
    print(f"  Time: {time.time()-t0:.1f}s")
    print(f"  Response: {r[:500]}...")
    e = check_keywords(r, ["0.72", "position", "minimum", "near"])
    results["1.2"] = e
    print(f"  Score: {e['pct']:.0f}% {'PASS' if e['passed'] else 'FAIL'}")

    # ============ LEVEL 2: PATTERN RECOGNITION ============
    print("\n" + "=" * 70)
    print("LEVEL 2: PATTERN RECOGNITION")
    print("=" * 70)

    # 2.1 Verify Relationships
    print("\n[2.1] Verify Key Relationships...")
    sys.stdout.flush()
    t0 = time.time()
    r = ask_ollama("""Verify these claimed relationships for Bitcoin puzzle keys:
1. k5 = k2 × k3 (where k2=3, k3=7, k5=21)
2. k6 = k3² (where k3=7, k6=49)
3. k9 = 2 × k8 + 19 (where k8=224, k9=467)

Calculate each one. Which are TRUE and which are FALSE?""")
    print(f"  Time: {time.time()-t0:.1f}s")
    print(f"  Response: {r[:500]}...")
    e = check_keywords(r, ["true", "21", "49", "467", "verified"])
    results["2.1"] = e
    print(f"  Score: {e['pct']:.0f}% {'PASS' if e['passed'] else 'FAIL'}")

    # 2.2 Anomaly Detection
    print("\n[2.2] Anomaly Detection...")
    sys.stdout.flush()
    t0 = time.time()
    r = ask_ollama("""Normalized delta = (k_{n+1} - k_n) / 2^n

Given:
- k9=467, k10=514: delta=47, normalized = 47/512 = 0.092
- k56=44218742292676575, k57=138245758910846492: normalized = 1.305
- Mean normalized delta across all puzzles = 0.76

Identify which transitions are anomalous (much lower or higher than mean).
What does the k9→k10 LOW delta tell us about key generation?""")
    print(f"  Time: {time.time()-t0:.1f}s")
    print(f"  Response: {r[:500]}...")
    e = check_keywords(r, ["0.09", "1.305", "anomal", "low", "high"])
    results["2.2"] = e
    print(f"  Score: {e['pct']:.0f}% {'PASS' if e['passed'] else 'FAIL'}")

    # 2.3 Divisibility Patterns
    print("\n[2.3] Divisibility Patterns...")
    sys.stdout.flush()
    t0 = time.time()
    r = ask_ollama("""Keys divisible by their puzzle number N:
- k1=1 (÷1=1), k4=8 (÷4=2), k8=224 (÷8=28), k11=1155 (÷11=105)

k69 = 297274491920375905804 is divisible by 11 (not 69).
Calculate: 297274491920375905804 ÷ 11 = ?

What pattern do you see? Why 11 instead of 69?""")
    print(f"  Time: {time.time()-t0:.1f}s")
    print(f"  Response: {r[:500]}...")
    e = check_keywords(r, ["27024953810943264164", "11", "divisible", "pattern"])
    results["2.3"] = e
    print(f"  Score: {e['pct']:.0f}% {'PASS' if e['passed'] else 'FAIL'}")

    # ============ LEVEL 3: PREDICTION ============
    print("\n" + "=" * 70)
    print("LEVEL 3: PREDICTION")
    print("=" * 70)

    # 3.1 Position Prediction
    print("\n[3.1] Predict k71 Position...")
    sys.stdout.flush()
    t0 = time.time()
    r = ask_ollama("""Position data:
- k4: 0% (at minimum)
- k10: 0.39% (near minimum)
- k69: 0.72% (near minimum - solved fast!)
- k70: 64.4% (mid-range)

k69 was solved FAST because it was near the minimum of its range.

Predict: Where should we search for k71?
a) First 1% of range (following k69 pattern)
b) Middle 40-60% (following k70 pattern)
c) Near maximum (>90%)

Explain your reasoning based on the patterns.""")
    print(f"  Time: {time.time()-t0:.1f}s")
    print(f"  Response: {r[:500]}...")
    e = check_keywords(r, ["first", "1%", "minimum", "k69", "search"])
    results["3.1"] = e
    print(f"  Score: {e['pct']:.0f}% {'PASS' if e['passed'] else 'FAIL'}")

    # 3.2 Divisibility Prediction
    print("\n[3.2] Predict k71 Divisibility...")
    sys.stdout.flush()
    t0 = time.time()
    r = ask_ollama("""Known divisibility:
- k4 % 4 = 0
- k8 % 8 = 0
- k11 % 11 = 0
- k69 % 11 = 0 (but k69 % 69 ≠ 0)

71 is PRIME.

Should k71 be divisible by 71?
If k71 % 71 = 0, what's the FIRST candidate in [2^70, 2^71-1]?
Calculate: ceil(2^70 / 71) × 71""")
    print(f"  Time: {time.time()-t0:.1f}s")
    print(f"  Response: {r[:500]}...")
    e = check_keywords(r, ["71", "prime", "divisible", "first"])
    results["3.2"] = e
    print(f"  Score: {e['pct']:.0f}% {'PASS' if e['passed'] else 'FAIL'}")

    # ============ LEVEL 4: SYNTHESIS ============
    print("\n" + "=" * 70)
    print("LEVEL 4: SYNTHESIS")
    print("=" * 70)

    # 4.1 Pattern Synthesis
    print("\n[4.1] Synthesize Anomalies...")
    sys.stdout.flush()
    t0 = time.time()
    r = ask_ollama("""Synthesize these observations:

1. Early keys (k1-k8) have mathematical relationships: k5=k2×k3, k6=k3²
2. After k8, relationships break down - keys appear random
3. k69 at 0.72% position was solved FAST
4. Lane 9's A-multiplier (32=2^5) breaks the 13-divisibility pattern

What does this suggest about how the keys were generated?
Is there a REGIME CHANGE in the key generation algorithm?
What wallet software might produce this pattern?""")
    print(f"  Time: {time.time()-t0:.1f}s")
    print(f"  Response: {r[:500]}...")
    e = check_keywords(r, ["regime", "change", "generation", "algorithm", "pattern"])
    results["4.1"] = e
    print(f"  Score: {e['pct']:.0f}% {'PASS' if e['passed'] else 'FAIL'}")

    # 4.2 Search Strategy
    print("\n[4.2] Optimal Search Strategy...")
    sys.stdout.flush()
    t0 = time.time()
    r = ask_ollama("""Design a search strategy for k71:

Given:
- 71-bit range: [2^70, 2^71-1]
- k69 at 0.72% (solved fast)
- k70 at 64.4%
- Historical delta range: 0.09 to 1.31 × 2^n

Options:
1. Exhaustive search from minimum
2. Focus on first 1% (like k69)
3. Check divisibility by 71 first
4. Wait for public key exposure (Kangaroo attack)

Rank these strategies and explain which should be PRIMARY.
What specific range should we prioritize?""")
    print(f"  Time: {time.time()-t0:.1f}s")
    print(f"  Response: {r[:500]}...")
    e = check_keywords(r, ["1%", "first", "minimum", "priority", "strategy"])
    results["4.2"] = e
    print(f"  Score: {e['pct']:.0f}% {'PASS' if e['passed'] else 'FAIL'}")

    # ============ SUMMARY ============
    print("\n" + "=" * 70)
    print("TRAINING COMPLETE")
    print("=" * 70)
    print(f"End: {datetime.now().strftime('%H:%M:%S')}")

    l1 = sum(1 for k in ["1.1", "1.2"] if results.get(k, {}).get("passed"))
    l2 = sum(1 for k in ["2.1", "2.2", "2.3"] if results.get(k, {}).get("passed"))
    l3 = sum(1 for k in ["3.1", "3.2"] if results.get(k, {}).get("passed"))
    l4 = sum(1 for k in ["4.1", "4.2"] if results.get(k, {}).get("passed"))
    total = l1 + l2 + l3 + l4

    print(f"\nLevel 1 (Foundation):  {l1}/2 {'✓' if l1 >= 1 else ''}")
    print(f"Level 2 (Patterns):    {l2}/3 {'✓' if l2 >= 2 else ''}")
    print(f"Level 3 (Prediction):  {l3}/2 {'✓' if l3 >= 1 else ''}")
    print(f"Level 4 (Synthesis):   {l4}/2 {'✓' if l4 >= 1 else ''}")
    print(f"\nTotal: {total}/9")
    print(f"Target: 7/9")

    status = "CERTIFIED" if total >= 7 else "NEEDS WORK"
    print(f"Status: {status}")

    # Save results
    output = {
        "model": MODEL,
        "timestamp": datetime.now().isoformat(),
        "results": results,
        "summary": {
            "level1": l1,
            "level2": l2,
            "level3": l3,
            "level4": l4,
            "total": total,
            "status": status
        }
    }

    with open("/home/solo/LA/c-solver/training_results.json", "w") as f:
        json.dump(output, f, indent=2)
    print("\nSaved: c-solver/training_results.json")

    return total >= 7

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
