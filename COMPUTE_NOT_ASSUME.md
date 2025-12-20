# COMPUTE, DON'T ASSUME

## The k[71] Failure

We ASSUMED:
- Offset ratio ≈ 1.67 (extrapolation)
- Pattern would continue (assumption)

Result: WRONG ADDRESS. Puzzle 71 still UNSOLVED.

## The Correct Approach

We have 70 KNOWN keys. For each n=2..70:
- k[n] is KNOWN (from database)
- k[n] = 2*k[n-1] + adj[n]
- adj[n] = 2^n - m[n]*k[d[n]]

Therefore m[n] and d[n] can be COMPUTED, not assumed:
1. adj[n] = k[n] - 2*k[n-1]  ← COMPUTE from known keys
2. For each candidate d: m = (2^n - adj[n]) / k[d]  ← COMPUTE
3. d[n] = the d that gives integer m[n]  ← VERIFY

## What We KNOW (computed, not assumed)

From database analysis:
- d[n] is chosen to MINIMIZE m[n] (67/69 verified)
- m[2]=m[3]=1 via self-reference d[n]=n
- First 3 keys are Mersenne: k[1]=1, k[2]=3, k[3]=7

## What We DON'T Know Yet

- WHY specific m[n] values are chosen
- The construction rule that GENERATES m[n]
- How to extend to n=71 without known k[71]

## The Real Question

Given ONLY k[1..70], k[75], k[80], k[85], k[90]:
Can we derive the rule that GENERATES k[n] for any n?

This requires finding the m[n] generation rule - NOT extrapolating patterns.
