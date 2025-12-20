#!/usr/bin/env python3
"""
Verify the m-d relationship with CORRECTED indexing.

Discovery: stored m_seq[n-1] = formula's m[n+1]
So for puzzle n, use m_seq[n-2] to get the correct m value.

Formula: m[n] = (2^n - adj[n]) / k[d[n]]
"""

import json
import sqlite3

def load_data():
    conn = sqlite3.connect('/home/rkh/ladder/db/kh.db')
    cursor = conn.cursor()
    cursor.execute("SELECT puzzle_id, priv_hex FROM keys WHERE puzzle_id <= 70 ORDER BY puzzle_id")
    rows = cursor.fetchall()
    conn.close()

    k_seq = {}
    for puzzle_id, hex_val in rows:
        k_seq[puzzle_id] = int(hex_val, 16)

    with open('/home/rkh/ladder/data_for_csolver.json', 'r') as f:
        data = json.load(f)

    return k_seq, data['m_seq'], data['d_seq']

def main():
    K, m_seq_stored, d_seq_stored = load_data()

    print("=" * 80)
    print("VERIFYING with CORRECTED indexing: stored m_seq[n-1] = formula m[n+1]")
    print("=" * 80)
    print()

    # Test: For formula's m[n], use stored m_seq[n-2]
    print("Testing: formula m[n] = stored m_seq[n-2]")
    print()

    matches = 0
    total = 0

    for n in range(4, 71):  # Start from n=4 where formula applies
        if n not in K or (n-1) not in K:
            continue
        if n-2 < 0 or n-2 >= len(m_seq_stored):
            continue

        # Corrected indexing: formula's m[n] = stored m_seq[n-2]
        m_formula = m_seq_stored[n-2]

        # For d[n], need to figure out the correct index too
        # Let's check if d also has a shift
        if n-2 >= len(d_seq_stored):
            continue
        d_n = d_seq_stored[n-2]  # Try same shift

        if d_n not in K:
            continue

        # Compute
        adj_n = K[n] - 2*K[n-1]
        numerator = 2**n - adj_n
        k_dn = K[d_n]

        total += 1

        if k_dn != 0 and numerator % k_dn == 0:
            m_computed = numerator // k_dn
            if m_computed == m_formula:
                matches += 1
                status = "✓"
            else:
                status = f"✗ computed={m_computed}, stored={m_formula}"
        else:
            status = f"✗ not divisible (num={numerator}, div={k_dn})"

        if n <= 20 or "✗" in status:
            print(f"n={n:2d}: adj={adj_n:>12,}, d[n]={d_n}, m_formula={m_formula:>10,} {status}")

    print()
    print(f"Result: {matches}/{total} matches")

    # Now let's try another hypothesis: verify the adj computation directly
    print()
    print("=" * 80)
    print("Trying: verify adj[n] = 2^n - m*k[d] with original indexing")
    print("=" * 80)
    print()

    matches2 = 0
    total2 = 0

    for n in range(2, 71):
        if n not in K or (n-1) not in K:
            continue
        if n-1 >= len(m_seq_stored) or n-1 >= len(d_seq_stored):
            continue

        m_n = m_seq_stored[n-1]
        d_n = d_seq_stored[n-1]

        if d_n not in K:
            continue

        adj_actual = K[n] - 2*K[n-1]
        adj_computed = 2**n - m_n * K[d_n]

        total2 += 1
        if adj_actual == adj_computed:
            matches2 += 1
            status = "✓"
        else:
            status = f"✗ actual={adj_actual}, computed={adj_computed}, diff={adj_actual-adj_computed}"

        if n <= 15 or "✗" in status[:5]:
            print(f"n={n:2d}: m={m_n:>10,}, d={d_n}, k[d]={K[d_n]:>10,}, {status}")

    print()
    print(f"Result: {matches2}/{total2} matches")

if __name__ == "__main__":
    main()
