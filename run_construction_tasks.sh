#!/bin/bash
# Orchestrate Tasks 7-10 for k-sequence construction exploration

echo "================================================"
echo "LLM CONSTRUCTION EXPLORATION - Tasks 7-10"
echo "================================================"
echo ""
echo "Starting 4 LLM tasks in parallel..."
echo ""

# Task 7: Construction Strategy (gpt-oss:120b-cloud)
echo "Starting Task 7: K-Sequence Construction Strategy (gpt-oss:120b-cloud)..."
nohup bash -c "cat llm_tasks/task7_construction_strategy.txt | ollama run gpt-oss:120b-cloud > llm_tasks/results/task7_construction_result.txt 2>&1" > /dev/null 2>&1 &
PID7=$!
echo "  Task 7 started (PID: $PID7)"

# Task 8: M-Value Generation (nemotron:30b-cloud)
echo "Starting Task 8: M-Value Generation Method (nemotron-3-nano:30b-cloud)..."
nohup bash -c "cat llm_tasks/task8_m_value_generation.txt | ollama run nemotron-3-nano:30b-cloud > llm_tasks/results/task8_m_value_result.txt 2>&1" > /dev/null 2>&1 &
PID8=$!
echo "  Task 8 started (PID: $PID8)"

# Task 9: D-Selection Algorithm (gpt-oss:120b-cloud)
echo "Starting Task 9: D-Selection Algorithm (gpt-oss:120b-cloud)..."
nohup bash -c "cat llm_tasks/task9_d_selection_algorithm.txt | ollama run gpt-oss:120b-cloud > llm_tasks/results/task9_d_selection_result.txt 2>&1" > /dev/null 2>&1 &
PID9=$!
echo "  Task 9 started (PID: $PID9)"

# Task 10: Bridge Prediction (nemotron:30b-cloud)
echo "Starting Task 10: Bridge Prediction Mechanism (nemotron-3-nano:30b-cloud)..."
nohup bash -c "cat llm_tasks/task10_bridge_prediction.txt | ollama run nemotron-3-nano:30b-cloud > llm_tasks/results/task10_bridge_prediction_result.txt 2>&1" > /dev/null 2>&1 &
PID10=$!
echo "  Task 10 started (PID: $PID10)"

echo ""
echo "All tasks started!"
echo ""
echo "Monitor progress:"
echo "  Task 7: tail -f llm_tasks/results/task7_construction_result.txt"
echo "  Task 8: tail -f llm_tasks/results/task8_m_value_result.txt"
echo "  Task 9: tail -f llm_tasks/results/task9_d_selection_result.txt"
echo "  Task 10: tail -f llm_tasks/results/task10_bridge_prediction_result.txt"
echo ""
echo "Check status:"
echo "  ps aux | grep -E '($PID7|$PID8|$PID9|$PID10)'"
echo ""
echo "Expected runtime: 20-40 minutes per task"
echo ""
echo "PIDs saved to: llm_tasks/construction_pids.txt"
echo "$PID7" > llm_tasks/construction_pids.txt
echo "$PID8" >> llm_tasks/construction_pids.txt
echo "$PID9" >> llm_tasks/construction_pids.txt
echo "$PID10" >> llm_tasks/construction_pids.txt
