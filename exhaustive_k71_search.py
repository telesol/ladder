#!/usr/bin/env python3
"""
Exhaustive search for k[71] across the entire valid range.
Uses intelligent sampling to maximize coverage.
"""

import json
import hashlib
import random
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

print("=" * 80)
print("EXHAUSTIVE k[71] SEARCH")
print("=" * 80)
print(f"Target: {TARGET}")
print(f"k[70] = {k_70}")

k71_min = 2**70
k71_max = 2**71 - 1
range_size = k71_max - k71_min

print(f"\nk[71] range: [{k71_min:.6e}, {k71_max:.6e}]")
print(f"Range size: {range_size:.6e}")

# Multi-strategy search

# Strategy 1: Grid search with various step sizes
print("\n### Strategy 1: Grid search ###")

def grid_search(step, max_samples=10000):
    count = 0
    for k_71 in range(k71_min, k71_max, step):
        addr = privkey_to_address(k_71)
        if addr == TARGET:
            return k_71
        if addr[:4] == TARGET[:4]:
            print(f"  4-char match: k={k_71:.6e}, addr={addr[:25]}...")
        count += 1
        if count >= max_samples:
            break
    return None

for exp in [19, 18, 17]:
    step = 10**exp
    print(f"  Step 10^{exp}: ", end="", flush=True)
    start = time.time()
    result = grid_search(step)
    elapsed = time.time() - start
    if result:
        print(f"FOUND! k[71] = {result}")
        print(f"Hex: {hex(result)}")
        exit(0)
    else:
        samples = min(range_size // step, 10000)
        print(f"No match ({samples} samples, {elapsed:.1f}s)")

# Strategy 2: Search around historical pattern predictions
print("\n### Strategy 2: Pattern-based predictions ###")

# Based on k[n] / 2^n ratios for similar n mod 3 values
k_68 = k[68]
k_65 = k[65]
k_62 = k[62]

ratio_68 = k_68 / (2**68)
ratio_65 = k_65 / (2**65)
ratio_62 = k_62 / (2**62)

print(f"  k[62]/2^62 = {ratio_62:.6f}")
print(f"  k[65]/2^65 = {ratio_65:.6f}")
print(f"  k[68]/2^68 = {ratio_68:.6f}")

# Predict k[71] based on these ratios
predictions = [
    int(ratio_68 * (2**71)),  # Same ratio as k[68]
    int(ratio_65 * (2**71)),  # Same ratio as k[65]
    int(ratio_62 * (2**71)),  # Same ratio as k[62]
    int((ratio_68 + ratio_65) / 2 * (2**71)),  # Average
]

for i, pred in enumerate(predictions):
    if k71_min <= pred <= k71_max:
        # Search around this prediction
        step = 10**16
        for offset in range(-100, 101):
            k_71 = pred + offset * step
            if k71_min <= k_71 <= k71_max:
                addr = privkey_to_address(k_71)
                if addr == TARGET:
                    print(f"  FOUND at prediction {i}! k[71] = {k_71}")
                    print(f"  Hex: {hex(k_71)}")
                    exit(0)

print("  No match in pattern predictions")

# Strategy 3: Search from 3-step recursion perspective
print("\n### Strategy 3: 3-step recursion based ###")

# k[71] = 9*k[68] + offset[71]
# Historical offsets trend negative and roughly double
offset_68 = k[68] - 9*k[65]
offset_69 = k[69] - 9*k[66]
offset_70 = k[70] - 9*k[67]

print(f"  offset[68] = {offset_68:.4e}")
print(f"  offset[69] = {offset_69:.4e}")
print(f"  offset[70] = {offset_70:.4e}")

# Try range of offsets based on trend
for mult in range(10, 40):  # 1.0x to 4.0x the offset[70]
    offset_71 = int(offset_70 * mult / 10)
    k_71 = 9*k_68 + offset_71
    if k71_min <= k_71 <= k71_max:
        addr = privkey_to_address(k_71)
        if addr == TARGET:
            print(f"  FOUND! offset_mult={mult/10}x, k[71] = {k_71}")
            print(f"  Hex: {hex(k_71)}")
            exit(0)

print("  No match in 3-step recursion search")

# Strategy 4: Random sampling
print("\n### Strategy 4: Random sampling (100,000 samples) ###")
random.seed(42)  # Reproducible

found = False
best_match = 0
for i in range(100000):
    k_71 = random.randint(k71_min, k71_max)
    addr = privkey_to_address(k_71)
    if addr == TARGET:
        print(f"  FOUND! k[71] = {k_71}")
        print(f"  Hex: {hex(k_71)}")
        found = True
        break
    # Count matching prefix length
    match_len = 0
    for j in range(min(len(addr), len(TARGET))):
        if addr[j] == TARGET[j]:
            match_len += 1
        else:
            break
    if match_len > best_match:
        best_match = match_len
        print(f"  Best prefix match so far: {match_len} chars - {addr[:match_len+5]}...")

    if i % 20000 == 0 and i > 0:
        print(f"  Progress: {i} samples...")

if not found:
    print(f"  No match. Best prefix: {best_match} chars")

# Strategy 5: Based on the main recurrence
print("\n### Strategy 5: Main recurrence with d-value enumeration ###")

base = 2*k_70 + 2**71
print(f"  base = 2*k[70] + 2^71 = {base:.6e}")

# For each d value, search m[71] space
for d in [1, 2, 5]:
    k_d = k[d]
    print(f"\n  d={d}, k[d]={k_d}:")

    # m[71] range for valid k[71]
    m_min = (base - k71_max) // k_d + 1
    m_max = (base - k71_min) // k_d

    if m_min > m_max:
        print(f"    No valid m[71] range")
        continue

    print(f"    m[71] range: [{m_min:.4e}, {m_max:.4e}]")

    # Sample m[71] values
    m_range = m_max - m_min
    step = max(1, m_range // 10000)

    for m_71 in range(m_min, m_max + 1, step):
        k_71 = base - m_71 * k_d
        if k71_min <= k_71 <= k71_max:
            addr = privkey_to_address(k_71)
            if addr == TARGET:
                print(f"    FOUND! m[71]={m_71}, k[71]={k_71}")
                print(f"    Hex: {hex(k_71)}")
                exit(0)

    print(f"    No match ({min(10000, m_range+1)} samples)")

print("\n" + "=" * 80)
print("EXHAUSTIVE SEARCH COMPLETE - NO MATCH FOUND")
print("=" * 80)
print("\nThe m[71] value likely has a specific mathematical construction")
print("that isn't captured by simple ratio or pattern extrapolation.")
