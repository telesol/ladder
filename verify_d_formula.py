#!/usr/bin/env python3
"""
Verify Nemotron's hypothesis:
d[n] = max{i : k[i] | N_n} where N_n = 2^n - adj[n]

This would mean d is deterministic from k values alone!
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

    return k_seq, data['d_seq']

def main():
    K, d_seq_stored = load_data()

    print("=" * 80)
    print("TESTING NEMOTRON HYPOTHESIS: d[n] = max{i : k[i] | (2^n - adj[n])}")
    print("=" * 80)
    print()

    matches = 0
    failures = 0

    for n in range(4, 71):
        if n not in K or (n-1) not in K:
            continue
        if n-2 >= len(d_seq_stored):
            continue

        # Corrected indexing: d_seq[n-2] = d for puzzle n
        d_stored = d_seq_stored[n-2]

        # Compute N_n = 2^n - adj[n]
        adj_n = K[n] - 2*K[n-1]
        N_n = 2**n - adj_n

        # Find max i such that k[i] divides N_n
        d_computed = 1
        for i in range(1, n):
            if i in K and K[i] != 0 and N_n % K[i] == 0:
                d_computed = i  # Keep updating to get max

        if d_computed == d_stored:
            matches += 1
            status = "✓"
        else:
            failures += 1
            # Find all divisors for debugging
            divisors = [i for i in range(1, n) if i in K and K[i] != 0 and N_n % K[i] == 0]
            status = f"✗ stored={d_stored}, computed_max={d_computed}, all_divisors={divisors}"

        if n <= 15 or "✗" in status:
            print(f"n={n:2d}: N_n={N_n:>15,}, d_stored={d_stored}, d_computed={d_computed} {status}")

    print()
    print("=" * 80)
    print(f"Result: {matches}/{matches+failures} matches")

    if failures == 0:
        print(">>> NEMOTRON HYPOTHESIS VERIFIED! d[n] = max{i : k[i] | N_n} <<<")
    else:
        print(f">>> {failures} FAILURES - hypothesis needs refinement <<<")
    print("=" * 80)

if __name__ == "__main__":
    main()
