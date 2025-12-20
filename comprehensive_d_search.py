#!/usr/bin/env python3
"""
Comprehensive search across all possible d values.
Uses the main recurrence: k[71] = 2*k[70] + 2^71 - m[71]*k[d[71]]
"""

import json
import hashlib
import time

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
base = 2*k_70 + 2**71

print("=" * 80)
print("COMPREHENSIVE D-VALUE SEARCH")
print("=" * 80)
print(f"Target: {TARGET}")
print(f"Base = 2*k[70] + 2^71 = {base:.6e}")

k71_min = 2**70
k71_max = 2**71 - 1

# Possible d values and their k[d]
d_values = [
    (1, 1),
    (2, 3),
    (3, 7),
    (4, 8),
    (5, 21),
    (6, 49),
    (7, 76),
    (8, 224),
]

best_match = 0
best_k71 = None
best_d = None

for d, k_d in d_values:
    # Calculate m[71] range
    m_max = (base - k71_min) // k_d
    m_min = (base - k71_max) // k_d + 1

    if m_min > m_max or m_min < 0:
        print(f"\nd={d}: No valid m[71] range")
        continue

    m_range = m_max - m_min
    print(f"\nd={d}, k[d]={k_d}: m[71] in [{m_min:.4e}, {m_max:.4e}], range={m_range:.4e}")

    # Determine step size for this range
    samples = min(100000, m_range)
    step = max(1, m_range // samples)

    start_time = time.time()
    count = 0
    local_best_match = 0

    for m_71 in range(m_min, m_max + 1, step):
        k_71 = base - m_71 * k_d

        if not (k71_min <= k_71 <= k71_max):
            continue

        addr = privkey_to_address(k_71)

        if addr == TARGET:
            print(f"\n*** EXACT MATCH FOUND! ***")
            print(f"d[71] = {d}")
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

        if match_len > local_best_match:
            local_best_match = match_len
            if match_len >= 3:
                print(f"  {match_len}-char: m={m_71:.6e}, addr={addr[:match_len+4]}...")

        if match_len > best_match:
            best_match = match_len
            best_k71 = k_71
            best_d = d

        count += 1

    elapsed = time.time() - start_time
    print(f"  Tested {count} samples in {elapsed:.1f}s, best local: {local_best_match} chars")

# Dense search around best match
if best_k71 and best_match >= 3:
    print("\n" + "=" * 80)
    print(f"DENSE SEARCH AROUND BEST MATCH (d={best_d}, {best_match} chars)")
    print("=" * 80)

    k_d = k[best_d]

    for fine_step in [10**13, 10**12, 10**11, 10**10]:
        print(f"\nStep size: {fine_step:.0e}")

        # Convert k[71] to m[71]
        best_m = (base - best_k71) // k_d

        for offset in range(-1000, 1001):
            m_71 = best_m + offset * (fine_step // k_d + 1)
            k_71 = base - m_71 * k_d

            if not (k71_min <= k_71 <= k71_max):
                continue

            addr = privkey_to_address(k_71)

            if addr == TARGET:
                print(f"\n*** EXACT MATCH FOUND! ***")
                print(f"d[71] = {best_d}")
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
                best_k71 = k_71
                print(f"  {match_len}-char: {addr[:match_len+4]}...")

print("\n" + "=" * 80)
print(f"Search complete. Best match: {best_match} characters")
print("=" * 80)
