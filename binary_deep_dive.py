#!/usr/bin/env python3
"""
Binary Deep Dive - Analyze bit patterns in k-sequence

Looking for:
1. XOR relationships between consecutive keys
2. Bit density patterns
3. Position of highest/lowest set bits
4. Hamming distance patterns
"""
import sqlite3

# Load known k values
conn = sqlite3.connect('/home/solo/ladder/db/kh.db')
cur = conn.cursor()
k_values = {}
for n in range(1, 91):
    cur.execute('SELECT priv_hex FROM keys WHERE puzzle_id = ?', (n,))
    row = cur.fetchone()
    if row:
        k_values[n] = int(row[0], 16)
conn.close()

print("=" * 70)
print("BINARY DEEP DIVE - k-Sequence Bit Pattern Analysis")
print("=" * 70)
print()

# 1. Bit density (Hamming weight / bit_length)
print("### Bit Density (popcount / bit_length) ###")
print()
print("| n  | k[n]           | bits | popcount | density |")
print("|----|----------------|------|----------|---------|")

densities = []
for n in range(1, 71):
    if n in k_values:
        k = k_values[n]
        bits = k.bit_length()
        popcount = bin(k).count('1')
        density = popcount / bits if bits > 0 else 0
        densities.append((n, density))
        if n <= 20 or n >= 60:
            print(f"| {n:2} | {k:14} | {bits:4} | {popcount:8} | {density:.4f} |")

print()
avg_density = sum(d for _, d in densities) / len(densities)
print(f"Average density: {avg_density:.4f}")
print()

# 2. XOR patterns
print("### XOR Patterns (k[n] XOR k[n-1]) ###")
print()

xor_densities = []
for n in range(2, 71):
    if n in k_values and (n-1) in k_values:
        xor = k_values[n] ^ k_values[n-1]
        bits = xor.bit_length()
        popcount = bin(xor).count('1')
        density = popcount / bits if bits > 0 else 0
        xor_densities.append((n, popcount, density))

print("XOR popcount statistics:")
popcounts = [p for _, p, _ in xor_densities]
print(f"  Min: {min(popcounts)}")
print(f"  Max: {max(popcounts)}")
print(f"  Avg: {sum(popcounts)/len(popcounts):.1f}")
print()

# Find low XOR popcount (similar consecutive keys)
print("Low XOR popcount cases (k[n] very similar to k[n-1]):")
for n, popcount, density in xor_densities:
    if popcount < 10:
        print(f"  n={n}: XOR popcount = {popcount}")
print()

# 3. Position of lowest set bit
print("### Lowest Set Bit Position ###")
print()

def lowest_set_bit(n):
    if n == 0:
        return -1
    pos = 0
    while (n & 1) == 0:
        n >>= 1
        pos += 1
    return pos

lsb_positions = []
for n in range(1, 71):
    if n in k_values:
        lsb = lowest_set_bit(k_values[n])
        lsb_positions.append((n, lsb))
        if lsb > 5:
            print(f"  k[{n}] has LSB at position {lsb} (divisible by 2^{lsb})")

print()

# 4. Special patterns
print("### Special Binary Patterns ###")
print()

for n in range(1, 71):
    if n in k_values:
        k = k_values[n]
        bits = k.bit_length()
        popcount = bin(k).count('1')
        
        # Check if k is near a power of 2
        if popcount == 1:
            print(f"  k[{n}] = 2^{bits-1} (single bit set)")
        elif popcount == 2:
            print(f"  k[{n}] has only 2 bits set")
        
        # Check if k is Mersenne-like (2^m - 1)
        if k == (1 << bits) - 1:
            print(f"  k[{n}] = 2^{bits} - 1 (Mersenne form)")

print()

# 5. Bit position patterns
print("### Bit Position Analysis (first 20 k-values) ###")
print()

for n in range(1, 21):
    if n in k_values:
        k = k_values[n]
        bits = k.bit_length()
        # Show binary with bit positions marked
        binary = bin(k)[2:]
        positions = [i for i, b in enumerate(binary[::-1]) if b == '1']
        print(f"k[{n:2}] = {k:10} | positions: {positions}")

print()

# 6. Consecutive bit patterns
print("### Consecutive 1-bit Runs ###")
print()

def longest_run(n):
    if n == 0:
        return 0
    binary = bin(n)[2:]
    runs = binary.split('0')
    return max(len(r) for r in runs if r)

for n in range(1, 71):
    if n in k_values:
        k = k_values[n]
        run = longest_run(k)
        if run >= 6:
            print(f"  k[{n}] has {run} consecutive 1-bits")

print()
print("=" * 70)
