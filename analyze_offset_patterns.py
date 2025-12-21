#!/usr/bin/env python3
"""
Extended Offset Analysis - Search for Alternative Patterns

After rejecting Mistral's formula, search for actual patterns in offset data.
"""

import sqlite3
import json
from collections import defaultdict

DB_PATH = "/home/rkh/ladder/db/kh.db"

def get_k_values(n_min=1, n_max=90):
    """Query all k values from database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    k_values = {}
    cursor.execute("""
        SELECT puzzle_id, priv_hex
        FROM keys
        WHERE puzzle_id >= ? AND puzzle_id <= ?
        ORDER BY puzzle_id
    """, (n_min, n_max))
    for puzzle_id, priv_hex in cursor.fetchall():
        k_values[puzzle_id] = int(priv_hex, 16)
    conn.close()
    return k_values

def load_data_for_csolver():
    """Load m_seq, d_seq, adj_seq from data_for_csolver.json"""
    with open("/home/rkh/ladder/data_for_csolver.json", "r") as f:
        data = json.load(f)
    return data

def prime_factorization(n):
    """Complete prime factorization."""
    if n == 0:
        return {0: 1}
    sign = 1 if n >= 0 else -1
    n = abs(n)
    factors = {}
    count = 0
    while n % 2 == 0:
        count += 1
        n //= 2
    if count > 0:
        factors[2] = count
    p = 3
    while p * p <= n:
        count = 0
        while n % p == 0:
            count += 1
            n //= p
        if count > 0:
            factors[p] = count
        p += 2
    if n > 1:
        factors[n] = 1
    if sign == -1:
        factors[-1] = 1
    return factors

def analyze_offset_patterns():
    """
    Search for alternative patterns in offset data.
    """
    print("=" * 80)
    print("EXTENDED OFFSET PATTERN ANALYSIS")
    print("=" * 80)
    print()

    # Load data
    k_values = get_k_values(1, 90)
    csolver_data = load_data_for_csolver()

    m_seq = csolver_data["m_seq"]
    d_seq = csolver_data["d_seq"]
    adj_seq = csolver_data["adj_seq"]

    # Compute offsets
    offsets = {}
    for n in range(10, 71):
        if n in k_values and (n-3) in k_values:
            offsets[n] = k_values[n] - 9 * k_values[n-3]

    print(f"Computed {len(offsets)} offsets (n=10 to n=70)")
    print()

    # === PATTERN 1: Offset split by n mod 3 ===
    print("PATTERN 1: Offset magnitude by n mod 3")
    print("-" * 80)

    by_mod3 = {0: [], 1: [], 2: []}
    for n, offset in offsets.items():
        by_mod3[n % 3].append((n, abs(offset)))

    for mod in [0, 1, 2]:
        values = by_mod3[mod]
        count = len(values)
        if count > 0:
            avg_mag = sum(v[1] for v in values) / count
            print(f"n ≡ {mod} (mod 3): {count} offsets, avg magnitude: {avg_mag:.2e}")
            # Show first few
            for n, mag in sorted(values)[:5]:
                print(f"  n={n}: |offset|={mag}")
    print()

    # === PATTERN 2: Offset ratios ===
    print("PATTERN 2: Offset[n] / Offset[n-3] ratios")
    print("-" * 80)

    ratios = []
    for n in sorted(offsets.keys()):
        if (n-3) in offsets and offsets[n-3] != 0:
            ratio = offsets[n] / offsets[n-3]
            ratios.append((n, ratio))
            print(f"n={n}: offset[{n}]/offset[{n-3}] = {ratio:15.6f}")

    print()
    print(f"Average ratio: {sum(r[1] for r in ratios)/len(ratios):.6f}")
    print(f"Min ratio: {min(r[1] for r in ratios):.6f} at n={min(ratios, key=lambda x: x[1])[0]}")
    print(f"Max ratio: {max(r[1] for r in ratios):.6f} at n={max(ratios, key=lambda x: x[1])[0]}")
    print()

    # === PATTERN 3: Offset vs adj[n] relationship ===
    print("PATTERN 3: Relationship between offset[n] and adj[n]")
    print("-" * 80)

    # Note: adj_seq is indexed differently (adj_seq[0] = adj[2])
    # adj[n] is stored in adj_seq[n-2] for n >= 2

    for n in range(10, 31):  # First 20 offsets
        if n in offsets:
            offset = offsets[n]
            # Get adj[n] and adj[n-3]
            if (n-2) < len(adj_seq) and (n-3-2) >= 0 and (n-3-2) < len(adj_seq):
                adj_n = adj_seq[n-2]
                adj_n3 = adj_seq[n-3-2]

                # Test: offset[n] = 9*adj[n-3] - adj[n] ?
                predicted = 9 * adj_n3 - adj_n
                error = abs(offset - predicted)
                match = "✓" if error == 0 else "✗"

                print(f"n={n}: offset={offset:12d} | 9*adj[{n-3}]-adj[{n}]={predicted:12d} | {match}")
    print()

    # === PATTERN 4: Offset vs k[n-6] ===
    print("PATTERN 4: Is offset[n] related to k[n-6]?")
    print("-" * 80)

    for n in range(16, 31):  # n >= 16 so n-6 >= 10
        if n in offsets and (n-6) in k_values:
            offset = offsets[n]
            k_n6 = k_values[n-6]

            # Test various relationships
            ratio = offset / k_n6 if k_n6 != 0 else float('inf')

            print(f"n={n}: offset[{n}]={offset:15d} | k[{n-6}]={k_n6:12d} | ratio={ratio:10.3f}")
    print()

    # === PATTERN 5: Offset mod small primes ===
    print("PATTERN 5: Offset[n] mod small primes")
    print("-" * 80)

    small_primes = [2, 3, 5, 7, 11, 13, 17, 19]

    for p in small_primes:
        residues = defaultdict(int)
        for n, offset in offsets.items():
            residues[offset % p] += 1

        print(f"Offset mod {p}: ", end="")
        for r in range(p):
            count = residues[r]
            print(f"{r}:{count} ", end="")
        print()
    print()

    # === PATTERN 6: n values where offset is divisible by k[i] ===
    print("PATTERN 6: When does k[i] divide offset[n]?")
    print("-" * 80)

    for i in range(1, 10):
        if i in k_values:
            k_i = k_values[i]
            divisible = []
            for n, offset in offsets.items():
                if offset % k_i == 0:
                    divisible.append(n)

            if divisible:
                print(f"k[{i}]={k_i} divides offset[n] for n={divisible[:10]}")
    print()

    # === PATTERN 7: Offset and m/d sequences ===
    print("PATTERN 7: Correlation with m_seq and d_seq")
    print("-" * 80)

    for n in range(10, 31):
        if n in offsets:
            offset = offsets[n]

            # Get m[n] and d[n] (remember index shift: m_seq[n-2] = m[n])
            if (n-2) < len(m_seq) and (n-2) < len(d_seq):
                m_n = m_seq[n-2]
                d_n = d_seq[n-2]

                # Get k[d_n] if available
                if d_n in k_values:
                    k_d = k_values[d_n]

                    # Test: offset[n] vs m[n] * k[d[n]]
                    product = m_n * k_d

                    print(f"n={n}: offset={offset:12d} | m[{n}]*k[{d_n}]={product:12d} | ratio={offset/product if product != 0 else 'inf':10.3f}")
    print()

    # === PATTERN 8: Prime offset cases ===
    print("PATTERN 8: Prime offsets (offsets that are prime)")
    print("-" * 80)

    prime_offsets = []
    for n, offset in offsets.items():
        factors = prime_factorization(offset)
        # Check if prime (only one factor, not -1, power = 1)
        factors_no_sign = {k: v for k, v in factors.items() if k != -1}
        if len(factors_no_sign) == 1 and list(factors_no_sign.values())[0] == 1:
            prime = list(factors_no_sign.keys())[0]
            prime_offsets.append((n, abs(offset), prime))

    print(f"Found {len(prime_offsets)} prime offsets:")
    for n, mag, prime in prime_offsets:
        print(f"  n={n}: offset = ±{prime}")
    print()

    # === PATTERN 9: Growth rate analysis ===
    print("PATTERN 9: Offset growth rate")
    print("-" * 80)

    # Compute |offset[n]| / |offset[n-1]|
    growth_rates = []
    for n in sorted(offsets.keys())[1:]:
        if (n-1) in offsets and offsets[n-1] != 0:
            rate = abs(offsets[n]) / abs(offsets[n-1])
            growth_rates.append((n, rate))

    print("Growth rate |offset[n]| / |offset[n-1]|:")
    for n, rate in growth_rates[:20]:
        print(f"  n={n}: {rate:8.3f}")

    avg_growth = sum(r[1] for r in growth_rates) / len(growth_rates)
    print(f"\nAverage growth rate: {avg_growth:.3f}")
    print()

    # === PATTERN 10: Sign changes ===
    print("PATTERN 10: Sign change analysis")
    print("-" * 80)

    sign_changes = []
    prev_sign = None
    for n in sorted(offsets.keys()):
        sign = 1 if offsets[n] >= 0 else -1
        if prev_sign is not None and sign != prev_sign:
            sign_changes.append(n)
        prev_sign = sign

    print(f"Sign changes occur at n={sign_changes[:20]}")
    print(f"Total sign changes: {len(sign_changes)} out of {len(offsets)-1} transitions")
    print()

    # Save summary
    summary = {
        "offset_mod3_distribution": {str(mod): len(by_mod3[mod]) for mod in [0, 1, 2]},
        "prime_offsets": [{"n": n, "prime": p} for n, mag, p in prime_offsets],
        "average_growth_rate": avg_growth,
        "sign_changes": sign_changes,
        "total_offsets": len(offsets)
    }

    with open("/home/rkh/ladder/offset_pattern_analysis.json", "w") as f:
        json.dump(summary, f, indent=2)

    print("=" * 80)
    print("Extended analysis saved to: offset_pattern_analysis.json")
    print("=" * 80)

if __name__ == "__main__":
    analyze_offset_patterns()
