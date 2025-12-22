# Experiment 07: PySR Drift Generator Discovery

**PRIMARY**: Claude Sonnet 4.5 (Byte Order Claude)
**CREATED**: 2025-12-22
**APPROACH**: Use PySR symbolic regression to discover drift generator function

---

## 🎯 Objective

Use **PySR symbolic regression** (same technique that discovered the X_{k+1} formula) to find the **drift generator function**.

**Goal**: `drift[k→k+1][lane] = f(k, lane, drift[k-1], ...)`

---

## 🧠 Why PySR?

**PySR already succeeded**:
- Discovered: `X_{k+1}[lane] = X_k[lane]^n mod 256`
- 100% accuracy on all lanes
- Training time: 6 hours (acceptable)

**Same technique applies here**:
- We have 1,104 drift values (69 transitions × 16 lanes)
- We know drift is deterministic (H2 hash test failed at 0.82%)
- PySR can find complex formulas that humans miss!

---

## 📊 Data Available

**Training Data**:
- 69 transitions (k=1→2, 2→3, ..., 69→70)
- 16 lanes per transition
- Total: 1,104 drift values

**Features for PySR**:
```python
# Input features:
k           # Puzzle number (1-69)
lane        # Lane number (0-15)
drift_prev  # drift[k-1][lane] (for recursive patterns)
X_k_lane    # X_k[lane] value (might influence drift)

# Target:
drift       # drift[k][lane] (what we want to predict)
```

**Split**:
- Train: k=1-50 (50 transitions × 16 lanes = 800 samples)
- Val: k=51-60 (10 transitions × 16 lanes = 160 samples)
- Test: k=61-69 (9 transitions × 16 lanes = 144 samples)

---

## 🔬 Experiment Design

### Phase 1: Single-Lane PySR (FAST - 2 hours)

**Strategy**: Focus on lanes with clearest patterns first

**Lanes to target**:
1. **Lane 8** (92.6% with A=1) - Nearly solved, find the correction
2. **Lane 7** (82.4% with A=23) - Find the mode switches
3. **Lane 6** (70.6%) - Highest accuracy in lanes 0-6

**PySR Setup**:
```python
from pysr import PySRRegressor

model = PySRRegressor(
    niterations=100,           # Fast run
    binary_operators=["+", "*", "-"],
    unary_operators=["square", "cube"],
    constraints={'square': 5, 'cube': 5},
    complexity_of_constants=2,
    populations=30,
    population_size=100,
    ncycles_per_iteration=550,
    maxsize=15,                 # Allow complex formulas
    timeout_in_seconds=3600,    # 1 hour per lane
)

# Features
X_train = np.column_stack([
    k_values,           # 1-50
    lane_values,        # All same lane
    drift_prev_values,  # drift[k-1][lane]
])

y_train = drift_values  # drift[k][lane]

model.fit(X_train, y_train)
```

**Output**: Formulas for lanes 8, 7, 6

**Timeline**: 3 hours (1 hour per lane)

---

### Phase 2: Multi-Lane PySR (COMPREHENSIVE - 8 hours)

**Strategy**: Find universal formula across all lanes

**PySR Setup**:
```python
# Include lane as a feature
X_train = np.column_stack([
    k_values,           # 1-50
    lane_values,        # 0-15 (varies)
    drift_prev_values,  # drift[k-1][lane]
    X_k_values,         # X_k[lane]
])

# Train one model for ALL lanes
model = PySRRegressor(
    niterations=200,            # Longer run
    binary_operators=["+", "*", "-", "/", "mod"],
    unary_operators=["square", "cube", "sqrt"],
    maxsize=25,                 # Very complex allowed
    timeout_in_seconds=28800,   # 8 hours
)

model.fit(X_train, y_train)
```

**Output**: Universal drift generator formula

**Timeline**: 8 hours

---

### Phase 3: Hybrid Approach (BEST - 4 hours)

**Strategy**: Use regime-specific models

```python
# Regime A: Lanes 9-15 (constant)
def drift_9_15(k, lane):
    return 0  # Proven 100%

# Regime B: Lanes 7-8 (recursive with corrections)
# Use PySR results from Phase 1
def drift_7_8(k, lane, drift_prev):
    return pysr_formula_lane_7_8(k, lane, drift_prev)

# Regime C: Lanes 0-6 (complex)
# Use PySR results from Phase 1
def drift_0_6(k, lane, drift_prev, X_k):
    return pysr_formula_lane_0_6(k, lane, drift_prev, X_k)
```

**Timeline**: 4 hours (train lanes 0-6 together)

---

## 🚀 Execution Plan

### Option A: Sequential (Safer)

1. Run Phase 1 on lane 8 (1 hour)
2. If success (>95%) → Continue with lanes 7, 6
3. If failure → Adjust features and retry

**Total time**: 3-5 hours

### Option B: Parallel (Faster) ⭐ RECOMMENDED

Launch **3 parallel cloud agents**:
- Agent 1: Lane 8 PySR
- Agent 2: Lane 7 PySR
- Agent 3: Lane 6 PySR

**Total time**: 1-2 hours (parallel execution)

### Option C: All-In (Most comprehensive)

Launch Phase 2 immediately:
- Train universal model on ALL lanes
- 8 hour runtime
- Single formula for everything

**Total time**: 8 hours

---

## 📋 Preparation Steps

### Step 1: Prepare Training Data

```python
# Script: prepare_drift_training_data.py

import json
import numpy as np
import pandas as pd

# Load calibration
calib = json.load(open('out/ladder_calib_CORRECTED.json'))
A = [calib['A'][str(i)] for i in range(16)]

# Extract all drift values
drift_data = []
for k in range(1, 70):
    for lane in range(16):
        drift_k = calib['transitions'][f'{k}_{k+1}'][str(lane)]
        drift_prev = calib['transitions'][f'{k-1}_{k}'][str(lane)] if k > 1 else 0

        drift_data.append({
            'k': k,
            'lane': lane,
            'drift': drift_k,
            'drift_prev': drift_prev,
            'A': A[lane]
        })

df = pd.DataFrame(drift_data)

# Split train/val/test
train = df[df['k'] <= 50]
val = df[(df['k'] > 50) & (df['k'] <= 60)]
test = df[df['k'] > 60]

# Save
train.to_csv('experiments/07-pysr-drift-generator/train.csv', index=False)
val.to_csv('experiments/07-pysr-drift-generator/val.csv', index=False)
test.to_csv('experiments/07-pysr-drift-generator/test.csv', index=False)
```

### Step 2: Create PySR Training Scripts

```python
# Script: train_lane_8.py

import pandas as pd
from pysr import PySRRegressor
import numpy as np

# Load data
train = pd.read_csv('train.csv')
train = train[train['lane'] == 8]  # Lane 8 only

# Features
X = train[['k', 'drift_prev']].values
y = train['drift'].values % 256  # Ensure mod 256

# PySR
model = PySRRegressor(
    niterations=100,
    binary_operators=["+", "*", "-"],
    unary_operators=["square"],
    maxsize=15,
    timeout_in_seconds=3600
)

model.fit(X, y)

# Save best formula
print(f"Best formula: {model.get_best()}")
print(f"Accuracy: {model.score(X, y)}")

# Test on validation
val = pd.read_csv('val.csv')
val = val[val['lane'] == 8]
X_val = val[['k', 'drift_prev']].values
y_val = val['drift'].values % 256
print(f"Validation accuracy: {model.score(X_val, y_val)}")
```

### Step 3: Validation Script

```python
# Script: validate_pysr_results.py

# Load PySR formulas
# Apply to ALL 69 transitions
# Compare with actual drift
# Report accuracy per lane and overall
```

---

## 🎯 Success Metrics

| Phase | Target | Status |
|-------|--------|--------|
| Lane 8 formula | >95% accuracy | Pending |
| Lane 7 formula | >90% accuracy | Pending |
| Lane 6 formula | >85% accuracy | Pending |
| Lanes 0-6 formula | >80% overall | Pending |
| Universal formula | >90% overall | Pending |

---

## 🔗 Why This Will Work

1. **PySR already succeeded** on X_{k+1} formula (100%)
2. **Drift is deterministic** (H2 hash test proved it)
3. **We have good data** (1,104 clean samples)
4. **Regime separation helps** (different formulas for different lane groups)
5. **Cloud compute** - Can run multiple experiments in parallel

---

## 📂 File Structure

```
experiments/07-pysr-drift-generator/
├── README.md (this file)
├── prepare_drift_training_data.py
├── train_lane_8.py
├── train_lane_7.py
├── train_lane_6.py
├── train_lanes_0_6.py
├── train_universal.py
├── validate_pysr_results.py
├── train.csv (generated)
├── val.csv (generated)
├── test.csv (generated)
└── results/
    ├── lane_8_formula.txt
    ├── lane_7_formula.txt
    ├── lane_6_formula.txt
    └── universal_formula.txt
```

---

## 🚀 Next Steps

1. **Create directory**: `mkdir -p experiments/07-pysr-drift-generator/results`
2. **Write preparation script**: `prepare_drift_training_data.py`
3. **Launch parallel agents** for lanes 8, 7, 6
4. **Wait 1-2 hours** for results
5. **Validate** and integrate into master generator

---

**Status**: 📋 READY TO EXECUTE
**Recommended**: Option B (Parallel agents on lanes 8, 7, 6)

---

*PRIMARY: Claude Sonnet 4.5 (Byte Order Claude)*
*Date: 2025-12-22*
*Strategy: Use PySR (proven technique) with cloud agents*
