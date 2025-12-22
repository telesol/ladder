#!/usr/bin/env python3
"""
Analysis of m[n] mod 7 with focus on skip-2 pattern
Since coefficients show a=0 dominance, analyze m[n] vs m[n-2] relationship
"""

import json
from typing import Dict

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

def analyze_skip2_pattern_mod7(m_seq: Dict[int, int]):
    """Analyze m[n] vs m[n-2] modulo 7"""

    p = 7
    print("=" * 80)
    print("SKIP-2 PATTERN ANALYSIS mod 7")
    print("=" * 80)

    n_values = sorted(m_seq.keys())
    residues = {n: m_seq[n] % p for n in n_values}

    print("\nSince many coefficients showed (a,b) = (0, b), analyze m[n] ≡ b*m[n-2] (mod 7):")
    print("\nn   | m[n-2] mod 7 | m[n] mod 7 | b = m[n]/m[n-2] mod 7 | n mod 7")
    print("-" * 90)

    b_values = []
    for i in range(2, len(n_values)):
        n = n_values[i]
        n2 = n_values[i-2]

        r_n = residues[n]
        r_n2 = residues[n2]

        # Find b such that b * r_n2 ≡ r_n (mod 7)
        b = None
        if r_n2 != 0:
            # Find multiplicative inverse of r_n2 mod 7
            for inv in range(p):
                if (r_n2 * inv) % p == 1:
                    b = (r_n * inv) % p
                    break
        else:
            # r_n2 = 0, so we can't divide
            if r_n == 0:
                b = "any"
            else:
                b = "impossible"

        b_values.append((n, b))
        print(f"{n:2d}  | {r_n2:13d} | {r_n:10d} | {str(b):21s} | {n % 7}")

    print("\n" + "=" * 80)
    print("PATTERN IN b VALUES:")
    print("=" * 80)

    # Group by n mod 7
    by_mod7 = {}
    for n, b in b_values:
        mod = n % 7
        if mod not in by_mod7:
            by_mod7[mod] = []
        by_mod7[mod].append((n, b))

    print("\nGrouped by n mod 7:")
    for mod in sorted(by_mod7.keys()):
        print(f"\nn mod 7 = {mod}:")
        for n, b in by_mod7[mod]:
            print(f"  n={n:2d}: b={b}")

def analyze_even_odd_sequences_mod7(m_seq: Dict[int, int]):
    """Separate m[n] into even and odd subsequences"""

    p = 7
    print("\n" + "=" * 80)
    print("EVEN/ODD SUBSEQUENCE ANALYSIS mod 7")
    print("=" * 80)

    n_values = sorted(m_seq.keys())

    # Split into even and odd n
    even_n = [n for n in n_values if n % 2 == 0]
    odd_n = [n for n in n_values if n % 2 == 1]

    print("\nEVEN n sequence:")
    print("n   | m[n] | m[n] mod 7")
    print("-" * 40)
    even_residues = []
    for n in even_n:
        r = m_seq[n] % p
        even_residues.append(r)
        print(f"{n:2d}  | {m_seq[n]:8d} | {r}")

    print("\nODD n sequence:")
    print("n   | m[n] | m[n] mod 7")
    print("-" * 40)
    odd_residues = []
    for n in odd_n:
        r = m_seq[n] % p
        odd_residues.append(r)
        print(f"{n:2d}  | {m_seq[n]:8d} | {r}")

    print(f"\nEven residues: {even_residues}")
    print(f"Odd residues:  {odd_residues}")

    # Check if each subsequence has a recurrence
    print("\n" + "=" * 80)
    print("RECURRENCE IN EVEN SUBSEQUENCE:")
    print("=" * 80)

    print("\nChecking if even[k] ≡ a*even[k-1] + b*even[k-2] (mod 7):")

    for a in range(p):
        for b in range(p):
            valid = True
            for i in range(2, len(even_residues)):
                predicted = (a * even_residues[i-1] + b * even_residues[i-2]) % p
                if predicted != even_residues[i]:
                    valid = False
                    break

            if valid:
                print(f"\n*** FOUND: even[k] ≡ {a}*even[k-1] + {b}*even[k-2] (mod {p}) ***")

                # Verify
                for i in range(2, len(even_residues)):
                    predicted = (a * even_residues[i-1] + b * even_residues[i-2]) % p
                    actual = even_residues[i]
                    print(f"k={i} (n={even_n[i]}): {a}*{even_residues[i-1]} + {b}*{even_residues[i-2]} ≡ {predicted} ≡ {actual} (mod {p})")

                break
        else:
            continue
        break
    else:
        print("No order-2 recurrence found in even subsequence")

    print("\n" + "=" * 80)
    print("RECURRENCE IN ODD SUBSEQUENCE:")
    print("=" * 80)

    print("\nChecking if odd[k] ≡ a*odd[k-1] + b*odd[k-2] (mod 7):")

    for a in range(p):
        for b in range(p):
            valid = True
            for i in range(2, len(odd_residues)):
                predicted = (a * odd_residues[i-1] + b * odd_residues[i-2]) % p
                if predicted != odd_residues[i]:
                    valid = False
                    break

            if valid:
                print(f"\n*** FOUND: odd[k] ≡ {a}*odd[k-1] + {b}*odd[k-2] (mod {p}) ***")

                # Verify
                for i in range(2, len(odd_residues)):
                    predicted = (a * odd_residues[i-1] + b * odd_residues[i-2]) % p
                    actual = odd_residues[i]
                    print(f"k={i} (n={odd_n[i]}): {a}*{odd_residues[i-1]} + {b}*{odd_residues[i-2]} ≡ {predicted} ≡ {actual} (mod {p})")

                break
        else:
            continue
        break
    else:
        print("No order-2 recurrence found in odd subsequence")

def analyze_differences_deeply_mod7(m_seq: Dict[int, int]):
    """Deep analysis of differences modulo 7"""

    p = 7
    print("\n" + "=" * 80)
    print("DEEP DIFFERENCE ANALYSIS mod 7")
    print("=" * 80)

    n_values = sorted(m_seq.keys())

    # First differences
    print("\nFirst differences Δm[n] = m[n] - m[n-1]:")
    print("n   | Δm[n] | Δm[n] mod 7")
    print("-" * 40)

    delta1 = {}
    for i in range(1, len(n_values)):
        n = n_values[i]
        n1 = n_values[i-1]
        d = m_seq[n] - m_seq[n1]
        delta1[n] = d % p
        print(f"{n:2d}  | {d:6d} | {delta1[n]}")

    # Second differences
    print("\nSecond differences Δ²m[n] = Δm[n] - Δm[n-1]:")
    print("n   | Δ²m[n] | Δ²m[n] mod 7")
    print("-" * 40)

    delta2 = {}
    delta1_list = [delta1[n] for n in sorted(delta1.keys())]
    n_list = sorted(delta1.keys())

    for i in range(1, len(delta1_list)):
        n = n_list[i]
        d2 = (delta1_list[i] - delta1_list[i-1]) % p
        delta2[n] = d2
        print(f"{n:2d}  | {d2:6d} | {d2}")

    # Check if second differences have a pattern
    print("\nSecond difference sequence mod 7:")
    print([delta2[n] for n in sorted(delta2.keys())])

def analyze_multiplicative_order_mod7(m_seq: Dict[int, int]):
    """Analyze multiplicative relationships mod 7"""

    p = 7
    print("\n" + "=" * 80)
    print("MULTIPLICATIVE ORDER ANALYSIS mod 7")
    print("=" * 80)

    n_values = sorted(m_seq.keys())
    residues = {n: m_seq[n] % p for n in n_values}

    print("\nFor each m[n] mod 7, check its multiplicative order:")
    print("(Order k means m[n]^k ≡ 1 (mod 7))")

    print("\nn   | m[n] mod 7 | m[n]^2 | m[n]^3 | m[n]^6 | order")
    print("-" * 70)

    for n in n_values:
        r = residues[n]

        if r == 0:
            print(f"{n:2d}  | {r:10d} | -      | -      | -      | ∞ (zero)")
            continue

        powers = {
            1: r % p,
            2: (r * r) % p,
            3: (r * r * r) % p,
            6: pow(r, 6, p)
        }

        # Find order
        order = None
        for k in [1, 2, 3, 6]:
            if powers[k] == 1:
                order = k
                break

        if order is None:
            order = ">6"

        print(f"{n:2d}  | {r:10d} | {powers[2]:6d} | {powers[3]:6d} | {powers[6]:6d} | {order}")

    print("\nNote: By Fermat's Little Theorem, a^6 ≡ 1 (mod 7) for gcd(a,7)=1")

def main():
    print("=" * 80)
    print("MODULAR CONSTRUCTION ANALYSIS: SKIP-2 AND SUBSEQUENCES")
    print("=" * 80)

    m_seq = load_m_sequence()

    analyze_skip2_pattern_mod7(m_seq)
    analyze_even_odd_sequences_mod7(m_seq)
    analyze_differences_deeply_mod7(m_seq)
    analyze_multiplicative_order_mod7(m_seq)

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
