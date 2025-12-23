#!/bin/bash
# Launch 4 PySR jobs in parallel on LOCAL machine
# Orchestrator: Claude (Sonnet 4.5)

echo "================================================================================"
echo "LAUNCHING 4 PARALLEL PySR JOBS (LOCAL)"
echo "================================================================================"
echo "Start time: $(date)"
echo ""

# Set Julia path
export PATH="$HOME/.juliaup/bin:$PATH"

# Create output directories
mkdir -p outputs/local_parallel
mkdir -p cluster/logs

echo "🚀 Starting 4 PySR discoveries in parallel..."
echo ""

# Launch Box 211: c[n] discovery
echo "[1/4] Launching c[n] oscillation discovery..."
nohup python3 cluster/box211_c_n_discovery.py > cluster/logs/box211_local.log 2>&1 &
PID211=$!
echo "      PID: $PID211"

# Launch Box 212: d_gap discovery
echo "[2/4] Launching d_gap linear discovery..."
nohup python3 cluster/box212_d_gap_discovery.py > cluster/logs/box212_local.log 2>&1 &
PID212=$!
echo "      PID: $PID212"

# Launch Box 213: adj[n] discovery
echo "[3/4] Launching adj[n] pattern discovery..."
nohup python3 cluster/box213_adj_pattern_discovery.py > cluster/logs/box213_local.log 2>&1 &
PID213=$!
echo "      PID: $PID213"

# Launch Box 214: seed discovery
echo "[4/4] Launching seed constants discovery..."
nohup python3 cluster/box214_seed_discovery.py > cluster/logs/box214_local.log 2>&1 &
PID214=$!
echo "      PID: $PID214"

echo ""
echo "================================================================================"
echo "ALL 4 JOBS RUNNING IN PARALLEL"
echo "================================================================================"
echo ""
echo "PIDs: $PID211, $PID212, $PID213, $PID214"
echo ""
echo "📊 Monitor progress:"
echo "   tail -f cluster/logs/box211_local.log  # c[n] oscillation"
echo "   tail -f cluster/logs/box212_local.log  # d_gap linear"
echo "   tail -f cluster/logs/box213_local.log  # adj[n] pattern"
echo "   tail -f cluster/logs/box214_local.log  # seed constants"
echo ""
echo "📈 Check running jobs:"
echo "   ps aux | grep python3 | grep cluster"
echo ""
echo "⏹️  Stop all jobs:"
echo "   kill $PID211 $PID212 $PID213 $PID214"
echo ""
echo "⏱️  Expected runtime: ~60 minutes (all 4 complete together)"
echo ""
echo "End launch: $(date)"
