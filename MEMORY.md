# PERSISTENT MEMORY - Bitcoin Puzzle Analysis

## CRITICAL RULES FOR ALL MODELS
1. **NO BRUTE FORCE** - Never suggest searching. Only mathematical derivation.
2. **RECONSTRUCT** - We are reverse engineering to rebuild the generator
3. **BUILD ON DISCOVERIES** - Read this file, add to it, don't repeat work

---

## VERIFIED FORMULAS (100%)

### Core Recurrence
```
k[n] = 2*k[n-1] + adj[n]
adj[n] = 2^n - m[n]*k[d[n]]
d[n] = argmin{m : k[d] | (2^n - adj[n])}
```

### Base Cases
```
k[1] = 1
k[2] = 3
k[3] = 7
d[2] = 2, m[2] = 1 (self-reference)
d[3] = 3, m[3] = 1 (self-reference)
```

### k[71] Equation
```
k[71] = 4,302,057,189,444,869,987,810 - m[71]*k[d[71]]
     = 2*k[70] + 2^71 - m[71]*k[d[71]]
Target address: 1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU
Target HASH160: f6f5431d25bbf7b12e8add9af5e3475c44a0a5b8
```

### k[71] Constraints (2025-12-21)
```
Valid range: [2^70, 2^71 - 1]
           = [1,180,591,620,717,411,303,424 , 2,361,183,241,434,822,606,847]

k[70] = 970,436,974,005,023,690,481
2^71  = 2,361,183,241,434,822,606,848
BASE  = 2*k[70] + 2^71 = 4,302,057,189,444,869,987,810

m[71] constraints per d value:
- d=1: m∈[1.94T, 3.12T] (huge range)
- d=2: m∈[647B, 1.04T]
- d=5: m∈[92B, 149B]
- d=8: m∈[8.7B, 13.9B] (smallest range)

Key insight: d is chosen to MINIMIZE m.
If d[71]=8, m[71] would be in ~10 billion range.
```

---

## KEY STRUCTURAL FACTS

### Special Keys
- k[1,2,3] = 1, 3, 7 (Mersenne-like: 2^n - 1)
- k[4] = 8 = 2³ (exact power of 2, position 0.00%)
- k[5] = 21 = 3×7 = k[2]×k[3]
- k[6] = 49 = 7² = k[3]²
- k[8] = 224 = 2⁵×7 = 32×k[3]
- k[10] = 514 = 2⁹ + 2 (only 2 bits set, position 0.39%)
- k[11] = 1155 = 3×5×7×11 (product of consecutive primes)

### Position Anomalies (near minimum of range)
- k[4]: 0.00% (exactly at minimum)
- k[10]: 0.39%
- k[69]: 0.72%

### d-Value Distribution
```
d=1: 43.5% (30/69)
d=2: 29.0% (20/69)
d=3-8: remaining 27.5%
```

---

## OPEN QUESTIONS (Need Investigation)

### 1. PRNG Reconstruction
- What PRNG could generate k[1..70]?
- Is there a seed that produces this sequence?
- Check: LCG, LFSR, Mersenne Twister patterns

### 2. Binary Structure
- Why are some keys very sparse (k[4], k[10])?
- What determines the bit pattern?
- XOR relationships between consecutive keys?

### 3. Bitcoin Block Connection
- Are keys derived from block hashes?
- Timestamp relationships?
- Transaction ID connections?

### 4. Mathematical Constants
- m[4]/m[3] ≈ 22/7 ≈ π (but m[2]=1, m[3]=1, so this needs revision)
- k[2], k[3] are Fibonacci-adjacent (3, 7 → fib 3, 5, 8)
- sqrt(3) convergent h[4] = 19 appears in m[6] and m[10]

---

## FAILED HYPOTHESES (Don't Retry)

1. ❌ Greedy generation from scratch (produces powers of 2)
2. ❌ Seeded greedy with k[1,2,3] (still wrong)
3. ❌ Simple linear recurrence for m[n]
4. ❌ d[n] from bit position of n

---

## DISCOVERIES LOG

### Session 2025-12-21
- Formula 100% verified for n=2..70
- k[71] equation derived
- Greedy rule does NOT generate the sequence
- Search is infeasible - DO NOT SUGGEST BRUTE FORCE

### deepseek-r1:70b Finding
The model derived: m[n] = (2^n - adj[n]) / k[d[n]]
With hypothesis d[n] = n-1, it verified:
- m[3] = (8 - 4)/4 = 1 ✓
- m[4] = (264)/12 = 22 ✓
- m[5] = (-2016)/(-224) = 9 ✓

BUT: It used hypothetical k values, not actual database values.
NEED: Verify this with REAL k values from database.

---

## SELF-REFERENTIAL M-PATTERNS (2025-12-21)

### Building Blocks
```
m[4] = 22, m[5] = 9, m[6] = 19, m[7] = 50, m[8] = 23
```

### Verified Self-Referential Formulas (n=36-70)
```
m[38] = m[4] × 4,975,901,387    (prime quotient)
m[40] = m[7] × 4,955,401,018
m[47] = m[8] × 5,386,442,171,234
m[50] = m[4] × 60,590,782,760,905
m[51] = m[7] × 4,043,746,545,334
m[55] = m[4] × 1,178,741,682,549,451
m[57] = m[6] × 236,358,179,825,470
m[58] = m[6] × 6,399,039,052,580,047
m[61] = m[4] × 47,729,366,167,182,299
m[69] = m[6] × 1,836,636,217,706,671,242
```

### Self-Index Pattern
When n is prime: m[n] = n × Q
```
m[19] = 19 × 29,689
m[41] = 41 × 22,342,064,035
=> m[71] might = 71 × Q (71 is prime!)
```

### d-Value Distribution (n=36-70)
```
d=1: 14 times (40%)
d=2: 12 times (34%)
d=3: 2 times
d=5: 4 times
d=6: 1 time
d=8: 2 times
```

### M[71] Prediction Constraints
```
If d[71]=1: m[71] ∈ [1.94×10^21, 3.12×10^21]
If d[71]=2: m[71] ∈ [6.47×10^20, 1.04×10^21]
If d[71]=8: m[71] ∈ [8.66×10^18, 1.39×10^19] (smallest range)

If 71 is prime self-index pattern applies:
  m[71] = 71 × Q where Q ∈ [27.3×10^18, 44.0×10^18]
```

### Key Approximation (2025-12-21)
```
m[n] ≈ 2^n / k[d[n]] with 1-60% error
Error comes from adj[n] = k[n] - 2*k[n-1]

Predicted m[71] centers:
  d=1: m ≈ 2^71 / 1   = 2.36×10^21
  d=2: m ≈ 2^71 / 3   = 7.87×10^20
  d=5: m ≈ 2^71 / 21  = 1.12×10^20
  d=8: m ≈ 2^71 / 224 = 1.05×10^19

d[71] most likely = 1 (40%) or 2 (30%) based on n=51-70 distribution

LOW-POSITION KEYS: k[4], k[10], k[69] all at <1% position
If k[71] = 2^70 (exactly at minimum like these):
  d[71] = 1
  m[71] = 3,121,465,568,727,458,684,386 (exact integer)
  adj[71] = -760,282,327,292,636,077,538
```

---

## SESSION 2025-12-21 KEY FINDINGS

### Self-Referential Patterns (n=36-70)
10 m-values are divisible by building blocks m[4-8]:
- m[38] = m[4]×prime, m[40] = m[7]×composite
- m[47] = m[8]×composite, m[50,55,61] = m[4]×...
- m[51] = m[7]×..., m[57,58,69] = m[6]×...

### Approximation Formula
m[n] ≈ 2^n / k[d[n]] with 1-60% error
- d=1: ratio ~1.0
- d=2: ratio ~0.32 (≈1/3)
- d=5: ratio ~0.048 (≈1/21)
- d=8: ratio ~0.005 (≈1/224)

### Low-Position Keys (n ≡ 1 mod 3)
k[1], k[4], k[10], k[69] all at <1% position in range
71 ≡ 2 (mod 3), so k[71] likely NOT at minimum

### d-Value Prediction for n=71
Based on n=51-70 distribution:
- d=1: 40% likely → m[71] ≈ 2^71
- d=2: 30% likely → m[71] ≈ 2^71/3
After d[70]=2, historically d[n+1]=1 (60%), d=2 (20%), d=5 (20%)

---

## NEXT TASKS (For Models)

1. **PRNG Analysis**: Reverse engineer possible PRNG from k[1..70]
2. **Binary Deep Dive**: Analyze bit patterns, find structure
3. **Block Connection**: Find relationship to Bitcoin blockchain
4. **m-Sequence Structure**: What generates m[n]? (not greedy)
5. **M[71] Prediction**: Use self-ref + self-index patterns to narrow m[71]
6. **d[71] Prediction**: Analyze consecutive d-value transitions
