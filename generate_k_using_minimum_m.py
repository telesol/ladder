#!/usr/bin/env python3
"""Generate k-sequence using minimum-m rule discovered by other Claudes.

Strategy:
1. We know k1-k70
2. For n=71, try all possible d values (1 to 70)
3. For each d, find if there exists m > 0 that satisfies the master formula
4. Choose (d, m) that minimizes m
5. Generate k71 from this
6. Repeat for k72, k73, k74, k75
7. Compare k75 with actual bridge value
"""

import sqlite3
import json

# Load known k-values
conn = sqlite3.connect('/home/solo/LadderV3/kh-assist/db/kh.db')
cur = conn.cursor()
cur.execute("SELECT puzzle_id, priv_hex FROM keys WHERE puzzle_id <= 95 ORDER BY puzzle_id")
rows = cur.fetchall()
conn.close()

k_known = {row[0]: int(row[1], 16) for row in rows}

print("="*80)
print("GENERATING K-SEQUENCE USING MINIMUM-M RULE")
print("="*80)
print()

# Master formula: k_n = 2*k_{n-1} + (2^n - m_n * k_{d_n})
# Rearranged: m_n = (2^n - (k_n - 2*k_{n-1})) / k_{d_n}

# For generation: Given n, d, m → k_n = 2*k_{n-1} + (2^n - m * k_d)

k_generated = k_known.copy()

print("Starting from k70 = {:#x}".format(k_generated[70]))
print()

for n in range(71, 76):
    print(f"Generating k{n}:")
    print("-" * 60)

    if n-1 not in k_generated:
        print(f"  ❌ Missing k{n-1}, cannot continue")
        break

    k_prev = k_generated[n-1]

    # Find all valid (d, m) pairs
    valid_pairs = []

    for d_candidate in range(1, n):
        if d_candidate not in k_generated:
            continue

        k_d = k_generated[d_candidate]
        if k_d == 0:
            continue

        # We need to find m such that k_n is in valid range
        # For puzzle n, k_n should be in range [2^(n-1), 2^n)
        # Try different m values and see which ones produce valid k_n

        # From master formula: k_n = 2*k_{n-1} + 2^n - m*k_d
        # For k_n to be in [2^(n-1), 2^n):
        #   2^(n-1) <= 2*k_{n-1} + 2^n - m*k_d < 2^n
        #   2^(n-1) - 2*k_{n-1} - 2^n <= -m*k_d < 2^n - 2*k_{n-1} - 2^n
        #   (2^n - 2*k_{n-1} - 2^(n-1)) / k_d <= m < (2^n - 2*k_{n-1}) / k_d

        min_k = 2 ** (n-1)
        max_k = 2 ** n

        # m bounds
        base = 2 * k_prev + 2**n
        m_max_float = (base - min_k) / k_d
        m_min_float = (base - max_k) / k_d

        if m_min_float < 0:
            m_min_float = 1  # m must be positive

        m_min = int(m_min_float) + (1 if m_min_float > int(m_min_float) else 0)
        m_max = int(m_max_float)

        # Try a range around the calculated bounds
        for m_candidate in range(max(1, m_min - 100), m_max + 101):
            if m_candidate <= 0:
                continue

            k_n = 2 * k_prev + (2**n - m_candidate * k_d)

            if min_k <= k_n < max_k:
                valid_pairs.append((d_candidate, m_candidate, k_n))

    if not valid_pairs:
        print(f"  ❌ No valid (d, m) pairs found!")
        break

    # Choose pair with minimum m (per other Claudes' discovery)
    valid_pairs.sort(key=lambda x: x[1])  # Sort by m

    d_chosen, m_chosen, k_n = valid_pairs[0]

    k_generated[n] = k_n

    print(f"  Found {len(valid_pairs)} valid (d, m) pairs")
    print(f"  Minimum m: d={d_chosen}, m={m_chosen}")
    print(f"  Generated: k{n} = {k_n:#x}")

    # If we have actual value, compare
    if n in k_known:
        k_actual = k_known[n]
        if k_n == k_actual:
            print(f"  ✅ EXACT MATCH with actual k{n}!")
        else:
            error = abs(k_n - k_actual)
            error_pct = 100 * error / k_actual
            print(f"  ❌ Mismatch:")
            print(f"     Generated: {k_n:#x}")
            print(f"     Actual:    {k_actual:#x}")
            print(f"     Error: {error_pct:.6f}%")

        # Show what (d, m) would give actual value
        actual_adj = k_actual - 2 * k_prev
        print(f"  Actual value would require:")
        for d_test in range(1, n):
            if d_test not in k_generated:
                continue
            k_d = k_generated[d_test]
            if k_d == 0:
                continue
            numerator = 2**n - actual_adj
            if numerator % k_d == 0:
                m_test = numerator // k_d
                if m_test > 0:
                    print(f"     d={d_test}, m={m_test}")

    print()

print("="*80)
print("RESULTS")
print("="*80)
print()

for n in range(71, 76):
    if n not in k_generated:
        continue

    gen_str = f"k{n} = {k_generated[n]:#x}"

    if n in k_known:
        if k_generated[n] == k_known[n]:
            print(f"✅ {gen_str} (MATCH)")
        else:
            print(f"❌ {gen_str} (MISMATCH)")
            print(f"   Actual: {k_known[n]:#x}")
    else:
        print(f"⚠️  {gen_str} (NO REFERENCE)")

print()
