#!/usr/bin/env python3
"""
Test specific m[71] candidates by verifying against the Bitcoin address.
"""

import hashlib

# secp256k1 curve parameters
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8

def modinv(a, m):
    if a < 0:
        a = a % m
    g, x = extended_gcd(a, m)[:2]
    return x % m

def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    return gcd, y1 - (b // a) * x1, x1

def point_add(p1, p2):
    if p1 is None: return p2
    if p2 is None: return p1
    x1, y1, x2, y2 = p1[0], p1[1], p2[0], p2[1]
    if x1 == x2 and y1 != y2: return None
    if x1 == x2:
        m = (3 * x1 * x1) * modinv(2 * y1, P) % P
    else:
        m = (y2 - y1) * modinv(x2 - x1, P) % P
    x3 = (m * m - x1 - x2) % P
    y3 = (m * (x1 - x3) - y1) % P
    return (x3, y3)

def point_multiply(k, point):
    result = None
    addend = point
    while k:
        if k & 1:
            result = point_add(result, addend)
        addend = point_add(addend, addend)
        k >>= 1
    return result

def privkey_to_address(privkey_int):
    pubkey = point_multiply(privkey_int, (Gx, Gy))
    x, y = pubkey
    prefix = b'\x02' if y % 2 == 0 else b'\x03'
    pubkey_compressed = prefix + x.to_bytes(32, 'big')
    sha = hashlib.sha256(pubkey_compressed).digest()
    h160 = hashlib.new('ripemd160', sha).digest()
    versioned = b'\x00' + h160
    checksum = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()[:4]

    # Base58 encode
    alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    data = versioned + checksum
    leading_zeros = len(data) - len(data.lstrip(b'\x00'))
    num = int.from_bytes(data, 'big')
    result = ''
    while num > 0:
        num, remainder = divmod(num, 58)
        result = alphabet[remainder] + result
    return '1' * leading_zeros + result

# Target address for puzzle 71
TARGET = "1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU"

# Known values
k_70 = 970436974005023690481
k = {1: 1, 2: 3, 5: 21}

print("=" * 70)
print("TESTING m[71] CANDIDATES")
print("=" * 70)
print(f"\nTarget address: {TARGET}")

# Generate candidates based on patterns
# For d=2: m[71] in [646957982670015793654, 1040488522909152894795]
# For recent d=2 cases: m[n]/2^n ≈ 0.23-0.46

two_71 = 2**71

# Test a range around the expected m[71]/2^71 ratio
print("\n### Testing d=2 candidates ###\n")

# Sample specific values based on patterns
# m[70] = 268234543517713141517 with d=2
# m[67] = 35869814695994276026 with d=2 (has 17 factor)

# Try m[71] = m[70] * growth_factor
growth_factors = [2.5, 3.0, 3.5, 4.0, 7.0, 7.5, 8.0]
for gf in growth_factors:
    m_71 = int(268234543517713141517 * gf)
    # Check if divisible by 3 (required for d=2)
    base = 2 * k_70 + two_71
    numerator = base - m_71 * 3

    if 2**70 <= numerator < 2**71:
        k_71 = numerator
        addr = privkey_to_address(k_71)
        match = "✓ MATCH!" if addr == TARGET else ""
        print(f"gf={gf}: m[71]={m_71}, k[71]={k_71}")
        print(f"  Address: {addr} {match}")
        if addr == TARGET:
            print(f"\n*** FOUND! k[71] = {k_71} ***")
            print(f"*** Hex: {hex(k_71)} ***")

# Also try based on the 19 factor (e-network) since m[69] = 19 × ...
print("\n### Testing 19-network candidates ###\n")
# m[69] = 19 × 1836636217706671242
# Try m[71] = 19 × (larger value)

for multiplier in [44000000000000000000, 45000000000000000000, 46000000000000000000,
                   47000000000000000000, 48000000000000000000, 49000000000000000000,
                   50000000000000000000, 51000000000000000000, 52000000000000000000]:
    m_71 = 19 * multiplier
    for d_val in [1, 2, 5]:
        k_d = k[d_val]
        base = 2 * k_70 + two_71
        numerator = base - m_71 * k_d

        if 2**70 <= numerator < 2**71:
            k_71 = numerator
            addr = privkey_to_address(k_71)
            match = "✓ MATCH!" if addr == TARGET else ""
            if match or d_val == 2:  # Show d=2 cases or matches
                print(f"m[71]=19×{multiplier}={m_71}, d={d_val}")
                print(f"  k[71]={k_71}, Address: {addr[:20]}... {match}")
                if addr == TARGET:
                    print(f"\n*** FOUND! k[71] = {k_71} ***")
