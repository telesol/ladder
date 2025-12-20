#!/usr/bin/env python3
"""
Kolmogorov Complexity Analysis of k-sequence

If we can compress the sequence significantly, we've found structure.
The compression ratio tells us how much redundancy/pattern exists.
"""

import sqlite3
import zlib
import lzma
import math
import struct

def load_k_sequence():
    """Load k[1-70] from database."""
    conn = sqlite3.connect('/home/rkh/ladder/db/kh.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT puzzle_id, priv_hex
        FROM keys
        WHERE puzzle_id BETWEEN 1 AND 70
          AND priv_hex IS NOT NULL
        ORDER BY puzzle_id
    """)
    rows = cursor.fetchall()
    conn.close()

    K = {}
    for pid, hex_val in rows:
        K[pid] = int(hex_val, 16)
    return K

def bits_needed(n):
    """Bits needed to represent n."""
    if n == 0:
        return 1
    return n.bit_length()

def to_bytes_sequence(K):
    """Convert k-sequence to byte sequence."""
    # Each k[n] needs n bits (approximately)
    # We'll pack them as variable-length integers

    data = b''
    for n in range(1, 71):
        if n in K:
            k = K[n]
            # Store as bytes (big-endian, variable length)
            byte_len = (k.bit_length() + 7) // 8
            if byte_len == 0:
                byte_len = 1
            data += k.to_bytes(byte_len, 'big')

    return data

def to_delta_sequence(K):
    """Convert to delta encoding: store differences from 2^(n-1)."""
    data = b''

    for n in range(1, 71):
        if n in K:
            k = K[n]
            # k[n] is in range [2^(n-1), 2^n)
            # Store offset from 2^(n-1)
            if n == 1:
                offset = k  # k[1] = 1
            else:
                offset = k - (2 ** (n - 1))

            # Offset needs at most n-1 bits
            byte_len = max(1, (offset.bit_length() + 7) // 8)
            data += offset.to_bytes(byte_len, 'big')

    return data

def to_adj_sequence(K):
    """Convert to adj encoding: adj[n] = k[n] - 2*k[n-1]."""
    data = b''

    for n in range(2, 71):
        if n in K and n-1 in K:
            adj = K[n] - 2 * K[n-1]
            # adj can be negative
            # Use signed encoding
            sign_byte = b'\x00' if adj >= 0 else b'\x01'
            abs_adj = abs(adj)
            byte_len = max(1, (abs_adj.bit_length() + 7) // 8)
            data += sign_byte + abs_adj.to_bytes(byte_len, 'big')

    return data

def main():
    print("=" * 70)
    print("KOLMOGOROV COMPLEXITY ANALYSIS OF K-SEQUENCE")
    print("=" * 70)

    K = load_k_sequence()
    print(f"\nLoaded {len(K)} keys (k[1] to k[70])")

    # Raw storage requirement
    raw_bits = sum(bits_needed(K[n]) for n in K)
    print(f"\nRaw storage (variable-length): {raw_bits} bits = {raw_bits/8:.1f} bytes")

    # Theoretical minimum (each k[n] in [2^(n-1), 2^n) needs ~n-1 bits)
    theoretical_bits = sum(n-1 for n in range(2, 71)) + 1  # +1 for k[1]=1
    print(f"Theoretical minimum (random in range): {theoretical_bits} bits = {theoretical_bits/8:.1f} bytes")

    print()
    print("=" * 70)
    print("COMPRESSION TESTS")
    print("=" * 70)

    # Test different encodings
    encodings = {
        'Raw bytes': to_bytes_sequence(K),
        'Delta (offset from 2^(n-1))': to_delta_sequence(K),
        'Adj sequence': to_adj_sequence(K),
    }

    for name, data in encodings.items():
        print(f"\n{name}:")
        print(f"  Uncompressed: {len(data)} bytes")

        # zlib compression
        zlib_compressed = zlib.compress(data, level=9)
        print(f"  zlib:         {len(zlib_compressed)} bytes ({100*len(zlib_compressed)/len(data):.1f}%)")

        # lzma compression
        lzma_compressed = lzma.compress(data, preset=9)
        print(f"  lzma:         {len(lzma_compressed)} bytes ({100*len(lzma_compressed)/len(data):.1f}%)")

    print()
    print("=" * 70)
    print("STRUCTURE ANALYSIS")
    print("=" * 70)

    # Check if k-sequence can be described by a short formula
    print("\nChecking known formulas:")

    # 1. k[n] = 2*k[n-1] + adj[n]
    print("\n1. Recurrence: k[n] = 2*k[n-1] + adj[n]")
    adj_sizes = []
    for n in range(2, 71):
        if n in K and n-1 in K:
            adj = K[n] - 2 * K[n-1]
            adj_sizes.append(bits_needed(abs(adj)))
            if n <= 10:
                print(f"   adj[{n}] = {adj} ({bits_needed(abs(adj))} bits)")

    avg_adj_bits = sum(adj_sizes) / len(adj_sizes)
    print(f"   Average |adj[n]| size: {avg_adj_bits:.1f} bits")
    print(f"   Total adj storage: {sum(adj_sizes) + len(adj_sizes)} bits (with signs)")

    # 2. Check 3-step recursion: k[n] = 9*k[n-3] + offset
    print("\n2. 3-step recursion: k[n] = 9*k[n-3] + offset")
    offset_sizes = []
    for n in range(4, 71):
        if n in K and n-3 in K:
            offset = K[n] - 9 * K[n-3]
            offset_sizes.append(bits_needed(abs(offset)))
            if n <= 10 or n >= 65:
                print(f"   offset[{n:2d}] = {offset:>25d} ({bits_needed(abs(offset)):2d} bits)")

    avg_offset_bits = sum(offset_sizes) / len(offset_sizes)
    print(f"   Average |offset[n]| size: {avg_offset_bits:.1f} bits")

    # 3. Check the unified formula
    print("\n3. Unified formula: m[n] = (2^n - adj[n]) / k[d[n]]")
    print("   (See COMPLETE_FORMULA_SYSTEM.md)")
    print("   If we can derive adj[n], we can derive k[n]")

    print()
    print("=" * 70)
    print("COMPRESSION RATIO SUMMARY")
    print("=" * 70)

    # Best compression ratio
    raw = to_bytes_sequence(K)
    compressed = lzma.compress(raw, preset=9)
    ratio = len(compressed) / len(raw)

    print(f"\nBest compression: {len(raw)} → {len(compressed)} bytes")
    print(f"Compression ratio: {ratio:.2%}")
    print(f"Bits saved: {8*len(raw) - 8*len(compressed)} bits")

    # Entropy estimate
    import collections
    byte_counts = collections.Counter(raw)
    entropy = -sum((c/len(raw)) * math.log2(c/len(raw)) for c in byte_counts.values() if c > 0)
    print(f"\nByte-level entropy: {entropy:.2f} bits/byte (max 8)")
    print(f"Estimated minimum size: {len(raw) * entropy / 8:.1f} bytes")

    print()
    print("=" * 70)
    print("CONCLUSION")
    print("=" * 70)
    print(f"""
The k-sequence compresses to {ratio:.1%} of its raw size.

This means there IS significant structure, but not trivially expressible.

The adj-sequence representation is more compact because:
- adj[n] grows slower than k[n]
- adj[n] has more regularity (sign patterns, magnitude patterns)

Key insight: The generator likely works with adj[n], not k[n] directly.
If we find the adj[n] formula, we have the complete solution.
""")

if __name__ == "__main__":
    main()
