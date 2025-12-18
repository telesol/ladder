# Bitcoin Puzzle Formula Exploration Plan

## Overview
**Goal:** Systematically explore ~175K formula theories to find the key generation pattern
**Split:** B-Solver (phi4) ~88K theories, C-Solver (qwq) ~88K theories

## Target Keys
- k9 = 467 (unknown formula)
- k10 = 514 (unknown formula)
- k12 = 2683 (unknown formula)
- k14 = 10544 (unknown formula)

## Known Keys (for reference)
```
k1=1, k2=3, k3=7, k4=8, k5=21, k6=49, k7=76, k8=224
k9=467, k10=514, k11=1155, k12=2683, k13=5216, k14=10544
```

## Verified Formulas (CONFIRMED)
- k5 = k2 × k3 = 3 × 7 = 21
- k6 = k3² = 7² = 49
- k7 = k2 × 9 + k6 = 27 + 49 = 76
- k8 = k5 × 13 - k6 = 273 - 49 = 224
- k11 = k6 × 19 + k8 = 931 + 224 = 1155
- k13 = 5216 (formula to be determined)

## Search Parameters

### Keys to Use as Bases
- k2=3, k3=7, k4=8, k5=21, k6=49, k7=76, k8=224, k9=467

### Multipliers
- Range: 1 to 25 (25 values)

### Constants
- Range: -50 to 100 (151 values)

## Formula Types to Explore

### Type A: Single-key Linear (k_a × M + C)
- 8 keys × 25 multipliers × 151 constants = 30,200 combinations per target

### Type B: Two-key Addition (k_a × M + k_b)
- 8 × 7 key pairs × 25 multipliers = 1,400 combinations per target

### Type C: Two-key Subtraction (k_a × M - k_b)
- 8 × 7 key pairs × 25 multipliers = 1,400 combinations per target

### Type D: Square ± Constant (k_a² ± C)
- 8 keys × 151 constants × 2 = 2,416 combinations per target

### Type E: Product ± Constant (k_a × k_b ± C)
- 28 unique pairs × 151 constants × 2 = 8,456 combinations per target

## Totals
- **Per target key:** 43,872 combinations
- **For 4 targets:** 175,488 combinations
- **Per model:** 87,744 combinations

---

## Work Split

### B-Solver (phi4-reasoning:14b) - 87,744 theories
Assignment: **k9 and k10** (all formula types)

#### k9 = 467
| Type | Count |
|------|-------|
| A. k_a × M + C | 30,200 |
| B. k_a × M + k_b | 1,400 |
| C. k_a × M - k_b | 1,400 |
| D. k_a² ± C | 2,416 |
| E. k_a × k_b ± C | 8,456 |
| **Subtotal** | **43,872** |

#### k10 = 514
Same breakdown: **43,872**

**B-Solver Total: 87,744**

---

### C-Solver (qwq:32b) - 87,744 theories
Assignment: **k12 and k14** (all formula types)

#### k12 = 2683
| Type | Count |
|------|-------|
| A. k_a × M + C | 30,200 |
| B. k_a × M + k_b | 1,400 |
| C. k_a × M - k_b | 1,400 |
| D. k_a² ± C | 2,416 |
| E. k_a × k_b ± C | 8,456 |
| **Subtotal** | **43,872** |

#### k14 = 10544
Same breakdown: **43,872**

**C-Solver Total: 87,744**

---

## Execution Strategy

### Batch Processing
- Process 1000 formulas per batch
- Report matches immediately
- Save progress every 10 batches
- Estimated runtime: ~24 hours per model

### Output Format
For each formula found:
```json
{
  "target_key": "k9",
  "target_value": 467,
  "formula_type": "A",
  "formula": "k8 × 2 + 19",
  "components": {"base_key": "k8", "multiplier": 2, "constant": 19},
  "verification": "224 × 2 + 19 = 467",
  "valid": true
}
```

### Success Criteria
A formula is "interesting" if:
1. It exactly produces the target value
2. Uses small multipliers (< 25)
3. Uses constants that appear in other formulas (9, 11, 13, 19, etc.)
4. Shows a pattern consistent with other known formulas

---

## Already Found Candidates (from iterative exploration)

### k9 = 467
- k8 × 2 + 19 = 448 + 19 = 467 ✓
- k7 × 6 + 11 = 456 + 11 = 467 ✓
- k6 × 9 + 26 = 441 + 26 = 467 ✓
- k5 × 22 + 5 = 462 + 5 = 467 ✓

### k10 = 514
- k8 × 2 + 66 = 448 + 66 = 514 ✓
- k7 × 6 + 58 = 456 + 58 = 514 ✓
- k4 × 63 + 10 = 504 + 10 = 514 ✓

### Still Needed
- k12 = 2683: NO FORMULA YET
- k14 = 10544: NO FORMULA YET

---

## Priority Order

1. **HIGH:** Find formulas for k12=2683 and k14=10544
2. **MEDIUM:** Verify pattern consistency across all formulas
3. **LOW:** Explore alternative formulas for k9, k10

## Database Schema

```sql
CREATE TABLE formula_theories (
    id INTEGER PRIMARY KEY,
    target_key TEXT,
    target_value INTEGER,
    formula_type TEXT,
    formula_string TEXT,
    base_key TEXT,
    base_value INTEGER,
    multiplier INTEGER,
    second_key TEXT,
    second_value INTEGER,
    constant INTEGER,
    computed_value INTEGER,
    is_valid BOOLEAN,
    explored_by TEXT,  -- 'b-solver' or 'c-solver'
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## Progress Tracking

| Target | Model | Status | Valid Formulas |
|--------|-------|--------|----------------|
| k9=467 | B-Solver | COMPLETE | 17 formulas |
| k10=514 | B-Solver | COMPLETE | 17 formulas |
| k12=2683 | C-Solver | COMPLETE | 1 formula |
| k14=10544 | C-Solver | COMPLETE | 6 formulas |

---

## COMPLETE FORMULA CATALOG

### k9 = 467 (17 valid formulas)
**Best formulas (smallest constants):**
- `k7 × 6 + 11 = 456 + 11 = 467` (uses prime 11)
- `k8 × 2 + 19 = 448 + 19 = 467` (uses prime 19)
- `k5² + 26 = 441 + 26 = 467`
- `k5 × 22 + 5 = 462 + 5 = 467`
- `k6 × 9 + 26 = 441 + 26 = 467`

### k10 = 514 (17 valid formulas)
**Best formulas:**
- `k3 × k7 - 18 = 532 - 18 = 514` (product formula)
- `k7 × 7 - 18 = 532 - 18 = 514`
- `k5 × 24 + 10 = 504 + 10 = 514`
- `k6 × 10 + 24 = 490 + 24 = 514`
- `k8 × 2 + 66 = 448 + 66 = 514`

### k12 = 2683 (1 valid formula)
**THE formula:**
- `k8 × 12 - 5 = 2688 - 5 = 2683`

### k14 = 10544 (6 valid formulas)
**Best formulas:**
- `k11 × 9 + 149 = 10395 + 149 = 10544` (uses constant 9!)
- `k12 × 4 - 188 = 10732 - 188 = 10544`
- `k8 × 47 + 16 = 10528 + 16 = 10544`
- `k5 × k10 - 250 = 10794 - 250 = 10544` (product formula)
- `k6 × k8 - 432 = 10976 - 432 = 10544` (product formula)
- `k9 × 23 - 197 = 10741 - 197 = 10544`

---

## KEY PATTERN OBSERVATIONS

1. **Constant 9 appears in multiple formulas:**
   - k7 = k2×9 + k6 (known)
   - k14 = k11×9 + 149
   - k9 = k6×9 + 26

2. **Primes 11 and 19 are special:**
   - k9 = k7×6 + 11
   - k9 = k8×2 + 19

3. **Product formulas exist:**
   - k10 = k3×k7 - 18
   - k14 = k5×k10 - 250
   - k14 = k6×k8 - 432

4. **k12 is unique - only ONE formula works!**
   - k12 = k8×12 - 5

---

## k15 CANDIDATE FORMULAS (Local AI Analysis)

**k15 range: [16384, 32767] (15-bit)**

### Valid Formulas Calculated:

| Formula | Calculation | Result | In Range? |
|---------|-------------|--------|-----------|
| k7 × k8 | 76 × 224 | **17024** | ✓ PRODUCT |
| k14 × 2 | 10544 × 2 | 21088 | ✓ |
| k13 × 3 | 5216 × 3 | 17295 | ✓ |
| k12 × 6 | 2683 × 6 | 16098 | ✓ |
| k11 × 15 | 1155 × 15 | 17325 | ✓ |
| k9 × 35 | 467 × 35 | 16345 | ✓ |
| k10 × 32 | 514 × 32 | 16448 | ✓ |
| k7² | 76² | 5776 | ✗ Too small |
| k8² | 224² | 50176 | ✗ Too big |

### Most Promising k15 Candidates:
1. **k15 = k7 × k8 = 17024** (product formula like k5=k2×k3)
2. **k15 = k13 × 3 = 17295** (linear formula)
3. **k15 = k11 × 15 = 17325** (linear formula)

---

## META-FORMULA HYPOTHESIS (from Local AI)

**Pattern:** Each key is built from earlier keys by multiplying + offset

**Multiplier Cycle:** [9, 13, 19, 12] (repeating)
**Offset Cycle:** [2, 5, 8, 0] (differences: +3, +3, -8)

**Proposed Meta-Formula:**
```
term_n = term_{n-1} × M(n) + C(n)
where M cycles through [9, 13, 19, 12]
      C cycles through [2, 5, 8, 0]
```

**Key Insight:** The multiplier "9" appears twice (k7 and k14), suggesting a cycle.

---

*Updated: 2025-12-11 09:45 UTC*
*C-Solver (qwq:32b) analysis: 1513s*
*B-Solver (phi4-reasoning:14b) analysis: 695s*
*Database: /home/solo/LA/formula_theories.db*
