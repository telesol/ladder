# Experiment 05: Complete Plan

## Vision

**Let PySR DISCOVER the ladder equation, then PROVE it cryptographically**

Not just matching hex - deriving full Bitcoin addresses from generated keys.

## Phase 1: Data Preparation ✅

### Input
- CSV: `btc_puzzle_1_160_full.csv`
- Columns: puzzle, address, key_hex_64

### Process
1. Load puzzles 1-70 (training set)
2. Extract last 16 bytes (little-endian for formula)
3. Create per-lane sequences:
   - Lane 0: [puzzle_1[0], puzzle_2[0], puzzle_3[0], ...]
   - Lane 1: [puzzle_1[1], puzzle_2[1], puzzle_3[1], ...]
   - ...
   - Lane 15: [puzzle_1[15], puzzle_2[15], puzzle_3[15], ...]

4. Create training pairs: `(X_k, k) → X_{k+1}`

### Output
- `data/train_lane_0.csv`, `data/train_lane_1.csv`, ..., `data/train_lane_15.csv`
- Each row: `puzzle_num, X_k, X_k+1`

## Phase 2: PySR Discovery 🔜

### Per-Lane Training

Train 16 separate PySR models (one per lane):

```python
from pysr import PySRRegressor

for lane in range(16):
    model = PySRRegressor(
        niterations=100,
        binary_operators=["+", "*"],
        unary_operators=["square", "cube"],
        populations=30,
        constraints={
            '*': (-1, 3),  # Limit complexity
        },
        maxsize=15,
    )

    # Fit: f(X_k, puzzle_num) → X_{k+1}
    model.fit(X_train, y_train)

    # Extract equation
    equation = model.sympy()
    print(f"Lane {lane}: {equation}")
```

### Expected Discoveries

Based on old AI's work:
- Most lanes: `X_{k+1} = X_k + C`
- Special lanes: `X_{k+1} = A * X_k + C`
- Lane 6: `X_{k+1} = 0` (always zero)

### Output
- Discovered equations per lane
- Coefficients (A matrix, drift patterns)
- Saved models: `models/lane_0.pkl`, ..., `models/lane_15.pkl`

## Phase 3: Cryptographic Validation ✅

### Implementation (`crypto_validator.py`)

```python
def validate_generated_key(private_key_hex, expected_address):
    # 1. Derive public key (ECDSA secp256k1)
    pubkey = ecdsa_derive(private_key_hex)

    # 2. Hash public key (SHA256 + RIPEMD160)
    pubkey_hash = ripemd160(sha256(pubkey))

    # 3. Encode to Bitcoin address (Base58Check)
    address = base58check_encode(pubkey_hash)

    # 4. Compare
    return address == expected_address
```

**Status**: ✅ Tested with puzzle 1 - WORKS!

### Key Finding

Bitcoin puzzle uses **COMPRESSED** public keys:
- Uncompressed: 04 + x + y (65 bytes)
- Compressed: 02/03 + x (33 bytes) ← **Puzzle uses this**

## Phase 4: End-to-End Pipeline 🔜

### Full Validation Loop

```python
# For each puzzle in validation set (71-95):

1. Use PySR equation to calculate next key
   privkey_71 = pysr_formula(puzzle_70)

2. Convert to full 32-byte format
   privkey_full = pad_to_32_bytes(privkey_71)

3. Derive Bitcoin address
   address_71 = derive_address(privkey_full)

4. Compare to CSV
   csv_address_71 = "1xxxxxxxxxxxxxxxxx"
   match = (address_71 == csv_address_71)

5. Report
   print(f"Puzzle 71: {match ? '✅' : '❌'}")
```

### Success Criteria

**Training (Puzzles 1-70)**:
- PySR discovers equations
- All 69 generated keys → correct Bitcoin addresses

**Validation (Puzzles 71-95)**:
- Use discovered equations
- Generate keys for puzzles 71-95
- Derive Bitcoin addresses
- **Goal**: >80% address matches (cryptographic proof)

## Phase 5: Analysis & Reporting 🔜

### Metrics to Report

1. **PySR Discovery**
   - Equations discovered per lane
   - Complexity scores
   - Training time

2. **Cryptographic Validation (Training)**
   - Puzzles 1-70: X/69 addresses match
   - Per-lane accuracy
   - Failed cases (if any)

3. **Extrapolation (Validation)**
   - Puzzles 71-95: X/25 addresses match
   - Which puzzles failed
   - Error analysis

4. **Formula Analysis**
   - Compare to old AI's affine formula
   - Identify A matrix from PySR
   - Understand drift patterns

### Output Files

- `results/pysr_equations.txt` - Discovered formulas
- `results/training_validation.json` - Address match results (1-70)
- `results/extrapolation_validation.json` - Address match results (71-95)
- `results/REPORT.md` - Human-readable summary

## Implementation Order

### Step 1: Data Preparation
File: `prepare_training_data.py`
- Load CSV
- Extract per-lane sequences
- Save training CSVs
**Time**: 30 min

### Step 2: PySR Training (One Lane First)
File: `train_pysr_single_lane.py`
- Train lane 0 only
- Verify it discovers correct equation
- Validate on puzzles 1-70
**Time**: 1-2 hours (PySR training)

### Step 3: Crypto Validation (Lane 0)
File: `validate_lane0_with_crypto.py`
- Generate keys using lane 0 equation
- Derive Bitcoin addresses
- Compare to CSV
**Time**: 30 min

### Step 4: Full System (All 16 Lanes)
File: `train_all_lanes.py`
- Train all 16 lanes
- Combine into unified formula
- Full cryptographic validation
**Time**: 2-3 hours

### Step 5: Extrapolation Test
File: `test_extrapolation_71_95.py`
- Generate puzzles 71-95
- Derive addresses
- Compare to CSV
**Time**: 30 min

## Key Differences from Previous Experiments

### Experiment 01 (PySR)
- ❌ Only validated hex matches
- ❌ No Bitcoin address derivation
- ✅ Discovered `x^n` pattern (partial)

### Experiment 04 (Verification)
- ✅ Verified old AI's formula
- ❌ No new discovery (just verification)
- ❌ No cryptographic proof

### Experiment 05 (This)
- ✅ PySR discovers equation from scratch
- ✅ Full cryptographic validation
- ✅ Proves keys are Bitcoin-valid
- ✅ Tests extrapolation (71-95)

## Expected Timeline

- **Day 1** (Today): Setup + Crypto validator ✅
- **Day 2**: Data prep + PySR lane 0 training
- **Day 3**: Full 16-lane training
- **Day 4**: Extrapolation + reporting

**Total**: ~4 days to complete

## Success Definition

**Minimum Success**:
- PySR discovers equations for at least 8/16 lanes
- Training set: >95% Bitcoin address matches
- Validation set: >50% Bitcoin address matches

**Full Success**:
- PySR discovers equations for all 16 lanes
- Training set: 100% Bitcoin address matches
- Validation set: >80% Bitcoin address matches
- Equations match old AI's affine formula

**Breakthrough**:
- Validation set: 100% Bitcoin address matches
- Proves ladder is learnable from data
- Can generate puzzles 96-160 with confidence

## Next Steps

1. ✅ Create crypto_validator.py - DONE
2. 🔜 Create prepare_training_data.py
3. 🔜 Create train_pysr_single_lane.py
4. 🔜 Test on lane 0 with crypto validation
5. 🔜 Extend to all 16 lanes

**Status**: Ready to build data preparation
