#!/usr/bin/env python3
"""
Verify k[71] predictions against target address.
"""
import sqlite3
import hashlib
import math

# Get k values
conn = sqlite3.connect('/home/solo/ladder/db/kh.db')
cur = conn.cursor()
k_values = {}
for n in range(1, 71):
    cur.execute('SELECT priv_hex FROM keys WHERE puzzle_id = ?', (n,))
    row = cur.fetchone()
    if row:
        k_values[n] = int(row[0], 16)
conn.close()

k68 = k_values[68]

# secp256k1
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

print("=" * 70)
print("VERIFYING K[71] PREDICTIONS")
print("=" * 70)
print(f"Target: {TARGET}")
print()

# Prediction 1: Constant d2
offset_71_d2 = -366119286746396287391
k71_d2 = 9*k68 + offset_71_d2
addr_d2 = privkey_to_address(k71_d2)
match_d2 = "✓✓✓ MATCH!" if addr_d2 == TARGET else ""
print(f"Prediction 1 (constant d2):")
print(f"  offset[71] = {offset_71_d2}")
print(f"  k[71] = {k71_d2}")
print(f"  k[71] hex = {hex(k71_d2)}")
print(f"  Address: {addr_d2}")
print(f"  {match_d2}")
print()

# Prediction 2: Exponential fit
offset_71_exp = int(-4.79e20)
k71_exp = 9*k68 + offset_71_exp
addr_exp = privkey_to_address(k71_exp)
match_exp = "✓✓✓ MATCH!" if addr_exp == TARGET else ""
print(f"Prediction 2 (exponential fit):")
print(f"  offset[71] = {offset_71_exp}")
print(f"  k[71] = {k71_exp}")
print(f"  k[71] hex = {hex(k71_exp)}")
print(f"  Address: {addr_exp}")
print(f"  {match_exp}")
print()

# Try variations around the predictions
print("### Searching near predictions ###")
base_offset = offset_71_d2
min_k71 = 2**70
max_k71 = 2**71 - 1

# Search ±1% of the range
search_radius = abs(base_offset) // 100
print(f"Searching offset[71] in range [{base_offset - search_radius}, {base_offset + search_radius}]")
print(f"Search step: {search_radius // 1000}")

found = False
for delta in range(-1000, 1001):
    offset_try = base_offset + delta * (search_radius // 1000)
    k71_try = 9*k68 + offset_try
    if min_k71 <= k71_try <= max_k71:
        addr_try = privkey_to_address(k71_try)
        if addr_try == TARGET:
            print()
            print("=" * 70)
            print("!!! SOLUTION FOUND !!!")
            print("=" * 70)
            print(f"offset[71] = {offset_try}")
            print(f"k[71] = {k71_try}")
            print(f"k[71] hex = {hex(k71_try)}")
            print(f"Address: {addr_try}")
            found = True
            break

if not found:
    print("No match found in search range.")
    print()
    
    # Try a wider search around exponential prediction
    print("### Wider search around exponential prediction ###")
    base2 = offset_71_exp
    for mult in [0.8, 0.9, 1.0, 1.1, 1.2, 0.7, 1.3, 0.6, 1.4, 0.5, 1.5]:
        offset_try = int(base2 * mult)
        k71_try = 9*k68 + offset_try
        if min_k71 <= k71_try <= max_k71:
            addr_try = privkey_to_address(k71_try)
            match = "✓✓✓" if addr_try == TARGET else ""
            print(f"mult={mult}: k71={k71_try:.4e}, addr={addr_try[:20]}... {match}")

print()
print("=" * 70)
