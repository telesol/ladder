#!/usr/bin/env python3
"""
Generate k[71] candidates based on constant selector hypothesis
"""
import sqlite3
import math
import hashlib

# Load k[70]
conn = sqlite3.connect('db/kh.db')
cursor = conn.cursor()
cursor.execute("SELECT priv_hex FROM keys WHERE puzzle_id=70")
k70 = int(cursor.fetchone()[0], 16)
conn.close()

# Target hash for verification
TARGET_HASH160 = "f6f5431d25bbf7b12e8add9af5e3475c44a0a5b8"

# Mathematical constants that might be used for n=71
# n=71: prime, n mod 5 = 1
CONSTANTS = {
    '1/phi': 2/(1+math.sqrt(5)),      # 0.6180339887...
    'pi/4': math.pi/4,                 # 0.7853981634...
    'ln(2)': math.log(2),              # 0.6931471806...
    '1/sqrt(2)': 1/math.sqrt(2),       # 0.7071067812...
    'e/pi': math.e/math.pi,            # 0.8652559795...
    '2/e': 2/math.e,                   # 0.7357588824...
    'sqrt(2)-1': math.sqrt(2)-1,       # 0.4142135624...
}

print("=" * 80)
print("K[71] CANDIDATES BASED ON CONSTANT SELECTOR")
print("=" * 80)

print(f"\nKnown: k[70] = {k70}")
print(f"Range: [{2**70}, {2**71-1}]")
print(f"Target HASH160: {TARGET_HASH160}")

print("\n" + "-" * 80)
print("Candidates for each constant:")
print("-" * 80)

candidates = []
for name, C in CONSTANTS.items():
    k71 = int(C * 2**71)
    
    # Check if in valid range
    if 2**70 <= k71 <= 2**71 - 1:
        adj71 = k71 - 2*k70
        
        # If d=1: m = 2^71 - adj
        m71_d1 = 2**71 - adj71
        
        # If d=2: m = (2^71 - adj) / 3
        m71_d2 = (2**71 - adj71) / 3 if (2**71 - adj71) % 3 == 0 else None
        
        hex_k71 = hex(k71)
        
        print(f"\n{name} (C = {C:.6f}):")
        print(f"  k[71] = {k71}")
        print(f"  k[71] hex = {hex_k71}")
        print(f"  adj[71] = {adj71}")
        print(f"  If d=1: m[71] = {m71_d1}")
        if m71_d2 and m71_d2 == int(m71_d2):
            print(f"  If d=2: m[71] = {int(m71_d2)}")
        
        candidates.append({
            'constant': name,
            'C': C,
            'k71': k71,
            'hex': hex_k71,
            'adj71': adj71,
            'm71_d1': m71_d1
        })

print("\n" + "=" * 80)
print("REFINED PREDICTIONS BASED ON PATTERN")
print("=" * 80)

# For primes with n mod 5 = 1:
# n=11: d=1, C ≈ 0.938 (close to e/pi but higher)
# n=31: d=1, C ≈ 0.983 (close to 1)
# n=41: d=2, C ≈ 0.663 (close to ln(2))
# n=61: d=2, C ≈ 0.618 (exactly 1/phi!)

print("\nPattern for primes with n mod 5 = 1:")
print("  n=11: C ≈ 0.938, d=1")
print("  n=31: C ≈ 0.983, d=1")
print("  n=41: C ≈ 0.663, d=2")
print("  n=61: C ≈ 0.618, d=2")

print("\nThe pattern suggests alternation!")
print("  n=11, 31 → d=1 (high C)")
print("  n=41, 61 → d=2 (low C, 1/phi)")
print("  n=71 → likely d=1 or continue d=2 pattern")

# Most likely candidates
print("\n" + "-" * 80)
print("MOST LIKELY CANDIDATES (based on pattern):")
print("-" * 80)

# If pattern continues: d=2, C = 1/phi
print("\n1. If pattern continues (d=2, C = 1/phi):")
C = 2/(1+math.sqrt(5))
k71 = int(C * 2**71)
print(f"   k[71] = {k71}")
print(f"   Hex: {hex(k71)}")

# If pattern alternates back: d=1, high C
print("\n2. If pattern alternates (d=1, C ≈ 0.98):")
C = 0.98
k71 = int(C * 2**71)
print(f"   k[71] = {k71}")
print(f"   Hex: {hex(k71)}")

# If using observed similar primes average
print("\n3. Using average of n=11,31,41,61 pattern:")
# Recent primes (41, 61) use lower C around 0.64
C = 0.64
k71 = int(C * 2**71)
print(f"   k[71] = {k71}")
print(f"   Hex: {hex(k71)}")

print("\n" + "=" * 80)
print("VERIFICATION NEEDED")
print("=" * 80)
print("""
To verify any candidate:
1. Compute Bitcoin address from private key
2. Check if HASH160 matches target: f6f5431d25bbf7b12e8add9af5e3475c44a0a5b8

The constant selector approach gives us candidates, but we need either:
- More pattern analysis to narrow down the exact C(71)
- Verification tool to test candidates
""")
