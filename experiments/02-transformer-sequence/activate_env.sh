#!/bin/bash
# Helper script to activate the correct environment

if [ -f "02-train/bin/activate" ]; then
    echo "Activating 02-train environment..."
    source 02-train/bin/activate
    echo "✅ Environment: 02-train"
    echo "✅ Python: $(python3 --version)"
    echo "✅ PyTorch: $(python3 -c 'import torch; print(torch.__version__)')"
    echo "✅ CUDA: $(python3 -c 'import torch; print(torch.cuda.is_available())')"
elif [ -f "../../.venv/bin/activate" ]; then
    echo "Activating ../../.venv environment..."
    source ../../.venv/bin/activate
    echo "✅ Environment: ../../.venv"
else
    echo "⚠️  No virtual environment found"
fi
