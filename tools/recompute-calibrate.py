#!/usr/bin/env python3
# recompute-calibrate.py
import sqlite3, json, collections, math, sys

DB   = "db/kh.db"
R0,R1 = 29,70                     # calibration interval
LANES = {1,5,9,13}
blk   = lambda i: (i-29)//32      # block index: 0 for bits 29‑60, 1 for 61‑92

def hex_to_bytes(h):
    return [int(h[i:i+2],16) for i in range(0, len(h), 2)]

con = sqlite3.connect(DB)
cur = con.cursor()

# --------------------------------------------------------------
# 1) Load the affine parameters that were fitted on the whole range
# --------------------------------------------------------------
row = cur.execute("""
    SELECT A_json, C_json
    FROM class_affine_phase
    WHERE m = 16
      AND start_bit <= 29
      AND end_bit   >= 155
    ORDER BY created_at DESC
    LIMIT 1;
""").fetchone()
if not row:
    sys.exit("No A/C parameters found in class_affine_phase.")
A = {int(k): int(v) for k,v in json.loads(row[0]).items()}
C = {int(k): int(v) for k,v in json.loads(row[1]).items()}

# --------------------------------------------------------------
# 2) Build the drift table Cstar from the calibration interval
# --------------------------------------------------------------
def build_cstar():
    cstar = collections.defaultdict(lambda: collections.defaultdict(list))
    pairs = cur.execute("""
        SELECT a.idx, a.hex, b.hex
        FROM ladder32_resid a
        JOIN ladder32_resid b ON b.idx = a.idx + 1
        WHERE a.idx BETWEEN ? AND ?
        ORDER BY a.idx;
    """, (R0,R1)).fetchall()

    if not pairs:
        sys.exit("No consecutive pairs found in the calibration range.  Did you recreate the view?")

    for idx, h0, h1 in pairs:
        x = hex_to_bytes(h0)          # plaintext (x)
        y = hex_to_bytes(h1)          # ciphertext (y) of the next half‑block
        b = blk(idx)

        occ = collections.defaultdict(int)
        for j, (xb, yb) in enumerate(zip(x, y)):
            lane = j % 16
            if lane not in LANES:
                continue
            o = occ[lane]; occ[lane] += 1
            drift = (yb - (A[lane] * xb & 0xFF)) & 0xFF
            cstar[b][lane].append(drift)

    # ---- 2‑a) sanity / graceful fallback ---------------------------------
    for b in (0,1):
        for lane in LANES:
            if len(cstar[b][lane]) == 0:
                # No data at all – this should never happen once the view is fixed.
                sys.exit(f"cstar completely missing for block {b} lane {lane}")
            if len(cstar[b][lane]) == 1:
                # Only one occurrence was seen (rare).  Duplicate it so the rest
                # of the code can assume two entries.
                cstar[b][lane].append(cstar[b][lane][0])
    return cstar

Cstar = build_cstar()

# --------------------------------------------------------------
# 3) (Optional) write the tables out for your later scripts
# --------------------------------------------------------------
out = {
    "A": A,
    "C": C,
    "Cstar": {b: dict(lane_map) for b, lane_map in Cstar.items()},
    "lanes": sorted(LANES)
}
with open("out/ladder_calib_29_70.json","w") as f:
    json.dump(out, f, indent=2)
print("✅ Calibration data written to out/ladder_calib_29_70.json")
