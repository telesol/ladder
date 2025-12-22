# Task 5 Results - Regime-Specific Analysis for Lanes 0-6

**Date**: 2025-12-22
**Approach**: Regime-specific baseline prediction (most common drift value per regime)
**Goal**: Test if separating training by transition rate regime improves accuracy

---

## Executive Summary

**Conclusion**: **REGIME-SPECIFIC APPROACH DOES NOT HELP**

Regime separation (stable/moderate/complex based on k value) provides **ZERO improvement** over simple global baseline for all 7 lanes tested.

**Result**: 0/7 lanes showed improvement

---

## Regimes Defined

| Regime | k Range | Transition Rate | Description |
|--------|---------|----------------|-------------|
| **Stable** | k < 32 | 6-25% | Early puzzles, low complexity |
| **Moderate** | 32 ≤ k < 64 | 25-48% | Mid puzzles, increasing complexity |
| **Complex** | k ≥ 64 | 52%+ | Late puzzles, high complexity |

---

## Results by Lane

### Lane 0

| Regime | Train Samples | Test Samples | Unique Values | Mean | Std | Trans% |
|--------|--------------|--------------|---------------|------|-----|--------|
| Stable | 24 | 3 | 24 | 111.9 | 90.0 | 100.0% |
| Moderate | 27 | 1 | 26 | 97.9 | 78.4 | 100.0% |
| Complex | 4 | 1 | 4 | 198.8 | 33.3 | 100.0% |

**Accuracy**:
- Simple (most common): **0.00%** (predicts 2)
- Regime-aware: **0.00%** (stable→1, moderate→61, complex→147)
- **Improvement: +0.00%**

**Analysis**: Extremely high diversity (50 unique values in 55 samples), 100% transition rate across all regimes. Drift is too chaotic for simple baseline prediction.

---

### Lane 1

| Regime | Train Samples | Test Samples | Unique Values | Mean | Std | Trans% |
|--------|--------------|--------------|---------------|------|-----|--------|
| Stable | 27 | 3 | 22 | 117.3 | 90.9 | 81.5% |
| Moderate | 25 | 5 | 24 | 99.4 | 73.5 | 96.0% |
| Complex | 4 | 1 | 4 | 128.5 | 54.8 | 100.0% |

**Accuracy**:
- Simple (most common): **22.22%** (predicts 0)
- Regime-aware: **22.22%** (stable→0, moderate→36, complex→77)
- **Improvement: +0.00%**

**Analysis**: Some zeros in stable regime (18.5%), but still very high unique value count. Regime-aware predicts different values per regime but provides no advantage.

---

### Lane 2

| Regime | Train Samples | Test Samples | Unique Values | Mean | Std | Trans% |
|--------|--------------|--------------|---------------|------|-----|--------|
| Stable | 24 | 4 | 13 | 42.5 | 69.2 | 50.0% |
| Moderate | 22 | 6 | 19 | 128.6 | 65.4 | 100.0% |
| Complex | 6 | 0 | 6 | 164.5 | 61.6 | 100.0% |

**Accuracy**:
- Simple (most common): **20.00%** (predicts 0)
- Regime-aware: **20.00%** (stable→0, moderate→45, complex→33)
- **Improvement: +0.00%**

**Analysis**: Stable regime shows only 50% transition rate (better), but moderate/complex still 100%. No test samples in complex regime.

---

### Lane 3

| Regime | Train Samples | Test Samples | Unique Values | Mean | Std | Trans% |
|--------|--------------|--------------|---------------|------|-----|--------|
| Stable | 25 | 0 | 9 | 7.4 | 17.7 | 32.0% |
| Moderate | 28 | 1 | 28 | 136.4 | 70.5 | 100.0% |
| Complex | 5 | 1 | 5 | 138.2 | 79.6 | 100.0% |

**Accuracy**:
- Simple (most common): **0.00%** (predicts 0)
- Regime-aware: **0.00%** (stable→0, moderate→4, complex→38)
- **Improvement: +0.00%**

**Analysis**: Stable regime shows promise (68% zeros, 32% transition rate), but no test samples. Moderate/complex remain 100% chaotic.

---

### Lane 4

| Regime | Train Samples | Test Samples | Unique Values | Mean | Std | Trans% |
|--------|--------------|--------------|---------------|------|-----|--------|
| Stable | 27 | 3 | 1 | 0.0 | 0.0 | 0.0% |
| Moderate | 26 | 4 | 25 | 79.7 | 75.7 | 100.0% |
| Complex | 5 | 0 | 5 | 72.8 | 81.7 | 100.0% |

**Accuracy**:
- Simple (most common): **42.86%** (predicts 0)
- Regime-aware: **42.86%** (stable→0, moderate→1, complex→13)
- **Improvement: +0.00%**

**Analysis**: **Stable regime is PERFECT** (100% zeros, 0% transition rate). But moderate/complex explode to 100% chaos. Regime-aware correctly predicts stable=0 but doesn't help overall.

---

### Lane 5

| Regime | Train Samples | Test Samples | Unique Values | Mean | Std | Trans% |
|--------|--------------|--------------|---------------|------|-----|--------|
| Stable | 27 | 2 | 1 | 0.0 | 0.0 | 0.0% |
| Moderate | 27 | 3 | 18 | 85.3 | 78.7 | 70.4% |
| Complex | 6 | 0 | 6 | 83.8 | 73.6 | 100.0% |

**Accuracy**:
- Simple (most common): **40.00%** (predicts 0)
- Regime-aware: **40.00%** (stable→0, moderate→0, complex→6)
- **Improvement: +0.00%**

**Analysis**: Stable perfect (100% zeros). Moderate shows some repetition (18 unique in 27 samples, 70.4% transition). Complex still 100% chaotic.

---

### Lane 6

| Regime | Train Samples | Test Samples | Unique Values | Mean | Std | Trans% |
|--------|--------------|--------------|---------------|------|-----|--------|
| Stable | 25 | 3 | 1 | 0.0 | 0.0 | 0.0% |
| Moderate | 24 | 3 | 11 | 26.5 | 55.3 | 45.8% |
| Complex | 5 | 0 | 5 | 129.8 | 86.7 | 100.0% |

**Accuracy**:
- Simple (most common): **100.00%** (predicts 0)
- Regime-aware: **100.00%** (stable→0, moderate→0, complex→1)
- **Improvement: +0.00%**

**Analysis**: **BEST LANE**. Stable perfect (100% zeros). Moderate shows **lowest transition rate of all lanes** (45.8%). Test samples all happen to be zeros, so both baselines achieve 100%.

---

## Key Findings

### 1. Stable Regime Behavior (k < 32)

**Lanes 0-3**: Chaotic (81-100% transition rates)
**Lanes 4-6**: **PERFECTLY STABLE** (0% transition rate, 100% zeros)

**Conclusion**: Lanes 4-6 have a **regime transition at k=32**. Before k=32, drift is always zero. After k=32, drift becomes chaotic.

---

### 2. Moderate Regime Behavior (32 ≤ k < 64)

**All lanes**: 45-100% transition rates (still very high)
**Best**: Lane 6 at 45.8% transition rate (lowest observed)

**Conclusion**: Even in "moderate" regime, drift remains highly unpredictable for most lanes.

---

### 3. Complex Regime Behavior (k ≥ 64)

**All lanes**: 100% transition rate (where data exists)

**Conclusion**: Past k=64, drift is completely chaotic. No repetition, no patterns.

---

### 4. Why Regime-Specific Doesn't Help

**Problem**: Regime-aware baseline learns "most common value per regime", but:

1. **Too much diversity**: Even within regimes, unique value count is near sample count
2. **Test distribution mismatch**: Test samples don't match training distribution
3. **Small regime sizes**: Complex regime has only 4-6 training samples
4. **No generalization**: "Most common value" doesn't generalize when every value appears once

**Example (Lane 0)**:
- Stable regime trains on 24 samples (24 unique values)
- Learns "most common = 1"
- Test samples are: 115, 195, 229 (none match!)
- Result: 0% accuracy

---

## Comparison with Task 4 (H4: Recursive)

| Lane | Task 4 H4 Accuracy | Task 5 Simple Baseline | Task 5 Regime Baseline | Winner |
|------|-------------------|----------------------|----------------------|--------|
| 0 | 6% | 0% | 0% | **H4** |
| 1 | 71% | 22% | 22% | **H4** |
| 2 | 7% | 20% | 20% | **Task 5** |
| 3 | 21% | 0% | 0% | **H4** |
| 4 | 23% | 43% | 43% | **Task 5** |
| 5 | 10% | 40% | 40% | **Task 5** |
| 6 | 50% | 100% | 100% | **Task 5** |

**Note**: Task 5 baselines use mode (most common value), while H4 used drift_prev features. Different approaches.

---

## Final Conclusion

### Does Regime-Specific Help?

**NO - 0/7 lanes improved**

Regime separation provides no advantage over simple global baseline for these reasons:

1. **Drift values are too unique** - Even within regimes, almost every transition has a unique drift value
2. **100% transition rates** - Most regimes show no repetition at all
3. **Small sample sizes** - Complex regime has only 4-6 samples (not enough to learn patterns)
4. **Test distribution mismatch** - Test samples don't match training distribution

### What We Learned

✅ **Lanes 4-6 have a clear regime boundary at k=32** (zeros before, chaos after)
✅ **Lane 6 is the "best" lane** (lowest transition rates, most zeros)
✅ **Complex regime (k≥64) is 100% chaotic** across all lanes
❌ **Simple baselines (mode prediction) fail** on chaotic drift data
❌ **Regime separation doesn't help** when patterns don't exist within regimes

### Next Steps

**Recommendation**: **ABANDON regime-specific approaches for lanes 0-6**

Instead:
1. **Focus on lanes 7-8** (higher accuracy in H4: 82-92%)
2. **Use advanced ML** (not PySR - too slow, not enough patterns for symbolic regression)
3. **Try ensemble methods** combining multiple weak predictors
4. **Accept limits**: Lanes 0-6 may be fundamentally unpredictable (cryptographic drift)

---

**Status**: ✅ COMPLETE
**Files**: `results/task5_regime_specific.json`, `task5_analysis.py`
**Runtime**: ~2 minutes (analysis only, no PySR training)
