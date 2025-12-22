# Drift Generator Research Plan

**Date**: 2025-12-17
**Status**: 🚀 READY TO EXECUTE
**Objective**: Discover the generator function that creates drift values

---

## 🎯 Core Mission

**We have 1,184 drift values (74 transitions × 16 lanes)**

If the Bitcoin puzzle creator used a deterministic generator, we should be able to reverse-engineer it!

**Success = Calculate ALL puzzles 1-160 without needing any calibration data!**

---

## 🔬 Four Hypotheses (4xH)

### Hypothesis 1 (H1): Pure Index-Based Generator
**Theory**: Drift depends ONLY on puzzle number and lane
```python
drift[k→k+1][lane] = f(k, lane)
```

**Research Tasks**:
- [ ] Statistical analysis: Are drifts correlated with k? with lane?
- [ ] Plot drift vs puzzle_k for each lane
- [ ] Test polynomial fits: `drift = a*k^2 + b*k + c` per lane
- [ ] Test modular arithmetic patterns
- [ ] Run PySR with ONLY features (k, lane) → drift

**Expected Time**: 2-3 hours
**Machine Assignment**: Spark 1

---

### Hypothesis 2 (H2): Cryptographic Hash Function
**Theory**: Drift is derived from hashing (puzzle, lane)
```python
drift[k→k+1][lane] = hash_function(k, lane) mod 256
```

**Research Tasks**:
- [ ] Test SHA256(str(k) + str(lane))
- [ ] Test SHA256(k.to_bytes() + lane.to_bytes())
- [ ] Test MD5, SHA1, SHA512, RIPEMD160
- [ ] Test with various salt/seed values
- [ ] Test Bitcoin-specific hashes (HASH256, HASH160)
- [ ] Try combinations: `hash(k) XOR hash(lane)`

**Expected Time**: 2-3 hours
**Machine Assignment**: Spark 2

---

### Hypothesis 3 (H3): PRNG (Pseudo-Random Generator)
**Theory**: Drift comes from seeded random number generator
```python
rng = PRNG(seed=?)
for puzzle in range(1, 161):
    for lane in range(16):
        drift[puzzle][lane] = rng.next() mod 256
```

**Research Tasks**:
- [ ] Test Python's random.Random() with various seeds
- [ ] Test numpy.random with various seeds
- [ ] Test Mersenne Twister (MT19937)
- [ ] Test LCG (Linear Congruential Generator)
- [ ] Test crypto PRNGs (ChaCha20, AES-CTR)
- [ ] Brute-force seeds: Try 0-100000 and compare first 10 drifts

**Expected Time**: 3-4 hours (brute force may take longer)
**Machine Assignment**: ASUS B10 #1

---

### Hypothesis 4 (H4): Recursive Pattern (Drift Ladder)
**Theory**: Drift follows its own recurrence relation
```python
# Drift might have a ladder too!
drift[k+1][lane] = g(drift[k][lane], k, lane)
```

**Research Tasks**:
- [ ] Analyze drift sequences: drift[1][0], drift[2][0], drift[3][0]...
- [ ] Look for recurrence patterns in drift evolution
- [ ] Test: `drift_next = A_drift * drift_current + C_drift (mod 256)`
- [ ] Run PySR on: `(drift_k, k, lane) → drift_k+1`
- [ ] Check if drift has fixed points or cycles
- [ ] Test: `drift[k] = drift[k-5] + constant` (bridge spacing pattern)

**Expected Time**: 2-3 hours
**Machine Assignment**: ASUS B10 #2

---

## 🎼 Orchestration Plan (Claude's Role)

### Phase 1: Setup (Before you leave)
- [x] Create this research plan document
- [ ] Generate 4 independent research scripts (one per hypothesis)
- [ ] Create shared data file: `drift_data_export.json` (all 74 transitions)
- [ ] Create result template: `H{1-4}_results.json`

### Phase 2: Execution (While you're away)
Each machine runs independently:
```bash
# Spark 1
python3 research_H1_index_based.py > H1_results.json

# Spark 2
python3 research_H2_hash_function.py > H2_results.json

# ASUS B10 #1
python3 research_H3_prng.py > H3_results.json

# ASUS B10 #2
python3 research_H4_recursive.py > H4_results.json
```

### Phase 3: Analysis (When you return)
- [ ] Collect all 4 result files
- [ ] Rank by accuracy (% of drift values matched)
- [ ] If any hypothesis hits 100% → WE FOUND IT!
- [ ] If none hit 100% → Combine best insights
- [ ] Generate final report

---

## 📊 Success Criteria

| Hypothesis | Minimum Success | Perfect Success |
|------------|----------------|-----------------|
| H1: Index  | >80% accuracy  | 100% match |
| H2: Hash   | >80% accuracy  | 100% match |
| H3: PRNG   | >80% accuracy  | 100% match |
| H4: Recursive | >80% accuracy | 100% match |

**If we find 100% match**: We can generate puzzles 1-160 immediately!

**If we find >90% match**: We're close, might need hybrid approach

**If all <80%**: Pattern is more complex, need advanced techniques

---

## 🔧 Data Export Format

```json
{
  "transitions": [
    {
      "from_puzzle": 1,
      "to_puzzle": 2,
      "drifts": [129, 91, 1, ...],  // 16 values
      "X_k": [0, 0, 0, ...],        // Starting state (16 bytes)
      "X_k_plus_1": [1, 0, 0, ...]  // Ending state (16 bytes)
    },
    ...
  ],
  "A_coefficients": [1, 91, 1, 1, 1, 169, 1, 1, 1, 32, 1, 1, 1, 182, 1, 1]
}
```

---

## 🚀 Quick Start Commands

### Setup (Do this before leaving)
```bash
cd /home/solo/LadderV3/kh-assist

# Export drift data
python3 export_drift_data.py

# Verify data export
cat drift_data_export.json | head -20
```

### Distribute to Machines
```bash
# Copy research scripts to each machine
scp research_H1_index_based.py spark1:/path/
scp research_H2_hash_function.py spark2:/path/
scp research_H3_prng.py asus-b10-1:/path/
scp research_H4_recursive.py asus-b10-2:/path/

# Copy shared data to all
scp drift_data_export.json [all-machines]:/path/
```

### Run on Each Machine
```bash
# Each machine runs its hypothesis
python3 research_H{X}_*.py --output results.json

# Results will show:
# - Accuracy percentage
# - Which drifts matched
# - Discovered parameters (if any)
```

---

## 📞 When You Return

Read this file first, then:
```bash
# Collect results
cat H1_results.json H2_results.json H3_results.json H4_results.json

# See which hypothesis won
python3 analyze_all_results.py

# If we found the generator:
python3 generate_all_puzzles_1_to_160.py  # 🎉
```

---

## 💡 Key Insights to Remember

1. **We have enough data** - 1,184 drift values is A LOT
2. **If it's deterministic, we WILL find it** - Math doesn't lie
3. **Parallel research** - 4 machines = 4x faster
4. **Pattern MUST exist** - Bitcoin creator didn't use 160 random numbers

---

## 🎯 Expected Breakthrough

**Best case**: One hypothesis hits 100% → Game over, we win! 🏆

**Good case**: Multiple hypotheses >90% → Combine for 100%

**Learning case**: All <80% but we learn the structure → Refine approach

---

**Status**: Ready for distributed execution
**Next Step**: Create the 4 research scripts (I'll do this now if you want)
**Your Move**: Go home, return when ready to see results!

🚀 Let's discover this generator!
