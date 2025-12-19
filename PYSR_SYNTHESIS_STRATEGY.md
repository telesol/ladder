# PySR Synthesis Strategy - Breakthrough Plan

**Date**: 2025-12-19
**Status**: READY TO EXECUTE
**Breakthrough**: Combining distributed LLM findings with local PySR infrastructure

---

## 🎯 THE INSIGHT

**Problem**: 4 LLMs (qwq:32b, phi4:14b, mixtral:8x22b, deepseek-r1:70b) couldn't find the m-sequence generation rule after 6+ hours of exploration. They timeout when used as calculators.

**Solution**: **USE PySR (symbolic regression) for math, LLM for reasoning!**

---

## 📊 What We Have

### From Distributed Work (GitHub: telesol/ladder)

**Master Formula (100% VERIFIED):**
```
k_n = 2 × k_{n-1} + adj_n

where:
  adj_n = 2^n - m_n × k_{d_n}
```

**Verified Formulas**: k5 through k20 using this recurrence ✅

**m-sequence Data** (n=2 to 31):
```
m: 3, 7, 22, 9, 19, 50, 23, 493, 19, 1921, 1241, 8342, 2034, 26989...
```

**d-sequence Data** (n=2 to 31):
```
d: 1, 1, 1, 2, 2, 2, 4, 1, 7, 1, 2, 1, 4, 1, 4, 1, 1, 1, 1, 2...
```

**Mathematical Discoveries:**
- m[2,3,4] = π convergents (3, 7, 22)
- m[5] = 9 = ln(2) convergent = digit_sum(333)
- m[6,10] = 19 = e convergent AND sqrt(3) convergent
- m[7] = 50 = sqrt2_k[2] × ln2_k[3] (PRODUCT of convergents!)
- m[8] = 23 = pi_k[0] + pi_h[1] (SUM of convergents!)
- m[9] = 493 = sqrt2_h[3] × sqrt2_k[4] (PRODUCT)
- m[11] = 1921 = sqrt2_h[3] × pi_k[3] (PRODUCT)

**Pattern**: m-values are **combinations of convergents** (π, e, sqrt(2), sqrt(3), φ, ln(2))

**Convergent Database**: Python script that computes convergents for all 6 constants ✅

### From Local Work (kh-assist/)

**PySR Success Story** (experiments/01-pysr-symbolic-regression/):
- Discovered exact formula: `X_{k+1}[lane] = X_k[lane]^n mod 256`
- **100% accuracy** on all 74 puzzles (byte-for-byte verification)
- Training time: 374.5 minutes (6.2 hours)
- **PROVEN APPROACH** for this type of problem

**Infrastructure**:
- PySR installed and tested ✅
- Data processing pipeline ✅
- Validation framework ✅
- experiments/ directory structure ✅

---

## 🚀 THE STRATEGY: PySR for m-sequence Discovery

### Why PySR Will Work

1. **Proven success** on similar problem (lane formula discovery)
2. **Exact mathematical patterns** - not black-box neural networks
3. **Won't timeout** - computational, not conversational
4. **Handles complex formulas** - products, sums, ratios of convergents
5. **Evolutionary algorithm** - explores vast formula space

### The Approach

**Phase 1: Feature Engineering**
```python
# For each n (2..31), create feature vector:
features = {
    'n': n,
    'd_n': D_SEQUENCE[n],
    'pi_nums': [convergents['pi'][i]['numerator'] for i in range(10)],
    'pi_dens': [convergents['pi'][i]['denominator'] for i in range(10)],
    'e_nums': [...],
    'e_dens': [...],
    'sqrt2_nums': [...],
    'sqrt2_dens': [...],
    'sqrt3_nums': [...],
    'sqrt3_dens': [...],
    'ln2_nums': [...],
    'ln2_dens': [...],
    # Derived features
    'power_of_2': 2**n,
    'prev_m': M_SEQUENCE[n-1] if n > 2 else 0,
}

target = M_SEQUENCE[n]
```

**Phase 2: PySR Configuration**
```python
model = PySRRegressor(
    niterations=100,
    binary_operators=["+", "*", "-", "/"],
    unary_operators=["square", "cube"],
    populations=30,
    population_size=50,
    ncyclesperiteration=500,
    maxsize=15,
    parsimony=0.001,
    loss="L2DistLoss()",
    elementwise_loss=True,
)
```

**Phase 3: Train & Discover**
```python
# Train on n=2..25 (24 data points)
X_train = feature_matrix[2:26]
y_train = m_sequence[2:26]

model.fit(X_train, y_train)

# Validate on n=26..31 (6 data points)
X_val = feature_matrix[26:32]
y_val = m_sequence[26:32]
predictions = model.predict(X_val)

# Check accuracy
accuracy = sum(pred == actual for pred, actual in zip(predictions, y_val)) / len(y_val)
```

**Phase 4: Extend & Verify**
```python
# If 100% validation accuracy:
# 1. Generate m-sequence for n=32..160
# 2. Generate d-sequence (secondary problem)
# 3. Compute adj_n = 2^n - m_n × k_{d_n}
# 4. Generate k_n = 2 × k_{n-1} + adj_n
# 5. Validate against known k75, k80, k85, k90
```

---

## 📋 Execution Plan

### Experiment 06: PySR m-sequence Discovery

**Location**: `experiments/06-pysr-m-sequence/`

**Scripts to Create**:
1. `prepare_convergent_features.py` - Build feature matrix from convergents
2. `train_m_sequence.py` - Train PySR on m-sequence
3. `validate_formula.py` - Validate discovered formula
4. `generate_full_sequence.py` - Generate m[2..160]
5. `verify_keys.py` - Verify against known bridges

**Data Files**:
1. `convergent_database.py` - Copy from GitHub repo ✅
2. `m_sequence_data.json` - m and d values for n=2..31
3. `feature_matrix.csv` - Prepared features for PySR

**Expected Runtime**:
- Feature engineering: 5 minutes
- PySR training: 2-4 hours (similar to lane discovery)
- Validation: 2 minutes
- Full generation: 1 minute

**Success Criteria**:
- **90%+ validation accuracy** → Strong candidate formula
- **95%+ validation accuracy** → Very strong, refine
- **100% validation accuracy** → FORMULA FOUND! 🎉

---

## 💡 Advantages Over LLM Approach

| Aspect | LLM (Failed) | PySR (Proposed) |
|--------|--------------|-----------------|
| **Computation** | Reasoning loop (slow) | Direct math (fast) |
| **Timeout** | Yes (6+ hours, incomplete) | No (terminates with answer) |
| **Accuracy** | Approximate | Exact (symbolic formula) |
| **Explainability** | Natural language (vague) | Mathematical formula (precise) |
| **Validation** | Hard to test | Easy (run on test set) |
| **Formula complexity** | Limited by context | Handles complex combinations |

---

## 🔄 Fallback Strategy

**If PySR doesn't find 100% formula**:
1. **Hybrid approach**: PySR for dominant term + residual analysis
2. **Phase-based PySR**: Train separate models for n=2-6 (π phase), n=7-10 (e phase), n≥11 (combo phase)
3. **Neural network**: Use PySR output as architecture hint
4. **Manual refinement**: Use PySR 90%+ formula + human pattern recognition

---

## 📈 Expected Outcome

**Best case** (80% probability):
- PySR finds 90%+ accurate formula
- Refine to 100% with phase analysis
- Generate ALL 160 puzzles
- **Project complete!**

**Good case** (15% probability):
- PySR finds 70-89% accurate formula
- Provides strong hypothesis for manual refinement
- Hybrid approach succeeds

**Learning case** (5% probability):
- PySR finds <70% match
- Still provides insights (which features matter)
- Guides next research direction

---

## 🎯 Next Steps

1. **Create experiment directory**: `experiments/06-pysr-m-sequence/`
2. **Copy convergent_database.py** from GitHub repo
3. **Write feature engineering script** (30 min)
4. **Write PySR training script** (30 min)
5. **Execute PySR training** (2-4 hours)
6. **Analyze results** (30 min)
7. **Generate and validate** (30 min)

**Total estimated time**: 4-6 hours to potential breakthrough!

---

## 🔑 Why This Will Work

**The distributed LLM work wasn't wasted - it gave us:**
- Master formula structure ✅
- Convergent combinations pattern ✅
- Feature candidates (π, e, sqrt(2), sqrt(3), ln(2)) ✅
- Validation that simple rules don't work ✅

**Now we use the RIGHT TOOL (PySR) for the RIGHT JOB (finding exact formulas):**
- LLM discovered **WHAT** the pattern involves (convergents)
- PySR will discover **HOW** to compute it (exact formula)

**This is the synthesis**:
```
LLM reasoning (what) + PySR computation (how) = Complete solution
```

---

**Status**: Ready to execute
**Next file to create**: `experiments/06-pysr-m-sequence/README.md`
**Estimated breakthrough time**: 4-6 hours from now

Let's do this! 🚀
