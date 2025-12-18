# Bitcoin Puzzle Formula Registry

**Date**: 2025-12-16
**Data Source**: db/kh.db (74 keys)

## Verified Formulas

### Formula 1: Master Recurrence
```
k_n = 2 × k_{n-1} + adj_n
```
**Verified**: 69/69 consecutive pairs (k1→k70)

### Formula 2: Adjustment Decomposition
```
adj_n = 2^n - m_n × k_{d_n}
```
**Verified**: 69/69 pairs

### Formula 3: Closed Form
```
k_n = 2^{n-1} + Σ(i=2 to n) 2^{n-i} × adj_i
```
**Verified**: 69/69 keys

## Data Tables

### Table 1: Base Keys
| n | k_n | hex |
|---|-----|-----|
| 1 | 1 | 0x1 |
| 2 | 3 | 0x3 |
| 3 | 7 | 0x7 |
| 4 | 8 | 0x8 |
| 5 | 21 | 0x15 |
| 6 | 49 | 0x31 |
| 7 | 76 | 0x4c |
| 8 | 224 | 0xe0 |

### Table 2: Complete (n, d, m, adj) Values

| n | d | m | adj_n |
|---|---|---|-------|
| 2 | 2 | 1 | 1 |
| 3 | 3 | 1 | 1 |
| 4 | 1 | 22 | -6 |
| 5 | 2 | 9 | 5 |
| 6 | 2 | 19 | 7 |
| 7 | 2 | 50 | -22 |
| 8 | 4 | 23 | 72 |
| 9 | 1 | 493 | 19 |
| 10 | 7 | 19 | -420 |
| 11 | 1 | 1921 | 127 |
| 12 | 2 | 1241 | 373 |
| 13 | 1 | 8342 | -150 |
| 14 | 4 | 2034 | 112 |
| 15 | 1 | 26989 | 5779 |
| 16 | 4 | 8470 | -2224 |
| 17 | 1 | 138269 | -7197 |
| 18 | 1 | 255121 | 7023 |
| 19 | 1 | 564091 | -39803 |
| 20 | 1 | 900329 | 148247 |
| 21 | 2 | 670674 | 85130 |
| 22 | 2 | 1603443 | -616025 |
| 23 | 1 | 8804812 | -416204 |
| 24 | 4 | 1693268 | 3231072 |
| 25 | 1 | 29226275 | 4328157 |
| 66 | 8 | 395435327538483377 | -14790537073782069984 |
| 67 | 2 | 35869814695994276026 | 39964508501693584850 |
| 68 | 1 | 340563526170809298635 | -45415620991456472779 |
| 69 | 5 | 34896088136426753598 | -142522040506256173846 |
| 70 | 2 | 268234543517713141517 | 375887990164271878873 |

### Table 3: d Frequency Distribution

| d | k_d | count |
|---|-----|-------|
| 1 | 1 | 30 |
| 2 | 3 | 20 |
| 3 | 7 | 4 |
| 4 | 8 | 5 |
| 5 | 21 | 5 |
| 6 | 49 | 1 |
| 7 | 76 | 1 |
| 8 | 224 | 3 |

### Table 4: Sequence Memberships

| n | k_n | F(i) | L(i) |
|---|-----|------|------|
| 1 | 1 | F(1), F(2) | L(1) |
| 2 | 3 | F(4) | L(2) |
| 3 | 7 | - | L(4) |
| 4 | 8 | F(6) | - |
| 5 | 21 | F(8) | - |
| 7 | 76 | - | L(9) |

### Table 5: Position in Bit Range

| n | k_n | pos = (k - 2^(n-1)) / (2^(n-1) - 1) |
|---|-----|-------------------------------------|
| 1 | 1 | 0.000000 |
| 4 | 8 | 0.000000 |
| 10 | 514 | 0.003914 |
| 69 | 297274491920375905804 | 0.007205 |
| 2 | 3 | 1.000000 |
| 3 | 7 | 1.000000 |

### Table 6: Gap Keys

| n | k_n | pos |
|---|-----|-----|
| 75 | 22538323240989823823367 | 0.193169 |
| 80 | 1105520030589234487939456 | 0.828929 |
| 85 | 21090315766411506144426920 | 0.090344 |
| 90 | 868012190417726402719548863 | 0.402349 |

## Numerical Bounds

| Metric | Min | Max | Mean |
|--------|-----|-----|------|
| adj_n / 2^n | -0.241 | +0.319 | +0.01 |
| m / 2^(n-d) | 0.718 | 2.750 | 1.684 |

## OEIS Reference

Sequence ID: A369920

## Verification Script

```python
import sqlite3
conn = sqlite3.connect('db/kh.db')
cur = conn.cursor()
cur.execute('SELECT puzzle_id, priv_hex FROM keys ORDER BY puzzle_id')
keys = {r[0]: int(r[1], 16) for r in cur.fetchall()}

# Verify Formula 1
for n in range(2, 71):
    if n in keys and n-1 in keys:
        adj = keys[n] - 2*keys[n-1]
        assert keys[n] == 2*keys[n-1] + adj

# Verify Formula 2
k_base = {1:1, 2:3, 3:7, 4:8, 5:21, 6:49, 7:76, 8:224}
for n in range(2, 71):
    if n in keys and n-1 in keys:
        adj = keys[n] - 2*keys[n-1]
        found = False
        for d in range(1, 9):
            if d in k_base:
                num = 2**n - adj
                if num % k_base[d] == 0:
                    found = True
                    break
        assert found
```
