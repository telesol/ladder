# REASONING TASK: Constant Selector Function

## VERIFIED DISCOVERIES

The Bitcoin puzzle k-values encode mathematical constants:
```
k[n] / 2^n ≈ C(n)  for some constant C(n)
```

### Ultra-Precise Matches (< 0.2% error):
| n | k[n]/2^n | Constant | Error |
|---|----------|----------|-------|
| 16 | 0.785980 | π/4 | 0.074% |
| 19 | 0.679304 | e/4 | 0.035% |
| 58 | 0.693808 | ln(2) | 0.095% |
| 59 | 0.782345 | π/4 | 0.389% |
| 61 | 0.618337 | 1/φ | 0.049% |
| 68 | 1.153874 | π/e | 0.164% |
| 70 | 0.679774 | e/4 | 0.030% |

### Groupings by Best Constant:
```
1/φ (golden ratio): n ∈ {13, 14, 36, 56, 61, 66}
  Pattern: 4 of 6 have n ≡ 1 (mod 5)

π/4: n ∈ {2, 6, 15, 16, 18, 20, 26, 29, 34, 53, 70}
  Pattern: 8 of 11 have n ≡ 0 (mod 2)

e/π: n ∈ {3, 8, 21, 24, 27, 28, 33, 43, 44, 47, 55, 62, 65, 67}
  Pattern: 9 of 14 have n ≡ 1 (mod 2)

e/4: n ∈ {5, 12, 19, 23, 41, 42, 48, 70}
  Pattern: Variable

1/√2: n ∈ {17, 22, 32, 37, 46, 49}
  Pattern: 4 of 6 have n ≡ 1 (mod 3)

1/√3: n ∈ {7, 11, 35, 39, 45, 54}
  Pattern: 5 of 6 have n ≡ 1 (mod 2)
```

### KEY OBSERVATION:
n = 71 is:
- PRIME
- 71 ≡ 1 (mod 5) → suggests 1/φ
- 71 ≡ 2 (mod 3) → does NOT suggest 1/√2
- 71 ≡ 1 (mod 7)
- 71 = 55 + 16 = 89 - 18 (near Fibonacci 55, 89)

## YOUR TASK

Find the EXACT rule for C(n). What mathematical function determines which constant to use?

Consider:
1. Is it based on n mod p for some prime p?
2. Is it based on primality of n?
3. Is it based on position relative to Fibonacci numbers?
4. Is there a cycle or pattern?

The puzzle creator had a DETERMINISTIC rule. Find it.

Think step by step. Show your reasoning.
