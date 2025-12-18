#!/usr/bin/env python3
# verify_affine.py
# -------------------------------------------------------------
#  Forward and reverse verification using the full per‑occurrence drifts.
#  Range is now determined dynamically from the database.
# -------------------------------------------------------------

import sqlite3, json, csv, os, sys, collections, math
import argparse

DB          = "db/kh.db"
CALIB_JSON  = "out/ladder_calib_29_70_full.json"

# Parse command-line arguments for flexible range
parser = argparse.ArgumentParser(description='Verify affine recurrence model')
parser.add_argument('--start', type=int, default=None, help='Start puzzle number')
parser.add_argument('--end', type=int, default=None, help='End puzzle number')
parser.add_argument('--db', type=str, default=DB, help='Database path')
parser.add_argument('--calib', type=str, default=CALIB_JSON, help='Calibration JSON path')
args = parser.parse_args()

DB = args.db
CALIB_JSON = args.calib

# Get dynamic range from database if not specified
def get_consecutive_range():
    """Find the consecutive puzzle range in the database"""
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("SELECT bits FROM lcg_residuals ORDER BY bits")
    all_bits = [row[0] for row in cur.fetchall()]
    con.close()

    if not all_bits:
        return 1, 70  # Fallback

    # Find consecutive range
    consecutive_end = all_bits[0]
    for i, b in enumerate(all_bits):
        if i > 0 and b != all_bits[i-1] + 1:
            break
        consecutive_end = b

    return all_bits[0], consecutive_end

# Set LOW/HIGH dynamically
if args.start is not None and args.end is not None:
    LOW, HIGH = args.start, args.end
else:
    LOW, HIGH = get_consecutive_range()
    print(f"📊 Using dynamic range from database: {LOW}-{HIGH}")

LANES = list(range(16))
blk = lambda i: (i - LOW) // 32  # Use LOW as base for block calculation

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
    occ = 0 if ((i - LOW) % 32) < 16 else 1   # 0 = first half, 1 = second half

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
