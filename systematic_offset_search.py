#!/usr/bin/env python3
"""
Systematic search using the offset constraint from k[80].

Key constraint:
729*offset[71] + 81*offset[74] + 9*offset[77] + offset[80] = -337,232,494,036,332,049,352,369

Historical offset pattern (negative, roughly doubling):
offset[68] = -5.52e+19
offset[69] = -1.20e+20
offset[70] = -2.23e+20

Estimated offset[71] should be around -4e+20 to -5e+20
"""

import json
import hashlib

# EC parameters
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
k_68 = k[68]

# Constraint from k[80]
constraint_80 = -337232494036332049352369

print("=" * 80)
print("SYSTEMATIC OFFSET-BASED SEARCH")
print("=" * 80)
print(f"Target: {TARGET}")
print(f"k[68] = {k_68}")
print(f"9*k[68] = {9*k_68}")
print(f"Constraint: 729*off[71] + 81*off[74] + 9*off[77] + off[80] = {constraint_80}")

# Historical offsets
offsets = {}
for n in range(31, 71):
    offsets[n] = k[n] - 9*k[n-3]

print(f"\nHistorical offsets (last 5):")
for n in range(66, 71):
    print(f"  offset[{n}] = {offsets[n]:.4e}")

# Compute offset ratios
print(f"\nOffset ratios:")
for n in range(67, 71):
    ratio = offsets[n] / offsets[n-1] if offsets[n-1] != 0 else 0
    print(f"  offset[{n}]/offset[{n-1}] = {ratio:.4f}")

# Search strategy: try different offset[71] values based on trend
print("\n" + "=" * 80)
print("SEARCHING AROUND PREDICTED OFFSET[71]")
print("=" * 80)

# Predicted offset[71] based on trend (roughly 2x every step)
predicted_offset_71 = offsets[70] * 2  # Should be around -4.5e+20

print(f"\nPredicted offset[71] ≈ {predicted_offset_71:.4e}")

# Valid k[71] range
k71_min = 2**70
k71_max = 2**71 - 1

# offset[71] = k[71] - 9*k[68]
offset71_min = k71_min - 9*k_68
offset71_max = k71_max - 9*k_68

print(f"Valid offset[71] range: [{offset71_min:.4e}, {offset71_max:.4e}]")

# Search around predicted value
search_center = int(predicted_offset_71)
search_range = abs(search_center) // 2  # ±50%

print(f"\nSearching offset[71] in [{search_center - search_range:.4e}, {search_center + search_range:.4e}]")

# Coarse search first
step = 10**18  # 10^18 step
found = False

for offset_71 in range(search_center - search_range, search_center + search_range + step, step):
    k_71 = 9*k_68 + offset_71

    if not (k71_min <= k_71 < k71_max):
        continue

    addr = privkey_to_address(k_71)

    if addr == TARGET:
        print(f"\n*** FOUND! ***")
        print(f"offset[71] = {offset_71}")
        print(f"k[71] = {k_71}")
        print(f"Hex: {hex(k_71)}")
        found = True
        break

    if addr[:4] == TARGET[:4]:
        print(f"Partial match at offset={offset_71:.4e}: {addr[:20]}...")

if not found:
    print("\nNo match in initial search.")

    # Try the full valid range with wider steps
    print("\nTrying full valid range with 10^19 steps...")

    step = 10**19
    for offset_71 in range(offset71_min, offset71_max + step, step):
        k_71 = 9*k_68 + offset_71

        if not (k71_min <= k_71 < k71_max):
            continue

        addr = privkey_to_address(k_71)

        if addr == TARGET:
            print(f"\n*** FOUND! ***")
            print(f"offset[71] = {offset_71}")
            print(f"k[71] = {k_71}")
            print(f"Hex: {hex(k_71)}")
            found = True
            break

if not found:
    print("\nNo match found.")
    print("\nThe offset[71] is not near the predicted trend value.")
    print("Need deeper analysis of the m-value construction pattern.")
