# Ladder Construction Foundations

## What We KNOW (100% Verified)

### 1. Bootstrap (Mersenne Numbers)
```
k[1] = 1 = 2¹ - 1
k[2] = 3 = 2² - 1
k[3] = 7 = 2³ - 1
```

### 2. Recurrence Relation (100% verified n=2-70)
```
k[n] = 2*k[n-1] + 2^n - m[n]*k[d[n]]

Where:
- adj[n] = k[n] - 2*k[n-1]
- m[n] = (2^n - adj[n]) / k[d[n]]  ← MUST be integer
- d[n] = argmin{|m|} among valid d
```

### 3. Prime k-Values
```
Position  Value   Note
n=2       3       Bootstrap prime
n=3       7       Bootstrap prime
n=9       467     First "reset" prime
n=12      2683    Second reset prime
```

### 4. Sign Pattern (++- for n=2-16)
```
n=2:  adj=+1   (+)
n=3:  adj=+1   (+)
n=4:  adj=-6   (-)
n=5:  adj=+5   (+)
n=6:  adj=+7   (+)
n=7:  adj=-22  (-)
...pattern repeats through n=16, BREAKS at n=17 (Fermat prime 2^4+1)
```

### 5. Multiplicative Structure (Verified)
```
k[4] = 2³ = 8                    (power of 2)
k[5] = k[2] × k[3] = 3 × 7 = 21  (product)
k[6] = k[3]² = 7² = 49           (square)
k[8] = 2⁵ × k[3] = 32 × 7 = 224  (power × previous k)
k[11] = 3 × 5 × 7 × 11 = 1155    (product of first 4 odd primes)
```

### 6. Coprime Reset Positions
```
Positions where k[n] is coprime with ALL previous:
n = 2, 3, 4, 9, 12, 15, 44, 45, 54, 59, 90

Early pattern: n ≡ 0 (mod 3) starting at n=9
```

---

## What We've DISPROVEN

| Hypothesis | Result | Evidence |
|------------|--------|----------|
| Minimize \|m\| globally | 0% match | Every n has m=3 candidate, never chosen |
| Minimize \|m\| with memory window | 0% match | All window sizes fail |
| Smallest k in range | Fails n≥5 | k[5]=21 not smallest |
| Closest to λ×k[n-1] | 0% match | Growth rate varies 1.1-3.4 |
| LCG pattern | Rejected | High variance (13.9) |
| LFSR pattern | Weak | Only 62.7% match |
| Low Hamming weight preference | Mixed | Some yes, some no |

---

## Critical Observation: Actual k[n] ≠ Min\|m\| Candidate

For EVERY n from 4-30:
- Min\|m\| candidate has m=3 (using d=n-1)
- Actual k[n] NEVER equals this candidate
- Actual \|m\| ranges from 3× to 197M× larger than minimum

**This proves: k[n] is NOT selected to minimize \|m\|**

---

## Building Blocks for Construction

### Layer 0: Bootstrap (Locked)
```python
k = {1: 1, 2: 3, 3: 7}  # Mersenne 2^n - 1
```

### Layer 1: Pure Structure (n=4-6)
```python
k[4] = 8   = 2³           # Power of 2
k[5] = 21  = k[2] × k[3]  # Product
k[6] = 49  = k[3]²        # Square
```

### Layer 2: Mixed Structure (n=7-8)
```python
k[7] = 76  = 2² × 19      # New prime 19 introduced
k[8] = 224 = 2⁵ × k[3]    # Power × previous k
```

### Layer 3: Prime Reset (n=9)
```python
k[9] = 467               # PRIME, coprime with all previous
```

### Pattern: After each prime reset, new multiplicative building begins

---

## What Remains Unknown

1. **Selection criterion**: What property selects k[n] from ~1000+ valid candidates?

2. **adj[n] magnitude**: We know the sign pattern (++- for n≤16), but what determines the actual value?

3. **Prime placement**: Why do primes appear at n=9, 12, 15... (interval 3)?

4. **Pattern break at n=17**: Why does Fermat prime 2^4+1 cause the sign pattern to break?

5. **Large n behavior**: Does multiplicative structure continue? Different rules?

---

## Next Steps for Construction

1. **Build forward from k[1-8]** using verified multiplicative structure
2. **Test if n=9 must be prime** (constraint or coincidence?)
3. **Analyze what happens at n=17** (Fermat prime transition)
4. **Look for hidden state** that determines adj[n] values
