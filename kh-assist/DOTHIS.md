## One‑shot checklist  
(Everything you can copy‑paste into a **single Markdown file** and run step‑by‑step)

---  

### 0️⃣  Prepare a clean workspace  

```bash
# make sure you are in the repository root
cd ~/Labz/kh-assis

# 0‑clear the table (removes any “wrong” rows)
sqlite3 db/kh.db "DELETE FROM lcg_residuals;"
```

---

### 1️⃣  Find the column that really contains the 32‑hex **half‑block**  

```bash
# show the first data line with column numbers
awk -F, 'NR==1{for(i=1;i<=NF;i++) printf "%2d:%s ",i,$i; print ""}' data/btc_puzzle_1_160_full.csv | head -n 1
awk -F, 'NR==2{for(i=1;i<=NF;i++) printf "%2d:%s ",i,$i; print ""}' data/btc_puzzle_1_160_full.csv | head -n 1
```

*Look at the output.*  
One of the columns will be a **32‑character** hex string (optionally prefixed with `0x`).  
Write down its **0‑based index** (e.g. if it is the 5th column → `index = 4`).  
If you are not sure, note the index you see and we’ll use it.

---

### 2️⃣  Re‑import the rows **with the key in the *right* half**  

Create (or edit) a tiny Python script – **only the two lines marked “CHANGE HERE” need editing**.

```bash
cat > reimport_ladder_fixed.py <<'PY'
#!/usr/bin/env python3
import csv, sqlite3, sys
from pathlib import Path

DB_PATH   = Path("db/kh.db")
CSV_PATH  = Path("data/btc_puzzle_1_160_full.csv")
BLOCK_ID  = 68
ZERO_RHS  = "0" * 32               # 16‑byte zero padding (32 hex chars)

# --------------------------------------------------------------
#  👉  CHANGE HERE – set to the column you discovered in step 1
# --------------------------------------------------------------
HALF_BLOCK_COL = 4      # <-- example: column 5 (0‑based index = 4)

# --------------------------------------------------------------
def is_hex32(s: str) -> bool:
    s = s.lower().removeprefix("0x")
    return len(s) == 32 and all(c in "0123456789abcdef" for c in s)

# --------------------------------------------------------------
def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS lcg_residuals (
                       block_id INTEGER NOT NULL,
                       bits     INTEGER NOT NULL,
                       actual_hex TEXT NOT NULL,
                       ok       INTEGER NOT NULL,
                       PRIMARY KEY (block_id,bits)
                   );""")
    cur.execute("DELETE FROM lcg_residuals;")   # just in case

    with CSV_PATH.open(newline="") as f:
        rdr = csv.reader(f)
        next(rdr)                     # skip header
        for line_no, row in enumerate(rdr, start=2):
            if not row: continue
            try:
                bits = int(row[0])
            except ValueError:
                print(f"⚠️  line {line_no}: bad bits → {row[0]}", file=sys.stderr)
                continue

            # --------‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑
            #  CHANGE HERE – take the column that holds the 32‑hex half‑block
            # -------------------------------------------------------------------------------
            raw = row[HALF_BLOCK_COL].strip()
            # -------------------------------------------------------------------------------
            if not is_hex32(raw):
                print(f"ℹ️  line {line_no} (bits {bits}) – no 32‑hex block, skipping.", file=sys.stderr)
                continue

            half = raw.lower().removeprefix("0x")      # the key, already little‑endian
            # left‑half = zeros, right‑half = key
            actual_hex = f"0x{ZERO_RHS}{half}"

            cur.execute(
                "INSERT OR REPLACE INTO lcg_residuals (block_id,bits,actual_hex,ok) "
                "VALUES (?,?,?,-1);",
                (BLOCK_ID, bits, actual_hex)
            )

    conn.commit()
    conn.close()
    print("\n✅  Import finished – rows 1‑130 stored as 0x<zeros><key>.\n")

if __name__ == "__main__":
    main()
PY
chmod +x reimport_ladder_fixed.py
```

**Run it**

```bash
./reimport_ladder_fixed.py
```

You should see only a few “skipping” messages for bits 71‑130 (those rows are
expected to be generated later).  

---

### 3️⃣  Patch the drift vector (Cstar) – it is a constant `[0,…,0,2]`

```bash
jq '
  .Cstar = {"0":{"0":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2]}}
' out/ladder_calib_1_70_full.json > tmp.json && mv tmp.json out/ladder_calib_1_70_full.json
```

---

### 4️⃣  Verify the **first 70 rows** (forward + reverse must be 100 %)

```bash
python3 verify_affine.py \
  --db db/kh.db \
  --calib out/ladder_calib_1_70_full.json \
  --start 1 --end 70
```

**What you must see**

```
=== Forward test === 70/70 = 100.000%
=== Reverse test === 70/70 = 100.000%
```

If you see any other percentage, run:

```bash
wc -l out/ladder_mismatch_log.csv
head -n 20 out/ladder_mismatch_log.csv
```

and paste the output – that tells us exactly which bits are still off.

---

### 5️⃣  (Optional) Generate rows 71‑130  

Only needed if you need the full ladder later:

```bash
chmod +x extend_to_130.py   # first time only
./extend_to_130.py
```

---

### 6️⃣  Verify the **whole ladder** (1‑130)

```bash
python3 verify_affine.py \
  --db db/kh.db \
  --calib out/ladder_calib_1_70_full.json \
  --start 1 --end 130
```

Again you should obtain **100 %** forward and reverse.  

---

## What to give me after each stage  

| Stage | What to copy‑paste into the chat |
|------|-----------------------------------|
| 1️⃣  (column index) | The index you found (e.g. `HALF_BLOCK_COL = 4`). |
| 2️⃣  (import) | The *exact* terminal output of `./reimport_ladder_fixed.py`. |
| 4️⃣  (verification) | The whole output of `python3 verify_affine.py …`. If it is **not** 100 %, also paste the `out/ladder_mismatch_log.csv` snippet. |
| 6️⃣  (full verify) | The final output of the 1‑130 verification. |

If each step matches the expected result, the ladder is done – no more loops, no more guessing.  

**That is all the work you need to do.** Follow the numbered items in order, copy the results back here, and we’ll stop as soon as the verifier reports 100 %. Good luck! 🚀
