# MASTER CHECKLIST: Formula Derivation

## The Goal
Derive k[71-74] using ONLY mathematics, NO assumptions.

## What We Have (VERIFIED)

### Known Keys (from database)
- [x] k[1] to k[70] - ALL 70 keys
- [x] k[75] = 22,538,323,240,989,823,823,367
- [x] k[80] = 303,539,067,084,864,993,920,014,405
- [x] k[85], k[90] also known

### Verified Formulas
- [x] k[n] = 2*k[n-1] + adj[n]
- [x] adj[n] = 2^n - m[n]*k[d[n]]
- [x] d[n] minimizes m[n] (67/69 verified)
- [x] 3-step: k[n] = 9*k[n-3] + offset[n] for n >= 31

### Computed Sequences (n=2 to 70)
- [x] m_seq[n] - computed from known keys
- [x] d_seq[n] - computed from known keys
- [x] adj[n] = k[n] - 2*k[n-1]
- [x] offset[n] = k[n] - 9*k[n-3] for n >= 31

---

## TASK 1: Compute d[n] Algorithm
**Question:** What rule determines d[n]?

### What we know:
- d[n] is always chosen to minimize m[n]
- d[n] values: 2,3,2,2,2,2,2,3,2,2,3,2,2,2,3,2,...

### To compute:
```python
for n in range(4, 71):
    for d_candidate in range(2, n):
        m_candidate = (2**n - adj[n]) / k[d_candidate]
        if m_candidate is integer and m_candidate > 0:
            record (n, d_candidate, m_candidate)
    d[n] = d that gives minimum m[n]
```

### Verify:
- [ ] Run computation for ALL n=4..70
- [ ] Confirm d[n] always minimizes m[n]
- [ ] Find pattern in d[n] sequence

---

## TASK 2: Compute Offset Pattern ✅ SOLVED!
**Question:** What generates offset[n] = k[n] - 9*k[n-3]?

### DERIVED FORMULA (100% verified for n=34..70):
```
offset[n] = 3*2^n - k[n-3] - (4*m[n-2]*k[d[n-2]] + 2*m[n-1]*k[d[n-1]] + m[n]*k[d[n]])
```

This is COMPUTED from the recurrence, not assumed!

### Known offsets (n=63-70):
```
off[63] = -1,222,142,202,450,997,670
off[64] = +4,967,579,474,010,341,790
off[65] = -4,606,975,570,506,195,703
off[66] = -34,592,851,995,373,892,186
off[67] = -27,540,062,615,817,873,350
off[68] = -55,217,129,595,261,785,870
off[69] = -119,841,466,032,741,115,730
off[70] = -223,475,518,416,452,616,237
```

### To compute:
```python
for n in range(31, 71):
    offset[n] = k[n] - 9*k[n-3]
    # Analyze: offset[n] = f(m[n], m[n-1], m[n-2], k[...])
```

### Verify:
- [ ] Compute all offsets n=31..70
- [ ] Find relationship to m-values
- [ ] Find relationship to k-values
- [ ] Test: is offset[n] = g(offset[n-1], offset[n-2], offset[n-3])?

---

## TASK 3: Bridge Math (k[75] → k[71]) ✅ EQUATIONS DERIVED!
**Question:** Given k[75], what constraints exist on k[71-74]?

### DERIVED EQUATION FOR k[71]:
```
k[71] = 4,302,057,189,444,869,987,810 - m[71]*k[d[71]]
```

Valid range: 1.18e21 <= k[71] < 2.36e21
For d[71]=2: m[71] ∈ [6.47e20, 1.04e21]
For d[71]=5: m[71] ∈ [9.24e19, 1.49e20]
For d[71]=8: m[71] ∈ [8.66e18, 1.39e19]

### Chain relationships:
```
k[72] = 9*k[69] + offset[72]     (k[69] known!)
k[73] = 9*k[70] + offset[73]     (k[70] known!)
k[74] = 9*k[71] + offset[74]     (k[71] UNKNOWN)
k[75] = 9*k[72] + offset[75]     (k[75] known!)
```

### From k[75]:
```
k[75] = 9*k[72] + offset[75]
k[75] = 9*(9*k[69] + offset[72]) + offset[75]
k[75] = 81*k[69] + 9*offset[72] + offset[75]

Therefore:
9*offset[72] + offset[75] = k[75] - 81*k[69]
                          = 22,538,323,240,989,823,823,367 - 81*k[69]
```

### To compute:
- [ ] Get exact k[69] from database
- [ ] Compute: constraint = k[75] - 81*k[69]
- [ ] This gives: 9*offset[72] + offset[75] = constraint
- [ ] Need second equation to solve for offset[72], offset[75]

### The missing piece:
We need the RULE that generates offset[n], not an assumption!

---

## TASK 4: m[n] Generation Rule
**Question:** What mathematical rule generates m[n]?

### Known patterns:
- m[2]=1, m[3]=1 (bootstrap via self-reference)
- m[4]=22 (π convergent 22/7)
- m[5]=9 (3^2)
- m[6]=19 (e convergent, sqrt(3) convergent h[4])
- m[7]=50, m[8]=23, m[9]=493, m[10]=19...

### Observed relationships:
- m[8] = m[2] + m[4] = 1 + 22 = 23
- m[10] = m[2] * m[6] = 1 * 19 = 19
- Factor 19 appears at n=6,10,11,71 (mod 3 pattern?)

### To verify:
- [ ] For each n, test: is m[n] a combination of earlier m-values?
- [ ] For each n, test: is m[n] a mathematical constant convergent?
- [ ] For each n, test: is m[n] = f(n) for some function f?

---

## VERIFICATION PROTOCOL

For ANY derived k[71]:
1. Compute BTC address: `python verify_btc_address.py`
2. Compare to puzzle 71: `1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU`
3. If MATCH → SOLVED
4. If NO MATCH → derivation is WRONG, go back to math

---

## BOX ASSIGNMENTS

| Box | Model | Task | Focus |
|-----|-------|------|-------|
| Spark1 | qwq:32b | TASK 4 | m[n] generation rule |
| Spark2 | phi4:14b | TASK 2 | Offset pattern analysis |
| Box211 | deepseek-r1:70b | TASK 3 | Bridge constraints |
| Box212 | deepseek-math:7b | TASK 1 | d[n] algorithm |

---

## SUCCESS CRITERIA

- [ ] d[n] algorithm: can compute d[n] for any n without known k[n]
- [ ] m[n] rule: can compute m[n] for any n without known k[n]
- [ ] offset[n] rule: can compute offset[n] from the rules
- [ ] k[71] derived that produces address `1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU`
