#!/usr/bin/env python3
"""
Dense search targeting 4+ character prefix matches.
Uses adaptive sampling to find the exact k[71] value.
"""

import json
import hashlib
import random
import time
import multiprocessing as mp

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

# Load known data
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
print("DENSE PREFIX-BASED SEARCH")
print("=" * 80)
print(f"Target: {TARGET}")

k71_min = 2**70
k71_max = 2**71 - 1

# First pass: find regions with 4+ char matches
print("\n### Phase 1: Finding 4+ character prefix match regions ###")

regions_4char = []
step = 10**17  # Coarse step
count = 0
for k_71 in range(k71_min, k71_max, step):
    addr = privkey_to_address(k_71)
    if addr[:4] == TARGET[:4]:
        regions_4char.append(k_71)
        print(f"  4-char match at k={k_71:.6e}: {addr[:20]}...")
    count += 1
    if count % 500 == 0:
        print(f"  Progress: {count} samples...")

print(f"\nFound {len(regions_4char)} regions with 4-char matches")

# Second pass: densely search around each 4-char match region
if regions_4char:
    print("\n### Phase 2: Dense search around 4-char match regions ###")

    for region_start in regions_4char:
        print(f"\nSearching around {region_start:.6e}")

        # Search with finer steps
        for sub_step in [10**16, 10**15, 10**14]:
            for offset in range(-100, 101):
                k_71 = region_start + offset * sub_step
                if k71_min <= k_71 <= k71_max:
                    addr = privkey_to_address(k_71)
                    if addr == TARGET:
                        print(f"\n*** EXACT MATCH FOUND! ***")
                        print(f"k[71] = {k_71}")
                        print(f"Hex: {hex(k_71)}")
                        exit(0)
                    if addr[:5] == TARGET[:5]:
                        print(f"  5-char: {addr[:20]}... at k+{offset}×{sub_step:.0e}")
                    elif addr[:4] == TARGET[:4]:
                        pass  # Already know 4-char matches

# Also try using the main recurrence formula with different m values
print("\n### Phase 3: Formula-based search with d=2 ###")

base = 2*k_70 + 2**71
k_d2 = 3  # k[2] = 3

# m[71] range for d=2
m_min = (base - k71_max) // k_d2 + 1
m_max = (base - k71_min) // k_d2

print(f"m[71] range for d=2: [{m_min:.6e}, {m_max:.6e}]")

# Dense search through m values
step = 10**14
count = 0
best_match = 0
best_m = None

for m_71 in range(m_min, m_max + 1, step):
    k_71 = base - m_71 * k_d2
    if k71_min <= k_71 <= k71_max:
        addr = privkey_to_address(k_71)
        if addr == TARGET:
            print(f"\n*** EXACT MATCH FOUND! ***")
            print(f"m[71] = {m_71}")
            print(f"k[71] = {k_71}")
            print(f"Hex: {hex(k_71)}")
            exit(0)

        match_len = 0
        for j in range(min(len(addr), len(TARGET))):
            if addr[j] == TARGET[j]:
                match_len += 1
            else:
                break

        if match_len > best_match:
            best_match = match_len
            best_m = m_71
            print(f"  {match_len}-char match: m={m_71:.6e}, addr={addr[:match_len+5]}...")

    count += 1
    if count % 10000 == 0:
        print(f"  Progress: {count} m-values tested...")

if best_m and best_match >= 4:
    print(f"\nBest m[71] region found: {best_m:.6e} ({best_match} chars)")

    # Super-dense search around best m
    print("\n### Phase 4: Super-dense search around best m ###")

    for fine_step in [10**13, 10**12, 10**11, 10**10]:
        print(f"  Searching with step {fine_step:.0e}...")
        for offset in range(-1000, 1001):
            m_71 = best_m + offset * fine_step
            if m_min <= m_71 <= m_max:
                k_71 = base - m_71 * k_d2
                if k71_min <= k_71 <= k71_max:
                    addr = privkey_to_address(k_71)
                    if addr == TARGET:
                        print(f"\n*** EXACT MATCH FOUND! ***")
                        print(f"m[71] = {m_71}")
                        print(f"k[71] = {k_71}")
                        print(f"d[71] = 2")
                        print(f"Hex: {hex(k_71)}")
                        exit(0)

print("\n" + "=" * 80)
print("Search complete. No exact match found.")
print("=" * 80)
