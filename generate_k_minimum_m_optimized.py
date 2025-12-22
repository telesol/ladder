#!/usr/bin/env python3
"""Optimized k-sequence generation using minimum-m rule.

Key insight: We don't need to try all m values.
For each d, there's a specific range of k_n values that are valid.
We can calculate the corresponding m values and find the minimum.
"""

import sqlite3

# Load known k-values
conn = sqlite3.connect('/home/solo/LadderV3/kh-assist/db/kh.db')
cur = conn.cursor()
cur.execute("SELECT puzzle_id, priv_hex FROM keys WHERE puzzle_id <= 95 ORDER BY puzzle_id")
rows = cur.fetchall()
conn.close()

k_known = {row[0]: int(row[1], 16) for row in rows}

print("="*80)
print("GENERATING K-SEQUENCE USING MINIMUM-M RULE (OPTIMIZED)")
print("="*80)
print()

k_generated = k_known.copy()

for n in range(71, 76):
    print(f"\nGenerating k{n}:")
    print("-" * 60)

    if n-1 not in k_generated:
        print(f"  ❌ Missing k{n-1}")
        break

    k_prev = k_generated[n-1]
    min_k_range = 2 ** (n-1)
    max_k_range = 2 ** n

    # For each d, find the m that gives the smallest k_n in valid range
    candidates = []

    for d in range(1, n):
        if d not in k_generated:
            continue

        k_d = k_generated[d]
        if k_d == 0:
            continue

        # Master formula: k_n = 2*k_{n-1} + 2^n - m*k_d
        # We want k_n in [2^(n-1), 2^n)
        # So: 2^(n-1) <= 2*k_{n-1} + 2^n - m*k_d < 2^n

        # Rearranging for m:
        # m*k_d >= 2*k_{n-1} + 2^n - 2^n = 2*k_{n-1}
        # m*k_d < 2*k_{n-1} + 2^n - 2^(n-1) = 2*k_{n-1} + 2^(n-1)

        # So: (2*k_{n-1}) / k_d <= m < (2*k_{n-1} + 2^(n-1)) / k_d

        base = 2 * k_prev + 2**n

        # To maximize k_n (minimize m), use m as small as possible
        # Minimum m: when k_n is just below 2^n
        m_min = (base - max_k_range + 1) // k_d + 1
        if m_min < 1:
            m_min = 1

        # Maximum m: when k_n is at least 2^(n-1)
        m_max = (base - min_k_range) // k_d

        # The minimum valid m for this d
        for m in range(m_min, m_max + 1):
            if m <= 0:
                continue

            k_n = 2 * k_prev + 2**n - m * k_d

            if min_k_range <= k_n < max_k_range:
                candidates.append((m, d, k_n))
                break  # We found the minimum m for this d

    if not candidates:
        print(f"  ❌ No valid candidates!")
        break

    # Sort by m (minimum m wins)
    candidates.sort(key=lambda x: x[0])

    m_chosen, d_chosen, k_n = candidates[0]
    k_generated[n] = k_n

    print(f"  Candidates: {len(candidates)}")
    print(f"  Best: d={d_chosen}, m={m_chosen}")
    print(f"  k{n} = {k_n:#x}")

    # Show top 5 candidates
    print(f"  Top 5 minimum-m candidates:")
    for i, (m, d, k) in enumerate(candidates[:5], 1):
        print(f"    {i}. d={d:2d}, m={m:>25}, k={k:#x}")

    # Compare with actual if available
    if n in k_known:
        k_actual = k_known[n]
        if k_n == k_actual:
            print(f"  ✅ EXACT MATCH!")
        else:
            print(f"  ❌ Mismatch with actual:")
            print(f"     Predicted: {k_n:#x}")
            print(f"     Actual:    {k_actual:#x}")

            # Find what (d,m) would give actual
            print(f"  What would give actual k{n}:")
            adj = k_actual - 2 * k_prev
            numerator = 2**n - adj
            matches = []
            for d_test in range(1, n):
                if d_test not in k_generated:
                    continue
                k_d_test = k_generated[d_test]
                if k_d_test != 0 and numerator % k_d_test == 0:
                    m_test = numerator // k_d_test
                    if m_test > 0:
                        matches.append((m_test, d_test))

            matches.sort(key=lambda x: x[0])
            for m_test, d_test in matches[:3]:
                print(f"     d={d_test}, m={m_test}")

print()
print("="*80)
print("SUMMARY")
print("="*80)
print()

for n in range(71, 76):
    if n not in k_generated:
        print(f"k{n}: NOT GENERATED")
    elif n not in k_known:
        print(f"k{n} = {k_generated[n]:#x} (no reference)")
    elif k_generated[n] == k_known[n]:
        print(f"k{n} = {k_generated[n]:#x} ✅ MATCH")
    else:
        print(f"k{n}:")
        print(f"  Generated: {k_generated[n]:#x}")
        print(f"  Actual:    {k_known[n]:#x}")
        print(f"  ❌ MISMATCH")
