#!/bin/bash
# Cluster Health Check - Dual Spark Setup

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║           LADDER CLUSTER HEALTH CHECK                        ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Spark 1 (local)
echo "┌─ SPARK 1 (10.0.0.1) - Primary ─────────────────────────────┐"
echo "│ Ollama models:"
ollama list 2>/dev/null | grep -E "NAME|qwq|phi4|qwen" | sed 's/^/│   /'
echo "│"
echo "│ Running:"
ollama ps 2>/dev/null | sed 's/^/│   /'
echo "│"
echo "│ GPU:"
nvidia-smi --query-gpu=name,memory.used,memory.total --format=csv,noheader 2>/dev/null | sed 's/^/│   /' || echo "│   No GPU info"
echo "└───────────────────────────────────────────────────────────────┘"
echo ""

# Spark 2 (remote)
echo "┌─ SPARK 2 (10.0.0.2) - Secondary ───────────────────────────┐"
if ping -c 1 -W 1 10.0.0.2 &>/dev/null; then
    echo "│ Status: ONLINE ($(ping -c 1 10.0.0.2 2>/dev/null | grep time= | sed 's/.*time=//' | sed 's/ ms/ms/'))"
    echo "│"
    echo "│ Ollama models:"
    ssh -o ConnectTimeout=5 spark2 "ollama list 2>/dev/null" | grep -E "NAME|qwq|phi4|qwen" | sed 's/^/│   /'
    echo "│"
    echo "│ Running:"
    ssh -o ConnectTimeout=5 spark2 "ollama ps 2>/dev/null" | sed 's/^/│   /'
    echo "│"
    echo "│ GPU:"
    ssh -o ConnectTimeout=5 spark2 "nvidia-smi --query-gpu=name,memory.used,memory.total --format=csv,noheader 2>/dev/null" | sed 's/^/│   /' || echo "│   No GPU info"
else
    echo "│ Status: OFFLINE"
fi
echo "└───────────────────────────────────────────────────────────────┘"
echo ""

# Summary
echo "┌─ CLUSTER SUMMARY ──────────────────────────────────────────┐"
echo "│ Spark 1: C-Solver (qwq:32b), B-Solver (phi4-reasoning:14b)"
echo "│ Spark 2: A-Solver (qwen3-vl:8b)"
echo "│ Link: 200Gbps / <1ms latency"
echo "│ Repo: github.com/telesol/ladder"
echo "└───────────────────────────────────────────────────────────────┘"
