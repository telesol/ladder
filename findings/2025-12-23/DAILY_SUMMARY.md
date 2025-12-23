# Daily Summary: 2025-12-23

## Major Discoveries

### 1. **Phase Change at Puzzle 70** (Zbook)
- **Discovery**: Drift becomes ~0 after puzzle 70
- **Formula**: `X_{k+1}[lane] = X_k[lane]^n mod 256` (no drift!)
- **Verification**: 99.3% pure exponential (152/153 transitions)
- **Impact**: Generated 48 intermediate puzzles (71-129)
- **Location**: `findings/2025-12-23/zbook_phase_change/`

### 2. **PySR Pattern Discovery** (LA - Claude Opus)
- **Method**: Symbolic regression on 82 known puzzles
- **Findings**:
  - c[n] oscillation: sin(mod(...)) periodic pattern
  - d_gap: depends on both n AND log10(m[n])
  - adj[n] signs: nested modular arithmetic
  - Seed constants: repeated values (-0.336, -0.971)
- **Location**: `findings/2025-12-23/la_pysr_analysis/`

### 3. **Wave 17 Dataset** (Victus)
- **Update**: Complete 82-key dataset
- **Finding**: Oscillation pattern breaks at n=100
- **Status**: Merged to main branch

## Integration Status

- [ ] Merge Zbook's local-work branch
- [ ] Validate generated puzzles with AI
- [ ] Reconcile PySR findings with phase change
- [x] Pull Wave 17 updates

## Next Steps

1. Cross-validate Zbook's 48 generated puzzles
2. Re-run PySR on simple phase (71-130)
3. Have QWQ analyze phase change implications
4. Update master findings document

## Timeline

- 05:00-08:00: Parallel exploration runs
- 08:10-08:20: PySR jobs launched and completed
- 08:22: Zbook phase change discovery
- 08:30: Integration planning (current)
