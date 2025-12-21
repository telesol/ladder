#!/usr/bin/env python3
"""
Solve k[71] using the unified formula system discovered by Claude Spark.

Key insight:
- adj[n] = k[n] - 2*k[n-1]
- k[n] = 2*k[n-1] + adj[n]
- For k[71]: k[71] = 2*k[70] + adj[71]

We need to find adj[71] such that k[71] produces target address.

Constraints:
- k[71] ∈ [2^70, 2^71 - 1]
- adj[71] = k[71] - 2*k[70]
- adj[71] ∈ [2^70 - 2*k[70], 2^71 - 1 - 2*k[70]]

Target: 1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU
"""
import hashlib
import sqlite3

# Get k[70] from database
conn = sqlite3.connect('/home/solo/ladder/db/kh.db')
cur = conn.cursor()
cur.execute('SELECT priv_hex FROM keys WHERE puzzle_id = 70')
k70 = int(cur.fetchone()[0], 16)
conn.close()

print("=" * 70)
print("SOLVING K[71] VIA ADJ[71] SEARCH")
print("=" * 70)
print(f"k[70] = {k70}")
print(f"2*k[70] = {2*k70}")
print()

# Valid k[71] range
min_k71 = 2**70
max_k71 = 2**71 - 1

print(f"Valid k[71] range: [{min_k71}, {max_k71}]")
print()

# Valid adj[71] range
adj71_min = min_k71 - 2*k70
adj71_max = max_k71 - 2*k70

print(f"Valid adj[71] range: [{adj71_min}, {adj71_max}]")
print(f"adj[71] range size: {adj71_max - adj71_min}")
print()

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

# Try different adj[71] estimation approaches
print("### Approach 1: Based on adj[70] pattern ###")
import json
with open('data_for_csolver.json') as f:
    data = json.load(f)

adj_seq = data['adj_seq']  # adj[2..70]

# Get recent adj values
print("Recent adj values:")
for n in range(65, 71):
    adj = adj_seq[n-2]
    print(f"  adj[{n}] = {adj}, bits={adj.bit_length()}")

adj70 = adj_seq[70-2]
adj69 = adj_seq[69-2]
adj68 = adj_seq[68-2]

print()
print(f"adj[68] = {adj68}")
print(f"adj[69] = {adj69}")
print(f"adj[70] = {adj70}")
print()

# Pattern analysis
print("### Pattern Analysis ###")
print(f"adj[70]/adj[69] = {adj70/adj69:.4f}")
print(f"adj[69]/adj[68] = {adj69/adj68:.4f}")
print()

# Estimate adj[71] using various patterns
estimates = []

# 1. Linear extrapolation
delta = adj70 - adj69
est1 = adj70 + delta
estimates.append(("linear", est1))

# 2. Ratio-based
ratio = adj70 / adj69
est2 = int(adj70 * ratio)
estimates.append(("ratio", est2))

# 3. Doubling (exponential)
est3 = adj70 * 2
estimates.append(("doubling", est3))

# 4. Based on 2^n scale
# adj[n] ~ c * 2^n for some c
c_est = adj70 / (2**70)
est4 = int(c_est * 2**71)
estimates.append(("2^n_scale", est4))

print("### Estimates for adj[71] ###")
for name, est in estimates:
    if adj71_min <= est <= adj71_max:
        k71 = 2*k70 + est
        if min_k71 <= k71 <= max_k71:
            addr = privkey_to_address(k71)
            match = "✓✓✓ MATCH!" if addr == TARGET else ""
            print(f"{name}: adj71={est}, k71={k71}, addr={addr[:20]}... {match}")
            if addr == TARGET:
                print()
                print("=" * 70)
                print("!!! SOLUTION FOUND !!!")
                print("=" * 70)
                print(f"k[71] = {k71}")
                print(f"k[71] hex = {hex(k71)}")
                print(f"adj[71] = {est}")
                print(f"Address: {addr}")
        else:
            print(f"{name}: adj71={est} gives k71 OUT OF RANGE")
    else:
        print(f"{name}: adj71={est} OUT OF RANGE")

print()

# Try searching around the estimates
print("### Searching near estimates ###")
best_est = estimates[0][1]  # Use linear as starting point

# Search in ±10% of best estimate
search_start = int(best_est * 0.9)
search_end = int(best_est * 1.1)
step = (search_end - search_start) // 1000

print(f"Search range: [{search_start}, {search_end}]")
print(f"Step: {step}")
print()

found = False
for adj71 in range(search_start, search_end, step):
    if adj71_min <= adj71 <= adj71_max:
        k71 = 2*k70 + adj71
        if min_k71 <= k71 <= max_k71:
            addr = privkey_to_address(k71)
            if addr == TARGET:
                print(f"!!! FOUND at adj71={adj71} !!!")
                print(f"k[71] = {k71}")
                print(f"k[71] hex = {hex(k71)}")
                print(f"Address: {addr}")
                found = True
                break

if not found:
    print("No match found in search range.")
    print("The adj[71] pattern may be different from simple extrapolation.")

print()
print("=" * 70)
