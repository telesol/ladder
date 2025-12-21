#!/usr/bin/env python3
"""
Generate period tables showing k[n] mod p for visualization.
Shows the first 40 values in tabular format.
"""

import json
import sqlite3

# Read data
with open('/home/rkh/ladder/data_for_csolver.json', 'r') as f:
    data = json.load(f)

# Query k values
conn = sqlite3.connect('/home/rkh/ladder/db/kh.db')
cursor = conn.cursor()
cursor.execute("SELECT puzzle_id, priv_hex FROM keys WHERE puzzle_id <= 70 ORDER BY puzzle_id")
results = cursor.fetchall()
conn.close()

k_values = {puzzle_id: int(priv_hex, 16) for puzzle_id, priv_hex in results}

primes = [7, 17, 19, 37, 41]

print("="*80)
print("PERIOD TABLES: k[n] mod p")
print("="*80)
print("\nShowing k[n] mod p for n=1 to 40")
print("="*80)

# Create table for each prime
for p in primes:
    print(f"\n{'='*80}")
    print(f"k[n] mod {p}")
    print('='*80)

    # Header
    print(f"{'n':<5}", end='')
    for i in range(10):
        print(f"{i:<4}", end='')
    print()
    print('-' * 80)

    # Rows (n = 0..40, showing in groups of 10)
    for row in range(4):
        start_n = row * 10 + 1
        print(f"{start_n:<5}", end='')

        for col in range(10):
            n = start_n + col
            if n in k_values and n <= 40:
                val = k_values[n] % p
                print(f"{val:<4}", end='')
            else:
                print(f"{'--':<4}", end='')
        print()

# Create highlighted zero table
print("\n" + "="*80)
print("ZERO PATTERNS VISUALIZATION")
print("="*80)
print("\nLegend: X = k[n]≡0 (mod p), . = k[n]≢0 (mod p)")
print("="*80)

for p in [7, 17, 19]:
    print(f"\np = {p}:")

    zeros = set(n for n in sorted(k_values.keys()) if k_values[n] % p == 0)

    # Show pattern for n=1..70
    for row in range(7):
        start_n = row * 10 + 1
        line = f"{start_n:>2}-{min(start_n+9, 70):>2}: "

        for col in range(10):
            n = start_n + col
            if n > 70:
                break

            if n in zeros:
                line += "X "
            else:
                line += ". "

        print(line)

# Statistical analysis of spacing
print("\n" + "="*80)
print("ZERO SPACING STATISTICS")
print("="*80)

for p in primes:
    zeros = sorted([n for n in k_values.keys() if k_values[n] % p == 0])

    if len(zeros) > 1:
        gaps = [zeros[i+1] - zeros[i] for i in range(len(zeros)-1)]

        print(f"\np = {p}: {len(zeros)} zeros")
        print(f"  Positions: {zeros}")
        print(f"  Gaps: {gaps}")
        print(f"  Min gap: {min(gaps)}")
        print(f"  Max gap: {max(gaps)}")
        print(f"  Mean gap: {sum(gaps)/len(gaps):.2f}")

        # Check if constant
        if len(set(gaps)) == 1:
            print(f"  *** PERIODIC with period {gaps[0]} ***")
        else:
            print(f"  Not periodic ({len(set(gaps))} different gaps)")
    elif len(zeros) == 1:
        print(f"\np = {p}: 1 zero at n={zeros[0]}")
    else:
        print(f"\np = {p}: No zeros")

# Compare k[n] mod p patterns
print("\n" + "="*80)
print("CROSS-PRIME CORRELATIONS")
print("="*80)

print("\nChecking if k[n]≡0 (mod p1) implies k[n]≡? (mod p2)")

for i, p1 in enumerate(primes[:3]):
    for p2 in primes[i+1:4]:
        zeros_p1 = set(n for n in k_values.keys() if k_values[n] % p1 == 0)

        if zeros_p1:
            print(f"\nk[n]≡0 (mod {p1}) at n={sorted(zeros_p1)[:5]}")
            print(f"  k[n] mod {p2} at these n:")

            for n in sorted(zeros_p1)[:5]:
                val = k_values[n] % p2
                print(f"    k[{n}] ≡ {val} (mod {p2})")

print("\n" + "="*80)
print("Period table generation complete!")
print("="*80)
