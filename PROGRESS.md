# Bitcoin Puzzle Analysis - Progress Tracker

## Project Status
**Last Sync**: 2025-12-18
**Current Phase**: Formula Derivation
**Barrier**: m_n generation rule unknown

---

## Verified Formula (100% confirmed)
```
k_n = 2 × k_{n-1} + adj_n
adj_n = 2^n - m_n × k_{d_n}
```

## Known Data
- **74 keys solved**: k1-k70, k75, k80, k85, k90
- **Formula verified**: All 70 consecutive keys (k1-k70)
- **m-sequence**: 24 values known (n=2..25)
- **d-sequence**: 24 values known (n=2..25)

---

## Session Log

### 2025-12-18: ALL 8 OPTIONS TESTED
**Tested approaches for m_n derivation:**

| Option | Method | Result |
|--------|--------|--------|
| 1 | Finite Differences | NOT polynomial |
| 2 | Linear Recurrence | NO pattern (order 2-6) |
| 3 | Modular Patterns | NO periodicity |
| 4 | Binary Analysis | NO clear pattern |
| 5 | Hash Derivation | NOT SHA256-based |
| 6 | Key Relationship | Formula VERIFIED |
| 7 | OEIS Search | NOT in database |
| 8 | Alt Decomposition | NO pattern found |

**Key Discoveries:**
- `m_n / 2^(n - d_n)` bounded in [0.72, 2.75], mean ≈ 1.66
- d_n is optimization-based (minimizes |m_n|), not predictable from n
- Normalized m clusters around simple fractions but is not deterministic
- Prime factorization of m_n shows no common structure

**Cluster Setup Completed:**
- Spark 1 (10.0.0.1): C-Solver (qwq:32b), B-Solver (phi4-reasoning:14b)
- Spark 2 (10.0.0.2): A-Solver (qwen3-vl:8b)
- 200Gbps link, 0.5ms latency confirmed
- Health check script: scripts/cluster_health.sh

**Next Steps:** Need new approaches beyond the original 8 options

### 2025-12-17: Formula Verification
- Confirmed recurrence: k_n = 2 × k_{n-1} + adj_n
- Derived decomposition: adj_n = 2^n - m_n × k_{d_n}
- Extracted m and d sequences for n=2..25

---

## Infrastructure

### Box 1 (Primary)
- **IP**: 10.0.0.1
- **GPU**: NVIDIA (Ollama)
- **RAM**: 119GB
- **Models**: qwq:32b, phi4-reasoning:14b, qwen3-vl:8b

### Box 2 (Secondary)
- **IP**: 10.0.0.2
- **Link**: 200Gbps (0.5ms latency)
- **Status**: Needs SSH setup

### Load Balancing Plan
```
Box 1 (10.0.0.1):          Box 2 (10.0.0.2):
├─ C-Solver (qwq:32b)      ├─ A-Solver (qwen3-vl:8b)
├─ Deep reasoning          ├─ Fast parallel search
└─ Formula derivation      └─ Brute force verification
```

---

## Files to Track

### Core Files
- `db/kh.db` - Key database (74 keys)
- `puzzle_config.py` - Configuration
- `CLAUDE.md` - Project instructions
- `ACTION_PLAN.md` - Current plan
- `CURRENT_BARRIER.md` - Barrier analysis

### Analysis Results
- `VERIFIED_FORMULAS_COMPLETE.json` - 26 exact formulas
- `agent_memory.db` - Agent insights

### Documentation
- `PROGRESS.md` - This file
- `FORMULA_REGISTRY.md` - Verified formulas

---

## Git Sync Commands
```bash
# Initial setup
git init
git remote add origin <repo-url>

# Sync progress
git add -A
git commit -m "Sync: $(date +%Y-%m-%d) - <summary>"
git push

# Pull on resume
git pull origin main
```

---

## Next Actions
1. [x] Setup SSH to Box 2 (Spark 2)
2. [x] Configure Ollama on Box 2 (A-Solver ready)
3. [x] Test Option 8 (Alt Decomposition) - NO PATTERN FOUND
4. [x] Extend m-sequence to n=70 - DONE
5. [ ] Explore EC scalar relationships
6. [ ] Test PRNG reconstruction with known seed patterns
7. [ ] Analyze creator's public commitment data (if available)
