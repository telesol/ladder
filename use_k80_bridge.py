#!/usr/bin/env python3
"""
Use k[80] bridge to constrain k[71].

Chain: k[71] → k[74] → k[77] → k[80]
Using 3-step recursion: k[n] = 9*k[n-3] + offset[n]

k[80] = 9*k[77] + offset[80]
k[77] = 9*k[74] + offset[77]
k[74] = 9*k[71] + offset[74]

So: k[80] = 9*(9*(9*k[71] + offset[74]) + offset[77]) + offset[80]
         = 729*k[71] + 81*offset[74] + 9*offset[77] + offset[80]

This gives us a constraint on k[71] if we can estimate the offsets!
"""
import sqlite3
import hashlib

# Get known k values
conn = sqlite3.connect('/home/solo/ladder/db/kh.db')
cur = conn.cursor()
k_values = {}
for n in [68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 85, 90]:
    cur.execute('SELECT priv_hex FROM keys WHERE puzzle_id = ?', (n,))
    row = cur.fetchone()
    if row:
        k_values[n] = int(row[0], 16)
conn.close()

print("=" * 70)
print("K[80] BRIDGE CONSTRAINT ANALYSIS")
print("=" * 70)
print()

print("### Known values ###")
for n in sorted(k_values.keys()):
    print(f"k[{n}] = {k_values[n]}")
print()

k68 = k_values[68]
k80 = k_values[80]

# From the formula:
# k[80] = 729*k[71] + 81*offset[74] + 9*offset[77] + offset[80]
# So: 729*k[71] = k[80] - 81*offset[74] - 9*offset[77] - offset[80]
#     k[71] = (k[80] - 81*offset[74] - 9*offset[77] - offset[80]) / 729

print("### Bridge equation ###")
print("k[80] = 729*k[71] + 81*offset[74] + 9*offset[77] + offset[80]")
print()

# We need to estimate the offsets
# From pattern analysis, offsets grow roughly exponentially
# offset[70] ≈ -2.23×10^20
# If offsets continue to grow by factor ~2 per step...

import math

# Get verified offsets for pattern
offsets_known = {}
for n in range(34, 71):
    if n in k_values and (n-3) in k_values:
        offsets_known[n] = k_values[n] - 9*k_values[n-3]

# Get last known offsets for fitting
off68 = offsets_known.get(68, -55217129595261785870)
off69 = offsets_known.get(69, -119841466032741115730)
off70 = offsets_known.get(70, -223475518416452616237)

# Estimate growth rate
growth_69 = off69 / off68 if off68 != 0 else 2
growth_70 = off70 / off69 if off69 != 0 else 2

print(f"offset[68] = {off68}")
print(f"offset[69] = {off69}")
print(f"offset[70] = {off70}")
print(f"Growth 69/68: {growth_69:.4f}")
print(f"Growth 70/69: {growth_70:.4f}")
print()

# Estimate future offsets assuming ~2x growth
avg_growth = (abs(growth_69) + abs(growth_70)) / 2
print(f"Average growth factor: {avg_growth:.4f}")
print()

# Project offsets
off71_est = off70 * avg_growth
off72_est = off71_est * avg_growth
off73_est = off72_est * avg_growth
off74_est = off73_est * avg_growth
off75_est = off74_est * avg_growth
off76_est = off75_est * avg_growth
off77_est = off76_est * avg_growth
off78_est = off77_est * avg_growth
off79_est = off78_est * avg_growth
off80_est = off79_est * avg_growth

print("Estimated offsets (exponential growth):")
for n, off in [(71, off71_est), (74, off74_est), (77, off77_est), (80, off80_est)]:
    print(f"  offset[{n}] ≈ {off:.4e}")

print()

# Compute k[71] from bridge equation
offset_sum = 81*off74_est + 9*off77_est + off80_est
k71_from_bridge = (k80 - offset_sum) / 729

print(f"### K[71] from bridge ###")
print(f"81*offset[74] + 9*offset[77] + offset[80] = {offset_sum:.4e}")
print(f"k[80] - offset_sum = {k80 - offset_sum:.4e}")
print(f"k[71] = (k[80] - offset_sum) / 729 = {k71_from_bridge:.4e}")
print()

min_k71 = 2**70
max_k71 = 2**71 - 1
print(f"Valid range: [{min_k71:.4e}, {max_k71:.4e}]")
print(f"In range: {min_k71 <= k71_from_bridge <= max_k71}")
print()

# Since the offset estimates are rough, try a range
print("### Testing different offset growth factors ###")

P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
G = (0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
     0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8)

def modinv(a, m):
    if a < 0: a = a % m
    def extended_gcd(a, b):
        if a == 0: return b, 0, 1
        g, x, y = extended_gcd(b % a, a)
        return g, y - (b // a) * x, x
    g, x, _ = extended_gcd(a, m)
    return x % m

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

for growth in [1.5, 1.7, 1.9, 2.0, 2.1, 2.3, 2.5]:
    off71 = off70 * growth
    off74 = off71 * growth**3
    off77 = off71 * growth**6
    off80 = off71 * growth**9
    
    offset_sum = 81*off74 + 9*off77 + off80
    k71_try = (k80 - offset_sum) / 729
    
    if min_k71 <= k71_try <= max_k71:
        k71_int = int(k71_try)
        addr = privkey_to_address(k71_int)
        match = "✓✓✓" if addr == TARGET else ""
        print(f"growth={growth}: k71={k71_int:.4e}, addr={addr[:20]}... {match}")
    else:
        print(f"growth={growth}: k71={k71_try:.4e} OUT OF RANGE")

print()
print("=" * 70)
