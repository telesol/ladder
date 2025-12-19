# Bitcoin Puzzle Formula Discovery Guide

**Project Start:** December 2024
**Last Updated:** 2025-12-19
**Status:** Active Research

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [The Core Formula](#the-core-formula)
3. [Verified Discoveries](#verified-discoveries)
4. [Failed Hypotheses](#failed-hypotheses)
5. [Open Questions](#open-questions)
6. [Model Evaluation](#model-evaluation)
7. [Research Log](#research-log)
8. [Next Steps](#next-steps)

---

## Project Overview

### Goal
Reverse-engineer the **key generation formula** used by the Bitcoin Puzzle creator to generate private keys k1-k160. We have 74 known keys (k1-k70, k75, k80, k85, k90) and want to derive the remaining 86.

### What We're NOT Doing
- Brute force searching
- Guessing/predicting keys
- Statistical analysis without mathematical basis

### What We ARE Doing
- Mathematical pattern analysis
- Formula derivation from known data
- Convergent analysis (π, e, sqrt(3), φ)
- Sequence reconstruction

---

## The Core Formula

### Primary Recurrence (100% VERIFIED)
```
k_n = 2 × k_{n-1} + adj_n
```
Where:
```
adj_n = 2^n - m_n × k_{d_n}
```

### What We Know
| Component | Status | Notes |
|-----------|--------|-------|
| k_n recurrence | **VERIFIED** | Works for all 70 known keys |
| m_n sequence | **KNOWN** | Have values for n=2..70 |
| d_n sequence | **KNOWN** | Have values for n=2..70 |
| m_n generation rule | **UNKNOWN** | This is the barrier |
| d_n generation rule | **UNKNOWN** | Secondary barrier |

### The Sequences (n=2 to 21)
```
m: 3, 7, 22, 9, 19, 50, 23, 493, 19, 1921, 1241, 8342, 2034, 26989, 8470, 138269, 255121, 564091, 900329, 670674
d: 1, 1, 1, 2, 2, 2, 4, 1, 7, 1, 2, 1, 4, 1, 4, 1, 1, 1, 1, 2
```

### Normalization Constraint
```
norm_m = m_n / 2^(n - d_n) must be in [0.72, 2.75]
```
This constraint is satisfied by ALL 70 known values.

---

## Verified Discoveries

### 1. π Convergent Seeding (VERIFIED)
```
m[2] = 3   ← π convergent numerator (3/1)
m[3] = 7   ← π convergent denominator (22/7)
m[4] = 22  ← π convergent numerator (22/7)
```
**Source:** π = [3; 7, 15, 1, 292, ...]

### 2. Transition Rule at n=5 (UPDATED)
```
m[5] = 9 = ln(2) convergent numerator (9/13)
```
**Also:** 9 = digit_sum(333) where 333 is π convergent - dual meaning?

### 3. e Convergent Integration (VERIFIED)
```
m[6] = 19  ← e convergent numerator (19/7)
m[7]/m[6] = 50/19 ≈ 2.63 (approximates e = 2.718)
```
**Source:** e = [2; 1, 2, 1, 1, 4, 1, 1, 6, ...]

### 4. sqrt(3) Connection (NEW - 2025-12-19)
```
sqrt(3) convergent numerators: 1, 2, 5, 7, 19, 26, 71, 97, 265...
                                          ↑
                                      h_4 = 19 = m[6]!
```
This may explain why 19 appears at m[6] AND m[10].

### 5. The "19 Mystery"
```
m[6]  = 19
m[10] = 19  (same value!)
m[11] = 1921 = 19 × 101
```
19 appears multiple times - likely not coincidence.

### 6. Fibonacci in k-sequence (VERIFIED)
```
k[1] = 1   (F_1)
k[2] = 3   (F_4)
k[4] = 8   (F_6)
k[5] = 21  (F_8)
```

### 7. Product Relationship (VERIFIED)
```
m[2] × m[3] = 3 × 7 = 21 = k[5]
```

### 8. Convergent Coverage Analysis (2025-12-19)
```
Computed convergents for: π, e, sqrt(2), sqrt(3), φ, ln(2)
Cross-referenced all 30 m-values (n=2..31)

RESULT: Only 6/30 are direct convergents!
- m[2]=3, m[3]=7: Multiple constants
- m[4]=22: π only
- m[5]=9: ln(2) convergent
- m[6]=19, m[10]=19: e and sqrt(3)

UNKNOWN SOURCE: m[7..31] (24 values) - NOT direct convergents
```

---

## Failed Hypotheses

### DO NOT RETRY THESE - They don't work:

| Hypothesis | Tested By | Result |
|------------|-----------|--------|
| d_n = floor(log2(m_n)) | phi4:14b | Only 2/15 matches (13%) |
| m_n from LFSR/PRNG | deepseek-r1:70b | No pattern found |
| Pure digit_sum for all m | mixtral:8x22b | Only works for m[5] |
| m_n = f(m_{n-1}, m_{n-2}) simple recurrence | qwq:32b | Doesn't match |
| Alternating e-step/π-step for n≥8 | phi4:14b | Base cases only |

---

## Open Questions

### Priority 1: m_n Generation Rule
- How are m values generated for n ≥ 8?
- What determines when to use π vs e vs sqrt(3)?
- Is there a unified formula?

### Priority 2: d_n Generation Rule
- What determines d values?
- d[10] = 7 is unusually large - why?
- Is d related to n, m, or something else?

### Priority 3: The 19 Mystery
- Why does 19 appear at n=6 and n=10?
- Is sqrt(3) the source?
- What's special about 19 × 101 = 1921?

### Priority 4: Constant Transitions
- n=2,3,4: π phase
- n=5: transition (digit_sum)
- n=6,7: e phase
- n≥8: ???

---

## Model Evaluation

### Available Models & Performance

| Model | Size | Location | Best For | Limitations |
|-------|------|----------|----------|-------------|
| **qwq:32b** | 19GB | Spark1 | Deep reasoning, exploring hypotheses | Can get stuck in loops |
| **phi4-reasoning:14b** | 11GB | Spark1/2 | Algorithm construction, pseudocode | Proposes untested formulas |
| **deepseek-r1:70b** | 42GB | Box 211 | Mathematical analysis, convergents | Slow, verbose |
| **mixtral:8x22b** | 79GB | Box 212 | Breadth exploration | Can't do actual computation |
| **qwen3-vl:8b** | 6GB | Spark2 | Fast verification | Limited depth |

### Model Performance Summary (2025-12-19 Explorations)

| Model | Task | Output | Actionable Insight? |
|-------|------|--------|---------------------|
| qwq:32b | 19 Mystery | 631 lines | Partial - explored many angles |
| phi4:14b | D-Sequence | 634 lines | No - formula failed verification |
| mixtral:8x22b | Bitwise XOR | 27 lines | No - only suggestions |
| deepseek-r1:70b | Constants | 538+ lines | **YES** - found sqrt(3) link |

### Recommendations (Updated 2025-12-19)

**STOP USING:**
- mixtral:8x22b - 79GB VRAM wasted, said "I can't compute", only 27 lines output

**For Deep Mathematical Analysis:**
- Use deepseek-r1:70b - best at convergent calculations
- Give 1-2 hour timeouts (not 6 hours - diminishing returns)
- Provide full context data

**For Algorithm Construction:**
- Use phi4-reasoning:14b
- Always verify output against actual data
- Don't trust proposed formulas without testing

**For Broad Exploration:**
- Use qwq:32b
- Good for generating hypotheses to test
- May need guidance to avoid loops

**For ALL Verification:**
- Use Python scripts directly (convergent_database.py)
- NEVER trust LLM mathematical claims without code verification
- Computation-first, philosophy second

---

## Research Log

### Session: 2025-12-18
- Launched 6-hour parallel explorations on 4 models
- Confirmed π convergent seeding (m[2,3,4])
- Confirmed digit_sum transition (m[5])
- Confirmed e convergent (m[6,7])

### Session: 2025-12-19 (Morning)
- Reviewed 6-hour exploration results
- phi4 proposed alternating e/π algorithm - works for base cases only
- qwq analyzed 19 mystery - no definitive answer
- mixtral suggested XOR approach - not computed
- deepseek concluded "non-trivial pattern"

### Session: 2025-12-19 (Current)
- Launched 2-hour targeted explorations
- **NEW DISCOVERY:** sqrt(3) convergent h_4 = 19 matches m[6]
- This may explain the 19 mystery
- deepseek still running, exploring more constants

---

## Next Steps

### Immediate (Today)
1. Wait for deepseek to complete sqrt(3)/constants analysis
2. Verify if sqrt(3) explains m[10] = 19
3. Check if other m values appear in sqrt(3) convergents

### Short-term
1. Build a convergent database (π, e, sqrt(3), φ, sqrt(2))
2. Cross-reference all m values against convergent numerators/denominators
3. Test if m[n] can be expressed as f(convergent[i], convergent[j])

### Medium-term
1. Investigate modular arithmetic patterns in d-sequence
2. Look for Bitcoin/secp256k1 constant connections
3. Consider if puzzle creator used specific mathematical software

### Do NOT Pursue (Already Failed)
- Simple PRNG reverse engineering
- d_n = floor(log2(m_n))
- Pure recurrence m[n] = f(m[n-1], m[n-2])

---

## Quick Reference

### Database Query
```bash
sqlite3 db/kh.db "SELECT puzzle_id, priv_hex FROM keys WHERE puzzle_id=66;"
```

### Check Exploration Status
```bash
./check_2hr_exploration.sh
```

### Key Files
- `puzzle_config.py` - Load all data programmatically
- `db/kh.db` - Main database with 74 known keys
- `EXPLORATION_RESULTS_2025-12-19.md` - Latest findings
- `CONSTRUCTION_SYNTHESIS.md` - Mathematical synthesis

### Cluster Setup
| Box | IP | Models | GPU |
|-----|-----|--------|-----|
| Spark1 | localhost | qwq:32b, phi4:14b | NVIDIA |
| Spark2 | 10.0.0.2 | phi4:14b, qwen3-vl:8b | NVIDIA |
| Box 212 | 192.168.111.212 | mixtral:8x22b | NVIDIA |
| Box 211 | 192.168.111.211 | deepseek-r1:70b | NVIDIA |

---

## Contributing

When adding new findings:
1. **VERIFY** against actual database values before claiming discovery
2. **DOCUMENT** in this guide under appropriate section
3. **LOG** the session date and what was tried
4. **UPDATE** Failed Hypotheses if something doesn't work
5. **COMMIT** changes to git with descriptive message

---

*This guide is the single source of truth for the project. Update it regularly.*
