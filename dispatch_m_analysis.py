#!/usr/bin/env python3
"""
Dispatch m-sequence structure analysis to local models.
Goal: Find what generates m[n].
"""
import sqlite3
import subprocess

# Load k values and compute m values
conn = sqlite3.connect('/home/solo/ladder/db/kh.db')
cur = conn.cursor()
k_values = {}
for n in range(1, 71):
    cur.execute('SELECT priv_hex FROM keys WHERE puzzle_id = ?', (n,))
    row = cur.fetchone()
    if row:
        k_values[n] = int(row[0], 16)
conn.close()

# Compute m and d values
m_values = {}
d_values = {}
adj_values = {}

for n in range(2, 71):
    if n in k_values and (n-1) in k_values:
        adj_n = k_values[n] - 2*k_values[n-1]
        adj_values[n] = adj_n
        N_n = 2**n - adj_n
        best_d = None
        best_m = None
        for try_d in range(1, n):
            if try_d in k_values:
                k_d = k_values[try_d]
                if N_n % k_d == 0:
                    m_try = N_n // k_d
                    if best_m is None or m_try < best_m:
                        best_m = m_try
                        best_d = try_d
        if best_m is not None:
            m_values[n] = best_m
            d_values[n] = best_d

# Prepare data
m_data = "\n".join([f"m[{n}] = {m_values[n]}, d[{n}] = {d_values[n]}" for n in range(2, 21)])

prompt = f"""You are analyzing the m-sequence from the Bitcoin puzzle to find its generation formula.

VERIFIED FORMULA:
m[n] = (2^n - adj[n]) / k[d[n]]

where:
- adj[n] = k[n] - 2*k[n-1]
- d[n] minimizes m[n] among valid divisors

DATA (n=2 to 20):
{m_data}

KEY PATTERNS FOUND:
- m[4] = 22 (π approximation 22/7)
- m[5] = 9 = 3²
- m[6] = 19 (prime, appears in √3 convergents)
- m[7] = 50 = 2 × 5²
- m[8] = 23 (prime)
- m[9] = 493 = 17 × 29
- m[10] = 19 (same as m[6]!)
- m[11] = 1921 = 17 × 113
- m[12] = 1241 = 17 × 73

SELF-REFERENTIAL PATTERNS:
- m[19] = 19 × 29689 (n divides m[n])
- m[41] = 41 × 22342064035 (n divides m[n])

TASK:
1. What mathematical structure generates m[n]?
2. Is there a closed-form formula m[n] = f(n)?
3. Why does 17 appear so often in m-value factorizations?
4. Can you find a pattern that predicts m[71]?

Provide rigorous mathematical analysis.
"""

print("=" * 70)
print("DISPATCHING M-SEQUENCE ANALYSIS TO LOCAL MODEL")
print("=" * 70)
print()

try:
    result = subprocess.run(
        ['ollama', 'run', 'nemotron-3-nano:30b-cloud', prompt],
        capture_output=True,
        text=True,
        timeout=300
    )
    print("### Nemotron-3-Nano Response ###")
    print(result.stdout[:3000] if result.stdout else "No output")
except subprocess.TimeoutExpired:
    print("Model timed out after 5 minutes")
except Exception as e:
    print(f"Error: {e}")

print()
print("=" * 70)
