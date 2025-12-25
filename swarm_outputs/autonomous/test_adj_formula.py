#!/usr/bin/env python3
"""
Test: Can adj[n] be expressed as a function of n, 2^n, and simple constants?

Hypothesis: adj[n] might be something like:
- adj[n] = a*2^n + b*n + c
- adj[n] = floor(alpha * 2^n) for some alpha
- adj[n] follows a simple recurrence

If we can predict adj[n], we can predict k[n] via k[n] = 2*k[n-1] + adj[n]
"""

import sqlite3
from math import floor, ceil, log2

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

def compute_adj(k):
    adj = {}
    for n in range(2, max(k.keys()) + 1):
        if n in k and (n-1) in k:
            adj[n] = k[n] - 2 * k[n-1]
    return adj

def test_linear_model(adj):
    """Test if adj[n]/2^n = a*n + b for some constants a, b"""
    print("=== Testing: adj[n]/2^n = a*n + b ===")

    # Use first 15 points for fitting
    ns = list(range(2, 17))
    ratios = [adj[n] / (2**n) for n in ns]

    # Simple linear regression
    n_sum = sum(ns)
    r_sum = sum(ratios)
    nr_sum = sum(n * r for n, r in zip(ns, ratios))
    n2_sum = sum(n**2 for n in ns)
    N = len(ns)

    a = (N * nr_sum - n_sum * r_sum) / (N * n2_sum - n_sum**2)
    b = (r_sum - a * n_sum) / N

    print(f"Fitted: adj[n]/2^n ≈ {a:.6f}*n + {b:.6f}")

    # Test predictions
    print("\nPrediction test:")
    for n in range(2, 25):
        if n not in adj:
            continue
        predicted_ratio = a * n + b
        actual_ratio = adj[n] / (2**n)
        predicted_adj = floor(predicted_ratio * (2**n))
        error = abs(predicted_adj - adj[n])
        error_pct = 100 * error / max(1, abs(adj[n]))
        print(f"  n={n}: predicted={predicted_adj:>12}, actual={adj[n]:>12}, error={error_pct:>6.1f}%")

def test_growth_rate(adj):
    """Test if adj[n] grows at a consistent rate"""
    print("\n=== Growth Rate Analysis ===")

    growth_rates = []
    for n in range(3, min(40, max(adj.keys()))):
        if n in adj and (n-1) in adj and adj[n-1] != 0:
            rate = adj[n] / adj[n-1]
            growth_rates.append((n, rate))
            print(f"  adj[{n}]/adj[{n-1}] = {rate:>10.4f}")

def test_recurrence(adj):
    """Test if adj[n] = f(adj[n-1], adj[n-2], ...)"""
    print("\n=== Recurrence Testing ===")

    # Test: adj[n] = 2*adj[n-1] - adj[n-2]
    print("Testing: adj[n] = 2*adj[n-1] - adj[n-2]")
    for n in range(4, min(20, max(adj.keys()))):
        if n in adj and (n-1) in adj and (n-2) in adj:
            predicted = 2 * adj[n-1] - adj[n-2]
            actual = adj[n]
            match = "✓" if predicted == actual else "✗"
            print(f"  n={n}: predicted={predicted:>10}, actual={actual:>10} {match}")

    # Test: adj[n] = -adj[n-3] (period 6 with alternating signs)
    print("\nTesting: adj[n] relates to adj[n-3]")
    for n in range(5, min(20, max(adj.keys()))):
        if n in adj and (n-3) in adj:
            ratio = adj[n] / adj[n-3] if adj[n-3] != 0 else 0
            print(f"  adj[{n}]/adj[{n-3}] = {ratio:>10.4f}")

def test_modular_structure(adj, k):
    """Test if adj[n] mod k[d] = 0 for some d < n"""
    print("\n=== Modular Structure ===")

    for n in range(4, min(30, max(adj.keys()))):
        if n not in adj:
            continue

        divisors = []
        for d in range(1, n):
            if d in k and k[d] != 0 and adj[n] % k[d] == 0:
                divisors.append(d)

        if divisors:
            print(f"  adj[{n}] = {adj[n]} divisible by k[{divisors}]")

def test_closest_power_of_2(adj):
    """Test if |adj[n]| is close to some power of 2"""
    print("\n=== Closest Power of 2 ===")

    for n in range(2, min(25, max(adj.keys()))):
        if n not in adj:
            continue

        val = abs(adj[n])
        if val == 0:
            continue

        log_val = log2(val)
        closest_pow = round(log_val)
        closest_2pow = 2**closest_pow
        diff = val - closest_2pow
        diff_pct = 100 * diff / closest_2pow

        sign = '+' if adj[n] >= 0 else '-'
        print(f"  adj[{n}] = {sign}{val:>12}, closest 2^{closest_pow}={closest_2pow:>12}, diff={diff_pct:>+6.1f}%")

def main():
    k = load_k_values()
    adj = compute_adj(k)

    print(f"Loaded {len(k)} k values, {len(adj)} adj values\n")

    test_linear_model(adj)
    test_growth_rate(adj)
    test_recurrence(adj)
    test_modular_structure(adj, k)
    test_closest_power_of_2(adj)

if __name__ == "__main__":
    main()
