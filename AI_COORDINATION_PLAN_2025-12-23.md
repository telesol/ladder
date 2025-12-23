# AI Coordination Plan: Drift Generator Research

**Date**: 2025-12-23
**Objective**: Distribute H1-H4 drift generator research across local AI models
**Goal**: Find drift[k][lane] = f(k, lane) to generate puzzles 71+

---

## Available AI Models

| Model | Size | Type | Specialization |
|-------|------|------|----------------|
| **qwen2.5-coder:7b** | 4.7 GB | Local | Code generation, algorithms |
| **olmo-3:7b-think** | 4.5 GB | Local | Reasoning, logical analysis |
| **qwen2.5:3b-instruct** | 1.9 GB | Local | Fast coordination, orchestration |
| **nemotron-3-nano:30b** | Cloud | Cloud | Deep security analysis |
| **gpt-oss:120b** | Cloud | Cloud | Comprehensive pattern analysis |
| **kimi-k2:1t** | Cloud | Cloud | Massive-scale reasoning |

---

## Task Distribution

### H1: Index-Based Generator
**Assigned to**: `qwen2.5-coder:7b` (local)

**Hypothesis**: `drift[k][lane] = polynomial(k, lane) or modular_arithmetic(k, lane)`

**Strategy** (from qwen2.5-coder):
1. Test polynomial functions: `drift = (a*k + b*lane + c) mod 256`
2. Test exponentiation: `drift = (k^2 + lane*k) mod 256`
3. Test XOR patterns: `drift = ((k XOR lane) * constant) mod 256`
4. Use PySR symbolic regression for automated discovery

**Time Estimate**: 2-3 hours (CPU), 30 min (with PySR)

**Success Criteria**: ≥90% match on puzzles 1-70, validate on multi-step bridge drift

**Tools**:
- Python + NumPy
- PySR (symbolic regression)
- `research_H1_index_based.py` (already exists)
- `drift_data_export.json` (1,104 values)

**Output**: `H1_results.json` with best formula and accuracy

---

### H2: Cryptographic Hash Function
**Assigned to**: `nemotron-3-nano:30b` (cloud) + `qwen2.5-coder:7b` (execution)

**Hypothesis**: `drift[k][lane] = hash_function(k, lane) mod 256`

**Strategy**:
1. Test standard hashes: SHA256, MD5, RIPEMD160
2. Test Bitcoin-specific: double SHA256, HASH160
3. Test various encodings: (k, lane), (k||lane), (k+lane), (k*lane)
4. Test salted hashes: hash(k || lane || salt)
5. Brute force common seeds/salts (if pattern detected)

**Reasoning** (Nemotron's specialization):
- Bitcoin puzzle likely uses Bitcoin-native hash functions
- Double SHA256 is Bitcoin's core primitive
- HASH160 (SHA256 + RIPEMD160) used for addresses
- May use puzzle creator's signature as salt

**Time Estimate**: 2-3 hours

**Success Criteria**: ≥95% match (hash functions should be exact or fail completely)

**Tools**:
- Python `hashlib`, Bitcoin crypto libraries
- `research_H2_hash_function.py` (already exists)

**Output**: `H2_results.json` with matching hash function (if found)

---

### H3: PRNG (Pseudo-Random Generator)
**Assigned to**: `olmo-3:7b-think` (local) + `qwen2.5:3b-instruct` (execution)

**Hypothesis**: `rng = PRNG(seed); drift = rng.next() mod 256`

**Strategy** (olmo-3 reasoning):
1. Test standard PRNGs: Python random, NumPy random, MT19937
2. Test LCG (Linear Congruential Generator) variants
3. Brute force seed search (0-1000000 for common PRNGs)
4. Test if drift[1] or drift[0][0] is the seed
5. Test Bitcoin block hashes as potential seeds

**Key Insight** (olmo-3 thinking):
- If PRNG, sequence must be reproducible
- Seed likely derived from puzzle constants or creator info
- Bitcoin puzzle block #1 hash could be seed source
- Test deterministic RNGs only (no time-based seeds)

**Time Estimate**: 3-4 hours (seed brute force is expensive)

**Success Criteria**: ≥99% match (PRNG should be exact or very close)

**Tools**:
- Python `random`, `numpy.random`
- Custom LCG implementations
- `research_H3_prng.py` (already exists)

**Output**: `H3_results.json` with PRNG type and seed (if found)

---

### H4: Recursive Pattern (Drift Ladder)
**Assigned to**: `gpt-oss:120b` (cloud) + `qwen2.5-coder:7b` (execution)

**Hypothesis**: `drift[k+1] = f(drift[k])` - drift has its own recurrence!

**Strategy** (gpt-oss comprehensive analysis):
1. Test affine recurrence: `drift[k+1][lane] = (A*drift[k][lane] + C) mod 256`
2. Test polynomial: `drift[k+1] = (drift[k]^n + offset) mod 256`
3. Test multi-step patterns: `drift[k+5] = f(drift[k])`
4. Test lane coupling: `drift[k+1][lane] = f(drift[k][lane-1], drift[k][lane])`
5. Validate against 90.8% constant multi-step drift finding

**Why gpt-oss** (pattern analysis strength):
- Can analyze complex multi-dimensional patterns
- Excellent at finding hidden recurrence relationships
- Can reason about connections between X_k formula and drift formula
- May discover drift inherits structure from X_k evolution

**Time Estimate**: 2-3 hours

**Success Criteria**: ≥80% match (recursive may have cumulative error)

**Tools**:
- Python + NumPy
- PySR (for automated pattern discovery)
- `research_H4_recursive.py` (already exists)

**Output**: `H4_results.json` with recurrence formula and accuracy

---

## Coordination Strategy

### Phase 1: Parallel Execution (2-4 hours)
**Orchestrator**: `qwen2.5:3b-instruct`

Run all 4 hypotheses in parallel:
```bash
# Can run simultaneously
python3 research_H1_index_based.py > H1.log 2>&1 &
python3 research_H2_hash_function.py > H2.log 2>&1 &
python3 research_H3_prng.py > H3.log 2>&1 &
python3 research_H4_recursive.py > H4.log 2>&1 &
```

**Monitor progress**: Check logs every 30 minutes

### Phase 2: Results Analysis (30 min)
**Analyzer**: `qwen2.5:3b-instruct` + `gpt-oss:120b`

Collect results:
```bash
python3 analyze_all_results.py
```

Rank by accuracy:
- 100%: ✅ Generator FOUND!
- 90-99%: 🔥 Very close, refine
- 80-89%: 👍 Good, combine approaches
- <80%: 🤔 Need advanced methods

### Phase 3: Refinement (if needed)
**Strategist**: `gpt-oss:120b`

If no 100% match:
1. Combine best 2-3 approaches (hybrid)
2. Test hybrid: `drift = H1_result XOR H2_result`
3. Use AI to suggest refinements based on error patterns

### Phase 4: Validation
**Validator**: `qwen2.5-coder:7b`

Test discovered formula:
1. Generate drift for puzzles 1-70 ✓
2. Compute multi-step drift for bridges
3. Verify against 90.8% constant drift pattern
4. Generate puzzles 71-95 using formula
5. Cryptographic validation (if possible)

---

## AI Consultation Summaries

### qwen2.5-coder:7b (H1 Strategy)
**Response received**: ✅

Key points:
- Start with polynomial (a*k + b*lane + c) mod 256
- Test modular exponentiation
- Use PySR for automated discovery
- Target 95% accuracy
- Time: 1-2 hours

### olmo-3:7b-think (H3 Reasoning)
**Status**: To be consulted

Expected insight:
- PRNG seed source analysis
- Deterministic vs non-deterministic
- Bitcoin block hash connection
- Reproducibility requirements

### nemotron-3-nano:30b (H2 Security Analysis)
**Status**: To be consulted (cloud)

Expected insight:
- Bitcoin-specific hash functions
- Cryptographic patterns
- Salt/seed candidates
- Security implications

### gpt-oss:120b (H4 Pattern Analysis)
**Status**: To be consulted (cloud)

Expected insight:
- Multi-dimensional recurrence patterns
- Drift-X_k structural connections
- Hidden symmetries
- Cumulative error analysis

---

## Success Scenarios

### Best Case: 100% Match Found
**Action**:
1. Validate on all datasets
2. Generate puzzles 71-130
3. Document discovery
4. Publish methodology

**Timeline**: Immediate (same session)

### Good Case: 90-99% Match
**Action**:
1. Analyze error patterns
2. Refine formula
3. Test hybrid approaches
4. Iterate until 100%

**Timeline**: 1-2 additional sessions

### Learning Case: <90% Match
**Action**:
1. Document what DOESN'T work
2. Use findings to constrain search space
3. Consider advanced methods (NN, genetic algorithms)
4. Wait for more data (puzzles 131+)

**Timeline**: Research continues

---

## Execution Plan

### Immediate (This Session):
1. ✅ Check available models
2. ✅ Create coordination plan (this document)
3. ⏳ Run H1 research (qwen2.5-coder)
4. ⏳ Run H2 research (local execution)
5. ⏳ Run H3 research (olmo-3 thinking)
6. ⏳ Run H4 research (local execution)

### Next 2-4 Hours:
- Monitor all 4 research scripts
- Collect results
- Analyze with AIs
- Determine winner or hybrid approach

### If Successful:
- Generate puzzles 71-95
- Validate against bridges
- Document breakthrough
- Push to GitHub

---

## Files Created/Used

**Input**:
- `drift_data_export.json` - 1,104 drift values (puzzles 1-70)

**Research Scripts** (already exist):
- `research_H1_index_based.py`
- `research_H2_hash_function.py`
- `research_H3_prng.py`
- `research_H4_recursive.py`
- `analyze_all_results.py`

**Output** (to be generated):
- `H1_results.json` - Index-based results
- `H2_results.json` - Hash function results
- `H3_results.json` - PRNG results
- `H4_results.json` - Recursive results
- `analysis_report.json` - Final ranked comparison

**Documentation**:
- `AI_COORDINATION_PLAN_2025-12-23.md` - This document
- `DRIFT_GENERATOR_RESEARCH_PLAN.md` - Detailed hypothesis docs

---

## AI Role Summary

| AI | Role | Task | Why |
|----|------|------|-----|
| **qwen2.5-coder:7b** | Executor | H1 + execution | Fast, code-focused, local |
| **olmo-3:7b-think** | Reasoner | H3 strategy | Thinking/logic focused |
| **qwen2.5:3b-instruct** | Orchestrator | Coordination | Fast, lightweight |
| **nemotron-3-nano:30b** | Security Analyst | H2 strategy | Crypto expertise |
| **gpt-oss:120b** | Pattern Analyst | H4 strategy | Comprehensive analysis |
| **kimi-k2:1t** | Reserve | Advanced methods | If basic approaches fail |

---

## Current Status

- [x] Models identified
- [x] Tasks distributed
- [x] H1 strategy received (qwen2.5-coder)
- [ ] Execute H1-H4 research
- [ ] Collect and analyze results
- [ ] Validate winner
- [ ] Generate puzzles 71+

**Ready to execute**: All 4 research scripts are prepared and ready to run!

---

*Created: 2025-12-23*
*Orchestrator: Claude Code (Sonnet 4.5)*
*Execution: Local + Cloud AI models*
