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

## NEXT TASKS (For Models)

1. **PRNG Analysis**: Reverse engineer possible PRNG from k[1..70]
2. **Binary Deep Dive**: Analyze bit patterns, find structure
3. **Block Connection**: Find relationship to Bitcoin blockchain
4. **m-Sequence Structure**: What generates m[n]? (not greedy)
