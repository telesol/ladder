# Drift Generator Research - Quick Start Guide

**Date**: 2025-12-18
**Status**: ✅ All scripts ready for distributed execution

---

## 📋 Overview

We have **1,104 drift values** (69 transitions × 16 lanes) and want to discover the generator function that creates them.

**Goal**: Find `drift[k][lane] = f(k, lane)` and unlock the ability to generate ALL 160 puzzles!

---

## 🚀 Quick Start (5 Steps)

### Step 1: Data Export (Already Done!)
```bash
cd /home/solo/LadderV3/kh-assist
python3 export_drift_data.py
```

**Output**: `drift_data_export.json` (46.8 KB, 69 transitions)

### Step 2: Copy to Research Machines

**Spark 1** (H1: Index-Based):
```bash
scp export_drift_data.py drift_data_export.json research_H1_index_based.py spark1:/path/
```

**Spark 2** (H2: Hash Functions):
```bash
scp export_drift_data.py drift_data_export.json research_H2_hash_function.py spark2:/path/
```

**ASUS B10 #1** (H3: PRNG):
```bash
scp export_drift_data.py drift_data_export.json research_H3_prng.py asus-b10-1:/path/
```

**ASUS B10 #2** (H4: Recursive):
```bash
scp export_drift_data.py drift_data_export.json research_H4_recursive.py asus-b10-2:/path/
```

### Step 3: Run on Each Machine

**On each machine**, run:
```bash
python3 research_H{X}_*.py > output.log 2>&1 &
```

**Expected runtimes**:
- H1 (Index-Based): 2-3 hours
- H2 (Hash Functions): 2-3 hours
- H3 (PRNG): 3-4 hours (includes brute force)
- H4 (Recursive): 2-3 hours

### Step 4: Collect Results

After all machines finish, copy back the result files:
```bash
scp spark1:/path/H1_results.json .
scp spark2:/path/H2_results.json .
scp asus-b10-1:/path/H3_results.json .
scp asus-b10-2:/path/H4_results.json .
```

### Step 5: Analyze Results
```bash
python3 analyze_all_results.py
```

**This will**:
- Rank all hypotheses by accuracy
- Identify the best approach
- Provide next steps recommendations

---

## 📊 What Each Hypothesis Tests

### H1: Index-Based Generator
**Theory**: `drift[k][lane] = f(k, lane)` (no dependency on X_k)

**Tests**:
- Statistical correlation
- Polynomial fits (degree 1-4)
- Modular arithmetic: `(mult*k + offset) mod 256`
- PySR symbolic regression (if available)

### H2: Cryptographic Hash Function
**Theory**: `drift = hash(k, lane) mod 256`

**Tests**:
- SHA256, MD5, SHA1, SHA512, RIPEMD160
- Bitcoin hashes (HASH256, HASH160)
- Different encodings (string, bytes, packed)
- Salted variations
- XOR combinations

### H3: PRNG (Pseudo-Random Number Generator)
**Theory**: `rng = PRNG(seed); drift = rng.next() mod 256`

**Tests**:
- Python random.Random()
- NumPy random
- LCG (Linear Congruential Generator)
- Mersenne Twister
- Brute force seed search (0-100,000)

### H4: Recursive Pattern (Drift Ladder)
**Theory**: `drift[k+1] = g(drift[k], k, lane)` (drift has its own ladder!)

**Tests**:
- Affine recurrence: `drift_next = A*drift + C mod 256`
- Polynomial recurrence: `drift_next = drift^n mod 256`
- Bridge spacing: `drift[k] = drift[k-5] + offset`
- Multi-step (Fibonacci-like, linear extrapolation)

---

## 🎯 Success Criteria

| Accuracy | Meaning | Action |
|----------|---------|--------|
| 100% | ✅ GENERATOR FOUND! | Generate puzzles 1-160 immediately! |
| 90-99% | 🔥 Very close | Refine winning hypothesis |
| 80-89% | 👍 Good progress | Combine multiple hypotheses |
| <80% | 🤔 More analysis | Try advanced techniques |

---

## 📁 Files Created

```
export_drift_data.py              ✅ Data export (46.8 KB output)
research_H1_index_based.py        ✅ Hypothesis 1 script (11K)
research_H2_hash_function.py      ✅ Hypothesis 2 script (12K)
research_H3_prng.py               ✅ Hypothesis 3 script (12K)
research_H4_recursive.py          ✅ Hypothesis 4 script (15K)
analyze_all_results.py            ✅ Results analysis (8.6K)
```

**Data file**:
```
drift_data_export.json            ✅ 1,104 drift values ready
```

**Expected outputs**:
```
H1_results.json                   ⏳ Pending
H2_results.json                   ⏳ Pending
H3_results.json                   ⏳ Pending
H4_results.json                   ⏳ Pending
analysis_report.json              ⏳ Pending
```

---

## 🔍 Monitoring Progress

Check if a machine is still running:
```bash
ps aux | grep research_H
```

Check partial results (if script prints progress):
```bash
tail -f output.log
```

---

## 💡 Tips

1. **Run in parallel** - All 4 machines can run simultaneously
2. **Use nohup** - Keep running if connection drops:
   ```bash
   nohup python3 research_H1_index_based.py > output.log 2>&1 &
   ```
3. **Check dependencies** - Most scripts only need Python 3 standard library
4. **PySR is optional** - H1 will skip PySR if not installed (doesn't affect other tests)

---

## 🚨 If 100% Match Found

If any hypothesis achieves 100% accuracy:

1. **Verify** - Re-run the winning script to confirm
2. **Document** - Note the exact formula/parameters
3. **Predict** - Use formula to generate puzzles 71-95
4. **Validate** - Compare with known bridge puzzles (75, 80, 85, 90, 95)
5. **Generate** - If validated, generate ALL puzzles 1-160!

---

## 📞 Next Steps After Analysis

See `analyze_all_results.py` output for specific recommendations based on results.

**Best case**: 100% match → Generate all puzzles immediately! 🎉

**Good case**: >90% match → Refine and combine approaches

**Learning case**: <90% → Advanced techniques (ML, genetic algorithms, etc.)

---

**Last updated**: 2025-12-18 15:10
**Status**: Ready for distributed execution! 🚀
