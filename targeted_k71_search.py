#!/usr/bin/env python3
"""
Targeted search for k[71] based on offset trend analysis.

Historical offsets show negative values growing roughly 2x every 3 steps.
offset[68] = -5.52e+19
offset[69] = -1.20e+20
offset[70] = -2.23e+20

Predicted offset[71] ≈ -4.0e+20 to -5.0e+20
"""

import json
import hashlib

# secp256k1 parameters
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
    alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    data = versioned + checksum
    leading_zeros = len(data) - len(data.lstrip(b'\x00'))
    num = int.from_bytes(data, 'big')
    result = ''
    while num > 0:
        num, remainder = divmod(num, 58)
        result = alphabet[remainder] + result
    return '1' * leading_zeros + result

# Load data
with open('data_for_csolver.json', 'r') as f:
    data = json.load(f)

m_seq = data['m_seq']
d_seq = data['d_seq']
k_base = {int(k): v for k, v in data['k_base'].items()}

k = k_base.copy()

def get_k(n):
    if n in k:
        return k[n]
    k_prev = get_k(n - 1)
    m_n = m_seq[n - 2]
    d_n = d_seq[n - 2]
    k_d = get_k(d_n)
    k[n] = 2 * k_prev + (2**n) - m_n * k_d
    return k[n]

for n in range(1, 71):
    get_k(n)

# Target address
TARGET = "1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU"

print("=" * 80)
print("TARGETED k[71] SEARCH")
print("=" * 80)
print(f"Target: {TARGET}")

# Known values
k_68 = k[68]
k_70 = k[70]

# offset[71] = k[71] - 9*k[68]
# Predicted offset range based on trend
offset_71_center = -450000000000000000000  # -4.5e+20
offset_71_range = 100000000000000000000   # ±1e+20

print(f"\nk[68] = {k_68}")
print(f"9*k[68] = {9*k_68}")
print(f"\nSearching offset[71] in range [{offset_71_center - offset_71_range:.2e}, {offset_71_center + offset_71_range:.2e}]")

# For each potential offset[71], compute k[71] and check address
step = 10000000000000000000  # 1e+19 step

best_matches = []

for offset_71 in range(offset_71_center - offset_71_range, offset_71_center + offset_71_range + step, step):
    k_71 = 9*k_68 + offset_71

    # Check if in valid 71-bit range
    if not (2**70 <= k_71 < 2**71):
        continue

    # Compute address
    addr = privkey_to_address(k_71)

    # Check for match
    if addr == TARGET:
        print(f"\n*** FOUND! ***")
        print(f"k[71] = {k_71}")
        print(f"offset[71] = {offset_71}")
        print(f"Address: {addr}")
        print(f"Hex: {hex(k_71)}")
        best_matches.append((k_71, offset_71, addr))
        break

    # Check for partial match (same prefix)
    if addr[:4] == TARGET[:4]:
        print(f"Partial match: offset={offset_71:.2e}, addr={addr[:20]}...")

if not best_matches:
    print("\nNo exact match found in initial range.")
    print("\nLet's try a different approach - testing specific m[71] values")

    # Based on analysis: m[71] ≈ 9e+20 for d=2
    print("\n### Testing d=2 with m[71] around historical ratios ###")

    # For d=2, valid m[71] range is [6.47e+20, 1.04e+21]
    # Historical m/2^n ratio for d=2 (n=62) was 0.257
    # Valid ratio range for d=2 is [0.274, 0.441]

    for ratio in [0.28, 0.30, 0.32, 0.34, 0.36, 0.38, 0.40]:
        m_71 = int(ratio * (2**71))

        # k[71] = 2*k[70] + 2^71 - m[71]*3
        k_71 = 2*k_70 + 2**71 - m_71 * 3

        if 2**70 <= k_71 < 2**71:
            addr = privkey_to_address(k_71)
            match = "✓ MATCH!" if addr == TARGET else ""
            print(f"ratio={ratio:.2f}: m[71]={m_71:.3e}, k[71]={k_71}, addr={addr[:25]}... {match}")

            if addr == TARGET:
                print(f"\n*** SOLUTION FOUND! ***")
                print(f"k[71] = {k_71}")
                print(f"m[71] = {m_71}")
                print(f"d[71] = 2")
                break

    # Also test d=1
    print("\n### Testing d=1 with m[71] around historical ratios ###")

    # For d=1, valid m[71] range is [1.94e+21, 3.12e+21]
    # Historical m/2^n ratio for d=1 (n=68) was 1.154

    for ratio in [0.85, 0.90, 0.95, 1.00, 1.05, 1.10, 1.15, 1.20, 1.25, 1.30]:
        m_71 = int(ratio * (2**71))

        # k[71] = 2*k[70] + 2^71 - m[71]*1
        k_71 = 2*k_70 + 2**71 - m_71

        if 2**70 <= k_71 < 2**71:
            addr = privkey_to_address(k_71)
            match = "✓ MATCH!" if addr == TARGET else ""
            print(f"ratio={ratio:.2f}: m[71]={m_71:.3e}, k[71]={k_71}, addr={addr[:25]}... {match}")

            if addr == TARGET:
                print(f"\n*** SOLUTION FOUND! ***")
                print(f"k[71] = {k_71}")
                print(f"m[71] = {m_71}")
                print(f"d[71] = 1")
                break
