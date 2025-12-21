#!/usr/bin/env python3
"""
Binary Pattern Analysis for Bitcoin Puzzle Keys k[1-70]

This script analyzes various binary patterns in the private keys:
- Bit counts (popcount)
- Longest runs of 1s and 0s
- Hamming distances between consecutive keys
- XOR patterns between consecutive keys
- Relationships between bit_count and puzzle number
"""

import sqlite3
import sys
from pathlib import Path

def get_keys_from_db(db_path, start=1, end=70):
    """Query database for keys in range [start, end]."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT puzzle_id, priv_hex
        FROM keys
        WHERE puzzle_id BETWEEN ? AND ?
        ORDER BY puzzle_id
    """, (start, end))

    keys = {}
    for puzzle_id, priv_hex in cursor.fetchall():
        # Remove '0x' prefix if present
        hex_str = priv_hex[2:] if priv_hex.startswith('0x') else priv_hex
        keys[puzzle_id] = int(hex_str, 16)

    conn.close()
    return keys

def popcount(n):
    """Count number of 1 bits in n."""
    return bin(n).count('1')

def longest_run(binary_str, char):
    """Find longest consecutive run of 'char' in binary_str."""
    max_run = 0
    current_run = 0

    for bit in binary_str:
        if bit == char:
            current_run += 1
            max_run = max(max_run, current_run)
        else:
            current_run = 0

    return max_run

def hamming_distance(a, b):
    """Calculate Hamming distance between two integers."""
    return popcount(a ^ b)

def analyze_binary_patterns(keys):
    """Perform comprehensive binary pattern analysis."""
    results = {}

    for n in sorted(keys.keys()):
        k = keys[n]
        binary = bin(k)[2:]  # Remove '0b' prefix

        # Basic metrics
        bit_length = len(binary)
        ones_count = popcount(k)
        zeros_count = bit_length - ones_count

        # Run lengths
        longest_ones = longest_run(binary, '1')
        longest_zeros = longest_run(binary, '0')

        # Relationship to puzzle number
        bit_diff = ones_count - n

        # Hamming distance and XOR with previous key
        hamming_dist = None
        xor_value = None
        xor_popcount = None

        if n > 1 and (n-1) in keys:
            prev_k = keys[n-1]
            hamming_dist = hamming_distance(k, prev_k)
            xor_value = k ^ prev_k
            xor_popcount = popcount(xor_value)

        results[n] = {
            'k': k,
            'hex': hex(k),
            'binary': binary,
            'bit_length': bit_length,
            'popcount': ones_count,
            'zeros': zeros_count,
            'longest_ones': longest_ones,
            'longest_zeros': longest_zeros,
            'bit_diff': bit_diff,
            'hamming_dist': hamming_dist,
            'xor_value': xor_value,
            'xor_popcount': xor_popcount
        }

    return results

def format_binary_with_spaces(binary_str, group_size=8):
    """Format binary string with spaces for readability."""
    # Pad to multiple of group_size
    padded = binary_str.zfill((len(binary_str) + group_size - 1) // group_size * group_size)
    groups = [padded[i:i+group_size] for i in range(0, len(padded), group_size)]
    return ' '.join(groups)

def generate_markdown_report(results, output_file):
    """Generate comprehensive markdown report."""

    with open(output_file, 'w') as f:
        f.write("# Binary Pattern Analysis of Bitcoin Puzzle Keys (k[1-70])\n\n")
        f.write("Analysis Date: 2025-12-21\n\n")

        # Table of Contents
        f.write("## Table of Contents\n\n")
        f.write("1. [Popcount Analysis](#popcount-analysis)\n")
        f.write("2. [Run Length Analysis](#run-length-analysis)\n")
        f.write("3. [Bit Count vs Puzzle Number](#bit-count-vs-puzzle-number)\n")
        f.write("4. [Hamming Distance Sequence](#hamming-distance-sequence)\n")
        f.write("5. [XOR Pattern Analysis](#xor-pattern-analysis)\n")
        f.write("6. [Complete Binary Table](#complete-binary-table)\n")
        f.write("7. [Discovered Regularities](#discovered-regularities)\n\n")

        # Section 1: Popcount Analysis
        f.write("## Popcount Analysis\n\n")
        f.write("Popcount is the number of 1-bits in the binary representation.\n\n")
        f.write("| n | k (hex) | Bit Length | Popcount | Zeros | Density |\n")
        f.write("|---|---------|------------|----------|-------|----------|\n")

        for n in sorted(results.keys()):
            r = results[n]
            density = r['popcount'] / r['bit_length'] if r['bit_length'] > 0 else 0
            f.write(f"| {n} | {r['hex'][2:]:>16} | {r['bit_length']:>10} | "
                   f"{r['popcount']:>8} | {r['zeros']:>5} | {density:>6.2%} |\n")

        # Statistics
        popcounts = [r['popcount'] for r in results.values()]
        f.write(f"\n**Statistics:**\n")
        f.write(f"- Min popcount: {min(popcounts)}\n")
        f.write(f"- Max popcount: {max(popcounts)}\n")
        f.write(f"- Average popcount: {sum(popcounts)/len(popcounts):.2f}\n")
        f.write(f"- Median popcount: {sorted(popcounts)[len(popcounts)//2]}\n\n")

        # Section 2: Run Length Analysis
        f.write("## Run Length Analysis\n\n")
        f.write("Analysis of consecutive sequences of 0s and 1s.\n\n")
        f.write("| n | Longest Run of 1s | Longest Run of 0s | Binary (grouped) |\n")
        f.write("|---|-------------------|-------------------|------------------|\n")

        for n in sorted(results.keys())[:20]:  # First 20 for readability
            r = results[n]
            binary_formatted = format_binary_with_spaces(r['binary'], 4)
            f.write(f"| {n} | {r['longest_ones']:>17} | {r['longest_zeros']:>17} | "
                   f"`{binary_formatted}` |\n")

        f.write(f"\n... (showing first 20 entries)\n\n")

        # Run length statistics
        longest_ones_list = [r['longest_ones'] for r in results.values()]
        longest_zeros_list = [r['longest_zeros'] for r in results.values()]

        f.write(f"**Run Length Statistics:**\n")
        f.write(f"- Max longest run of 1s: {max(longest_ones_list)} (puzzle {[n for n, r in results.items() if r['longest_ones'] == max(longest_ones_list)][0]})\n")
        f.write(f"- Max longest run of 0s: {max(longest_zeros_list)} (puzzle {[n for n, r in results.items() if r['longest_zeros'] == max(longest_zeros_list)][0]})\n")
        f.write(f"- Avg longest run of 1s: {sum(longest_ones_list)/len(longest_ones_list):.2f}\n")
        f.write(f"- Avg longest run of 0s: {sum(longest_zeros_list)/len(longest_zeros_list):.2f}\n\n")

        # Section 3: Bit Count vs Puzzle Number
        f.write("## Bit Count vs Puzzle Number\n\n")
        f.write("Analyzing the relationship: `bit_diff = popcount(k[n]) - n`\n\n")
        f.write("| n | Popcount | n | Difference (popcount - n) |\n")
        f.write("|---|----------|---|---------------------------|\n")

        for n in sorted(results.keys()):
            r = results[n]
            f.write(f"| {n} | {r['popcount']:>8} | {n:>1} | {r['bit_diff']:>25} |\n")

        # Statistics on bit_diff
        bit_diffs = [r['bit_diff'] for r in results.values()]
        f.write(f"\n**Bit Difference Statistics:**\n")
        f.write(f"- Min: {min(bit_diffs)}\n")
        f.write(f"- Max: {max(bit_diffs)}\n")
        f.write(f"- Average: {sum(bit_diffs)/len(bit_diffs):.2f}\n")

        # Check for patterns
        positive_count = sum(1 for d in bit_diffs if d > 0)
        negative_count = sum(1 for d in bit_diffs if d < 0)
        zero_count = sum(1 for d in bit_diffs if d == 0)

        f.write(f"- Positive differences: {positive_count}\n")
        f.write(f"- Negative differences: {negative_count}\n")
        f.write(f"- Zero differences: {zero_count}\n\n")

        # Section 4: Hamming Distance
        f.write("## Hamming Distance Sequence\n\n")
        f.write("Hamming distance between consecutive keys: `H(k[n], k[n-1])`\n\n")
        f.write("| n | k[n] (hex) | k[n-1] (hex) | Hamming Distance |\n")
        f.write("|---|------------|--------------|------------------|\n")

        for n in sorted(results.keys()):
            if n > 1:
                r = results[n]
                r_prev = results[n-1]
                f.write(f"| {n} | {r['hex'][2:]:>16} | {r_prev['hex'][2:]:>16} | "
                       f"{r['hamming_dist']:>16} |\n")

        # Hamming distance statistics
        hamming_dists = [r['hamming_dist'] for r in results.values() if r['hamming_dist'] is not None]
        f.write(f"\n**Hamming Distance Statistics:**\n")
        f.write(f"- Min: {min(hamming_dists)}\n")
        f.write(f"- Max: {max(hamming_dists)}\n")
        f.write(f"- Average: {sum(hamming_dists)/len(hamming_dists):.2f}\n")
        f.write(f"- Median: {sorted(hamming_dists)[len(hamming_dists)//2]}\n\n")

        # Section 5: XOR Patterns
        f.write("## XOR Pattern Analysis\n\n")
        f.write("Analysis of `k[n] XOR k[n-1]`\n\n")
        f.write("| n | k[n] XOR k[n-1] (hex) | XOR Popcount | XOR Binary |\n")
        f.write("|---|-----------------------|--------------|------------|\n")

        for n in sorted(results.keys())[:25]:  # First 25
            if n > 1:
                r = results[n]
                xor_hex = hex(r['xor_value'])[2:]
                xor_bin = bin(r['xor_value'])[2:]
                xor_formatted = format_binary_with_spaces(xor_bin, 4)
                f.write(f"| {n} | {xor_hex:>21} | {r['xor_popcount']:>12} | "
                       f"`{xor_formatted}` |\n")

        f.write(f"\n... (showing first 25 entries)\n\n")

        # XOR statistics
        xor_popcounts = [r['xor_popcount'] for r in results.values() if r['xor_popcount'] is not None]
        f.write(f"**XOR Popcount Statistics:**\n")
        f.write(f"- Min: {min(xor_popcounts)}\n")
        f.write(f"- Max: {max(xor_popcounts)}\n")
        f.write(f"- Average: {sum(xor_popcounts)/len(xor_popcounts):.2f}\n")
        f.write(f"- Median: {sorted(xor_popcounts)[len(xor_popcounts)//2]}\n\n")

        # Check for XOR patterns
        f.write("**XOR Value Analysis:**\n\n")
        xor_values = [(n, r['xor_value']) for n, r in results.items() if r['xor_value'] is not None]

        # Check if XOR values are powers of 2 or near powers of 2
        power_of_2_count = 0
        for n, xor_val in xor_values:
            if xor_val & (xor_val - 1) == 0:  # Check if power of 2
                power_of_2_count += 1
                if power_of_2_count <= 10:  # Show first 10
                    f.write(f"- k[{n}] XOR k[{n-1}] = {hex(xor_val)} (power of 2: 2^{xor_val.bit_length()-1})\n")

        f.write(f"\nTotal XOR values that are powers of 2: {power_of_2_count}/{len(xor_values)}\n\n")

        # Section 6: Complete Binary Table
        f.write("## Complete Binary Table\n\n")
        f.write("Full binary representations of all keys.\n\n")
        f.write("| n | Hex | Binary (grouped by 8 bits) |\n")
        f.write("|---|-----|----------------------------|\n")

        for n in sorted(results.keys()):
            r = results[n]
            binary_formatted = format_binary_with_spaces(r['binary'], 8)
            # Truncate hex for display
            hex_short = r['hex'][2:][-16:] if len(r['hex']) > 18 else r['hex'][2:]
            f.write(f"| {n} | {hex_short:>16} | `{binary_formatted}` |\n")

        # Section 7: Discovered Regularities
        f.write("\n## Discovered Regularities\n\n")

        # Analyze various patterns
        f.write("### Key Observations\n\n")

        # 1. Popcount growth
        f.write("#### 1. Popcount Growth Pattern\n\n")
        popcount_increases = 0
        for n in sorted(results.keys())[1:]:
            if results[n]['popcount'] > results[n-1]['popcount']:
                popcount_increases += 1

        f.write(f"- Popcount increases from k[n-1] to k[n]: {popcount_increases}/{len(results)-1} times\n")
        f.write(f"- Percentage of increases: {popcount_increases/(len(results)-1)*100:.1f}%\n\n")

        # 2. Bit length relationship
        f.write("#### 2. Bit Length Relationship\n\n")
        bit_length_equals_n = 0
        bit_length_around_n = 0
        for n in sorted(results.keys()):
            if results[n]['bit_length'] == n:
                bit_length_equals_n += 1
            if abs(results[n]['bit_length'] - n) <= 2:
                bit_length_around_n += 1

        f.write(f"- Keys where bit_length exactly equals n: {bit_length_equals_n}/{len(results)}\n")
        f.write(f"- Keys where bit_length is within ±2 of n: {bit_length_around_n}/{len(results)}\n\n")

        # 3. Hamming distance patterns
        f.write("#### 3. Hamming Distance Patterns\n\n")
        small_hamming = sum(1 for d in hamming_dists if d <= 5)
        large_hamming = sum(1 for d in hamming_dists if d >= 15)

        f.write(f"- Small Hamming distances (≤5): {small_hamming}/{len(hamming_dists)}\n")
        f.write(f"- Large Hamming distances (≥15): {large_hamming}/{len(hamming_dists)}\n\n")

        # 4. XOR patterns
        f.write("#### 4. XOR Patterns\n\n")
        f.write(f"- XOR values that are powers of 2: {power_of_2_count}/{len(xor_values)}\n")
        f.write(f"- Percentage: {power_of_2_count/len(xor_values)*100:.1f}%\n\n")

        # 5. Correlation analysis
        f.write("#### 5. Correlation Between Metrics\n\n")

        # Simple correlation: do larger n have larger popcount?
        ns = sorted(results.keys())
        pcs = [results[n]['popcount'] for n in ns]

        # Calculate simple correlation coefficient
        n_mean = sum(ns) / len(ns)
        pc_mean = sum(pcs) / len(pcs)

        numerator = sum((ns[i] - n_mean) * (pcs[i] - pc_mean) for i in range(len(ns)))
        denom_n = sum((n - n_mean) ** 2 for n in ns) ** 0.5
        denom_pc = sum((pc - pc_mean) ** 2 for pc in pcs) ** 0.5

        if denom_n > 0 and denom_pc > 0:
            correlation = numerator / (denom_n * denom_pc)
            f.write(f"- Correlation between puzzle number (n) and popcount: {correlation:.4f}\n")

            if correlation > 0.7:
                f.write("  - **Strong positive correlation**: As n increases, popcount tends to increase\n")
            elif correlation < -0.7:
                f.write("  - **Strong negative correlation**: As n increases, popcount tends to decrease\n")
            else:
                f.write("  - **Weak or no correlation**: No strong linear relationship\n")

        f.write("\n### Summary of Findings\n\n")
        f.write("Based on the analysis of binary patterns in k[1-70]:\n\n")
        f.write("1. **Popcount Distribution**: ")
        f.write(f"Ranges from {min(popcounts)} to {max(popcounts)} with average {sum(popcounts)/len(popcounts):.2f}\n")

        f.write("2. **Run Lengths**: ")
        f.write(f"Maximum consecutive 1s: {max(longest_ones_list)}, maximum consecutive 0s: {max(longest_zeros_list)}\n")

        f.write("3. **Hamming Distances**: ")
        f.write(f"Between consecutive keys range from {min(hamming_dists)} to {max(hamming_dists)}\n")

        f.write("4. **XOR Patterns**: ")
        if power_of_2_count > len(xor_values) * 0.1:
            f.write(f"Notable presence of power-of-2 XOR values ({power_of_2_count}/{len(xor_values)})\n")
        else:
            f.write(f"XOR values show typical distribution\n")

        f.write("5. **Bit Count vs Puzzle Number**: ")
        if abs(sum(bit_diffs)/len(bit_diffs)) < 2:
            f.write("Bit count closely tracks puzzle number on average\n")
        else:
            f.write(f"Bit count deviates from puzzle number by {sum(bit_diffs)/len(bit_diffs):.2f} on average\n")

        f.write("\n---\n")
        f.write("\n*Analysis complete. All patterns documented above.*\n")

def main():
    """Main execution function."""
    db_path = Path("/home/rkh/ladder/db/kh.db")
    output_file = Path("/home/rkh/ladder/binary_patterns.md")

    if not db_path.exists():
        print(f"Error: Database not found at {db_path}")
        sys.exit(1)

    print("Binary Pattern Analysis for Bitcoin Puzzle Keys")
    print("=" * 50)
    print()

    print("Step 1: Querying database for k[1-70]...")
    keys = get_keys_from_db(db_path, 1, 70)
    print(f"✓ Retrieved {len(keys)} keys")
    print()

    print("Step 2: Analyzing binary patterns...")
    results = analyze_binary_patterns(keys)
    print(f"✓ Analysis complete")
    print()

    print("Step 3: Generating markdown report...")
    generate_markdown_report(results, output_file)
    print(f"✓ Report written to {output_file}")
    print()

    # Print some quick stats to console
    print("Quick Summary:")
    print("-" * 50)
    popcounts = [r['popcount'] for r in results.values()]
    hamming_dists = [r['hamming_dist'] for r in results.values() if r['hamming_dist'] is not None]

    print(f"Popcount range: {min(popcounts)} - {max(popcounts)}")
    print(f"Average popcount: {sum(popcounts)/len(popcounts):.2f}")
    print(f"Hamming distance range: {min(hamming_dists)} - {max(hamming_dists)}")
    print(f"Average Hamming distance: {sum(hamming_dists)/len(hamming_dists):.2f}")

    xor_popcounts = [r['xor_popcount'] for r in results.values() if r['xor_popcount'] is not None]
    print(f"XOR popcount range: {min(xor_popcounts)} - {max(xor_popcounts)}")
    print(f"Average XOR popcount: {sum(xor_popcounts)/len(xor_popcounts):.2f}")

    print()
    print("Analysis complete!")

if __name__ == "__main__":
    main()
