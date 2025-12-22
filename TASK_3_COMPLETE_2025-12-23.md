# TASK 3 Complete - PySR Training Script Ready

**Date**: 2025-12-23
**Task**: TASK 3 - Prepare PySR Training Script
**Status**: ✅ **COMPLETE**
**Next**: TASK 4 - Run PySR Training (2-8 hours)

---

## Summary

Created complete PySR training infrastructure for discovering the drift evolution formula.

---

## What Was Created

### 1. Main Training Script ✅

**Location**: `experiments/01-pysr-symbolic-regression/drift_formula/train_drift_evolution.py`

**Features**:
- Extracts 332 evolution values (k > lane×8) from transitions 1-69
- Features: k, lane, steps_since_activation, exponent
- Train/val split: puzzles 1-55 (216 samples) / 56-69 (116 samples)
- PySR configuration optimized for CPU training
- Outputs: model file (.pkl) + equations (.csv)

**Configuration**:
```python
Binary operators: ["+", "-", "*", "/", "mod"]
Unary operators: ["square", "cube", "abs"]
Max size: 20
Max depth: 8
Iterations: 100
Populations: 15
```

### 2. Data Loading Test Script ✅

**Location**: `experiments/01-pysr-symbolic-regression/drift_formula/test_data_loading.py`

**Purpose**: Verify data extraction logic before full training

**Result**: ✅ **PASSED** - 332 values extracted correctly

### 3. Documentation ✅

**Location**: `experiments/01-pysr-symbolic-regression/drift_formula/README.md`

**Contents**:
- Context and goal explanation
- Data statistics and per-lane breakdown
- Usage instructions for both scripts
- Strategy options (unified vs per-lane)
- Critical data correction (multiples of 16 myth)
- Expected results and next steps

---

## Critical Discovery: LLM Analysis Error

**LLM Claim**: ">95% of drift values are multiples of 16"

**Reality**:
- **ALL drift** (1,104 values): 71% multiples of 16
  (because 763 inactive values are all 0!)
- **EVOLUTION drift** (332 values): **6.3%** multiples of 16
  (this is what we train on!)

**Why the error**: LLM analyzed all data without filtering inactive zeros.

**Impact**: Removed quantization assumptions from training script.

---

## Data Statistics

### Overall
- Total evolution values: 332
- Drift range: [0, 254]
- Drift mean: 112.93 ± 78.90
- Multiples of 16: 21/332 = 6.3%

### Per-Lane Distribution
```
Lane 0:  68 values, drift ∈ [  1, 254], mean=124.0, exp=3
Lane 1:  61 values, drift ∈ [  0, 248], mean=128.0, exp=2
Lane 2:  53 values, drift ∈ [  2, 249], mean=113.1, exp=3
Lane 3:  45 values, drift ∈ [  2, 246], mean=120.0, exp=2
Lane 4:  37 values, drift ∈ [  1, 239], mean=84.8, exp=2
Lane 5:  29 values, drift ∈ [  1, 225], mean=123.2, exp=3
Lane 6:  21 values, drift ∈ [  1, 246], mean=91.6, exp=0
Lane 7:  13 values, drift ∈ [  1, 219], mean=90.6, exp=2
Lane 8:   5 values, drift ∈ [  1,  36], mean=10.2, exp=2
```

**Note**: High variance in per-lane means suggests formula may involve lane-specific constants or lane-dependent logic.

### Train/Val Split
- Training: puzzles 1-55 → 216 samples (65%)
- Validation: puzzles 56-69 → 116 samples (35%)

---

## How to Run (TASK 4)

```bash
cd /home/solo/LadderV3/kh-assist

# Activate venv with PySR
source experiments/01-pysr-symbolic-regression/.venv/bin/activate

# Run training (2-8 hours)
python3 experiments/01-pysr-symbolic-regression/drift_formula/train_drift_evolution.py

# Or run in background with logging
nohup python3 experiments/01-pysr-symbolic-regression/drift_formula/train_drift_evolution.py > pysr_training.log 2>&1 &

# Monitor progress
tail -f pysr_training.log
```

---

## Expected Outcomes

### Level 4: 100% Match ✅ FORMULA FOUND!
- Proceed immediately to TASK 6 (validation on X_75)
- Use formula to generate transitions 70→75
- If X_75 matches bridge → generate ALL puzzles 71-160!

### Level 3: 90-99% Match 🔥 EXCELLENT
- Very close! Analyze errors
- Refine formula or try ensemble approach
- Likely ready for TASK 6

### Level 2: 70-90% Match 👍 GOOD
- Promising progress
- Try per-lane models
- May need more iterations or different operators

### Level 1: 50-70% Match 🤔 LEARNING
- Pattern partially detected
- Increase iterations (200-500)
- Consider state-dependent features (X_k values)

### <50% Match 🔬 RESEARCH NEEDED
- May need different approach
- Consider adding X_k[lane] as feature
- Try neural network (experiments/05-ai-learns-ladder)

---

## Files Created

```
experiments/01-pysr-symbolic-regression/drift_formula/
├── README.md                      ← Documentation
├── train_drift_evolution.py       ← Main training script (executable)
├── test_data_loading.py           ← Quick test (✅ passed)
└── results/                       ← Output directory (created automatically)
    ├── drift_model_unified.pkl    ← (generated after training)
    └── drift_equations_unified.csv ← (generated after training)
```

---

## Validation Plan (After Training)

Once PySR training completes with ≥90% accuracy:

**TASK 6: Validate by Generating X_70→X_75**

```python
# 1. Use discovered formula to GENERATE drift
drift_70_to_71 = discovered_formula(k=70, lane=0..15)
drift_71_to_72 = discovered_formula(k=71, lane=0..15)
drift_72_to_73 = discovered_formula(k=72, lane=0..15)
drift_73_to_74 = discovered_formula(k=73, lane=0..15)
drift_74_to_75 = discovered_formula(k=74, lane=0..15)

# 2. Calculate unknown puzzles using GENERATED drift
X_71 = (X_70^n + drift_70_to_71) mod 256
X_72 = (X_71^n + drift_71_to_72) mod 256
X_73 = (X_72^n + drift_72_to_73) mod 256
X_74 = (X_73^n + drift_73_to_74) mod 256
X_75 = (X_74^n + drift_74_to_75) mod 256

# 3. Validate
if X_75_calculated == X_75_bridge:
    print("✅ SUCCESS! Formula works!")
    # Generate puzzles 71-160
```

---

## Known Limitations

1. **Small training set** (332 samples)
   - May not be enough for complex formulas
   - Solution: Try per-lane models (smaller, simpler problems)

2. **Unbalanced lane data**
   - Lane 0: 68 samples, Lane 8: 5 samples
   - May affect unified model accuracy
   - Solution: Train per-lane models

3. **No state-dependent features**
   - Current features: k, lane, steps, exponent
   - Drift may depend on X_k[lane] values
   - Solution: Add X_k as feature if needed

4. **CPU training** (no GPU acceleration)
   - PySR is CPU-based (evolutionary algorithm)
   - Training time: 2-8 hours on modern CPU
   - Solution: Increase iterations if needed, or use parallel populations

---

## Technical Notes

### Why No Quantization Operators?

Initial LLM analysis suggested ">95% multiples of 16", but this was based on all drift values including inactive zeros. Evolution drift is only 6.3% multiples of 16, so quantization is NOT a pattern.

### Why Unified Model First?

If drift has a universal formula `drift = f(k, lane, exponent)`, unified training will find it faster than per-lane. If no universal formula exists, validation accuracy will be low (<70%), and we'll switch to per-lane models.

### Why Train/Val Split at Puzzle 55?

- Training needs enough samples (216 is reasonable for PySR)
- Validation needs different k values to test generalization
- Split ensures both sets have data from all active lanes

---

## Status Summary

- ✅ **TASK 1**: LLM Analysis complete (Nemotron + GPT-OSS)
- ✅ **TASK 2**: Data validation complete (69 transitions, 332 evolution values)
- ✅ **TASK 3**: PySR training script ready ← **WE ARE HERE**
- ⏳ **TASK 4**: Run PySR training (NEXT)
- ⏳ **TASK 5**: Integrate findings
- ⏳ **TASK 6**: Validate on X_75
- ⏳ **TASK 7**: Generate puzzles 71-95

---

## Next Actions

**Option A: Run Training Now**
```bash
cd /home/solo/LadderV3/kh-assist
source experiments/01-pysr-symbolic-regression/.venv/bin/activate
nohup python3 experiments/01-pysr-symbolic-regression/drift_formula/train_drift_evolution.py > pysr_training.log 2>&1 &
```

**Option B: Wait for User Decision**
- Training takes 2-8 hours
- User may want to review script first
- User may want to adjust configuration

---

**Completed**: 2025-12-23
**Duration**: ~1 hour (analysis + scripting + testing)
**Result**: ✅ Ready for TASK 4 (PySR training)
**Blocker**: None - all dependencies verified (PySR installed in venv)

---

**The drift formula is within reach!** 🚀
