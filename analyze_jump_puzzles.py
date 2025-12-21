#!/usr/bin/env python3
"""
Jump Puzzle Constraint Analysis
Analyzes k[75], k[80], k[85], k[90] to constrain k[71] search space
"""

import sqlite3
import json
from typing import Dict, List, Tuple

def load_keys(db_path: str = "/home/rkh/ladder/db/kh.db") -> Dict[int, int]:
    """Load all known keys from database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT puzzle_id, priv_hex FROM keys WHERE puzzle_id IS NOT NULL ORDER BY puzzle_id, LENGTH(priv_hex) DESC")
    rows = cursor.fetchall()
    conn.close()

    k = {}
    for puzzle_id, priv_hex in rows:
        if puzzle_id not in k:
            k[puzzle_id] = int(priv_hex, 16)

    return k

def calculate_adj(k: Dict[int, int]) -> Dict[int, int]:
    """Calculate adj[n] = k[n] - 2*k[n-1] for all consecutive keys"""
    adj = {}
    for n in sorted(k.keys()):
        if n > 1 and (n-1) in k:
            adj[n] = k[n] - 2*k[n-1]
    return adj

def test_nstep_recursion(k: Dict[int, int], step: int = 5, multiplier: int = 9):
    """Test k[n] = multiplier*k[n-step] + offset pattern"""
    print(f"\n{'='*80}")
    print(f"Testing {step}-step recursion: k[n] = {multiplier}*k[n-{step}] + offset")
    print(f"{'='*80}")

    results = []
    for n in sorted(k.keys()):
        if (n - step) in k:
            offset = k[n] - multiplier * k[n - step]
            ratio = offset / k[n - step]
            results.append({
                'n': n,
                'n_prev': n - step,
                'offset': offset,
                'ratio': ratio
            })
            print(f"k[{n}] = {multiplier}*k[{n-step}] + {offset}")
            print(f"  offset/k[{n-step}] = {ratio:.6f}")

    # Check offset growth rates
    if len(results) > 1:
        print(f"\nOffset growth rates:")
        for i in range(1, len(results)):
            ratio = results[i]['offset'] / results[i-1]['offset']
            print(f"  offset[{results[i]['n']}] / offset[{results[i-1]['n']}] = {ratio:.6f}")

    return results

def analyze_adj_pattern(adj: Dict[int, int], start: int = 65, end: int = 70):
    """Analyze adj[n] pattern for sign changes and magnitude growth"""
    print(f"\n{'='*80}")
    print(f"adj[n] pattern analysis (n={start} to {end})")
    print(f"{'='*80}")

    adj_values = []
    for n in range(start, end + 1):
        if n in adj:
            adj_values.append((n, adj[n]))
            sign = "+" if adj[n] > 0 else "-"
            print(f"adj[{n}] = {sign}{abs(adj[n]):40d}")

    # Calculate ratios
    print(f"\nConsecutive ratios:")
    ratios = []
    for i in range(1, len(adj_values)):
        n_prev, adj_prev = adj_values[i-1]
        n_curr, adj_curr = adj_values[i]
        ratio = adj_curr / adj_prev
        ratios.append(ratio)
        print(f"  adj[{n_curr}]/adj[{n_prev}] = {ratio:10.6f}")

    # Statistics
    avg_abs = sum(abs(adj[n]) for n in range(start, end + 1) if n in adj) / len(adj_values)
    print(f"\nAverage |adj[n]|: {avg_abs:.2e}")

    return adj_values, ratios, avg_abs

def backtrack_from_jump(k_target: int, n_target: int, n_start: int, adj_model: str = "zero",
                        adj_const: int = 0, avg_mag: float = 0) -> int:
    """
    Back-calculate k[n_start] from k[n_target] using adj model

    adj_model options:
    - "zero": adj[n] = 0 (pure doubling)
    - "constant": adj[n] = adj_const
    - "alternating": adj[n] alternates ± avg_mag
    """
    k_calc = k_target
    steps = n_target - n_start

    for i in range(steps):
        if adj_model == "zero":
            k_calc = k_calc / 2
        elif adj_model == "constant":
            k_calc = (k_calc - adj_const) / 2
        elif adj_model == "alternating":
            # Alternate +/-, working backwards
            sign = 1 if (steps - i - 1) % 2 == 0 else -1
            k_calc = (k_calc - sign * avg_mag) / 2
        else:
            raise ValueError(f"Unknown adj_model: {adj_model}")

    return int(k_calc)

def estimate_k71_bounds(k: Dict[int, int], adj: Dict[int, int]):
    """Estimate bounds for k[71] using multiple models"""
    print(f"\n{'='*80}")
    print(f"Estimating k[71] bounds from k[75]")
    print(f"{'='*80}")

    k75 = k[75]
    adj70 = adj[70]

    # Calculate average adj magnitude for n=65-70
    avg_mag = sum(abs(adj[n]) for n in range(65, 71) if n in adj) / 6

    # Model scenarios
    scenarios = [
        ("Zero adj (pure doubling)", "zero", 0, 0),
        ("Constant adj[70]", "constant", adj70, 0),
        ("Alternating adj", "alternating", 0, avg_mag),
    ]

    estimates = []
    for name, model, adj_const, avg_mag_val in scenarios:
        k71_est = backtrack_from_jump(k75, 75, 71, model, adj_const, avg_mag_val)
        estimates.append((name, k71_est))

        # Calculate position in 71-bit range
        range_min = 2**70
        range_max = 2**71 - 1
        position = (k71_est - range_min) / (range_max - range_min) * 100

        print(f"\n{name}:")
        print(f"  k[71] ≈ {k71_est}")
        print(f"       ≈ {hex(k71_est)}")
        print(f"  Position: {position:.4f}% in 71-bit range")

        # Verify by calculating k[70]
        k70_calc = backtrack_from_jump(k71_est, 71, 70, model, adj_const, avg_mag_val)
        k70_actual = k[70]
        error = abs(k70_calc - k70_actual) / k70_actual * 100
        print(f"  Verify k[70]: calc={k70_calc}, actual={k70_actual}, error={error:.2f}%")

    # Bounds
    all_est = [est for _, est in estimates]
    k71_min = min(all_est)
    k71_max = max(all_est)

    print(f"\n{'='*80}")
    print(f"ESTIMATED BOUNDS FOR k[71]")
    print(f"{'='*80}")
    print(f"Lower: {k71_min} ({hex(k71_min)})")
    print(f"Upper: {k71_max} ({hex(k71_max)})")
    print(f"Range: {k71_max - k71_min}")
    print(f"\n71-bit range: {2**70} to {2**71 - 1}")
    print(f"Bounded search space: {(k71_max - max(k71_min, 2**70)) / (2**71 - 2**70) * 100:.2f}% of range")

    return estimates

def test_linear_formula(k: Dict[int, int], n_target: int, terms: List[Tuple[int, int, int]]):
    """
    Test if k[n_target] = a*k[i] + b*k[j] + ...

    terms: List of (n, a_range_max, b_range_max) to test
    """
    print(f"\n{'='*80}")
    print(f"Testing linear formulas for k[{n_target}]")
    print(f"{'='*80}")

    for i, j in [(70, 69), (75, 70)]:
        if i not in k or j not in k:
            continue

        print(f"\nSearching for k[{n_target}] = a*k[{i}] + b*k[{j}]...")

        best_diff = float('inf')
        best_formula = None

        for a in range(1, 100):
            for b in range(-100, 100):
                result = a * k[i] + b * k[j]
                diff = abs(k[n_target] - result)
                if diff < best_diff:
                    best_diff = diff
                    best_formula = (a, b, result)

        if best_formula:
            a, b, result = best_formula
            print(f"Best: k[{n_target}] ≈ {a}*k[{i}] + {b}*k[{j}]")
            print(f"  Calculated: {result}")
            print(f"  Actual:     {k[n_target]}")
            print(f"  Difference: {k[n_target] - result}")
            print(f"  Error %:    {abs(k[n_target] - result) / k[n_target] * 100:.6f}%")

def main():
    """Main analysis routine"""
    print("="*80)
    print("JUMP PUZZLE CONSTRAINT ANALYSIS")
    print("="*80)

    # Load data
    print("\nLoading keys from database...")
    k = load_keys()
    print(f"Loaded {len(k)} keys")

    # Calculate adj
    print("Calculating adj values...")
    adj = calculate_adj(k)
    print(f"Calculated {len(adj)} adj values")

    # Show jump puzzle keys
    print(f"\n{'='*80}")
    print("Known jump puzzle keys:")
    print(f"{'='*80}")
    for n in [69, 70, 75, 80, 85, 90]:
        if n in k:
            print(f"k[{n}] = {k[n]}")
            print(f"      = {hex(k[n])}")

    # Test 5-step recursion
    test_nstep_recursion(k, step=5, multiplier=9)

    # Analyze adj pattern
    analyze_adj_pattern(adj, start=65, end=70)

    # Estimate k[71] bounds
    estimates = estimate_k71_bounds(k, adj)

    # Test linear formulas
    test_linear_formula(k, 75, [(70, 100, 100), (75, 100, 100)])
    test_linear_formula(k, 80, [(75, 100, 100)])

    # Save results
    results = {
        'jump_puzzles': {n: k[n] for n in [69, 70, 75, 80, 85, 90] if n in k},
        'adj_values': {n: adj[n] for n in range(65, 71) if n in adj},
        'k71_estimates': {name: est for name, est in estimates},
        'bounds': {
            'lower': max(min(est for _, est in estimates), 2**70),
            'upper': max(est for _, est in estimates),
        }
    }

    output_file = "/home/rkh/ladder/jump_puzzle_analysis_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n{'='*80}")
    print(f"Results saved to: {output_file}")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()
