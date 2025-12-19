# Claude Coordination Note - UPDATED

**Last Updated**: 2025-12-19 19:20 UTC
**Status**: FACTORIZATION COMPLETE - READY FOR PYSR PRIME OPERATOR

---

## FACTORIZATION COMPLETE!

**ALL 35 values (n=36-70) have been factored!**

| Range | Status | Factored |
|-------|--------|----------|
| n=36-45 | COMPLETE | 10/10 |
| n=46-55 | COMPLETE | 10/10 |
| n=56-70 | COMPLETE | 15/15 |

**Results file**: `factorization_database.json`

---

## MISTAKES FOUND - READ CAREFULLY

### 1. DATA ERROR (CRITICAL)
**OLD DATA WAS WRONG!** The m-sequence values were incorrect:
- OLD: m[2]=3, m[3]=7, d[2]=1, d[3]=1
- CORRECT: m[2]=1, m[3]=1, d[2]=2, d[3]=3

Also wrong m-values for n>=22:
- OLD: m[22]=4494340
- CORRECT: m[22]=1603443

**Source of truth**: `/home/solo/LA/data_for_csolver.json`

### 2. PySR API ISSUES
The PySR training script had bugs:
- `equation_file` parameter doesn't exist anymore
- `elementwise_loss=True` conflicts with `loss="L2DistLoss()"`
- `ncyclesperiteration` should be `ncycles_per_iteration`
- `model.save()` method doesn't exist - use pickle instead

**Fixed in**: `/home/solo/LA/experiments/06-pysr-m-sequence/train_m_sequence.py`

### 3. FACTORIZATION LESSONS
- GNU `factor` is 60000x faster than sympy `factorint`
- `sympy.primepi()` is very slow for primes > 10 billion
- Use `quick_factor.py` which defers large prime index computation

---

## KEY FINDINGS FROM FACTORIZATION

### Interesting Patterns in n=36-70:
- **n=48**: Contains p[7]=17 (m=329601320238553 = 11 x 17 x 1762573905019)
- **n=57**: Many small primes! m = 2 x 5 x 19 x 113 x 1487 x 5953 x 23629
- **n=67**: Contains p[7]=17 again (m = 2 x 17 x 31 x 179 x 15053 x 12630264037)
- **n=69**: Contains p[8]=19 (m = 2 x 3 x 19 x 109 x 959617 x 2926492819)

### Prime Index Pattern
p[7] = 17 appears at: n=9, n=11, n=12, n=48, n=67
p[8] = 19 appears at: n=6, n=10, n=57, n=58, n=69

---

## PYSR STATUS

### Current Configuration (FIXED):
```python
PySRRegressor(
    niterations=100,
    binary_operators=["+", "*", "-", "/"],
    unary_operators=["square", "cube"],
    populations=40,
    population_size=50,
    parallelism='multiprocessing',  # USE ALL 20 CORES!
    procs=20,
)
```

### Next Step: Add prime(i) Operator
Need to create a custom operator that returns the i-th prime.
This is necessary because m-values are often prime products.

---

## KEY FILES

### Verified Data
- `data_for_csolver.json` - CORRECT m_seq, d_seq for n=2..70
- `FORMULA_SUMMARY.md` - Verified formulas for n=2..35
- `factorization_database.json` - Complete factorizations for n=36..70

### Scripts
- `quick_factor.py` - Fast factorization using GNU factor
- `merge_factorizations.py` - Merges factorization JSON files
- `experiments/06-pysr-m-sequence/train_m_sequence.py` - Fixed PySR script

### Coordination
- `COORDINATION_NOTE_FOR_OTHER_CLAUDE.md` - THIS FILE
- `CLAUDE.md` - Project rules and context

---

## VERIFIED FORMULAS (n=2 to 35)

The m-sequence uses **PRIME INDICES** and **SELF-REFERENCES**:

```
m[9]  = p[7] x p[10] = 17 x 29 = 493
m[11] = p[7] x p[n+m[6]] = 17 x 113 = 1921
m[12] = p[7] x p[n+m[5]] = 17 x 73 = 1241
m[18] = prime(m[7] x p[87]) = prime(22450) = 255121
```

**Key building blocks**:
- m[2]=1, m[3]=1, m[4]=22, m[5]=9, m[6]=19, m[7]=50, m[8]=23
- p[7]=17 appears frequently as a factor

---

## PROGRESS TRACKER

- [x] Master formula verified: k_n = 2*k_{n-1} + adj_n
- [x] Convergent patterns discovered (pi, e, sqrt2, sqrt3, phi, ln2)
- [x] PySR experiment run (approximate formula found)
- [x] Data discrepancy fixed (m[2]=1, m[3]=1)
- [x] Factorization of m[36-70] COMPLETE
- [x] Factorization database created
- [ ] Prime operator added to PySR
- [ ] Re-train PySR with prime operator
- [ ] Generate formulas for m[71-160]

---

## NEXT ACTIONS

1. **Add prime(i) operator to PySR** - custom Julia operator
2. **Re-run PySR** with expanded operator set and full parallelization
3. **Analyze factorization patterns** - look for index formulas
4. **Try predicting n=71+** using discovered patterns

---

## SYNC COMMAND

```bash
git pull origin main
cat COORDINATION_NOTE_FOR_OTHER_CLAUDE.md
```
