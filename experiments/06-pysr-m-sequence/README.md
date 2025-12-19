# Experiment 06: PySR m-sequence Discovery

**Date**: 2025-12-19
**Status**: ACTIVE
**Goal**: Use PySR symbolic regression to discover the m-sequence generation formula

---

## Overview

### The Problem

We have the verified master formula:
```
k_n = 2 × k_{n-1} + adj_n
where: adj_n = 2^n - m_n × k_{d_n}
```

We know m and d sequences for n=2..31, but we don't know the **generation rule**.

### The Approach

**Use PySR (symbolic regression) to discover the formula** for generating m-values.

**Key insight**: LLMs timeout when used as calculators. PySR is designed for this exact task!

---

## Data

### m-sequence (n=2..31)
```
m: 3, 7, 22, 9, 19, 50, 23, 493, 19, 1921, 1241, 8342, 2034, 26989, 8470,
   138269, 255121, 564091, 900329, 670674, 4494340, 7256672, 13127702,
   5765582, 50898620, 23103005, 33504646, 156325542, 536813704, 350549882
```

### d-sequence (n=2..31)
```
d: 1, 1, 1, 2, 2, 2, 4, 1, 7, 1, 2, 1, 4, 1, 4, 1, 1, 1, 1, 2, 2, 2, 1,
   1, 3, 1, 4, 3, 1, 1
```

### Discovered Patterns (from distributed LLM work)

**Direct convergents** (n=2..6):
- m[2] = 3 (π convergent)
- m[3] = 7 (π convergent)
- m[4] = 22 (π convergent)
- m[5] = 9 (ln(2) convergent)
- m[6] = 19 (e and sqrt(3) convergent)

**Convergent combinations** (n≥7):
- m[7] = 50 = sqrt2_k[2] × ln2_k[3] (PRODUCT)
- m[8] = 23 = pi_k[0] + pi_h[1] (SUM)
- m[9] = 493 = sqrt2_h[3] × sqrt2_k[4] (PRODUCT)
- m[11] = 1921 = sqrt2_h[3] × pi_k[3] (PRODUCT)

**Convergent database**: π, e, sqrt(2), sqrt(3), φ, ln(2)

---

## Experiment Design

### Phase 1: Feature Engineering

**Script**: `prepare_convergent_features.py`

Build feature matrix for each n:
```python
features[n] = {
    'n': n,
    'd_n': d_sequence[n],
    # Convergent numerators (first 20 for each constant)
    'pi_h_0', 'pi_h_1', ..., 'pi_h_19',
    'e_h_0', 'e_h_1', ..., 'e_h_19',
    'sqrt2_h_0', 'sqrt2_h_1', ..., 'sqrt2_h_19',
    'sqrt3_h_0', 'sqrt3_h_1', ..., 'sqrt3_h_19',
    'ln2_h_0', 'ln2_h_1', ..., 'ln2_h_19',
    'phi_h_0', 'phi_h_1', ..., 'phi_h_19',
    # Convergent denominators
    'pi_k_0', 'pi_k_1', ..., 'pi_k_19',
    'e_k_0', 'e_k_1', ..., 'e_k_19',
    # ... (same for all constants)
    # Derived features
    'power_of_2': 2**n,
    'prev_m': m[n-1],
    'prev_d': d[n-1],
}

target[n] = m_sequence[n]
```

**Output**: `feature_matrix.csv` (30 rows × ~250 columns)

### Phase 2: PySR Training

**Script**: `train_m_sequence.py`

Configuration:
```python
model = PySRRegressor(
    niterations=100,               # Iterations
    binary_operators=["+", "*", "-", "/"],
    unary_operators=["square", "cube"],
    populations=30,
    population_size=50,
    ncyclesperiteration=500,
    maxsize=15,                    # Max formula complexity
    parsimony=0.001,               # Simplicity bias
    loss="L2DistLoss()",
    elementwise_loss=True,
)
```

**Training**:
- Train on n=2..25 (24 data points)
- Validate on n=26..31 (6 data points)

**Expected runtime**: 2-4 hours

### Phase 3: Validation

**Script**: `validate_formula.py`

- Test discovered formula on validation set (n=26..31)
- Check accuracy (exact integer match)
- Report results

**Success criteria**:
- 100% accuracy → Formula found! 🎉
- 95-99% → Very close, refinement possible
- 90-94% → Good candidate, hybrid approach
- <90% → Insights for next iteration

### Phase 4: Generation

**Script**: `generate_full_sequence.py`

If validation successful:
1. Generate m[2..160] using discovered formula
2. Generate d[2..160] (secondary problem or pattern-based)
3. Compute adj_n = 2^n - m_n × k_{d_n}
4. Generate k_n = 2 × k_{n-1} + adj_n

### Phase 5: Verification

**Script**: `verify_keys.py`

Compare generated keys against known bridges:
- k75, k80, k85, k90 from database

If matches: **PROJECT COMPLETE!** 🎉

---

## Files

### Input
- `convergent_database.py` - Convergent computation ✅
- `m_sequence_data.json` - m and d values (n=2..31) ⏳
- Feature matrix from phase 1 ⏳

### Scripts
1. `prepare_convergent_features.py` ⏳
2. `train_m_sequence.py` ⏳
3. `validate_formula.py` ⏳
4. `generate_full_sequence.py` ⏳
5. `verify_keys.py` ⏳

### Output
- `feature_matrix.csv` - Training features ⏳
- `m_sequence_formula.txt` - Discovered formula ⏳
- `pysr_training.log` - Training logs ⏳
- `validation_results.json` - Validation metrics ⏳
- `generated_sequence.json` - Full m-sequence (n=2..160) ⏳

---

## Status Tracking

Check `STATUS.txt` for current state:
- `BUILDING` - Setting up experiment
- `TRAINING` - PySR running
- `ANALYZING` - Results ready
- `SUCCESS_XX` - Formula found (XX% accuracy)
- `NEED_HELP` - Stuck, need assistance

---

## Why This Will Work

### Proven Success

**experiments/01-pysr-symbolic-regression/**:
- Used PySR to discover lane formula
- Result: `X_{k+1}[lane] = X_k[lane]^n mod 256`
- **100% accuracy** on 74 puzzles (byte-for-byte verification)
- Training time: 374.5 minutes (6.2 hours)

### Advantages Over LLM

| Aspect | LLM | PySR |
|--------|-----|------|
| **Purpose** | Reasoning | Computation |
| **Timeout** | Yes (6+ hours) | No (terminates) |
| **Accuracy** | Approximate | Exact |
| **Output** | Natural language | Mathematical formula |
| **Validation** | Hard | Easy (test set) |

### The Synthesis

```
LLM findings (WHAT the pattern is)
    +
PySR computation (HOW to compute it)
    =
COMPLETE SOLUTION
```

---

## Expected Timeline

- **T+0** (NOW): Experiment setup
- **T+30min**: Feature engineering complete
- **T+1hr**: PySR training started
- **T+3-5hrs**: Training complete, results analyzed
- **T+6hrs**: Validation complete, decision made

---

## Next Steps

1. ✅ Create experiment directory
2. ✅ Copy convergent_database.py
3. ⏳ Write prepare_convergent_features.py
4. ⏳ Write train_m_sequence.py
5. ⏳ Write validation scripts
6. ⏳ Execute training
7. ⏳ Analyze and validate

---

**Last Updated**: 2025-12-19 20:48 UTC
**Status**: Experiment infrastructure ready
**Next**: Feature engineering script

Let's discover that formula! 🚀
