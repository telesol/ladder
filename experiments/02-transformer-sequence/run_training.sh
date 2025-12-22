#!/bin/bash
# Quick training script

set -e

echo "=========================================="
echo "Transformer Training for Bitcoin Puzzles"
echo "=========================================="
echo ""
echo "Baseline: PySR formula (100% proven)"
echo "Goal: Neural network learns same pattern"
echo ""

# Phase 1: Quick test (10 epochs)
echo "Phase 1: Quick test (10 epochs, ~5 min)"
echo "------------------------------------------"
python3 scripts/train_transformer.py \
  --epochs 10 \
  --batch-size 8 \
  --lr 0.001 \
  --hidden-size 128 \
  --device cpu

echo ""
echo "Quick test complete!"
echo ""
read -p "Continue with full training (100 epochs)? [y/N] " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "Phase 2: Full training (100 epochs, ~2-3 hours)"
    echo "------------------------------------------------"
    python3 scripts/train_transformer.py \
      --epochs 100 \
      --batch-size 8 \
      --lr 0.001 \
      --hidden-size 128 \
      --device cpu
    
    echo ""
    echo "=========================================="
    echo "Training complete!"
    echo "=========================================="
    echo ""
    echo "Results saved to: models/best_model.pth"
    echo "Training history: results/training_history.json"
fi
