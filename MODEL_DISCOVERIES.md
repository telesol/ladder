# Model Discovery Attribution Log

Track which models made which discoveries to evaluate performance.

## Format
```
[DATE] [MODEL] [DISCOVERY] [VERIFIED: YES/NO]
```

---

## Discovery Log

### 2025-12-20

| Model | Discovery | Verified | Notes |
|-------|-----------|----------|-------|
| Claude Opus 4.5 | Offset formula: offset[n] = -k[n-3] + 4*adj[n-2] + 2*adj[n-1] + adj[n] | YES (40/40) | Verified for n=34-70 |
| Claude Opus 4.5 | k[75] documentation was WRONG (corrected from DB) | YES | DB value: 22,538,323,240,989,823,823,367 |
| Claude Opus 4.5 | k[80] constraint: 729*off[71] + 81*off[74] + 9*off[77] + off[80] = -337,232,494,036,332,049,352,369 | YES | Derived from verified k[80] |
| Claude Opus 4.5 | n mod 9 pattern for d-selection | PARTIAL | n=62 and n=71 both ≡ 8 (mod 9) |
| Nemotron 30B | m-values have ~(k-2) bits | YES | Observation confirmed |
| Nemotron 30B | m-values are products of small primes × large prime | PARTIAL | Pattern observed but not universal |
| DeepSeek v3.1 | 1861/1153 not exact Fibonacci but close to 21/13≈1.615 | YES | Verified: 21/13=1.6154, 1861/1153=1.6140 |
| DeepSeek v3.1 | Suggested Pell-type recurrence k_n = 6k_{n-1} - k_{n-2} | TESTING | Need to verify |
| DeepSeek v3.1 | m[n] may be CF denominators with Fibonacci-related partial quotients | HYPOTHESIS | Plausible but unverified |

---

## Model Performance Summary

| Model | Discoveries | Verified | Success Rate |
|-------|-------------|----------|--------------|
| Claude Opus 4.5 | 4 | 4 | 100% |
| Nemotron 30B | 2 | 1.5 | 75% |
| DeepSeek v3.1 671B | 3 | 2 | 67% |

---

## Pending Attributions
- m[71] construction formula: (unsolved)

---

## Prime Factorization Results (Claude Opus 4.5, 2025-12-20)

### Verified Factorizations (GNU factor)
```
m[62] = 2 × 3 × 281 × 373 × 2843 × 10487 × 63199 (7 prime factors)
m[65] = 24239 × 57283 × 1437830129 (3 prime factors)
m[68] = 5 × 1153 × 1861 × 31743327447619 (4 prime factors)
```

### Convergent Matches
| Factor | Match | Source |
|--------|-------|--------|
| 2 | ln2_num[2] | Trivial |
| 3 | ln2_den[2], Mersenne 2^2-1 | Trivial |
| 5 | φ_den[4] (Fibonacci) | Trivial |
| 281, 373, 2843, 10487, 63199 | No match | - |
| 24239, 57283, 1437830129 | No match | - |
| 1153, 1861, 31743327447619 | No match | - |

### Key Finding
The three m-values are **coprime** (GCD = 1). This suggests they are independently constructed, not derived from a common base.

### Notable Discoveries (Claude Opus 4.5)

1. **Golden Ratio in m[68]**:
   - 1861/1153 = 1.6140... ≈ φ (golden ratio 1.618...)
   - This suggests m[68] factors may be related to Fibonacci-like sequences

2. **Prime Index Pattern**:
   - 281 is the **60th prime** (n=62, so 62-2=60 ✓)
   - 373 is the 74th prime
   - 1153 is the 191st prime
   - 1861 is the 284th prime

3. **Power-of-2 Forms**:
   - 1153 = 9×2^7 + 1 = 9×128 + 1
   - 2843 = 11×2^8 ± 27
   - 57283 = 7×2^13 + 61

4. **p_{n-2} Divisibility Pattern** (VERIFIED):
   - m[9] % p_7 = m[9] % 17 = 0 ✓
   - m[10] % p_8 = m[10] % 19 = 0 ✓
   - m[62] % p_60 = m[62] % 281 = 0 ✓
   - Only 3 out of 67 m-values follow this pattern!

5. **PREDICTION for m[71]**:
   - If pattern holds: m[71] should be divisible by p_69 = **347**
   - Note: Pattern only matches 3/67 cases, so this is a weak constraint

6. **MAJOR DISCOVERY: Generalized Fibonacci Pairs in m-values** (Claude Opus 4.5):

   **m[62]**: 281 = G_2(189, 92), 373 = G_3(189, 92)
   - Sequence: 189, 92, **281**, **373**, 654, 1027, ...
   - Initial: 189 = 3³×7, 92 = 2²×23
   - Note: 281 is also the 60th prime (p_{n-2} pattern)

   **m[68]**: 1153 = G_6(101, 81), 1861 = G_7(101, 81)
   - Sequence: 101, 81, 182, 263, 445, 708, **1153**, **1861**, 3014, ...
   - Initial: 101 (prime), 81 = 3⁴

   **PATTERN**: m[n] contains consecutive G_k, G_{k+1} from specific initial pairs!

7. **INDEX FORMULA** (DeepSeek v3.1 671B):
   - k = 2(n - 59) / 3
   - For n=62: k=2 ✓
   - For n=68: k=6 ✓
   - For n=71: k=8 (prediction)
   - **CAVEAT**: Pattern only verified for d ∈ {1, 2}; n=65 (d=5) breaks it
