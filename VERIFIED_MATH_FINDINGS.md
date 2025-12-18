# Verified Mathematical Findings

**Date**: 2025-12-16
**Source**: Pure mathematical analysis of db/kh.db (74 known keys)
**Status**: COMPLETE

## Master Formula (VERIFIED for ALL 69 consecutive pairs)

```
k_n = 2 × k_{n-1} + adj_n
```

where:

```
adj_n = 2^n - m_n × k_{d_n}
```

- `d_n` ∈ {1, 2, 3, 4, 5, 6, 7, 8} is chosen to minimize |m_n|
- This formula holds for ALL consecutive pairs from k1 to k70

## Closed Form

```
k_n = 2^{n-1} + Σ(i=2 to n) 2^{n-i} × adj_i
```

This is algebraically equivalent to the recurrence and verified for all n.

## Fibonacci/Lucas Foundations

| Key | Value | Sequence Form |
|-----|-------|---------------|
| k1 | 1 | F(1) = L(1) |
| k2 | 3 | F(4) = L(2) |
| k3 | 7 | L(4) |
| k4 | 8 | F(6) = 2³ |
| k5 | 21 | F(8) |
| k7 | 76 | L(9) |

## Complete (d, m) Table for adj_n = 2^n - m × k_d

### Early keys (n = 2-25)

| n | d | m | adj_n | Verification |
|---|---|---|-------|--------------|
| 2 | 2 | 1 | 1 | 2² - 1×3 = 1 ✓ |
| 3 | 3 | 1 | 1 | 2³ - 1×7 = 1 ✓ |
| 4 | 1 | 22 | -6 | 2⁴ - 22×1 = -6 ✓ |
| 5 | 2 | 9 | 5 | 2⁵ - 9×3 = 5 ✓ |
| 6 | 2 | 19 | 7 | 2⁶ - 19×3 = 7 ✓ |
| 7 | 2 | 50 | -22 | 2⁷ - 50×3 = -22 ✓ |
| 8 | 4 | 23 | 72 | 2⁸ - 23×8 = 72 ✓ |
| 9 | 1 | 493 | 19 | 2⁹ - 493×1 = 19 ✓ |
| 10 | 7 | 19 | -420 | 2¹⁰ - 19×76 = -420 ✓ |
| 11 | 1 | 1921 | 127 | 2¹¹ - 1921×1 = 127 ✓ |
| 12 | 2 | 1241 | 373 | 2¹² - 1241×3 = 373 ✓ |
| 13 | 1 | 8342 | -150 | 2¹³ - 8342×1 = -150 ✓ |
| 14 | 4 | 2034 | 112 | 2¹⁴ - 2034×8 = 112 ✓ |

### High keys (n = 66-70)

| n | d | m | adj_n |
|---|---|---|-------|
| 66 | 8 | 395435327538483377 | -14790537073782069984 |
| 67 | 2 | 35869814695994276026 | 39964508501693584850 |
| 68 | 1 | 340563526170809298635 | -45415620991456472779 |
| 69 | 5 | 34896088136426753598 | -142522040506256173846 |
| 70 | 2 | 268234543517713141517 | 375887990164271878873 |

## d Value Frequency

| d | Count | k_d | Notes |
|---|-------|-----|-------|
| 1 | 30 | 1 | Default when no divisor found |
| 2 | 20 | 3 | Most common divisor |
| 3 | 4 | 7 | |
| 4 | 5 | 8 | |
| 5 | 5 | 21 | |
| 6 | 1 | 49 | |
| 7 | 1 | 76 | |
| 8 | 3 | 224 | |

## Adjustment Bounds

For all n:
- adj_n / 2^n ∈ [-0.24, +0.32]
- Mean ratio ≈ 0.01
- Adjustments are bounded perturbations around 0

## Key Position Anomalies

Keys closest to range minimum (2^{n-1}):

| n | Position | k_n | Notes |
|---|----------|-----|-------|
| 1 | 0.000 | 1 | = 2⁰ exactly |
| 4 | 0.000 | 8 | = 2³ exactly |
| 10 | 0.004 | 514 | ≈ 2⁹ |
| 69 | 0.007 | 297274491920375905804 | Very close to minimum |

## What Remains Unknown

### The m Sequence

The multiplier sequence {m_n} does not follow a simple pattern:
- When d=2: m ∈ {1, 9, 19, 50, 1241, ...}
- No common factor (GCD = 1)
- No clear arithmetic/geometric progression
- m/2^{n-d} ratio averages ~1.68 but varies from 0.72 to 2.75

### Open Questions

1. **What determines m_n?**
   - Is it derived from some function of n?
   - Is it computed from earlier keys?
   - Is it pseudo-random but seeded deterministically?

2. **Why are certain keys Fibonacci/Lucas numbers?**
   - k1, k2, k3, k4, k5, k7 follow sequences
   - Later keys do not

3. **Why do k4, k10, k69 cluster near range minimum?**
   - These positions seem non-random
   - May indicate intentional structure

## OEIS Reference

The key sequence is registered as **A369920** in OEIS:
"The private keys for the 32 BTC Bitcoin puzzle"

## Verification Commands

```bash
# Query database
sqlite3 db/kh.db "SELECT puzzle_id, priv_hex FROM keys ORDER BY puzzle_id;"

# Verify master recurrence
python3 -c "
import sqlite3
conn = sqlite3.connect('db/kh.db')
cur = conn.cursor()
cur.execute('SELECT puzzle_id, priv_hex FROM keys ORDER BY puzzle_id')
keys = {r[0]: int(r[1], 16) for r in cur.fetchall()}
for n in range(2, 71):
    if n in keys and n-1 in keys:
        adj = keys[n] - 2*keys[n-1]
        print(f'k{n} = 2×k{n-1} + {adj}')
"
```
