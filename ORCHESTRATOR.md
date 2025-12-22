# ORCHESTRATOR REFERENCE - READ THIS FIRST

**Last Updated**: 2025-12-22
**Purpose**: Persistent memory for Claude orchestrator sessions

---

## CRITICAL: READ BEFORE DOING ANYTHING

1. Read this file completely before taking action
2. Check MEMORY.md for current research state
3. Check CLAUDE.md for project rules
4. Use monitor scripts to check running tasks

---

## NETWORK TOPOLOGY

```
                    ┌─────────────────────────────────────┐
                    │         WIFI: 192.168.111.x         │
                    └─────────────────────────────────────┘
                              │           │
                    ┌─────────┴───┐   ┌───┴─────────┐
                    │   Box211    │   │   Box212    │
                    │192.168.111. │   │192.168.111. │
                    │    211      │   │    212      │
                    │ deepseek-r1 │   │ mixtral8x22 │
                    │    :70b     │   │     :b      │
                    └─────────────┘   └─────────────┘

    ┌─────────────────────────────────────────────────────┐
    │              HIGH-SPEED: 10.0.0.x (200Gbps)         │
    └─────────────────────────────────────────────────────┘
              │                           │
    ┌─────────┴─────────┐       ┌─────────┴─────────┐
    │      SPARK1       │       │      SPARK2       │
    │    10.0.0.1       │       │    10.0.0.2       │
    │  (THIS MACHINE)   │       │   ssh: spark2     │
    │    qwq:32b        │       │   qwen3:32b       │
    │  phi4-reason:14b  │       │  phi4-reason:14b  │
    │   + cloud models  │       │  nemotron:30b     │
    └───────────────────┘       └───────────────────┘
```

---

## COMPUTE RESOURCES

### Spark1 (LOCAL - 10.0.0.1) - THIS MACHINE
- **Hardware**: NVIDIA GB10 (Jetson), 128GB RAM
- **SSH**: N/A (local)
- **Local Models**:
  - `qwq:32b` (19GB) - Deep reasoning, formula derivation
  - `phi4-reasoning:14b` (11GB) - Reasoning, verification
  - `qwen3-vl:8b` (6.1GB) - Fast analysis
- **Cloud Models**: deepseek-v3.1:671b, qwen3-coder:480b, mistral-large-3:675b, kimi-k2:1t, etc.
- **Best For**: Main orchestration, deep reasoning tasks

### Spark2 (10.0.0.2)
- **Hardware**: Jetson Orin, similar to Spark1
- **SSH**: `ssh spark2`
- **Local Models**:
  - `qwen3:32b` (20GB) - Deep reasoning
  - `nemotron-3-nano:30b` (24GB) - Broad reasoning
  - `devstral:14b` (14GB) - Code tasks
  - `phi4-reasoning:14b` (11GB) - Reasoning
- **Best For**: Parallel deep reasoning, pattern finding

### Box211 (192.168.111.211)
- **Hardware**: GPU workstation
- **SSH**: `ssh box211`
- **Local Models**:
  - `deepseek-r1:70b` (42GB) - BEST for deep math reasoning
  - `devstral-small-2:24b` (15GB) - Code tasks
  - `qwen2.5-coder:7b` (4.7GB) - Fast code
- **Best For**: Heavy mathematical reasoning, long context

### Box212 (192.168.111.212)
- **Hardware**: GPU workstation
- **SSH**: `ssh box212`
- **Local Models**:
  - `mixtral:8x22b` (79GB) - LARGEST, broad knowledge
  - `codellama:70b` (38GB) - Code generation
  - `yi-coder:9b` (17GB) - Code tasks
  - `deepseek-math:7b` (4.9GB) - Fast math
- **Best For**: Synthesis, broad reasoning, large context

---

## SSH COMMANDS

```bash
# Connect to boxes
ssh spark2          # 10.0.0.2
ssh box211          # 192.168.111.211
ssh box212          # 192.168.111.212

# Run model on remote box
ssh box211 "ollama run deepseek-r1:70b 'your prompt'"

# Pipe file to remote model
cat task.txt | ssh box211 "ollama run deepseek-r1:70b"

# Check remote GPU
ssh box211 "nvidia-smi"
ssh box212 "nvidia-smi"
```

---

## PROJECT STRUCTURE

```
/home/solo/LA/                    # Project root
├── ORCHESTRATOR.md               # THIS FILE - read first!
├── CLAUDE.md                     # Project rules and context
├── MEMORY.md                     # Research state and findings
├── db/kh.db                      # SQLite database with 74 known keys
├── data_for_csolver.json         # m_seq, d_seq for n=2..70
├── puzzle_config.py              # Data access utilities
├── N17_*.txt                     # Current investigation tasks
├── n17_results/                  # Task outputs
│   ├── task_a_before_*.txt
│   ├── task_b_breakpoint_*.txt
│   ├── task_c_after_*.txt
│   └── task_d_why17_*.txt
├── monitor_n17.sh                # Monitor running tasks
└── dispatch_n17_tasks.sh         # Dispatch tasks
```

---

## CRITICAL KNOWLEDGE

### The Bitcoin Puzzle
- 160 puzzles total, 74 solved (k1-k70, k75, k80, k85, k90)
- Goal: Find the KEY GENERATION FORMULA, not brute force
- Core formula: `k[n] = 2*k[n-1] + adj[n]`
- Unified: `m[n] = (2^n - adj[n]) / k[d[n]]` (100% verified)

### Current Focus: n=17 Transition
- Sign pattern ++- works 100% for n=2-16
- Pattern BREAKS at n=17
- Understanding this reveals the algorithm

### Key Files to Read
1. `CLAUDE.md` - Project rules (READ FIRST)
2. `MEMORY.md` - Current research state
3. `COMPLETE_FORMULA_SYSTEM.md` - Verified formulas
4. `COORDINATION_NOTE_FOR_OTHER_CLAUDE.md` - Multi-Claude sync

---

## DISPATCH PATTERNS

### Single Task to Box
```bash
# Background task with output capture
nohup ssh box211 "cat /dev/stdin | ollama run deepseek-r1:70b" < task.txt > output.txt 2>&1 &
echo $!  # Save PID
```

### Parallel Tasks (All 4 Boxes)
```bash
# Spark1 (local)
nohup ollama run qwq:32b < task_a.txt > result_a.txt 2>&1 &

# Spark2
nohup ssh spark2 "cat /dev/stdin | ollama run qwen3:32b" < task_b.txt > result_b.txt 2>&1 &

# Box211
nohup ssh box211 "cat /dev/stdin | ollama run deepseek-r1:70b" < task_c.txt > result_c.txt 2>&1 &

# Box212
nohup ssh box212 "cat /dev/stdin | ollama run mixtral:8x22b" < task_d.txt > result_d.txt 2>&1 &
```

### Monitor Running Tasks
```bash
# Check process status
ps aux | grep ollama

# Check output sizes
ls -lh *.txt

# Tail specific output
tail -f result_a.txt
```

---

## MODEL SELECTION GUIDE

| Task Type | Best Model | Box |
|-----------|------------|-----|
| Deep math reasoning | deepseek-r1:70b | Box211 |
| Formula derivation | qwq:32b | Spark1 |
| Pattern finding | qwen3:32b | Spark2 |
| Broad synthesis | mixtral:8x22b | Box212 |
| Code generation | codellama:70b | Box212 |
| Fast verification | phi4-reasoning:14b | Any |
| Quick analysis | qwen3-vl:8b | Spark1/2 |

---

## CURRENT TASK STATUS

### N17 Investigation (2025-12-22)
- **Task A** (Before n=17): Spark2/qwen3:32b - RUNNING
- **Task B** (Breakpoint): Spark1/qwq:32b - RUNNING
- **Task C** (After n=17): Box211/devstral:24b - RUNNING
- **Task D** (Why 17?): Box212/mixtral:8x22b - RUNNING

Monitor: `/home/solo/LA/monitor_n17.sh`

---

## GIT WORKFLOW

```bash
# Always pull before starting
git pull

# Commit findings
git add -A
git commit -m "Description"
git push

# If conflict
git stash && git pull --rebase && git stash pop
```

---

## BACKUP/NAS

(To be configured - currently no NAS mounted)

Local backup: `/home/solo/LA/` on 3.7TB NVMe (3.0TB free)

---

## TROUBLESHOOTING

### Box not responding
```bash
ping 192.168.111.211  # Check connectivity
ssh box211 "hostname"  # Check SSH
ssh box211 "ollama ps" # Check Ollama
```

### Model not loading
```bash
ssh box211 "ollama pull deepseek-r1:70b"  # Re-pull model
ssh box211 "systemctl restart ollama"      # Restart service
```

### Task stuck
```bash
ps aux | grep ollama  # Find PID
kill <PID>            # Kill stuck process
```

---

## REMEMBER

1. **DON'T ASSUME** - Always verify connectivity and model availability
2. **READ FIRST** - Check CLAUDE.md, MEMORY.md, this file before acting
3. **TRACK TASKS** - Use TodoWrite for complex multi-step work
4. **PUSH OFTEN** - Commit findings to git for other Claude instances
5. **MONITOR** - Check running tasks before dispatching new ones

---

*This file is the orchestrator's persistent memory. Update it when infrastructure changes.*
