# Experiment 05: PySR + Cryptographic Validation

**Goal**: Let PySR DISCOVER the ladder equation, then PROVE it's correct by deriving Bitcoin addresses

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  EXPERIMENT 05 PIPELINE                      │
└─────────────────────────────────────────────────────────────┘

1. DATA PREPARATION
   ├─> Load puzzles 1-70 (training)
   ├─> Extract per-lane sequences
   └─> Create features: X_k(ℓ) → X_{k+1}(ℓ)

2. PYSR DISCOVERY (Per-Lane Learning)
   ├─> Train 16 separate PySR models (one per lane)
   ├─> Discover equations: f(X_k, k) → X_{k+1}
   ├─> Extract discovered formulas
   └─> Save coefficients/equations

3. FORMULA SYNTHESIS
   ├─> Combine 16 lane equations into full model
   ├─> Identify patterns (A matrix, drift functions)
   └─> Create unified ladder equation

4. CRYPTOGRAPHIC VALIDATION ⭐ (THE KEY PART)
   ├─> Generate private key using discovered formula
   ├─> Compute public key (ECDSA secp256k1)
   ├─> Hash: SHA256 → RIPEMD160
   ├─> Encode: Base58Check → Bitcoin address
   └─> Compare to CSV address (PROOF!)

5. EXTRAPOLATION TEST
   ├─> Generate puzzles 71-95
   ├─> For each: derive full Bitcoin address
   ├─> Compare to known addresses in CSV
   └─> Report match rate
```

## Why This Approach?

### The User's Vision

> "we need PySR to do the simple math and the Neural network to guide it and verify"

**PySR**: Discovers the mathematical ladder equation from data
**Neural Network/AI**: Guides the process, validates cryptographically
**Validation**: Not just hex matching, but FULL Bitcoin address derivation

### What Makes This Different?

**Experiment 01** (Previous PySR):
- ❌ Only matched hex patterns
- ❌ No cryptographic validation
- ❌ Didn't derive Bitcoin addresses

**Experiment 05** (This):
- ✅ PySR discovers equation
- ✅ Full cryptographic validation
- ✅ Derives Bitcoin addresses from scratch
- ✅ Proves keys are cryptographically valid

## Success Criteria

### Training Phase (Puzzles 1-70)
- ✅ PySR discovers equation per lane
- ✅ Generated keys → Bitcoin addresses match CSV 100%

### Validation Phase (Puzzles 71-95)
- ✅ Generated keys → Bitcoin addresses match CSV
- ✅ Extrapolation accuracy measured
- ✅ Equation proven on unseen data

## Components

### 1. Data Loader
- Load CSV with addresses + private keys
- Extract per-lane sequences
- Prepare training/validation split

### 2. PySR Trainer
- Train one model per lane
- Search space: addition, multiplication, modulo
- Discover: `X_{k+1}(ℓ) = f(X_k(ℓ), k)`

### 3. Crypto Validator
- ECDSA point multiplication (secp256k1)
- SHA256 + RIPEMD160 hashing
- Base58Check encoding
- Address comparison

### 4. End-to-End Pipeline
- Generate key → Derive address → Validate
- Report: "Puzzle 71: Address Match ✅" or "❌"

## Key Insight

**From user's feedback**:
> "the model should derive the public key, hash it ripemd160 and get the bitcoin address and match it to the csv file"

This is the REAL validation - not just matching hex strings, but proving the keys are cryptographically correct by deriving the full Bitcoin address.

## Files to Create

1. `prepare_data.py` - Load and structure data for PySR
2. `train_pysr_per_lane.py` - Train 16 PySR models
3. `crypto_validator.py` - Bitcoin address derivation
4. `validate_with_addresses.py` - End-to-end validation
5. `generate_71_95.py` - Extrapolation with crypto proof

## Status

**Created**: 2025-12-01
**Status**: 🔜 Ready to build
**Priority**: HIGH - User's core requirement
