# Bitcoin Puzzle Analysis Project

## ⚠️ CLAUDE: READ THIS FIRST
**NO PREDICTION. NO ASSUMPTIONS. READ THE RULES. IF LOST, ASK THE USER.**

You are the ORCHESTRATOR. You have 4 Spark nodes (128GB RAM, 1 pflop each) with local AI models.
- **YOUR JOB:** Coordinate, log findings, update repo, delegate research to local models
- **NOT YOUR JOB:** Do the research yourself, make assumptions, go off on tangents

## Project Status
**Last Updated**: 2025-12-19

## SESSION RESUME POINT (2025-12-19)
- **Progress:** 34 formulas verified (n=2 to n=35)
- **Next task:** COMPUTE factorizations first, THEN pattern recognition
- **Key file:** `FORMULA_SUMMARY.md` has all verified formulas
- **IMPORTANT:** m[2]=1, m[3]=1 (NOT 3,7 as some old task files state)
- **Data source:** `data_for_csolver.json` has correct m_seq, d_seq
- **NEW PLAN:** `PLAN_COMPUTE_THEN_REASON.md` - compute with Python, reason with LLMs
- **COLLABORATION:** User uploading experiment from laptop - check `/home/solo/LA/experiments/`

## PRIMARY GOAL
**Derive the key generation FORMULA** - NOT predict search positions, NOT brute force.

The puzzle creator used SOME method to generate the keys. We want to reverse-engineer that method.
ALL unsolved puzzles are targets - no single puzzle is prioritized.

## EXPLORATION MINDSET - CRITICAL

### Be Curious, Not Judgmental
- **DO NOT declare "no pattern found"** - instead say "haven't found it YET"
- **DO NOT close doors prematurely** - every observation is a clue
- **DO explore freely** - ask "what if?" and test hypotheses
- **DO let the models think deeply** - give them time for reasoning

### Construction Over Analysis
The goal is to **BUILD a ladder generator** that can reproduce the sequence.
- Think like the puzzle creator: "How would I construct this?"
- Test construction hypotheses, not just analyze data
- If we can build it, we can tune it to match

### Key Discovery (2025-12-18)
Mathematical constants are embedded in early values:
- m[4]/m[3] = 22/7 ≈ π
- k[1], k[2], k[4], k[5] are Fibonacci numbers
- m values connect to π, e, and φ convergents
See: `DISCOVERY_PI.md` for full details

## STRICT RULES - READ THIS

### DO NOT:
- **NEVER predict, guess, or hallucinate key values**
- **NEVER claim to have "solved" a puzzle without verification against the database**
- **NEVER invent data** - if a key is unknown, say "UNKNOWN"
- **NEVER output fake "solutions"** like "puzzle 66 = 17" - that's hallucination garbage

### DO:
- **ALWAYS query `db/kh.db`** for known key values
- **ALWAYS verify formulas** against actual database values
- **ALWAYS distinguish** between KNOWN (in DB) and UNKNOWN (not in DB) keys
- **ALWAYS use `puzzle_config.py`** to load data programmatically

### Known Keys in Database
```
k1-k70:  ALL 70 keys are in the database (SOLVED)
k75:     In database (SOLVED)
k80:     In database (SOLVED)
k85:     In database (SOLVED)
k90:     In database (SOLVED)
k71-k74: NOT in database (UNSOLVED)
k76-k79: NOT in database (UNSOLVED)
k81-k84: NOT in database (UNSOLVED)
k86-k89: NOT in database (UNSOLVED)
k91-k160: NOT in database (UNSOLVED)
```

### Quick DB Query
```bash
# Get key by puzzle number
sqlite3 db/kh.db "SELECT puzzle_id, priv_hex FROM keys WHERE puzzle_id=66;"

# Get decimal value (Python)
python3 -c "print(int('0x2832ed74f2b5e35ee', 16))"

# List all known puzzle IDs
sqlite3 db/kh.db "SELECT DISTINCT puzzle_id FROM keys ORDER BY puzzle_id;"
```

If you cannot verify a claim against the database, **DO NOT MAKE THE CLAIM**.

## Data Status

| Category | Count | Source |
|----------|-------|--------|
| Known keys | 74 | DB: k1-k70, k75, k80, k85, k90 |
| Unsolved (targets) | 86 | All remaining puzzles |
| Total puzzles | 160 | Bitcoin Puzzle Challenge |

**Use `puzzle_config.py` for all data access - no hardcoded values.**

## Multi-Agent Architecture

| Agent | Model | Size | Specialization | Status |
|-------|-------|------|----------------|--------|
| A-Solver | qwen3-vl:8b | 6.1GB | Fast analysis, wallet forensics | Certified (10/10) |
| B-Solver | phi4-reasoning:14b | 11GB | Deep reasoning, anomalies | Training (7/12) |
| C-Solver | qwq:32b | 19GB | Formula derivation, deep math reasoning | Oracle Mode |
| Maestro | Claude (Opus) | Cloud | Orchestration, coordination | Active |

## Verified Mathematical Relationships (FROM DATABASE)

```
k5  = k2 × k3       = 3 × 7 = 21
k6  = k3²           = 7² = 49
k7  = k2×9 + k6     = 27 + 49 = 76
k8  = k5×13 - k6    = 273 - 49 = 224
k8  = k4×k3×4       = 8×7×4 = 224 (alternate)
k11 = k6×19 + k8    = 931 + 224 = 1155
k12 = k8×12 - 5     = 2688 - 5 = 2683 (UNIQUE formula!)
k13 = k10×10 + k7   = 5140 + 76 = 5216
k14 = k11×9 + 149   = 10395 + 149 = 10544
k14 = k8×47 + 16    = 10528 + 16 = 10544 (alternate)
k15 = k12×10 + 37   = 26830 + 37 = 26867
k16 = k11×45 - 465  = 51975 - 465 = 51510
k18 = k13×38 + 461  = 198208 + 461 = 198669
```

**WARNING**: Previous findings were WRONG:
- Old: k13=5765 → ACTUAL: k13=5216
- Old: k15 candidates [17024,17295] → ACTUAL: k15=26867
ALWAYS verify against database!

## Position Anomalies (near minimum of range)
- k4: 0.00% (exactly at minimum)
- k10: 0.39%
- k69: 0.72% (solved FAST)

## Prime Keys
- k9 = 467 (prime)
- k12 = 2683 (prime)
These have "unique" formulas because they can't be factored!

## Highly Structured Keys
- k17 = 3⁴ × 7 × 13² = 81 × 7 × 169 = 95823
- k11 = 3 × 5 × 7 × 11 (divisible by all small primes!)

## Keys Divisible by Puzzle Number
- k1, k4, k8, k11, k36 (pattern: 1, 4, 8, 11, 36...)

## EC (Elliptic Curve) Relationships

**Point Addition:**
- k4 = k1 + k3 = 1 + 7 = 8

**Powers of 2:**
- k4 = 2³ × k1 = 8
- k8 = 2⁵ × k3 = 32 × 7 = 224

**Clean EC-style formulas (a×P + b×Q):**
```
k7  = 4×k5 - k4    = 84 - 8 = 76
k8  = 5×k6 - k5    = 245 - 21 = 224
k11 = 5×k3 + 5×k8  = 35 + 1120 = 1155
k12 = 12×k8 - 5×k1 = 2688 - 5 = 2683
k13 = k7 + 10×k10  = 76 + 5140 = 5216
```

**Offsets ARE key values:**
- k7 offset = +k6 (+49)
- k8 offset = -k6 (-49)
- k11 offset = +k8 (+224)
- k13 offset = +k7 (+76)

## Key Files

- `puzzle_config.py` - Central config, loads all data from DB
- `db/kh.db` - Main database with all 74 known keys
- `formula_derivation_result.json` - C-Solver formula analysis
- `prng_reconstruction_result.json` - B-Solver PRNG analysis
- `agent_memory.db` - SQLite database with agent insights (PROJECT ROOT, not db/)
- `MASTER_FINDINGS.json` - Key formulas k5-k14, k15 candidates
- `FINAL_FORMULA_SYNTHESIS.json` - Full formula synthesis with meta-formula

## System Resources

- **Disk**: 3.7T total, 3.0T available (14% used)
- **RAM**: 119GB total, ~78GB available
- **GPU**: NVIDIA (Ollama using GPU acceleration)

## User Context

User was close to solving puzzles 67, 68 and missed 69 when someone else solved it.
The REAL goal is to understand the formula that generates ALL keys.

## Oracle Mode

For deep reasoning tasks, agents run in "Oracle Mode":
- Streaming responses (no timeout)
- Extended thinking time (30+ minutes allowed)
- Full `<think>` block reasoning captured

## Next Steps

1. Use ALL 74 known keys for formula derivation (not just k1-k14)
2. Synthesize findings from B-Solver and C-Solver
3. Test any derived formulas against ALL known keys
4. If formula found, derive ALL unsolved puzzles

## Commands

```bash
# Check data status
python puzzle_config.py

# Check agent memory stats
curl http://localhost:5050/api/oracle/memory/stats

# View oracle interface
# http://localhost:5050/oracle

# Run puzzle CLI
python puzzle_cli.py status
```
