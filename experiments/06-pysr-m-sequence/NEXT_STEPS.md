# Next Steps After PySR Discovery
## Updated: 2025-12-19

## 🔥 Critical Discovery

**Convergent hypothesis is WRONG!** PySR completely ignored all 240 convergent features.

**What works:** Simple pattern using only `2^n`, `n`, and `d_n`

**Formula discovered:** `m ≈ 2^n × 1077.5 / (n × (d_n + 0.4))²` (60-80% accuracy)

## 📋 Immediate Next Steps

### Step 1: Extract m-values from Bridge Puzzles ⭐ **DO THIS FIRST**

We have known correct k-values from Bitcoin CSV for bridges (k75, k80, k85, k90, k95).
Use master formula to reverse-engineer m-values:

```
Master formula: k_n = 2 × k_{n-1} + (2^n - m_n × k_{d_n})

Solve for m_n:
k_n - 2×k_{n-1} = 2^n - m_n × k_{d_n}
m_n × k_{d_n} = 2^n - (k_n - 2×k_{n-1})
m_n = (2^n - (k_n - 2×k_{n-1})) / k_{d_n}
```

**Action:**
```bash
cd /home/solo/LadderV3/kh-assist/experiments/06-pysr-m-sequence
python3 extract_m_from_bridges.py
```

This will:
- Read k75, k80, k85, k90, k95 from CSV
- Calculate actual m75, m80, m85, m90, m95
- Validate PySR formula on these values
- Report accuracy

### Step 2: Validate PySR Formula on Bridges

Compare PySR predictions vs reverse-engineered m-values:

```python
# For each bridge (n = 75, 80, 85, 90, 95)
m_predicted = power_of_2 * 1077.5 / (n * (d_n + 0.4066))**2
m_actual = extracted from step 1
accuracy = m_predicted / m_actual * 100
```

**Expected outcome:**
- If accuracy > 90%: PySR formula is correct, just needs calibration!
- If accuracy 60-80%: Consistent with validation set, formula is approximate
- If accuracy < 50%: Formula breaks down at higher n values

### Step 3: Simplify PySR Features (Quick Iteration)

Run PySR again with minimal features (should complete in < 5 min):

```python
# Features: ONLY basic patterns
features = [
    'n',           # index
    'd_n',         # d-sequence value
    'power_of_2',  # 2^n
    'n_squared',   # n²
    'n_cubed',     # n³
    'd_n_squared', # d_n²
    'prev_m',      # m_{n-1}
    'prev_d',      # d_{n-1}
]
```

**Action:**
```bash
cd /home/solo/LadderV3/kh-assist/experiments/06-pysr-m-sequence
python3 prepare_simple_features.py   # Create minimal feature matrix
python3 train_m_sequence_simple.py   # Train on 8 features (not 245!)
```

### Step 4: Analyze d_n Groups (Piecewise Hypothesis)

Check if pattern differs by d_n value:

```python
# Group training data by d_n
d_n_1 = samples where d_n == 1  # (n = 4, 9, 11, 13, ...)
d_n_2 = samples where d_n == 2  # (n = 2, 5, 6, 7, ...)
d_n_3 = samples where d_n == 3  # (n = 3)
d_n_4 = samples where d_n == 4  # (n = 8, 14, 16, ...)
d_n_7 = samples where d_n == 7  # (n = 10)

# Train separate PySR model for each group
# Check if different formulas emerge
```

**Action:**
```bash
python3 analyze_by_d_groups.py
```

### Step 5: Test Hybrid Approach

Use PySR as base predictor + correction factor:

```python
# Base prediction
m_base = power_of_2 * 1077.5 / (n * (d_n + 0.4066))**2

# Learn correction factors by d_n
correction = {
    1: m_actual[d_n==1] / m_base[d_n==1],  # avg correction for d=1
    2: m_actual[d_n==2] / m_base[d_n==2],  # avg correction for d=2
    # etc.
}

# Final prediction
m_predicted = m_base * correction[d_n]
```

**Action:**
```bash
python3 train_hybrid_corrector.py
```

## 🎯 Success Criteria

| Accuracy | Status | Action |
|----------|--------|--------|
| 100% | 🎉 FORMULA FOUND! | Generate m32-m160, solve puzzle |
| 95-99% | 🔥 Very close | Refine coefficients |
| 80-94% | 👍 Good progress | Use hybrid approach |
| 60-79% | 🤔 Need new ideas | Try modular arithmetic |
| <60% | ❌ Wrong direction | Revisit assumptions |

## 📁 Scripts to Create

### 1. extract_m_from_bridges.py

```python
#!/usr/bin/env python3
"""
Extract actual m-values from bridge puzzles using reverse calculation.
"""
import pandas as pd

# Read CSV
df = pd.read_csv('../../data/btc_puzzle_1_160_full.csv')

# Bridge puzzles (known correct k-values)
bridges = [75, 80, 85, 90, 95]

for n in bridges:
    k_n = int(df[df['bits'] == n]['priv_hex'].values[0], 16)
    k_prev = int(df[df['bits'] == n-1]['priv_hex'].values[0], 16)
    d_n = D_SEQUENCE[n]  # from convergent_database.py
    k_d = int(df[df['bits'] == d_n]['priv_hex'].values[0], 16)

    # Reverse-engineer m_n
    m_n = (2**n - (k_n - 2*k_prev)) // k_d

    print(f"n={n}: m={m_n}, d={d_n}")

    # Validate: does this m give correct k?
    k_check = 2*k_prev + (2**n - m_n * k_d)
    assert k_check == k_n, f"Validation failed for n={n}"
```

### 2. prepare_simple_features.py

```python
#!/usr/bin/env python3
"""
Create feature matrix with ONLY basic features (no convergents).
"""
import pandas as pd
from convergent_database import M_SEQUENCE, D_SEQUENCE

rows = []
for n in range(2, 32):
    row = {
        'n': n,
        'd_n': D_SEQUENCE[n],
        'power_of_2': 2**n,
        'n_squared': n**2,
        'n_cubed': n**3,
        'd_n_squared': D_SEQUENCE[n]**2,
        'prev_m': M_SEQUENCE.get(n-1, 0),
        'prev_d': D_SEQUENCE.get(n-1, 0),
        'target_m': M_SEQUENCE[n]
    }
    rows.append(row)

df = pd.DataFrame(rows)
df.to_csv('feature_matrix_simple.csv', index=False)
print(f"Created simple feature matrix: {len(df)} samples, {len(df.columns)-1} features")
```

### 3. analyze_by_d_groups.py

```python
#!/usr/bin/env python3
"""
Analyze m-sequence patterns grouped by d_n value.
"""
import pandas as pd
from convergent_database import M_SEQUENCE, D_SEQUENCE

# Group by d_n
groups = {}
for n in range(2, 32):
    d = D_SEQUENCE[n]
    if d not in groups:
        groups[d] = []
    groups[d].append((n, M_SEQUENCE[n]))

# Analyze each group
for d, samples in sorted(groups.items()):
    print(f"\nd_n = {d}:")
    print(f"  Count: {len(samples)}")
    print(f"  Samples: {samples[:5]}...")  # first 5

    # Check if simple pattern exists
    for n, m in samples[:3]:
        ratio = m * d**2 * n**2 / (2**n)
        print(f"  n={n}: m={m}, ratio={ratio:.2f}")
```

## 🚀 Priority Order

1. **HIGHEST:** Extract m from bridges (Step 1) - validates if we're on right track
2. **HIGH:** Simplify PySR features (Step 3) - fast iteration, tests if simplicity helps
3. **MEDIUM:** Analyze d_n groups (Step 4) - checks piecewise hypothesis
4. **MEDIUM:** Hybrid approach (Step 5) - practical solution if exact formula doesn't exist
5. **LOW:** Report to other Claudes - after we have bridge validation results

## 📊 Decision Tree

```
Run Step 1 (extract m from bridges)
  |
  ├─> If PySR accuracy on bridges > 90%
  |     └─> Calibrate coefficients, generate m32-m160 ✅
  |
  ├─> If PySR accuracy on bridges 60-80%
  |     ├─> Run Step 3 (simple features)
  |     ├─> Run Step 4 (d_n groups)
  |     └─> Run Step 5 (hybrid)
  |
  └─> If PySR accuracy on bridges < 60%
        └─> Formula breaks down, try modular arithmetic hypothesis
```

## 🔄 Communication with Other Claudes

**After Step 1 completes, create GitHub update:**

```bash
cd /home/solo/LadderV3/kh-assist
git add experiments/06-pysr-m-sequence/
git commit -m "CRITICAL: Convergent hypothesis DISPROVEN by PySR

PySR training complete (3 min, 0% exact accuracy).

KEY FINDINGS:
- Convergent features (π, e, sqrt2, etc.) completely ignored by PySR
- Best formula uses ONLY: 2^n, n, d_n (3 features vs 245!)
- Approximate formula: m ≈ 2^n × 1077.5 / (n × (d_n + 0.4))²
- Validation accuracy: 60-80% (consistent underprediction)

NEXT STEPS:
- Extract m-values from bridge puzzles (reverse calculation)
- Validate PySR formula on bridges
- Simplify feature set and re-run

FILES:
- DIAGNOSTIC_REPORT.md - full analysis
- NEXT_STEPS.md - action plan
- training_results.json - validation results
- m_sequence_model.pkl - PySR model

See DIAGNOSTIC_REPORT.md for implications."

git push origin local-work
```

## 📝 Notes

- Bridge extraction is crucial - it gives us ground truth for n=75-95
- If PySR formula works on bridges, we can calibrate it
- If PySR formula fails on bridges, we need different approach
- Simple features should be tested before giving up on PySR
- Modular arithmetic is last resort if continuous regression fails
