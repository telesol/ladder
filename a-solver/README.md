# A-Solver: Bitcoin Puzzle Mathematics AI

**Model:** qwen3-vl:8b (GPU-accelerated via Ollama)
**Certified:** 2025-12-09
**Score:** 10/10 (Perfect)
**Platform:** NVIDIA DGX Spark (GB10 Blackwell)

---

## Quick Start

```bash
# Query the model directly
curl -X POST http://localhost:11434/api/generate \
  -d '{"model": "qwen3-vl:8b", "prompt": "YOUR_QUESTION", "stream": false}'

# Or use the Python API
python a-solver/query.py "What is the range for puzzle 71?"
```

---

## Certification Results

| Level | Category | Score | Status |
|-------|----------|-------|--------|
| 1 | Foundation | 3/3 | PASS |
| 2 | Pattern Recognition | 5/5 | PASS |
| 3 | Analysis & Reasoning | 2/2 | PASS |

### Exercises Passed

1. **Key Range Calculation** - Computes [2^(N-1), 2^N - 1] for any puzzle N
2. **Key Factorization** - Prime factorizes keys, identifies patterns (k_5 = 3×7, k_6 = 7²)
3. **Position in Range** - Calculates percentage position of key in valid range
4. **Verify Relationships** - Confirms/denies claimed key relationships
5. **Linear Recurrence** - Verifies k_n = a×k_{n-1} + b×k_{n-2} patterns
6. **Normalized Delta** - Calculates (k_{n+1} - k_n)/2^n, identifies anomalies
7. **Affine Model Limitation** - Explains circular dependency in C = (y - A×x) mod 256
8. **Bridge Ratios** - Computes 5-step jump ratios, compares to expected 2^5
9. **Anomaly Detection** - Identifies pattern breaks (Lane 9 not divisible by 13)
10. **Constraint Derivation** - Analyzes if delta bounds reduce search space

---

## Capabilities

### What This Model Can Do

- Calculate valid key ranges for any puzzle number
- Factorize puzzle keys and identify mathematical relationships
- Verify claimed formulas between keys
- Compute normalized deltas and identify anomalies
- Analyze the affine byte-level model
- Reason about search space constraints
- Identify pattern breaks and anomalies

### What This Model Cannot Do

- Predict unknown private keys (no cryptographic breakthrough)
- Find shortcuts that reduce 2^70 search space significantly
- Explain the exact key generation algorithm used

---

## Mathematical Knowledge

### Core Formulas

```
Key Range:     k_N ∈ [2^(N-1), 2^N - 1]
Position:      pos% = (k_N - 2^(N-1)) / (2^(N-1) - 1) × 100
Norm Delta:    δ_norm = (k_{n+1} - k_n) / 2^n
Affine Model:  y = A×x + C (mod 256)
```

### Known Key Relationships

```
k_5 = k_2 × k_3 = 3 × 7 = 21
k_6 = k_3² = 7² = 49
k_8 = k_4 × k_3 × 4 = 8 × 7 × 4 = 224
```

### Linear Recurrence (coefficient 19)

```
k_3 = -4×k_2 + 19×k_1 = -12 + 19 = 7 ✓
k_4 = -7×k_3 + 19×k_2 = -49 + 57 = 8 ✓
k_5 = -14×k_4 + 19×k_3 = -112 + 133 = 21 ✓
Pattern breaks after k_6
```

### A Multipliers (Byte-Level Affine)

| Lane | A Value | Factorization |
|------|---------|---------------|
| 0 | 1 | 1 |
| 1 | 91 | 7 × 13 |
| 5 | 169 | 13² |
| 9 | 32 | 2^5 (ANOMALY) |
| 13 | 182 | 2 × 7 × 13 |

### Key Statistics

- Normalized delta range: [0.092, 1.305]
- Normalized delta mean: 0.762
- Position mean: 51.86%
- Anomalous positions: k_4 (0%), k_69 (0.72%), k_3 (100%)

---

## Reference Data

### Known Private Keys

```python
KNOWN_KEYS = {
    1: 1, 2: 3, 3: 7, 4: 8, 5: 21, 6: 49, 7: 76, 8: 224,
    9: 467, 10: 514, 11: 1155, 12: 2683, 13: 5765, 14: 10544,
    15: 26867, 16: 51510, 17: 95823, 18: 198669, 19: 357535,
    20: 863317,
    # ... up to puzzle 70 solved
    69: 297274491920375905804,
    70: 970436974005023690481,
    # Bridge puzzles
    75: 22538323240989823823367,
    80: 1105520030589234487939456,
    85: 21090315766411506144426920,
    90: 868012190417726402719548863,
    # ... up to 130
}
```

### Unsolved Target

```
Puzzle 71: k_71 ∈ [2^70, 2^71 - 1]
         = [1180591620717411303424, 2361183241434822606847]
Search space: ~1.18 × 10^21 candidates
```

---

## Files

```
a-solver/
├── README.md              # This file
├── query.py               # Python query interface
├── MATH_REFERENCE.md      # Complete mathematical reference
├── TRAINING_LOG.md        # Training session transcript
├── config.json            # Model configuration
└── examples/              # Example queries and responses
```

---

## Usage Examples

### Example 1: Verify a Relationship

```python
from query import ask

response = ask("Is k_10 = k_5 × k_4? Given k_5=21, k_4=8, k_10=514")
# Response: FALSE. 21 × 8 = 168 ≠ 514
```

### Example 2: Calculate Normalized Delta

```python
response = ask("Calculate normalized delta for k_68→k_69")
# Response: δ = (297274491920375905804 - prev) / 2^68
```

### Example 3: Analyze Anomaly

```python
response = ask("Why is k_69 anomalous?")
# Response: k_69 is at 0.72% of its valid range, extremely low
# compared to mean of 51.86%. This allowed fast solving.
```

---

## Performance

- **Inference Speed:** ~20-100s per complex query (GPU)
- **Memory Usage:** ~11GB VRAM
- **Accuracy:** 100% on certified exercises

---

## Limitations & Honest Assessment

1. **No Predictive Power:** Cannot predict unknown keys
2. **Circular Reasoning:** Affine model C values require knowing the answer
3. **Delta Bounds Don't Help:** For puzzle 71, delta constraints don't reduce search beyond bit range
4. **Pattern Breaks:** Early key relationships (k_5=k_2×k_3) don't extend to larger puzzles
5. **Cryptographically Random:** Keys above ~20 appear pseudo-random

---

## Version History

| Date | Version | Notes |
|------|---------|-------|
| 2025-12-09 | 1.0 | Initial certification (10/10) |

---

## Contact

For questions about the mathematical analysis, refer to:
- `/home/solo/LA/AI_TRAINING_CURRICULUM.md`
- `/home/solo/LA/AI_TRAINING_ANSWER_KEY.json`
- `/home/solo/LA/LOCAL_AI_TRAINING_PLAN.md`
