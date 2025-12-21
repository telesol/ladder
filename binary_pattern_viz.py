#!/usr/bin/env python3
"""
Binary Pattern Visualization Tool

Quick visualization and analysis of specific binary patterns in the keys.
Can be used to explore interesting findings from the main analysis.
"""

import sqlite3
from pathlib import Path

def visualize_binary_progression(start, end, db_path="/home/rkh/ladder/db/kh.db"):
    """Show binary progression from start to end puzzle."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT puzzle_id, priv_hex
        FROM keys
        WHERE puzzle_id BETWEEN ? AND ?
        ORDER BY puzzle_id
    """, (start, end))

    print(f"\nBinary Progression k[{start}] to k[{end}]")
    print("=" * 100)
    print(f"{'n':<4} {'k (dec)':<20} {'Binary':<70} {'Pop':<4} {'HD':<4}")
    print("-" * 100)

    prev_k = None
    for pid, phex in cursor.fetchall():
        k = int(phex[2:] if phex.startswith('0x') else phex, 16)
        binary = bin(k)[2:]
        popcount = bin(k).count('1')

        # Hamming distance from previous
        hamming = ""
        if prev_k is not None:
            hamming = str(bin(k ^ prev_k).count('1'))

        # Format binary with spaces every 8 bits
        binary_formatted = ' '.join([binary[i:i+8] for i in range(0, len(binary), 8)])

        print(f"{pid:<4} {k:<20} {binary_formatted:<70} {popcount:<4} {hamming:<4}")
        prev_k = k

    conn.close()

def analyze_xor_sequence(start, end, db_path="/home/rkh/ladder/db/kh.db"):
    """Analyze XOR pattern between consecutive keys."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT puzzle_id, priv_hex
        FROM keys
        WHERE puzzle_id BETWEEN ? AND ?
        ORDER BY puzzle_id
    """, (start, end))

    keys = {}
    for pid, phex in cursor.fetchall():
        keys[pid] = int(phex[2:] if phex.startswith('0x') else phex, 16)

    conn.close()

    print(f"\nXOR Analysis k[{start}] to k[{end}]")
    print("=" * 100)
    print(f"{'n':<4} {'k[n] XOR k[n-1]':<25} {'Binary':<70} {'Pop':<4}")
    print("-" * 100)

    for n in sorted(keys.keys())[1:]:
        xor = keys[n] ^ keys[n-1]
        binary = bin(xor)[2:]
        popcount = bin(xor).count('1')

        # Check if power of 2
        is_pow2 = (xor & (xor - 1)) == 0 and xor != 0
        marker = " ← POWER OF 2" if is_pow2 else ""

        # Format binary
        binary_formatted = ' '.join([binary[i:i+8] for i in range(0, len(binary), 8)])

        print(f"{n:<4} {hex(xor):<25} {binary_formatted:<70} {popcount:<4}{marker}")

def show_bit_diff_pattern(start, end, db_path="/home/rkh/ladder/db/kh.db"):
    """Show bit_count - n pattern."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT puzzle_id, priv_hex
        FROM keys
        WHERE puzzle_id BETWEEN ? AND ?
        ORDER BY puzzle_id
    """, (start, end))

    print(f"\nBit Count vs Puzzle Number: popcount(k[n]) - n")
    print("=" * 70)
    print(f"{'n':<4} {'Popcount':<10} {'n':<4} {'Difference':<12} {'Trend':<20}")
    print("-" * 70)

    prev_diff = None
    for pid, phex in cursor.fetchall():
        k = int(phex[2:] if phex.startswith('0x') else phex, 16)
        popcount = bin(k).count('1')
        diff = popcount - pid

        # Trend analysis
        trend = ""
        if prev_diff is not None:
            if diff > prev_diff:
                trend = "↑ increasing"
            elif diff < prev_diff:
                trend = "↓ decreasing"
            else:
                trend = "→ stable"

        print(f"{pid:<4} {popcount:<10} {pid:<4} {diff:<12} {trend:<20}")
        prev_diff = diff

    conn.close()

def find_interesting_patterns(db_path="/home/rkh/ladder/db/kh.db"):
    """Find and display interesting patterns."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT puzzle_id, priv_hex FROM keys WHERE puzzle_id <= 70 ORDER BY puzzle_id")

    keys = {}
    for pid, phex in cursor.fetchall():
        keys[pid] = int(phex[2:] if phex.startswith('0x') else phex, 16)

    conn.close()

    print("\n" + "=" * 100)
    print("INTERESTING BINARY PATTERNS DISCOVERED")
    print("=" * 100)

    # 1. Mersenne-like patterns (all 1s)
    print("\n1. MERSENNE-LIKE PATTERNS (consecutive 1s)")
    print("-" * 70)
    for n, k in keys.items():
        binary = bin(k)[2:]
        if '0' not in binary[:min(len(binary), 10)]:  # First 10 bits all 1s
            print(f"   k[{n}] = {k} = {binary} (all 1s in first {len(binary)} bits)")

    # 2. Low Hamming weight
    print("\n2. LOW HAMMING WEIGHT (sparse 1s)")
    print("-" * 70)
    for n, k in keys.items():
        popcount = bin(k).count('1')
        bit_length = len(bin(k)[2:])
        if popcount <= 3 and bit_length >= 6:
            density = popcount / bit_length * 100
            print(f"   k[{n}] = {k} = {bin(k)[2:]} (only {popcount} ones, density={density:.1f}%)")

    # 3. Powers of 2 or near powers of 2
    print("\n3. POWERS OF 2 OR NEAR POWERS OF 2")
    print("-" * 70)
    for n, k in keys.items():
        # Check if power of 2
        if k & (k - 1) == 0 and k != 0:
            exp = k.bit_length() - 1
            print(f"   k[{n}] = {k} = 2^{exp} = {bin(k)[2:]}")
        # Check if one less than power of 2 (Mersenne form)
        elif (k + 1) & k == 0:
            exp = (k + 1).bit_length() - 1
            print(f"   k[{n}] = {k} = 2^{exp} - 1 = {bin(k)[2:]} (Mersenne)")

    # 4. Exceptional Hamming distances
    print("\n4. EXCEPTIONAL HAMMING DISTANCES (very small or large)")
    print("-" * 70)
    for n in sorted(keys.keys())[1:]:
        hamming = bin(keys[n] ^ keys[n-1]).count('1')
        if hamming <= 2:
            print(f"   H(k[{n}], k[{n-1}]) = {hamming} (very small!)")
        elif hamming >= 35:
            print(f"   H(k[{n}], k[{n-1}]) = {hamming} (very large!)")

    # 5. XOR patterns that are powers of 2
    print("\n5. XOR VALUES THAT ARE POWERS OF 2")
    print("-" * 70)
    for n in sorted(keys.keys())[1:]:
        xor = keys[n] ^ keys[n-1]
        if xor & (xor - 1) == 0 and xor != 0:
            exp = xor.bit_length() - 1
            print(f"   k[{n}] XOR k[{n-1}] = {xor} = 2^{exp} = {bin(xor)[2:]}")

    # 6. Bit length exactly equals puzzle number
    print("\n6. BIT LENGTH RELATIONSHIP")
    print("-" * 70)
    exact_matches = 0
    for n, k in keys.items():
        bit_length = len(bin(k)[2:])
        if bit_length == n:
            exact_matches += 1
    print(f"   Keys where bit_length(k[n]) == n: {exact_matches}/{len(keys)}")
    if exact_matches == len(keys):
        print("   ★★★ PERFECT MATCH! All keys have bit_length == puzzle_number ★★★")

def main():
    """Main menu."""
    import sys

    if len(sys.argv) < 2:
        print("Binary Pattern Visualization Tool")
        print("=" * 70)
        print("\nUsage:")
        print("  python binary_pattern_viz.py progression <start> <end>")
        print("  python binary_pattern_viz.py xor <start> <end>")
        print("  python binary_pattern_viz.py bitdiff <start> <end>")
        print("  python binary_pattern_viz.py interesting")
        print("\nExamples:")
        print("  python binary_pattern_viz.py progression 1 10")
        print("  python binary_pattern_viz.py xor 1 20")
        print("  python binary_pattern_viz.py bitdiff 1 30")
        print("  python binary_pattern_viz.py interesting")
        return

    cmd = sys.argv[1].lower()

    if cmd == "progression":
        if len(sys.argv) < 4:
            print("Usage: binary_pattern_viz.py progression <start> <end>")
            return
        start = int(sys.argv[2])
        end = int(sys.argv[3])
        visualize_binary_progression(start, end)

    elif cmd == "xor":
        if len(sys.argv) < 4:
            print("Usage: binary_pattern_viz.py xor <start> <end>")
            return
        start = int(sys.argv[2])
        end = int(sys.argv[3])
        analyze_xor_sequence(start, end)

    elif cmd == "bitdiff":
        if len(sys.argv) < 4:
            print("Usage: binary_pattern_viz.py bitdiff <start> <end>")
            return
        start = int(sys.argv[2])
        end = int(sys.argv[3])
        show_bit_diff_pattern(start, end)

    elif cmd == "interesting":
        find_interesting_patterns()

    else:
        print(f"Unknown command: {cmd}")
        print("Valid commands: progression, xor, bitdiff, interesting")

if __name__ == "__main__":
    main()
