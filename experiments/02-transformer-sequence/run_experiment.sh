#!/bin/bash
# Master script for running transformer experiments

set -e

cd "$(dirname "$0")"

# Activate 02-train environment
if [ -f "02-train/bin/activate" ]; then
    source 02-train/bin/activate
    echo "✅ Using environment: 02-train"
elif [ -f "../../.venv/bin/activate" ]; then
    source ../../.venv/bin/activate
    echo "✅ Using environment: ../../.venv"
else
    echo "⚠️  No virtual environment found. Using system Python."
fi
echo ""

echo "=========================================="
echo "Transformer Training Experiment Manager"
echo "=========================================="
echo ""

# Default configurations
RUN_NAME="${1:-baseline}"
EPOCHS="${2:-100}"
HIDDEN_SIZE="${3:-128}"

# Auto-detect GPU
if command -v nvidia-smi &> /dev/null && nvidia-smi &> /dev/null; then
    DEVICE="cuda"
    echo "🎮 GPU detected! Using CUDA"
else
    DEVICE="cpu"
    echo "💻 No GPU detected. Using CPU"
fi

echo "📋 Configuration:"
echo "   Run name: $RUN_NAME"
echo "   Epochs: $EPOCHS"
echo "   Hidden size: $HIDDEN_SIZE"
echo ""

# Step 1: Create run directory
echo "Step 1: Creating run directory..."
python3 scripts/create_run.py \
  --name "$RUN_NAME" \
  --epochs "$EPOCHS" \
  --hidden-size "$HIDDEN_SIZE" \
  --batch-size 8 \
  --lr 0.001 \
  --device cpu

# Get the run directory name
RUN_DIR=$(ls -td runs/run_* | head -1)

echo ""
echo "✅ Run directory created: $RUN_DIR"
echo ""

# Step 2: Quick test (10 epochs)
echo "=========================================="
echo "Step 2: Quick Test (10 epochs, ~5 min)"
echo "=========================================="
echo ""

python3 scripts/train_transformer.py \
  --run-dir "$RUN_DIR" \
  --epochs 10 \
  --batch-size 8 \
  --lr 0.001 \
  --hidden-size "$HIDDEN_SIZE" \
  --device "$DEVICE"

echo ""
echo "Quick test complete! Results:"
cat "$RUN_DIR/logs/final_results.json" | python3 -c "import sys, json; d=json.load(sys.stdin); print(f\"   Validation accuracy: {d['best_val_acc']:.2f}%\")"
echo ""

read -p "Continue with full training ($EPOCHS epochs)? [y/N] " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo ""
    echo "=========================================="
    echo "Step 3: Full Training ($EPOCHS epochs)"
    echo "=========================================="
    echo ""
    echo "⏰ Estimated time: 2-3 hours (CPU)"
    echo "   You can monitor progress in another terminal:"
    echo "   tail -f $RUN_DIR/logs/training.log"
    echo ""

    # Run full training (with larger batch size if GPU)
    if [ "$DEVICE" = "cuda" ]; then
        BATCH_SIZE=32  # Larger batch for GPU
    else
        BATCH_SIZE=8   # Smaller batch for CPU
    fi

    python3 scripts/train_transformer.py \
      --run-dir "$RUN_DIR" \
      --epochs "$EPOCHS" \
      --batch-size "$BATCH_SIZE" \
      --lr 0.001 \
      --hidden-size "$HIDDEN_SIZE" \
      --device "$DEVICE" | tee "$RUN_DIR/logs/training.log"

    echo ""
    echo "=========================================="
    echo "Training Complete!"
    echo "=========================================="
    echo ""

    # Show results
    echo "📊 Final Results:"
    cat "$RUN_DIR/logs/final_results.json" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f\"   Best epoch: {d['best_epoch']}\")
print(f\"   Validation accuracy: {d['best_val_acc']:.2f}%\")
print(f\"   PySR baseline: {d['pysr_baseline']:.2f}%\")
print(f\"   Gap: {d['gap']:.2f}%\")
print(f\"   Training time: {d['training_time_seconds']/60:.1f} minutes\")
"

    echo ""
    echo "💾 Results saved to:"
    echo "   $RUN_DIR/logs/final_results.json"
    echo "   $RUN_DIR/logs/training_history.json"
    echo "   $RUN_DIR/checkpoints/best_model.pth"
    echo ""
else
    echo ""
    echo "Training cancelled. Quick test results saved to:"
    echo "   $RUN_DIR"
fi
