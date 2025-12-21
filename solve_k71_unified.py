#!/usr/bin/env python3
"""
Solve k[71] using unified formula approach.

Key insight from joint analysis:
  k[71] = 2*k[70] + adj[71]
       = 2*k[70] + 2^71 - m[71]*k[d[71]]

Strategy:
1. For each candidate d ∈ {1, 2, 4} (covers 73% of cases)
2. Compute valid m range that gives k[71] ∈ [2^70, 2^71)
3. Search m values systematically
4. Verify each candidate against target Bitcoin address
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
    return result

# Load known k values from database
conn = sqlite3.connect('/home/solo/ladder/db/kh.db')
cur = conn.cursor()
k_values = {}
for n in range(1, 91):
    cur.execute('SELECT priv_hex FROM keys WHERE puzzle_id = ?', (n,))
    row = cur.fetchone()
    if row:
        k_values[n] = int(row[0], 16)
conn.close()

TARGET = "1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU"

print("=" * 70)
print("UNIFIED FORMULA APPROACH: k[71] = 2*k[70] + 2^71 - m[71]*k[d[71]]")
print("=" * 70)
print()

k70 = k_values[70]
print(f"k[70] = {k70}")
print(f"2*k[70] = {2*k70}")
print(f"2^71 = {2**71}")
print()

# Valid k[71] range
min_k71 = 2**70
max_k71 = 2**71 - 1
print(f"Valid k[71] range: [{min_k71:.4e}, {max_k71:.4e}]")
print()

# For each d value, compute valid m range
# k[71] = 2*k[70] + 2^71 - m*k[d]
# For k[71] >= min_k71:
#   2*k[70] + 2^71 - m*k[d] >= min_k71
#   m*k[d] <= 2*k[70] + 2^71 - min_k71
#   m <= (2*k[70] + 2^71 - min_k71) / k[d]
#
# For k[71] <= max_k71:
#   2*k[70] + 2^71 - m*k[d] <= max_k71
#   m*k[d] >= 2*k[70] + 2^71 - max_k71
#   m >= (2*k[70] + 2^71 - max_k71) / k[d]

base = 2*k70 + 2**71

print("### Computing valid m ranges for each d ###")
print()

# Most likely d values based on analysis
d_candidates = [1, 2, 4, 3, 5, 7, 8]

for d in d_candidates:
    if d not in k_values:
        continue
    k_d = k_values[d]

    m_min = (base - max_k71) / k_d
    m_max = (base - min_k71) / k_d

    if m_min < 0:
        m_min = 0

    m_min_int = int(m_min)
    m_max_int = int(m_max) + 1

    range_size = m_max_int - m_min_int

    print(f"d={d}: k[{d}]={k_d}, m ∈ [{m_min_int}, {m_max_int}] ({range_size:,} candidates)")

print()
print("=" * 70)
print("SEARCHING d=1 (simplest case: adj[71] = 2^71 - m[71])")
print("=" * 70)
print()

# For d=1, k[1]=1, so: k[71] = 2*k[70] + 2^71 - m
# Valid m range for k[71] in [2^70, 2^71-1]
d = 1
k_d = k_values[d]  # k[1] = 1

m_min = (base - max_k71) // k_d
m_max = (base - min_k71) // k_d

print(f"For d=1: m ∈ [{m_min}, {m_max}]")
print(f"Range size: {m_max - m_min:,}")
print()

# The range is huge. Let's look for patterns in known m values.
# From analysis: m[n] often involves mathematical constants

# Let's check if there's a pattern in m growth
# First compute known m values
print("### Known m values for guidance ###")

m_values = {}
adj_values = {}
d_values = {}

for n in range(2, 71):
    if n in k_values and (n-1) in k_values:
        adj_n = k_values[n] - 2*k_values[n-1]
        adj_values[n] = adj_n

        # Find d[n] - the d that minimizes m[n]
        best_d = None
        best_m = None
        N_n = 2**n - adj_n

        for try_d in range(1, n):
            if try_d in k_values:
                k_d = k_values[try_d]
                if N_n % k_d == 0:
                    m_try = N_n // k_d
                    if best_m is None or m_try < best_m:
                        best_m = m_try
                        best_d = try_d

        if best_m is not None:
            m_values[n] = best_m
            d_values[n] = best_d

# Show m growth pattern for recent values
print("\nRecent m values (n=60-70):")
for n in range(60, 71):
    if n in m_values:
        print(f"  m[{n}] = {m_values[n]:.4e}")

# Estimate m[71] from growth
if 70 in m_values and 69 in m_values:
    growth = m_values[70] / m_values[69]
    m71_est = m_values[70] * growth
    print(f"\nEstimated m[71] (exponential): {m71_est:.4e}")
    print(f"Growth rate m[70]/m[69]: {growth:.4f}")

print()
print("=" * 70)
print("SEARCHING AROUND ESTIMATED m[71]")
print("=" * 70)
print()

# Search around the estimated value with a reasonable range
if 70 in m_values:
    m_center = int(m_values[70] * growth)

    # Search ±50% around center
    search_min = int(m_center * 0.5)
    search_max = int(m_center * 1.5)

    # Clamp to valid range
    search_min = max(search_min, m_min)
    search_max = min(search_max, m_max)

    print(f"Searching m ∈ [{search_min:.4e}, {search_max:.4e}]")
    print(f"Search range: {search_max - search_min:,} values")
    print()

    # This is still a large range. Let's sample it.
    # Try specific values first based on patterns

    # From the analysis, m values sometimes involve:
    # 1. Powers of 2
    # 2. Mathematical constant convergents
    # 3. Self-reference (m[71] | m[71 + m[71]])

    # Let's try a sparse search first
    print("Testing sample values...")

    found = False
    tested = 0

    # Try values at regular intervals
    step = max(1, (search_max - search_min) // 10000)

    for m in range(search_min, search_max + 1, step):
        k71_try = base - m * k_d

        if min_k71 <= k71_try <= max_k71:
            tested += 1
            addr = privkey_to_address(k71_try)

            if addr == TARGET:
                print()
                print("!" * 70)
                print("!!! SOLUTION FOUND !!!")
                print("!" * 70)
                print(f"d = {d}")
                print(f"m[71] = {m}")
                print(f"k[71] = {k71_try}")
                print(f"k[71] hex = {hex(k71_try)}")
                print(f"adj[71] = {2**71 - m}")
                print(f"Address: {addr}")
                print("!" * 70)
                found = True
                break

            if tested % 1000 == 0:
                print(f"  Tested {tested} values, m={m:.4e}, addr prefix: {addr[:8]}...")

    if not found:
        print(f"\nNo match found in sampled search ({tested} values tested)")

print()
print("=" * 70)
print("TRYING d=2 (k[2]=3)")
print("=" * 70)
print()

d = 2
k_d = k_values[d]  # k[2] = 3

m_min = (base - max_k71) // k_d
m_max = (base - min_k71) // k_d

print(f"For d=2: m ∈ [{m_min}, {m_max}]")

# For d=2, we need (2^71 - adj[71]) to be divisible by 3
# Search with step that respects divisibility

# Estimate based on m[70]/3 relationship
if 70 in m_values:
    m_center = int(m_values[70] * growth / 3)  # Rough adjustment for d=2

    search_min = max(int(m_min), int(m_center * 0.5))
    search_max = min(int(m_max), int(m_center * 2.0))

    step = max(1, (search_max - search_min) // 5000)

    tested = 0
    for m in range(search_min, search_max + 1, step):
        # Check divisibility: 2^71 - adj must be divisible by k[d]=3
        # adj = 2^71 - m*3, so 2^71 - adj = m*3 (always divisible)

        k71_try = base - m * k_d

        if min_k71 <= k71_try <= max_k71:
            tested += 1
            addr = privkey_to_address(k71_try)

            if addr == TARGET:
                print()
                print("!" * 70)
                print("!!! SOLUTION FOUND with d=2 !!!")
                print(f"m[71] = {m}")
                print(f"k[71] = {k71_try}")
                print(f"Address: {addr}")
                print("!" * 70)
                break

            if tested % 1000 == 0:
                print(f"  d=2: Tested {tested}, m={m:.4e}...")

print()
print("=" * 70)
print("ADDITIONAL INSIGHT: Use offset bridge constraints")
print("=" * 70)

# From the bridge analysis:
# k[80] = 729*k[71] + 81*offset[74] + 9*offset[77] + offset[80]
# This gives: k[71] = (k[80] - 81*offset[74] - 9*offset[77] - offset[80]) / 729

# If we can estimate the offsets better, we can constrain k[71]
# offset[n] = k[n] - 9*k[n-3]

# From the growth factor analysis, offset growth is ~1.5-1.9
# This constrains k[71] to a narrower range

k80 = k_values[80]
print(f"\nk[80] = {k80}")
print(f"k[80] / 729 = {k80 / 729:.4e}")
print()

# For k[71] to be in valid range with offset sum near 0:
# k[71] ≈ k[80] / 729
k71_bridge_est = k80 / 729
print(f"Bridge estimate (offset sum ≈ 0): k[71] ≈ {k71_bridge_est:.4e}")
print(f"This is in valid range: {min_k71 <= k71_bridge_est <= max_k71}")
print()

# Test around this bridge estimate
print("Testing values around bridge estimate...")

bridge_center = int(k71_bridge_est)
search_radius = int(bridge_center * 0.01)  # ±1% around bridge estimate

found = False
for offset in range(-search_radius, search_radius + 1, max(1, search_radius // 500)):
    k71_try = bridge_center + offset

    if min_k71 <= k71_try <= max_k71:
        addr = privkey_to_address(k71_try)

        if addr == TARGET:
            print()
            print("!" * 70)
            print("!!! SOLUTION FOUND via BRIDGE !!!")
            print(f"k[71] = {k71_try}")
            print(f"k[71] hex = {hex(k71_try)}")
            print(f"Address: {addr}")
            print("!" * 70)
            found = True
            break

if not found:
    print("No match found near bridge estimate")

print()
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print()
print("The unified formula approach requires knowing m[71] or d[71].")
print("Search space for d=1 alone is ~10^21 values - too large for brute force.")
print()
print("Next steps:")
print("1. Find additional constraints on m[71] from m-sequence patterns")
print("2. Use multiple bridge constraints (k[75], k[80], k[85]) together")
print("3. Look for modular constraints that reduce search space")
print("4. Check if m[71] has special form (prime, power of 2, etc.)")
