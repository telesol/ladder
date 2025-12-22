#!/usr/bin/env python3
"""
Anchor Analysis - Find the pattern behind ultra-precise constant matches.

Hypothesis: The creator chose specific n values to force k[n]/2^n = constant.
These "anchor" values have <0.5% error. Between anchors, m[n] follows a rule.
"""

import sqlite3
import math

PI = math.pi
E = math.e
PHI = (1 + math.sqrt(5)) / 2
LN2 = math.log(2)

CONSTANTS = {
    'π/4': PI/4,      # 0.7854
    'e/π': E/PI,      # 0.8653
    '1/φ': 1/PHI,     # 0.6180
    'φ-1': PHI-1,     # 0.6180 (same!)
    'ln(2)': LN2,     # 0.6931
    'e/4': E/4,       # 0.6796
    '2/e': 2/E,       # 0.7358
    '1/√2': 1/math.sqrt(2),  # 0.7071
    '1/2': 0.5,
    '2/3': 2/3,
    '3/4': 0.75,
    '7/8': 0.875,
}

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

def find_anchors(k, threshold=0.5):
    """Find n values where k[n]/2^n matches a constant with <threshold% error"""
    anchors = []

    for n in sorted(k.keys()):
        ratio = k[n] / (2**n)

        best_const = None
        best_error = float('inf')

        for name, val in CONSTANTS.items():
            error = abs(ratio - val) / val * 100
            if error < best_error:
                best_error = error
                best_const = name

        if best_error < threshold:
            anchors.append({
                'n': n,
                'constant': best_const,
                'value': CONSTANTS[best_const],
                'actual': ratio,
                'error': best_error
            })

    return anchors

def analyze_anchor_pattern(anchors):
    """Look for patterns in anchor n values"""
    print("=" * 60)
    print("ANCHOR ANALYSIS (k[n]/2^n matches constant <0.5% error)")
    print("=" * 60)

    print("\nAnchors found:")
    for a in anchors:
        print(f"  n={a['n']:2d}: {a['constant']:6s} (error: {a['error']:.4f}%)")

    # Extract n values
    n_values = [a['n'] for a in anchors]
    print(f"\nAnchor n values: {n_values}")

    # Check for patterns
    print("\nPattern analysis:")

    # Differences between consecutive anchors
    diffs = [n_values[i+1] - n_values[i] for i in range(len(n_values)-1)]
    print(f"  Differences: {diffs}")

    # Check n mod patterns
    for mod in [2, 3, 4, 5, 6, 7, 8]:
        residues = [n % mod for n in n_values]
        unique = len(set(residues))
        print(f"  n mod {mod}: {residues} ({unique} unique)")

    # Check if anchors align with Fibonacci
    fibs = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
    fib_anchors = [n for n in n_values if n in fibs]
    print(f"  Fibonacci anchors: {fib_anchors}")

    # Check for prime pattern
    def is_prime(n):
        if n < 2: return False
        for i in range(2, int(n**0.5) + 1):
            if n % i == 0: return False
        return True

    prime_anchors = [n for n in n_values if is_prime(n)]
    print(f"  Prime anchors: {prime_anchors}")

    return n_values

def analyze_between_anchors(anchors, m, k):
    """Analyze m[n] pattern between anchor points"""
    print("\n" + "=" * 60)
    print("BETWEEN-ANCHOR ANALYSIS")
    print("=" * 60)

    anchor_ns = [a['n'] for a in anchors]

    for i in range(len(anchors) - 1):
        n1 = anchors[i]['n']
        n2 = anchors[i+1]['n']
        gap = n2 - n1

        if gap <= 1:
            continue

        print(f"\nBetween n={n1} ({anchors[i]['constant']}) and n={n2} ({anchors[i+1]['constant']}):")
        print(f"  Gap size: {gap}")

        # Look at m[n]/2^n ratios in this gap
        for n in range(n1, n2 + 1):
            if n in m:
                m_ratio = m[n] / (2**n)
                k_ratio = k[n] / (2**n) if n in k else 0
                in_anchor = "ANCHOR" if n in anchor_ns else ""
                print(f"    n={n:2d}: m/2^n={m_ratio:.6f}, k/2^n={k_ratio:.6f} {in_anchor}")

def predict_from_anchors(anchors, m, k):
    """Try to predict m[71] using anchor pattern"""
    print("\n" + "=" * 60)
    print("PREDICTION FOR n=71")
    print("=" * 60)

    # Find nearest anchors to n=71
    anchor_ns = [a['n'] for a in anchors]
    before_71 = [n for n in anchor_ns if n < 71]
    after_71 = [n for n in anchor_ns if n > 71]

    if before_71:
        print(f"Nearest anchor before 71: n={max(before_71)}")
        for a in anchors:
            if a['n'] == max(before_71):
                print(f"  Constant: {a['constant']} = {a['value']:.8f}")

    if after_71:
        print(f"Nearest anchor after 71: n={min(after_71)}")
        for a in anchors:
            if a['n'] == min(after_71):
                print(f"  Constant: {a['constant']} = {a['value']:.8f}")

    # Method 1: Linear interpolation between anchors
    if before_71 and 90 in anchor_ns:
        n_before = max(before_71)
        n_after = 90

        for a in anchors:
            if a['n'] == n_before:
                c_before = a['value']
            if a['n'] == n_after:
                c_after = a['value']

        # Linear interpolation
        t = (71 - n_before) / (n_after - n_before)
        c_71_interp = c_before + t * (c_after - c_before)
        print(f"\nMethod 1 (linear interpolation):")
        print(f"  Interpolated constant for n=71: {c_71_interp:.8f}")

        # Compute k[71] if this constant is correct
        k_71_est = int(c_71_interp * (2**71))
        print(f"  Estimated k[71]: {k_71_est}")

        # Compute m[71]
        if 70 in k:
            m_71_est = 2**71 - k_71_est + 2*k[70]
            print(f"  Estimated m[71]: {m_71_est}")

    # Method 2: Check if n=71 might be an anchor
    print("\nMethod 2 (71 as potential anchor):")
    for name, val in CONSTANTS.items():
        k_71_est = int(val * (2**71))
        if 70 in k:
            m_71_est = 2**71 - k_71_est + 2*k[70]
            print(f"  If k[71]/2^71 = {name}: k[71] = {k_71_est}, m[71] = {m_71_est}")

    # Method 3: Use m[n]/2^n pattern from nearby odd n
    print("\nMethod 3 (m-ratio from nearby odd n):")
    odd_ns = [n for n in m.keys() if n % 2 == 1 and n >= 60 and n <= 70]
    if odd_ns:
        m_ratios = [m[n] / (2**n) for n in odd_ns]
        avg_ratio = sum(m_ratios) / len(m_ratios)
        print(f"  Odd n near 71: {odd_ns}")
        print(f"  Their m[n]/2^n ratios: {[f'{r:.4f}' for r in m_ratios]}")
        print(f"  Average: {avg_ratio:.6f}")
        m_71_pred = int(avg_ratio * (2**71))
        print(f"  Predicted m[71]: {m_71_pred}")

        if 70 in k:
            k_71_pred = 2*k[70] + 2**71 - m_71_pred
            print(f"  Predicted k[71]: {k_71_pred}")
            print(f"  k[71] hex: {hex(k_71_pred)}")

def main():
    k = load_keys()
    m = compute_m(k)

    print(f"Loaded {len(k)} keys, computed {len(m)} m-values")

    # Find anchors with different thresholds
    for threshold in [0.1, 0.25, 0.5]:
        anchors = find_anchors(k, threshold)
        print(f"\nAnchors with <{threshold}% error: {len(anchors)}")

    # Use 0.25% threshold for detailed analysis
    anchors = find_anchors(k, threshold=0.25)
    anchor_ns = analyze_anchor_pattern(anchors)

    analyze_between_anchors(anchors, m, k)
    predict_from_anchors(anchors, m, k)

if __name__ == "__main__":
    main()
