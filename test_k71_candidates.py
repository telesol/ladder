#!/usr/bin/env python3
"""
Test k[71] candidates by:
1. Using different d values (1, 2, 5)
2. Using different (a, b) pairs for generalized Fibonacci
3. Computing m[71] from G_8 * G_9 * Q
4. Computing k[71] via recurrence
5. Verifying against target Bitcoin address

Target address: 1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU
"""
import json
import hashlib

# Load known k values
with open('data_for_csolver.json', 'r') as f:
    data = json.load(f)

k_seq = data['k_seq']
m_seq = data['m_seq']
d_seq = data['d_seq']

# Get k[70] (index 70-2 = 68)
k70 = k_seq[68]
print(f"k[70] = {k70}")

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

# Target address
TARGET = "1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU"

print("=" * 70)
print("K[71] CANDIDATE TESTING")
print("=" * 70)
print(f"Target address: {TARGET}")
print(f"k[70] = {k70}")
print()

def gen_fib(a, b, n):
    """Generate generalized Fibonacci sequence."""
    seq = [a, b]
    for _ in range(n):
        seq.append(seq[-1] + seq[-2])
    return seq

# Q values estimated from pattern
Q_pred = 594687606650579  # From log-linear extrapolation

# Candidate (a, b) pairs that satisfy mod 11 constraint
# (a ≡ 2, b ≡ 4 mod 11)
candidates_mod11 = [
    (57, 70), (57, 81), (46, 70), (46, 81), (68, 70), (68, 81),
    (35, 59), (35, 70), (79, 70), (79, 81),
]

# Also try without mod 11 constraint (DeepSeek suggestions)
candidates_linear = [(57, 76)]

all_candidates = candidates_mod11 + candidates_linear

# Try different d values
d_candidates = [1, 2, 5]

print("### Testing candidates ###")
print()

matches = []

for d in d_candidates:
    kd = k_seq[d-2] if d >= 2 else k_seq[d-1]  # Handle index
    
    for a, b in all_candidates:
        seq = gen_fib(a, b, 10)
        G8 = seq[8]
        G9 = seq[9]
        
        # Estimate m[71] = G_8 * G_9 * Q
        m71 = G8 * G9 * Q_pred
        
        # Compute k[71] using recurrence: k[n] = 2*k[n-1] + 2^n - m[n]*k[d[n]]
        k71 = 2 * k70 + 2**71 - m71 * kd
        
        # Check if k[71] is in valid range
        min_val = 2**70
        max_val = 2**71 - 1
        
        if min_val <= k71 <= max_val:
            # Compute address
            addr = privkey_to_address(k71)
            match = addr == TARGET
            
            if match:
                matches.append({
                    'd': d,
                    'a': a,
                    'b': b,
                    'G8': G8,
                    'G9': G9,
                    'm71': m71,
                    'k71': k71,
                    'addr': addr
                })
                print(f"!!! MATCH FOUND !!!")
                print(f"d={d}, (a,b)=({a},{b})")
                print(f"G_8={G8}, G_9={G9}")
                print(f"m[71] = {m71}")
                print(f"k[71] = {k71}")
                print(f"k[71] hex = {hex(k71)}")
                print(f"Address: {addr}")
                print()
        elif k71 > 0:
            # Just log some for debugging
            pass

print(f"\nTotal matches: {len(matches)}")

if not matches:
    print("\nNo exact matches found. Q prediction may be wrong.")
    print("Trying Q values from range...")
    
    # Try a range of Q values near the prediction
    for Q_try in range(Q_pred - 1000, Q_pred + 1000):
        for d in [1, 2]:
            kd = k_seq[d-2] if d >= 2 else k_seq[d-1]
            
            for a, b in [(57, 70), (57, 81), (68, 70), (68, 81)]:
                seq = gen_fib(a, b, 10)
                G8 = seq[8]
                G9 = seq[9]
                
                m71 = G8 * G9 * Q_try
                k71 = 2 * k70 + 2**71 - m71 * kd
                
                min_val = 2**70
                max_val = 2**71 - 1
                
                if min_val <= k71 <= max_val:
                    addr = privkey_to_address(k71)
                    if addr == TARGET:
                        print(f"!!! MATCH at Q={Q_try} !!!")
                        print(f"d={d}, (a,b)=({a},{b}), k[71]={k71}")

print()
print("=" * 70)
