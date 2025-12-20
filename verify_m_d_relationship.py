#!/usr/bin/env python3
"""
Verify the ACTUAL m-d relationship from FORMULA_PATTERNS.md:

m[n] = (2^n - adj[n]) / k[d[n]]

where adj[n] = k[n] - 2*k[n-1]
and d[n] is chosen to minimize m[n]
"""

import json
import sqlite3

def load_data():
    """Load k-sequence from DB and m/d from JSON."""
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

    m_seq = data['m_seq']  # 0-indexed, m_seq[n-1] = m[n]
    d_seq = data['d_seq']  # 0-indexed, d_seq[n-1] = d[n]

    return k_seq, m_seq, d_seq

def main():
    K, m_seq, d_seq = load_data()

    print("=" * 80)
    print("VERIFYING: m[n] = (2^n - adj[n]) / k[d[n]]")
    print("=" * 80)
    print()

    matches = 0
    failures = 0

    for n in range(2, 71):
        if n not in K or (n-1) not in K:
            continue

        if n-1 >= len(m_seq) or n-1 >= len(d_seq):
            continue

        # Get values
        m_n = m_seq[n-1]
        d_n = d_seq[n-1]

        if d_n not in K:
            print(f"n={n}: d[n]={d_n} not in K")
            continue

        # Compute adj[n]
        adj_n = K[n] - 2*K[n-1]

        # Compute expected m[n] from formula
        numerator = 2**n - adj_n
        k_dn = K[d_n]

        if k_dn == 0:
            print(f"n={n}: k[d[n]]=0, cannot divide")
            continue

        # Check if divisible
        if numerator % k_dn == 0:
            m_computed = numerator // k_dn
            if m_computed == m_n:
                matches += 1
                status = "✓"
            else:
                failures += 1
                status = "✗ MISMATCH"
        else:
            failures += 1
            status = "✗ NOT DIVISIBLE"
            m_computed = numerator / k_dn

        # Print for first 20 and any failures
        if n <= 20 or status != "✓":
            print(f"n={n:2d}: adj={adj_n:>12,}, 2^n-adj={numerator:>15,}, k[d={d_n}]={k_dn:>10,}")
            print(f"       m_computed={(numerator/k_dn):>15.2f}, m_stored={m_n:>15,} {status}")

    print()
    print("=" * 80)
    print(f"RESULT: {matches} matches, {failures} failures out of {matches + failures}")
    print("=" * 80)

    if failures == 0:
        print(">>> FORMULA m[n] = (2^n - adj[n]) / k[d[n]] VERIFIED <<<")
    else:
        print(">>> SOME FAILURES - investigating... <<<")

if __name__ == "__main__":
    main()
