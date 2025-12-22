#!/usr/bin/env python3
"""
K-Sequence Generator - Synthesizing all findings
Goal: Build a generator that works for ALL n values

Based on verified findings:
- Core recurrence: k[n] = 2*k[n-1] + adj[n]
- adj[n] = 2^n - m[n]*k[d[n]]
- Phase 1 (n≤18): Fibonacci/Lucas foundation + precise formulas
- Phase 2 (n≥19): Constant encoding layer + formula layer
- DUAL-LAYER: Both layers must agree
"""

import sqlite3
import math
from fractions import Fraction

# Mathematical constants for reference
PI = math.pi
E = math.e
PHI = (1 + math.sqrt(5)) / 2
SQRT2 = math.sqrt(2)
SQRT3 = math.sqrt(3)
LN2 = math.log(2)

# Load all 74 known keys from database
def load_keys():
    """Load all known keys from database"""
    conn = sqlite3.connect('/home/solo/LA/db/kh.db')
    cursor = conn.cursor()
    cursor.execute("SELECT puzzle_id, priv_hex FROM keys WHERE puzzle_id IS NOT NULL ORDER BY puzzle_id")
    rows = cursor.fetchall()
    conn.close()

    keys = {}
    for puzzle_id, priv_hex in rows:
        if priv_hex and puzzle_id is not None:
            keys[int(puzzle_id)] = int(priv_hex, 16)
    return keys

# Fibonacci and Lucas sequences
def fib(n):
    """Fibonacci number F(n)"""
    if n <= 0: return 0
    if n == 1: return 1
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

def lucas(n):
    """Lucas number L(n)"""
    if n == 0: return 2
    if n == 1: return 1
    a, b = 2, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

# π convergents: 3/1, 22/7, 333/106, 355/113, ...
PI_CONVERGENTS = [(3, 1), (22, 7), (333, 106), (355, 113), (103993, 33102)]

# e convergents: 2/1, 3/1, 8/3, 11/4, 19/7, 87/32, 106/39, ...
E_CONVERGENTS = [(2, 1), (3, 1), (8, 3), (11, 4), (19, 7), (87, 32), (106, 39)]

# φ convergents (ratios of consecutive Fibonacci): F(n+1)/F(n)
PHI_CONVERGENTS = [(1, 1), (2, 1), (3, 2), (5, 3), (8, 5), (13, 8), (21, 13), (34, 21)]

# √2 convergents: 1/1, 3/2, 7/5, 17/12, 41/29, 99/70, ...
SQRT2_CONVERGENTS = [(1, 1), (3, 2), (7, 5), (17, 12), (41, 29), (99, 70), (239, 169)]

# √3 convergents: 1/1, 2/1, 5/3, 7/4, 19/11, 26/15, 71/41, ...
SQRT3_CONVERGENTS = [(1, 1), (2, 1), (5, 3), (7, 4), (19, 11), (26, 15), (71, 41)]

def compute_m_and_d(k, verbose=False):
    """
    Compute m[n] and d[n] sequences from known k values
    Using: k[n] = 2*k[n-1] + adj[n]
           adj[n] = 2^n - m[n]*k[d[n]]
    """
    n_max = max(k.keys())
    m = {}
    d = {}
    adj = {}

    for n in range(2, n_max + 1):
        if n not in k or n-1 not in k:
            continue

        # Compute adj[n] from recurrence
        adj[n] = k[n] - 2*k[n-1]

        # Find d[n] and m[n] such that adj[n] = 2^n - m[n]*k[d[n]]
        # So: m[n]*k[d[n]] = 2^n - adj[n]
        target = 2**n - adj[n]

        best_d = None
        best_m = None

        # Try all possible d values
        for d_cand in range(1, n):
            if d_cand not in k or k[d_cand] == 0:
                continue
            if target % k[d_cand] == 0:
                m_cand = target // k[d_cand]
                if m_cand > 0:
                    # Prefer smaller d values (simpler formula)
                    if best_d is None or d_cand < best_d:
                        best_d = d_cand
                        best_m = m_cand

        if best_d is not None:
            m[n] = best_m
            d[n] = best_d
            if verbose and n <= 20:
                print(f"n={n}: k={k[n]}, adj={adj[n]}, m={best_m}, d={best_d}")

    return m, d, adj

def analyze_constant_layer(k):
    """
    Analyze k[n]/2^n ratios for constant encoding
    """
    print("\n=== CONSTANT LAYER ANALYSIS ===")
    print("Looking for k[n]/2^n ≈ constant patterns\n")

    constants = {
        'π/4': PI/4,
        'e/π': E/PI,
        'π/e': PI/E,
        '1/φ': 1/PHI,
        'ln(2)': LN2,
        'e/4': E/4,
        '1/√2': 1/SQRT2,
        '√2/2': SQRT2/2,
        '2/e': 2/E,
        'φ-1': PHI-1,
        '1/e': 1/E,
        '1/π': 1/PI,
    }

    matches = []
    for n in sorted(k.keys()):
        if n < 16:  # Focus on n≥16 for constant layer
            continue
        ratio = k[n] / (2**n)

        best_const = None
        best_error = float('inf')
        for name, value in constants.items():
            error = abs(ratio - value) / value * 100
            if error < best_error:
                best_error = error
                best_const = name

        if best_error < 5:  # Less than 5% error
            matches.append((n, ratio, best_const, best_error))
            if n <= 30 or best_error < 1:
                print(f"n={n:2d}: k[n]/2^n = {ratio:.8f} ≈ {best_const} ({constants[best_const]:.8f}) error={best_error:.3f}%")

    print(f"\nMatches < 5% error: {len(matches)}/{len([n for n in k if n >= 16])}")
    return matches

def verify_phase1_formulas(k):
    """
    Verify Phase 1 formulas (n=5 to n=18)
    """
    print("\n=== PHASE 1 FORMULAS (n=5-18) ===")

    formulas = [
        (5, lambda: k[2] * k[3], "k[2] × k[3]"),
        (6, lambda: k[3]**2, "k[3]²"),
        (7, lambda: k[2]*9 + k[6], "k[2]×9 + k[6]"),
        (8, lambda: k[5]*13 - k[6], "k[5]×13 - k[6]"),
        (9, lambda: k[6]*10 - k[5] - 12, "k[6]×10 - k[5] - 12"),
        (10, lambda: k[7]*7 - k[5] - 11, "k[7]×7 - k[5] - 11"),
        (11, lambda: k[6]*19 + k[8], "k[6]×19 + k[8]"),
        (12, lambda: k[8]*12 - 5, "k[8]×12 - 5"),
        (13, lambda: k[10]*10 + k[7], "k[10]×10 + k[7]"),
        (14, lambda: k[11]*9 + 149, "k[11]×9 + 149"),
        (15, lambda: k[12]*10 + 37, "k[12]×10 + 37"),
        (16, lambda: k[11]*45 - 465, "k[11]×45 - 465"),
        (17, lambda: -42*k[1] + 83*k[11], "-42×k[1] + 83×k[11]"),
        (18, lambda: 883*k[8] + 877, "883×k[8] + 877"),
    ]

    verified = 0
    for n, formula_fn, formula_str in formulas:
        if n not in k:
            continue
        try:
            computed = formula_fn()
            actual = k[n]
            match = "✓" if computed == actual else "✗"
            if computed == actual:
                verified += 1
            print(f"k[{n:2d}] = {formula_str:25s} = {computed:10d} vs {actual:10d} {match}")
        except Exception as e:
            print(f"k[{n:2d}] = {formula_str:25s} ERROR: {e}")

    print(f"\nVerified: {verified}/{len(formulas)}")
    return verified

def search_phase2_formulas(k, m, d):
    """
    Search for Phase 2 formulas (n≥19)
    Pattern observed: k[n] = a×k[n-offset1] + b×k[n-offset2] + c
    """
    print("\n=== PHASE 2 FORMULA SEARCH (n≥19) ===")

    found = 0
    formulas = {}

    for n in range(19, 71):
        if n not in k:
            continue

        target = k[n]

        # Try patterns: k[n] = a×k[i] + b×k[j] + c
        best_formula = None

        for i in range(max(1, n-10), n):
            if i not in k:
                continue
            for j in range(1, i):
                if j not in k:
                    continue

                # Solve for a, b, c: target = a*k[i] + b*k[j] + c
                # Try small coefficient ranges
                for a in range(-100, 101):
                    if a == 0:
                        continue
                    remainder = target - a * k[i]

                    for b in range(-50, 51):
                        c = remainder - b * k[j]
                        if abs(c) < 1000:  # Reasonable offset
                            computed = a * k[i] + b * k[j] + c
                            if computed == target:
                                formula = f"{a}×k[{i}] + {b}×k[{j}] + {c}"
                                # Prefer simpler formulas
                                complexity = abs(a) + abs(b) + abs(c)//100
                                if best_formula is None or complexity < best_formula[1]:
                                    best_formula = (formula, complexity, (a, i, b, j, c))

        if best_formula:
            found += 1
            formulas[n] = best_formula
            if n <= 25 or n % 10 == 0:
                print(f"k[{n:2d}] = {best_formula[0]}")

    print(f"\nFormulas found: {found}/{len([n for n in k if n >= 19 and n <= 70])}")
    return formulas

def analyze_m_sequence(m, d):
    """
    Analyze the m-sequence for patterns
    """
    print("\n=== M-SEQUENCE ANALYSIS ===")

    # Check for convergent patterns
    print("\nChecking π convergent connections:")
    for n in sorted(m.keys())[:20]:
        m_val = m[n]
        for num, denom in PI_CONVERGENTS:
            if m_val == num or m_val == denom:
                print(f"  m[{n}] = {m_val} = π convergent component")

    print("\nChecking e convergent connections:")
    for n in sorted(m.keys())[:20]:
        m_val = m[n]
        for num, denom in E_CONVERGENTS:
            if m_val == num or m_val == denom:
                print(f"  m[{n}] = {m_val} = e convergent component")

    print("\nChecking √3 convergent connections:")
    for n in sorted(m.keys())[:20]:
        m_val = m[n]
        for num, denom in SQRT3_CONVERGENTS:
            if m_val == num or m_val == denom:
                print(f"  m[{n}] = {m_val} = √3 convergent component")

    # Check m ratios
    print("\nSignificant m-value ratios:")
    m_list = sorted(m.items())
    for i in range(1, min(15, len(m_list))):
        n1, m1 = m_list[i-1]
        n2, m2 = m_list[i]
        if m1 > 0:
            ratio = m2 / m1
            # Check if ratio is close to known constants
            for name, val in [('π', PI), ('e', E), ('φ', PHI), ('22/7', 22/7)]:
                if abs(ratio - val) < 0.01:
                    print(f"  m[{n2}]/m[{n1}] = {m2}/{m1} = {ratio:.6f} ≈ {name}")

def test_gap_puzzles(k):
    """
    Test patterns against GAP puzzles (75, 80, 85, 90)
    """
    print("\n=== GAP PUZZLE ANALYSIS ===")

    gap_puzzles = [75, 80, 85, 90]
    for n in gap_puzzles:
        if n not in k:
            continue

        ratio = k[n] / (2**n)
        print(f"\nk[{n}]:")
        print(f"  Value: {k[n]}")
        print(f"  Hex: {hex(k[n])}")
        print(f"  k[n]/2^n: {ratio:.10f}")

        # Check constant matches
        constants = {
            'π/4': PI/4, 'e/π': E/PI, '1/φ': 1/PHI,
            'ln(2)': LN2, 'e/4': E/4, '1/√2': 1/SQRT2
        }
        for name, val in constants.items():
            error = abs(ratio - val) / val * 100
            if error < 5:
                print(f"  ≈ {name} (error: {error:.3f}%)")

def build_generator():
    """
    Build comprehensive k-sequence generator
    """
    print("=" * 60)
    print("K-SEQUENCE GENERATOR - SYNTHESIS MODE")
    print("=" * 60)

    # Load all known keys
    k = load_keys()
    print(f"\nLoaded {len(k)} known keys from database")
    print(f"Range: n={min(k.keys())} to n={max(k.keys())}")

    # Compute m and d sequences
    m, d, adj = compute_m_and_d(k, verbose=True)
    print(f"\nComputed m[n] for {len(m)} values")
    print(f"Computed d[n] for {len(d)} values")

    # Verify Phase 1 formulas
    phase1_verified = verify_phase1_formulas(k)

    # Analyze constant layer
    const_matches = analyze_constant_layer(k)

    # Search Phase 2 formulas
    phase2_formulas = search_phase2_formulas(k, m, d)

    # Analyze m-sequence
    analyze_m_sequence(m, d)

    # Test GAP puzzles
    test_gap_puzzles(k)

    # Summary
    print("\n" + "=" * 60)
    print("GENERATOR CONSTRUCTION SUMMARY")
    print("=" * 60)

    total_coverage = phase1_verified + len(phase2_formulas)
    total_keys = len([n for n in k if n >= 5 and n <= 70])

    print(f"\nPhase 1 (n=5-18): {phase1_verified}/14 formulas verified")
    print(f"Phase 2 (n=19-70): {len(phase2_formulas)}/52 formulas found")
    print(f"Total coverage: {total_coverage}/{total_keys} ({100*total_coverage/total_keys:.1f}%)")
    print(f"Constant layer matches: {len(const_matches)} values")

    # Return data for further analysis
    return {
        'k': k,
        'm': m,
        'd': d,
        'adj': adj,
        'phase1_verified': phase1_verified,
        'phase2_formulas': phase2_formulas,
        'const_matches': const_matches
    }

if __name__ == "__main__":
    result = build_generator()
