#!/bin/bash
# SOURCE MATH EXPLORATION - Fundamental Structure Discovery
# Date: 2025-12-21
# Mission: Discover WHAT the ladder IS, not how to predict individual values

echo "========================================================================"
echo "SOURCE MATH EXPLORATION - Fundamental Structure Discovery"
echo "========================================================================"
echo ""
echo "READ: SOURCE_MATH_DIRECTIVE.md for mission understanding"
echo ""
echo "Mission: Discover the MATHEMATICAL OBJECT that IS the ladder"
echo "NOT: Predict individual k-values or fit curves to data"
echo ""
echo "========================================================================"
echo ""

# Create output directory
mkdir -p llm_tasks/source_math/results

# Task A: Period-5 Structure Analysis (gpt-oss:120b-cloud - best for deep mathematical reasoning)
echo "Starting Task A: Period-5 Structure Analysis (gpt-oss:120b-cloud)..."
nohup bash -c "cat llm_tasks/source_math/task_period5_structure.txt | ollama run gpt-oss:120b-cloud > llm_tasks/source_math/results/period5_analysis.txt 2>&1" > /dev/null 2>&1 &
PID_A=$!
echo "  Task A started (PID: $PID_A)"
echo ""

# Task B: Algebraic Structure Discovery (deepseek-r1:671b-cloud - excellent for abstract algebra)
echo "Starting Task B: Algebraic Structure Discovery (deepseek-r1:671b-cloud)..."
nohup bash -c "cat llm_tasks/source_math/task_algebraic_structure.txt | ollama run deepseek-r1:671b-cloud > llm_tasks/source_math/results/algebraic_structure.txt 2>&1" > /dev/null 2>&1 &
PID_B=$!
echo "  Task B started (PID: $PID_B)"
echo ""

# Save PIDs
echo "$PID_A" > llm_tasks/source_math/source_math_pids.txt
echo "$PID_B" >> llm_tasks/source_math/source_math_pids.txt

echo "========================================================================"
echo "All SOURCE MATH tasks started!"
echo "========================================================================"
echo ""
echo "Monitor progress:"
echo "  Task A (Period-5): tail -f llm_tasks/source_math/results/period5_analysis.txt"
echo "  Task B (Algebraic): tail -f llm_tasks/source_math/results/algebraic_structure.txt"
echo ""
echo "Expected runtime: 30-60 minutes per task (deep reasoning required)"
echo ""
echo "These are NOT prediction tasks. These are DISCOVERY tasks."
echo "The LLMs are looking for the FUNDAMENTAL MATHEMATICAL STRUCTURE."
echo ""
echo "========================================================================"
echo ""
