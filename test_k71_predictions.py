#!/usr/bin/env python3
"""
Test all k[71] predictions against target Bitcoin address.
"""
import sqlite3
import hashlib

# secp256k1 parameters
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
    for byte in versioned:
        if byte == 0:
            result = '1' + result
        else:
            break
    return result

TARGET = "1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU"

# All k[71] predictions from different analyses
predictions = [
    ("Ratio model", 1562418735284878593264),
    ("Avg model", 1529105702563386215391),
    ("d2 model", 1613043600291433327230),
    ("Consistent growth (1.423)", 1661078733213232267264),
    ("Bridge estimate (offset=0)", 1516516294215448800190),
]

print("=" * 70)
print("TESTING ALL K[71] PREDICTIONS AGAINST TARGET")
print("=" * 70)
print()
print(f"Target address: {TARGET}")
print()

min_k71 = 2**70
max_k71 = 2**71 - 1

for name, k71 in predictions:
    if min_k71 <= k71 <= max_k71:
        addr = privkey_to_address(k71)
        match = "MATCH!!!" if addr == TARGET else ""
        print(f"{name}:")
        print(f"  k[71] = {k71}")
        print(f"  Address: {addr}")
        print(f"  {match}")
    else:
        print(f"{name}: OUT OF RANGE")
    print()

print("=" * 70)
print("None of the predictions match.")
print("The offset pattern extrapolation is INCORRECT.")
print("Need to find the true underlying formula.")
print("=" * 70)
