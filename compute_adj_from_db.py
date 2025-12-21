#!/usr/bin/env python3
"""
Compute adj[n] = k[n] - 2*k[n-1] from database k values.
Then analyze patterns to predict adj[71].
"""
import sqlite3
import hashlib

# Get k values from database
conn = sqlite3.connect('/home/solo/ladder/db/kh.db')
cur = conn.cursor()

k_values = {}
for n in range(1, 71):
    cur.execute('SELECT priv_hex FROM keys WHERE puzzle_id = ?', (n,))
    row = cur.fetchone()
    if row:
        k_values[n] = int(row[0], 16)

conn.close()

print("=" * 70)
print("COMPUTING ADJ VALUES FROM DATABASE")
print("=" * 70)
print()

# Compute adj[n] for all available n
adj_values = {}
for n in range(2, 71):
    if n in k_values and (n-1) in k_values:
        adj_values[n] = k_values[n] - 2 * k_values[n-1]

print("### Recent adj values ###")
for n in range(60, 71):
    if n in adj_values:
        adj = adj_values[n]
        sign = "+" if adj >= 0 else ""
        print(f"adj[{n}] = {sign}{adj}, bits={adj.bit_length()}")

print()

# Pattern analysis
print("### Pattern Analysis ###")
adj68 = adj_values[68]
adj69 = adj_values[69]
adj70 = adj_values[70]

print(f"adj[68] = {adj68}")
print(f"adj[69] = {adj69}")
print(f"adj[70] = {adj70}")
print()

print(f"adj[69] - adj[68] = {adj69 - adj68}")
print(f"adj[70] - adj[69] = {adj70 - adj69}")
print()

# Sign pattern analysis
print("### Sign Pattern ###")
signs = []
for n in range(2, 71):
    if n in adj_values:
        sign = "+" if adj_values[n] >= 0 else "-"
        signs.append((n, sign))

# Show recent signs
print("Recent signs:")
for n, sign in signs[-15:]:
    print(f"  n={n}: {sign}")

print()

# Compute adj[71] estimates
print("### ADJ[71] ESTIMATES ###")
k70 = k_values[70]

# Valid ranges
min_k71 = 2**70
max_k71 = 2**71 - 1
adj71_min = min_k71 - 2*k70
adj71_max = max_k71 - 2*k70

print(f"Valid adj[71] range: [{adj71_min}, {adj71_max}]")
print()

# Different estimation methods
estimates = []

# 1. Linear from adj[69], adj[70]
delta = adj70 - adj69
est1 = adj70 + delta
estimates.append(("linear_69_70", est1))

# 2. Linear from adj[68], adj[70]
slope = (adj70 - adj68) / 2
est2 = int(adj70 + slope)
estimates.append(("linear_68_70", est2))

# 3. Geometric (ratio)
if adj69 != 0:
    ratio = adj70 / adj69
    est3 = int(adj70 * ratio)
    estimates.append(("ratio", est3))

# 4. Based on 2^n growth
# adj[n] ~ c * 2^n
c = adj70 / (2**70)
est4 = int(c * 2**71)
estimates.append(("2^n_scale", est4))

# 5. Average of last 3 deltas
if 67 in adj_values and 68 in adj_values:
    d1 = adj68 - adj_values[67]
    d2 = adj69 - adj68
    d3 = adj70 - adj69
    avg_delta = (d1 + d2 + d3) // 3
    est5 = adj70 + avg_delta
    estimates.append(("avg_delta", est5))

# 6. Second difference based
if 67 in adj_values:
    dd1 = (adj69 - adj68) - (adj68 - adj_values[67])
    dd2 = (adj70 - adj69) - (adj69 - adj68)
    d_next = (adj70 - adj69) + dd2  # Assume same second diff
    est6 = adj70 + d_next
    estimates.append(("2nd_diff", est6))

print("Estimation methods:")
for name, est in estimates:
    in_range = adj71_min <= est <= adj71_max
    status = "✓ valid" if in_range else "✗ out of range"
    print(f"  {name}: adj71 = {est} ({status})")

print()

# secp256k1 verification
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

print("### Testing Estimates Against Target Address ###")
for name, est in estimates:
    if adj71_min <= est <= adj71_max:
        k71 = 2*k70 + est
        if min_k71 <= k71 <= max_k71:
            addr = privkey_to_address(k71)
            match = "✓✓✓ MATCH!" if addr == TARGET else ""
            print(f"{name}: k71={k71}, addr={addr[:25]}... {match}")
            if addr == TARGET:
                print()
                print("=" * 70)
                print("!!! SOLUTION FOUND !!!")
                print(f"k[71] = {k71}")
                print(f"k[71] hex = {hex(k71)}")
                print(f"adj[71] = {est}")
                print("=" * 70)

print()
print("=" * 70)
