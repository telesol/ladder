#!/usr/bin/env python3
"""
Test k[71] candidates - Version 2
Properly compute k[71] from recurrence and verify against target address.
"""
import json
import hashlib

# Known k values from database
K = {
    1: 1,
    2: 3,
    5: 21,
    70: 970436974005023690481
}

# Load m and d sequences
with open('data_for_csolver.json', 'r') as f:
    data = json.load(f)

m_seq = data['m_seq']
d_seq = data['d_seq']

# secp256k1 parameters
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
G = (0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
     0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8)

def modinv(a, m):
    if a < 0:
        a = a % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError("No modular inverse")
    return x % m

def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    g, x, y = extended_gcd(b % a, a)
    return g, y - (b // a) * x, x

def point_add(p1, p2):
    if p1 is None:
        return p2
    if p2 is None:
        return p1
    x1, y1 = p1
    x2, y2 = p2
    if x1 == x2:
        if y1 != y2:
            return None
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

def privkey_to_address(privkey, compressed=True):
    pubkey = scalar_mult(privkey, G)
    x, y = pubkey
    if compressed:
        prefix = b'\x02' if y % 2 == 0 else b'\x03'
        pubkey_bytes = prefix + x.to_bytes(32, 'big')
    else:
        pubkey_bytes = b'\x04' + x.to_bytes(32, 'big') + y.to_bytes(32, 'big')
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

# Target address for puzzle 71
TARGET = "1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU"

print("=" * 70)
print("K[71] CANDIDATE TESTING - VERSION 2")
print("=" * 70)
print(f"Target address: {TARGET}")
print(f"k[70] = {K[70]}")
print()

def gen_fib(a, b, n):
    """Generate generalized Fibonacci sequence."""
    seq = [a, b]
    for _ in range(n):
        seq.append(seq[-1] + seq[-2])
    return seq

# Q values: Q[62] = 11305495059954, Q[68] = 158716637238095
# Ratio: 14.04, so Q grows roughly exponentially
# Try a range of Q values

print("### Testing with Q search ###")
print()

# Key insight: k[71] = 2*k[70] + 2^71 - m[71]*k[d]
# 2^71 = 2361183241434822606848
# 2*k[70] = 1940873948010047380962

base = 2 * K[70] + 2**71
print(f"Base = 2*k[70] + 2^71 = {base}")
print()

# Valid k[71] range: [2^70, 2^71-1]
min_k71 = 2**70
max_k71 = 2**71 - 1

# For k[71] to be valid:
# min_k71 <= base - m[71]*k[d] <= max_k71
# => base - max_k71 <= m[71]*k[d] <= base - min_k71
# => (base - max_k71)/k[d] <= m[71] <= (base - min_k71)/k[d]

for d in [1, 2, 5]:
    kd = K[d]
    m71_min = (base - max_k71) // kd
    m71_max = (base - min_k71) // kd
    print(f"d={d}: k[d]={kd}, m[71] range: [{m71_min}, {m71_max}]")

print()

# The m[71] should be around 5-6 × 10^21 based on pattern
# Let me compute what m[71] values give valid k[71]

print("### Sample m[71] values and resulting k[71] ###")
print()

# Try a few sample (a, b) pairs and Q values
candidates_ab = [
    (57, 70), (57, 81), (46, 70), (46, 81), (68, 70), (68, 81),
    (57, 76),  # DeepSeek linear prediction
]

Q_estimates = [
    594687606650579,  # Log-linear extrapolation
    600000000000000,
    550000000000000,
    500000000000000,
    700000000000000,
    800000000000000,
]

for d in [1, 2]:
    kd = K[d]
    print(f"### d = {d}, k[d] = {kd} ###")
    
    for a, b in candidates_ab[:3]:  # First 3 candidates
        seq = gen_fib(a, b, 10)
        G8, G9 = seq[8], seq[9]
        
        for Q in Q_estimates[:3]:  # First 3 Q values
            m71 = G8 * G9 * Q
            k71 = base - m71 * kd
            
            if min_k71 <= k71 <= max_k71:
                addr = privkey_to_address(k71)
                match = "✓ MATCH!" if addr == TARGET else ""
                print(f"  ({a},{b}) Q={Q:.2e}: m71={m71:.2e}, k71={k71}, addr={addr[:15]}... {match}")
                
                if addr == TARGET:
                    print()
                    print("=" * 70)
                    print("!!! SOLUTION FOUND !!!")
                    print("=" * 70)
                    print(f"k[71] = {k71}")
                    print(f"k[71] hex = {hex(k71)}")
                    print(f"d = {d}")
                    print(f"(a, b) = ({a}, {b})")
                    print(f"Q = {Q}")
                    print(f"m[71] = {m71}")
                    print(f"Address: {addr}")
                    print("=" * 70)
    print()

# Alternative approach: brute force m[71] that gives correct address
print("### Brute force search for m[71] ###")
print("Searching for m[71] that produces target address...")
print()

# For d=1 (most common for high n)
d = 1
kd = K[d]

# m[71] should be in valid range
m71_min = (base - max_k71) // kd
m71_max = (base - min_k71) // kd

print(f"Search range for m[71] with d={d}: [{m71_min}, {m71_max}]")
print(f"Range size: {m71_max - m71_min}")
print()

# This range is too large to brute force directly
# But we can check if there's a pattern in m[n] values
print("### m[n] pattern for recent n ###")
for n in range(65, 71):
    m = m_seq[n-2]
    print(f"m[{n}] = {m}")

print()
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print("Need to find the exact Q value or m[71] formula")
print("The generalized Fibonacci pattern gives candidates but Q is uncertain")
