#!/usr/bin/env python3
"""
Check if m[n] relates to powers of 2 modulo various primes
Since the puzzle uses 2^n ranges, there might be a connection
"""

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

def analyze_m_vs_2n_mod_p(m_seq: Dict[int, int], p: int):
    """Check if m[n] relates to 2^n modulo p"""

    print(f"\n{'=' * 80}")
    print(f"ANALYSIS: m[n] vs 2^n mod {p}")
    print(f"{'=' * 80}")

    n_values = sorted(m_seq.keys())

    print(f"\nn   | m[n] mod {p} | 2^n mod {p} | m[n]*2^n mod {p} | m[n]/2^n mod {p}")
    print("-" * 90)

    for n in n_values:
        m_mod = m_seq[n] % p
        pow2_mod = pow(2, n, p)
        product_mod = (m_mod * pow2_mod) % p

        # Find division: m[n] / 2^n mod p
        # Need multiplicative inverse of 2^n mod p
        div_mod = None
        if pow2_mod != 0:
            for inv in range(p):
                if (pow2_mod * inv) % p == 1:
                    div_mod = (m_mod * inv) % p
                    break

        print(f"{n:2d}  | {m_mod:12d} | {pow2_mod:11d} | {product_mod:16d} | {str(div_mod):15s}")

    # Check if m[n] * 2^n is constant mod p
    products = [(m_seq[n] * pow(2, n, p)) % p for n in n_values]
    if len(set(products)) == 1:
        print(f"\n*** CONSTANT: m[n] * 2^n ≡ {products[0]} (mod {p}) ***")

    # Check if m[n] / 2^n follows a pattern
    divisions = []
    for n in n_values:
        m_mod = m_seq[n] % p
        pow2_mod = pow(2, n, p)
        if pow2_mod != 0:
            for inv in range(p):
                if (pow2_mod * inv) % p == 1:
                    div = (m_mod * inv) % p
                    divisions.append(div)
                    break

    if len(set(divisions)) == 1:
        print(f"\n*** CONSTANT: m[n] / 2^n ≡ {divisions[0]} (mod {p}) ***")

def analyze_m_vs_n_power_mod_p(m_seq: Dict[int, int], p: int):
    """Check if m[n] relates to n^k modulo p"""

    print(f"\n{'=' * 80}")
    print(f"ANALYSIS: m[n] vs n^k mod {p}")
    print(f"{'=' * 80}")

    n_values = sorted(m_seq.keys())

    print(f"\nn   | m[n] mod {p} | n mod {p} | n^2 mod {p} | n^3 mod {p}")
    print("-" * 80)

    for n in n_values:
        m_mod = m_seq[n] % p
        n_mod = n % p
        n2_mod = (n * n) % p
        n3_mod = (n * n * n) % p

        print(f"{n:2d}  | {m_mod:12d} | {n_mod:9d} | {n2_mod:11d} | {n3_mod:11d}")

def check_linear_combination_mod_p(m_seq: Dict[int, int], p: int):
    """Check if m[n] ≡ a*2^n + b*n + c (mod p)"""

    print(f"\n{'=' * 80}")
    print(f"LINEAR COMBINATION: m[n] ≡ a*2^n + b*n + c (mod {p})")
    print(f"{'=' * 80}")

    n_values = sorted(m_seq.keys())

    # Try all combinations
    for a in range(p):
        for b in range(p):
            for c in range(p):
                valid = True
                for n in n_values:
                    predicted = (a * pow(2, n, p) + b * n + c) % p
                    actual = m_seq[n] % p
                    if predicted != actual:
                        valid = False
                        break

                if valid:
                    print(f"\n*** FOUND: m[n] ≡ {a}*2^n + {b}*n + {c} (mod {p}) ***")

                    # Verify
                    print(f"\nVerification:")
                    for n in n_values:
                        pow2 = pow(2, n, p)
                        predicted = (a * pow2 + b * n + c) % p
                        actual = m_seq[n] % p
                        print(f"n={n:2d}: {a}*{pow2} + {b}*{n} + {c} ≡ {predicted} ≡ {actual} (mod {p})")

                    return (a, b, c)

    print(f"\nNo formula m[n] ≡ a*2^n + b*n + c found (mod {p})")
    return None

def analyze_m_range_position(m_seq: Dict[int, int]):
    """Analyze where m[n] falls within [0, 2^n - 1]"""

    print(f"\n{'=' * 80}")
    print(f"POSITION ANALYSIS: m[n] within range [0, 2^n - 1]")
    print(f"{'=' * 80}")

    n_values = sorted(m_seq.keys())

    print(f"\nn   | m[n]     | 2^n - 1     | m[n]/(2^n-1)")
    print("-" * 70)

    for n in n_values[:10]:  # First 10 to avoid overflow display issues
        m = m_seq[n]
        max_val = 2**n - 1
        ratio = m / max_val

        print(f"{n:2d}  | {m:8d} | {max_val:11d} | {ratio:12.9f}")

    print(f"\nNote: If m[n] is a search position, this ratio indicates how far into the range.")

def analyze_binary_weight_mod_p(m_seq: Dict[int, int], p: int):
    """Check if m[n] mod p relates to binary weight (popcount) of n"""

    print(f"\n{'=' * 80}")
    print(f"BINARY WEIGHT ANALYSIS mod {p}")
    print(f"{'=' * 80}")

    n_values = sorted(m_seq.keys())

    print(f"\nn   | n (binary) | popcount(n) | m[n] mod {p}")
    print("-" * 70)

    for n in n_values:
        binary = bin(n)[2:]
        popcount = binary.count('1')
        m_mod = m_seq[n] % p

        print(f"{n:2d}  | {binary:10s} | {popcount:11d} | {m_mod:12d}")

    # Check if m[n] mod p equals popcount mod p
    match = all((m_seq[n] % p) == (bin(n).count('1') % p) for n in n_values)
    if match:
        print(f"\n*** m[n] ≡ popcount(n) (mod {p}) ***")

def check_fibonacci_mod_p_connection(m_seq: Dict[int, int], p: int):
    """Check if m[n] relates to Fibonacci numbers mod p"""

    print(f"\n{'=' * 80}")
    print(f"FIBONACCI CONNECTION mod {p}")
    print(f"{'=' * 80}")

    # Generate Fibonacci sequence mod p
    fib = [0, 1]
    for i in range(2, 30):
        fib.append((fib[-1] + fib[-2]) % p)

    n_values = sorted(m_seq.keys())

    print(f"\nn   | m[n] mod {p} | F(n) mod {p} | F(n+1) mod {p} | m[n]-F(n) mod {p}")
    print("-" * 90)

    for n in n_values:
        m_mod = m_seq[n] % p
        f_n = fib[n] if n < len(fib) else None
        f_n1 = fib[n+1] if n+1 < len(fib) else None
        diff = (m_mod - f_n) % p if f_n is not None else None

        print(f"{n:2d}  | {m_mod:12d} | {str(f_n):12s} | {str(f_n1):14s} | {str(diff):18s}")

def main():
    print("=" * 80)
    print("MODULAR ANALYSIS: POWERS OF 2 AND SPECIAL SEQUENCES")
    print("=" * 80)

    m_seq = load_m_sequence()

    # Analyze for key primes
    for p in [7, 3, 5]:
        analyze_m_vs_2n_mod_p(m_seq, p)
        analyze_m_vs_n_power_mod_p(m_seq, p)
        check_linear_combination_mod_p(m_seq, p)

    # Other analyses
    analyze_m_range_position(m_seq)

    for p in [7, 3]:
        analyze_binary_weight_mod_p(m_seq, p)
        check_fibonacci_mod_p_connection(m_seq, p)

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
