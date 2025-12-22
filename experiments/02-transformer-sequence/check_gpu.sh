#!/bin/bash
# Check GPU availability and PyTorch CUDA support

echo "============================================"
echo "GPU & CUDA Availability Check"
echo "============================================"
echo ""

# Check nvidia-smi
echo "1. Checking nvidia-smi..."
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
    echo "   ✅ NVIDIA GPU detected"
else
    echo "   ❌ nvidia-smi not found (no GPU or drivers not installed)"
fi

echo ""
echo "2. Checking PyTorch CUDA support..."

# Activate venv if exists
# Check for 02-train first, then fall back to .venv
if [ -f "$HOME/LadderV3/kh-assist/experiments/02-transformer-sequence/02-train/bin/activate" ]; then
    source "$HOME/LadderV3/kh-assist/experiments/02-transformer-sequence/02-train/bin/activate"
    echo "   Using environment: 02-train"
elif [ -f "../../.venv/bin/activate" ]; then
    source ../../.venv/bin/activate
    echo "   Using environment: ../../.venv"
fi

# Check PyTorch
python3 -c "
import torch
print(f'   PyTorch version: {torch.__version__}')
print(f'   CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'   CUDA version: {torch.version.cuda}')
    print(f'   GPU count: {torch.cuda.device_count()}')
    print(f'   GPU name: {torch.cuda.get_device_name(0)}')
    print(f'   GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB')
    print('')
    print('   ✅ GPU ready for training!')
    print('   Use: --device cuda')
else:
    print('')
    print('   ⚠️  CUDA not available')
    print('   Use: --device cpu')
    print('')
    print('   To enable GPU:')
    print('   pip uninstall torch')
    print('   pip install torch --index-url https://download.pytorch.org/whl/cu118')
" 2>/dev/null || echo "   ❌ PyTorch not installed"

echo ""
echo "============================================"
