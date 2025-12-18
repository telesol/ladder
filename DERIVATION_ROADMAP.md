# Formula Derivation Roadmap

## Status Summary

| Category | Count | Details |
|----------|-------|---------|
| Total puzzles | 160 | Bitcoin Puzzle Challenge |
| Known keys (in DB) | 74 | k1-k70, k75, k80, k85, k90 |
| Unknown keys | 86 | k71-k74, k76-k79, k81-k84, k86-k89, k91-k160 |
| Verified formulas | 13 | Proven against DB |
| Need formulas | 55 | k9, k10, k17, k19-k70 (excluding verified) |

## Verified Formulas (PROVEN)

```
k5  = k2 × k3           = 3 × 7 = 21
k6  = k3²               = 49
k7  = k2×9 + k6         = 27 + 49 = 76
k8  = k5×13 - k6        = 273 - 49 = 224
k8  = k4×k3×4           = 224 (alternate)
k11 = k6×19 + k8        = 931 + 224 = 1155
k12 = k8×12 - 5         = 2683
k13 = k10×10 + k7       = 5140 + 76 = 5216
k14 = k11×9 + 149       = 10544
k14 = k8×47 + 16        = 10544 (alternate)
k15 = k12×10 + 37       = 26867
k16 = k11×45 - 465      = 51510
k18 = k13×38 + 461      = 198669
```

## Pattern Analysis

### Multiplier Sequence
```
k7:  9   (from k2)
k8:  13  (from k5)
k11: 19  (from k6)
k12: 12  (from k8)
k13: 10  (from k10)
k14: 9   (from k11) ← 9 repeats
k15: 10  (from k12) ← 10 repeats
k16: 45  (from k11) ← jump!
k18: 38  (from k13)
```

### Base Key Selection
```
k7  uses k2  (gap: 5)
k8  uses k5  (gap: 3)
k11 uses k6  (gap: 5)
k12 uses k8  (gap: 4)
k13 uses k10 (gap: 3)
k14 uses k11 (gap: 3)
k15 uses k12 (gap: 3)
k16 uses k11 (gap: 5)
k18 uses k13 (gap: 5)
```

## Phase 1: Immediate Tasks

### Task 1.1: Derive k9 and k10
- k9 = 467, k10 = 514
- Find formula in terms of k1-k8
- Test all combinations: products, squares, linear

### Task 1.2: Derive k17
- k17 = 95823
- No simple formula found yet
- Test against k1-k16

### Task 1.3: Derive k19, k20
- k19 = 357535
- k20 = 863317
- Look for pattern continuation

## Phase 2: Pattern Discovery

### Task 2.1: Multiplier Meta-Formula
- Why [9, 13, 19, 12, 10, 9, 10, 45, 38]?
- Is multiplier related to key index?
- Is multiplier related to previous keys?

### Task 2.2: Offset Meta-Formula
- Offsets: [+49, -49, +224, -5, +76, +149, +37, -465, +461]
- Pattern in offsets?
- Related to other keys?

### Task 2.3: Base Key Selection Rule
- Gaps: [5, 3, 5, 4, 3, 3, 3, 5, 5]
- Is there a rule for which key to use as base?

## Phase 3: Extend to All Keys

### Task 3.1: Derive k21-k35
- Medium-sized keys
- Test if pattern holds

### Task 3.2: Derive k36-k50
- Larger keys
- Numerical precision matters

### Task 3.3: Derive k51-k70
- Large keys (50+ bits)
- Test against bridge keys

## Phase 4: Validate with Bridge Keys

### Task 4.1: Test formulas on k75, k80, k85, k90
- If formulas work on k66-k70, do they work on bridges?
- Can we derive k71 from k70?

## Success Criteria

A formula is VERIFIED if:
1. It produces the EXACT value in the database
2. It uses only previously known keys
3. The mathematical steps are explicit
4. It can be independently verified

## Data Access

```bash
# Query any key from database
sqlite3 db/kh.db "SELECT puzzle_id, priv_hex FROM keys WHERE puzzle_id = N;"

# Convert hex to decimal
python3 -c "print(int('0xHEX', 16))"

# Run derivation script
python derive_formula.py --test N
```
