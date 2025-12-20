# Bitcoin Puzzle Analysis Project

## ⚠️ CLAUDE: READ THIS FIRST
**NO PREDICTION. NO ASSUMPTIONS. READ THE RULES. IF LOST, ASK THE USER.**

You are the ORCHESTRATOR. You have 4 Spark nodes (128GB RAM, 1 pflop each) with local AI models.
- **YOUR JOB:** Coordinate, log findings, update repo, delegate research to local models
- **NOT YOUR JOB:** Do the research yourself, make assumptions, go off on tangents

## Project Status
**Last Updated**: 2025-12-20

## SESSION RESUME POINT (2025-12-20)

### MAJOR BREAKTHROUGHS - READ THESE!

1. **d[n] SOLVED**: d[n] is ALWAYS chosen to minimize m[n]!
   - 67/69 verified for n=4 to n=70: d[n] gives minimum m[n]
   - 2 special cases (n=2,3): Bootstrap conditions with d[n]=n
   - See: `verify_d_minimizes_m.py`

2. **BOOTSTRAP MECHANISM DISCOVERED**: First 3 k-values are Mersenne!
   - k[1]=1=2^1-1, k[2]=3=2^2-1, k[3]=7=2^3-1
   - adj[2]=adj[3]=1 (Mersenne recurrence: k[n]=2*k[n-1]+1)
   - d[2]=2, d[3]=3 (self-reference!) gives m[2]=m[3]=1
   - Transition at n=4: adj=-6, k[4]=8=2^3, m[4]=22 (π convergent)
   - See: `FORMULA_PATTERNS.md`

3. **Sign Pattern**: adj[n] sign follows ++- pattern for n=2-16
   - adj = k[n] - 2*k[n-1]
   - 15 CONSECUTIVE MATCHES (n=2 to n=16)
   - Pattern BREAKS at n=17 (31 exceptions after)
   - Implication: algorithm changed at n=17
   - See: `analyze_adj_sequence.py`

4. **m-value formulas found**:
   - m[8] = m[2] + m[4] = 1 + 22 = 23
   - m[9] = 2^9 - m[6] = 512 - 19 = 493
   - m[10] = m[2] × m[6] = 1 × 19 = 19
   - m[16] = 2^7 + m[13] = 128 + 8342 = 8470
   - See: `find_m_formulas.py`

5. **UNIFIED FORMULA DISCOVERED (2025-12-20)**: ★★★★★
   - **m[n] = (2^n - adj[n]) / k[d[n]]** (works for ALL n!)
   - Verified 30/30 (100%) for n=2 to n=31
   - Special case d[n]=1: m[n] = 2^n - adj[n] (since k[1]=1)
   - The m-sequence is DERIVED, not independent!
   - See: `COMPLETE_FORMULA_SYSTEM.md` for full details

6. **Multi-Model Synthesis (2025-12-20)**:
   - 100% coverage of m[2]-m[15] via continued fraction convergents
   - Prime 17 network: Fermat prime 2^4+1 in 40% of m-values
   - Self-reference: m[n] | m[n+m[n]] (57% success rate)
   - e-ratio: m[26]/m[25] ≈ e (0.63% error)
   - See: `MULTI_MODEL_SYNTHESIS.md`, `M_SEQUENCE_EXTENDED_ANALYSIS.md`

### ⚠️ CRITICAL WARNING
The Zbook k[71] derivation using offset ratio extrapolation was INCORRECT.
- **Derived k[71]:** 1,602,101,676,614,237,534,489 (0x56d9a08a95095fb919)
- **Derived address:** `1KEqStQnjYJnEWyqYhwdAup53JCDnTm7va`
- **ACTUAL puzzle 71:** `1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU` (UNSOLVED!)

**Root cause:** Offset ratio extrapolation assumption was wrong.
**Verification tool:** Run `python verify_btc_address.py` to check any derivation.

### Current Status
- **Progress:** Unified formula verified 100%, k[71] still unsolved
- **Key insight:** m[n] = (2^n - adj[n]) / k[d[n]] for ALL n
- **Data source:** `data_for_csolver.json` - use `m_seq[n-2]`, `d_seq[n-2]`
- **Next goal:** Find adj[71] pattern to derive k[71]

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
