# Environment Setup

## ✅ Current Setup: 02-train

You have created a Python virtual environment at:
```
/home/solo/LadderV3/kh-assist/experiments/02-transformer-sequence/02-train/
```

**Installed:**
- ✅ PyTorch 2.7.1+cu118 (GPU version)
- ✅ CUDA 11.8 support
- ✅ GPU detected: NVIDIA RTX 5000 Ada (16GB VRAM)

---

## Activate Environment

**Always activate before running scripts:**

```bash
cd /home/solo/LadderV3/kh-assist/experiments/02-transformer-sequence
source 02-train/bin/activate
```

---

## Verify GPU

```bash
source 02-train/bin/activate
./check_gpu.sh
```

Expected output:
```
✅ GPU ready for training!
GPU name: NVIDIA RTX 5000 Ada Generation Laptop GPU
GPU memory: 16.10 GB
CUDA available: True
```

---

## Training with GPU

**All scripts now auto-detect and use GPU:**

```bash
# Activate environment
source 02-train/bin/activate

# Run training (will use GPU automatically)
./run_experiment.sh baseline 100 128
```

**Or manual:**

```bash
source 02-train/bin/activate
python3 scripts/train_transformer.py --run-dir run_001_baseline --device cuda
```

---

## Performance Expectations

With RTX 5000 GPU:
- **Quick test (10 epochs)**: ~1-2 minutes
- **Full training (100 epochs)**: ~10-15 minutes
- **Batch size**: 32-64 (vs 8 on CPU)

**8-12x faster than CPU!** ⚡

---

## Troubleshooting

### "CUDA not available"
Make sure you're using the `02-train` environment:
```bash
source 02-train/bin/activate
python3 -c "import torch; print(torch.cuda.is_available())"
```

Should output: `True`

### "torch not found"
Install in 02-train environment:
```bash
source 02-train/bin/activate
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

---

## Environment Info

**Location:** `02-train/`
**Python:** 3.12
**PyTorch:** 2.7.1+cu118
**CUDA:** 11.8
**GPU:** NVIDIA RTX 5000 Ada (16GB)

---

**Scripts automatically use this environment!**
Just run: `./run_experiment.sh baseline 100 128`
