#!/usr/bin/env python3
"""
B-Solver Training Script
Train phi4-reasoning:14b on mathematical analysis, anomalies, drift, and puzzle relations
"""
import requests
import json
import time
import sys
from datetime import datetime

MODEL = "phi4-reasoning:14b"
BASE_URL = "http://localhost:11434"
TIMEOUT = 180  # Phi4 reasoning needs more time


def ask_phi(prompt: str, timeout: int = TIMEOUT) -> str:
    """Query phi4-reasoning model"""
    try:
        resp = requests.post(
            f"{BASE_URL}/api/generate",
            json={"model": MODEL, "prompt": prompt, "stream": False},
            timeout=timeout
        )
        if resp.status_code == 200:
            return resp.json().get("response", "No response")
        return f"Error: {resp.status_code}"
    except requests.exceptions.Timeout:
        return "TIMEOUT"
    except Exception as e:
        return f"Error: {e}"


def check_keywords(response: str, keywords: list) -> dict:
    """Check if response contains expected keywords"""
    found = [k for k in keywords if k.lower() in response.lower()]
    missing = [k for k in keywords if k.lower() not in response.lower()]
    pct = len(found) / len(keywords) * 100 if keywords else 0
    return {"found": found, "missing": missing, "pct": pct, "passed": pct >= 50}


def run_training():
    """Run B-Solver training exercises"""
    print("=" * 70)
    print("B-SOLVER TRAINING - phi4-reasoning:14b")
    print("Focus: Math, Anomalies, Drift Analysis, Puzzle Relations")
    print("=" * 70)
    print(f"Model: {MODEL}")
    print(f"Start: {datetime.now().strftime('%H:%M:%S')}")
    print()

    results = {}

    # ============ LEVEL 1: MATHEMATICAL FOUNDATIONS ============
    print("=" * 70)
    print("LEVEL 1: MATHEMATICAL FOUNDATIONS")
    print("=" * 70)

    # 1.1 Statistical Analysis
    print("\n[1.1] Statistical Analysis...")
    sys.stdout.flush()
    t0 = time.time()
    r = ask_phi("""Given normalized deltas for Bitcoin puzzle keys:
Mean = 0.762, Min = 0.092, Max = 1.305, StdDev = 0.25

Questions:
1. What percentage of deltas are within 1 standard deviation of the mean?
2. Is 0.092 a statistical outlier? (Use 2-sigma rule)
3. Calculate z-score for delta = 0.092

Show calculations.""")
    print(f"  Time: {time.time()-t0:.1f}s")
    print(f"  Response: {r[:500]}...")
    e = check_keywords(r, ["outlier", "sigma", "z-score", "0.092"])
    results["1.1"] = e
    print(f"  Score: {e['pct']:.0f}% {'PASS' if e['passed'] else 'FAIL'}")

    # 1.2 Position Calculation
    print("\n[1.2] Position Calculation...")
    sys.stdout.flush()
    t0 = time.time()
    r = ask_phi("""Key k69 = 297274491920375905804
Range: [2^68, 2^69 - 1] = [295147905179352825856, 590295810358705651711]

Calculate:
1. Position % = (k69 - low) / (high - low) × 100
2. Is this near the minimum?
3. What does position 0.72% mean for search strategy?

Show step-by-step calculation.""")
    print(f"  Time: {time.time()-t0:.1f}s")
    print(f"  Response: {r[:500]}...")
    e = check_keywords(r, ["0.72", "minimum", "position", "search"])
    results["1.2"] = e
    print(f"  Score: {e['pct']:.0f}% {'PASS' if e['passed'] else 'FAIL'}")

    # 1.3 Ratio Analysis
    print("\n[1.3] Ratio Analysis...")
    sys.stdout.flush()
    t0 = time.time()
    r = ask_phi("""Consecutive key ratios:
k70/k69 = 970436974005023690481 / 297274491920375905804

Expected if doubling: 2.0
Calculate:
1. Actual ratio
2. Percentage deviation from expected
3. Is this ratio anomalous? Why?""")
    print(f"  Time: {time.time()-t0:.1f}s")
    print(f"  Response: {r[:500]}...")
    e = check_keywords(r, ["3.26", "ratio", "anomal", "deviation"])
    results["1.3"] = e
    print(f"  Score: {e['pct']:.0f}% {'PASS' if e['passed'] else 'FAIL'}")

    # ============ LEVEL 2: ANOMALY DETECTION ============
    print("\n" + "=" * 70)
    print("LEVEL 2: ANOMALY DETECTION")
    print("=" * 70)

    # 2.1 Delta Anomalies
    print("\n[2.1] Delta Anomaly Classification...")
    sys.stdout.flush()
    t0 = time.time()
    r = ask_phi("""Normalized deltas (k_{n+1} - k_n) / 2^n:
- k3→k4: 0.125
- k9→k10: 0.092
- k39→k40: 1.237
- k56→k57: 1.305

Normal range: [0.15, 1.20]

Classify each as:
- LOW anomaly (< 0.15)
- HIGH anomaly (> 1.20)
- Normal

What pattern do you see in anomaly locations?""")
    print(f"  Time: {time.time()-t0:.1f}s")
    print(f"  Response: {r[:500]}...")
    e = check_keywords(r, ["low", "high", "0.092", "1.305", "anomaly"])
    results["2.1"] = e
    print(f"  Score: {e['pct']:.0f}% {'PASS' if e['passed'] else 'FAIL'}")

    # 2.2 Position Anomalies
    print("\n[2.2] Position Anomaly Detection...")
    sys.stdout.flush()
    t0 = time.time()
    r = ask_phi("""Keys and their positions in range:
- k2: 100% (at max)
- k3: 100% (at max)
- k4: 0% (at min)
- k10: 0.39% (near min)
- k69: 0.72% (near min)
- k70: 64.4% (mid-range)

Questions:
1. What puzzles have position < 5% (near min)?
2. What puzzles have position > 95% (near max)?
3. Is there a pattern? Do early vs late puzzles differ?
4. What does k69 at 0.72% suggest about how it was found "fast"?""")
    print(f"  Time: {time.time()-t0:.1f}s")
    print(f"  Response: {r[:500]}...")
    e = check_keywords(r, ["k4", "k69", "minimum", "pattern", "fast"])
    results["2.2"] = e
    print(f"  Score: {e['pct']:.0f}% {'PASS' if e['passed'] else 'FAIL'}")

    # 2.3 Relationship Anomalies
    print("\n[2.3] Relationship Anomaly...")
    sys.stdout.flush()
    t0 = time.time()
    r = ask_phi("""Verified relationships:
- k5 = k2 × k3 = 3 × 7 = 21 ✓
- k6 = k3² = 49 ✓
- k8 = k4 × k3 × 4 = 224 ✓
- k9 = 2 × k8 + 19 = 467 ✓

But these fail:
- k7 ≠ k2 × k5 (63 ≠ 76)
- k10 ≠ 2 × k9 (934 ≠ 514)

Questions:
1. What changed after k9?
2. Why do early keys have clear relationships but later don't?
3. Is there a "transition point" where patterns break?""")
    print(f"  Time: {time.time()-t0:.1f}s")
    print(f"  Response: {r[:500]}...")
    e = check_keywords(r, ["transition", "pattern", "break", "early", "later"])
    results["2.3"] = e
    print(f"  Score: {e['pct']:.0f}% {'PASS' if e['passed'] else 'FAIL'}")

    # ============ LEVEL 3: DRIFT ANALYSIS ============
    print("\n" + "=" * 70)
    print("LEVEL 3: DRIFT ANALYSIS")
    print("=" * 70)

    # 3.1 Delta Drift
    print("\n[3.1] Normalized Delta Drift...")
    sys.stdout.flush()
    t0 = time.time()
    r = ask_phi("""Mean normalized delta by window:
- Puzzles 1-10: mean=0.52, std=0.35
- Puzzles 11-20: mean=0.72, std=0.20
- Puzzles 21-30: mean=0.81, std=0.18
- Puzzles 31-40: mean=0.78, std=0.22
- Puzzles 41-50: mean=0.75, std=0.25
- Puzzles 51-60: mean=0.84, std=0.30
- Puzzles 61-70: mean=0.89, std=0.35

Questions:
1. Is the mean trending upward over puzzle numbers?
2. What's happening to variance/std over time?
3. Are later puzzles more or less predictable?
4. Extrapolate: what might mean delta be for puzzles 71-80?""")
    print(f"  Time: {time.time()-t0:.1f}s")
    print(f"  Response: {r[:500]}...")
    e = check_keywords(r, ["trend", "increasing", "variance", "predict"])
    results["3.1"] = e
    print(f"  Score: {e['pct']:.0f}% {'PASS' if e['passed'] else 'FAIL'}")

    # 3.2 Position Drift
    print("\n[3.2] Position Drift Analysis...")
    sys.stdout.flush()
    t0 = time.time()
    r = ask_phi("""Mean position % by window:
- Puzzles 1-10: mean=45.2%, range=[0%, 100%]
- Puzzles 11-20: mean=52.1%, range=[8%, 89%]
- Puzzles 31-40: mean=48.5%, range=[12%, 78%]
- Puzzles 51-60: mean=55.3%, range=[18%, 97%]
- Puzzles 61-70: mean=42.8%, range=[0.72%, 95%]

Questions:
1. Is mean position stable or drifting?
2. Why does k69 (0.72%) bring down the 61-70 window mean?
3. What does this suggest about k71's likely position?""")
    print(f"  Time: {time.time()-t0:.1f}s")
    print(f"  Response: {r[:500]}...")
    e = check_keywords(r, ["k69", "position", "drift", "k71"])
    results["3.2"] = e
    print(f"  Score: {e['pct']:.0f}% {'PASS' if e['passed'] else 'FAIL'}")

    # ============ LEVEL 4: PUZZLE RELATIONS ============
    print("\n" + "=" * 70)
    print("LEVEL 4: PUZZLE RELATIONS")
    print("=" * 70)

    # 4.1 Find Relations
    print("\n[4.1] Discover Hidden Relations...")
    sys.stdout.flush()
    t0 = time.time()
    r = ask_phi("""Known keys: k1=1, k2=3, k3=7, k4=8, k5=21, k6=49, k7=76, k8=224

Test these potential relationships:
1. k7 = k6 + k5 + ? = 49 + 21 + ? = 76 (solve for ?)
2. k7 = k3 × k4 + ? = 56 + ? = 76 (solve for ?)
3. k8 = k7 × ? = 224 (solve for ?)
4. k8 = k6 × ? + k5 = 224 (solve for ?)

Which relationships hold exactly?""")
    print(f"  Time: {time.time()-t0:.1f}s")
    print(f"  Response: {r[:500]}...")
    e = check_keywords(r, ["76", "224", "relationship", "exact"])
    results["4.1"] = e
    print(f"  Score: {e['pct']:.0f}% {'PASS' if e['passed'] else 'FAIL'}")

    # 4.2 Divisibility Patterns
    print("\n[4.2] Divisibility Analysis...")
    sys.stdout.flush()
    t0 = time.time()
    r = ask_phi("""Keys divisible by their puzzle number N:
- k1 ÷ 1 = 1 ✓
- k4 ÷ 4 = 2 ✓
- k8 ÷ 8 = 28 ✓
- k11 ÷ 11 = 105 ✓
- k36 ÷ 36 = 1177438055 ✓

k69 = 297274491920375905804
k69 ÷ 69 = ?

Questions:
1. Is k69 divisible by 69?
2. Is k69 divisible by any factors of 69 (3, 23)?
3. k69 = 4 × 11 × large_prime. Why is 11 significant?
4. If k71 is divisible by 71 (a prime), what does that imply?""")
    print(f"  Time: {time.time()-t0:.1f}s")
    print(f"  Response: {r[:500]}...")
    e = check_keywords(r, ["divisible", "11", "71", "prime"])
    results["4.2"] = e
    print(f"  Score: {e['pct']:.0f}% {'PASS' if e['passed'] else 'FAIL'}")

    # ============ LEVEL 5: ADVANCED REASONING ============
    print("\n" + "=" * 70)
    print("LEVEL 5: ADVANCED REASONING")
    print("=" * 70)

    # 5.1 k71 Prediction
    print("\n[5.1] k71 Position Prediction...")
    sys.stdout.flush()
    t0 = time.time()
    r = ask_phi("""Given:
- k69 at position 0.72% (solved "fast")
- k70 at position 64.4%
- k4 at position 0% (minimum)
- k10 at position 0.39%

Pattern observation: Keys at/near minimum were found faster.

71-bit range: [2^70, 2^71 - 1]

Questions:
1. Based on the pattern, what position % would you predict for k71?
2. If k71 is at ~1% position, what would its approximate value be?
3. If k71 is divisible by 71, what's the first such value in range?
4. What search strategy would you recommend?""")
    print(f"  Time: {time.time()-t0:.1f}s")
    print(f"  Response: {r[:500]}...")
    e = check_keywords(r, ["position", "search", "minimum", "predict"])
    results["5.1"] = e
    print(f"  Score: {e['pct']:.0f}% {'PASS' if e['passed'] else 'FAIL'}")

    # 5.2 Anomaly Synthesis
    print("\n[5.2] Anomaly Synthesis...")
    sys.stdout.flush()
    t0 = time.time()
    r = ask_phi("""Synthesize all anomalies:

Delta anomalies:
- k3→k4 (0.125) and k9→k10 (0.092) are LOW
- k56→k57 (1.305) is HIGH

Position anomalies:
- k2, k3 at 100% (max)
- k4, k10, k69 near 0% (min)

Ratio anomalies:
- k10/k9 = 1.10 (too low, expected ~2)
- k70/k69 = 3.26 (too high)

Questions:
1. Are LOW delta anomalies correlated with near-min positions?
2. What generates keys near range extremes?
3. Is there a "regime change" around k9-k10?
4. What does this tell us about the key generation algorithm?""")
    print(f"  Time: {time.time()-t0:.1f}s")
    print(f"  Response: {r[:500]}...")
    e = check_keywords(r, ["correlation", "regime", "generation", "algorithm"])
    results["5.2"] = e
    print(f"  Score: {e['pct']:.0f}% {'PASS' if e['passed'] else 'FAIL'}")

    # ============ SUMMARY ============
    print("\n" + "=" * 70)
    print("B-SOLVER TRAINING COMPLETE")
    print("=" * 70)
    print(f"End: {datetime.now().strftime('%H:%M:%S')}")

    l1 = sum(1 for k in ["1.1", "1.2", "1.3"] if results.get(k, {}).get("passed"))
    l2 = sum(1 for k in ["2.1", "2.2", "2.3"] if results.get(k, {}).get("passed"))
    l3 = sum(1 for k in ["3.1", "3.2"] if results.get(k, {}).get("passed"))
    l4 = sum(1 for k in ["4.1", "4.2"] if results.get(k, {}).get("passed"))
    l5 = sum(1 for k in ["5.1", "5.2"] if results.get(k, {}).get("passed"))

    print(f"\nLevel 1 (Math Foundations): {l1}/3")
    print(f"Level 2 (Anomaly Detection): {l2}/3")
    print(f"Level 3 (Drift Analysis): {l3}/2")
    print(f"Level 4 (Puzzle Relations): {l4}/2")
    print(f"Level 5 (Advanced Reasoning): {l5}/2")

    total = l1 + l2 + l3 + l4 + l5
    print(f"\nTotal: {total}/12")

    if total >= 10:
        status = "CERTIFIED (EXCELLENT)"
    elif total >= 8:
        status = "CERTIFIED"
    elif total >= 6:
        status = "NEEDS IMPROVEMENT"
    else:
        status = "NEEDS WORK"

    print(f"Status: {status}")

    # Save results
    with open("/home/solo/LA/b-solver/training_results.json", "w") as f:
        json.dump({
            "model": MODEL,
            "timestamp": datetime.now().isoformat(),
            "results": results,
            "summary": {
                "level1": l1,
                "level2": l2,
                "level3": l3,
                "level4": l4,
                "level5": l5,
                "total": total,
                "status": status
            }
        }, f, indent=2)
    print("\nSaved: /home/solo/LA/b-solver/training_results.json")

    return total, status


if __name__ == "__main__":
    run_training()
