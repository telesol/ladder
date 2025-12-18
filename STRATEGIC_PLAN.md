# Strategic Plan - Bitcoin Puzzle Ladder System

## Current State Assessment

### Proven Capabilities
- Affine recurrence model: `y ≡ A[l] * x + C[k][l][occ] (mod 256)` - VALIDATED
- 82/160 puzzles solved in database
- 100% verification accuracy on known puzzles
- Autonomous system operational with learning enabled
- Multi-agent coordination functional

### Key Mathematical Insight
The "ladder" is a **byte-wise affine transformation** where:
- Each of 16 lanes (byte positions) evolves independently
- Most lanes have A=1 (identity + drift)
- 4 lanes have strong multipliers: A[1]=91, A[5]=169, A[9]=32, A[13]=182

### The Gap
Current system proves math on **single bytes** but Bitcoin keys are **32 bytes**.
We need to understand how the 16-lane model maps to 32-byte keys.

---

## Priority 1: Understand Key Structure

### Question to Answer
How does a 256-bit (32-byte) Bitcoin private key map to 16 lanes?

**Hypothesis A**: First 16 bytes only (lanes 0-15 = bytes 0-15)
**Hypothesis B**: Interleaved (lane 0 = bytes 0,16; lane 1 = bytes 1,17; etc.)
**Hypothesis C**: Little-endian packed (lane format already discovered)

### Action Items
1. Examine `actual_hex` format in database for solved puzzles
2. Compare database storage vs Bitcoin standard format
3. Verify byte ordering (we already fixed little-endian conversion)

---

## Priority 2: Extend Calibration Beyond Puzzle 70

### Current State
- Calibration file covers puzzles 29-70 (block 0 and partial block 1)
- Block structure: 32 puzzles per block
- Bridge puzzles available: 75, 80, 85, 90, 95, 100, 105, 110, 115, 120, 125, 130

### Challenge
To solve unsolved puzzles, we need C[block 1] drift constants, which require:
- Known puzzle 70 (have it)
- Known unsolved puzzles (DON'T have it - that's the target!)

### Solution Approaches

**Approach A: Bridge Interpolation**
Use bridges (75, 80, etc.) to infer drift patterns for missing puzzles.
- From 70→75: 5 steps, can compute C if pattern is consistent
- Risk: Drift may not be constant across block boundaries

**Approach B: Pattern Extrapolation**
Analyze drift progression in block 0 (puzzles 29-60) to predict block 1 drift.
- Look for linear, cyclic, or other patterns in C values
- Risk: Pattern may break at block boundary

**Approach C: Constraint Satisfaction**
Given puzzle 70 and bridges 75, 80, set up system of equations.
- More unknowns (puzzles 71-74) but also more constraints (bridges)
- Could be solvable if system is overdetermined

---

## Priority 3: Full Key Recovery Pipeline

### Current Capability
```
Puzzle N (known) → Affine equations → Single byte X → Verified
```

### Target Capability
```
Puzzle N (known) → Affine equations for all 16 lanes → 16 bytes → Full key
```

### Implementation Steps
1. For each lane (0-15), compute the byte value using affine math
2. Assemble 16 bytes into key (respecting byte order)
3. Convert to Bitcoin format (handle endianness)
4. Derive public key and address
5. Verify against known puzzle address

---

## Priority 4: Attack Unsolved Puzzles

### Nearest Targets
- **unsolved puzzles**: First unsolved, requires block 1 drift
- **Puzzle 72-74**: Same block, same drift challenge
- **Puzzle 76-79**: Between bridges 75 and 80

### Strategy for unsolved puzzles
1. Use puzzle 70 as anchor (known, verified)
2. Apply forward affine step for each lane
3. Drift constants from extrapolation or bridge analysis
4. Generate candidate key
5. Verify against unsolved puzzles's known address

---

## Recommended Immediate Actions

### Today (Quick Wins)
1. [ ] Verify byte ordering in current calculate_puzzle() function
2. [ ] Test full 16-lane calculation on known puzzle (e.g., puzzle 50)
3. [ ] Compare calculated key with database - should match exactly

### This Week
1. [ ] Analyze drift patterns in existing calibration (C values over puzzles)
2. [ ] Attempt bridge-based drift estimation for block 1
3. [ ] Implement full key assembly from 16-lane outputs

### Next Week
1. [ ] Generate candidate key for unsolved puzzles
2. [ ] Verify against blockchain
3. [ ] If successful, automate for puzzles 72-74

---

## Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Solved puzzles | 82 | 83+ |
| Full key recovery | 0 | 1+ |
| Calibration range | 29-70 | 29-130 |
| Autonomous success rate | 100% (on known) | 100% (on unknown) |

---

## Risk Assessment

### High Risk
- Drift pattern may not be predictable beyond calibration
- Block boundaries may introduce discontinuities
- Model assumptions may break for higher puzzles

### Mitigation
- Use multiple approaches (interpolation, extrapolation, constraint)
- Validate each step against known bridges

---

## Technical Debt to Address

1. **Logging**: Now recording learnings - monitor for insights
2. **Calibration files**: Need unified format for extended range
3. **Byte ordering**: Already fixed, but verify everywhere
4. **GPU acceleration**: Not urgent until solving works

---

*Generated: 2025-12-09*
*System Status: Operational, Learning Enabled*
