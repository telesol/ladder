# Direct Formula Research - k[n] = f(n)

## Date: 2025-12-21

## Critical Insight

The gap puzzles (k[75], k[80], k[85], k[90]) **PROVE** a direct formula exists.
The creator generated k[75] WITHOUT k[71-74].

This means: **k[n] = f(n)** for some function f that takes only n as input.

## Data Points

### Known Ratios
| From | To | Ratio | Per-step | Expected (2^5) |
|------|-----|-------|----------|----------------|
| k[70] | k[75] | 23.23 | 1.88 | 32 |
| k[75] | k[80] | 49.05 | 2.18 | 32 |
| k[80] | k[85] | 19.08 | 1.80 | 32 |
| k[85] | k[90] | 41.16 | 2.05 | 32 |

The ratios OSCILLATE around 32, not constant.

### Gap Structure
- Gaps at n = 75, 80, 85, 90 (5-step intervals)
- 75 = 3 × 5²
- 80 = 2⁴ × 5
- 85 = 17 × 5 (17 is Fermat prime F₂!)
- 90 = 2 × 3² × 5

## Model Responses

### DeepSeek V3.1 Analysis (partial - timed out)
- Growth rate ~1.4 to 2.2 per step (not constant)
- Not pure exponential (g^n doesn't fit)
- Modular arithmetic unlikely (k[n] grows, no periodicity)
- Considered: polynomial, exponential with variability

### Qwen 2.5 Coder Analysis
Suggested formula structure:

```
k[n] = 2^(n-1) + f(n) × g(n)
```

Where:
- 2^(n-1) ensures bit_length = n constraint
- f(n), g(n) introduce oscillating variability

Possible forms:
1. **Polynomial**: k[n] = 2^(n-1) + p(n) × q(n)
2. **Trigonometric**: k[n] = 2^(n-1) + A × sin(Bn + C) + D
3. **Piecewise**: Different functions for different n ranges

### Approach Suggested
1. Start with base: k[n] = 2^(n-1) + f(n)
2. Fit f(n) using known data points
3. Consider piecewise functions at gap boundaries
4. Test and validate against all 74 known keys

## Key Questions

1. What determines f(n)?
   - Is it related to m[n]?
   - Is it related to number-theoretic properties of n?

2. Why 5-step gaps?
   - All gap positions are multiples of 5
   - 85 = 17 × 5 (Fermat prime connection)

3. How does m[n] relate to direct formula?
   - m[n] = (2^n - adj[n]) / k[d[n]]
   - If we can express m[n] directly, we solve everything

## Research Direction

**DON'T**: Try to predict/guess k[71]
**DO**: Reverse-engineer f(n) from the 74 known data points

The formula exists. We need to find it.

## Files Related
- gap_puzzle_analysis output (above)
- adj_complete_table.txt
- experiments/06-pysr-m-sequence/

## Next Steps
1. Calculate m[75], m[80], m[85], m[90] if possible
2. Look for f(n) patterns in the gap data
3. Test trigonometric/polynomial fits
4. Check if 5-step structure reveals hidden periodicity
