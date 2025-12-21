# EC Ladder Deep Analysis

## Date: 2025-12-21
## Session: Dell + Local Models

---

## Key Discoveries

### 1. EC Point Construction Formula

```
P[n] = 2*P[n-1] + 2^n × G - m[n] × P[d[n]]
```

Each puzzle point P[n] is built from:
1. **Doubled previous point**: 2×P[n-1]
2. **Power-of-2 generator multiple**: 2^n × G
3. **Reference point multiple**: m[n] × P[d[n]]

### 2. Bridge Verification INCOMPLETE

We verified our formula for n=2-70 (100% match).
**BUT**: We CANNOT verify for bridges (75, 80, 85, 90) because:
- adj[n] = k[n] - 2*k[n-1] requires k[n-1]
- k[74], k[79], k[84], k[89] don't exist in the puzzle

**This is a fundamental gap in our verification!**

### 3. Position in Range Oscillates

| n | Position (0=min, 1=max) | Category |
|---|-------------------------|----------|
| 10 | 0.0039 | Very Low |
| 20 | 0.6466 | Mid-High |
| 30 | 0.9244 | Very High |
| 40 | 0.8256 | High |
| 50 | 0.0856 | Very Low |
| 60 | 0.9690 | Very High |
| 70 | 0.6440 | Mid-High |
| 75 | 0.1932 | Low |
| 80 | 0.8289 | High |
| 85 | 0.0903 | Very Low |
| 90 | 0.4023 | Mid |

Pattern: Position oscillates with ~30-40 step period!

### 4. DeepSeek's Exploration

DeepSeek explored whether k[n] = n × 2^n + c (constant).
Result: **c is NOT constant** - varies wildly.

Alternative: k[n] = 2^(n-1) + f(n) where f(n) is bounded.

### 5. Critical Questions

1. **How was k[75] generated without k[71-74]?**
   - The creator MUST have a direct formula
   - Our recursive formula is derived, not the source

2. **What determines the position oscillation?**
   - Is it related to m[n]?
   - Is it related to d[n]?
   - Is there a hidden period?

3. **What's the EC significance?**
   - P[n] construction uses P[d[n]] as reference
   - d[n] is usually small (1, 2, 3, 4)
   - The "ladder" always references back to base points

---

## The m[n] Lock

The m[n] sequence is the LOCK:
- Self-references: m[n] | m[n+m[n]] (57%)
- 17-network (Fermat prime)
- Convergent patterns (π, e, φ)

If we crack m[n], we crack everything:
```
k[n] = 2^n - m[n]*k[d[n]] + recursive_terms
```

---

## Files Related
- DIRECT_FORMULA_RESEARCH.md
- compute_gap_m_values.py
- adj_complete_table.txt
- experiments/06-pysr-m-sequence/

---

## NEW: 5-Step Gap Pattern Analysis (2025-12-21)

### 6. Gap Puzzle Offset Oscillation

The offsets k[n] - 32*k[n-5] for gap puzzles OSCILLATE between + and -:

| From | To | Offset / k[n-5] | Sign |
|------|-----|-----------------|------|
| k[70] | k[75] | -8.78 × k[70] | **-** |
| k[75] | k[80] | +17.05 × k[75] | **+** |
| k[80] | k[85] | -12.92 × k[80] | **-** |
| k[85] | k[90] | +9.16 × k[85] | **+** |

Pattern: **Alternating negative/positive**!

### 7. Autocorrelation Peaks

Position oscillation autocorrelation peaks at:
- **Lag 14**: -0.2804 (strongest, negative!)
- **Lag 3**: +0.2516 (positive)
- **Lag 31**: +0.2031 (positive)

The lag-14 peak suggests ~14-step quasi-period in positions.

### 8. d[n] Distribution

For n=2 to n=70:
- **d=1**: 43.5% (30 times) - self-referencing k[1]=1
- **d=2**: 29.0% (20 times) - using k[2]=3
- **d=3-8**: 27.5% (remaining)

The ladder heavily relies on k[1] and k[2] as reference points!

### 9. k[5n]/k[n] Ratio Pattern

| n | k[5n]/k[n] | log2 |
|---|------------|------|
| 1 | 21.0 | 4.39 |
| 2 | 171.3 | 7.42 |
| 3 | 3838.1 | 11.91 |
| 4 | 107914.6 | 16.72 |
| 5 | 1580262.3 | 20.59 |
| 8 | 4480586665.0 | 32.06 |
| 14 | 92036890554345952.0 | 56.35 |

Approximate pattern: log2(k[5n]/k[n]) ≈ 4n

---

## Next Steps
1. Find the period in position oscillation
2. Compute m[n] for bridges using constraints
3. Look for patterns in d[n] selection
4. Test if position oscillation correlates with m[n] properties
5. **NEW**: Investigate the alternating +/- offset pattern in gaps
6. **NEW**: Test if lag-14 quasi-period reveals formula structure
