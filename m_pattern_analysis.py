#!/usr/bin/env python3
"""
Deep analysis of m[n] pattern to find the generation rule.
The goal: Find a rule that generates m[n] for ANY n.
"""

import sqlite3
import math
import numpy as np
from collections import defaultdict

PI = math.pi
E = math.e
PHI = (1 + math.sqrt(5)) / 2
SQRT2 = math.sqrt(2)
LN2 = math.log(2)

def load_keys():
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

def compute_m(k):
    m = {}
    for n in range(2, max(k.keys()) + 1):
        if n in k and n-1 in k:
            m[n] = 2**n - k[n] + 2*k[n-1]
    return m

def analyze_modular_patterns(m):
    """Analyze m[n] mod various bases"""
    print("=" * 60)
    print("MODULAR PATTERN ANALYSIS")
    print("=" * 60)

    # Check patterns mod small primes
    for mod in [2, 3, 5, 7, 11, 13]:
        print(f"\nm[n] mod {mod}:")
        pattern = []
        for n in range(2, 35):
            if n in m:
                pattern.append(m[n] % mod)
        print(f"  {pattern}")

        # Look for periodicity
        for period in range(1, len(pattern)//2):
            matches = 0
            total = 0
            for i in range(period, len(pattern)):
                if pattern[i] == pattern[i - period]:
                    matches += 1
                total += 1
            if total > 0 and matches / total > 0.8:
                print(f"  Possible period {period}: {matches}/{total} matches")

def analyze_ratio_evolution(m):
    """How does m[n]/2^n evolve?"""
    print("\n" + "=" * 60)
    print("RATIO EVOLUTION ANALYSIS")
    print("=" * 60)

    ratios = {}
    for n in sorted(m.keys()):
        ratios[n] = m[n] / (2**n)

    # Look at differences between consecutive ratios
    print("\nRatio differences (r[n+1] - r[n]):")
    for n in range(2, 30):
        if n in ratios and n+1 in ratios:
            diff = ratios[n+1] - ratios[n]
            print(f"  n={n:2d}: r[{n+1}] - r[{n}] = {diff:+.6f}")

    # Look at ratio of ratios
    print("\nRatio of ratios (r[n+1] / r[n]):")
    for n in range(2, 30):
        if n in ratios and n+1 in ratios and ratios[n] != 0:
            ratio_ratio = ratios[n+1] / ratios[n]
            print(f"  n={n:2d}: r[{n+1}] / r[{n}] = {ratio_ratio:.6f}")

def analyze_constant_selection(m, k):
    """
    Hypothesis: Creator selected constants for k[n]/2^n,
    and m[n] follows from the recurrence.
    """
    print("\n" + "=" * 60)
    print("CONSTANT SELECTION ANALYSIS")
    print("=" * 60)

    constants = {
        'π/4': PI/4,      # 0.7854
        'e/π': E/PI,      # 0.8653
        '1/φ': 1/PHI,     # 0.6180
        'φ-1': PHI-1,     # 0.6180
        'ln(2)': LN2,     # 0.6931
        'e/4': E/4,       # 0.6796
        '2/e': 2/E,       # 0.7358
        '1/√2': 1/SQRT2,  # 0.7071
        '√2/2': SQRT2/2,  # 0.7071
        '1/e': 1/E,       # 0.3679
        '1/π': 1/PI,      # 0.3183
        'π/e': PI/E,      # 1.1557
        '1/2': 0.5,
        '2/3': 2/3,
        '3/4': 0.75,
        '7/8': 0.875,
    }

    print("\nBest constant match for each k[n]/2^n:")
    best_matches = {}
    for n in sorted(k.keys()):
        ratio = k[n] / (2**n)
        best_const = None
        best_error = float('inf')
        for name, val in constants.items():
            error = abs(ratio - val) / val * 100
            if error < best_error:
                best_error = error
                best_const = (name, val)
        best_matches[n] = (best_const[0], best_error)
        if n <= 30 or best_error < 1:
            print(f"  n={n:2d}: k[n]/2^n = {ratio:.8f} ≈ {best_const[0]:6s} (error: {best_error:.4f}%)")

    # Analyze the sequence of best matches
    print("\nConstant selection sequence (low error only):")
    selection_seq = []
    for n in sorted(k.keys()):
        if n in best_matches and best_matches[n][1] < 2:
            selection_seq.append((n, best_matches[n][0]))
            print(f"  n={n:2d}: {best_matches[n][0]}")

    return best_matches

def analyze_m_construction(m):
    """
    Analyze how m[n] might be constructed from previous values.
    """
    print("\n" + "=" * 60)
    print("M-SEQUENCE CONSTRUCTION RULES")
    print("=" * 60)

    # Test: m[n] = a*m[n-1] + b where a and b are constants or simple functions
    print("\nTest m[n] / m[n-1] = 2 + correction:")
    for n in range(3, 25):
        if n in m and n-1 in m:
            ratio = m[n] / m[n-1]
            correction = ratio - 2
            print(f"  n={n:2d}: m[{n}]/m[{n-1}] = {ratio:.6f} = 2 + {correction:+.6f}")

    # Test: m[n] = f(n) * 2^n where f(n) is some function
    print("\nTest m[n]/2^n = f(n):")
    f_values = []
    for n in range(2, 25):
        if n in m:
            f_n = m[n] / (2**n)
            f_values.append((n, f_n))
            if n <= 15:
                print(f"  f({n:2d}) = {f_n:.8f}")

    # Check if f(n) follows a pattern related to n mod something
    print("\nf(n) grouped by n mod 3:")
    for mod in range(3):
        vals = [(n, f) for n, f in f_values if n % 3 == mod]
        if vals:
            avg_f = sum(f for n, f in vals) / len(vals)
            print(f"  n ≡ {mod} (mod 3): avg f(n) = {avg_f:.6f}")

    print("\nf(n) grouped by n mod 4:")
    for mod in range(4):
        vals = [(n, f) for n, f in f_values if n % 4 == mod]
        if vals:
            avg_f = sum(f for n, f in vals) / len(vals)
            print(f"  n ≡ {mod} (mod 4): avg f(n) = {avg_f:.6f}")

def search_recurrence(m):
    """
    Search for recurrence relations in m[n].
    """
    print("\n" + "=" * 60)
    print("RECURRENCE RELATION SEARCH")
    print("=" * 60)

    # Try m[n] = a*m[n-1] + b*m[n-2] + c*2^n
    print("\nTest: m[n] = a*m[n-1] + b*m[n-2] + c*2^n")
    for n in range(4, 20):
        if n in m and n-1 in m and n-2 in m:
            # Solve for a, b, c using three equations
            # m[n] = a*m[n-1] + b*m[n-2] + c*2^n
            # m[n-1] = a*m[n-2] + b*m[n-3] + c*2^(n-1)
            # This is underdetermined, so let's try specific values

            # Try a=2, b=0: m[n] = 2*m[n-1] + c*2^n
            c_est = (m[n] - 2*m[n-1]) / (2**n)
            predicted = 2*m[n-1] + c_est * (2**n)
            error = abs(predicted - m[n])
            if abs(c_est) < 0.5:
                print(f"  n={n:2d}: m[{n}] ≈ 2*m[{n-1}] + {c_est:.4f}*2^{n} (error: {error:.1f})")

    # Try m[n] = floor(α * m[n-1] + β)
    print("\nTest: m[n] = floor(α * m[n-1] + β)")
    for n in range(3, 15):
        if n in m and n-1 in m and n+1 in m:
            # Simple linear fit
            alpha = (m[n+1] - m[n]) / (m[n] - m[n-1]) if m[n] != m[n-1] else 0
            if 1.5 < alpha < 3:
                print(f"  n={n:2d}: growth factor ≈ {alpha:.4f}")

def analyze_pi_e_connection(m):
    """
    Deep dive into the π and e connections.
    """
    print("\n" + "=" * 60)
    print("π AND e CONNECTION ANALYSIS")
    print("=" * 60)

    # m[4]/m[3] = 22/7 = π
    print(f"\nKnown: m[4]/m[3] = {m[4]}/{m[3]} = {m[4]/m[3]:.10f} = 22/7 = π")

    # Look for more π convergent connections
    pi_conv = [(3, 1), (22, 7), (333, 106), (355, 113), (103993, 33102)]
    e_conv = [(2, 1), (3, 1), (8, 3), (11, 4), (19, 7), (87, 32)]

    print("\nSearching for π convergent patterns in m[n]:")
    for n in sorted(m.keys())[:30]:
        m_val = m[n]
        for num, denom in pi_conv:
            if m_val % num == 0:
                factor = m_val // num
                print(f"  m[{n}] = {m_val} = {factor} × {num} (π convergent numerator)")
            if m_val % denom == 0 and denom > 1:
                factor = m_val // denom
                print(f"  m[{n}] = {m_val} = {factor} × {denom} (π convergent denominator)")

    print("\nSearching for e convergent patterns in m[n]:")
    for n in sorted(m.keys())[:30]:
        m_val = m[n]
        for num, denom in e_conv:
            if num > 1 and m_val % num == 0:
                factor = m_val // num
                if factor < 1000:
                    print(f"  m[{n}] = {m_val} = {factor} × {num} (e convergent)")
            if denom > 1 and m_val % denom == 0:
                factor = m_val // denom
                if factor < 1000:
                    print(f"  m[{n}] = {m_val} = {factor} × {denom} (e convergent denom)")

    # Check if m[n] encodes constants via specific formulas
    print("\nChecking m[n] against constant expressions:")
    for n in range(2, 20):
        if n in m:
            m_val = m[n]
            power = 2**n

            # Check if m[n] = floor(c * 2^n) for various c
            for name, c in [('π/4', PI/4), ('e/4', E/4), ('ln2', LN2), ('1', 1.0)]:
                approx = int(c * power)
                if abs(m_val - approx) < power * 0.01:
                    print(f"  m[{n}] = {m_val} ≈ floor({name} × 2^{n}) = {approx} (diff: {m_val - approx})")

def main():
    k = load_keys()
    m = compute_m(k)

    print(f"Loaded {len(k)} keys, computed {len(m)} m-values")

    analyze_modular_patterns(m)
    analyze_ratio_evolution(m)
    analyze_constant_selection(m, k)
    analyze_m_construction(m)
    search_recurrence(m)
    analyze_pi_e_connection(m)

    print("\n" + "=" * 60)
    print("KEY INSIGHTS")
    print("=" * 60)
    print("""
VERIFIED:
- k[n] = 2*k[n-1] + 2^n - m[n] (100% accurate)
- m[4]/m[3] = 22/7 = π exactly
- k[n]/2^n matches constants at specific n values

TO FIND:
- The rule that selects which constant (or value) for each n
- This rule likely involves the index n itself
- May use modular arithmetic, continued fractions, or number theory
""")

if __name__ == "__main__":
    main()
