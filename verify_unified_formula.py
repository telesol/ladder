#!/usr/bin/env python3
"""
Verify the unified formula: k[n] = 2^n + 2k[n-1] - m[n] * k[d[n]]

Uses data from data_for_csolver.json for m_seq and d_seq.
"""

import json
import sqlite3

def load_data():
    """Load k-sequence from DB and m/d from JSON."""
    # Load k from database
    conn = sqlite3.connect('/home/rkh/ladder/db/kh.db')
    cursor = conn.cursor()
    cursor.execute("SELECT puzzle_id, priv_hex FROM keys WHERE puzzle_id <= 70 ORDER BY puzzle_id")
    rows = cursor.fetchall()
    conn.close()

    k_seq = {}
    for puzzle_id, hex_val in rows:
        k_seq[puzzle_id] = int(hex_val, 16)

    # Load m and d from JSON
    with open('/home/rkh/ladder/data_for_csolver.json', 'r') as f:
        data = json.load(f)

    m_seq = data['m_seq']  # list indexed from 0, so m_seq[n-1] = m[n]
    d_seq = data['d_seq']  # list indexed from 0, so d_seq[n-1] = d[n]

    return k_seq, m_seq, d_seq

def main():
    K, m_seq, d_seq = load_data()

    print("=" * 80)
    print("VERIFYING UNIFIED FORMULA: k[n] = 2^n + 2k[n-1] - m[n] * k[d[n]]")
    print("=" * 80)
    print()

    matches = 0
    failures = 0

    # n=1 is base case, start from n=2
    for n in range(2, 71):
        if n not in K or (n-1) not in K:
            continue

        # Get m[n] and d[n] (arrays are 0-indexed)
        if n-1 >= len(m_seq) or n-1 >= len(d_seq):
            print(f"n={n}: Missing m or d data")
            continue

        m_n = m_seq[n-1]
        d_n = d_seq[n-1]

        if d_n not in K:
            print(f"n={n}: d[n]={d_n} not in K")
            continue

        # Compute using formula
        computed = (2**n) + 2*K[n-1] - m_n * K[d_n]
        actual = K[n]

        if computed == actual:
            matches += 1
            status = "✓"
        else:
            failures += 1
            status = "✗"
            diff = actual - computed

        if computed != actual:
            print(f"n={n:2d}: {status} computed={computed:,}, actual={actual:,}, diff={diff:,}")
            print(f"        2^n={2**n:,}, 2k[n-1]={2*K[n-1]:,}, m[n]={m_n}, d[n]={d_n}, k[d[n]]={K[d_n]:,}")
        else:
            # Only print first few and last few successes for brevity
            if n <= 10 or n >= 65:
                print(f"n={n:2d}: {status} computed={computed:,} = actual")

    print()
    print("=" * 80)
    print(f"RESULT: {matches} matches, {failures} failures out of {matches + failures} tests")
    print("=" * 80)

    if failures == 0:
        print(">>> UNIFIED FORMULA VERIFIED 100% <<<")
    else:
        print(f">>> FAILURES DETECTED - need investigation <<<")

if __name__ == "__main__":
    main()
