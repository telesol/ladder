#!/usr/bin/env python3
"""
Search for k[71] with constraint k[71] ≡ 2 (mod 3).
Based on pattern: n=62,71,80 all have n mod 9 = 8, and n=62 has d=2.

If d[71] = 2:
- k[71] ≡ 2 (mod 3)
- m[71] = (2*k[70] + 2^71 - k[71]) / 3
- m[71] must be in [6.47e+20, 1.04e+21]
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

with open('data_for_csolver.json', 'r') as f:
    data = json.load(f)

k_base = {int(k): v for k, v in data['k_base'].items()}
m_seq = data['m_seq']
d_seq = data['d_seq']

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

TARGET = "1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU"
k_70 = k[70]

print("=" * 80)
print("SEARCHING k[71] WITH d=2 CONSTRAINT")
print("=" * 80)
print(f"Target: {TARGET}")

# For d=2:
# m[71] = (2*k[70] + 2^71 - k[71]) / 3
# Valid m[71] range: [6.47e+20, 1.04e+21]

base = 2*k_70 + 2**71
print(f"\n2*k[70] + 2^71 = {base}")
print(f"base mod 3 = {base % 3}")

# m[71] range
m71_min = 646957982670015793654
m71_max = 1040488522909152894795

# k[71] = base - 3*m[71]
k71_max = base - 3*m71_min
k71_min = base - 3*m71_max

print(f"\nFor d=2 (k[2]=3):")
print(f"m[71] range: [{m71_min:.4e}, {m71_max:.4e}]")
print(f"k[71] range: [{k71_min}, {k71_max}]")

# Verify k[71] is in valid 71-bit range
print(f"\nValid 71-bit range: [2^70, 2^71) = [{2**70}, {2**71})")
print(f"Computed k[71] range overlaps: [{max(k71_min, 2**70)}, {min(k71_max, 2**71-1)}]")

# Verify k[71] ≡ 2 (mod 3) for these values
test_k = k71_min
print(f"\nk[71]_min mod 3 = {k71_min % 3}")
print(f"k[71]_max mod 3 = {k71_max % 3}")

# Search in this range
print("\n" + "=" * 80)
print("SEARCHING FOR MATCHING ADDRESS")
print("=" * 80)

# The valid range is [k71_min, k71_max] with k[71] ≡ 2 (mod 3)
search_start = k71_min
if search_start % 3 != 2:
    search_start += (2 - search_start % 3) % 3

search_end = k71_max

# Step by 3 to maintain k[71] ≡ 2 (mod 3)
step = 3

# First, sample some values to see the addresses
print("\nSampling addresses in valid range:")

sample_count = 20
sample_step = (search_end - search_start) // sample_count

for i in range(sample_count + 1):
    k_71 = search_start + i * sample_step
    if k_71 % 3 != 2:
        k_71 += (2 - k_71 % 3) % 3
    if k_71 > search_end:
        break

    m_71 = (base - k_71) // 3
    addr = privkey_to_address(k_71)
    match = "✓ MATCH!" if addr == TARGET else ""

    print(f"k[71]={k_71}, m[71]={m_71:.3e}, addr={addr[:25]}... {match}")

    if addr == TARGET:
        print(f"\n*** SOLUTION FOUND! ***")
        print(f"k[71] = {k_71}")
        print(f"m[71] = {m_71}")
        print(f"d[71] = 2")
        print(f"Hex: {hex(k_71)}")
        break

# If no match, also check if d=1 might be correct
print("\n" + "=" * 80)
print("ALSO CHECKING d=1 CASE")
print("=" * 80)

# For d=1: m[71] = 2*k[70] + 2^71 - k[71]
# Valid m[71] range: [1.94e+21, 3.12e+21]

m71_min_d1 = 1940873948010047380963
m71_max_d1 = 3121465568727458684386

k71_max_d1 = base - m71_min_d1
k71_min_d1 = base - m71_max_d1

print(f"\nFor d=1 (k[1]=1):")
print(f"m[71] range: [{m71_min_d1:.4e}, {m71_max_d1:.4e}]")
print(f"k[71] range: [{k71_min_d1}, {k71_max_d1}]")

print("\nSampling addresses:")
sample_step_d1 = (k71_max_d1 - k71_min_d1) // 20

for i in range(21):
    k_71 = k71_min_d1 + i * sample_step_d1
    if k_71 > k71_max_d1:
        break

    m_71 = base - k_71
    addr = privkey_to_address(k_71)
    match = "✓ MATCH!" if addr == TARGET else ""

    print(f"k[71]={k_71}, m[71]={m_71:.3e}, addr={addr[:25]}... {match}")

    if addr == TARGET:
        print(f"\n*** SOLUTION FOUND! ***")
        print(f"k[71] = {k_71}")
        print(f"m[71] = {m_71}")
        print(f"d[71] = 1")
        print(f"Hex: {hex(k_71)}")
        break
