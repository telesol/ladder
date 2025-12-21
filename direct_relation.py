#!/usr/bin/env python3
"""
Find direct relationships between k[69], k[70], k[75], k[80], k[85], k[90]
that might constrain k[71].
"""
import sqlite3
import hashlib

# Load known k values
conn = sqlite3.connect('/home/solo/ladder/db/kh.db')
cur = conn.cursor()
k = {}
for n in range(1, 91):
    cur.execute('SELECT priv_hex FROM keys WHERE puzzle_id = ?', (n,))
    row = cur.fetchone()
    if row:
        k[n] = int(row[0], 16)
conn.close()

print("=" * 70)
print("DIRECT RELATIONSHIP ANALYSIS")
print("=" * 70)
print()

print("### Known Values ###")
for n in [69, 70, 75, 80, 85, 90]:
    print(f"k[{n}] = {k[n]}")

print()
print("### Ratios ###")
print(f"k[80] / k[70] = {k[80] / k[70]:.6f}")
print(f"k[90] / k[80] = {k[90] / k[80]:.6f}")
print(f"k[85] / k[75] = {k[85] / k[75]:.6f}")
print(f"k[75] / k[70] = {k[75] / k[70]:.6f}")
print()

# The 3-step recursion gives us:
# k[n] = 9*k[n-3] + offset[n]
# So k[72] = 9*k[69] + offset[72]
#    k[75] = 9*k[72] + offset[75] = 81*k[69] + 9*offset[72] + offset[75]
# Therefore: offset[72] = (k[75] - 81*k[69] - offset[75]) / 9

# But we don't know offset[72] or offset[75] individually.
# Let S = 9*offset[72] + offset[75] = k[75] - 81*k[69]

S = k[75] - 81*k[69]
print(f"### Bridge Constraint ###")
print(f"S = k[75] - 81*k[69] = {S}")
print(f"S = 9*offset[72] + offset[75]")
print()

# Similarly for k[90] from k[69]:
# k[90] = 9^7 * k[69] + (complex sum of offsets 72, 75, 78, 81, 84, 87, 90)

T = k[90] - (9**7) * k[69]
print(f"T = k[90] - 9^7*k[69] = {T}")
print(f"T = sum of offset terms from 72 to 90")
print()

# Now for the key: k[80] from k[71]
# k[80] = 729*k[71] + 81*offset[74] + 9*offset[77] + offset[80]

# We want to relate k[71] to known quantities.
# k[71] = 2*k[70] + adj[71]

# From the recurrence: k[71] = 9*k[68] + offset[71]
# But wait, we DO have k[68]!

print(f"### Using k[68] ###")
print(f"k[68] = {k[68]}")
print(f"9 * k[68] = {9 * k[68]}")
print()

# k[71] = 9*k[68] + offset[71]
# offset[71] = k[71] - 9*k[68]

# For k[71] in valid range:
min_k71 = 2**70
max_k71 = 2**71 - 1

min_offset71 = min_k71 - 9*k[68]
max_offset71 = max_k71 - 9*k[68]

print(f"k[71] range: [{min_k71:.4e}, {max_k71:.4e}]")
print(f"offset[71] range: [{min_offset71:.4e}, {max_offset71:.4e}]")
print()

# Compare to known offset pattern
off68 = k[68] - 9*k[65]
off69 = k[69] - 9*k[66]
off70 = k[70] - 9*k[67]

print(f"### Known Offsets ###")
print(f"offset[68] = {off68}")
print(f"offset[69] = {off69}")
print(f"offset[70] = {off70}")
print()

# Offset growth
print(f"### Offset Growth ###")
print(f"offset[69]/offset[68] = {off69/off68:.4f}")
print(f"offset[70]/offset[69] = {off70/off69:.4f}")
print()

# If we continue with same growth:
growth = off70 / off69
off71_est = off70 * growth
k71_est = 9*k[68] + off71_est

print(f"### Extrapolated k[71] ###")
print(f"Estimated offset[71] = {off71_est:.4e}")
print(f"Estimated k[71] = {k71_est:.4e}")
print(f"In valid range: {min_k71 <= k71_est <= max_k71}")
print()

# But wait - we also have k[74] constraint from k[80]!
# k[74] = 9*k[71] + offset[74]
# k[77] = 9*k[74] + offset[77]
# k[80] = 9*k[77] + offset[80]
# So k[80] = 729*k[71] + 81*offset[74] + 9*offset[77] + offset[80]

# If offsets continue growing at same rate:
off74_est = off71_est * growth**3
off77_est = off74_est * growth**3
off80_est = off77_est * growth**3

offset_sum_80 = 81*off74_est + 9*off77_est + off80_est
k71_from_80 = (k[80] - offset_sum_80) / 729

print(f"### k[71] from k[80] Bridge ###")
print(f"With growth factor {growth:.4f}:")
print(f"  offset[74] = {off74_est:.4e}")
print(f"  offset[77] = {off77_est:.4e}")
print(f"  offset[80] = {off80_est:.4e}")
print(f"  k[71] from k[80] = {k71_from_80:.4e}")
print(f"  In valid range: {min_k71 <= k71_from_80 <= max_k71}")
print()

# Now verify consistency between both estimates
print(f"### Consistency Check ###")
print(f"k[71] from k[68] + offset = {k71_est:.4e}")
print(f"k[71] from k[80] bridge   = {k71_from_80:.4e}")
print(f"Difference = {abs(k71_est - k71_from_80):.4e}")
print()

# The two estimates should match if our growth assumption is correct!
# The discrepancy tells us the growth is wrong.

# Let's find the growth that makes them consistent
print(f"### Finding Consistent Growth ###")

def compute_k71_pair(g):
    off71 = off70 * g
    k71_from_68 = 9*k[68] + off71
    
    off74 = off71 * g**3
    off77 = off74 * g**3
    off80 = off77 * g**3
    offset_sum = 81*off74 + 9*off77 + off80
    k71_from_80 = (k[80] - offset_sum) / 729
    
    return k71_from_68, k71_from_80

best_g = None
best_diff = float('inf')

for g_int in range(100, 300):
    g = g_int / 100.0
    k71_a, k71_b = compute_k71_pair(g)
    diff = abs(k71_a - k71_b)
    if diff < best_diff:
        best_diff = diff
        best_g = g

# Refine
for g_int in range(int(best_g*1000) - 100, int(best_g*1000) + 100):
    g = g_int / 1000.0
    k71_a, k71_b = compute_k71_pair(g)
    diff = abs(k71_a - k71_b)
    if diff < best_diff:
        best_diff = diff
        best_g = g

print(f"Best growth for consistency: {best_g:.4f}")
k71_a, k71_b = compute_k71_pair(best_g)
print(f"k[71] from k[68]: {k71_a:.4e}")
print(f"k[71] from k[80]: {k71_b:.4e}")
print(f"Difference: {best_diff:.4e}")
print(f"In valid range: {min_k71 <= k71_a <= max_k71}")
print()

# Generate address for the consistent k[71]
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

def scalar_mult(kk, point):
    result = None
    addend = point
    while kk:
        if kk & 1: result = point_add(result, addend)
        addend = point_add(addend, addend)
        kk >>= 1
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

if min_k71 <= k71_a <= max_k71:
    k71_int = int(k71_a)
    addr = privkey_to_address(k71_int)
    print(f"### Address Check ###")
    print(f"k[71] = {k71_int}")
    print(f"k[71] hex = {hex(k71_int)}")
    print(f"Address: {addr}")
    print(f"Target:  {TARGET}")
    print(f"Match: {'YES!!!' if addr == TARGET else 'No'}")
else:
    print("k[71] out of valid range, skipping address generation")

print()
print("=" * 70)
