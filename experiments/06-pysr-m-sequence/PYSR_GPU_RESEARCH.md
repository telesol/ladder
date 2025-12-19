# PySR GPU/Performance Research Results

**Date**: 2025-12-19
**GPU**: NVIDIA RTX 5000 Ada (15GB VRAM)
**PySR Version**: 1.5.9

---

## 🔍 Research Findings

### GPU Support in PySR

**❌ PySR 1.5.9 does NOT have native GPU support**

- PySR uses Julia's SymbolicRegression.jl backend
- SymbolicRegression.jl is CPU-only (uses multiprocessing/multithreading)
- No CUDA/GPU acceleration in standard PySR

### GPU-Accelerated Alternative

**SymbolicRegressionGPU.jl** (experimental fork):
- GitHub: https://github.com/x66ccff/SymbolicRegressionGPU.jl
- Provides PSRN (Parallel Symbolic Regression Network)
- Requires PyTorch with CUDA
- **NOT compatible with standard PySR 1.5.9**

### Performance Reality

**For our use case**:
- 24 training samples (VERY small dataset)
- 245 features
- GPU acceleration wouldn't help much (CPU multiprocessing is better)
- Bottleneck: evolutionary search, not linear algebra

---

## ✅ Optimal Strategy for Our Case

### Use CPU Multiprocessing

**Best PySR configuration**:

```python
model = PySRRegressor(
    # Parallelization (uses all CPU cores)
    procs=4,              # Use 4 parallel processes
    multithreading=True,  # Enable Julia multithreading

    # Evolution parameters
    niterations=100,
    populations=20,       # Reduce from 30 (4 procs × 5 populations each)
    population_size=50,
    ncycles_per_iteration=500,

    # Formula complexity
    maxsize=15,
    parsimony=0.001,

    # Operators
    binary_operators=["+", "*", "-", "/"],
    unary_operators=["square", "cube"],

    # Output
    verbosity=1,
    progress=True,
    temp_equation_file=True,
)
```

### Why This Works Better Than GPU

1. **Small dataset** (24 samples) - no GPU benefit
2. **Evolutionary search** - inherently parallel (CPU multiproc wins)
3. **Feature evaluation** - CPU cache-friendly for 245 features
4. **RTX 5000 Ada** - better used for other tasks (neural networks, etc.)

---

## 📊 Performance Optimization

### Multiprocessing Configuration

**Formula**:
```
procs = min(CPU_cores, populations)
populations = procs × populations_per_proc
```

**For typical machine** (8 cores):
```python
procs=4                 # Use 4 cores (leave some free)
populations=20          # 4 procs × 5 populations each
population_size=50      # Size of each population
```

### Expected Performance

**Sequential** (procs=0):
- ~4-6 hours for 100 iterations

**Parallel** (procs=4):
- ~1-2 hours for 100 iterations
- **2-3x speedup**

**With more cores** (procs=8):
- ~30-60 minutes
- **4-6x speedup**

---

## 🚀 Updated Training Script

```python
#!/usr/bin/env python3
import pandas as pd
import numpy as np
import json
from datetime import datetime
from pysr import PySRRegressor

def main():
    # Load data
    df = pd.read_csv('feature_matrix.csv')
    train_df = df[df['n'] <= 25]
    val_df = df[df['n'] > 25]

    X_train = train_df.drop(['target_m'], axis=1).values
    y_train = train_df['target_m'].values
    X_val = val_df.drop(['target_m'], axis=1).values
    y_val = val_df['target_m'].values

    feature_names = train_df.drop(['target_m'], axis=1).columns.tolist()

    # Configure PySR with CPU multiprocessing
    model = PySRRegressor(
        procs=4,                       # 4 parallel processes
        multithreading=True,           # Enable Julia threading
        niterations=100,
        populations=20,                # 4 × 5 populations
        population_size=50,
        ncycles_per_iteration=500,
        maxsize=15,
        parsimony=0.001,
        binary_operators=["+", "*", "-", "/"],
        unary_operators=["square", "cube"],
        verbosity=1,
        progress=True,
        temp_equation_file=True,
    )

    print("Training with CPU multiprocessing (procs=4)...")
    print(f"Expected runtime: 1-2 hours")

    model.fit(X_train, y_train, variable_names=feature_names)

    # Validation
    y_pred = model.predict(X_val)
    accuracy = sum(int(round(p)) == a for p, a in zip(y_pred, y_val)) / len(y_val) * 100

    print(f"Validation Accuracy: {accuracy:.1f}%")
    print(f"Best Formula: {model.sympy()}")

    return model, accuracy

if __name__ == "__main__":
    main()
```

---

## 🎯 Bottom Line

**GPU is NOT needed for PySR with our dataset size.**

**Best approach**:
1. ✅ Use CPU multiprocessing (`procs=4`)
2. ✅ Enable multithreading
3. ✅ Optimize population parameters
4. ✅ Expected: 1-2 hours runtime (vs 4-6 hours sequential)

**GPU alternatives** (if needed later):
- SymbolicRegressionGPU.jl fork (complex setup)
- Neural network approach (transformers, etc.) - DOES use GPU
- Hybrid: PySR for formula discovery, NN for refinement

---

## 📝 Next Steps

1. Wait for other Claude to update GitHub with correct m-sequence data
2. Pull latest data
3. Update `prepare_convergent_features.py` with correct data
4. Run training with optimized CPU multiprocessing config
5. Expected result: 1-2 hours to formula discovery

---

**Status**: Research complete, ready to proceed with CPU optimization
**GPU**: Not applicable for PySR symbolic regression
**Performance gain**: 2-3x with procs=4
