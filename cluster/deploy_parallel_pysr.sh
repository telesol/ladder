#!/bin/bash
# Deploy parallel PySR jobs to 4-box cluster
# Orchestrator: Claude (Sonnet 4.5)

echo "================================================================================"
echo "DEPLOYING PARALLEL PySR TO 4-BOX CLUSTER"
echo "================================================================================"
echo "Start time: $(date)"
echo ""

# Box configuration
BOXES=("box211" "box212" "box213" "box214")
SCRIPTS=("box211_c_n_discovery.py" "box212_d_gap_discovery.py" "box213_adj_pattern_discovery.py" "box214_seed_discovery.py")
TARGETS=("c[n] oscillation" "d_gap linear" "adj[n] pattern" "seed constants")

# Create outputs directory
mkdir -p outputs
mkdir -p cluster/logs

echo "📦 Preparing data for deployment..."
echo "   - data/clean/PHASE1_FEATURES_COMPLETE.json"
echo "   - 4 specialized PySR scripts"
echo ""

# Function to deploy to a box
deploy_to_box() {
    local box=$1
    local script=$2
    local target=$3
    local idx=$4

    echo "[$box] Deploying for: $target"

    # Create remote directory
    ssh $box "mkdir -p ~/LA/cluster ~/LA/data/clean ~/LA/outputs" 2>/dev/null

    # Copy data
    scp -q data/clean/PHASE1_FEATURES_COMPLETE.json $box:~/LA/data/clean/ 2>/dev/null

    # Copy script
    scp -q cluster/$script $box:~/LA/cluster/ 2>/dev/null

    # Make executable
    ssh $box "chmod +x ~/LA/cluster/$script" 2>/dev/null

    echo "[$box] ✅ Deployed"
}

# Deploy to all boxes in parallel
echo "🚀 Deploying to all boxes..."
for i in "${!BOXES[@]}"; do
    deploy_to_box "${BOXES[$i]}" "${SCRIPTS[$i]}" "${TARGETS[$i]}" "$i" &
done
wait

echo ""
echo "✅ All deployments complete!"
echo ""
echo "================================================================================"
echo "LAUNCHING PARALLEL PySR JOBS"
echo "================================================================================"
echo ""

# Launch function
launch_on_box() {
    local box=$1
    local script=$2
    local target=$3

    echo "[$box] Launching: $target"

    # Launch in background, redirect to log
    ssh $box "cd ~/LA && nohup python3 cluster/$script > cluster/logs/${box}_output.log 2>&1 &" 2>/dev/null

    # Get PID
    sleep 1
    pid=$(ssh $box "pgrep -f $script" 2>/dev/null)

    if [ -n "$pid" ]; then
        echo "[$box] ✅ Running (PID: $pid)"
    else
        echo "[$box] ❌ Failed to start"
    fi
}

# Launch all jobs
for i in "${!BOXES[@]}"; do
    launch_on_box "${BOXES[$i]}" "${SCRIPTS[$i]}" "${TARGETS[$i]}"
done

echo ""
echo "================================================================================"
echo "ALL JOBS LAUNCHED"
echo "================================================================================"
echo ""
echo "📊 Monitor progress:"
for box in "${BOXES[@]}"; do
    echo "   ssh $box 'tail -f ~/LA/cluster/logs/${box}_output.log'"
done

echo ""
echo "📥 Collect results (after completion):"
echo "   ./cluster/collect_results.sh"
echo ""
echo "⏱️  Expected runtime: 30-60 minutes per box"
echo "   Jobs run in parallel, total time ~60 min"
echo ""
echo "End deployment: $(date)"
