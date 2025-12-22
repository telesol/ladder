# 1‑Progress.md  (updated 2025‑09‑22)

## ✅  What we have accomplished so far

| Action | Command we ran | Result |
|--------|----------------|--------|
| **Export bridge half‑blocks** (first 32 hex chars) | `export HEX75=$(awk -F, '$1==75 {print substr($4,1,32)}' data/btc_puzzle_1_160_full.csv)`<br>`export HEX80=$(awk -F, '$1==80 {print substr($4,1,32)}' data/btc_puzzle_1_160_full.csv)` | `HEX75 length 32` <br> `HEX80 length 32` |
| **Compute drift `C0`** | (Python one‑liner) | `✅ missing_c0.json written` |
| **Patch calibration JSON** | `python3 tools/patch_cstar_from_bridge_pair.py --calib out/ladder_calib_29_70_full.json --drift missing_c0.json --block 0 --occ 0` | `✅ Cstar patched – block‑0 occ 1 and block‑1 occ 0 now contain the correct drifts.` |
| **Inspect DB contents** | `sqlite3 db/kh.db "SELECT bits FROM lcg_residuals WHERE bits BETWEEN 1 AND 130 ORDER BY bits;"` | Bits **29‑70** and the bridge rows **75, 80, 85,…, 130** are present. Bits **1‑28** and all the intermediate gaps (71‑74, 76‑79, … 126‑129) are still missing. |
| **Run verification** | `python verify_affine.py` | Forward = 95.833 % (736/768) <br> Reverse = 94.922 % (729/768) <br> Mismatches written to `out/ladder_mismatch_log.csv`. |

The percentages are low because the verification script tries to compare **every consecutive pair** of half‑blocks.  
*All rows that are absent from the database are automatically counted as mismatches.*  
Hence the only thing left is to **populate the missing rows**.

---

## 📂  What the missing rows are

Running the “missing‑bits” query:

```bash
sqlite3 db/kh.db "
SELECT bits
FROM   lcg_residuals
WHERE  bits BETWEEN 1 AND 130
ORDER BY bits;
"
