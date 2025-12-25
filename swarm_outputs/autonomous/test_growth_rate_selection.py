#!/usr/bin/env python3
"""
Test Growth Rate Stability Hypothesis:

If k[n] is selected to maintain λ ≈ 2.0073, then:
1. k[n]/k[n-1] should be consistently close to λ
2. Among all valid candidates for k[n], the actual one might be closest to λ*k[n-1]

Let's test this.
"""

import sqlite3
from math import log

DB_PATH = "/home/rkh/ladder/db/kh.db"

def load_k_values():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT puzzle_id, priv_hex
        FROM ground_truth
        WHERE priv_hex IS NOT NULL
        ORDER BY puzzle_id
    """)
    rows = c.fetchall()
    conn.close()
    k = {}
    for puzzle_id, priv_hex in rows:
        if priv_hex.startswith('0x'):
            k[puzzle_id] = int(priv_hex, 16)
        else:
            k[puzzle_id] = int(priv_hex, 16)
    return k

def compute_growth_rate(k, start=2, end=70):
    """Compute the average growth rate λ = (k[n]/k[n-1])^(1/1) averaged"""
    rates = []
    for n in range(start, end + 1):
        if n in k and (n-1) in k and k[n-1] > 0:
            rate = k[n] / k[n-1]
            rates.append(rate)

    # Geometric mean
    product = 1.0
    for r in rates:
        product *= r
    geo_mean = product ** (1/len(rates)) if rates else 0

    # Arithmetic mean
    arith_mean = sum(rates) / len(rates) if rates else 0

    return geo_mean, arith_mean, rates

def test_growth_rate_prediction(k, lam):
    """Test if predicting k[n] ≈ λ * k[n-1] works"""
    print(f"\n=== Testing Growth Rate Prediction with λ={lam:.6f} ===\n")

    errors = []
    for n in range(4, min(31, max(k.keys()) + 1)):
        if n not in k or (n-1) not in k:
            continue

        predicted = lam * k[n-1]
        actual = k[n]
        error = actual - predicted
        error_pct = 100 * error / actual if actual != 0 else 0

        # Also compute the actual ratio
        ratio = actual / k[n-1]

        errors.append(abs(error_pct))

        print(f"n={n:>2}: predicted={predicted:>14.0f}, actual={actual:>14}, error={error_pct:>+7.2f}%, ratio={ratio:.4f}")

    print(f"\nMean absolute error: {sum(errors)/len(errors):.2f}%")
    print(f"Max absolute error: {max(errors):.2f}%")

def test_growth_rate_selection(k):
    """
    Test if the actual k[n] is selected from candidates based on growth rate.

    For each n, compute all valid candidates and check if the actual one
    is closest to λ*k[n-1].
    """
    print("\n=== Testing Growth Rate Selection Hypothesis ===\n")

    # First compute average λ
    geo_mean, arith_mean, rates = compute_growth_rate(k)
    print(f"Computed λ (geometric mean): {geo_mean:.6f}")
    print(f"Computed λ (arithmetic mean): {arith_mean:.6f}")

    # Use geometric mean
    lam = geo_mean

    # For each n, find candidates and check if actual is closest to λ*k[n-1]
    print("\nChecking if actual k[n] is closest to λ*k[n-1] among valid candidates:")

    matches = 0
    total = 0

    for n in range(4, min(21, max(k.keys()) + 1)):
        if n not in k or (n-1) not in k:
            continue

        actual_k = k[n]
        target = lam * k[n-1]

        # Generate candidates: k[n] = base - m*kd for various d, m
        base = 2 * k[n-1] + (1 << n)
        candidates = []

        for d in range(1, n):
            kd = k[d]
            # For various m values
            for m in range(-100, 500):
                candidate = base - m * kd
                if 2**(n-1) <= candidate < 2**n:  # Valid range
                    # Verify it's a valid candidate (m is integer)
                    adj = candidate - 2 * k[n-1]
                    numerator = (1 << n) - adj
                    if numerator % kd == 0:
                        candidates.append((candidate, m, d, abs(candidate - target)))

        if not candidates:
            continue

        # Find candidate closest to target
        closest = min(candidates, key=lambda x: x[3])

        # Find actual in candidates
        actual_candidate = None
        for c in candidates:
            if c[0] == actual_k:
                actual_candidate = c
                break

        if actual_candidate is None:
            print(f"n={n}: ACTUAL NOT IN CANDIDATES!")
            continue

        total += 1
        is_closest = (closest[0] == actual_k)
        if is_closest:
            matches += 1
            status = "✓ CLOSEST"
        else:
            status = f"✗ closest={closest[0]} (m={closest[1]}, d={closest[2]})"

        actual_dist = actual_candidate[3]
        closest_dist = closest[3]

        print(f"n={n}: actual={actual_k}, target={target:.0f}, dist={actual_dist:.0f}, {status}")

    print(f"\nResults: {matches}/{total} matches ({100*matches/total:.1f}%)")

    if matches == total:
        print("\n==> BREAKTHROUGH: Growth rate selection hypothesis WORKS!")
    elif matches > total * 0.5:
        print("\n==> Partial support for growth rate hypothesis")
    else:
        print("\n==> Growth rate selection hypothesis does NOT fully explain selection")

def analyze_growth_rate_variance(k):
    """Analyze how the growth rate varies"""
    print("\n=== Growth Rate Variance Analysis ===\n")

    geo_mean, arith_mean, rates = compute_growth_rate(k)

    print(f"λ geometric mean: {geo_mean:.6f}")
    print(f"λ arithmetic mean: {arith_mean:.6f}")
    print(f"Min rate: {min(rates):.6f}")
    print(f"Max rate: {max(rates):.6f}")
    print(f"Std dev: {(sum((r - arith_mean)**2 for r in rates) / len(rates))**0.5:.6f}")

    # Check for patterns in rate
    print("\nRates by n:")
    for i, rate in enumerate(rates[:25], start=2):
        deviation = rate - arith_mean
        bar = "+" * int(deviation * 20) if deviation > 0 else "-" * int(-deviation * 20)
        print(f"  k[{i+1}]/k[{i}] = {rate:.4f} {bar}")

def main():
    k = load_k_values()
    print(f"Loaded {len(k)} k values\n")

    analyze_growth_rate_variance(k)

    geo_mean, arith_mean, rates = compute_growth_rate(k)
    test_growth_rate_prediction(k, geo_mean)

    test_growth_rate_selection(k)

if __name__ == "__main__":
    main()
