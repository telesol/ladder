# Parallel Exploration Plan - Self-Referential Formula Discovery
**Date:** 2025-12-19
**Status:** Active

## Breakthrough Summary

We discovered the m-sequence is **SELF-REFERENTIAL**:
```
m[11] = p[n-4] × p[n+m[6]]   (uses m[6]=19)
m[12] = p[n-5] × p[n+m[5]]   (uses m[5]=9)
m[18] = prime(m[7] × p[87])  (uses m[7]=50)
```

## Remaining Targets

| n | m[n] | Status | Notes |
|---|------|--------|-------|
| 13 | 8342 | UNKNOWN | = 2 × 43 × 97 |
| 14 | 2034 | UNKNOWN | = 2 × 3² × 113 |
| 15 | 26989 | PARTIAL | = p[33] × p[45], need m-ref |
| 16 | 8470 | UNKNOWN | = 2 × 5 × 7 × 11² |
| 17 | 138269 | PARTIAL | = p[12]² × p[26], need m-ref |
| 19 | 564091 | UNKNOWN | = 11 × 19 × 2699 |
| 21+ | ... | UNKNOWN | Need analysis |

## Task Distribution

### SPARK1 (qwq:32b) - Self-Ref Hunter A
Focus: n = 13, 14, 15, 16
Method: For each m[n], find if m[n] = p[f(n)] × p[g(n,m[j])] for some j < n

### BOX 211 (deepseek-r1:70b) - Self-Ref Hunter B
Focus: n = 17, 19, 21, and verify prime-index patterns
Method: Check if m[n] = prime(h(n, m[k])) for some k < n

### LOCAL PYTHON (Maestro) - Verifier
Focus: Exhaustive search for self-referential patterns
Method: For each n, try ALL combinations of earlier m-values

## Specific Questions Per Model

### Spark1 Questions:
1. Is m[13] = 8342 expressible as p[a] × p[b] where b = n + m[j]?
2. Is m[14] = 2034 = 2 × 3² × 113. Does 113 = p[30]. Is 30 = 14 + m[?]?
3. For m[15] = p[33] × p[45]: Is 33 or 45 related to n + m[k]?
4. m[16] = 8470 = 2×5×7×121. Is there a prime-index pattern?

### Box 211 Questions:
1. m[17] = p[12]² × p[26]. Is 12 or 26 = f(17, m[k])?
2. m[19] = 11 × 19 × 2699. Is 2699 a prime? What index?
3. What pattern governs when m[n] is PRIME vs COMPOSITE?
4. Can we predict m[71] using the discovered patterns?

## Success Criteria

A formula is VERIFIED if:
1. It produces the exact m[n] value
2. It uses only n and earlier m-values (m[2]...m[n-1])
3. It follows a consistent pattern with other verified formulas

## Timeline

- Phase 1 (Now): Deploy exploration tasks
- Phase 2 (30 min): Collect initial results
- Phase 3 (1 hour): Synthesize findings
- Phase 4: Document unified formula
