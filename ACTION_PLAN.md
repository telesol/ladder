# Action Plan: Finding m_n Generation Rule

**Date**: 2025-12-18
**Status**: ALL 8 OPTIONS TESTED - m_n rule NOT found
**Next**: Need new approaches (EC analysis, PRNG reconstruction, external data)

## Session Results (2025-12-18)

| Option | Status | Result |
|--------|--------|--------|
| 1. Finite Differences | ✓ DONE | NOT polynomial - differences diverge |
| 2. Linear Recurrence | ✓ DONE | NO pattern - max error >8M at order 6 |
| 3. Modular Patterns | ✓ DONE | NO periodicity detected |
| 4. Binary Analysis | ✓ DONE | NO clear bit pattern |
| 5. Hash Derivation | ✓ DONE | NOT hash-based (no SHA256 correlation) |
| 6. Key Relationship | ✓ DONE | Formula VERIFIED 100% for all 70 keys |
| 7. OEIS Search | ✓ DONE | NOT in database |
| 8. Alt Decomposition | ✓ DONE | No pattern - see OPTION8_RESULTS.md |

**Key Discovery**: `m_n / 2^(n - d_n)` is bounded in [1.0, 2.75], mean ≈ 1.72

## Current Barrier
The formula `adj_n = 2^n - m_n × k_d` is verified, but `m_n` generation rule is unknown.

## Options to Try (Priority Order)

### Option 1: Finite Differences Analysis
**What**: Compute successive differences of m-sequence
**Why**: May reveal polynomial structure
**How**:
```python
m = [1, 1, 22, 9, 19, 50, 23, 493, 19, 1921, ...]
d1 = [m[i+1] - m[i] for i in range(len(m)-1)]
d2 = [d1[i+1] - d1[i] for i in range(len(d1)-1)]
# Check if d_k becomes constant for some k
```
**Effort**: Low
**Priority**: 1

### Option 2: Linear Recurrence Detection
**What**: Find if m_n = a1×m_{n-1} + a2×m_{n-2} + ... + ak×m_{n-k}
**Why**: Many integer sequences satisfy linear recurrences
**How**:
```python
# Use Berlekamp-Massey algorithm or matrix methods
# Check recurrence orders 2, 3, 4, 5, ...
```
**Effort**: Medium
**Priority**: 2

### Option 3: Modular Arithmetic Patterns
**What**: Check m_n mod p for small primes p
**Why**: May reveal hidden periodicity
**How**:
```python
for p in [2, 3, 5, 7, 11, 13, 17, 19, 23]:
    print(f"m mod {p}: {[m % p for m in m_seq]}")
# Look for periodic patterns
```
**Effort**: Low
**Priority**: 3

### Option 4: Binary/Bitwise Analysis
**What**: Examine binary representation of m values
**Why**: Cryptographic generators often use bit operations
**How**:
```python
for m in m_seq:
    print(f"{m}: {bin(m)}, popcount={bin(m).count('1')}")
# Look for XOR patterns, bit rotations
```
**Effort**: Low
**Priority**: 4

### Option 5: Hash-Based Derivation Test
**What**: Check if m_n = f(SHA256(n)) or f(SHA256(k_n))
**Why**: Creator may have used deterministic hash
**How**:
```python
import hashlib
for n in range(2, 26):
    h = hashlib.sha256(str(n).encode()).digest()
    candidate = int.from_bytes(h[:8], 'big') % (2**n)
    # Compare with actual m_n
```
**Effort**: Medium
**Priority**: 5

### Option 6: Relationship to Earlier Keys
**What**: Check if m_n = f(k_1, k_2, ..., k_{n-1})
**Why**: m may be derived from cumulative key data
**How**:
```python
# Test: m_n = sum(k_i) mod X
# Test: m_n = product(k_i) mod X
# Test: m_n = k_{n-1} XOR k_{n-2}
```
**Effort**: Medium
**Priority**: 6

### Option 7: OEIS Search for m-sequence
**What**: Search OEIS for the m-sequence
**Why**: May be a known sequence
**How**:
```
Search: 1, 1, 22, 9, 19, 50, 23, 493, 19, 1921
```
**Effort**: Low
**Priority**: 7

### Option 8: Different Decomposition Form
**What**: Try alternative formulas besides adj_n = 2^n - m×k_d
**Why**: May find simpler pattern with different structure
**How**:
```python
# Try: adj_n = a×2^b + c×k_d + e
# Try: adj_n = f(n) × g(k_d)
# Try: adj_n as continued fraction
```
**Effort**: High
**Priority**: 8

## Execution Order

| Step | Option | Est. Time | Dependencies |
|------|--------|-----------|--------------|
| 1 | Finite Differences | 10 min | None |
| 2 | Modular Patterns | 10 min | None |
| 3 | Binary Analysis | 10 min | None |
| 4 | OEIS Search | 5 min | None |
| 5 | Linear Recurrence | 30 min | None |
| 6 | Key Relationship | 30 min | None |
| 7 | Hash Derivation | 30 min | None |
| 8 | Alt Decomposition | 60 min | Steps 1-7 |

## Success Criteria

A successful approach will:
1. Produce m_n for n > 70 given only n and base keys
2. Be verifiable against known m values (n=2..70)
3. Have mathematical justification (not just curve fitting)

## Data for Analysis

```python
m_seq = [1, 1, 22, 9, 19, 50, 23, 493, 19, 1921, 1241, 8342, 2034, 26989, 8470, 138269, 255121, 564091, 900329, 670674, 1603443, 8804812, 1693268, 29226275]
d_seq = [2, 3, 1, 2, 2, 2, 4, 1, 7, 1, 2, 1, 4, 1, 4, 1, 1, 1, 1, 2, 2, 1, 4, 1]
k_base = {1:1, 2:3, 3:7, 4:8, 5:21, 6:49, 7:76, 8:224}
```
