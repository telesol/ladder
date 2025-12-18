# Solver Synthesis: Construction Approaches
Date: 2025-12-18

## B-Solver (phi4) - EC Scalar Construction

### Key Proposal
```
kₙ = 2·kₙ₋₁ + adjₙ
adjₙ = f(x(n·G)) mod 2ⁿ
```

Where f extracts bits from EC point coordinates.

### Specific Approaches
1. **Option A (x-coordinate based)**:
   - Compute P = n · G
   - adjₙ = x(P) mod 2ⁿ
   - Or: adjₙ = H(x(P)) mod 2ⁿ (with hash H)

2. **Option B (y-coordinate based)**:
   - adjₙ = f(x(P), y(P))

3. **Verification pseudocode provided**:
   - Recompute kₙ from recurrence
   - Verify public keys lie on curve

### Parameter Search Strategies
- Brute force on adjustment function f
- Statistical analysis of key ranges
- Curve order considerations (secp256k1)
- Cross-validation with public keys

---

## C-Solver (QWQ) - PRNG Reconstruction (partial)

### Key Insights
1. **m_n constraint**: m_n / 2^(n-d_n) ∈ [0.72, 2.75]
2. **m_n must be INTEGER** (verified from data)
3. **d_n selection**: Chosen from {1..8} to minimize |m_n|

### PRNG Candidates
1. **LCG**: x_{n+1} = (a·xₙ + c) mod m
2. **XORshift**: Fast, simple bit manipulation
3. **Mersenne Twister**: High quality but complex

### Generation Method
```
For each n:
  1. Generate norm_m ∈ [0.72, 2.75] from PRNG
  2. Compute m_n = round(norm_m × 2^(n-d_n))
  3. d_n chosen to minimize |m_n|
```

---

## Combined Construction Hypothesis

The puzzle creator likely used ONE of these methods:

### Method 1: EC-Derived Adjustment
```python
def generate_ladder_ec(G, n_keys, secret_function):
    k = [0, 1]  # k_0=0, k_1=1
    for n in range(2, n_keys + 1):
        P_n = n * G  # EC point multiplication
        adj_n = secret_function(P_n) % (2**n)
        k_n = 2 * k[n-1] + adj_n
        k.append(k_n)
    return k
```

### Method 2: PRNG-Seeded m Values
```python
def generate_ladder_prng(seed, n_keys):
    rng = init_prng(seed)
    k = [0, 1]
    for n in range(2, n_keys + 1):
        # Try each d from 1-8, pick one minimizing |m|
        best_d, best_m = None, float('inf')
        for d in range(1, min(n, 9)):
            if k[d] == 0: continue
            target_adj = ??? # Need to reverse-engineer
            m = (2**n - target_adj) // k[d]
            if abs(m) < abs(best_m):
                best_d, best_m = d, m

        adj_n = 2**n - best_m * k[best_d]
        k_n = 2 * k[n-1] + adj_n
        k.append(k_n)
    return k
```

### Method 3: Hybrid (EC + PRNG)
The adjustment could come from EC operations seeded by a PRNG:
```python
adj_n = prng_value * x_coord(n * G) % 2**n
```

---

## Next Steps

1. **Test EC hypothesis** - Compute n*G for n=1..70, check if x-coordinates relate to adj_n
2. **Test PRNG hypothesis** - Try common seeds (0, 1, puzzle dates, etc.)
3. **Build working prototype** - Implement both methods, test against known k_1..k_70

## Data for Testing
Known sequences (n=2..20):
- m: [1, 1, 22, 9, 19, 50, 23, 493, 19, 1921, 1241, 8342, 2034, 26989, 8470, 138269, 255121, 564091, 900329, 670674]
- d: [2, 3, 1, 2, 2, 2, 4, 1, 7, 1, 2, 1, 4, 1, 4, 1, 1, 1, 1, 2]
