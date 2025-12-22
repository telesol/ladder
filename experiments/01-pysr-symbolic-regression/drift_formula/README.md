# Drift Formula Discovery - PySR Training

**Created**: 2025-12-23
**Purpose**: Discover the evolution formula for `drift[k][lane]` when `k > lane × 8`

## Context

We have the complete recurrence formula:
```python
X_{k+1}[lane] = ((X_k[lane])^n + drift[k][lane]) mod 256
```

Where:
- `n = EXPONENTS[lane]` = [3, 2, 3, 2, 2, 3, 0, 2, 2, 3, 3, 2, 2, 2, 2, 3]
- Drift formula is 70% known, 30% unknown (evolution phase)

**Known drift rules**:
- Rule 1: `drift[k][lane] = 0` if `k < lane × 8` (100% proven, 763 values)
- Rule 2: `drift[k][lane] = 1` if `k == lane × 8` (100% proven, 8 lanes)
- **UNKNOWN**: `drift[k][lane] = ???` if `k > lane × 8` (332 values, 30%)

**Goal**: Discover the evolution formula to **GENERATE** drift for transitions 70+

## Data

**Source**: `/home/solo/LadderV3/kh-assist/drift_data_CORRECT_BYTE_ORDER.json`

**Training data**:
- 69 transitions (puzzles 1→70 only)
- 332 evolution values (k > lane×8)
- Lanes 0-8 only (lanes 9-15 never activated in our data)

**Statistics**:
- Drift range: [0, 254]
- Drift mean: 112.93 ± 78.90
- **Multiples of 16**: 6.3% (NOT 95% as LLM suggested!)
- Distribution: Nearly uniform across mod 16

**Per-lane counts**:
```
Lane 0: 68 values (exponent=3)
Lane 1: 61 values (exponent=2)
Lane 2: 53 values (exponent=3)
Lane 3: 45 values (exponent=2)
Lane 4: 37 values (exponent=2)
Lane 5: 29 values (exponent=3)
Lane 6: 21 values (exponent=0)
Lane 7: 13 values (exponent=2)
Lane 8:  5 values (exponent=2)
```

## Scripts

### 1. `test_data_loading.py`

Quick test to verify data extraction works correctly.

**Run**:
```bash
cd /home/solo/LadderV3/kh-assist
python3 experiments/01-pysr-symbolic-regression/drift_formula/test_data_loading.py
```

**Output**: Statistics, train/val split info, sample data

### 2. `train_drift_evolution.py`

Main PySR training script.

**Run**:
```bash
cd /home/solo/LadderV3/kh-assist

# Activate venv (has PySR installed)
source experiments/01-pysr-symbolic-regression/.venv/bin/activate

# Run training (2-8 hours)
python3 experiments/01-pysr-symbolic-regression/drift_formula/train_drift_evolution.py
```

**Configuration**:
- Features: `k`, `lane`, `steps_since_activation`, `exponent`
- Operators: `+`, `-`, `*`, `/`, `mod`, `square`, `cube`, `abs`
- Max size: 20
- Max depth: 8
- Iterations: 100 (increase for longer search)
- Train/val split: puzzles 1-55 train, 56-69 validation

**Output**:
- `results/drift_model_unified.pkl` - Trained model
- `results/drift_equations_unified.csv` - Discovered equations

## Strategy

### Approach A: Unified Model (default)

Train on all lanes together (332 samples).

**Pros**: May find universal formula
**Cons**: Harder to discover (more complex)

### Approach B: Per-Lane Models

Train 16 separate models (can parallelize).

**Pros**: Simpler formulas per lane
**Cons**: 16 separate formulas to manage

If Approach A fails to achieve >90% accuracy, try Approach B.

## Critical Data Correction

**LLM Analysis Claim (WRONG)**: ">95% of drift values are multiples of 16"

**Reality**:
- ALL drift (including inactive zeros): 71% multiples of 16
- EVOLUTION drift (what we train on): **6.3%** multiples of 16

**Why the error**: LLM analyzed all 1,104 drift values without filtering out 763 inactive zeros.

**Impact**: DO NOT add quantization operators or filter to multiples of 16!

## Expected Results

**Success criteria** (validation set):
- Level 1: 50-70% exact match → refine formula
- Level 2: 70-90% exact match → very good, minor corrections
- Level 3: 90-99% exact match → excellent, ready for TASK 6
- Level 4: 100% exact match → **FORMULA DISCOVERED!**

**What happens after discovery**:
1. Use formula to GENERATE drift for transitions 70→75
2. Calculate X_71, X_72, X_73, X_74, X_75 using generated drift
3. Validate X_75 against known bridge value
4. If successful → generate ALL puzzles 71-160!

## Files

```
drift_formula/
├── README.md (this file)
├── train_drift_evolution.py (main training script)
├── test_data_loading.py (quick test)
└── results/
    ├── drift_model_unified.pkl (trained model)
    └── drift_equations_unified.csv (equations)
```

## Next Steps

**After training completes**:

1. Review discovered equations:
   ```bash
   cat results/drift_equations_unified.csv
   ```

2. Test best equation on validation set

3. If accuracy ≥ 90%, proceed to **TASK 6** (validation on X_75)

4. If accuracy < 90%, try per-lane models

## Status

- [x] Data extraction implemented
- [x] Data loading tested (332 values, 216 train, 116 val)
- [x] PySR script created
- [x] Configuration tuned for CPU training
- [ ] Full training run (TASK 4)
- [ ] Results analysis
- [ ] Validation on X_75 (TASK 6)

---

**Created**: 2025-12-23
**Task**: TASK 3 (Prepare PySR Training Script)
**Status**: ✅ COMPLETE
**Next**: TASK 4 (Run PySR Training)
