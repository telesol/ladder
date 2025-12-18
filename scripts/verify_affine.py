#!/usr/bin/env python3
# verify_affine.py
# -------------------------------------------------------------
#  Forward and reverse verification using the full per‑occurrence drifts.
# -------------------------------------------------------------

import sqlite3, json, csv, os, sys, collections, math

DB          = "db/kh.db"
CALIB_JSON  = "out/ladder_calib_29_70_full.json"
LOW, HIGH   = 45, 68                       # any sub‑range inside 29‑70

LANES = list(range(16))
blk = lambda i: (i - 29) // 32

def hex_to_bytes(h):
    h = h.rjust(64, '0')
    return [int(h[i:i+2], 16) for i in range(0, 64, 2)]

def solve_noninvertible(y, lane, occ, block, A, Cstar):
    a = A[lane]
    c = Cstar[block][lane][occ]
    rhs = (y - c) & 0xFF
    g = math.gcd(a, 256)          # =2 for lanes 9,13
    mod = 256 // g                # =128
    inv_a = pow(a // g, -1, mod)
    base = (inv_a * ((rhs // g) % mod)) % mod
    cand0 = base
    cand1 = (base + mod) & 0xFF
    return cand0 if cand0 <= 0x7F else cand1

# -----------------------------------------------------------------
# 1. Load calibration (full drift lists)
# -----------------------------------------------------------------
if not os.path.exists(CALIB_JSON):
    sys.exit(f"❌ {CALIB_JSON} not found – run rebuild_full_cstar_from_raw.py first.")
cfg   = json.load(open(CALIB_JSON))
A = {int(k): int(v) for k, v in cfg["A"].items()}
Cstar = {int(b): {int(l): v for l, v in lane_map.items()}
         for b, lane_map in cfg["Cstar"].items()}

# -----------------------------------------------------------------
# 2. Pull needed half‑blocks (bits LOW … HIGH+1)
# -----------------------------------------------------------------
con = sqlite3.connect(DB)
cur = con.cursor()
cur.execute("""
    SELECT bits, lower(substr(actual_hex,3)) AS hex
    FROM   lcg_residuals
    WHERE  bits BETWEEN ? AND ?
    ORDER BY bits;
""", (LOW, HIGH+1))
rows = cur.fetchall()
if not rows:
    sys.exit("❌ No rows in the selected range.")
data = {bits: hex_to_bytes(hex_str) for bits, hex_str in rows}

# -----------------------------------------------------------------
# 3. Forward & reverse tests (occurrence is just first/second half)
# -----------------------------------------------------------------
forward_ok = reverse_ok = 0
total = 0
mismatches = []

for i in range(LOW, HIGH+1):
    x = data[i]
    y = data[i+1]
    b = blk(i)

    # ----- occurrence (first half / second half of the current 32‑half‑block) -----
    occ = 0 if ((i - 29) % 32) < 16 else 1   # 0 = first half, 1 = second half

    # ----- forward prediction -----
    y_hat = [(A[pos % 16] * xb + Cstar[b][pos % 16][occ]) & 0xFF
             for pos, xb in enumerate(x)]

    # ----- reverse prediction -----
    x_hat = []
    for pos, yb in enumerate(y):
        lane = pos % 16
        if math.gcd(A[lane], 256) == 1:               # invertible
            inv = pow(A[lane], -1, 256)
            x_hat.append((inv * ((yb - Cstar[b][lane][occ]) & 0xFF)) & 0xFF)
        else:                                          # lanes 9,13
            x_hat.append(solve_noninvertible(yb, lane, occ, b, A, Cstar))

    # ----- count matches ----------
    for pos in range(32):
        total += 1
        if y_hat[pos] == y[pos]:
            forward_ok += 1
        else:
            mismatches.append(("fwd", i, pos, y_hat[pos], y[pos]))
        if x_hat[pos] == x[pos]:
            reverse_ok += 1
        else:
            mismatches.append(("rev", i, pos, x_hat[pos], x[pos]))

print("\n=== Forward test ===")
print(f"  {forward_ok}/{total} = {forward_ok/total:.3%}")
print("\n=== Reverse test ===")
print(f"  {reverse_ok}/{total} = {reverse_ok/total:.3%}")

if mismatches:
    csv_path = "out/ladder_mismatch_log.csv"
    with open(csv_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["direction","idx","byte_pos","predicted","actual"])
        w.writerows(mismatches)
    print(f"📊 Mismatches written to {csv_path}")
else:
    print("🎉 No mismatches – the affine model reproduces the data perfectly!")
