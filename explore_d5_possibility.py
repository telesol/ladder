#!/usr/bin/env python3
"""
Explore d=5 possibility for n=71.

For n ≡ 2 (mod 3):
- n=62 (mod 9=8): d=2
- n=65 (mod 9=2): d=5
- n=68 (mod 9=5): d=1

n=71 (mod 9=8) -> same as n=62, suggests d=2

But let's also check d=5 since that gave good results for n=65.
"""

import json
import hashlib

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
    result, addend = None, point
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
d_seq = data['d_seq']
k_base = {int(k): v for k, v in data['k_base'].items()}

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

print("=" * 80)
print("EXPLORING d=5 POSSIBILITY FOR n=71")
print("=" * 80)
print(f"Target: {TARGET}")

# For d=5: m[71] must be in [9.24e+19, 1.49e+20]
# k[71] = 2*k[70] + 2^71 - 21*m[71]

base = 2*k_70 + 2**71
k5 = 21  # k[5]

m71_min_d5 = 92422568952859399093
m71_max_d5 = 148641217558450413542

k71_max_d5 = base - 21*m71_min_d5
k71_min_d5 = base - 21*m71_max_d5

print(f"\nFor d=5 (k[5]=21):")
print(f"m[71] range: [{m71_min_d5:.4e}, {m71_max_d5:.4e}]")
print(f"k[71] range: [{k71_min_d5}, {k71_max_d5}]")

# Historical m/2^n ratio for d=5 case (n=65)
m_65 = m_seq[63]
ratio_65 = m_65 / (2**65)
print(f"\nHistorical ratio for d=5 (n=65): m/2^n = {ratio_65:.6f}")

# Predicted m[71] based on this ratio
predicted_m71_d5 = int(ratio_65 * (2**71))
print(f"Predicted m[71] based on same ratio: {predicted_m71_d5:.4e}")

# Check if predicted value is in valid range
if m71_min_d5 <= predicted_m71_d5 <= m71_max_d5:
    print("✓ Predicted value is in valid range!")

    # Test this candidate
    k_71 = base - 21 * predicted_m71_d5
    if 2**70 <= k_71 < 2**71:
        addr = privkey_to_address(k_71)
        print(f"\nTesting predicted m[71] = {predicted_m71_d5}:")
        print(f"k[71] = {k_71}")
        print(f"Address: {addr}")
        if addr == TARGET:
            print("*** MATCH! ***")
else:
    print(f"✗ Predicted value {predicted_m71_d5:.4e} is out of range")

# Search around the predicted value
print("\n### Searching around predicted m[71] for d=5 ###")

step = 10**15  # Fine step
search_range = predicted_m71_d5 // 10

for m_71 in range(max(m71_min_d5, predicted_m71_d5 - search_range),
                  min(m71_max_d5, predicted_m71_d5 + search_range) + step,
                  step):
    k_71 = base - 21 * m_71

    if not (2**70 <= k_71 < 2**71):
        continue

    addr = privkey_to_address(k_71)
    if addr == TARGET:
        print(f"\n*** FOUND! ***")
        print(f"m[71] = {m_71}")
        print(f"k[71] = {k_71}")
        print(f"d[71] = 5")
        print(f"Hex: {hex(k_71)}")
        break

# Also try some specific patterns
print("\n### Testing specific patterns for d=5 ###")

# Try m = constant × 2^k patterns
for const in [1, 2, 3, 5, 7, 9, 11, 13, 17, 19, 21, 23]:
    for exp in range(60, 68):
        m_71 = const * (2**exp)
        if m71_min_d5 <= m_71 <= m71_max_d5:
            k_71 = base - 21 * m_71
            if 2**70 <= k_71 < 2**71:
                addr = privkey_to_address(k_71)
                if addr == TARGET:
                    print(f"\n*** FOUND! m = {const} × 2^{exp} ***")
                    print(f"m[71] = {m_71}")
                    print(f"k[71] = {k_71}")
                    print(f"Hex: {hex(k_71)}")

# Try m[65] × ratio patterns
for ratio in [50, 55, 60, 65, 70, 75]:
    m_71 = m_65 * ratio
    if m71_min_d5 <= m_71 <= m71_max_d5:
        k_71 = base - 21 * m_71
        if 2**70 <= k_71 < 2**71:
            addr = privkey_to_address(k_71)
            if addr == TARGET:
                print(f"\n*** FOUND! m = m[65] × {ratio} ***")
                print(f"m[71] = {m_71}")
                print(f"k[71] = {k_71}")

print("\nSearch completed for d=5.")
