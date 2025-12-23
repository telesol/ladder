#!/bin/bash
# Collect PySR results from 4-box cluster
# Orchestrator: Claude (Sonnet 4.5)

echo "================================================================================"
echo "COLLECTING PySR RESULTS FROM CLUSTER"
echo "================================================================================"
echo "Start time: $(date)"
echo ""

BOXES=("box211" "box212" "box213" "box214")
TARGETS=("c_n" "d_gap" "adj" "seed")

mkdir -p outputs/cluster_results
mkdir -p cluster/logs

echo "📥 Fetching results from all boxes..."
echo ""

for i in "${!BOXES[@]}"; do
    box="${BOXES[$i]}"
    target="${TARGETS[$i]}"

    echo "[$box] Collecting $target results..."

    # Fetch hall of fame CSV
    scp -q $box:~/LA/outputs/box*_${target}_hall_of_fame.csv outputs/cluster_results/ 2>/dev/null

    # Fetch model pickle
    scp -q $box:~/LA/outputs/box*_${target}_model.pkl outputs/cluster_results/ 2>/dev/null

    # Fetch log
    scp -q $box:~/LA/cluster/logs/${box}_output.log cluster/logs/ 2>/dev/null

    if [ -f "outputs/cluster_results/box*_${target}_hall_of_fame.csv" ]; then
        equations=$(wc -l < outputs/cluster_results/box*_${target}_hall_of_fame.csv 2>/dev/null || echo "0")
        echo "[$box] ✅ $equations equations"
    else
        echo "[$box] ⚠️  No results yet"
    fi
done

echo ""
echo "================================================================================"
echo "RESULTS SUMMARY"
echo "================================================================================"
echo ""

# Count total equations
total=0
for target in "${TARGETS[@]}"; do
    count=$(wc -l < outputs/cluster_results/box*_${target}_hall_of_fame.csv 2>/dev/null || echo "0")
    if [ "$count" -gt 0 ]; then
        echo "  $target: $count equations"
        total=$((total + count))
    fi
done

echo ""
echo "  Total: $total equations discovered"
echo ""
echo "📁 Results saved to:"
echo "   outputs/cluster_results/"
echo "   cluster/logs/"
echo ""
echo "🔍 Next: Analyze with Deliberation Chamber"
echo ""
echo "End collection: $(date)"
