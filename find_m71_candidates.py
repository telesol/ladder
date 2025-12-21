#!/usr/bin/env python3
"""
Find m[71] candidates using various patterns observed in d=1 cases.
"""
import json
import hashlib

K = {1: 1, 2: 3, 5: 21, 70: 970436974005023690481}

with open('data_for_csolver.json', 'r') as f:
    data = json.load(f)

m_seq = data['m_seq']
d_seq = data['d_seq']

# secp256k1 parameters
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
G = (0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
     0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8)

def modinv(a, m):
    if a < 0: a = a % m
    g, x, _ = extended_gcd(a, m)
    if g != 1: raise ValueError("No modular inverse")
    return x % m

def extended_gcd(a, b):
    if a == 0: return b, 0, 1
    g, x, y = extended_gcd(b % a, a)
    return g, y - (b // a) * x, x

def point_add(p1, p2):
    if p1 is None: return p2
    if p2 is None: return p1
    x1, y1 = p1
    x2, y2 = p2
    if x1 == x2:
        if y1 != y2: return None
        lam = (3 * x1 * x1) * modinv(2 * y1, P) % P
    else:
        lam = (y2 - y1) * modinv(x2 - x1, P) % P
    x3 = (lam * lam - x1 - x2) % P
    y3 = (lam * (x1 - x3) - y1) % P
    return (x3, y3)

def scalar_mult(k, point):
    result = None
    addend = point
    while k:
        if k & 1: result = point_add(result, addend)
        addend = point_add(addend, addend)
        k >>= 1
    return result

def privkey_to_address(privkey):
    pubkey = scalar_mult(privkey, G)
    x, y = pubkey
    prefix = b'\x02' if y % 2 == 0 else b'\x03'
    pubkey_bytes = prefix + x.to_bytes(32, 'big')
    sha256 = hashlib.sha256(pubkey_bytes).digest()
    ripemd160 = hashlib.new('ripemd160', sha256).digest()
    versioned = b'\x00' + ripemd160
    checksum = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()[:4]
    alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    n = int.from_bytes(versioned + checksum, 'big')
    result = ''
    while n > 0:
        n, r = divmod(n, 58)
        result = alphabet[r] + result
    return result

TARGET = "1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU"

print("=" * 70)
print("M[71] CANDIDATE SEARCH")
print("=" * 70)
print(f"Target: {TARGET}")
print()

base = 2 * K[70] + 2**71
m71_min = base - (2**71 - 1)
m71_max = base - 2**70

print(f"Valid m[71] range: [{m71_min}, {m71_max}]")
print()

# Pattern 1: m/2^n ≈ 1
print("### Pattern 1: m[71] ≈ c * 2^71 ###")
m70 = m_seq[70-2]
m68 = m_seq[68-2]
for c in [1.0, 1.1, 1.15, 1.2, 0.9, 0.95]:
    m71 = int(c * 2**71)
    if m71_min <= m71 <= m71_max:
        k71 = base - m71
        addr = privkey_to_address(k71)
        match = "✓✓✓ MATCH!" if addr == TARGET else ""
        print(f"c={c}: m71={m71:.4e}, k71={k71}, addr={addr[:20]}... {match}")

print()

# Pattern 2: Growth ratio from d=2 to d=1
print("### Pattern 2: m[71] = growth * m[70] ###")
for growth in [7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0, 10.5, 11.0]:
    m71 = int(growth * m70)
    if m71_min <= m71 <= m71_max:
        k71 = base - m71
        addr = privkey_to_address(k71)
        match = "✓✓✓ MATCH!" if addr == TARGET else ""
        print(f"growth={growth}: m71={m71:.4e}, k71={k71}, addr={addr[:20]}... {match}")

print()

# Pattern 3: Based on m[68] * some factor
print("### Pattern 3: m[71] = factor * m[68] ###")
for factor in [5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0]:
    m71 = int(factor * m68)
    if m71_min <= m71 <= m71_max:
        k71 = base - m71
        addr = privkey_to_address(k71)
        match = "✓✓✓ MATCH!" if addr == TARGET else ""
        print(f"factor={factor}: m71={m71:.4e}, k71={k71}, addr={addr[:20]}... {match}")

print()

# Pattern 4: Linear extrapolation
print("### Pattern 4: Linear extrapolation from recent d=1 cases ###")
# Use m[63] and m[68] to extrapolate
m63 = m_seq[63-2]
slope = (m68 - m63) / (68 - 63)
m71_lin = int(m68 + slope * (71 - 68))
print(f"Linear from m[63], m[68]: slope={slope:.4e}")
if m71_min <= m71_lin <= m71_max:
    k71 = base - m71_lin
    addr = privkey_to_address(k71)
    match = "✓✓✓ MATCH!" if addr == TARGET else ""
    print(f"m71={m71_lin:.4e}, k71={k71}, addr={addr[:20]}... {match}")
else:
    print(f"m71={m71_lin:.4e} OUTSIDE valid range")

print()

# Pattern 5: Log-linear extrapolation
import math
print("### Pattern 5: Log-linear extrapolation ###")
log_m63 = math.log(m63)
log_m68 = math.log(m68)
slope_log = (log_m68 - log_m63) / (68 - 63)
log_m71 = log_m68 + slope_log * (71 - 68)
m71_loglin = int(math.exp(log_m71))
print(f"Log-linear: slope={slope_log:.4f}")
if m71_min <= m71_loglin <= m71_max:
    k71 = base - m71_loglin
    addr = privkey_to_address(k71)
    match = "✓✓✓ MATCH!" if addr == TARGET else ""
    print(f"m71={m71_loglin:.4e}, k71={k71}, addr={addr[:20]}... {match}")
else:
    print(f"m71={m71_loglin:.4e} OUTSIDE valid range")

print()

# Pattern 6: Try m[71] = 2^71 + small adjustment
print("### Pattern 6: m[71] = 2^71 + adj ###")
two_71 = 2**71
for adj_pct in [-10, -5, -2, 0, 2, 5, 10, 15, 20]:
    m71 = int(two_71 * (1 + adj_pct/100))
    if m71_min <= m71 <= m71_max:
        k71 = base - m71
        addr = privkey_to_address(k71)
        match = "✓✓✓ MATCH!" if addr == TARGET else ""
        print(f"adj={adj_pct}%: m71={m71:.4e}, k71={k71}, addr={addr[:20]}... {match}")

print()
print("=" * 70)
