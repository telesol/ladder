# Experiment 01: PySR Symbolic Regression - TODO Plan

## Objective
Use symbolic regression to automatically discover the mathematical formula for the Bitcoin puzzle ladder recurrence relation.

## Target Formula
```
X_{k+1}(ℓ) = A_ℓ^4 * X_k(ℓ) + Γ_ℓ * C_0(ℓ) (mod 256)
```

**Goal:** Discover coefficients `A_ℓ` and `C_0(ℓ)` for each of 16 lanes.

---

## Phase 1: Environment Setup ✅

### 1.1 Install Dependencies
```bash
# Core ML libraries
pip install numpy pandas matplotlib scikit-learn

# PySR (symbolic regression)
pip install pysr

# Julia backend (required by PySR)
# PySR will auto-install Julia on first run, or:
# python -c "import pysr; pysr.install()"

# GPU support (optional, for faster symbolic search)
# pip install julia  # if manual Julia setup needed
```

**Status:** ⏳ Pending
**Expected time:** 10-15 minutes
**Verification:**
```bash
python3 -c "import pysr; print(f'PySR version: {pysr.__version__}')"
```

---

## Phase 2: Data Preparation ✅

### 2.1 Validate Training Data
**Files available:**
- ✅ `data/puzzles_full.json` (82 puzzles)
- ✅ `data/lane_matrix.npy` (82×32 array)
- ✅ `data/half_blocks.json`
- ✅ `data/pattern_analysis.json`

### 2.2 Create Training/Validation Split
**Script:** `scripts/prepare_data.py`

Split strategy:
- **Training:** Puzzles 1-60 (60 samples)
- **Validation:** Puzzles 61-70 (10 samples)
- **Test:** Bridge rows 75, 80, 85, 90, 95 (5 samples)

**Output:**
- `data/train_matrix.npy` (60×32)
- `data/val_matrix.npy` (10×32)
- `data/test_matrix.npy` (5×32)

**Status:** ⏳ Pending
**Expected time:** 5 minutes

---

## Phase 3: Symbolic Regression Training

### 3.1 Single Lane Discovery (Proof of Concept)
**Script:** `scripts/train_single_lane.py`

**Goal:** Discover formula for Lane 0 only

**Configuration:**
```python
model = PySRRegressor(
    niterations=1000,
    populations=15,
    population_size=33,
    binary_operators=["+", "*", "-"],
    unary_operators=["square", "cube"],
    constraints={
        'pow': (1, 5),  # Allow x^1 through x^5
    },
    maxsize=15,
    parsimony=0.001,
    model_selection="best",
    loss="loss(x, y) = abs(mod(x - y, 256))",  # Modular loss
)
```

**Training command:**
```bash
python3 scripts/train_single_lane.py --lane 0 --iterations 1000
```

**Expected output:**
```
Lane 0 discovered formula:
  f(x) = 245*x^4 + 12  (mod 256)

Accuracy: 98.3%
R² score: 0.95
```

**Status:** ⏳ Pending
**Expected time:** 30-60 minutes (CPU-bound)

### 3.2 Multi-Lane Discovery (All 16 Lanes)
**Script:** `scripts/train_all_lanes.py`

**Parallel training:**
- Train 16 models in parallel (one per lane)
- Use multiprocessing or sequential execution
- Save each model separately

**Training command:**
```bash
python3 scripts/train_all_lanes.py --iterations 1000 --parallel
```

**Output:**
- `results/lane_00_formula.txt`
- `results/lane_01_formula.txt`
- ...
- `results/lane_15_formula.txt`
- `results/discovered_coefficients.json`

**Status:** ⏳ Pending
**Expected time:** 8-12 hours (16 lanes × 30-45 min each)

**Checkpoint strategy:**
- Save progress after each lane
- Resume from last completed lane if interrupted

---

## Phase 4: Formula Extraction

### 4.1 Extract Coefficients
**Script:** `scripts/extract_coefficients.py`

Parse discovered formulas to extract:
- `A_ℓ` values (multiplication factors)
- `C_0(ℓ)` values (drift constants)

**Expected format:**
```json
{
  "A": [245, 123, 67, ...],  // 16 values
  "C0": [12, 5, 0, ...],      // 16 values
  "formulas": {
    "0": "245*x^4 + 12",
    "1": "123*x^4 + 5",
    ...
  }
}
```

**Status:** ⏳ Pending
**Expected time:** 5 minutes

### 4.2 Verify Modular Arithmetic
Ensure all coefficients work correctly mod 256:
```python
for lane in range(16):
    a = A[lane]
    c = C0[lane]

    # Test on training data
    for i in range(len(X_train) - 1):
        calculated = (pow(a, 4) * X_train[i, lane] + c) % 256
        actual = X_train[i+1, lane]
        assert calculated == actual, f"Lane {lane} failed at index {i}"
```

**Status:** ⏳ Pending
**Expected time:** 2 minutes

---

## Phase 5: Validation & Testing

### 5.1 Forward Verification
**Script:** `scripts/verify_forward.py`

Test: Given puzzle k, calculate puzzle k+1

**Validation set (puzzles 61-70):**
- Accuracy target: **100%** (exact byte matches)
- Compute per-lane accuracy
- Compute overall accuracy

**Status:** ⏳ Pending
**Expected time:** 5 minutes

### 5.2 Reverse Verification
**Script:** `scripts/verify_reverse.py`

Test: Given puzzle k+1, reconstruct puzzle k

**Requires:** Modular inverse of A^4 (mod 256)

**Status:** ⏳ Pending
**Expected time:** 10 minutes

### 5.3 Bridge Row Testing
**Script:** `scripts/test_bridges.py`

Test on bridge rows (75, 80, 85, 90, 95):
- These are further apart (5-step intervals)
- Requires applying formula 5 times sequentially

**Status:** ⏳ Pending
**Expected time:** 5 minutes

---

## Phase 6: Export & Integration

### 6.1 Export Calibration JSON
**Script:** `scripts/export_calibration.py`

Create JSON compatible with existing tools:
```json
{
  "A": {
    "0": 245,
    "1": 123,
    ...
    "15": 89
  },
  "Cstar": {
    "0": {
      "0": [12, 5, 0, ..., 2]  // 16-element C0 vector
    }
  },
  "discovered_by": "PySR symbolic regression",
  "accuracy_forward": 100.0,
  "accuracy_reverse": 100.0
}
```

**Output:** `results/ladder_calib_pysr.json`

**Status:** ⏳ Pending
**Expected time:** 5 minutes

### 6.2 Integrate with Existing Tools
Test compatibility:
```bash
python3 ../../verify_affine.py \
  --db ../../db/kh.db \
  --calib results/ladder_calib_pysr.json \
  --start 1 --end 70
```

**Expected:** 100% forward and reverse verification

**Status:** ⏳ Pending
**Expected time:** 5 minutes

---

## Phase 7: Documentation & Visualization

### 7.1 Generate Report
**Script:** `scripts/generate_report.py`

Create comprehensive report:
- Discovered formulas for all 16 lanes
- Accuracy metrics
- Visualization of calculations vs actual
- Coefficient heatmap

**Output:** `results/PYSR_REPORT.md` + `results/figures/`

**Status:** ⏳ Pending
**Expected time:** 10 minutes

### 7.2 Create Visualizations
- Lane-by-lane coefficient plot
- Accuracy heatmap
- Calculation error distribution
- Formula complexity chart

**Status:** ⏳ Pending
**Expected time:** 15 minutes

---

## Timeline Summary

| Phase | Task | Time | Status |
|-------|------|------|--------|
| 1 | Environment setup | 15 min | ⏳ |
| 2 | Data preparation | 5 min | ⏳ |
| 3.1 | Single lane PoC | 1 hour | ⏳ |
| 3.2 | All 16 lanes | 8-12 hours | ⏳ |
| 4 | Extract coefficients | 5 min | ⏳ |
| 5 | Validation | 20 min | ⏳ |
| 6 | Export & integrate | 10 min | ⏳ |
| 7 | Documentation | 25 min | ⏳ |
| **Total** | | **~10-14 hours** | |

**Most time-consuming:** Phase 3.2 (multi-lane discovery)
**Can run overnight:** Yes, with checkpointing

---

## Success Criteria

✅ **Phase 3 Success:**
- Discover formulas for all 16 lanes
- Each formula has form `a*x^k + c` where k=4 ideally

✅ **Phase 5 Success:**
- Forward accuracy: 100% on validation set
- Reverse accuracy: 100% on validation set
- Bridge row calculations: 100% accurate

✅ **Phase 6 Success:**
- Exported calibration JSON works with existing tools
- Integration test passes

---

## Execution Commands

### Quick Start (Sequential)
```bash
cd experiments/01-pysr-symbolic-regression

# Phase 1
pip install pysr numpy pandas scikit-learn matplotlib

# Phase 2
python3 scripts/prepare_data.py

# Phase 3.1 (PoC)
python3 scripts/train_single_lane.py --lane 0

# Phase 3.2 (All lanes - will take 8-12 hours)
python3 scripts/train_all_lanes.py

# Phase 4-7 (Automated)
python3 scripts/run_validation_pipeline.py
```

### Quick Start (One Command)
```bash
cd experiments/01-pysr-symbolic-regression
./run_experiment.sh  # Master script (to be created)
```

---

## Fallback Plan

If PySR doesn't converge or formulas are too complex:

**Option A:** Constrain search space more aggressively
- Force formula form: `a*x^4 + c`
- Provide hint about modular arithmetic

**Option B:** Use grid search
- Brute force test all `a ∈ [0, 255]` and `c ∈ [0, 255]`
- ~65k combinations per lane, very fast

**Option C:** Switch to transformer model (Experiment 02)

---

## Next Steps

1. ✅ Create experiment folder structure
2. ✅ Copy clean data
3. ⏳ Create all scripts (Phase 1-7)
4. ⏳ Install PySR dependencies
5. ⏳ Run Phase 3.1 (single lane PoC)
6. ⏳ If successful → Run Phase 3.2 (all lanes)
7. ⏳ Validate and export results

**Ready to proceed?** 🚀
