#!/usr/bin/env python3
"""
Refined search using k[80] bridge with growth factors 1.5-1.9
"""
import sqlite3
import hashlib

conn = sqlite3.connect('/home/solo/ladder/db/kh.db')
cur = conn.cursor()
k_values = {}
for n in [68, 69, 70, 80]:
    cur.execute('SELECT priv_hex FROM keys WHERE puzzle_id = ?', (n,))
    row = cur.fetchone()
    if row:
        k_values[n] = int(row[0], 16)
conn.close()

k80 = k_values[80]
off70 = -223475518416452616237

min_k71 = 2**70
max_k71 = 2**71 - 1

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
print("REFINED K[80] BRIDGE SEARCH")
print("=" * 70)
print(f"Target: {TARGET}")
print()

# Fine-grained search
print("Testing growth factors 1.50 to 1.99 in 0.01 steps...")
print()

best_matches = []
for growth_pct in range(150, 200):
    growth = growth_pct / 100.0
    
    off71 = off70 * growth
    off74 = off71 * growth**3
    off77 = off71 * growth**6
    off80 = off71 * growth**9
    
    offset_sum = 81*off74 + 9*off77 + off80
    k71_try = (k80 - offset_sum) / 729
    
    if min_k71 <= k71_try <= max_k71:
        k71_int = int(k71_try)
        addr = privkey_to_address(k71_int)
        
        if addr == TARGET:
            print()
            print("=" * 70)
            print("!!! SOLUTION FOUND !!!")
            print(f"Growth factor: {growth}")
            print(f"k[71] = {k71_int}")
            print(f"k[71] hex = {hex(k71_int)}")
            print(f"Address: {addr}")
            print("=" * 70)
            break
            
        # Track valid but non-matching
        if growth_pct % 10 == 0:
            print(f"growth={growth}: k71={k71_int:.4e}, addr={addr[:15]}...")

print()
print("No exact match found with uniform growth assumption.")
print()

# The growth might not be uniform. Try varying growth for different intervals
print("### Trying non-uniform growth patterns ###")
print()

# Try: growth 71-74 might be different from 74-77, 77-80
for g1 in [1.4, 1.5, 1.6, 1.7]:
    for g2 in [1.4, 1.5, 1.6, 1.7]:
        for g3 in [1.4, 1.5, 1.6, 1.7]:
            off71 = off70 * g1
            off74 = off71 * g1**2 * g2
            off77 = off74 * g2**2 * g3
            off80 = off77 * g3**2 * g1
            
            offset_sum = 81*off74 + 9*off77 + off80
            k71_try = (k80 - offset_sum) / 729
            
            if min_k71 <= k71_try <= max_k71:
                k71_int = int(k71_try)
                addr = privkey_to_address(k71_int)
                
                if addr == TARGET:
                    print(f"!!! MATCH with g1={g1}, g2={g2}, g3={g3} !!!")
                    print(f"k[71] = {k71_int}")
                    print(f"Address: {addr}")

print("Non-uniform search complete.")
print("=" * 70)
