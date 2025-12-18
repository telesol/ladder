#!/usr/bin/env python3
"""
Ladder Generator Prototype
Goal: Reconstruct the key generation method used in Bitcoin Puzzle

Two hypotheses tested:
1. EC-based: adj_n derived from elliptic curve point operations
2. PRNG-based: adj_n derived from seeded random number generator
"""

import sqlite3
import hashlib
from typing import List, Tuple, Optional

# secp256k1 parameters
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
GX = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
GY = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8

class ECPoint:
    """Simple EC point on secp256k1"""
    def __init__(self, x: Optional[int], y: Optional[int]):
        self.x = x
        self.y = y

    def is_infinity(self):
        return self.x is None

    @staticmethod
    def infinity():
        return ECPoint(None, None)

def modinv(a: int, m: int) -> int:
    """Modular inverse using extended Euclidean algorithm"""
    if a < 0:
        a = a % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError("Modular inverse doesn't exist")
    return x % m

def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def ec_add(p1: ECPoint, p2: ECPoint) -> ECPoint:
    """Add two EC points"""
    if p1.is_infinity():
        return p2
    if p2.is_infinity():
        return p1

    if p1.x == p2.x:
        if p1.y != p2.y:
            return ECPoint.infinity()
        # Point doubling
        if p1.y == 0:
            return ECPoint.infinity()
        lam = (3 * p1.x * p1.x * modinv(2 * p1.y, P)) % P
    else:
        lam = ((p2.y - p1.y) * modinv(p2.x - p1.x, P)) % P

    x3 = (lam * lam - p1.x - p2.x) % P
    y3 = (lam * (p1.x - x3) - p1.y) % P
    return ECPoint(x3, y3)

def ec_multiply(k: int, point: ECPoint) -> ECPoint:
    """Scalar multiplication using double-and-add"""
    result = ECPoint.infinity()
    addend = point

    while k:
        if k & 1:
            result = ec_add(result, addend)
        addend = ec_add(addend, addend)
        k >>= 1

    return result

G = ECPoint(GX, GY)

def load_known_keys(db_path: str = "db/kh.db") -> dict:
    """Load known keys from database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT puzzle_id, priv_hex FROM keys ORDER BY puzzle_id")
    rows = cursor.fetchall()
    conn.close()

    keys = {}
    for puzzle_id, priv_hex in rows:
        keys[puzzle_id] = int(priv_hex, 16)
    return keys

def compute_adj_n(k: List[int], n: int) -> int:
    """Compute adj_n from recurrence: k_n = 2*k_{n-1} + adj_n"""
    return k[n] - 2 * k[n-1]

def compute_m_d(k: List[int], n: int) -> Tuple[int, int]:
    """
    Find m_n and d_n such that:
    adj_n = 2^n - m_n * k_{d_n}
    d_n in {1..8}, chosen to minimize |m_n|
    """
    adj_n = compute_adj_n(k, n)

    best_d, best_m = None, None
    best_m_abs = float('inf')

    for d in range(1, min(n, 9)):  # d from 1 to min(n-1, 8)
        if k[d] == 0:
            continue
        # adj_n = 2^n - m * k[d]
        # m = (2^n - adj_n) / k[d]
        numerator = (1 << n) - adj_n
        if numerator % k[d] == 0:
            m = numerator // k[d]
            if abs(m) < best_m_abs:
                best_m = m
                best_d = d
                best_m_abs = abs(m)

    return best_m, best_d

def analyze_ec_hypothesis(keys: dict) -> None:
    """Test if adj_n relates to EC point operations"""
    print("\n=== EC Hypothesis Analysis ===")
    print("Testing: adj_n = f(x(n*G)) mod 2^n")
    print()

    k = [0] + [keys.get(i, 0) for i in range(1, 71)]

    matches = []
    for n in range(2, 21):  # Test first 20
        adj_n = compute_adj_n(k, n)
        P = ec_multiply(n, G)
        x_coord = P.x

        # Test various functions
        x_mod = x_coord % (1 << n)
        x_low_bits = x_coord & ((1 << n) - 1)
        x_hash = int(hashlib.sha256(x_coord.to_bytes(32, 'big')).hexdigest(), 16) % (1 << n)

        match_direct = (x_mod == adj_n)
        match_low = (x_low_bits == adj_n)
        match_hash = (x_hash == adj_n)

        print(f"n={n:2d}: adj_n={adj_n:15d}, x(n*G) mod 2^n={x_mod:15d}, match={match_direct}")

        if match_direct or match_low or match_hash:
            matches.append(n)

    print(f"\nMatches found: {len(matches)}/{19}")
    if matches:
        print(f"Matching n values: {matches}")

def test_prng_lcg(seed: int, a: int, c: int, m: int, n_keys: int) -> List[int]:
    """
    Generate sequence using LCG PRNG
    x_{n+1} = (a*x_n + c) mod m
    """
    k = [0, 1]  # k_0=0, k_1=1
    rng_state = seed

    for n in range(2, n_keys + 1):
        # Generate next PRNG value
        rng_state = (a * rng_state + c) % m

        # Scale to get normalized m in [0.72, 2.75]
        norm_m = 0.72 + (rng_state / m) * (2.75 - 0.72)

        # Find best d (1-8) to minimize |m|
        best_d, best_m_val = 1, None
        for d in range(1, min(n, 9)):
            if k[d] == 0:
                continue
            m_val = int(norm_m * (1 << (n - d)))
            if best_m_val is None or abs(m_val) < abs(best_m_val):
                best_d = d
                best_m_val = m_val

        if best_m_val is None:
            best_m_val = 1

        # Compute adjustment and new key
        adj_n = (1 << n) - best_m_val * k[best_d]
        k_n = 2 * k[n-1] + adj_n
        k.append(k_n)

    return k

def verify_sequence(generated: List[int], actual: dict, n_check: int = 20) -> Tuple[int, int]:
    """Count how many generated keys match actual keys"""
    matches = 0
    for n in range(1, min(n_check + 1, len(generated))):
        if generated[n] == actual.get(n, -1):
            matches += 1
    return matches, min(n_check, len(generated) - 1)

def search_lcg_seeds():
    """Search for LCG parameters that could generate the sequence"""
    print("\n=== PRNG (LCG) Seed Search ===")

    keys = load_known_keys()

    # Common LCG parameters to try
    lcg_params = [
        # (a, c, m) - various well-known LCGs
        (1103515245, 12345, 2**31),  # glibc
        (6364136223846793005, 1442695040888963407, 2**64),  # Knuth
        (1664525, 1013904223, 2**32),  # Numerical Recipes
        (22695477, 1, 2**32),  # Borland
    ]

    best_match = 0
    best_params = None

    for a, c, m in lcg_params:
        print(f"\nTesting LCG(a={a}, c={c}, m={m})")

        # Try seeds 0-100
        for seed in range(101):
            generated = test_prng_lcg(seed, a, c, m, 70)
            matches, total = verify_sequence(generated, keys)

            if matches > best_match:
                best_match = matches
                best_params = (seed, a, c, m, generated[:21])
                print(f"  Seed {seed}: {matches}/{total} matches")

    print(f"\nBest result: {best_match} matches")
    if best_params:
        print(f"  Parameters: seed={best_params[0]}, a={best_params[1]}, c={best_params[2]}, m={best_params[3]}")
        print(f"  First 20 generated: {best_params[4][1:21]}")

def analyze_m_sequence():
    """Analyze the m sequence for patterns"""
    print("\n=== m-Sequence Analysis ===")

    keys = load_known_keys()
    k = [0] + [keys.get(i, 0) for i in range(1, 71)]

    print("n   |  m_n        |  d_n  |  norm_m = m/(2^(n-d))")
    print("----|-------------|-------|----------------------")

    m_vals = []
    norm_m_vals = []

    for n in range(2, 71):
        m, d = compute_m_d(k, n)
        if m is not None and d is not None:
            norm_m = m / (1 << (n - d))
            m_vals.append(m)
            norm_m_vals.append(norm_m)
            if n <= 25:  # Print first 25
                print(f"{n:3d} | {m:11d} | {d:5d} | {norm_m:.6f}")

    print(f"\nStatistics (n=2..70):")
    print(f"  norm_m range: [{min(norm_m_vals):.4f}, {max(norm_m_vals):.4f}]")
    print(f"  norm_m mean:  {sum(norm_m_vals)/len(norm_m_vals):.4f}")

def main():
    print("=" * 60)
    print("LADDER GENERATOR PROTOTYPE")
    print("Testing EC and PRNG reconstruction hypotheses")
    print("=" * 60)

    # Load known keys
    keys = load_known_keys()
    print(f"\nLoaded {len(keys)} known keys from database")

    # Analyze m sequence
    analyze_m_sequence()

    # Test EC hypothesis
    analyze_ec_hypothesis(keys)

    # Search PRNG seeds
    search_lcg_seeds()

    print("\n" + "=" * 60)
    print("Analysis complete")
    print("=" * 60)

if __name__ == "__main__":
    main()
