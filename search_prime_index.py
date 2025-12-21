#!/usr/bin/env python3
"""
Since 71 is PRIME, m[71] might follow the self-index pattern: m[n] = n × Q

From MEMORY.md:
  m[19] = 19 × 29,689
  m[41] = 41 × 22,342,064,035

If m[71] = 71 × Q, we can search for Q values that give valid k[71].
"""
import sqlite3
import hashlib

# Load k values
conn = sqlite3.connect('/home/solo/ladder/db/kh.db')
cur = conn.cursor()
k_values = {}
for n in range(1, 91):
    cur.execute('SELECT priv_hex FROM keys WHERE puzzle_id = ?', (n,))
    row = cur.fetchone()
    if row:
        k_values[n] = int(row[0], 16)
conn.close()

k70 = k_values[70]
BASE = 2*k70 + 2**71

print("=" * 70)
print("PRIME SELF-INDEX PATTERN: m[71] = 71 × Q")
print("=" * 70)
print()

# Verify the pattern for known primes
print("### Verifying self-index pattern for known primes ###")

# Compute m values
adj_values = {}
m_values = {}
d_values = {}

for n in range(2, 71):
    if n in k_values and (n-1) in k_values:
        adj_n = k_values[n] - 2*k_values[n-1]
        adj_values[n] = adj_n
        N_n = 2**n - adj_n
        best_d = None
        best_m = None
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

# Check primes
primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67]
print("Prime n | m[n] | n divides m[n]? | m[n]/n")
print("-"*60)
for p in primes:
    if p in m_values:
        divides = m_values[p] % p == 0
        quotient = m_values[p] // p if divides else "N/A"
        status = "✓" if divides else ""
        print(f"{p:7} | {m_values[p]:20} | {str(divides):15} | {quotient} {status}")

print()
print("### If m[71] = 71 × Q, what are the constraints? ###")
print()

# For d=1: m[71] ∈ [1.94e21, 3.12e21]
# m[71] = 71 × Q => Q ∈ [2.73e19, 4.39e19]

min_k71 = 2**70
max_k71 = 2**71 - 1

print("For d[71] = 1:")
min_adj = min_k71 - 2*k70
max_adj = max_k71 - 2*k70
min_m = 2**71 - max_adj
max_m = 2**71 - min_adj
min_Q = min_m // 71 + 1  # ceiling
max_Q = max_m // 71
print(f"  m[71] ∈ [{min_m:.4e}, {max_m:.4e}]")
print(f"  Q = m[71]/71 ∈ [{min_Q:.4e}, {max_Q:.4e}]")
print(f"  Q range size: {max_Q - min_Q:,}")
print()

# For d=2: m[71] ∈ [6.47e20, 1.04e21]
print("For d[71] = 2:")
min_m_d2 = (2**71 - max_adj) // 3
max_m_d2 = (2**71 - min_adj) // 3
min_Q_d2 = min_m_d2 // 71 + 1
max_Q_d2 = max_m_d2 // 71
print(f"  m[71] ∈ [{min_m_d2:.4e}, {max_m_d2:.4e}]")
print(f"  Q = m[71]/71 ∈ [{min_Q_d2:.4e}, {max_Q_d2:.4e}]")
print(f"  Q range size: {max_Q_d2 - min_Q_d2:,}")
print()

# Let's look at Q values for known prime m-values
print("### Q values for known primes where n | m[n] ###")
for p in primes:
    if p in m_values and m_values[p] % p == 0:
        Q = m_values[p] // p
        print(f"  Q[{p}] = {Q} (is prime: {all(Q % d != 0 for d in range(2, int(Q**0.5)+1)) if Q > 1 else False})")

print()
print("### Key observation: Q values often have structure ###")
print("Q[19] = 29689 = 17 × 1746.41... (not exact)")
print("Q[41] = 22342064035 = 5 × 4468412807")
print()

# Address generation setup
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

# Try specific Q values based on patterns
print("=" * 70)
print("TESTING SPECIFIC Q VALUES")
print("=" * 70)
print()

# Q might follow a pattern related to previous Q values
# Q[41] / Q[19] ≈ 752,000 → possible growth factor

# Test some specific Q values for d=1
test_qs = [
    27333099135597318907,  # min_Q
    35210341014878832066,  # mid_Q
    43931657825014270533,  # max_Q
]

for d in [1, 2]:
    print(f"### Testing d = {d} ###")
    k_d = k_values[d]

    for Q in test_qs[:1]:  # Just test min to show the process
        m = 71 * Q
        adj = 2**71 - m * k_d
        k71 = 2*k70 + adj

        if min_k71 <= k71 <= max_k71:
            addr = privkey_to_address(k71)
            print(f"Q = {Q}")
            print(f"m[71] = {m}")
            print(f"k[71] = {k71}")
            print(f"Address: {addr}")
            print(f"Match: {addr == TARGET}")
            print()

print()
print("=" * 70)
print("CONCLUSION")
print("=" * 70)
print()
print("Even with the self-index constraint (m[71] = 71 × Q),")
print("the Q range is still ~10^19 values - too large for brute force.")
print()
print("NEXT: Find pattern in Q values that could predict Q[71]")
