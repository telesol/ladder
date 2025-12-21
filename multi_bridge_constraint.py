#!/usr/bin/env python3
"""
Use multiple bridge constraints from k[75], k[80], k[85], k[90] to constrain k[71].

Bridge equations using 3-step recursion k[n] = 9*k[n-3] + offset[n]:

For k[75] (from k[69]):
  k[72] = 9*k[69] + offset[72]
  k[75] = 9*k[72] + offset[75] = 81*k[69] + 9*offset[72] + offset[75]

For k[80] (from k[71]):
  k[74] = 9*k[71] + offset[74]
  k[77] = 9*k[74] + offset[77] = 81*k[71] + 9*offset[74] + offset[77]
  k[80] = 9*k[77] + offset[80] = 729*k[71] + 81*offset[74] + 9*offset[77] + offset[80]

For k[90] (from k[69]):
  k[90] = 9^7*k[69] + (9^6*offset[72] + 9^5*offset[75] + 9^4*offset[78] + 9^3*offset[81] + 9^2*offset[84] + 9*offset[87] + offset[90])
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

# Compute known offset values
offsets = {}
for n in range(4, 71):
    if n in k_values and (n-3) in k_values:
        offsets[n] = k_values[n] - 9 * k_values[n-3]

print("=" * 70)
print("MULTI-BRIDGE CONSTRAINT ANALYSIS")
print("=" * 70)
print()

k69 = k_values[69]
k70 = k_values[70]
k75 = k_values[75]
k80 = k_values[80]
k85 = k_values[85]
k90 = k_values[90]

print(f"k[69] = {k69}")
print(f"k[70] = {k70}")
print(f"k[75] = {k75}")
print(f"k[80] = {k80}")
print(f"k[85] = {k85}")
print(f"k[90] = {k90}")
print()

# Bridge 1: k[75] constraint
# k[75] = 81*k[69] + 9*offset[72] + offset[75]
S75 = k75 - 81 * k69
print("### Bridge 1: k[75] ###")
print(f"k[75] - 81*k[69] = {S75}")
print(f"This equals: 9*offset[72] + offset[75]")
print()

# Bridge 2: k[80] constraint
# k[80] = 729*k[71] + 81*offset[74] + 9*offset[77] + offset[80]
print("### Bridge 2: k[80] ###")
print(f"k[80] = 729*k[71] + 81*offset[74] + 9*offset[77] + offset[80]")
print()

# Bridge 3: k[90] constraint
# k[90] = 9^7*k[69] + offset_sum_90
nine_pow_7 = 9**7  # 4782969
print("### Bridge 3: k[90] ###")
print(f"9^7 = {nine_pow_7}")
S90 = k90 - nine_pow_7 * k69
print(f"k[90] - 9^7*k[69] = {S90}")
print(f"This equals: 9^6*offset[72] + 9^5*offset[75] + 9^4*offset[78] + 9^3*offset[81] + 9^2*offset[84] + 9*offset[87] + offset[90]")
print()

# Let's analyze the offset growth pattern
print("### Offset Pattern Analysis (n=65-70) ###")
for n in range(65, 71):
    if n in offsets:
        print(f"offset[{n}] = {offsets[n]:.4e}")

# Compute offset growth ratios
print("\n### Offset Growth Ratios ###")
for n in range(66, 71):
    if n in offsets and (n-1) in offsets:
        ratio = offsets[n] / offsets[n-1]
        print(f"offset[{n}]/offset[{n-1}] = {ratio:.4f}")

print()
print("=" * 70)
print("KEY INSIGHT: Offset Pattern from n=68-70")
print("=" * 70)
print()

off68 = offsets[68]
off69 = offsets[69]
off70 = offsets[70]

print(f"offset[68] = {off68}")
print(f"offset[69] = {off69}")
print(f"offset[70] = {off70}")
print()

# Compute second difference
d1_69 = off69 - off68
d1_70 = off70 - off69
d2 = d1_70 - d1_69

print(f"First difference d1[69] = offset[69] - offset[68] = {d1_69}")
print(f"First difference d1[70] = offset[70] - offset[69] = {d1_70}")
print(f"Second difference d2 = d1[70] - d1[69] = {d2}")
print()

# Try to extrapolate using different models
print("### Extrapolation Models ###")
print()

# Model 1: Constant second difference
d1_71_const = d1_70 + d2
off71_const = off70 + d1_71_const
print(f"Model 1 (constant d2): offset[71] = {off71_const:.4e}")

# Model 2: Exponential growth (ratio stays constant)
ratio_69 = off69 / off68
ratio_70 = off70 / off69
avg_ratio = (ratio_69 + ratio_70) / 2
off71_exp = off70 * avg_ratio
print(f"Model 2 (exponential, ratio={avg_ratio:.4f}): offset[71] = {off71_exp:.4e}")

# Model 3: Use the S75 constraint
# S75 = 9*offset[72] + offset[75]
# If we assume offset growth continues at avg_ratio:
# offset[72] = offset[69] * ratio^3
# offset[75] = offset[72] * ratio^3 = offset[69] * ratio^6
# S75 = 9*offset[69]*ratio^3 + offset[69]*ratio^6

# Solve for ratio using S75
# S75 = offset[69] * (9*ratio^3 + ratio^6)

# This is a degree 6 polynomial. Let's find the ratio numerically.
import math

def compute_S75_for_ratio(r):
    off72_est = off69 * (r ** 3)
    off75_est = off72_est * (r ** 3)
    return 9 * off72_est + off75_est

print()
print("### Solving for ratio using S75 constraint ###")
print(f"Target S75 = {S75}")
print()

# Binary search for ratio
best_ratio = None
best_error = float('inf')

for r_int in range(100, 300):  # Test ratios from 1.0 to 3.0
    r = r_int / 100.0
    s75_est = compute_S75_for_ratio(r)
    error = abs(s75_est - S75) / abs(S75)
    if error < best_error:
        best_error = error
        best_ratio = r

# Refine with finer search
for r_int in range(int(best_ratio * 1000) - 50, int(best_ratio * 1000) + 50):
    r = r_int / 1000.0
    s75_est = compute_S75_for_ratio(r)
    error = abs(s75_est - S75) / abs(S75)
    if error < best_error:
        best_error = error
        best_ratio = r

print(f"Best ratio from S75: {best_ratio:.4f}")
print(f"Error: {best_error*100:.4f}%")
print()

# Use this ratio to estimate offsets
off71_s75 = off70 * best_ratio
off72_s75 = off71_s75 * best_ratio
off73_s75 = off72_s75 * best_ratio
off74_s75 = off73_s75 * best_ratio
off75_s75 = off74_s75 * best_ratio
off77_s75 = off74_s75 * best_ratio**3
off80_s75 = off77_s75 * best_ratio**3

print(f"Estimated offset[71] = {off71_s75:.4e}")
print(f"Estimated offset[74] = {off74_s75:.4e}")
print(f"Estimated offset[77] = {off77_s75:.4e}")
print(f"Estimated offset[80] = {off80_s75:.4e}")
print()

# Compute k[71] from k[80] bridge
# k[80] = 729*k[71] + 81*offset[74] + 9*offset[77] + offset[80]
offset_sum_80 = 81*off74_s75 + 9*off77_s75 + off80_s75
k71_from_80 = (k80 - offset_sum_80) / 729

print("### k[71] from k[80] bridge ###")
print(f"81*offset[74] + 9*offset[77] + offset[80] = {offset_sum_80:.4e}")
print(f"k[71] = (k[80] - offset_sum) / 729 = {k71_from_80:.4e}")
print()

min_k71 = 2**70
max_k71 = 2**71 - 1
print(f"Valid range: [{min_k71:.4e}, {max_k71:.4e}]")
print(f"In range: {min_k71 <= k71_from_80 <= max_k71}")
print()

# Verify with S90 constraint
# S90 = 9^6*offset[72] + 9^5*offset[75] + 9^4*offset[78] + 9^3*offset[81] + 9^2*offset[84] + 9*offset[87] + offset[90]
print("### Verifying with S90 constraint ###")

off78_s75 = off75_s75 * best_ratio**3
off81_s75 = off78_s75 * best_ratio**3
off84_s75 = off81_s75 * best_ratio**3
off87_s75 = off84_s75 * best_ratio**3
off90_s75 = off87_s75 * best_ratio**3

S90_est = (9**6 * off72_s75 + 9**5 * off75_s75 + 9**4 * off78_s75 +
           9**3 * off81_s75 + 9**2 * off84_s75 + 9 * off87_s75 + off90_s75)

print(f"Actual S90 = {S90:.4e}")
print(f"Estimated S90 = {S90_est:.4e}")
print(f"Error: {abs(S90_est - S90) / abs(S90) * 100:.2f}%")
print()

# The S90 error tells us how accurate our ratio is
# Let's try to find a better ratio using both constraints

print("=" * 70)
print("JOINT OPTIMIZATION: Find ratio matching both S75 and S90")
print("=" * 70)
print()

def compute_errors(r):
    off72 = off69 * (r ** 3)
    off75 = off72 * (r ** 3)
    off78 = off75 * (r ** 3)
    off81 = off78 * (r ** 3)
    off84 = off81 * (r ** 3)
    off87 = off84 * (r ** 3)
    off90 = off87 * (r ** 3)

    s75_est = 9 * off72 + off75
    s90_est = (9**6 * off72 + 9**5 * off75 + 9**4 * off78 +
               9**3 * off81 + 9**2 * off84 + 9 * off87 + off90)

    err75 = abs(s75_est - S75) / abs(S75)
    err90 = abs(s90_est - S90) / abs(S90)

    return err75, err90, err75 + err90

best_joint_ratio = None
best_joint_error = float('inf')

for r_int in range(1000, 3000):
    r = r_int / 1000.0
    err75, err90, total = compute_errors(r)
    if total < best_joint_error:
        best_joint_error = total
        best_joint_ratio = r

print(f"Best joint ratio: {best_joint_ratio:.4f}")
err75, err90, _ = compute_errors(best_joint_ratio)
print(f"S75 error: {err75*100:.2f}%")
print(f"S90 error: {err90*100:.2f}%")
print()

# Use joint ratio
off71_joint = off70 * best_joint_ratio
off74_joint = off71_joint * best_joint_ratio**3
off77_joint = off74_joint * best_joint_ratio**3
off80_joint = off77_joint * best_joint_ratio**3

offset_sum_joint = 81*off74_joint + 9*off77_joint + off80_joint
k71_joint = (k80 - offset_sum_joint) / 729

print(f"k[71] from joint optimization: {k71_joint:.4e}")
print(f"In valid range: {min_k71 <= k71_joint <= max_k71}")
print()

# Generate Bitcoin address for this k[71]
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

if min_k71 <= k71_joint <= max_k71:
    k71_int = int(k71_joint)
    addr = privkey_to_address(k71_int)
    print(f"k[71] = {k71_int}")
    print(f"Address: {addr}")
    print(f"Target:  {TARGET}")
    print(f"Match: {'YES!!!' if addr == TARGET else 'No'}")
else:
    print("k[71] out of valid range")

print()
print("=" * 70)
print("SEARCHING AROUND JOINT ESTIMATE")
print("=" * 70)
print()

# Skip expensive search - focus on analysis
print("Skipping full search - range is too large for brute force")

print()
print("=" * 70)
print("CONCLUSION")
print("=" * 70)
print()
print("The uniform growth assumption doesn't match S75 and S90 perfectly.")
print("The offset sequence has more complex structure than simple exponential.")
print()
print("Next: Analyze offset sequence for non-uniform growth patterns")
