# Ladder Agents (LA)

24/7 Autonomous Bitcoin Puzzle Discovery System

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     CLAUDE ORCHESTRATOR (API)                           │
│  - Task planning & decomposition                                         │
│  - Result validation & synthesis                                         │
│  - Human interface                                                       │
└─────────────────────────┬───────────────────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ MATH AGENT      │ │ VERIFICATION    │ │ DISCOVERY       │
│ (Ollama Cloud)  │ │ AGENT           │ │ AGENT           │
│                 │ │ (Ollama Cloud)  │ │ (Ollama Cloud)  │
│ - Affine calc   │ │ - BTC address   │ │ - Pattern search│
│ - Drift compute │ │ - Signature     │ │ - Hypothesis    │
│ - Lane analysis │ │ - Full crypto   │ │ - New approaches│
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                   │                   │
         └───────────────────┼───────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        LOCAL RAG LAYER                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                   │
│  │ kh.db        │  │ memory.db    │  │ Vector Store │                   │
│  │ (puzzles,    │  │ (discoveries,│  │ (embeddings  │                   │
│  │  calibration)│  │  learnings)  │  │  for search) │                   │
│  └──────────────┘  └──────────────┘  └──────────────┘                   │
└─────────────────────────────────────────────────────────────────────────┘
```

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set API keys
export ANTHROPIC_API_KEY="your-key"
export OLLAMA_API_KEY="your-key"

# Index training data for RAG
python main.py rag-index

# Run single goal
python main.py goal -g "Analyze lane 0 patterns"

# Start 24/7 daemon
python main.py daemon
```

## Directory Structure

```
LA/
├── agents/              # AI agents
│   ├── base_agent.py    # Base class for all agents
│   ├── math_agent.py    # Affine recurrence calculations
│   ├── verification_agent.py  # Bitcoin crypto validation
│   ├── discovery_agent.py     # Pattern discovery
│   └── orchestrator.py  # Claude orchestrator
├── config/
│   └── config.yaml      # Configuration
├── data/
│   ├── btc_puzzle_1_160_full.csv  # Puzzle data
│   ├── training_data.json         # Training examples
│   └── calibration/     # Calibration JSON files
├── db/
│   ├── kh.db           # Puzzle database
│   └── memory.db       # Discoveries & learnings
├── logs/               # Daemon logs
├── models/             # Local model weights (if any)
├── rag/
│   ├── vector_store.py # Vector store for RAG
│   └── vectors/        # FAISS index
├── scripts/            # Utility scripts
├── sync/
│   ├── nas_sync.py     # NAS synchronization
│   └── mnt/            # NAS mount point
├── daemon.py           # 24/7 daemon
├── main.py             # Entry point
└── requirements.txt    # Dependencies
```

## NAS Sync

Sync to Boyz-NAS (QNAP) at 192.168.111.232:

```bash
# Set credentials
export NAS_USER="admin"
export NAS_PASS="yourpassword"

# Check status
python main.py nas-status

# Manual sync
python main.py nas-sync

# Run sync daemon (in background)
python sync/nas_sync.py daemon &
```

## Core Principles

1. **NO STUBS** - Always compute full mathematical values
2. **NO HARDCODING** - Derive everything from the model
3. **VERIFY EVERYTHING** - Use cryptographic proofs
4. **PURE MATH** - Show all steps, no shortcuts
5. **DATA LOCAL** - All data stays on local machine + NAS

## Mathematical Model

Each lane follows affine recurrence:
```
y = A[l] * x + C[k][l][occ] (mod 256)
```

Where:
- `l` = lane (0-15)
- `k` = block index
- `occ` = occurrence within block
- `A[l]` = multiplier for lane
- `C[k][l][occ]` = drift constant
