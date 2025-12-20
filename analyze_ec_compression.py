#!/usr/bin/env python3
"""
Analyze EC point compression patterns for Bitcoin puzzle keys.

Key insight: All puzzle keys use compressed format (02/03 prefix).
The prefix encodes y-coordinate parity (02=even, 03=odd).

Is there a pattern in the parity sequence?
"""

import sqlite3
import hashlib

# secp256k1 parameters
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
A = 0
B = 7
Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

def modinv(a, m):
    """Modular inverse using extended Euclidean algorithm."""
    if a < 0:
        a = a % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError("Modular inverse doesn't exist")
    return x % m

def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def point_add(p1, p2):
    """Add two points on secp256k1."""
    if p1 is None:
        return p2
    if p2 is None:
        return p1

    x1, y1 = p1
    x2, y2 = p2

    if x1 == x2 and y1 != y2:
        return None  # Point at infinity

    if x1 == x2:  # Point doubling
        m = (3 * x1 * x1) * modinv(2 * y1, P) % P
    else:
        m = (y2 - y1) * modinv(x2 - x1, P) % P

    x3 = (m * m - x1 - x2) % P
    y3 = (m * (x1 - x3) - y1) % P

    return (x3, y3)

def scalar_mult(k, point):
    """Multiply point by scalar k."""
    result = None
    addend = point

    while k:
        if k & 1:
            result = point_add(result, addend)
        addend = point_add(addend, addend)
        k >>= 1

    return result

def get_y_parity(k):
    """Get y-coordinate parity for k*G."""
    G = (Gx, Gy)
    P_point = scalar_mult(k, G)
    if P_point is None:
        return None
    x, y = P_point
    return y % 2  # 0 = even (02), 1 = odd (03)

def main():
    print("=" * 70)
    print("EC COMPRESSION ANALYSIS - Y-Parity Patterns")
    print("=" * 70)

    # Load keys from database
    conn = sqlite3.connect('/home/rkh/ladder/db/kh.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT puzzle_id, priv_hex
        FROM keys
        WHERE puzzle_id IS NOT NULL
          AND puzzle_id BETWEEN 1 AND 90
          AND priv_hex IS NOT NULL
        ORDER BY puzzle_id
    """)
    rows = cursor.fetchall()
    conn.close()

    print(f"\nLoaded {len(rows)} keys from database")
    print()

    # Compute y-parity for each key
    parities = {}
    parity_seq = []

    print("Computing y-parities (this may take a moment)...")
    print()

    for puzzle_id, hex_val in rows:
        if hex_val is None:
            continue
        k = int(hex_val, 16)
        if k == 0:
            continue
        parity = get_y_parity(k)
        parities[puzzle_id] = parity
        parity_seq.append((puzzle_id, parity))

        prefix = "02" if parity == 0 else "03"
        print(f"k[{puzzle_id:2d}] = {k:>25d}  →  prefix: {prefix}")

    print()
    print("=" * 70)
    print("PARITY SEQUENCE ANALYSIS")
    print("=" * 70)

    # Extract just parities for analysis
    just_parities = [p for _, p in parity_seq]

    # Display as binary string
    parity_str = ''.join(['0' if p == 0 else '1' for p in just_parities])
    print(f"\nParity sequence (0=02/even, 1=03/odd):")

    # Show in groups of 10
    for i in range(0, len(parity_str), 10):
        chunk = parity_str[i:i+10]
        start_id = parity_seq[i][0] if i < len(parity_seq) else i+1
        end_idx = min(i+10, len(parity_seq))
        end_id = parity_seq[end_idx-1][0] if end_idx <= len(parity_seq) else end_idx
        print(f"  k[{start_id:2d}-{end_id:2d}]: {chunk}")

    # Count statistics
    zeros = parity_str.count('0')
    ones = parity_str.count('1')
    total = len(parity_str)

    print(f"\nStatistics:")
    print(f"  02 (even y): {zeros}/{total} = {100*zeros/total:.1f}%")
    print(f"  03 (odd y):  {ones}/{total} = {100*ones/total:.1f}%")

    # Check for patterns
    print()
    print("=" * 70)
    print("PATTERN DETECTION")
    print("=" * 70)

    # Run length encoding
    print("\nRun-length encoding:")
    runs = []
    current = just_parities[0]
    count = 1
    for p in just_parities[1:]:
        if p == current:
            count += 1
        else:
            runs.append((current, count))
            current = p
            count = 1
    runs.append((current, count))

    run_str = ' '.join([f"{'0' if r[0]==0 else '1'}×{r[1]}" for r in runs[:30]])
    print(f"  {run_str}...")

    # Check for periodicity
    print("\nPeriodicity check:")
    for period in range(2, 20):
        matches = 0
        for i in range(period, len(just_parities)):
            if just_parities[i] == just_parities[i - period]:
                matches += 1
        match_rate = matches / (len(just_parities) - period)
        if match_rate > 0.55:
            print(f"  Period {period}: {100*match_rate:.1f}% match")

    # Check if parity correlates with k mod something
    print("\nCorrelation with k mod n:")
    for mod in [2, 3, 4, 5, 6]:
        correlation = 0
        for puzzle_id, hex_val in rows:
            k = int(hex_val, 16)
            parity = parities[puzzle_id]
            if (k % mod) % 2 == parity:
                correlation += 1
        print(f"  k mod {mod} (mod 2) vs parity: {correlation}/{len(rows)} = {100*correlation/len(rows):.1f}%")

    # The key insight: y² = x³ + 7 (mod p)
    # Parity of y depends on the quadratic residue choice
    print()
    print("=" * 70)
    print("KEY INSIGHT")
    print("=" * 70)
    print("""
The y-parity is determined by:
  y² ≡ x³ + 7 (mod p)

For each x, there are two possible y values: y and p-y
One is even, one is odd.

The sequence of parities depends on the sequence of x-coordinates,
which depends on the sequence of k values.

If there's a pattern in k, it might manifest as a pattern in parities.
""")

if __name__ == "__main__":
    main()
