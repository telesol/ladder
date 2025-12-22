#!/usr/bin/env python3
"""
Deep modular pattern analysis for m-sequence
Focus on finding construction rules through advanced techniques
"""

import json
from typing import List, Dict, Tuple
import numpy as np

def load_m_sequence():
    """Load m-sequence from task specification"""
    m_seq = {
        2: 3,
        3: 7,
        4: 22,
        5: 27,
        6: 57,
        7: 150,
        8: 184,
        9: 493,
        10: 1444,
        11: 1921,
        12: 3723,
        13: 8342,
        14: 16272,
        15: 26989,
        16: 67760
    }
    return m_seq

def analyze_fibonacci_like_mod_p(m_seq: Dict[int, int], p: int):
    """Check if m[n] ≡ a*m[n-1] + b*m[n-2] (mod p) with different (a,b) per n"""

    print(f"\n{'=' * 80}")
    print(f"FIBONACCI-LIKE ANALYSIS mod {p}")
    print(f"{'=' * 80}")

    print(f"\nChecking if coefficients (a, b) vary with n or n mod k:")

    n_values = sorted(m_seq.keys())
    residues = {n: m_seq[n] % p for n in n_values}

    # For each n, compute what (a, b) would satisfy m[n] ≡ a*m[n-1] + b*m[n-2] (mod p)
    print(f"\nn   | m[n-2] | m[n-1] | m[n] | (a,b) such that m[n]≡a*m[n-1]+b*m[n-2] (mod {p})")
    print("-" * 100)

    coeffs = []
    for i in range(2, len(n_values)):
        n = n_values[i]
        n1 = n_values[i-1]
        n2 = n_values[i-2]

        r_n = residues[n]
        r_n1 = residues[n1]
        r_n2 = residues[n2]

        # Find (a, b) such that a*r_n1 + b*r_n2 ≡ r_n (mod p)
        found = []
        for a in range(p):
            for b in range(p):
                if (a * r_n1 + b * r_n2) % p == r_n:
                    found.append((a, b))

        coeffs.append((n, found))
        print(f"{n:2d}  | {r_n2:6d} | {r_n1:6d} | {r_n:4d} | {found[:5] if len(found) <= 5 else found[:3] + ['...']}")

    # Check if coefficients follow a pattern based on n mod something
    print(f"\n{'=' * 80}")
    print(f"PATTERN IN COEFFICIENTS:")
    print(f"{'=' * 80}")

    # For small p, check if first coefficient choice follows a cycle
    if p <= 7:
        print(f"\nUsing first valid (a,b) for each n:")
        chosen_coeffs = []
        for n, found in coeffs:
            if found:
                chosen_coeffs.append((n, found[0]))
                print(f"n={n:2d} (n mod 7={n%7}): (a,b) = {found[0]}")

def analyze_convergent_patterns_mod_7(m_seq: Dict[int, int]):
    """Check if m[n] mod 7 relates to continued fraction convergents"""

    print(f"\n{'=' * 80}")
    print(f"CONVERGENT PATTERNS mod 7")
    print(f"{'=' * 80}")

    print(f"\nSince m[4]/m[3] = 22/7 is a π convergent, check if pattern continues:")

    n_values = sorted(m_seq.keys())

    print(f"\nn   | m[n]     | m[n]/m[n-1]    | m[n] mod 7 | m[n-1] mod 7")
    print("-" * 80)

    for i in range(1, len(n_values)):
        n = n_values[i]
        n1 = n_values[i-1]

        ratio = m_seq[n] / m_seq[n1]
        mod7 = m_seq[n] % 7
        mod7_prev = m_seq[n1] % 7

        print(f"{n:2d}  | {m_seq[n]:8d} | {ratio:14.6f} | {mod7:10d} | {mod7_prev:12d}")

def analyze_ratio_patterns_mod_7(m_seq: Dict[int, int]):
    """Analyze if m[n]*m[n-2] has special mod 7 properties"""

    print(f"\n{'=' * 80}")
    print(f"PRODUCT ANALYSIS mod 7")
    print(f"{'=' * 80}")

    print(f"\nChecking products and differences modulo 7:")

    n_values = sorted(m_seq.keys())

    print(f"\nn   | m[n]*m[n-2] mod 7 | m[n]^2 mod 7 | m[n]-m[n-1] mod 7")
    print("-" * 80)

    for i in range(2, len(n_values)):
        n = n_values[i]
        n1 = n_values[i-1]
        n2 = n_values[i-2]

        prod = (m_seq[n] * m_seq[n2]) % 7
        sq = (m_seq[n] ** 2) % 7
        diff = (m_seq[n] - m_seq[n1]) % 7

        print(f"{n:2d}  | {prod:17d} | {sq:12d} | {diff:17d}")

def analyze_higher_order_recurrence_mod_7(m_seq: Dict[int, int]):
    """Try order-3 recurrence: m[n] ≡ a*m[n-1] + b*m[n-2] + c*m[n-3] (mod 7)"""

    p = 7
    print(f"\n{'=' * 80}")
    print(f"ORDER-3 RECURRENCE mod {p}")
    print(f"{'=' * 80}")

    print(f"\nSearching for: m[n] ≡ a*m[n-1] + b*m[n-2] + c*m[n-3] (mod {p})")

    n_values = sorted(m_seq.keys())
    residues = {n: m_seq[n] % p for n in n_values}

    # Brute force search
    for a in range(p):
        for b in range(p):
            for c in range(p):
                valid = True
                for i in range(3, min(len(n_values), 15)):
                    n = n_values[i]
                    n1 = n_values[i-1]
                    n2 = n_values[i-2]
                    n3 = n_values[i-3]

                    predicted = (a * residues[n1] + b * residues[n2] + c * residues[n3]) % p
                    if predicted != residues[n]:
                        valid = False
                        break

                if valid:
                    print(f"\n*** FOUND: m[n] ≡ {a}*m[n-1] + {b}*m[n-2] + {c}*m[n-3] (mod {p}) ***")

                    # Verify on all values
                    print(f"\nVerification:")
                    for i in range(3, len(n_values)):
                        n = n_values[i]
                        n1 = n_values[i-1]
                        n2 = n_values[i-2]
                        n3 = n_values[i-3]

                        predicted = (a * residues[n1] + b * residues[n2] + c * residues[n3]) % p
                        actual = residues[n]
                        match = "✓" if predicted == actual else "✗"
                        print(f"n={n:2d}: {a}*{residues[n1]} + {b}*{residues[n2]} + {c}*{residues[n3]} ≡ {predicted} ≡ {actual} (mod {p}) {match}")

                    return (a, b, c)

    print(f"\nNo order-3 recurrence found mod {p}")
    return None

def analyze_quadratic_congruence_mod_7(m_seq: Dict[int, int]):
    """Check if m[n] satisfies quadratic congruences"""

    p = 7
    print(f"\n{'=' * 80}")
    print(f"QUADRATIC CONGRUENCES mod {p}")
    print(f"{'=' * 80}")

    n_values = sorted(m_seq.keys())

    print(f"\nChecking if m[n]^2 relates to m[n±k] mod {p}:")

    print(f"\nn   | m[n] | m[n]^2 | m[n]^2 mod {p} | Relations")
    print("-" * 80)

    for i in range(len(n_values)):
        n = n_values[i]
        m = m_seq[n]
        sq = m ** 2
        sq_mod = sq % p

        relations = []

        # Check if m[n]^2 ≡ m[k] (mod 7) for some k
        for k in n_values:
            if (m_seq[k] % p) == sq_mod and k != n:
                relations.append(f"≡ m[{k}]")

        rel_str = ", ".join(relations) if relations else "-"
        print(f"{n:2d}  | {m:4d} | {sq:6d} | {sq_mod:14d} | {rel_str}")

def find_generating_function_mod_7(m_seq: Dict[int, int]):
    """Try to find if m[n] mod 7 can be expressed as a simple function of n"""

    p = 7
    print(f"\n{'=' * 80}")
    print(f"GENERATING FUNCTION mod {p}")
    print(f"{'=' * 80}")

    n_values = sorted(m_seq.keys())
    residues = [m_seq[n] % p for n in n_values]

    print(f"\nTrying: m[n] ≡ a*n^2 + b*n + c (mod {p})")

    # Try quadratic in n
    for a in range(p):
        for b in range(p):
            for c in range(p):
                valid = True
                for i, n in enumerate(n_values):
                    predicted = (a * n * n + b * n + c) % p
                    if predicted != residues[i]:
                        valid = False
                        break

                if valid:
                    print(f"\n*** FOUND: m[n] ≡ {a}*n^2 + {b}*n + {c} (mod {p}) ***")

                    for i, n in enumerate(n_values):
                        predicted = (a * n * n + b * n + c) % p
                        actual = residues[i]
                        print(f"n={n:2d}: {a}*{n}^2 + {b}*{n} + {c} ≡ {predicted} ≡ {actual} (mod {p})")

                    return (a, b, c)

    print(f"\nNo quadratic function m[n] ≡ a*n^2 + b*n + c found")

    # Try other functions
    print(f"\nTrying: m[n] ≡ a*2^n + b (mod {p})")
    for a in range(p):
        for b in range(p):
            valid = True
            for i, n in enumerate(n_values):
                predicted = (a * pow(2, n, p) + b) % p
                if predicted != residues[i]:
                    valid = False
                    break

            if valid:
                print(f"\n*** FOUND: m[n] ≡ {a}*2^n + {b} (mod {p}) ***")
                return (a, b)

    print(f"\nNo exponential function m[n] ≡ a*2^n + b found")

def analyze_matrix_recurrence_mod_7(m_seq: Dict[int, int]):
    """Check if m[n] follows a matrix recurrence mod 7"""

    p = 7
    print(f"\n{'=' * 80}")
    print(f"MATRIX RECURRENCE mod {p}")
    print(f"{'=' * 80}")

    print(f"\nFor Fibonacci-like sequences, we have:")
    print(f"[m[n]  ]   [a b] [m[n-1]]")
    print(f"[m[n-1]] = [1 0] [m[n-2]]")
    print(f"\nSearching for 2x2 matrix [a,b; 1,0] that works mod {p}...")

    n_values = sorted(m_seq.keys())
    residues = {n: m_seq[n] % p for n in n_values}

    for a in range(p):
        for b in range(p):
            valid = True
            for i in range(2, len(n_values)):
                n = n_values[i]
                n1 = n_values[i-1]
                n2 = n_values[i-2]

                # Apply matrix: m[n] = a*m[n-1] + b*m[n-2]
                predicted = (a * residues[n1] + b * residues[n2]) % p
                if predicted != residues[n]:
                    valid = False
                    break

            if valid:
                print(f"\n*** FOUND: Matrix [[{a}, {b}], [1, 0]] (mod {p}) ***")
                print(f"This means: m[n] ≡ {a}*m[n-1] + {b}*m[n-2] (mod {p})")

                # Compute eigenvalues mod 7 (approximate)
                # λ^2 - a*λ - b = 0
                print(f"\nCharacteristic equation: λ^2 - {a}λ - {b} ≡ 0 (mod {p})")

                # Try all λ mod 7
                eigenvalues = []
                for lam in range(p):
                    if (lam*lam - a*lam - b) % p == 0:
                        eigenvalues.append(lam)

                if eigenvalues:
                    print(f"Eigenvalues mod {p}: {eigenvalues}")

                return (a, b)

    print(f"\nNo 2x2 matrix recurrence found")
    return None

def main():
    print("=" * 80)
    print("DEEP MODULAR CONSTRUCTION ANALYSIS")
    print("=" * 80)

    m_seq = load_m_sequence()

    print(f"\nLoaded {len(m_seq)} values: m[2] to m[{max(m_seq.keys())}]")
    print(f"Values: {list(m_seq.values())}")

    # Run all analyses
    analyze_fibonacci_like_mod_p(m_seq, 7)
    analyze_convergent_patterns_mod_7(m_seq)
    analyze_ratio_patterns_mod_7(m_seq)
    analyze_higher_order_recurrence_mod_7(m_seq)
    analyze_quadratic_congruence_mod_7(m_seq)
    find_generating_function_mod_7(m_seq)
    analyze_matrix_recurrence_mod_7(m_seq)

    # Try smaller primes too
    for p in [2, 3, 5]:
        print(f"\n{'=' * 80}")
        print(f"HIGHER ORDER RECURRENCE mod {p}")
        print(f"{'=' * 80}")

        # Try order-3 for smaller primes
        n_values = sorted(m_seq.keys())
        residues = {n: m_seq[n] % p for n in n_values}

        found = False
        for a in range(p):
            for b in range(p):
                for c in range(p):
                    valid = True
                    for i in range(3, len(n_values)):
                        n = n_values[i]
                        n1 = n_values[i-1]
                        n2 = n_values[i-2]
                        n3 = n_values[i-3]

                        predicted = (a * residues[n1] + b * residues[n2] + c * residues[n3]) % p
                        if predicted != residues[n]:
                            valid = False
                            break

                    if valid:
                        print(f"\n*** FOUND mod {p}: m[n] ≡ {a}*m[n-1] + {b}*m[n-2] + {c}*m[n-3] (mod {p}) ***")
                        found = True
                        break
                if found:
                    break
            if found:
                break

        if not found:
            print(f"\nNo order-3 recurrence found mod {p}")

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
