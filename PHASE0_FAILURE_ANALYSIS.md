# Phase 0 Failure Analysis - Critical Discovery
## Date: 2025-12-22
## Finding: PySR Formula Does NOT Work Forward!

---

## 🚨 THE CRITICAL DISCOVERY

**Test**: Calculate X_75 from X_70 using proven PySR formula
**Result**: **37.5% accuracy (6/16 lanes match)**
**Verdict**: **Formula does NOT work for forward generation!**

---

## 📊 Test Results

### What We Tested

```python
# Start: X_70 (known from CSV)
X_70 = [0, 0, 0, 0, 0, 0, 0, 52, 155, 132, 182, 67, 26, 108, 78, 241]

# Formula: X_{k+1}[lane] = (X_k[lane])^n mod 256
# Exponents: [3, 2, 3, 2, 2, 3, 0, 2, 2, 3, 3, 2, 2, 2, 2, 3]

# Iterate 5 times: X_70 → X_71 → X_72 → X_73 → X_74 → X_75
```

### What We Got

```
X_70 (start):       00000000000000349b84b6431a6c4ef1
X_71 (step 1):      0000000000000090d9401889a490c4d1
X_72 (step 2):      0000000000000000f100005110001071
X_73 (step 3):      0000000000000000e10000a100000051
X_74 (step 4):      0000000000000000c1000041000000f1
X_75 (calculated):  000000000000000081000081000000d1  ← What we calculated
X_75 (actual):      00000000000004c5ce114686a1336e07  ← What it should be
```

### Lane-by-Lane Comparison

| Lane | Exp | X_70 | Calculated | Actual | Match? | Diff |
|------|-----|------|------------|--------|--------|------|
| 0 | 3 | 0 | 0 | 0 | ✓ | 0 |
| 1 | 2 | 0 | 0 | 0 | ✓ | 0 |
| 2 | 3 | 0 | 0 | 0 | ✓ | 0 |
| 3 | 2 | 0 | 0 | 0 | ✓ | 0 |
| 4 | 2 | 0 | 0 | 0 | ✓ | 0 |
| 5 | 3 | 0 | 0 | 0 | ✓ | 0 |
| 6 | 0 | 0 | 0 | 4 | ✗ | -4 |
| 7 | 2 | 52 | 0 | 197 | ✗ | -197 |
| 8 | 2 | 155 | 129 | 206 | ✗ | -77 |
| 9 | 3 | 132 | 0 | 17 | ✗ | -17 |
| 10 | 3 | 182 | 0 | 70 | ✗ | -70 |
| 11 | 2 | 67 | 129 | 134 | ✗ | -5 |
| 12 | 2 | 26 | 0 | 161 | ✗ | -161 |
| 13 | 2 | 108 | 0 | 51 | ✗ | -51 |
| 14 | 2 | 78 | 0 | 110 | ✗ | -110 |
| 15 | 3 | 241 | 209 | 7 | ✗ | 202 |

**Matches**: 6/16 (37.5%)
**Mismatches**: 10/16 (62.5%)

---

## 🔍 WHAT WENT WRONG?

### The Deceptive "100% Accuracy"

**PySR claimed 100% accuracy on puzzles 1-70**. What did this actually mean?

**Verification Test** (what PySR did):
```python
# Given: X_k and X_{k+1} (both known)
# Test: Does X_{k+1} == f(X_k)?
# Result: YES, 100% match!
```

**Generation Test** (what we need):
```python
# Given: X_k only
# Calculate: X_{k+1} = f(X_k)
# Test: Does calculated X_{k+1} == actual X_{k+1}?
# Result: NO, only 37.5% match!
```

### Why Verification ≠ Generation

**The formula X_{k+1} = X_k^n works as a DESCRIPTOR but not a GENERATOR!**

Think of it like:
- **Verification**: "Does this key fit this lock?" ✓ (works!)
- **Generation**: "Generate the key from the lock" ✗ (doesn't work!)

The PySR formula describes a relationship but **omits critical information** needed for generation!

---

## 💡 THE MISSING PIECE: DRIFT TERMS

### The Real Formula

The actual generation formula is:

```
X_{k+1}[lane] = (A[lane]^4 * X_k[lane] + drift[k→k+1][lane]) mod 256
```

**NOT**:
```
X_{k+1}[lane] = X_k[lane]^n mod 256
```

### Why Drift Matters

The **drift terms** carry essential information:
- They encode the transition from k to k+1
- They vary for each step (not constant!)
- They cannot be derived from X_k alone
- They must be either:
  - Looked up from calibration data
  - Calculated from a generator function
  - Interpolated from bridges

**Without drift → Cannot generate forward!**

---

## 📈 PATTERNS IN THE FAILURE

### Observation 1: Zeros Collapse

Notice how calculated values become mostly zeros:
```
X_71: 0000000000000090d9401889a490c4d1  (some non-zero)
X_72: 0000000000000000f100005110001071  (more zeros)
X_73: 0000000000000000e10000a100000051  (even more)
X_74: 0000000000000000c1000041000000f1
X_75: 000000000000000081000081000000d1  (mostly zeros!)
```

**Why?**
- Small values: x^2 or x^3 mod 256 often → 0
- Without drift injection, system loses energy
- Converges to attractor (all zeros)

### Observation 2: Lane 6 Already Wrong at Step 5

```
Lane 6 (exponent 0): calculated=0, actual=4
```

Even though exponent is 0 (should stay constant), actual value changed!

**This proves drift is injected between steps!**

### Observation 3: First 6 Lanes Match (All Zero)

Lanes 0-5 match because they START at zero and STAY at zero.

But lanes 7-15 (non-zero starting values) all diverge!

**Conclusion**: Formula only works when values stay at zero attractors.

---

## 🎯 WHAT THIS MEANS

### 1. PySR Discovery Was Incomplete

PySR found a **pattern** in the data:
- "X_k^n is correlated with X_{k+1}"
- TRUE! But incomplete.

It did NOT find the **generator**:
- "X_{k+1} can be CALCULATED from X_k using only X_k^n"
- FALSE!

### 2. The "100% Proof" Was Misleading

The proof in `experiments/01-pysr-symbolic-regression/PROOF.md` shows:
- ✅ The formula DESCRIBES the relationship
- ❌ The formula does NOT GENERATE the values

**Verification ≠ Generation!**

### 3. We Need the Affine Model

The affine model with drift:
```
X_{k+1} = A^4 * X_k + drift
```

has 100% accuracy because it INCLUDES the missing information (drift).

**Location**: `experiments/05-ai-learns-ladder/out/ladder_calib_CORRECTED.json`

---

## 🔬 INVESTIGATION TASKS FOR LOCAL MODELS

### Task 1: Reverse-Engineer Drift from Known Transitions

```python
# We know: X_70 → X_75 (actual)
# We calculated: X_75 (formula only)

# Question: What drift values would correct our calculation?

for each step k in [70, 71, 72, 73, 74]:
    drift[k] = X_{k+1}_actual - f(X_k_actual)
    # This gives us the "missing piece" for each transition
```

**Run this on local model!**

### Task 2: Test Affine Model Forward

```python
# Load: ladder_calib_CORRECTED.json
# Contains: A values and drift values for transitions 1→2, 2→3, ..., 69→70

# Test: Can we calculate X_71 from X_70 using affine model?
X_71_calculated = A^4 * X_70 + drift[70→71]

# Problem: We don't have drift[70→71] in calibration!
# (Calibration only goes up to 70)
```

**Investigate if drift can be extrapolated!**

### Task 3: Bridge Interpolation Strategy

```python
# Known: X_70, X_75
# Unknown: X_71, X_72, X_73, X_74

# Can we interpolate drift values?
# Linear interpolation?
# Polynomial interpolation?
# Pattern from previous drifts?
```

**Run interpolation experiments!**

---

## 📋 ACTION ITEMS

### Immediate (Next 30 minutes)

1. ✅ Create this analysis document
2. ⏳ Test affine model forward calculation
3. ⏳ Extract drift pattern from calibration file
4. ⏳ Attempt drift extrapolation/interpolation

### Short-term (Next 2-4 hours)

1. ⏳ Run local model investigation tasks
2. ⏳ Test multiple drift prediction strategies
3. ⏳ Validate on known bridges (75, 80, 85, 90, 95)
4. ⏳ Document what works

### Medium-term (Next session)

1. ⏳ If drift prediction works → Generate puzzles 71-160
2. ⏳ If drift prediction fails → Revisit 4xH research
3. ⏳ Cross-validate using multiple approaches

---

## 🎓 LESSONS LEARNED

### Lesson 1: Verification ≠ Generation

A model can be perfect at CHECKING answers but useless at CREATING answers.

Always test forward generation, not just backward verification!

### Lesson 2: "100% Accuracy" Needs Context

PySR's "100% accuracy" was for:
- Task: Verification
- NOT for: Generation

Always clarify WHAT the accuracy measures!

### Lesson 3: Missing Information Can Be Hidden

The drift terms were the missing information all along.

They were hidden in the calibration file but not in the PySR formula.

### Lesson 4: Simple ≠ Complete

The PySR formula (X^n) is simpler than the affine formula (A^4*X + drift).

But simplicity came at the cost of completeness!

**Complex reality > Simple fiction**

---

## 🚀 NEXT STEPS

### Option A: Use Affine Model Directly

**Pros**:
- Has 100% accuracy on 1-70
- Includes drift terms
- Already calibrated

**Cons**:
- No drift for 71-160 (need to generate/predict)
- Requires drift generator or interpolation

**Status**: RECOMMENDED

### Option B: Improve PySR Formula

**Pros**:
- Simpler model
- Already discovered

**Cons**:
- Fundamentally incomplete
- Cannot work without drift terms

**Status**: NOT VIABLE

### Option C: Hybrid Approach

**Pros**:
- Use affine for structure (A^4 * X)
- Use PySR pattern for validation
- Use interpolation for drift

**Cons**:
- Complex
- Multiple failure points

**Status**: BACKUP PLAN

---

## 📊 SUMMARY TABLE

| Model | Verification Accuracy | Generation Accuracy | Usable? |
|-------|---------------------|-------------------|---------|
| **PySR (X^n)** | 100% | 37.5% | ❌ NO |
| **Affine (A^4*X + drift)** | 100% | 100% (with drift) | ✅ YES |
| **Period-5 Recurrence** | N/A | 18.46% | ❌ NO |

**Conclusion**: Use affine model with drift terms!

---

## 🎯 CRITICAL REALIZATION

**The entire project hinges on one thing: DRIFT GENERATION!**

**If we can generate/predict drift[70→71], drift[71→72], ..., drift[159→160]:**
- ✅ We can use affine model to generate ALL puzzles
- ✅ 100% accuracy (proven on 1-70)
- ✅ Project complete!

**If we cannot generate drift:**
- ❌ PySR formula doesn't work forward
- ❌ Period-5 theory doesn't apply
- ❌ Back to square one

**THIS is why the 4xH drift research matters!**

But we predicted H1-H3 would fail (drift depends on X_k, not just indices).

**New hypothesis**: Maybe drift CAN be predicted from the SEQUENCE of X values, not just indices!

---

**Status**: Analysis complete, ready for next phase
**Next**: Test affine model forward, investigate drift prediction strategies
