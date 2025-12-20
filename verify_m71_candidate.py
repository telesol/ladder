#!/usr/bin/env python3
"""
Verify any (m[71], d[71]) candidate by computing BTC address.
Usage: python verify_m71_candidate.py <m71> <d71>
"""

import sys
import hashlib

# secp256k1 parameters
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
G = (0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
     0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8)

# Known k-values for d lookup
K_VALUES = {
    1: 1, 2: 3, 3: 7, 4: 8, 5: 21, 6: 49, 7: 76, 8: 224,
    9: 467, 10: 514, 11: 1155, 12: 2683, 13: 5216, 14: 10544,
    15: 26867, 16: 51510, 17: 95823, 18: 198669, 19: 357535, 20: 863317
}

K71_BASE = 4302057189444869987810

TARGET_ADDRESS = "1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU"

def modinv(a, m):
    if a < 0: a = a % m
    g, x, _ = extended_gcd(a, m)
    if g != 1: raise ValueError("No inverse")
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
        if k & 1:
            result = point_add(result, addend)
        addend = point_add(addend, addend)
        k >>= 1
    return result

def privkey_to_address(privkey):
    pub = scalar_mult(privkey, G)
    x, y = pub
    prefix = b'\x02' if y % 2 == 0 else b'\x03'
    pubkey_bytes = prefix + x.to_bytes(32, 'big')
    sha256 = hashlib.sha256(pubkey_bytes).digest()
    ripemd160 = hashlib.new('ripemd160', sha256).digest()
    versioned = bytes([0x00]) + ripemd160
    checksum = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()[:4]
    
    # Base58
    alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    n = int.from_bytes(versioned + checksum, 'big')
    result = ''
    while n > 0:
        n, r = divmod(n, 58)
        result = alphabet[r] + result
    for byte in versioned + checksum:
        if byte == 0: result = '1' + result
        else: break
    return result

def verify_candidate(m71, d71):
    k_d = K_VALUES.get(d71)
    if k_d is None:
        print(f"Unknown k[{d71}]")
        return False
    
    k71 = K71_BASE - m71 * k_d
    
    # Check range
    k71_min = 2**70
    k71_max = 2**71 - 1
    
    if k71 < k71_min or k71 > k71_max:
        print(f"k[71] = {k71:,} OUT OF RANGE [{k71_min:,}, {k71_max:,}]")
        return False
    
    # Compute address
    address = privkey_to_address(k71)
    
    print(f"m[71] = {m71:,}")
    print(f"d[71] = {d71}")
    print(f"k[71] = {k71:,}")
    print(f"k[71] hex = {hex(k71)}")
    print(f"Address = {address}")
    print(f"Target  = {TARGET_ADDRESS}")
    
    if address == TARGET_ADDRESS:
        print("\n🎉 MATCH! PUZZLE 71 SOLVED! 🎉")
        return True
    else:
        print("\n❌ No match")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python verify_m71_candidate.py <m71> <d71>")
        print("Example: python verify_m71_candidate.py 899985170943544151107 2")
        sys.exit(1)
    
    m71 = int(sys.argv[1])
    d71 = int(sys.argv[2])
    verify_candidate(m71, d71)
