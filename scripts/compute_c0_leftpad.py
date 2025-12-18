#!/usr/bin/env python3
import json, sys

# -----------------------------------------------------------------
# The two halves we will use: right‑most 32 hex chars of bits 1 and 2
# -----------------------------------------------------------------
HEX1 = sys.argv[1]   # 32‑hex‑char string (the key part of bit 1)
HEX2 = sys.argv[2]   # 32‑hex‑char string (the key part of bit 2)

# -----------------------------------------------------------------
# Load matrix A from the existing calibration JSON (it already contains A)
# -----------------------------------------------------------------
with open('out/ladder_calib_29_70_full.json') as f:
    calib = json.load(f)

A = calib['A']                      # list of 16 integers (64‑bit each)

def half_to_int(h):
    """Convert a 32‑hex‑char string to a 128‑bit integer (little‑endian view)."""
    return int(h, 16)

a = half_to_int(HEX1)
b = half_to_int(HEX2)

MOD = 1 << 64
C_bytes = bytearray(16)

# lane‑wise drift: C_i = (b_i - A_i * a_i) (mod 2⁶⁴)
for i in range(16):
    a_i   = (a >> (8*i)) & 0xFF
    prod  = (A[i] * a_i) % MOD
    b_i   = (b >> (8*i)) & 0xFF
    C_i   = (b_i - prod) % MOD
    C_bytes[i] = C_i

# -----------------------------------------------------------------
# Patch the calibration JSON (we will write a *new* file that reflects the 1‑70 range)
# -----------------------------------------------------------------
drift = {"0": {"0": list(C_bytes)}}
calib['Cstar'] = drift

out_path = 'out/ladder_calib_1_70_full.json'   # new file that covers 1‑70
with open(out_path, 'w') as f:
    json.dump(calib, f, indent=2)

print(f"C₀ written to {out_path}")
