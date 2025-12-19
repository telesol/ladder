# Master Plan: Cracking the m-sequence Formula

**Created**: 2025-12-19 19:30 UTC
**Status**: PLANNING

---

## Current State

### What We Have
1. **All 70 m-values** (n=2 to n=70) - verified in `data_for_csolver.json`
2. **Factorizations for n=36-70** - in `factorization_database.json`
3. **Verified formula structure**: `k_n = 2*k_{n-1} + adj_n` where `adj_n = 2^n - m_n * k_{d_n}`
4. **PySR approximate formula**: `m_n ≈ pow2_n * f(d_n) - m_{n-2}` (not exact)

### Key Observations from Factorization
| n | m | Factors | Notable Pattern |
|---|---|---------|-----------------|
| 9 | 493 | 17 × 29 | p[7] × p[10] |
| 11 | 1921 | 17 × 113 | p[7] × p[30] |
| 12 | 1241 | 17 × 73 | p[7] × p[21] |
| 48 | 329601320238553 | 11 × 17 × ... | Contains p[7]=17 |
| 57 | 4490805416683930 | 2×5×19×113×... | Many small primes |
| 67 | 35869814695994276026 | 2×17×31×179×... | Contains p[7]=17 |

### What Doesn't Work
- **PySR with standard operators**: Can't find exact integer formulas
- **Float coefficients**: m-values are products of primes, not continuous functions
- **Single formula for all n**: The sequence may have phase transitions

---

## Strategic Options

### Option A: Prime Index Pattern Discovery
**Hypothesis**: m_n = product of primes at specific indices, where indices are computable from n

**Approach**:
1. For each n, list the prime indices of factors
2. Look for patterns in index sequences
3. Use LLMs (qwq:32b, deepseek-r1:70b) to find index generation rule

**Pro**: Directly addresses the structure we see
**Con**: Large numbers have indices too large to verify easily

### Option B: Phase-Based Analysis
**Hypothesis**: The formula changes at certain breakpoints

**Approach**:
1. Split into phases (n=2-10, n=11-20, n=21-35, n=36-70)
2. Find separate formulas for each phase
3. Identify the transition rule

**Pro**: Simpler formulas per phase
**Con**: Still need to find exact formulas

### Option C: d-sequence Focus
**Hypothesis**: Understanding d_n generation unlocks m_n

**Approach**:
1. The d_n sequence is much simpler (values 1-8 only)
2. Find d_n generation rule first
3. Use d_n pattern to constrain m_n search

**Pro**: Simpler target
**Con**: d_n might also be algorithmically complex

### Option D: PRNG Reverse Engineering
**Hypothesis**: m_n comes from a seeded PRNG

**Approach**:
1. Treat m_n as PRNG output
2. Test common PRNGs (LCG, Mersenne Twister, etc.)
3. Find seed and parameters

**Pro**: Would explain apparently random values
**Con**: Many possible PRNGs to test

### Option E: Self-Referential Bootstrap
**Hypothesis**: Each m_n is computed from previous m values

**Approach**:
1. m_n = f(m_{n-1}, m_{n-2}, ..., m_{n-k}, n)
2. The function f might involve primes, modular arithmetic
3. Base cases: m[2]=1, m[3]=1, m[4]=22, m[5]=9, m[6]=19, m[7]=50, m[8]=23

**Pro**: Matches self-referential formulas we've found
**Con**: Complex to search

---

## Recommended Plan

### Phase 1: Deep Prime Index Analysis (Priority: HIGH)
**Task for qwq:32b or deepseek-r1:70b**

Analyze the factorization data and find:
1. For small primes (2,3,5,7,11,13,17,19,23,29), which n values have them as factors?
2. Are there patterns in when p[7]=17 appears?
3. For each n, what determines which primes are used?

### Phase 2: d-sequence Crack (Priority: MEDIUM)
**Task for phi4:14b**

The d_n sequence is:
```
d[2]=2, d[3]=3, d[4]=1, d[5]=2, d[6]=2, d[7]=2, d[8]=4, d[9]=1, d[10]=7, ...
```

Find the pattern. This is much smaller search space.

### Phase 3: Self-Referential Formula Search (Priority: MEDIUM)
**Computational task**

Test formulas of the form:
```
m_n = a * m_{n-d_n} + b * 2^n + c * prime(f(n))
```
Where a, b, c are small integers and f(n) is a simple function of n.

### Phase 4: Multi-Box Parallel Search (Priority: HIGH)
**Use all 4 boxes**

- Spark1: Prime index pattern analysis
- Spark2: d-sequence formula search
- Box 211: Self-referential formula testing
- Box 212: PRNG hypothesis testing

---

## Immediate Actions

1. **Create task files for each box** with specific assignments
2. **Dispatch to local LLMs** via Ollama API
3. **Monitor and collect results**
4. **Synthesize findings** into unified formula

---

## Success Criteria

We have succeeded when we can:
1. Compute m_n for any n using only n and base cases
2. Verify formula produces correct values for all 70 known m values
3. Generate m_71 to m_160 with confidence

---

## Resources

| Box | Model | RAM | Task |
|-----|-------|-----|------|
| Spark1 | qwq:32b, phi4:14b | 128GB | Pattern analysis |
| Spark2 | phi4:14b, qwen3-vl:8b | 128GB | d-sequence |
| Box 211 | deepseek-r1:70b | 128GB | Deep reasoning |
| Box 212 | mixtral:8x22b | 128GB | PRNG testing |

---

**Let's crack this systematically.**
