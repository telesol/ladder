#!/usr/bin/env python3
"""
Verify k[71] prediction against target HASH160.
Also explore the anchor-based prediction refinement.
"""

import sqlite3
import hashlib
import math

# Target for puzzle 71
TARGET_HASH160 = "f6f5431d25bbf7b12e8add9af5e3475c44a0a5b8"

# Constants
PI = math.pi
E = math.e
PHI = (1 + math.sqrt(5)) / 2
LN2 = math.log(2)

CONSTANTS = {
    'π/4': PI/4,
    'e/π': E/PI,
    '1/φ': 1/PHI,
    'ln(2)': LN2,
    'e/4': E/4,
    '2/e': 2/E,
    '1/√2': 1/math.sqrt(2),
    '1/2': 0.5,
    '2/3': 2/3,
    '3/4': 0.75,
    '7/8': 0.875,
}

def load_keys():
    conn = sqlite3.connect('/home/solo/LA/db/kh.db')
    cursor = conn.cursor()
    cursor.execute("SELECT puzzle_id, priv_hex FROM keys WHERE puzzle_id IS NOT NULL ORDER BY puzzle_id")
    rows = cursor.fetchall()
    conn.close()
    keys = {}
    for puzzle_id, priv_hex in rows:
        if priv_hex and puzzle_id is not None:
            keys[int(puzzle_id)] = int(priv_hex, 16)
    return keys

def compute_m(k):
    m = {}
    for n in range(2, max(k.keys()) + 1):
        if n in k and n-1 in k:
            m[n] = 2**n - k[n] + 2*k[n-1]
    return m

def privkey_to_hash160(privkey_int):
    """Convert private key integer to HASH160 (simplified - for testing)"""
    # This is a placeholder - actual BTC uses secp256k1
    # For now, just compute a hash to check format
    try:
        import ecdsa
        from hashlib import sha256

        # Get the signing key
        sk = ecdsa.SigningKey.from_secret_exponent(privkey_int, curve=ecdsa.SECP256k1)

        # Get public key (compressed)
        vk = sk.verifying_key
        pubkey_point = vk.pubkey.point
        x = pubkey_point.x()
        y = pubkey_point.y()

        # Compressed format
        prefix = b'\x02' if y % 2 == 0 else b'\x03'
        compressed_pubkey = prefix + x.to_bytes(32, 'big')

        # HASH160 = RIPEMD160(SHA256(pubkey))
        sha256_hash = hashlib.sha256(compressed_pubkey).digest()
        ripemd160 = hashlib.new('ripemd160')
        ripemd160.update(sha256_hash)
        return ripemd160.hexdigest()
    except ImportError:
        return None
    except Exception as e:
        return f"error: {e}"

def analyze_m_oscillation(m, k):
    """Analyze m[n]/2^n oscillation pattern to refine prediction"""
    print("=" * 60)
    print("M-OSCILLATION PATTERN ANALYSIS")
    print("=" * 60)

    # Look at odd n values near 71
    print("\nOdd n values (61-71):")
    for n in [61, 63, 65, 67, 69]:
        if n in m:
            m_ratio = m[n] / (2**n)
            k_ratio = k[n] / (2**n) if n in k else 0
            print(f"  n={n}: m/2^n={m_ratio:.6f}, k/2^n={k_ratio:.6f}")

    # Check pattern: Is there a period in the oscillation?
    print("\nChecking for oscillation period:")
    odd_m_ratios = [(n, m[n] / (2**n)) for n in sorted(m.keys()) if n % 2 == 1 and n >= 55 and n <= 70]
    for i, (n, ratio) in enumerate(odd_m_ratios):
        direction = "↑" if i > 0 and ratio > odd_m_ratios[i-1][1] else "↓" if i > 0 else "-"
        print(f"  n={n}: {ratio:.4f} {direction}")

    # Calculate prediction based on alternating pattern
    print("\nAlternating pattern analysis:")
    # n=61 (high), n=63 (low), n=65 (high), n=67 (low), n=69 (high)
    # So n=71 should be LOW
    highs = [m[n] / (2**n) for n in [61, 65, 69] if n in m]
    lows = [m[n] / (2**n) for n in [63, 67] if n in m]

    if highs and lows:
        avg_high = sum(highs) / len(highs)
        avg_low = sum(lows) / len(lows)
        print(f"  Average HIGH (61,65,69): {avg_high:.6f}")
        print(f"  Average LOW (63,67): {avg_low:.6f}")

        # Predict n=71 as LOW (continuing pattern)
        m_71_low = int(avg_low * (2**71))
        k_71_from_low = 2*k[70] + 2**71 - m_71_low

        print(f"\n  If n=71 is LOW: m[71] ≈ {m_71_low}")
        print(f"                  k[71] ≈ {k_71_from_low}")
        print(f"                  k[71] hex: {hex(k_71_from_low)}")

        # Also check HIGH case
        m_71_high = int(avg_high * (2**71))
        k_71_from_high = 2*k[70] + 2**71 - m_71_high

        print(f"\n  If n=71 is HIGH: m[71] ≈ {m_71_high}")
        print(f"                   k[71] ≈ {k_71_from_high}")
        print(f"                   k[71] hex: {hex(k_71_from_high)}")

def generate_k71_candidates(k, m):
    """Generate multiple k[71] candidates based on different hypotheses"""
    print("\n" + "=" * 60)
    print("K[71] CANDIDATE GENERATION")
    print("=" * 60)

    candidates = []

    # Method 1: Each constant
    for name, val in CONSTANTS.items():
        k_71 = int(val * (2**71))
        # Verify it's in valid range
        if 2**70 <= k_71 < 2**71:
            m_71 = 2**71 - k_71 + 2*k[70]
            candidates.append({
                'method': f'constant {name}',
                'k_71': k_71,
                'm_71': m_71
            })

    # Method 2: Based on oscillation (LOW prediction)
    odd_lows = [m[n] / (2**n) for n in [63, 67] if n in m]
    if odd_lows:
        avg_low = sum(odd_lows) / len(odd_lows)
        m_71 = int(avg_low * (2**71))
        k_71 = 2*k[70] + 2**71 - m_71
        if 2**70 <= k_71 < 2**71:
            candidates.append({
                'method': 'oscillation LOW',
                'k_71': k_71,
                'm_71': m_71
            })

    # Method 3: Based on oscillation (HIGH prediction)
    odd_highs = [m[n] / (2**n) for n in [61, 65, 69] if n in m]
    if odd_highs:
        avg_high = sum(odd_highs) / len(odd_highs)
        m_71 = int(avg_high * (2**71))
        k_71 = 2*k[70] + 2**71 - m_71
        if 2**70 <= k_71 < 2**71:
            candidates.append({
                'method': 'oscillation HIGH',
                'k_71': k_71,
                'm_71': m_71
            })

    # Method 4: Linear extrapolation from m[69], m[70]
    if 69 in m and 70 in m:
        m_diff = m[70] - m[69]
        m_71_extrap = m[70] + m_diff
        k_71_extrap = 2*k[70] + 2**71 - m_71_extrap
        if 2**70 <= k_71_extrap < 2**71:
            candidates.append({
                'method': 'linear extrapolation',
                'k_71': k_71_extrap,
                'm_71': m_71_extrap
            })

    # Method 5: m[71] = 2*m[70] - m[69] (centered difference)
    if 69 in m and 70 in m:
        m_71_centered = 2*m[70] - m[69]
        k_71_centered = 2*k[70] + 2**71 - m_71_centered
        if 2**70 <= k_71_centered < 2**71:
            candidates.append({
                'method': 'centered difference',
                'k_71': k_71_centered,
                'm_71': m_71_centered
            })

    print(f"\nGenerated {len(candidates)} candidates:\n")
    for c in candidates:
        k_ratio = c['k_71'] / (2**71)
        print(f"  {c['method']:25s}: k[71] = {hex(c['k_71'])}")
        print(f"  {' ':25s}  k[71]/2^71 = {k_ratio:.8f}")

    return candidates

def verify_candidates(candidates):
    """Verify candidates against target hash (if ecdsa available)"""
    print("\n" + "=" * 60)
    print("HASH160 VERIFICATION")
    print("=" * 60)

    try:
        import ecdsa
        print(f"\nTarget HASH160: {TARGET_HASH160}")
        print("\nChecking candidates...")

        for c in candidates[:5]:  # Check first 5
            hash160 = privkey_to_hash160(c['k_71'])
            match = "✓ MATCH!" if hash160 == TARGET_HASH160 else ""
            print(f"  {c['method']:25s}: {hash160} {match}")

    except ImportError:
        print("\necdsa module not available. Install with: pip install ecdsa")
        print("Showing hex values only:")
        for c in candidates[:5]:
            print(f"  {c['method']:25s}: {hex(c['k_71'])}")

def main():
    k = load_keys()
    m = compute_m(k)

    print(f"Loaded {len(k)} keys")
    print(f"k[70] = {k[70]} = {hex(k[70])}")

    analyze_m_oscillation(m, k)
    candidates = generate_k71_candidates(k, m)
    verify_candidates(candidates)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("""
The k[71] value depends on predicting m[71] correctly.

Key observations:
1. m[n]/2^n oscillates for odd n: HIGH-LOW-HIGH-LOW pattern
2. n=69 was HIGH (~1.24), so n=71 should be LOW (~0.80)
3. Anchor before 71 is n=61 (φ-1)
4. Anchor after 71 is n=90 (1/√2)

Most likely prediction: k[71]/2^71 ≈ LOW value (0.75-0.85)

To verify, we need to check HASH160 against target.
""")

if __name__ == "__main__":
    main()
