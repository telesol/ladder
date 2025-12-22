# 5-Step Pattern Analysis Results

## Date: 2025-12-22

## CRITICAL DISCOVERIES

### 1. The 5-step formula is DERIVED, not fundamental!

```
k[n+5] = 32 × k[n] + offset5[n]
```

Where:
```
offset5[n] = 16×adj[n+1] + 8×adj[n+2] + 4×adj[n+3] + 2×adj[n+4] + adj[n+5]
           = Σ 2^(5-i) × adj[n+i] for i=1 to 5
```

**VERIFIED: 100% match for all available n (1-80)**

### 2. The 1-step adj formula is verified

```
adj[n] = k[n] - 2×k[n-1]
adj[n] = 2^n - m[n]×k[d[n]]
```

**VERIFIED: 100% match for n=2 to n=70**

### 3. The combined 10-step formula

```
offset10[n] = 32×offset5[n] + offset5[n+5]
k[n+10] = 1024×k[n] + offset10[n]
```

**VERIFIED: 100% match for all available pairs**

## KEY INSIGHT

The 5-step "bridge" pattern is NOT a separate formula - it's a mathematical CONSEQUENCE of the 1-step recurrence!

The TRUE unknowns are:
- **m[n]**: The mysterious m-sequence
- **d[n]**: The divisor index sequence

If we can find the generation rules for m[n] and d[n], we can compute ANY k[n]!

## Sign Pattern Analysis

The offset5 signs do NOT follow a simple n mod 10 pattern. The signs depend on:
- The sum of adj values in the 5-step window
- Each adj sign depends on whether 2^n > m[n]×k[d[n]]

## Normalized Offset Analysis

| n | offset5[n]/2^n | Sign |
|---|----------------|------|
| 70 | -7.21 | - |
| 75 | +10.17 | + |
| 80 | -11.82 | - |
| 85 | +4.99 | + |

The magnitudes vary because the adj values vary!

## Formula Chain

```
d[n] → (unknown rule)
m[n] → (unknown rule, possibly minimizes result)
adj[n] = 2^n - m[n]×k[d[n]]
k[n] = 2×k[n-1] + adj[n]
offset5[n] = Σ 2^(5-i) × adj[n+i]
k[n+5] = 32×k[n] + offset5[n]
```

## Next Steps

1. Find the d[n] generation rule
2. Find the m[n] generation rule  
3. These are the ONLY unknowns needed for ANY puzzle

## Cluster Task Findings (Preliminary)

- **Spark2 (qwen3:32b)**: Proposed selector function based on n mod 5
  - n ≡ 0 mod 5: C = 1/√2
  - n ≡ 3 mod 5: C = ln(2)
  - n ≡ 1 mod 5 (power of 2): C = π/4
  - n ≡ 1 mod 5 (prime): C = 1/φ

- **Box211 (deepseek-r1:70b)**: Analyzing 5-step interpolation
- **Spark1 (qwq:32b)**: Investigating m-sequence generation
