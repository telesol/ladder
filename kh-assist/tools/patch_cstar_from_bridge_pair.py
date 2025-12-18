#!/usr/bin/env python3
# --------------------------------------------------------------------
# patch_cstar_from_bridge_pair.py
#   – reads bits 60 and 61 from the DB,
#   – computes the 16 drifts,
#   – writes them into out/ladder_calib_29_70_full.json
# --------------------------------------------------------------------
import sqlite3, json, sys, os

DB        = "db/kh.db"
CALIB_JSON = "out/ladder_calib_29_70_full.json"

# --------------------------------------------------------------
# 1. Load the per‑lane multiplier A (the same A used everywhere)
# --------------------------------------------------------------
con = sqlite3.connect(DB)
cur = con.cursor()
row = cur.execute("""
    SELECT A_json
    FROM   class_affine_phase
    WHERE  m = 16
      AND  start_bit <= 29
      AND  end_bit   >= 70
    ORDER BY created_at DESC
    LIMIT 1
""").fetchone()
if not row:
    sys.exit("❌ No A_json found.")
A = {int(k): int(v) for k, v in json.loads(row[0]).items()}

# --------------------------------------------------------------
# 2. Pull bits 60 and 61 (strip the leading '0x')
# --------------------------------------------------------------
hex60 = cur.execute(
    "SELECT lower(substr(actual_hex,3)) FROM lcg_residuals WHERE bits = 60"
).fetchone()[0].rjust(64, '0')
hex61 = cur.execute(
    "SELECT lower(substr(actual_hex,3)) FROM lcg_residuals WHERE bits = 61"
).fetchone()[0].rjust(64, '0')

x = [int(hex60[i:i+2], 16)   for i in range(0, 64, 2)]   # bytes of bits 60
y = [int(hex61[i:i+2], 16)   for i in range(0, 64, 2)]   # bytes of bits 61

# --------------------------------------------------------------
# 3. Compute the drift for each lane (occ = 1 for block 0,
#    which is the same value the ladder uses as occ = 0 for block 1)
# --------------------------------------------------------------
drift_per_lane = [
    (y[pos] - (A[pos % 16] * x[pos] & 0xFF)) & 0xFF
    for pos in range(32)               # 32 bytes = 2 occurrences per lane
]

# --------------------------------------------------------------
# 4. Load the calibration JSON and patch the two missing slots
# --------------------------------------------------------------
if not os.path.exists(CALIB_JSON):
    sys.exit(f"❌ Calibration file {CALIB_JSON} not found – run rebuild_full_cstar_from_raw.py first.")
cal = json.load(open(CALIB_JSON))

# The JSON uses string keys for block and lane (exactly as verify_affine.py expects)
for lane in range(16):
    # block 0, occ 1
    cal["Cstar"]["0"][str(lane)][1] = drift_per_lane[lane]
    # block 1, occ 0  (the ladder copies the same value)
    cal["Cstar"]["1"][str(lane)][0] = drift_per_lane[lane]

# --------------------------------------------------------------
# 5. Write the patched JSON back to disk
# --------------------------------------------------------------
with open(CALIB_JSON, "w") as f:
    json.dump(cal, f, indent=2)

print("✅ Cstar patched – block‑0 occ 1 and block‑1 occ 0 now contain the correct drifts.")
print("   You can now run:  python verify_affine.py  (expect 100 % success)")
