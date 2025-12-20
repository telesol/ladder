#!/usr/bin/env python3
"""
Test m[71] candidates against the target Bitcoin address.
"""

import json
import hashlib

# secp256k1 parameters
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8

def modinv(a, m):
    if a < 0: a = a % m
    g, x = extended_gcd(a, m)[:2]
    return x % m

def extended_gcd(a, b):
    if a == 0: return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    return gcd, y1 - (b // a) * x1, x1

def point_add(p1, p2):
    if p1 is None: return p2
    if p2 is None: return p1
    x1, y1, x2, y2 = p1[0], p1[1], p2[0], p2[1]
    if x1 == x2 and y1 != y2: return None
    if x1 == x2: m = (3 * x1 * x1) * modinv(2 * y1, P) % P
    else: m = (y2 - y1) * modinv(x2 - x1, P) % P
    x3 = (m * m - x1 - x2) % P
    y3 = (m * (x1 - x3) - y1) % P
    return (x3, y3)

def point_multiply(k, point):
    result = None
    addend = point
    while k:
        if k & 1: result = point_add(result, addend)
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
    alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    data = versioned + checksum
    leading_zeros = len(data) - len(data.lstrip(b'\x00'))
    num = int.from_bytes(data, 'big')
    result = ''
    while num > 0:
        num, remainder = divmod(num, 58)
        result = alphabet[remainder] + result
    return '1' * leading_zeros + result

with open('data_for_csolver.json', 'r') as f:
    data = json.load(f)

m_seq = data['m_seq']
k_base = {int(k): v for k, v in data['k_base'].items()}
d_seq = data['d_seq']

k = k_base.copy()
def get_k(n):
    if n in k: return k[n]
    k_prev = get_k(n - 1)
    m_n = m_seq[n - 2]
    d_n = d_seq[n - 2]
    k_d = get_k(d_n)
    k[n] = 2 * k_prev + (2**n) - m_n * k_d
    return k[n]

for n in range(1, 71):
    get_k(n)

TARGET = "1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU"
k_70 = k[70]
m_68 = m_seq[66]

print("=" * 80)
print("TESTING m[71] CANDIDATES")
print("=" * 80)
print(f"Target: {TARGET}\n")

# Candidates for d=2 (m[71] in [6.47e+20, 1.04e+21])
m71_candidates_d2 = [
    (int(m_68 * 2.0), "m[68] × 2.0"),
    (19 * 2**65, "19 × 2^65"),
    (5 * 2**67, "5 × 2^67"),
    (11 * 2**66, "11 × 2^66"),
    (22 * 2**65, "22 × 2^65"),
    (23 * 2**65, "23 × 2^65"),
    (int(m_68 * 2.5), "m[68] × 2.5"),
    (3 * 2**68, "3 × 2^68"),
    (13 * 2**66, "13 × 2^66"),
    (int(m_68 * 3.0), "m[68] × 3.0"),
    (7 * 2**67, "7 × 2^67"),
    # Additional candidates based on patterns
    (17 * 2**65, "17 × 2^65"),
    (17 * 2**66, "17 × 2^66"),
    (19 * 2**66, "19 × 2^66"),
    (2 * 2**69, "2 × 2^69"),
    (9 * 2**66, "9 × 2^66"),
]

# Also test d=1 candidates (m[71] in [1.94e+21, 3.12e+21])
m71_candidates_d1 = [
    (int(m_68 * 6), "m[68] × 6"),
    (int(m_68 * 7), "m[68] × 7"),
    (int(m_68 * 8), "m[68] × 8"),
    (int(m_68 * 9), "m[68] × 9"),
    (17 * 2**67, "17 × 2^67"),
    (19 * 2**67, "19 × 2^67"),
    (3 * 2**69, "3 × 2^69"),
    (5 * 2**68, "5 × 2^68"),
    (7 * 2**68, "7 × 2^68"),
    (11 * 2**67, "11 × 2^67"),
    (13 * 2**67, "13 × 2^67"),
    (2**71, "2^71"),
]

print("### Testing d=2 candidates ###\n")

for m_71, desc in m71_candidates_d2:
    # k[71] = 2*k[70] + 2^71 - m[71]*k[d[71]] with d=2, k[2]=3
    k_71 = 2*k_70 + 2**71 - m_71 * 3

    if not (2**70 <= k_71 < 2**71):
        continue

    addr = privkey_to_address(k_71)
    match = "✓ MATCH!" if addr == TARGET else ""

    if match or addr[:3] == TARGET[:3]:
        print(f"m={m_71:.4e} ({desc})")
        print(f"  k[71]={k_71}")
        print(f"  addr={addr} {match}")
        if match:
            print(f"\n*** SOLUTION FOUND! ***")
            print(f"k[71] = {k_71}")
            print(f"m[71] = {m_71}")
            print(f"d[71] = 2")
            print(f"Hex: {hex(k_71)}")

print("\n### Testing d=1 candidates ###\n")

for m_71, desc in m71_candidates_d1:
    # k[71] = 2*k[70] + 2^71 - m[71]*k[d[71]] with d=1, k[1]=1
    k_71 = 2*k_70 + 2**71 - m_71

    if not (2**70 <= k_71 < 2**71):
        continue

    addr = privkey_to_address(k_71)
    match = "✓ MATCH!" if addr == TARGET else ""

    if match or addr[:3] == TARGET[:3]:
        print(f"m={m_71:.4e} ({desc})")
        print(f"  k[71]={k_71}")
        print(f"  addr={addr} {match}")
        if match:
            print(f"\n*** SOLUTION FOUND! ***")
            print(f"k[71] = {k_71}")
            print(f"m[71] = {m_71}")
            print(f"d[71] = 1")
            print(f"Hex: {hex(k_71)}")

# More exhaustive search around promising patterns
print("\n### Extended search around 17× and 19× patterns ###\n")

for multiplier in range(15, 25):
    for exp in range(64, 69):
        m_71 = multiplier * (2**exp)

        # Test d=2
        k_71 = 2*k_70 + 2**71 - m_71 * 3
        if 2**70 <= k_71 < 2**71:
            addr = privkey_to_address(k_71)
            if addr == TARGET:
                print(f"*** FOUND d=2: m={multiplier}×2^{exp}, k[71]={k_71} ***")

        # Test d=1
        k_71 = 2*k_70 + 2**71 - m_71
        if 2**70 <= k_71 < 2**71:
            addr = privkey_to_address(k_71)
            if addr == TARGET:
                print(f"*** FOUND d=1: m={multiplier}×2^{exp}, k[71]={k_71} ***")

print("\nNo match found in tested candidates.")
print("\nThe m[71] construction likely involves a more complex formula.")
