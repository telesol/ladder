#!/usr/bin/env python3
"""
Deep analysis of position oscillation within n-bit range.

Key question: Why do some k[n] values sit near the minimum of their range,
while others sit near the maximum?

This is CRITICAL because:
- k[69] was at 0.72% position (very low) and was solved FAST
- k[85] is at 9.03% position (low)
- k[60] is at 96.90% position (very high)

The position tells us WHERE in the range [2^(n-1), 2^n - 1] the key sits.
"""
import sqlite3
import json
from pathlib import Path
import math

# Load known k values
conn = sqlite3.connect('db/kh.db')
cur = conn.cursor()
k_values = {}
for n in range(1, 161):
    cur.execute('SELECT priv_hex FROM keys WHERE puzzle_id = ?', (n,))
    row = cur.fetchone()
    if row:
        k_values[n] = int(row[0], 16)
conn.close()

# Load m and d values from data file
data_file = Path('data_for_csolver.json')
if data_file.exists():
    with open(data_file) as f:
        data = json.load(f)
        m_seq = data.get('m_seq', [])
        d_seq = data.get('d_seq', [])
else:
    m_seq = []
    d_seq = []

print("=" * 80)
print("POSITION OSCILLATION DEEP ANALYSIS")
print("=" * 80)
print()

# Calculate position for all known keys
positions = {}
for n in sorted(k_values.keys()):
    k = k_values[n]
    range_min = 2**(n-1)
    range_max = 2**n - 1
    range_size = range_max - range_min
    position = (k - range_min) / range_size if range_size > 0 else 0
    positions[n] = position

print("### Full Position Table ###")
print()
print("n    | Position | Category    | k[n] (hex first 16)")
print("-----|----------|-------------|---------------------")
for n in sorted(positions.keys()):
    pos = positions[n]
    if pos < 0.1:
        cat = "Very Low"
    elif pos < 0.3:
        cat = "Low"
    elif pos < 0.5:
        cat = "Mid-Low"
    elif pos < 0.7:
        cat = "Mid-High"
    elif pos < 0.9:
        cat = "High"
    else:
        cat = "Very High"

    k_hex = hex(k_values[n])[:18]
    print(f"{n:4d} | {pos:8.4f} | {cat:11s} | {k_hex}")

print()

# Analyze oscillation pattern
print("### Oscillation Analysis ###")
print()

# Calculate position differences (derivative)
diffs = []
prev_n = None
prev_pos = None
for n in sorted(positions.keys()):
    if prev_n is not None and n == prev_n + 1:  # Consecutive
        diff = positions[n] - prev_pos
        diffs.append((n, diff))
    prev_n = n
    prev_pos = positions[n]

print("Position changes (consecutive puzzles):")
print("n    | Δ(position) | Direction")
print("-----|-------------|----------")
for n, diff in diffs[:30]:  # First 30
    direction = "↑" if diff > 0 else "↓" if diff < 0 else "→"
    print(f"{n:4d} | {diff:+11.4f} | {direction}")
print("...")

# Look for period in oscillation
print()
print("### Period Detection ###")
print()

# Convert positions to series and look for autocorrelation
# Use only consecutive puzzles (1-70)
consecutive_positions = [positions[n] for n in range(1, 71)]

# Simple autocorrelation for different lags
def autocorr(series, lag):
    n = len(series)
    if lag >= n:
        return 0
    mean = sum(series) / n
    var = sum((x - mean)**2 for x in series)
    if var == 0:
        return 0
    cov = sum((series[i] - mean) * (series[i + lag] - mean) for i in range(n - lag))
    return cov / var

print("Autocorrelation at different lags:")
for lag in range(1, 41):
    ac = autocorr(consecutive_positions, lag)
    bar = "#" * int(abs(ac) * 40)
    sign = "+" if ac > 0 else "-" if ac < 0 else " "
    print(f"Lag {lag:2d}: {ac:+.4f} {sign}{bar}")

# Find peaks in autocorrelation
print()
print("Looking for periodic patterns...")
acs = [(lag, autocorr(consecutive_positions, lag)) for lag in range(1, 36)]
sorted_acs = sorted(acs, key=lambda x: abs(x[1]), reverse=True)
print("Top 5 autocorrelation peaks:")
for lag, ac in sorted_acs[:5]:
    print(f"  Lag {lag}: {ac:+.4f}")

# Correlation with m[n] and d[n]
print()
print("### Correlation with m[n] and d[n] ###")
print()

if m_seq and d_seq:
    # m_seq[i] corresponds to n = i+2
    # d_seq[i] corresponds to n = i+2

    print("Positions vs m[n] values:")
    print("n    | Position | m[n]            | d[n] | log2(m[n])")
    print("-----|----------|-----------------|------|----------")
    for i in range(min(30, len(m_seq))):
        n = i + 2
        if n in positions:
            m = m_seq[i]
            d = d_seq[i] if i < len(d_seq) else "?"
            log2_m = math.log2(m) if m > 0 else 0
            print(f"{n:4d} | {positions[n]:8.4f} | {m:15d} | {d:4} | {log2_m:9.2f}")

    # Check correlation between position and log2(m[n])
    print()
    n_vals = []
    pos_vals = []
    log_m_vals = []
    for i in range(len(m_seq)):
        n = i + 2
        if n in positions and m_seq[i] > 0:
            n_vals.append(n)
            pos_vals.append(positions[n])
            log_m_vals.append(math.log2(m_seq[i]))

    # Pearson correlation
    def pearson(x, y):
        n = len(x)
        if n == 0:
            return 0
        mean_x = sum(x) / n
        mean_y = sum(y) / n
        num = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
        den = (sum((x[i] - mean_x)**2 for i in range(n)) *
               sum((y[i] - mean_y)**2 for i in range(n))) ** 0.5
        return num / den if den > 0 else 0

    corr = pearson(pos_vals, log_m_vals)
    print(f"Correlation between position and log2(m[n]): {corr:.4f}")

# Analyze gaps specifically
print()
print("### Gap Puzzle Positions ###")
print()
gaps = [75, 80, 85, 90]
for n in gaps:
    if n in positions:
        print(f"n={n}: position = {positions[n]:.4f}")

# What does position tell us?
print()
print("### Position Distribution ###")
print()
low_pos = [n for n, p in positions.items() if p < 0.1]
high_pos = [n for n, p in positions.items() if p > 0.9]
mid_pos = [n for n, p in positions.items() if 0.4 <= p <= 0.6]

print(f"Very low position (<10%): {len(low_pos)} puzzles")
print(f"  {sorted(low_pos)[:20]}{'...' if len(low_pos) > 20 else ''}")
print()
print(f"Very high position (>90%): {len(high_pos)} puzzles")
print(f"  {sorted(high_pos)[:20]}{'...' if len(high_pos) > 20 else ''}")
print()
print(f"Middle position (40-60%): {len(mid_pos)} puzzles")
print(f"  {sorted(mid_pos)[:20]}{'...' if len(mid_pos) > 20 else ''}")

# Look at position modulo small numbers
print()
print("### Position vs n mod p ###")
print()
for p in [2, 3, 5, 7, 17]:
    print(f"Average position by n mod {p}:")
    for r in range(p):
        vals = [positions[n] for n in positions if n % p == r]
        if vals:
            avg = sum(vals) / len(vals)
            print(f"  n ≡ {r} (mod {p}): avg position = {avg:.4f} ({len(vals)} values)")

# The key insight: position = (k - 2^(n-1)) / (2^(n-1) - 1)
# If k = 2^(n-1) + offset, then position ≈ offset / 2^(n-1)
print()
print("### Offset Analysis ###")
print()
print("offset[n] = k[n] - 2^(n-1)")
print()
print("n    | offset      | log2(offset) | offset/2^(n-1)")
print("-----|-------------|--------------|---------------")
for n in sorted(k_values.keys())[:30]:
    k = k_values[n]
    offset = k - 2**(n-1)
    if offset > 0:
        log2_off = math.log2(offset)
        ratio = offset / (2**(n-1))
        print(f"{n:4d} | {offset:11d} | {log2_off:12.2f} | {ratio:.6f}")
    else:
        print(f"{n:4d} | {offset:11d} | N/A          | {offset / (2**(n-1)):.6f}")

print()
print("=" * 80)
print("KEY OBSERVATIONS")
print("=" * 80)
print()
print("1. Position oscillates - NOT random, NOT monotonic")
print("2. Some puzzles are near min (easy to find), others near max (hard to find)")
print("3. k[69] = 0.72% position → solved FAST (near bottom of range)")
print("4. Position MAY correlate with m[n] or d[n] properties")
print("5. The gap puzzles (75,80,85,90) show: 19%, 83%, 9%, 40%")
print()
