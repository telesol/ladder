# Bitcoin Puzzle Mathematics - Complete Reference

## 1. Fundamental Concepts

### 1.1 Key Range Formula

For puzzle number N, the private key k_N must satisfy:

```
k_N ∈ [2^(N-1), 2^N - 1]
```

This means k_N is an N-bit number with the most significant bit set to 1.

| Puzzle | Range Low | Range High | Search Space |
|--------|-----------|------------|--------------|
| 5 | 16 | 31 | 16 |
| 10 | 512 | 1023 | 512 |
| 20 | 524288 | 1048575 | 524288 |
| 71 | 2^70 | 2^71 - 1 | ~1.18 × 10^21 |

### 1.2 Position in Range

The position percentage indicates where a key sits within its valid range:

```
position% = (k_N - 2^(N-1)) / (2^(N-1) - 1) × 100
```

| Key | Position | Interpretation |
|-----|----------|----------------|
| k_3 = 7 | 100% | Maximum value (2^3 - 1) |
| k_4 = 8 | 0% | Minimum value (2^3) |
| k_69 | 0.72% | Very low - allowed fast solving |
| Mean | 51.86% | Slightly above midpoint |

---

## 2. Known Key Relationships

### 2.1 Exact Product Relationships

```
k_5 = k_2 × k_3 = 3 × 7 = 21         ✓ EXACT
k_6 = k_3² = 7² = 49                 ✓ EXACT
k_8 = k_4 × k_3 × 4 = 8 × 7 × 4 = 224  ✓ EXACT
```

### 2.2 Linear Recurrence (Coefficient 19)

The pattern k_n = a×k_{n-1} + 19×k_{n-2} works for early keys:

```
k_3 = -4×k_2 + 19×k_1 = -4(3) + 19(1) = -12 + 19 = 7   ✓
k_4 = -7×k_3 + 19×k_2 = -7(7) + 19(3) = -49 + 57 = 8   ✓
k_5 = -14×k_4 + 19×k_3 = -14(8) + 19(7) = -112 + 133 = 21  ✓
```

**Pattern breaks at k_7:**
```
k_7 = a×k_6 + 19×k_5 requires a = (76 - 399)/49 = -6.59... (not integer)
```

### 2.3 Prime Factorizations

| Key | Value | Factorization | Special Property |
|-----|-------|---------------|------------------|
| k_2 | 3 | 3 | Prime |
| k_3 | 7 | 7 | Prime |
| k_5 | 21 | 3 × 7 | k_2 × k_3 |
| k_6 | 49 | 7² | k_3² |
| k_11 | 1155 | 3 × 5 × 7 × 11 | Contains puzzle number |
| k_17 | 95823 | 3⁴ × 7 × 13² | Contains 7 and 13² |

---

## 3. Transition Analysis

### 3.1 Normalized Delta

The normalized delta measures how much a key grows relative to the bit size:

```
δ_norm = (k_{n+1} - k_n) / 2^n
```

**Statistics:**
- Range: [0.092, 1.305]
- Mean: 0.762
- Median: 0.724

**Anomalous Transitions:**
| Transition | δ_norm | Note |
|------------|--------|------|
| 9 → 10 | 0.092 | Smallest (k_10 barely grew) |
| 56 → 57 | 1.305 | Largest (k_57 grew fast) |

### 3.2 Consecutive Ratios

The ratio k_{n+1}/k_n typically ranges from 1.14 to 3.26.

---

## 4. Byte-Level Affine Model

### 4.1 The Model

For each byte position (lane) in the key:

```
y[lane] = A[lane] × x[lane] + C[lane] (mod 256)
```

Where:
- x = byte from k_n
- y = corresponding byte from k_{n+1}
- A = lane-specific multiplier
- C = transition-specific constant

### 4.2 A Multipliers

| Lane | A | Factorization | Note |
|------|---|---------------|------|
| 0 | 1 | 1 | Identity |
| 1 | 91 | 7 × 13 | Divisible by 13 |
| 5 | 169 | 13² | Divisible by 13 |
| 9 | 32 | 2^5 | **ANOMALY** - NOT divisible by 13 |
| 13 | 182 | 2 × 7 × 13 | Divisible by 13 |
| Others | 1 | 1 | Identity |

**Pattern:** Lanes 1, 5, 13 have A divisible by 13. Lane 9 breaks this pattern.

### 4.3 Critical Limitation

The affine model is **circular reasoning**:

```
To predict y: need C
To calculate C: C = (y - A×x) mod 256 → need y!
```

This means the model can describe relationships after knowing both keys, but cannot predict unknown keys.

---

## 5. Bridge Puzzles

Bridge puzzles are solved keys at intervals of 5 (N = 75, 80, 85, 90, ...).

### 5.1 Known Bridge Keys

```python
k_70 = 970436974005023690481
k_75 = 22538323240989823823367
k_80 = 1105520030589234487939456
k_85 = 21090315766411506144426920
k_90 = 868012190417726402719548863
```

### 5.2 Bridge Ratios

Expected ratio for 5-bit jump: 2^5 = 32

| Jump | Actual Ratio | Deviation |
|------|--------------|-----------|
| 70→75 | 23.22 | -27.4% |
| 75→80 | 49.05 | +53.3% |
| 80→85 | 19.08 | -40.4% |

The high variance suggests keys are pseudo-random, not following a simple growth pattern.

---

## 6. Constraint Analysis for Puzzle 71

### 6.1 Bit Range Constraint

```
k_71 ∈ [2^70, 2^71 - 1]
     = [1180591620717411303424, 2361183241434822606847]
```

### 6.2 Delta Constraint

Using historical δ_norm ∈ [0.09, 1.31]:

```
k_71 ∈ [k_70 + 0.09×2^70, k_70 + 1.31×2^70]
     ≈ [1.08×10^21, 2.52×10^21]
```

### 6.3 Combined Analysis

The delta constraint interval **completely contains** the bit range:
- Delta low (1.08×10^21) < Bit low (1.18×10^21)
- Delta high (2.52×10^21) > Bit high (2.36×10^21)

**Conclusion:** Delta constraints do NOT reduce the search space.

---

## 7. Negative Results (What Doesn't Work)

### 7.1 Tested and Failed Approaches

| Approach | Result |
|----------|--------|
| LCG (Linear Congruential Generator) | No consistent (a, c) parameters |
| SHA256(n) | k_n ≠ SHA256(n) masked to n bits |
| Polynomial generators | Finite differences not constant |
| Fibonacci-like | 15-45% error per step |
| XOR patterns | k_n ≠ k_a XOR k_b |
| Affine prediction | Circular - requires knowing answer |

### 7.2 Key Insight

Early keys (1-6) have exact mathematical relationships, but larger keys appear **cryptographically random**. The puzzle creator likely used a deterministic HD wallet that produces pseudo-random output.

---

## 8. Open Research Questions

1. **Why coefficient 19?** The linear recurrence uses 19 consistently for k_3, k_4, k_5.

2. **Why 13 in A multipliers?** (91 = 7×13, 169 = 13², 182 = 14×13)

3. **Why does Lane 9 break the pattern?** A=32=2^5 instead of 13-related.

4. **What wallet software was used?** Could reveal derivation path.

5. **Can bridge ratios constrain intermediate keys?**

---

## 9. Complete Known Key Table

```
Puzzle  | Private Key (decimal)
--------|------------------------------------------
1       | 1
2       | 3
3       | 7
4       | 8
5       | 21
6       | 49
7       | 76
8       | 224
9       | 467
10      | 514
11      | 1155
12      | 2683
13      | 5765
14      | 10544
15      | 26867
16      | 51510
17      | 95823
18      | 198669
19      | 357535
20      | 863317
...     | ...
69      | 297274491920375905804
70      | 970436974005023690481
75      | 22538323240989823823367
80      | 1105520030589234487939456
85      | 21090315766411506144426920
90      | 868012190417726402719548863
```

---

## 10. Formulas Quick Reference

```python
# Key range
range_low = 2 ** (N - 1)
range_high = 2 ** N - 1

# Position in range
position_pct = (k_N - range_low) / (range_high - range_low) * 100

# Normalized delta
delta_norm = (k_next - k_curr) / (2 ** n)

# Affine model
y = (A * x + C) % 256
C = (y - A * x) % 256

# Bridge ratio
ratio = k_n5 / k_n  # Expected ~32 for 5-step jump
```

---

*Document Version: 1.0*
*Last Updated: 2025-12-09*
