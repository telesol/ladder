#!/usr/bin/env python3
"""
Direct analysis of adj[n] = k[n] - 2*k[n-1]

Since k[n] = 2*k[n-1] + adj[n], if we can predict adj[n], we can predict k[n].

Let's look for patterns in adj[n]:
- Sign patterns
- Magnitude patterns
- Relationships to n, 2^n, previous adj values
- Divisibility properties
"""

import sqlite3

DB_PATH = "/home/rkh/ladder/db/kh.db"

def load_k_values():
    """Load actual k values from database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT puzzle_id, priv_hex
        FROM ground_truth
        WHERE priv_hex IS NOT NULL
        ORDER BY puzzle_id
    """)
    rows = c.fetchall()
    conn.close()
    k = {}
    for puzzle_id, priv_hex in rows:
        if priv_hex.startswith('0x'):
            k[puzzle_id] = int(priv_hex, 16)
        else:
            k[puzzle_id] = int(priv_hex, 16)
    return k

def main():
    k = load_k_values()
    print(f"Loaded {len(k)} k values\n")

    # Compute adj[n] for all n
    adj = {}
    for n in range(2, max(k.keys()) + 1):
        if n in k and (n-1) in k:
            adj[n] = k[n] - 2 * k[n-1]

    print("=== adj[n] = k[n] - 2*k[n-1] ===\n")
    print(f"{'n':>4} | {'k[n]':>20} | {'2*k[n-1]':>20} | {'adj[n]':>20} | {'sign':>5} | {'|adj|/2^n':>12}")
    print("-" * 95)

    for n in sorted(adj.keys())[:40]:
        sign = '+' if adj[n] >= 0 else '-'
        ratio = abs(adj[n]) / (2**n)
        print(f"{n:>4} | {k[n]:>20} | {2*k[n-1]:>20} | {adj[n]:>20} | {sign:>5} | {ratio:>12.6f}")

    # Sign pattern analysis
    print("\n=== Sign Pattern ===")
    signs = ''.join(['+' if adj[n] >= 0 else '-' for n in sorted(adj.keys())[:40]])
    print(f"n=2-41: {signs}")

    # Check for ++- pattern
    print("\nChecking ++- pattern:")
    for i in range(0, len(signs)-2, 3):
        chunk = signs[i:i+3]
        expected = "++-"
        match = "✓" if chunk == expected else "✗"
        print(f"  n={2+i} to {4+i}: {chunk} {match}")
        if i >= 18:
            break

    # Ratio adj[n]/2^n analysis
    print("\n=== adj[n]/2^n ratio ===")
    ratios = [adj[n] / (2**n) for n in sorted(adj.keys())[:40]]
    print(f"Min ratio: {min(ratios):.6f}")
    print(f"Max ratio: {max(ratios):.6f}")
    print(f"Mean ratio: {sum(ratios)/len(ratios):.6f}")

    # Check if adj[n] is related to previous adj values
    print("\n=== Recurrence in adj? ===")
    print("Testing: adj[n] = a*adj[n-1] + b*adj[n-2] + c")

    # Try to find coefficients using first few values
    for n in range(4, min(15, max(adj.keys()))):
        if n in adj and (n-1) in adj and (n-2) in adj:
            # Try different simple relationships
            a1 = adj[n-1]
            a2 = adj[n-2]
            an = adj[n]

            # Check a*adj[n-1] + b for various a
            for a in range(-3, 4):
                if a == 0:
                    continue
                b = an - a * a1
                # Verify
                if a * a1 + b == an:
                    print(f"  n={n}: adj[{n}] = {a}*adj[{n-1}] + {b}")
                    break

    # Check divisibility of adj[n] by small numbers
    print("\n=== Divisibility of adj[n] ===")
    for d in [2, 3, 7, k[2], k[3]]:
        divisible = [n for n in sorted(adj.keys()) if adj[n] % d == 0]
        print(f"  Divisible by {d}: {len(divisible)} / {len(adj)} = {100*len(divisible)/len(adj):.1f}%")

    # Check if adj[n] relates to k[d[n]]
    print("\n=== adj[n] modulo k[1..10] ===")
    for n in range(4, min(20, max(adj.keys()))):
        if n in adj:
            mods = []
            for d in range(1, min(n, 11)):
                if d in k:
                    mods.append(f"mod k[{d}]={adj[n] % k[d]}")
            print(f"  adj[{n}] = {adj[n]}: {', '.join(mods[:5])}")

if __name__ == "__main__":
    main()
