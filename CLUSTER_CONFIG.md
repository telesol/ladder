# Dual-Spark Cluster Configuration

## Network Topology
```
┌─────────────────┐     200Gbps      ┌─────────────────┐
│    SPARK 1      │◄────────────────►│    SPARK 2      │
│   10.0.0.1      │    enP2p1s0f0    │   10.0.0.2      │
│                 │     <1ms RTT     │                 │
│  Primary/Coord  │                  │  Secondary/Work │
└─────────────────┘                  └─────────────────┘
```

## GitHub Repository
**Repo**: https://github.com/telesol/ladder
**Branch**: main

## Role Assignment

### Box 1 (Maestro + C-Solver)
- **Role**: Coordination, deep reasoning
- **Models**:
  - qwq:32b (C-Solver) - Formula derivation
  - phi4-reasoning:14b (B-Solver) - Verification
- **Services**:
  - Oracle API (port 5050)
  - Agent orchestration
  - Git repository (primary)

### Box 2 (A-Solver + Workers)
- **Role**: Parallel computation, fast search
- **Models**:
  - qwen3-vl:8b (A-Solver) - Fast analysis
  - Additional workers for parallel tasks
- **Services**:
  - Ollama API (port 11434)
  - Worker pool for batch processing

## Setup Commands

### Box 1 (already configured)
```bash
# Verify Ollama
ollama list
systemctl status ollama

# Verify Oracle API
curl http://localhost:5050/api/oracle/status
```

### Box 2 (needs setup)
```bash
# SSH setup (run on Box 1)
ssh-keygen -t ed25519 -f ~/.ssh/box2_key
ssh-copy-id -i ~/.ssh/box2_key solo@10.0.0.2

# Test connection
ssh solo@10.0.0.2 "echo 'Box 2 connected'"

# Install Ollama on Box 2
ssh solo@10.0.0.2 "curl -fsSL https://ollama.com/install.sh | sh"

# Pull models on Box 2
ssh solo@10.0.0.2 "ollama pull qwen3-vl:8b"
```

## Load Balancing Strategy

### Task Distribution
```python
# Pseudo-code for task routing
def route_task(task):
    if task.type == "deep_reasoning":
        return BOX1  # C-Solver (qwq:32b)
    elif task.type == "fast_search":
        return BOX2  # A-Solver (qwen3-vl:8b)
    elif task.type == "parallel_batch":
        return BOTH  # Distribute across both
    else:
        return BOX1  # Default to primary
```

### API Endpoints
| Service | Box 1 | Box 2 |
|---------|-------|-------|
| Ollama API | http://10.0.0.1:11434 | http://10.0.0.2:11434 |
| Oracle API | http://10.0.0.1:5050 | - |
| SSH | - | solo@10.0.0.2 |

## Sync Protocol

### Database Sync
```bash
# Sync kh.db to Box 2 (read-only replica)
rsync -avz db/kh.db solo@10.0.0.2:~/LA/db/

# Sync agent memory
rsync -avz agent_memory.db solo@10.0.0.2:~/LA/
```

### Git Sync
```bash
# On Box 1: Push changes
git add -A && git commit -m "sync" && git push

# On Box 2: Pull changes
git pull origin main
```

## Monitoring

### Health Check Script
```bash
#!/bin/bash
# cluster_health.sh

echo "=== Box 1 (local) ==="
ollama ps
curl -s http://localhost:5050/api/oracle/status | jq '.ollama_connected'

echo "=== Box 2 (10.0.0.2) ==="
ssh solo@10.0.0.2 "ollama ps" 2>/dev/null || echo "Box 2 unreachable"
```

## Performance Targets
- Inter-box latency: <1ms
- Throughput: 200Gbps (25GB/s)
- Model load time: <30s
- Task queue depth: 10 per box
