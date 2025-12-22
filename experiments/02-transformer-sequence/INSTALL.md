# Installation Guide

## ⚠️ Important: This is NOT an LLM

We are **NOT** using qwen2.5-coder or any language model.

We are training a **custom PyTorch neural network** from scratch.

---

## Quick Install

```bash
cd /home/solo/LadderV3/kh-assist/experiments/02-transformer-sequence

# Run installation script
./install_deps.sh
```

This will:
1. Create/use virtual environment at `../../.venv`
2. Install PyTorch (CPU version)
3. Install NumPy, pandas, scikit-learn, etc.
4. Verify installation

---

## Manual Install

If you prefer manual installation:

```bash
# Create virtual environment (if not exists)
cd /home/solo/LadderV3/kh-assist
python3 -m venv .venv

# Activate
source .venv/bin/activate

# Install dependencies
cd experiments/02-transformer-sequence
pip install -r requirements.txt
```

---

## Dependencies

### Core (Required)
- **PyTorch** >= 2.0.0 (deep learning framework)
- **NumPy** >= 1.24.0 (numerical computing)
- **pandas** >= 2.0.0 (data manipulation)

### Training (Required)
- **scikit-learn** >= 1.3.0 (metrics, utilities)
- **matplotlib** >= 3.7.0 (plotting)
- **tqdm** >= 4.65.0 (progress bars)

### Optional
- **seaborn** (better plots)
- **scipy** (scientific computing)

---

## GPU Support (Optional)

If you have CUDA GPU:

```bash
# Instead of CPU version, install CUDA version
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

Then use `--device cuda` when training:
```bash
python scripts/train_transformer.py --device cuda
```

---

## Verify Installation

```bash
# Check PyTorch
python3 -c "import torch; print(f'PyTorch: {torch.__version__}')"

# Check NumPy
python3 -c "import numpy; print(f'NumPy: {numpy.__version__}')"

# Check if CUDA available
python3 -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

Expected output:
```
PyTorch: 2.x.x
NumPy: 1.24.x
CUDA available: False  (or True if GPU)
```

---

## Troubleshooting

### "torch not found"
```bash
# Make sure virtual environment is activated
source ../../.venv/bin/activate

# Reinstall PyTorch
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

### "numpy version conflict"
```bash
pip install --upgrade numpy
```

### "Permission denied"
```bash
chmod +x install_deps.sh
./install_deps.sh
```

---

## What Gets Installed

**NOT installed:**
- ❌ Ollama
- ❌ qwen2.5-coder
- ❌ transformers library (huggingface)
- ❌ Any language models

**Actually installed:**
- ✅ PyTorch (custom neural networks)
- ✅ NumPy (array operations)
- ✅ Basic ML utilities

**Total size:** ~500MB (PyTorch CPU) or ~2GB (PyTorch GPU)

---

## Next Steps After Install

1. **Verify data is ready:**
   ```bash
   ls -lh data/train_*.npy
   ```

2. **Run quick test:**
   ```bash
   ./run_experiment.sh baseline 100 128
   ```

3. **Monitor training:**
   ```bash
   tail -f runs/run_001_baseline/logs/training.log
   ```

---

**Ready to train when installation complete!** 🚀
