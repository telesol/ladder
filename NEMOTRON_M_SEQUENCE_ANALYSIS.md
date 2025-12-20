# Nemotron M-Sequence Analysis

**Date**: 2025-12-20
**Model**: nemotron-3-nano:30b-cloud

## Key Observations from Analysis

### Convergent Mapping Attempts

| n | m[n] | Factorization | Convergent Source |
|---|------|---------------|-------------------|
| 4 | 22 | 2×11 | π numerator (22/7) |
| 5 | 9 | 3² | √2 or π numerator squared |
| 6 | 19 | prime | e numerator (19/7) |
| 7 | 50 | 2×5² | √2 denominators? |
| 8 | 23 | prime | **Unknown** - not in standard lists |
| 9 | 493 | 17×29 | √2 num × √2 denom |
| 10 | 19 | prime | e numerator (repeat of n=6) |
| 11 | 1921 | 17×113 | √2 num × π denom |
| 12 | 1241 | prime | Unknown |
| 13 | 8342 | 2×4171 | Unknown |
| 14 | 2034 | 2×3×339 | Unknown |
| 15 | 26989 | prime | Unknown |

### Patterns Identified

1. **Cross-constant products**: Some m-values are products of convergents from DIFFERENT constants
   - m[9] = 17 × 29 (√2 numerator × √2 denominator)
   - m[11] = 17 × 113 (√2 numerator × π denominator)

2. **n mod 6 hypothesis** (partial):
   - n ≡ 4 (mod 6): π-related
   - n ≡ 0 (mod 6): e-related
   - n ≡ 3 (mod 6): √2-related

3. **Primes that don't fit**: 23, 1241, 26989 are primes not appearing in standard convergent lists

### Construction Rules Observed

1. **Single convergent**: m = convergent numerator (e.g., m[4]=22, m[6]=19)
2. **Squared convergent**: m = (convergent)² (e.g., m[5]=9=3²)
3. **Product of two convergents**: m = conv₁ × conv₂ (e.g., m[9]=17×29)
4. **Cross-constant product**: m = conv(const₁) × conv(const₂) (e.g., m[11]=17×113)

### Known Convergent Lists

```
π numerators: 3, 22, 333, 355, 103993, ...
π denominators: 1, 7, 106, 113, 33102, ...

√2 numerators: 1, 3, 7, 17, 41, 99, 239, ...
√2 denominators: 1, 2, 5, 12, 29, 70, 169, ...

e numerators: 2, 3, 8, 11, 19, 87, 106, ...
e denominators: 1, 1, 3, 4, 7, 32, 39, ...

φ numerators: 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, ...
φ denominators: 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, ...
```

## Verification Needed

The m-values for n=16-20 were given for verification:
- m[16] = 8470
- m[17] = 138269
- m[18] = 255121
- m[19] = 564091
- m[20] = 900329

### Factorizations to check:
```
8470 = 2 × 5 × 7 × 11 × 11 = 2 × 5 × 7 × 121
138269 = ?
255121 = ?
564091 = ?
900329 = ?
```

## Conclusion

The m-sequence construction is MORE COMPLEX than simple convergent selection:
1. Some values are single convergents
2. Some are squares of convergents
3. Some are products of convergents from DIFFERENT constants
4. Some primes don't appear in any standard convergent list

A fully deterministic rule likely requires:
- Extended constant list (possibly √3, √5, ln(2), etc.)
- Complex combination rules (products, sums, differences)
- Possibly table-based lookup for edge cases
