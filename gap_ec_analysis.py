#!/usr/bin/env python3
"""
ELLIPTIC CURVE ANALYSIS FOR GAP PUZZLES

CRITICAL INSIGHT: Bitcoin uses secp256k1 elliptic curve.
What if the GAP puzzles have EC relationships?

Test:
1. P[n] = k[n] × G (public key from private key)
2. Check if P[75] = 5×P[15] or similar EC point addition
3. Check if P[n] has patterns not visible in k[n]
"""

import sqlite3

DB_PATH = "/home/solo/LA/db/kh.db"

def get_keys_with_pubkeys():
    """Load keys with public key coordinates"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT puzzle_id, priv_hex, x_hex, y_hex
        FROM keys
        WHERE puzzle_id IS NOT NULL
        AND x_hex IS NOT NULL
        ORDER BY puzzle_id
    """)

    rows = cursor.fetchall()
    conn.close()

    data = {}
    for pid, priv_hex, x_hex, y_hex in rows:
        data[pid] = {
            'k': int(priv_hex, 16),
            'x': int(x_hex, 16) if x_hex else None,
            'y': int(y_hex, 16) if y_hex else None
        }

    return data

def analyze_ec_point_patterns(data):
    """Analyze patterns in EC point coordinates"""
    print("="*80)
    print("ELLIPTIC CURVE POINT ANALYSIS")
    print("="*80)

    gap_keys = [70, 75, 80, 85, 90]

    print("\nGAP puzzle public key coordinates:\n")

    for n in gap_keys:
        if n in data and data[n]['x'] is not None:
            k = data[n]['k']
            x = data[n]['x']
            y = data[n]['y']

            print(f"n={n}:")
            print(f"  k[{n}] = {k}")
            print(f"  P[{n}].x = {x}")
            print(f"  P[{n}].y = {y}")
            print(f"  x hex: {hex(x)}")
            print(f"  y hex: {hex(y)}")

            # Analyze x coordinate
            x_bits = x.bit_length()
            y_bits = y.bit_length()

            print(f"  x bit length: {x_bits}")
            print(f"  y bit length: {y_bits}")
            print()

def test_ec_multiples(data):
    """Test if P[5n] = 5×P[n] (EC point multiplication)"""
    print("="*80)
    print("EC POINT MULTIPLICATION TEST")
    print("="*80)
    print("\nHypothesis: P[5n] = 5×P[n] (not k[5n] = 5×k[n]!)")
    print("This would be an EC relationship, not algebraic\n")

    # For EC points, we can't test without EC library
    # But we can check if k values suggest EC operations

    test_pairs = [
        (14, 70),
        (15, 75),
        (16, 80),
        (17, 85),
        (18, 90),
    ]

    print("Testing k[5n] mod k[n]:\n")

    for n1, n2 in test_pairs:
        if n1 in data and n2 in data:
            k1 = data[n1]['k']
            k2 = data[n2]['k']

            quotient = k2 // k1
            remainder = k2 % k1

            print(f"k[{n2}] / k[{n1}]:")
            print(f"  Quotient: {quotient}")
            print(f"  Remainder: {remainder}")
            print(f"  k[{n2}] = {quotient}×k[{n1}] + {remainder}")
            print()

def test_x_coordinate_patterns(data):
    """Test if x-coordinates have patterns"""
    print("="*80)
    print("X-COORDINATE PATTERN ANALYSIS")
    print("="*80)

    gap_keys = sorted([n for n in [70, 75, 80, 85, 90] if n in data])

    print("\nTesting x-coordinate relationships:\n")

    for i in range(len(gap_keys) - 1):
        n1 = gap_keys[i]
        n2 = gap_keys[i + 1]

        if data[n1]['x'] is not None and data[n2]['x'] is not None:
            x1 = data[n1]['x']
            x2 = data[n2]['x']

            print(f"P[{n1}].x → P[{n2}].x:")
            print(f"  x[{n2}] / x[{n1}] = {x2 / x1:.6f}")
            print(f"  x[{n2}] - x[{n1}] = {x2 - x1}")
            print(f"  x[{n2}] XOR x[{n1}] popcount = {bin(x1 ^ x2).count('1')}")
            print()

def check_ec_order_patterns(data):
    """Check if keys relate to secp256k1 curve order"""
    print("="*80)
    print("SECP256K1 CURVE ORDER ANALYSIS")
    print("="*80)

    # secp256k1 curve order
    n_curve = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

    print(f"\nsecp256k1 curve order n = {n_curve}")
    print(f"                          = {hex(n_curve)}\n")

    gap_keys = sorted([n for n in [70, 75, 80, 85, 90] if n in data])

    print("Testing k[n] mod n_curve:\n")

    for n in gap_keys:
        k = data[n]['k']
        k_mod_n = k % n_curve

        print(f"k[{n}] mod n_curve = {k_mod_n}")
        print(f"                   = {hex(k_mod_n)}")

        # Check if it's close to a simple fraction of n_curve
        for frac in [2, 3, 4, 5, 10, 100]:
            threshold = n_curve // frac
            if abs(k_mod_n - threshold) < threshold * 0.01:  # Within 1%
                print(f"  !! Close to n_curve/{frac}")

        print()

def main():
    print("="*80)
    print("GAP PUZZLE ELLIPTIC CURVE ANALYSIS")
    print("="*80)

    data = get_keys_with_pubkeys()

    print(f"\nLoaded {len(data)} keys with public key data\n")

    # Check which GAP keys have pubkey data
    gap_keys = [70, 75, 80, 85, 90]
    available = [n for n in gap_keys if n in data and data[n]['x'] is not None]

    print(f"GAP keys with pubkey data: {available}\n")

    if len(available) > 0:
        analyze_ec_point_patterns(data)
        test_ec_multiples(data)
        test_x_coordinate_patterns(data)
        check_ec_order_patterns(data)
    else:
        print("⚠ No public key data available for GAP keys in database")
        print("Public keys may need to be computed from private keys")

    print("\n" + "="*80)
    print("EC ANALYSIS COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()
