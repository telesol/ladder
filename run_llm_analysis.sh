#!/bin/bash
# Orchestrate sequential LLM analysis tasks (120B model is too large for parallel)

echo "=========================================="
echo "LLM Task Orchestration - Bridge Analysis"
echo "=========================================="
echo ""
echo "Model: gpt-oss:120b-cloud"
echo "Tasks: 4 (running sequentially)"
echo "Output: llm_tasks/results/"
echo ""

# Create results directory
mkdir -p llm_tasks/results

# Check if ollama is available
if ! command -v ollama &> /dev/null; then
    echo "ERROR: ollama not found. Please install ollama first."
    exit 1
fi

# Check if model is available
echo "Checking model availability..."
if ! ollama list | grep -q "gpt-oss:120b-cloud"; then
    echo "WARNING: gpt-oss:120b-cloud not found in ollama list"
    echo "Available models:"
    ollama list
    echo ""
    echo "Continue anyway? (y/n)"
    read -r response
    if [[ "$response" != "y" ]]; then
        exit 1
    fi
fi

echo ""
echo "Starting analysis..."
echo ""

# Task 1
echo "=========================================="
echo "TASK 1/4: Divisibility Pattern Analysis"
echo "=========================================="
cat llm_tasks/task1_divisibility.txt | ollama run gpt-oss:120b-cloud > llm_tasks/results/task1_divisibility_result.txt 2>&1
echo "✓ Task 1 complete"
echo ""

# Task 2
echo "=========================================="
echo "TASK 2/4: M-Value Magnitude Pattern"
echo "=========================================="
cat llm_tasks/task2_m_magnitude.txt | ollama run gpt-oss:120b-cloud > llm_tasks/results/task2_m_magnitude_result.txt 2>&1
echo "✓ Task 2 complete"
echo ""

# Task 3
echo "=========================================="
echo "TASK 3/4: D-Selection Meta-Pattern"
echo "=========================================="
cat llm_tasks/task3_d_selection.txt | ollama run gpt-oss:120b-cloud > llm_tasks/results/task3_d_selection_result.txt 2>&1
echo "✓ Task 3 complete"
echo ""

# Task 4
echo "=========================================="
echo "TASK 4/4: Number Theory Deep Analysis"
echo "=========================================="
cat llm_tasks/task4_number_theory.txt | ollama run gpt-oss:120b-cloud > llm_tasks/results/task4_number_theory_result.txt 2>&1
echo "✓ Task 4 complete"
echo ""

echo "=========================================="
echo "All tasks complete!"
echo "=========================================="
echo ""
echo "Results:"
ls -lh llm_tasks/results/
echo ""
echo "Next: Run 'python3 synthesize_llm_results.py' to analyze findings"
