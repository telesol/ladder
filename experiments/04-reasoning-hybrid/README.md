# Experiment 04: Reasoning-Hybrid System

**Vision**: AI as the Brain 🧠, PySR as the Calculator 🔢

## Quick Summary

Instead of training a neural network to learn the pattern from scratch (which failed in Exp 02), we train the AI to:

1. **REASON** about the problem (understand puzzle structure)
2. **DECIDE** which operations to apply (choose exponents per lane)
3. **EXECUTE** via PySR calculator (proven 100% accurate)
4. **VALIDATE** results (confidence scoring)

## Key Insight

The AI doesn't need to rediscover `X_{k+1} = X_k^n mod 256`. It just needs to:
- Learn which exponents to use: [3,2,3,2,2,3,0,2,2,3,3,2,2,2,2,3]
- Know when to apply the formula
- Validate outputs make sense

## Approach

```
Puzzles 1-70  →  [AI Brain]  →  Exponent Calculation
                      ↓
                 [PySR Calculator]  →  Next Puzzle
                      ↓
                 [AI Validator]  →  Confidence Score
```

## Prototype Goals (2-4 hours)

✅ Can AI learn to calculate exponents? (Target: >80% accuracy)
✅ Does PySR interface work? (Should be 100%)
✅ Can we generate puzzle 71? (Target: >50% byte accuracy)

## Files

- **PLAN.md** - Comprehensive planning document
- **prototype/** - Minimal viable prototype (start here)
- **data/** - Data loading and preparation
- **scripts/** - Training and testing scripts
- **results/** - Output and metrics

## Status

🔜 **Phase 1: Planning** - DONE
🔜 **Phase 2: Prototype** - READY TO START
⏸️ **Phase 3: Validation** - Pending prototype success
⏸️ **Phase 4: Production** - Pending validation success

## Next Action

Start building the prototype! See PLAN.md Section 2.2 for implementation steps.

**Time to first results**: ~3-4 hours
**Go/No-Go decision point**: After prototype testing
