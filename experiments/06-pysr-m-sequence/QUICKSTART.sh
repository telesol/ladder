#!/bin/bash
# Quick Start: Run PySR m-sequence discovery experiment

echo "=========================================="
echo "PySR m-sequence Discovery - Quick Start"
echo "=========================================="

# Check if we're in the right directory
if [ ! -f "convergent_database.py" ]; then
    echo "ERROR: Run this script from experiments/06-pysr-m-sequence/"
    exit 1
fi

# Step 1: Check dependencies
echo ""
echo "Step 1: Checking dependencies..."
python3 -c "import pandas" 2>/dev/null && echo "  ✓ pandas installed" || echo "  ✗ pandas missing (pip install pandas)"
python3 -c "import numpy" 2>/dev/null && echo "  ✓ numpy installed" || echo "  ✗ numpy missing (pip install numpy)"
python3 -c "import pysr" 2>/dev/null && echo "  ✓ pysr installed" || echo "  ✗ pysr missing (pip install pysr)"

# Step 2: Prepare features
echo ""
echo "Step 2: Preparing convergent features..."
echo "STATUS: BUILDING" > STATUS.txt
python3 prepare_convergent_features.py

if [ ! -f "feature_matrix.csv" ]; then
    echo "ERROR: Feature preparation failed"
    exit 1
fi

echo "  ✓ Features prepared (feature_matrix.csv created)"

# Step 3: Check if user wants to proceed
echo ""
echo "Step 3: Ready to train PySR"
echo "  Training will take 2-4 hours"
echo "  Press Enter to start training, or Ctrl+C to cancel"
read

# Step 4: Train PySR
echo ""
echo "Step 4: Training PySR (this will take a while)..."
echo "STATUS: TRAINING" > STATUS.txt
echo "Started: $(date)" >> STATUS.txt

python3 train_m_sequence.py

# Step 5: Show results
echo ""
echo "=========================================="
echo "Training Complete!"
echo "=========================================="

if [ -f "training_results.json" ]; then
    echo ""
    echo "Results:"
    cat training_results.json | python3 -m json.tool | grep -E "(accuracy_percent|best_equation)" | head -10

    echo ""
    echo "Status:"
    cat STATUS.txt

    echo ""
    echo "Next steps:"
    echo "  - Review training_results.json for detailed results"
    echo "  - Check pysr_equations.csv for all discovered formulas"
    echo "  - If accuracy ≥ 90%, run generate_full_sequence.py"
else
    echo "ERROR: Training did not produce results file"
fi
