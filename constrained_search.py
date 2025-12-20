#!/usr/bin/env python3
"""
Search for k[71] using the k[80] constraint to narrow the search space.
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
k_68 = k[68]
k_80 = int('ea1a5c66dcc11b5ad180', 16)
constraint_80 = k_80 - 6561*k_68

print("=" * 80)
print("CONSTRAINED SEARCH USING K[80] BRIDGE")
print("=" * 80)
print(f"Target: {TARGET}")
print(f"Constraint: 729*off[71] + 81*off[74] + 9*off[77] + off[80] = {constraint_80}")

k71_min = 2**70
k71_max = 2**71 - 1

# Test different growth rate assumptions
print("\n### Testing different growth rate models ###")

best_match = 0
best_k71 = None

for r in [1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]:
    coef = 729 + 81*r + 9*(r**2) + (r**3)
    offset_71_center = constraint_80 / coef
    k_71_center = 9*k_68 + int(offset_71_center)

    print(f"\nGrowth rate r={r}: k[71] center = {k_71_center:.6e}")

    # Search around this center
    step = 10**17
    for delta in range(-50, 51):
        k_71 = k_71_center + delta * step
        if k71_min <= k_71 <= k71_max:
            addr = privkey_to_address(k_71)
            if addr == TARGET:
                print(f"\n*** EXACT MATCH FOUND! ***")
                print(f"k[71] = {k_71}")
                print(f"r = {r}")
                print(f"offset[71] = {k_71 - 9*k_68}")
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
                print(f"  {match_len}-char match: {addr[:match_len+5]}... at r={r}, delta={delta}")

# Fine search around best match
if best_k71 and best_match >= 3:
    print(f"\n### Fine search around best match ({best_match} chars) ###")

    for fine_step in [10**16, 10**15, 10**14]:
        print(f"\nStep size: {fine_step:.0e}")
        for delta in range(-100, 101):
            k_71 = best_k71 + delta * fine_step
            if k71_min <= k_71 <= k71_max:
                addr = privkey_to_address(k_71)
                if addr == TARGET:
                    print(f"\n*** EXACT MATCH FOUND! ***")
                    print(f"k[71] = {k_71}")
                    print(f"offset[71] = {k_71 - 9*k_68}")
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
                    print(f"  {match_len}-char match: {addr[:match_len+5]}...")

# Also try the exact interpolation between different r values
print("\n### Interpolating between r values ###")

for r in [x / 10.0 for x in range(15, 85, 5)]:
    coef = 729 + 81*r + 9*(r**2) + (r**3)
    offset_71 = constraint_80 / coef
    k_71 = 9*k_68 + int(offset_71)

    if k71_min <= k_71 <= k71_max:
        addr = privkey_to_address(k_71)
        if addr == TARGET:
            print(f"\n*** EXACT MATCH FOUND! ***")
            print(f"k[71] = {k_71}")
            print(f"r = {r}")
            print(f"Hex: {hex(k_71)}")
            exit(0)

        match_len = 0
        for j in range(min(len(addr), len(TARGET))):
            if addr[j] == TARGET[j]:
                match_len += 1
            else:
                break

        if match_len >= 4:
            print(f"  r={r}: {match_len}-char match: {addr[:match_len+3]}...")

print("\n" + "=" * 80)
print("Constrained search complete.")
print(f"Best match: {best_match} characters")
print("=" * 80)
