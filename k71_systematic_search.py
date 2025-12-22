#!/usr/bin/env python3
"""
Systematic search for k[71] based on discovered patterns.

Key insights:
1. k[n]/2^n oscillates for odd n: HIGH-LOW-HIGH-LOW
2. n=69 was HIGH (~1.24 for m-ratio, ~0.50 for k-ratio)
3. n=71 should follow the oscillation pattern
4. Anchors at n=61 (φ-1), n=90 (1/√2)
"""

import hashlib
import sqlite3

try:
    import ecdsa
    HAS_ECDSA = True
except ImportError:
    HAS_ECDSA = False
    print("Warning: ecdsa not available")

TARGET = 'f6f5431d25bbf7b12e8add9af5e3475c44a0a5b8'

def load_keys():
    conn = sqlite3.connect('/home/solo/LA/db/kh.db')
    cursor = conn.cursor()
    cursor.execute("SELECT puzzle_id, priv_hex FROM keys WHERE puzzle_id IS NOT NULL")
    rows = cursor.fetchall()
    conn.close()
    return {int(pid): int(hex_val, 16) for pid, hex_val in rows if pid and hex_val}

def compute_hash160(k):
    if not HAS_ECDSA:
        return None
    try:
        sk = ecdsa.SigningKey.from_secret_exponent(k, curve=ecdsa.SECP256k1)
        vk = sk.verifying_key
        point = vk.pubkey.point
        prefix = b'\x02' if point.y() % 2 == 0 else b'\x03'
        compressed = prefix + point.x().to_bytes(32, 'big')
        return hashlib.new('ripemd160', hashlib.sha256(compressed).digest()).hexdigest()
    except:
        return None

def search_around_prediction(k70, base_ratio, ratio_range, name):
    """Search around a predicted k[71]/2^71 ratio"""
    print(f"\n=== Searching: {name} ===")
    print(f"Base ratio: {base_ratio:.8f}")
    print(f"Search range: ±{ratio_range:.4f}")

    k71_base = int(base_ratio * (2**71))
    step = int(ratio_range * (2**71) / 1000)  # 1000 steps in range

    checked = 0
    for offset in range(-500, 501):
        k71 = k71_base + offset * step
        if k71 < 2**70 or k71 >= 2**71:
            continue

        h = compute_hash160(k71)
        checked += 1

        if h == TARGET:
            print(f"\n✓ FOUND! k[71] = {k71}")
            print(f"         = {hex(k71)}")
            print(f"  k[71]/2^71 = {k71 / (2**71):.10f}")
            # Verify m[71]
            m71 = 2**71 - k71 + 2*k70
            print(f"  m[71] = {m71}")
            print(f"  m[71]/2^71 = {m71 / (2**71):.10f}")
            return k71

    print(f"  Checked {checked} values, no match found")
    return None

def main():
    if not HAS_ECDSA:
        print("Need ecdsa library for hash verification")
        return

    k = load_keys()
    k70 = k[70]
    print(f"k[70] = {k70}")
    print(f"k[70]/2^70 = {k70 / (2**70):.10f}")

    # Based on oscillation pattern analysis:
    # n=67: k-ratio=0.899 (odd, medium-high)
    # n=69: k-ratio=0.504 (odd, low)
    # n=71: should be HIGH based on alternating

    # Try different hypotheses:

    # Hypothesis 1: n=71 follows HIGH pattern (like n=67)
    search_around_prediction(k70, 0.85, 0.10, "HIGH hypothesis (like n=67)")

    # Hypothesis 2: n=71 is near a constant
    import math
    constants = [
        ('π/4', math.pi/4),
        ('e/π', math.e/math.pi),
        ('1/φ', 2/(1+math.sqrt(5))),
        ('ln(2)', math.log(2)),
        ('2/e', 2/math.e),
        ('1/√2', 1/math.sqrt(2)),
        ('3/4', 0.75),
        ('7/8', 0.875),
    ]

    for name, val in constants:
        search_around_prediction(k70, val, 0.02, f"Near {name}")

    # Hypothesis 3: Linear interpolation between anchors
    # Anchor at 61 (φ-1 ≈ 0.618), anchor at 90 (1/√2 ≈ 0.707)
    # Linear interpolation to 71
    t = (71 - 61) / (90 - 61)  # = 10/29
    interp_ratio = 0.618 + t * (0.707 - 0.618)
    search_around_prediction(k70, interp_ratio, 0.05, "Linear interp 61→90")

    print("\n" + "=" * 60)
    print("Search complete. If no match found, pattern is more complex.")
    print("=" * 60)

if __name__ == "__main__":
    main()
