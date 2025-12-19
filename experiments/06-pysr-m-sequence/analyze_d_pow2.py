#!/usr/bin/env python3
"""
Analyze the d-sequence relationship with powers of 2.

Key observations:
- d=4 at n=8,14,16,24,30 (near 8=2^3, 16=2^4, 32=2^5)
- d=8 at n=60,66 (near 64=2^6)

Hypothesis: d[n] = 2^k when n is "close" to 2^(k+something)
"""

import json

with open('/home/rkh/ladder/data_for_csolver.json', 'r') as f:
    data = json.load(f)

D_SEQ = data['d_seq']
M_SEQ = data['m_seq']

def d(n):
    if n < 2 or n > 70:
        return None
    return D_SEQ[n - 2]

def m(n):
    if n < 2 or n > 70:
        return None
    return M_SEQ[n - 2]

print("=" * 70)
print("D-SEQUENCE AND POWERS OF 2")
print("=" * 70)

# Full d-sequence
print("\n### Complete d-sequence (n=2 to 70):")
for start in range(2, 71, 20):
    end = min(start + 20, 71)
    vals = [d(n) for n in range(start, end)]
    indices = list(range(start, end))
    print(f"n={start:2}-{end-1:2}: {vals}")

# Find all positions where d[n] is a power of 2 > 1
print("\n### Positions where d[n] is a power of 2 > 1:")
pow2_positions = {}
for n in range(2, 71):
    dn = d(n)
    if dn > 1 and (dn & (dn - 1)) == 0:  # Is power of 2
        log2_d = dn.bit_length() - 1
        if log2_d not in pow2_positions:
            pow2_positions[log2_d] = []
        pow2_positions[log2_d].append(n)

for log2_d in sorted(pow2_positions.keys()):
    positions = pow2_positions[log2_d]
    print(f"  d=2^{log2_d}={2**log2_d}: at n={positions}")

# Analyze proximity to powers of 2
print("\n### Proximity to powers of 2:")
print("For each position with d=2^k (k>0), check distance to nearest 2^m")
print()

for log2_d in sorted(pow2_positions.keys()):
    positions = pow2_positions[log2_d]
    d_val = 2 ** log2_d
    print(f"d={d_val} (2^{log2_d}):")
    for n in positions:
        # Find nearest power of 2
        log2_n = n.bit_length() - 1
        lower = 2 ** log2_n
        upper = 2 ** (log2_n + 1)

        dist_lower = n - lower
        dist_upper = upper - n

        nearest = lower if dist_lower <= dist_upper else upper
        nearest_log = log2_n if dist_lower <= dist_upper else log2_n + 1
        dist = dist_lower if dist_lower <= dist_upper else dist_upper

        print(f"  n={n:2}: nearest 2^{nearest_log}={nearest}, distance={dist}")
    print()

# Check if d[n] relates to floor(log2(n)) or similar
print("=" * 70)
print("TESTING FORMULAS FOR d-SEQUENCE")
print("=" * 70)

# Test: d[n] = 2^floor(log2(n)-2) for certain n
print("\n### Test: d[n] = 2^(floor(log2(n))-2) when n near power of 2?")
for n in range(8, 71, 8):  # Check multiples of 8
    dn = d(n)
    log2_n = n.bit_length() - 1
    predicted = 2 ** max(0, log2_n - 2)
    match = "✓" if predicted == dn else ""
    print(f"  n={n:2}: d[n]={dn}, 2^(log2({n})-2)=2^{log2_n-2}={predicted} {match}")

# Check: d[n] = ruler function at certain positions?
print("\n### Test: d[n] vs ruler function (1 + trailing zeros in n-offset)")
print("Testing various offsets...")

best_offset = None
best_match_count = 0

for offset in range(-5, 10):
    matches = 0
    for n in range(2, 35):  # Test on first half
        x = n + offset
        if x <= 0:
            continue
        # Ruler function: 1 + number of trailing zeros
        tz = 0
        y = x
        while y > 0 and y % 2 == 0:
            tz += 1
            y //= 2
        ruler = tz + 1

        if d(n) == ruler:
            matches += 1

    if matches > best_match_count:
        best_match_count = matches
        best_offset = offset

print(f"\nBest offset: {best_offset} with {best_match_count}/33 matches")

# Show actual vs predicted for best offset
if best_offset is not None:
    print(f"\nWith offset={best_offset}:")
    print("n    d[n]  ruler(n+{})  match".format(best_offset))
    for n in range(2, 35):
        x = n + best_offset
        if x <= 0:
            dn = d(n)
            print(f"{n:3}  {dn:4}  N/A")
            continue
        tz = 0
        y = x
        while y > 0 and y % 2 == 0:
            tz += 1
            y //= 2
        ruler = tz + 1
        dn = d(n)
        match = "✓" if dn == ruler else ""
        print(f"{n:3}  {dn:4}  {ruler:4}        {match}")

# Check d-sequence self-reference
print("\n" + "=" * 70)
print("D-SEQUENCE SELF-REFERENCE")
print("=" * 70)

print("\n### Does d[n] = d[n - d[n-1]] or similar?")
for n in range(3, 20):
    dn = d(n)
    dn_prev = d(n - 1)
    if n - dn_prev >= 2:
        d_target = d(n - dn_prev)
        match = "✓" if dn == d_target else ""
        print(f"d[{n}]={dn}, d[{n} - d[{n-1}]] = d[{n-dn_prev}]={d_target} {match}")

print("\n### Does d[n] relate to the position of most significant bit?")
for n in range(2, 25):
    dn = d(n)
    msb = n.bit_length()  # Position of MSB
    print(f"n={n:3}: d[n]={dn}, msb_pos={msb}, n%msb={n%msb}, n//msb={n//msb}")

# Check if d[n] = k[d[n-1]] % something
print("\n" + "=" * 70)
print("D vs M RELATIONSHIP")
print("=" * 70)

print("\n### Is d[n] related to m[n-1] or m[d[n-1]]?")
for n in range(3, 20):
    dn = d(n)
    dn_prev = d(n - 1)
    mn_prev = m(n - 1)
    m_d_prev = m(dn_prev) if dn_prev >= 2 else None

    print(f"n={n:3}: d[n]={dn}, d[n-1]={dn_prev}, m[n-1]={mn_prev}, m[d[n-1]]={m_d_prev}")
