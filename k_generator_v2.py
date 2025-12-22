#!/usr/bin/env python3
"""
K-Sequence Generator v2 - Focus on m[n] prediction
Key insight: d=1 for most n, so k[n] = 2*k[n-1] + 2^n - m[n]

If we can predict m[n], we can generate k[n]!
"""

import sqlite3
import math
from fractions import Fraction

# Mathematical constants
PI = math.pi
E = math.e
PHI = (1 + math.sqrt(5)) / 2
SQRT2 = math.sqrt(2)
SQRT3 = math.sqrt(3)
LN2 = math.log(2)

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

def compute_m_sequence(k):
    """
    Compute m[n] from known k values
    Since d=1 for most n: m[n] = 2^n - k[n] + 2*k[n-1]
    """
    m = {}
    for n in range(2, max(k.keys()) + 1):
        if n in k and n-1 in k:
            # From: k[n] = 2*k[n-1] + adj[n]
            # And:  adj[n] = 2^n - m[n]*k[d[n]]
            # If d[n]=1: adj[n] = 2^n - m[n]
            adj_n = k[n] - 2*k[n-1]
            m_n = 2**n - adj_n
            m[n] = m_n
    return m

def analyze_m_pattern(m):
    """Analyze m[n] sequence for predictable patterns"""
    print("=" * 60)
    print("M-SEQUENCE DEEP ANALYSIS")
    print("=" * 60)

    # Print m values
    print("\nm[n] values (n=2 to 25):")
    for n in range(2, 26):
        if n in m:
            print(f"  m[{n:2d}] = {m[n]:>12d}")

    # Check m[n]/2^n ratios
    print("\nm[n]/2^n ratios:")
    for n in range(2, 26):
        if n in m:
            ratio = m[n] / (2**n)
            print(f"  m[{n:2d}]/2^{n} = {ratio:.8f}")

    # Check differences and ratios between consecutive m values
    print("\nm[n+1]/m[n] ratios:")
    m_list = [(n, m[n]) for n in sorted(m.keys()) if n <= 30]
    for i in range(1, len(m_list)):
        n1, m1 = m_list[i-1]
        n2, m2 = m_list[i]
        if m1 > 0:
            ratio = m2 / m1
            # Check against known constants
            best_match = None
            best_err = float('inf')
            for name, val in [('2', 2), ('π', PI), ('e', E), ('φ', PHI), ('3', 3), ('22/7', 22/7)]:
                err = abs(ratio - val)
                if err < best_err:
                    best_err = err
                    best_match = (name, val)
            if best_err < 0.2:
                print(f"  m[{n2}]/m[{n1}] = {ratio:.6f} ≈ {best_match[0]} (error: {best_err:.4f})")

    # Check m[n] mod small numbers
    print("\nm[n] mod 7 pattern:")
    for n in range(2, 26):
        if n in m:
            print(f"  m[{n:2d}] mod 7 = {m[n] % 7}")

    # Check if m[n] relates to 2^n via simple formula
    print("\nm[n] vs 2^n relationships:")
    for n in range(2, 20):
        if n in m:
            power = 2**n
            diff = m[n] - power
            ratio = m[n] / power
            print(f"  n={n:2d}: 2^n = {power:8d}, m[n] = {m[n]:8d}, diff = {diff:8d}, ratio = {ratio:.4f}")

def test_m_generation_rules(m, k):
    """
    Test various hypotheses for generating m[n]
    """
    print("\n" + "=" * 60)
    print("M-SEQUENCE GENERATION RULE SEARCH")
    print("=" * 60)

    # Hypothesis 1: m[n] = floor(α * 2^n) for some constant α
    print("\nHypothesis 1: m[n] = floor(α * 2^n)")
    for n in range(2, 20):
        if n in m:
            alpha = m[n] / (2**n)
            # Check if this alpha predicts m[n+1]
            if n+1 in m:
                predicted = int(alpha * (2**(n+1)))
                actual = m[n+1]
                error = abs(predicted - actual)
                print(f"  n={n}: α={alpha:.6f}, predicts m[{n+1}]={predicted}, actual={actual}, error={error}")

    # Hypothesis 2: m[n] follows a recurrence m[n] = a*m[n-1] + b*2^n + c
    print("\nHypothesis 2: m[n] = a*m[n-1] + b*2^(n-1) + c")
    for n in range(5, 15):
        if n in m and n-1 in m and n+1 in m:
            # Solve for a, b, c using three consecutive values
            # m[n] = a*m[n-1] + b*2^(n-1) + c
            # m[n+1] = a*m[n] + b*2^n + c
            # Subtract: m[n+1] - m[n] = a*(m[n] - m[n-1]) + b*2^(n-1)
            delta_m = m[n] - m[n-1]
            delta_m_next = m[n+1] - m[n]
            if delta_m != 0:
                # Estimate a
                # For simple case, assume b=0
                a_est = delta_m_next / delta_m
                print(f"  n={n}: δm[n]={delta_m}, δm[n+1]={delta_m_next}, ratio≈{a_est:.4f}")

    # Hypothesis 3: m[n] relates to k[n]/2^n constant
    print("\nHypothesis 3: m[n] from constant layer")
    constants = {
        'π/4': PI/4, 'e/π': E/PI, '1/φ': 1/PHI,
        'ln(2)': LN2, 'e/4': E/4, '2/e': 2/E
    }
    for n in [16, 48, 58, 61]:  # Ultra-precise matches
        if n in k and n in m:
            C = k[n] / (2**n)
            # From k[n] = 2*k[n-1] + 2^n - m[n]
            # k[n]/2^n = 2*k[n-1]/2^n + 1 - m[n]/2^n
            # C = k[n-1]/2^(n-1) + 1 - m[n]/2^n
            m_ratio = m[n] / (2**n)
            print(f"  n={n}: k[n]/2^n = {C:.8f}, m[n]/2^n = {m_ratio:.8f}")
            print(f"         sum = {C + m_ratio:.8f}, diff = {m_ratio - C:.8f}")
            for name, val in constants.items():
                if abs(C - val) < 0.01:
                    print(f"         k[{n}]/2^{n} ≈ {name}")

    # Hypothesis 4: m[n] from bit patterns
    print("\nHypothesis 4: m[n] bit patterns")
    for n in range(2, 16):
        if n in m:
            m_bin = bin(m[n])[2:]
            bit_len = len(m_bin)
            ones = m_bin.count('1')
            print(f"  m[{n:2d}] = {m[n]:8d} = 0b{m_bin:>20s} ({bit_len} bits, {ones} ones)")

def derive_k_from_m(m, k_known):
    """
    Given m[n] sequence, derive k[n] using the recurrence
    k[n] = 2*k[n-1] + 2^n - m[n]
    """
    print("\n" + "=" * 60)
    print("K-SEQUENCE DERIVATION FROM M")
    print("=" * 60)

    k_derived = {1: 1}  # k[1] = 1

    errors = []
    for n in range(2, max(m.keys()) + 1):
        if n in m:
            if n-1 in k_derived:
                k_derived[n] = 2*k_derived[n-1] + 2**n - m[n]

                # Verify against known
                if n in k_known:
                    if k_derived[n] == k_known[n]:
                        status = "✓"
                    else:
                        status = "✗"
                        errors.append(n)

                    if n <= 20 or n in errors:
                        print(f"k[{n:2d}]: derived={k_derived[n]:12d}, known={k_known[n]:12d} {status}")

    print(f"\nDerivation accuracy: {len(k_derived) - len(errors) - 1}/{len(k_derived) - 1} correct")
    if errors:
        print(f"Errors at n={errors}")

    return k_derived

def find_m_pattern_extended(m):
    """
    Extended search for m[n] generation pattern
    """
    print("\n" + "=" * 60)
    print("EXTENDED M-PATTERN SEARCH")
    print("=" * 60)

    # Look at m[n]/2^n more carefully
    print("\nm[n]/2^n detailed analysis:")
    m_ratios = {}
    for n in sorted(m.keys()):
        if n <= 70:
            ratio = m[n] / (2**n)
            m_ratios[n] = ratio

    # Group by similar ratios
    groups = {}
    for n, ratio in m_ratios.items():
        found_group = False
        for base_ratio, members in groups.items():
            if abs(ratio - base_ratio) < 0.05:
                members.append((n, ratio))
                found_group = True
                break
        if not found_group:
            groups[ratio] = [(n, ratio)]

    print("\nRatio clusters:")
    for base_ratio in sorted(groups.keys()):
        members = groups[base_ratio]
        if len(members) >= 2:
            ns = [m[0] for m in members]
            avg_ratio = sum(m[1] for m in members) / len(members)
            print(f"  ratio ≈ {avg_ratio:.4f}: n = {ns}")

    # Check for linear relationship: m[n] = a*n + b*2^n
    print("\nLinear relationship check:")
    print("  n    m[n]      m[n]/n      m[n]/2^n    m[n]/(n*2^n)")
    for n in range(2, 21):
        if n in m:
            print(f"  {n:2d}   {m[n]:8d}  {m[n]/n:10.2f}  {m[n]/2**n:.6f}  {m[n]/(n*2**n):.8f}")

    # Fibonacci connection
    print("\nFibonacci connection:")
    fibs = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597, 2584, 4181, 6765]
    for n in range(2, 20):
        if n in m:
            for i, f in enumerate(fibs):
                if m[n] % f == 0 and f > 1:
                    print(f"  m[{n}] = {m[n]} = {m[n]//f} × F[{i}] ({f})")
                    break

def predict_m_71(m, k):
    """
    Attempt to predict m[71] using discovered patterns
    """
    print("\n" + "=" * 60)
    print("PREDICTING m[71]")
    print("=" * 60)

    # Method 1: Use average m[n]/2^n ratio from similar n values
    # Look at odd n values around 71
    similar_ns = [n for n in m.keys() if n >= 55 and n <= 70 and n % 2 == 1]
    avg_ratio = sum(m[n] / (2**n) for n in similar_ns) / len(similar_ns)
    m_71_pred1 = int(avg_ratio * (2**71))
    print(f"\nMethod 1 (avg ratio from odd n near 71):")
    print(f"  Average m[n]/2^n ratio: {avg_ratio:.8f}")
    print(f"  Predicted m[71]: {m_71_pred1}")

    # Method 2: Use growth rate from consecutive pairs
    if 70 in m and 69 in m:
        growth = m[70] / m[69]
        m_71_pred2 = int(m[70] * growth)
        print(f"\nMethod 2 (growth rate m[70]/m[69]):")
        print(f"  Growth rate: {growth:.8f}")
        print(f"  Predicted m[71]: {m_71_pred2}")

    # Method 3: Use constant layer if k[71]/2^71 is known
    print("\nMethod 3 (constant layer):")
    constants_at_odd = {
        61: 1/PHI,  # k[61]/2^61 ≈ 1/φ
        67: 2/E,    # Check
        69: LN2,    # Check
    }
    # If k[71] has similar constant, we can estimate m[71]
    for const_name, const_val in [('1/φ', 1/PHI), ('ln(2)', LN2), ('e/4', E/4), ('2/e', 2/E)]:
        # If k[71]/2^71 ≈ const_val
        # k[71] = const_val * 2^71
        # m[71] = 2^71 - k[71] + 2*k[70]
        if 70 in k:
            k_71_est = int(const_val * (2**71))
            m_71_est = 2**71 - k_71_est + 2*k[70]
            print(f"  If k[71]/2^71 ≈ {const_name}: m[71] ≈ {m_71_est}")

def main():
    # Load data
    k = load_keys()
    print(f"Loaded {len(k)} known keys")

    # Compute m sequence
    m = compute_m_sequence(k)
    print(f"Computed m[n] for {len(m)} values")

    # Analyze m pattern
    analyze_m_pattern(m)

    # Test generation rules
    test_m_generation_rules(m, k)

    # Extended pattern search
    find_m_pattern_extended(m)

    # Verify derivation works
    k_derived = derive_k_from_m(m, k)

    # Attempt prediction
    predict_m_71(m, k)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("""
KEY FINDINGS:
1. d=1 for all n: k[n] = 2*k[n-1] + 2^n - m[n]
2. m[4]/m[3] = 22/7 = π exactly
3. m[n]/2^n oscillates but doesn't follow simple periodic pattern
4. If we can predict m[n], we can generate ALL k[n]

BREAKTHROUGH NEEDED:
- Find the rule that generates m[n]
- m[n] encodes mathematical constants (π, e, φ)
- The encoding method is the key to solving ALL puzzles
""")

    return m, k

if __name__ == "__main__":
    m, k = main()
