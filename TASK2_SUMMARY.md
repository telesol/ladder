# TASK 2: Offset Formula Verification - Summary Report

**Date**: 2025-12-21
**Status**: COMPLETED
**Result**: Mistral's formula REJECTED - Alternative patterns discovered

---

## Quick Summary

Mistral's proposed offset formula has been **empirically disproven**:

```
❌ REJECTED: offset[n] = (-1)^(n+1) × 2^f(n) × 5^g(n) × h(n)
where f(n) = floor(n/3) - 2, h(n) ∈ {17, 19}
```

**Verification scores**:
- f(n) = floor(n/3) - 2: **1.6% match** (1/61)
- Sign pattern (-1)^(n+1): **52.5% match** (random)
- Prime 17 hypothesis: **4.9% coverage** (too rare)
- Prime 19 hypothesis: **0% accuracy** (completely wrong)

---

## What We Computed

### All 61 offsets for n=10 to n=70

Using the verified relationship:
```
offset[n] = k[n] - 9 × k[n-3]
```

All offsets computed from database values and completely factorized.

### Key Statistics

| Metric | Value |
|--------|-------|
| Total offsets | 61 |
| Prime offsets | 3 (n=14, 21, 46) |
| Sign changes | 22 out of 60 transitions |
| Average growth rate | 5.43x per step |
| Most common prime | 2 (55.7%) |
| Second most common | 3 and 5 (32.8% each) |

---

## Key Discoveries

### 1. NO Simple Power-of-2 Formula

Powers of 2 in offset factorizations vary from 2^0 to 2^6 with **no pattern**.

Only n=10 matched the hypothesis f(n) = floor(n/3) - 2.

**Conclusion**: Power of 2 is NOT determined by a simple function of n.

### 2. Primes 17 and 19 Are RARE, Not Dominant

| Prime | Appearances | Percentage |
|-------|-------------|------------|
| 2 | 34/61 | 55.7% |
| 5 | 20/61 | 32.8% |
| 3 | 20/61 | 32.8% |
| 7 | 11/61 | 18.0% |
| 11 | 8/61 | 13.1% |
| 13 | 7/61 | 11.5% |
| **19** | **5/61** | **8.2%** |
| **17** | **3/61** | **4.9%** |

Mistral's hypothesis that 17/19 are the "characteristic primes" is **wrong**.

### 3. Prime 19 Selection Rule is Completely Wrong

Mistral claimed: "19 appears when n ≡ 2 (mod 6)"

**Reality**: Prime 19 appears at n = 12, 24, 29, 34, 60

| n | n mod 6 | Predicted? | Result |
|---|---------|------------|--------|
| 12 | 0 | No | Wrong |
| 24 | 0 | No | Wrong |
| 29 | 5 | No | Wrong |
| 34 | 4 | No | Wrong |
| 60 | 0 | No | Wrong |

**0/5 correct** - The hypothesis is completely false.

### 4. Power of 5 is Usually ZERO, Not One

Mistral claimed: "Power of 5 is usually 1"

**Reality**:
- 5^0: 67.2% (41/61 offsets)
- 5^1: 26.2% (16/61 offsets)
- 5^2: 6.6% (4/61 offsets)

Most offsets have **no factor of 5** at all.

### 5. Prime Offsets Exist

Three offsets are prime numbers themselves:
- offset[14] = 149
- offset[21] = 23743
- offset[46] = 15279629081813

This proves offset[n] **cannot** always be a product of small prime powers.

### 6. Large Prime Factors Are Common

Many offsets have very large prime factors (>10^12), indicating they are NOT constructed from small building blocks.

Examples:
- offset[58] = -7 × **10061692350069013**
- offset[65] = -227 × **20295046566106589**

---

## Alternative Patterns Discovered

### Pattern A: Divisibility by Small k Values

Some offsets are divisible by early k values:

| k[i] | Divides offset[n] for n = |
|------|---------------------------|
| k[2]=3 | 11, 16, 17, 18, 22, 27, 28, 36, 37, 39, ... |
| k[3]=7 | 11, 18, 20, 30, 34, 39, 58, 59, 61, 64, 70 |
| k[4]=8 | 12, 15, 22, 24, 29, 32, 38, 53, 55, 59 |
| k[5]=21 | 11, 18, 39, 64, 70 |
| k[7]=76 | 12, 24, 29 |

**Observation**: offset[n] often shares factors with k[i] for small i.

### Pattern B: No Correlation with m[n] × k[d[n]]

Tested hypothesis: offset[n] ≈ m[n] × k[d[n]]

**Result**: Ratios vary from 0.001 to 0.268 - no consistent relationship.

### Pattern C: Growth Rate is Chaotic

offset[n]/offset[n-1] varies wildly:
- Min: 0.009 (n=20)
- Max: 46.531 (n=18)
- Average: 5.43

No smooth growth pattern detected.

### Pattern D: Offset Ratios offset[n]/offset[n-3]

Average ratio: -39.98 (negative due to sign changes)

Extreme outliers:
- n=23: ratio = -2385.77 (huge spike)
- n=45: ratio = +333.99 (huge spike)

**Observation**: Offsets grow erratically, not smoothly.

---

## What Mistral Got Wrong

| Claim | Reality | Verdict |
|-------|---------|---------|
| f(n) = floor(n/3) - 2 | Only 1/61 match | ❌ WRONG |
| Power of 5 usually 1 | Usually 0 (67.2%) | ❌ WRONG |
| Sign follows (-1)^(n+1) | 52.5% match (random) | ❌ WRONG |
| Prime 17 for n ≡ 0,3,4 mod 6 | Only 4.9% coverage | ⚠️ INCOMPLETE |
| Prime 19 for n ≡ 2 mod 6 | 0% accuracy | ❌ COMPLETELY WRONG |
| Offsets have simple structure | Many large primes, prime offsets | ❌ WRONG |

**Overall Assessment**: Mistral's formula bears almost no resemblance to the actual offset data.

---

## Implications

### 1. Offsets Are NOT Independently Generated

The offset sequence does NOT follow a simple formula based on n alone.

### 2. Offsets Are Likely Emergent

Since k[n] = 2k[n-1] + adj[n] and k[n] = 9k[n-3] + offset[n], the offset is likely:

```
offset[n] = k[n] - 9k[n-3]
          = (2k[n-1] + adj[n]) - 9k[n-3]
          = 2k[n-1] + adj[n] - 9k[n-3]
```

So offset[n] is a **derived quantity**, not a primitive one.

### 3. The Mod-3 Structure is Fundamental

The fact that k[n] = 9k[n-3] + offset[n] works perfectly for n=10-70 means:

- The mod-3 recurrence is the PRIMARY structure
- Offsets are corrections to this recurrence
- Any formula for offset[n] must account for k[n-1], k[n-3], and adj[n]

---

## Recommended Next Steps

### HIGH PRIORITY

1. **Derive offset[n] from adj[n] sequence**
   - Test: offset[n] = f(adj[n], adj[n-1], adj[n-3], ...)
   - Look for recurrences in the offset sequence itself

2. **Investigate offset[n] mod 3 patterns**
   - Split offsets by n mod 3
   - Check if each subset has different structure

3. **Test secondary recurrences**
   - Can offset[n] = a×offset[n-1] + b×offset[n-2] + c×offset[n-3]?
   - Use linear regression on small ranges

### MEDIUM PRIORITY

4. **Cross-reference with d[n] sequence**
   - Does offset[n] depend on which k[d[n]] was used?
   - Group offsets by d[n] value

5. **Analyze offset[n] / k[n-6] ratios**
   - Pattern 4 showed some correlation
   - May reveal hidden relationship

6. **Test offset divisibility patterns**
   - Why do k[3], k[5], k[7] frequently divide offsets?
   - Is there a divisibility rule we can exploit?

### LOW PRIORITY

7. **Study the 3 prime offsets** (n=14, 21, 46)
   - What makes these special?
   - Do they mark transitions or anomalies?

8. **Search for continued fraction convergents in offsets**
   - Since m[n] uses convergents, maybe offset[n] does too?

---

## Files Generated

1. `/home/rkh/ladder/verify_offset_formula.py` - Main verification script
2. `/home/rkh/ladder/analyze_offset_patterns.py` - Extended pattern analysis
3. `/home/rkh/ladder/offset_formula_verified.md` - Detailed verification report
4. `/home/rkh/ladder/offset_verification_results.json` - JSON data export
5. `/home/rkh/ladder/offset_pattern_analysis.json` - Pattern analysis data
6. `/home/rkh/ladder/TASK2_SUMMARY.md` - This summary

---

## Conclusion

**Mistral's offset formula is empirically disproven.**

The offset sequence is far more complex than a simple product of prime powers. It appears to be an **emergent property** of the main recurrence relation k[n] = 2k[n-1] + adj[n], not an independently generated sequence.

**Next research direction**: Focus on deriving offset[n] from the adj[n] sequence and k[n-1], k[n-3] values, rather than searching for a formula based on n alone.

**NO ASSUMPTIONS MADE. ALL DATA DERIVED FROM DATABASE.**

---

*Report Completed: 2025-12-21*
*Total offsets analyzed: 61 (n=10 to n=70)*
*Source: /home/rkh/ladder/db/kh.db*
