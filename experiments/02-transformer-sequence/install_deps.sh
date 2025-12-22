#!/bin/bash
# Install dependencies for transformer training

set -e

echo "============================================"
echo "Installing Transformer Training Dependencies"
echo "============================================"
echo ""

# Check if virtual environment exists
if [ ! -d "../../.venv" ]; then
    echo "Creating virtual environment..."
    cd ../..
    python3 -m venv .venv
    cd experiments/02-transformer-sequence
fi

# Activate virtual environment
echo "Activating virtual environment..."
source ../../.venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install PyTorch
echo ""
echo "Checking for GPU availability..."
if command -v nvidia-smi &> /dev/null; then
    echo "GPU detected! Installing PyTorch with CUDA support..."
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
else
    echo "No GPU detected. Installing PyTorch (CPU version)..."
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
fi

# Install other dependencies
echo ""
echo "Installing other dependencies..."
pip install numpy pandas scikit-learn matplotlib seaborn tqdm scipy jsonlines

echo ""
echo "============================================"
echo "✅ Installation complete!"
echo "============================================"
echo ""
echo "Verify installation:"
python3 -c "import torch; print(f'PyTorch version: {torch.__version__}')"
python3 -c "import numpy; print(f'NumPy version: {numpy.__version__}')"
echo ""
echo "To activate environment in future sessions:"
echo "  source ../../.venv/bin/activate"
