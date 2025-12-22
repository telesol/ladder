#!/usr/bin/env python3
# --------------------------------------------------------------
# predict_next_halfblock.py
#   – reads the calibrated ladder (A, Cstar)
#   – fetches the last known half‑block (bits = 70)
#   • uses the ladder’s *periodicity* to obtain the correct drift for
#     the upcoming half‑block (bits = 71)
#   – prints the calculated 64‑hex‑digit string
#   – if bits 71 already exists in the DB it also prints a match report
# --------------------------------------------------------------
import sqlite3, json, sys, os

DB          = "db/kh.db"
CALIB_JSON  = "out/ladder_calib_29_70_full.json"

# -----------------------------------------------------------------
# 1. Load A and Cstar (keys are strings → convert to int)
# -----------------------------------------------------------------
if not os.path.exists(CALIB_JSON):
    sys.exit("❌ Calibration file missing – run rebuild_full_cstar_from_raw.py first.")
with open(CALIB_JSON) as f:
    cal = json.load(f)

A = {int(k): int(v) for k, v in cal["A"].items()}
C = {
    int(b): {int(l): v for l, v in lane_map.items()}
    for b, lane_map in cal["Cstar"].items()
}   # C[block][lane] = [occ0, occ1]

# -----------------------------------------------------------------
# 2. Helper to go between hex strings and byte lists
# -----------------------------------------------------------------
def hex_to_bytes(s):
    s = s.rjust(64, '0')
    return [int(s[i:i+2], 16) for i in range(0, 64, 2)]

def bytes_to_hex(b):
    return '0x' + ''.join(f'{x:02x}' for x in b)

# -----------------------------------------------------------------
# 3. Grab the *real* half‑block 70 (the last known one)
# -----------------------------------------------------------------
con = sqlite3.connect(DB)
cur = con.cursor()
row70 = cur.execute(
    "SELECT lower(substr(actual_hex,3)) FROM lcg_residuals WHERE bits = 70"
).fetchone()
if not row70:
    sys.exit("❌ No row for bits 70.")
x_bytes = hex_to_bytes(row70[0])          # bytes of bits 70 (the current state)

# -----------------------------------------------------------------
# 4. Determine which drift the ladder will use for bits 71
# -----------------------------------------------------------------
#   bits 71 belongs to block = 2 (the *third* block) and occ = 0
#   The ladder repeats its drifts every 2 blocks:
#       block 0 occ0 → C[0][ℓ][0]
#       block 0 occ1 → C[0][ℓ][1]
#       block 1 occ0 → C[1][ℓ][0] = C[0][ℓ][1]   (bridge)
#       block 1 occ1 → C[1][ℓ][1]
#       block 2 occ0 → C[2][ℓ][0] = C[1][ℓ][1]   (next‑block bridge)
#       block 2 occ1 → C[2][ℓ][1] = C[0][ℓ][0]
#   Because we only calibrated blocks 0 and 1, we obtain the needed drift
#   from block 1, occ 1.
drift_source_block = 1           # block 1
drift_source_occ   = 1           # occ 1  → this is the drift that will be used for bits 71 occ 0
drift_table = C[drift_source_block]   # dict lane → [occ0, occ1]

# -----------------------------------------------------------------
# 5. Apply the affine map (forward direction) to obtain bits 71
# -----------------------------------------------------------------
y_bytes = []
for pos, xb in enumerate(x_bytes):
    lane = pos % 16
    drift = drift_table[lane][drift_source_occ]   # C[1][lane][1] = C[2][lane][0]
    y = (A[lane] * xb + drift) & 0xFF
    y_bytes.append(y)

predicted_hex = bytes_to_hex(y_bytes)
print(f"Calculated bits 71: {predicted_hex}")

# -----------------------------------------------------------------
# 6. (Optional) compare with the *real* half‑block 71, if it exists
# -----------------------------------------------------------------
row71 = cur.execute(
    "SELECT lower(substr(actual_hex,3)) FROM lcg_residuals WHERE bits = 71"
).fetchone()
if row71:
    real_hex = '0x' + row71[0]
    print(f"Real bits 71:      {real_hex}")

    # byte‑by‑byte comparison
    real_bytes = hex_to_bytes(row71[0])
    mismatches = [(i, r, p) for i, (r, p) in enumerate(zip(real_bytes, y_bytes)) if r != p]
    if not mismatches:
        print("✅ 100 % match – the ladder predicts the next block perfectly!")
    else:
        print(f"⚠️  Mismatch in {len(mismatches)} / 32 bytes:")
        for i, r, p in mismatches[:10]:   # show first few
            print(f"   byte {i:02d}: real = {r:02x}, calculated = {p:02x}")
else:
    print("ℹ️  No real half‑block 71 in the DB – you can now store the above value.")
