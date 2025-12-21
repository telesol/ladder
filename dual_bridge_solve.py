#!/usr/bin/env python3
"""
Use dual bridge constraints to narrow down k[71].

Key insight: We have two independent bridge paths:

Path 1: k[70] → k[73] → k[76] → k[79] → k[82] → k[85]
  k[85] = 6561*k[70] + 729*offset[73] + 81*offset[76] + 9*offset[79] + offset[82] + ...

Path 2: k[71] → k[74] → k[77] → k[80]
  k[80] = 729*k[71] + 81*offset[74] + 9*offset[77] + offset[80]

Since offset[n] = k[n] - 9*k[n-3], and k[n] = 2*k[n-1] + adj[n],
there's a relationship between adj values that we can exploit.
"""
import sqlite3
import hashlib

# Load known k values
conn = sqlite3.connect('/home/solo/ladder/db/kh.db')
cur = conn.cursor()
k_values = {}
for n in range(1, 91):
    cur.execute('SELECT priv_hex FROM keys WHERE puzzle_id = ?', (n,))
    row = cur.fetchone()
    if row:
        k_values[n] = int(row[0], 16)
conn.close()

print("=" * 70)
print("DUAL BRIDGE CONSTRAINT ANALYSIS")
print("=" * 70)
print()

k70 = k_values[70]
k85 = k_values[85]
k80 = k_values[80]

# Bridge from k[70] to k[85]
# k[73] = 9*k[70] + offset[73]
# k[76] = 9*k[73] + offset[76] = 81*k[70] + 9*offset[73] + offset[76]
# k[79] = 9*k[76] + offset[79] = 729*k[70] + 81*offset[73] + 9*offset[76] + offset[79]
# k[82] = 9*k[79] + offset[82] = 6561*k[70] + 729*offset[73] + 81*offset[76] + 9*offset[79] + offset[82]
# k[85] = 9*k[82] + offset[85] = 59049*k[70] + 6561*offset[73] + 729*offset[76] + 81*offset[79] + 9*offset[82] + offset[85]

S85 = k85 - (9**5) * k70
print(f"k[70] = {k70}")
print(f"k[85] = {k85}")
print(f"9^5 = {9**5}")
print(f"S85 = k[85] - 9^5*k[70] = {S85}")
print(f"S85 = 6561*offset[73] + 729*offset[76] + 81*offset[79] + 9*offset[82] + offset[85]")
print()

# Bridge from k[71] to k[80]
# k[80] = 729*k[71] + 81*offset[74] + 9*offset[77] + offset[80]

print(f"k[80] = {k80}")
print(f"k[80] = 729*k[71] + 81*offset[74] + 9*offset[77] + offset[80]")
print()

# Now, there's a relationship between the offsets through k[71].
# k[71] = 2*k[70] + adj[71]
# offset[74] = k[74] - 9*k[71]
# k[74] = 2*k[73] + adj[74]
# k[73] = 2*k[72] + adj[73]
# k[72] = 2*k[71] + adj[72]

# So k[74] = 2*(2*(2*k[71] + adj[72]) + adj[73]) + adj[74]
#          = 8*k[71] + 4*adj[72] + 2*adj[73] + adj[74]

# offset[74] = k[74] - 9*k[71] = -k[71] + 4*adj[72] + 2*adj[73] + adj[74]

# Similarly for offset[77] and offset[80]

print("### Key relationship ###")
print("offset[74] = -k[71] + 4*adj[72] + 2*adj[73] + adj[74]")
print("offset[77] = -k[74] + 4*adj[75] + 2*adj[76] + adj[77]")
print("offset[80] = -k[77] + 4*adj[78] + 2*adj[79] + adj[80]")
print()

# Substituting into k[80] equation:
# k[80] = 729*k[71] + 81*(-k[71] + 4*adj[72] + ...) + 9*(...) + (...)
# This gets complicated. Let me try a different approach.

print("### Alternative: Direct k[71] bounds from k[80] ###")
print()

# We know k[80]. We can bound k[71] if we bound the offset sum.
# offset_sum = 81*offset[74] + 9*offset[77] + offset[80]

# From the known offset pattern (n=68-70):
off68 = k_values[68] - 9*k_values[65]
off69 = k_values[69] - 9*k_values[66]
off70 = k_values[70] - 9*k_values[67]

print(f"offset[68] = {off68}")
print(f"offset[69] = {off69}")
print(f"offset[70] = {off70}")
print()

# Growth ratios
r68_69 = off69 / off68
r69_70 = off70 / off69
print(f"Ratio 69/68: {r68_69:.4f}")
print(f"Ratio 70/69: {r69_70:.4f}")
print()

# The ratios vary. Let's compute bounds for offset[74], [77], [80]
# using different growth scenarios

print("### Offset bounds with different growth scenarios ###")
print()

# Scenario 1: Growth continues at r69_70
def scenario_growth(base_off, growth, steps):
    result = base_off
    for _ in range(steps):
        result *= growth
    return result

# For offset[74]: 4 steps from offset[70]
# For offset[77]: 7 steps from offset[70]
# For offset[80]: 10 steps from offset[70]

scenarios = [
    ("Conservative (1.5)", 1.5),
    ("Medium (1.7)", 1.7),
    ("Aggressive (2.0)", 2.0),
    ("Recent ratio", r69_70),
]

min_k71 = 2**70
max_k71 = 2**71 - 1

print(f"Valid k[71] range: [{min_k71:.4e}, {max_k71:.4e}]")
print()

for name, growth in scenarios:
    off74 = scenario_growth(off70, growth, 4)
    off77 = scenario_growth(off70, growth, 7)
    off80 = scenario_growth(off70, growth, 10)

    offset_sum = 81*off74 + 9*off77 + off80
    k71_est = (k80 - offset_sum) / 729

    in_range = min_k71 <= k71_est <= max_k71
    status = "VALID" if in_range else "OUT OF RANGE"

    print(f"{name}:")
    print(f"  offset[74] = {off74:.4e}")
    print(f"  offset[77] = {off77:.4e}")
    print(f"  offset[80] = {off80:.4e}")
    print(f"  offset_sum = {offset_sum:.4e}")
    print(f"  k[71] = {k71_est:.4e} [{status}]")
    print()

# Now let's find the growth factor that makes k[71] exactly at the boundaries
print("### Finding growth factor bounds ###")
print()

# k[71] = (k80 - offset_sum) / 729
# For k[71] = min_k71: offset_sum = k80 - 729*min_k71
# For k[71] = max_k71: offset_sum = k80 - 729*max_k71

offset_sum_for_min = k80 - 729 * min_k71
offset_sum_for_max = k80 - 729 * max_k71

print(f"For k[71] = min: offset_sum = {offset_sum_for_min:.4e}")
print(f"For k[71] = max: offset_sum = {offset_sum_for_max:.4e}")
print()

# Find growth that gives these offset sums
def find_growth_for_sum(target_sum):
    # offset_sum = 81*off70*g^4 + 9*off70*g^7 + off70*g^10
    # = off70 * (81*g^4 + 9*g^7 + g^10)

    for g_int in range(100, 300):
        g = g_int / 100.0
        est_sum = off70 * (81 * g**4 + 9 * g**7 + g**10)
        if abs(est_sum - target_sum) < abs(target_sum * 0.001):
            return g, est_sum
    return None, None

g_min, _ = find_growth_for_sum(offset_sum_for_min)
g_max, _ = find_growth_for_sum(offset_sum_for_max)

if g_min:
    print(f"Growth for k[71]=min: {g_min:.4f}")
if g_max:
    print(f"Growth for k[71]=max: {g_max:.4f}")

print()
print("=" * 70)
print("USING S85 CONSTRAINT TO FURTHER NARROW")
print("=" * 70)
print()

# S85 = 6561*offset[73] + 729*offset[76] + 81*offset[79] + 9*offset[82] + offset[85]
# offset[73] = off70 * g^3
# offset[76] = off70 * g^6
# offset[79] = off70 * g^9
# offset[82] = off70 * g^12
# offset[85] = off70 * g^15

def compute_S85_for_growth(g):
    return off70 * (6561 * g**3 + 729 * g**6 + 81 * g**9 + 9 * g**12 + g**15)

print(f"Actual S85 = {S85}")
print()

# Find growth that matches S85
best_g = None
best_error = float('inf')

for g_int in range(100, 300):
    g = g_int / 100.0
    est_S85 = compute_S85_for_growth(g)
    error = abs(est_S85 - S85) / abs(S85)
    if error < best_error:
        best_error = error
        best_g = g

# Refine
for g_int in range(int(best_g * 1000) - 100, int(best_g * 1000) + 100):
    g = g_int / 1000.0
    est_S85 = compute_S85_for_growth(g)
    error = abs(est_S85 - S85) / abs(S85)
    if error < best_error:
        best_error = error
        best_g = g

print(f"Best growth from S85: {best_g:.4f}")
print(f"S85 error: {best_error*100:.2f}%")
print()

# Use this growth to estimate k[71]
off74_s85 = off70 * best_g**4
off77_s85 = off70 * best_g**7
off80_s85 = off70 * best_g**10

offset_sum_s85 = 81*off74_s85 + 9*off77_s85 + off80_s85
k71_s85 = (k80 - offset_sum_s85) / 729

print(f"Using S85-derived growth:")
print(f"  offset[74] = {off74_s85:.4e}")
print(f"  offset_sum = {offset_sum_s85:.4e}")
print(f"  k[71] = {k71_s85:.4e}")
print(f"  In range: {min_k71 <= k71_s85 <= max_k71}")
print()

# Generate address
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

if min_k71 <= k71_s85 <= max_k71:
    k71_int = int(k71_s85)
    addr = privkey_to_address(k71_int)
    print(f"k[71] = {k71_int}")
    print(f"k[71] hex = {hex(k71_int)}")
    print(f"Address: {addr}")
    print(f"Target:  {TARGET}")
    print(f"Match: {'YES!!!' if addr == TARGET else 'No'}")

print()
print("=" * 70)
print("INSIGHT: NON-UNIFORM OFFSET GROWTH")
print("=" * 70)
print()

# Let's analyze the offset pattern more carefully
print("### Offset ratio pattern analysis ###")
print()

# Compute all known offsets
offsets = {}
for n in range(4, 71):
    if n in k_values and (n-3) in k_values:
        offsets[n] = k_values[n] - 9*k_values[n-3]

# Show the ratio sequence
print("Offset ratios (offset[n]/offset[n-1]):")
for n in range(40, 71):
    if n in offsets and (n-1) in offsets and offsets[n-1] != 0:
        ratio = offsets[n] / offsets[n-1]
        print(f"  r[{n}] = {ratio:.4f}")

# Look for periodicity
print()
print("### Looking for periodicity in ratios ###")

ratios = []
for n in range(50, 71):
    if n in offsets and (n-1) in offsets and offsets[n-1] != 0:
        ratios.append((n, offsets[n] / offsets[n-1]))

# Check for period-3 pattern (since we use 3-step recursion)
print("Period-3 averages:")
for phase in range(3):
    phase_ratios = [r for n, r in ratios if n % 3 == phase]
    if phase_ratios:
        avg = sum(phase_ratios) / len(phase_ratios)
        print(f"  Phase {phase} (n mod 3 = {phase}): avg ratio = {avg:.4f}")

print()
print("=" * 70)
