#!/usr/bin/env python3
"""
Combined Ratio Analysis and Magnitude Growth Analysis
Tasks 10 & 12: Analyze k-value ratios and adj magnitude growth patterns
"""

import json
import math
import sqlite3
from typing import List, Tuple, Dict
from fractions import Fraction
from statistics import mean, stdev

def continued_fraction(p: int, q: int, max_terms: int = 10) -> List[int]:
    """Compute continued fraction representation of p/q."""
    if q == 0:
        return []

    cf = []
    while q != 0 and len(cf) < max_terms:
        a = p // q
        cf.append(a)
        p, q = q, p - a * q
    return cf

def convergents_from_cf(cf: List[int]) -> List[Tuple[int, int]]:
    """Compute convergents from continued fraction."""
    if not cf:
        return []

    convergents = []
    h_prev2, h_prev1 = 0, 1
    k_prev2, k_prev1 = 1, 0

    for a in cf:
        h = a * h_prev1 + h_prev2
        k = a * k_prev1 + k_prev2
        convergents.append((h, k))
        h_prev2, h_prev1 = h_prev1, h
        k_prev2, k_prev1 = k_prev1, k

    return convergents

def load_k_values() -> Dict[int, int]:
    """Load k values from database."""
    db_path = '/home/rkh/ladder/db/kh.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT puzzle_id, priv_hex FROM keys WHERE puzzle_id BETWEEN 1 AND 70 ORDER BY puzzle_id")
    k_values = {}

    for puzzle_id, priv_hex in cursor.fetchall():
        k_values[puzzle_id] = int(priv_hex, 16)

    conn.close()
    return k_values

def load_m_and_adj() -> Tuple[Dict[int, int], Dict[int, int]]:
    """Load m_seq and adj_seq from data_for_csolver.json."""
    with open('/home/rkh/ladder/data_for_csolver.json', 'r') as f:
        data = json.load(f)

    # m_seq is indexed from n=2 (m_seq[0] = m[2])
    m_dict = {}
    for i, m in enumerate(data['m_seq']):
        m_dict[i + 2] = m

    # adj_seq is indexed from n=2 (adj_seq[0] = adj[2])
    adj_dict = {}
    for i, adj in enumerate(data['adj_seq']):
        adj_dict[i + 2] = adj

    return m_dict, adj_dict

def task_10_ratio_analysis(k_values: Dict[int, int]) -> Dict:
    """
    Task 10: Ratio Analysis
    10.1. Compute r[n] = k[n]/k[n-1] for n=2 to n=70
    10.2. Find continued fraction representation of each ratio
    10.3. Check if ratios approach a limit (should be ~2)
    10.4. Check correlation with 2^n growth
    """
    results = {
        'ratios': {},
        'continued_fractions': {},
        'ratio_stats': {},
        'convergence_to_2': {},
        'growth_analysis': {}
    }

    # 10.1: Compute ratios
    ratios = []
    for n in range(2, 71):
        if n in k_values and n-1 in k_values:
            ratio = k_values[n] / k_values[n-1]
            ratios.append(ratio)
            results['ratios'][n] = {
                'decimal': ratio,
                'k_n': k_values[n],
                'k_n_minus_1': k_values[n-1]
            }

    # 10.2: Continued fractions (for first 20 ratios to keep output manageable)
    for n in range(2, min(22, 71)):
        if n in k_values and n-1 in k_values:
            k_n = k_values[n]
            k_n_minus_1 = k_values[n-1]

            # Compute continued fraction
            cf = continued_fraction(k_n, k_n_minus_1, max_terms=15)
            results['continued_fractions'][n] = {
                'cf': cf,
                'convergents': convergents_from_cf(cf)[:5]  # First 5 convergents
            }

    # 10.3: Check if ratios approach limit of 2
    ratio_values = [r['decimal'] for r in results['ratios'].values()]
    results['ratio_stats'] = {
        'mean': mean(ratio_values),
        'stdev': stdev(ratio_values) if len(ratio_values) > 1 else 0,
        'min': min(ratio_values),
        'max': max(ratio_values),
        'median': sorted(ratio_values)[len(ratio_values)//2]
    }

    # Analyze convergence in windows
    window_size = 10
    for i in range(0, len(ratio_values) - window_size + 1, window_size):
        window = ratio_values[i:i+window_size]
        n_start = 2 + i
        n_end = n_start + window_size - 1
        results['convergence_to_2'][f'n_{n_start}_to_{n_end}'] = {
            'mean': mean(window),
            'deviation_from_2': abs(mean(window) - 2.0),
            'stdev': stdev(window) if len(window) > 1 else 0
        }

    # 10.4: Check correlation with 2^n growth
    # If k[n] ≈ c * 2^n, then k[n]/k[n-1] ≈ 2
    # Compute how well k[n] fits exponential model
    log2_k_values = []
    for n in range(1, 71):
        if n in k_values:
            log2_k = math.log2(k_values[n]) if k_values[n] > 0 else 0
            log2_k_values.append({
                'n': n,
                'log2_k': log2_k,
                'theoretical_log2': n,  # If k[n] = 2^n
                'deviation': log2_k - n
            })

    results['growth_analysis']['log2_k_vs_n'] = log2_k_values

    # Linear regression: log2(k[n]) ≈ a*n + b
    n_vals = [item['n'] for item in log2_k_values]
    log2_vals = [item['log2_k'] for item in log2_k_values]

    n_mean = mean(n_vals)
    log2_mean = mean(log2_vals)

    numerator = sum((n - n_mean) * (log2 - log2_mean) for n, log2 in zip(n_vals, log2_vals))
    denominator = sum((n - n_mean) ** 2 for n in n_vals)

    slope = numerator / denominator if denominator != 0 else 0
    intercept = log2_mean - slope * n_mean

    results['growth_analysis']['linear_regression'] = {
        'slope': slope,
        'intercept': intercept,
        'interpretation': f'log2(k[n]) ≈ {slope:.4f}*n + {intercept:.4f}',
        'theoretical_slope': 1.0,  # If k[n] = 2^n
        'deviation_from_theoretical': abs(slope - 1.0)
    }

    return results

def task_12_magnitude_analysis(adj_dict: Dict[int, int]) -> Dict:
    """
    Task 12: Magnitude Growth Analysis
    12.1. Compute log2(|adj[n]|) for n=4 to n=70
    12.2. Fit linear regression: log2(|adj[n]|) ≈ a*n + b
    12.3. Compare with theoretical: adj grows as O(2^n)
    12.4. Find deviation patterns from exponential growth
    """
    results = {
        'magnitude_data': [],
        'regression': {},
        'deviation_analysis': {},
        'growth_pattern': {}
    }

    # 12.1: Compute log2(|adj[n]|)
    for n in range(4, 71):  # Start from n=4 as specified
        if n in adj_dict:
            adj_val = adj_dict[n]
            abs_adj = abs(adj_val)

            if abs_adj > 0:
                log2_abs_adj = math.log2(abs_adj)
            else:
                log2_abs_adj = 0  # Handle adj[n] = 0 edge case

            results['magnitude_data'].append({
                'n': n,
                'adj': adj_val,
                'abs_adj': abs_adj,
                'log2_abs_adj': log2_abs_adj,
                'sign': '+' if adj_val >= 0 else '-'
            })

    # 12.2: Linear regression on log2(|adj[n]|) vs n
    n_vals = [item['n'] for item in results['magnitude_data'] if item['abs_adj'] > 0]
    log2_vals = [item['log2_abs_adj'] for item in results['magnitude_data'] if item['abs_adj'] > 0]

    if len(n_vals) > 1:
        n_mean = mean(n_vals)
        log2_mean = mean(log2_vals)

        numerator = sum((n - n_mean) * (log2 - log2_mean) for n, log2 in zip(n_vals, log2_vals))
        denominator = sum((n - n_mean) ** 2 for n in n_vals)

        slope = numerator / denominator if denominator != 0 else 0
        intercept = log2_mean - slope * n_mean

        # Compute R^2
        ss_tot = sum((log2 - log2_mean) ** 2 for log2 in log2_vals)
        ss_res = sum((log2 - (slope * n + intercept)) ** 2 for n, log2 in zip(n_vals, log2_vals))
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

        results['regression'] = {
            'slope': slope,
            'intercept': intercept,
            'r_squared': r_squared,
            'formula': f'log2(|adj[n]|) ≈ {slope:.4f}*n + {intercept:.4f}',
            'theoretical_slope': 1.0,  # If adj grows as O(2^n)
            'deviation_from_theoretical': abs(slope - 1.0)
        }

    # 12.3 & 12.4: Deviation patterns
    if 'slope' in results['regression'] and 'intercept' in results['regression']:
        slope = results['regression']['slope']
        intercept = results['regression']['intercept']

        deviations = []
        for item in results['magnitude_data']:
            if item['abs_adj'] > 0:
                n = item['n']
                log2_actual = item['log2_abs_adj']
                log2_predicted = slope * n + intercept
                deviation = log2_actual - log2_predicted

                deviations.append({
                    'n': n,
                    'deviation': deviation,
                    'abs_deviation': abs(deviation)
                })

        results['deviation_analysis'] = {
            'mean_abs_deviation': mean([d['abs_deviation'] for d in deviations]),
            'max_abs_deviation': max([d['abs_deviation'] for d in deviations]),
            'deviations': deviations
        }

        # Find patterns in deviations
        positive_dev = [d for d in deviations if d['deviation'] > 0.5]
        negative_dev = [d for d in deviations if d['deviation'] < -0.5]

        results['growth_pattern'] = {
            'above_expected_count': len(positive_dev),
            'below_expected_count': len(negative_dev),
            'above_expected_n': [d['n'] for d in positive_dev],
            'below_expected_n': [d['n'] for d in negative_dev],
            'interpretation': 'Values with |deviation| > 0.5 indicate significant departure from exponential growth'
        }

    return results

def write_markdown_report(ratio_results: Dict, magnitude_results: Dict, output_file: str):
    """Write combined analysis to markdown file."""

    with open(output_file, 'w') as f:
        f.write("# Combined Ratio and Magnitude Growth Analysis\n\n")
        f.write("**Analysis Date:** 2025-12-21\n\n")
        f.write("**Project:** Bitcoin Puzzle Analysis - k-value sequence analysis\n\n")

        f.write("---\n\n")

        # TASK 10: RATIO ANALYSIS
        f.write("## Task 10: Ratio Analysis (k[n]/k[n-1])\n\n")

        f.write("### 10.1 Ratio Values (n=2 to n=70)\n\n")
        f.write("Computed r[n] = k[n]/k[n-1] for all consecutive pairs.\n\n")
        f.write(f"**Total ratios computed:** {len(ratio_results['ratios'])}\n\n")

        # Sample first 20 ratios
        f.write("#### Sample Ratios (n=2 to n=21)\n\n")
        f.write("| n | k[n] | k[n-1] | r[n] = k[n]/k[n-1] |\n")
        f.write("|---|------|--------|--------------------|\n")
        for n in range(2, min(22, 71)):
            if n in ratio_results['ratios']:
                data = ratio_results['ratios'][n]
                f.write(f"| {n} | {data['k_n']} | {data['k_n_minus_1']} | {data['decimal']:.6f} |\n")
        f.write("\n")

        # 10.2 Continued Fractions
        f.write("### 10.2 Continued Fraction Representations\n\n")
        f.write("Continued fraction expansion of k[n]/k[n-1] for n=2 to n=21:\n\n")

        for n in sorted(ratio_results['continued_fractions'].keys()):
            cf_data = ratio_results['continued_fractions'][n]
            cf = cf_data['cf']
            f.write(f"**n={n}:** [{', '.join(map(str, cf))}]\n")

            # Show convergents
            convergents = cf_data['convergents']
            if convergents:
                f.write(f"  - Convergents: ")
                conv_strs = [f"{p}/{q}" for p, q in convergents]
                f.write(", ".join(conv_strs) + "\n")
            f.write("\n")

        # 10.3 Convergence to 2
        f.write("### 10.3 Convergence Analysis: Do Ratios Approach 2?\n\n")

        stats = ratio_results['ratio_stats']
        f.write("#### Overall Statistics\n\n")
        f.write(f"- **Mean ratio:** {stats['mean']:.6f}\n")
        f.write(f"- **Standard deviation:** {stats['stdev']:.6f}\n")
        f.write(f"- **Median ratio:** {stats['median']:.6f}\n")
        f.write(f"- **Min ratio:** {stats['min']:.6f}\n")
        f.write(f"- **Max ratio:** {stats['max']:.6f}\n")
        f.write(f"- **Deviation from 2.0:** {abs(stats['mean'] - 2.0):.6f}\n\n")

        f.write("#### Windowed Analysis (10-value windows)\n\n")
        f.write("| Window | Mean Ratio | Deviation from 2.0 | StDev |\n")
        f.write("|--------|------------|-------------------|-------|\n")
        for window_name, window_data in sorted(ratio_results['convergence_to_2'].items()):
            f.write(f"| {window_name} | {window_data['mean']:.6f} | {window_data['deviation_from_2']:.6f} | {window_data['stdev']:.6f} |\n")
        f.write("\n")

        interpretation = "**Interpretation:** "
        if abs(stats['mean'] - 2.0) < 0.1:
            interpretation += "Ratios are very close to 2.0 on average, suggesting near-exponential doubling."
        elif abs(stats['mean'] - 2.0) < 0.5:
            interpretation += "Ratios are reasonably close to 2.0, with some variation."
        else:
            interpretation += "Ratios deviate significantly from 2.0, indicating non-uniform growth."
        f.write(interpretation + "\n\n")

        # 10.4 Growth Analysis
        f.write("### 10.4 Correlation with 2^n Growth\n\n")

        growth = ratio_results['growth_analysis']
        reg = growth['linear_regression']

        f.write("#### Linear Regression: log2(k[n]) vs n\n\n")
        f.write(f"**Formula:** {reg['interpretation']}\n\n")
        f.write(f"- **Slope:** {reg['slope']:.6f}\n")
        f.write(f"- **Intercept:** {reg['intercept']:.6f}\n")
        f.write(f"- **Theoretical slope (if k[n] = 2^n):** {reg['theoretical_slope']:.6f}\n")
        f.write(f"- **Deviation from theoretical:** {reg['deviation_from_theoretical']:.6f}\n\n")

        if abs(reg['slope'] - 1.0) < 0.05:
            f.write("**Interpretation:** Slope is very close to 1.0, confirming k[n] grows approximately as 2^n.\n\n")
        else:
            f.write(f"**Interpretation:** Slope of {reg['slope']:.4f} indicates growth rate is {reg['slope']/1.0:.2f}x the exponential base-2 rate.\n\n")

        # Sample log2 deviations
        f.write("#### Sample log2(k[n]) Deviations from n (n=1 to n=20)\n\n")
        f.write("| n | log2(k[n]) | Theoretical (n) | Deviation |\n")
        f.write("|---|------------|-----------------|----------|\n")
        for item in growth['log2_k_vs_n'][:20]:
            f.write(f"| {item['n']} | {item['log2_k']:.4f} | {item['theoretical_log2']} | {item['deviation']:+.4f} |\n")
        f.write("\n")

        f.write("---\n\n")

        # TASK 12: MAGNITUDE ANALYSIS
        f.write("## Task 12: Magnitude Growth Analysis (adj[n])\n\n")

        f.write("### 12.1 Magnitude Data: log2(|adj[n]|) for n=4 to n=70\n\n")
        f.write(f"**Total data points:** {len(magnitude_results['magnitude_data'])}\n\n")

        # Sample magnitude data
        f.write("#### Sample Data (n=4 to n=23)\n\n")
        f.write("| n | adj[n] | |adj[n]| | log2(|adj[n]|) | Sign |\n")
        f.write("|---|--------|----------|----------------|------|\n")
        for item in magnitude_results['magnitude_data'][:20]:
            if item['abs_adj'] > 0:
                f.write(f"| {item['n']} | {item['adj']} | {item['abs_adj']} | {item['log2_abs_adj']:.4f} | {item['sign']} |\n")
        f.write("\n")

        # 12.2 Linear Regression
        f.write("### 12.2 Linear Regression: log2(|adj[n]|) vs n\n\n")

        if 'slope' in magnitude_results['regression']:
            reg = magnitude_results['regression']
            f.write(f"**Formula:** {reg['formula']}\n\n")
            f.write(f"- **Slope:** {reg['slope']:.6f}\n")
            f.write(f"- **Intercept:** {reg['intercept']:.6f}\n")
            f.write(f"- **R² (goodness of fit):** {reg['r_squared']:.6f}\n")
            f.write(f"- **Theoretical slope (if adj grows as O(2^n)):** {reg['theoretical_slope']:.6f}\n")
            f.write(f"- **Deviation from theoretical:** {reg['deviation_from_theoretical']:.6f}\n\n")

        # 12.3 Comparison with theoretical
        f.write("### 12.3 Comparison with Theoretical O(2^n) Growth\n\n")

        if 'slope' in magnitude_results['regression']:
            slope = magnitude_results['regression']['slope']

            if abs(slope - 1.0) < 0.1:
                f.write(f"**Result:** Slope of {slope:.4f} is very close to 1.0, confirming |adj[n]| grows approximately as O(2^n).\n\n")
            else:
                growth_rate = 2 ** slope
                f.write(f"**Result:** Slope of {slope:.4f} indicates |adj[n]| grows as O({growth_rate:.4f}^n) rather than O(2^n).\n\n")

            r2 = magnitude_results['regression']['r_squared']
            if r2 > 0.95:
                f.write(f"**Fit Quality:** R² = {r2:.6f} indicates excellent exponential fit.\n\n")
            elif r2 > 0.85:
                f.write(f"**Fit Quality:** R² = {r2:.6f} indicates good exponential fit with some variation.\n\n")
            else:
                f.write(f"**Fit Quality:** R² = {r2:.6f} indicates poor exponential fit - significant non-exponential patterns present.\n\n")

        # 12.4 Deviation Patterns
        f.write("### 12.4 Deviation Patterns from Exponential Growth\n\n")

        if 'mean_abs_deviation' in magnitude_results['deviation_analysis']:
            dev_analysis = magnitude_results['deviation_analysis']
            f.write(f"- **Mean absolute deviation:** {dev_analysis['mean_abs_deviation']:.4f}\n")
            f.write(f"- **Max absolute deviation:** {dev_analysis['max_abs_deviation']:.4f}\n\n")

            # Pattern analysis
            pattern = magnitude_results['growth_pattern']
            f.write("#### Significant Deviations (|deviation| > 0.5)\n\n")
            f.write(f"- **Values above expected:** {pattern['above_expected_count']}\n")
            f.write(f"  - Puzzle IDs: {pattern['above_expected_n']}\n\n")
            f.write(f"- **Values below expected:** {pattern['below_expected_count']}\n")
            f.write(f"  - Puzzle IDs: {pattern['below_expected_n']}\n\n")
            f.write(f"**Note:** {pattern['interpretation']}\n\n")

            # Top 10 deviations
            f.write("#### Top 10 Largest Deviations\n\n")
            deviations = sorted(dev_analysis['deviations'], key=lambda x: x['abs_deviation'], reverse=True)[:10]
            f.write("| Rank | n | Deviation | Direction |\n")
            f.write("|------|---|-----------|----------|\n")
            for rank, dev in enumerate(deviations, 1):
                direction = "Above" if dev['deviation'] > 0 else "Below"
                f.write(f"| {rank} | {dev['n']} | {dev['deviation']:+.4f} | {direction} |\n")
            f.write("\n")

        f.write("---\n\n")

        # COMBINED INSIGHTS
        f.write("## Combined Insights\n\n")

        f.write("### Key Findings\n\n")

        ratio_mean = ratio_results['ratio_stats']['mean']
        growth_slope = ratio_results['growth_analysis']['linear_regression']['slope']
        adj_slope = magnitude_results['regression'].get('slope', 0)

        f.write(f"1. **k-value growth rate:**\n")
        f.write(f"   - Average ratio k[n]/k[n-1] = {ratio_mean:.4f}\n")
        f.write(f"   - Linear regression slope (log2 scale) = {growth_slope:.4f}\n")
        f.write(f"   - Interpretation: k-values grow at approximately 2^{growth_slope:.4f} per step\n\n")

        f.write(f"2. **adj-value magnitude growth:**\n")
        f.write(f"   - Linear regression slope (log2 scale) = {adj_slope:.4f}\n")
        f.write(f"   - Interpretation: |adj[n]| grows at approximately 2^{adj_slope:.4f} per step\n\n")

        f.write(f"3. **Relationship between k and adj growth:**\n")
        ratio_comparison = growth_slope / adj_slope if adj_slope != 0 else 0
        f.write(f"   - Growth rate ratio: k-slope / adj-slope = {ratio_comparison:.4f}\n")

        if abs(growth_slope - adj_slope) < 0.1:
            f.write(f"   - **Both grow at similar exponential rates**, suggesting adj is a significant component of k-value jumps.\n\n")
        else:
            f.write(f"   - **Different growth rates**, indicating k-values are dominated by the recurrence term 2*k[n-1] rather than adj[n].\n\n")

        # Formula reminder
        f.write("### Formula Context\n\n")
        f.write("Recall the fundamental formula:\n\n")
        f.write("```\n")
        f.write("k[n] = 2*k[n-1] + adj[n]\n")
        f.write("adj[n] = 2^n - m[n] * k[d[n]]\n")
        f.write("```\n\n")

        f.write("This analysis shows:\n")
        f.write(f"- The 2*k[n-1] term dominates (exponential with base ~2^{growth_slope:.3f})\n")
        f.write(f"- The adj[n] term provides adjustments (exponential with base ~2^{adj_slope:.3f})\n")
        f.write(f"- Deviations in adj growth reveal where m[n] selection creates unusual corrections\n\n")

        f.write("---\n\n")
        f.write("**Analysis complete.** All numerical results have been computed from database values.\n")

def main():
    print("=" * 80)
    print("COMBINED TASKS 10 & 12: RATIO ANALYSIS AND MAGNITUDE GROWTH")
    print("=" * 80)
    print()

    # Load data
    print("Loading k-values from database...")
    k_values = load_k_values()
    print(f"Loaded {len(k_values)} k-values (n=1 to n=70)")

    print("\nLoading m-sequence and adj-sequence from data_for_csolver.json...")
    m_dict, adj_dict = load_m_and_adj()
    print(f"Loaded {len(m_dict)} m-values")
    print(f"Loaded {len(adj_dict)} adj-values")

    print("\n" + "-" * 80)
    print("TASK 10: RATIO ANALYSIS")
    print("-" * 80)

    print("\nPerforming ratio analysis...")
    ratio_results = task_10_ratio_analysis(k_values)

    print(f"✓ Computed {len(ratio_results['ratios'])} ratios")
    print(f"✓ Generated {len(ratio_results['continued_fractions'])} continued fractions")
    print(f"✓ Mean ratio: {ratio_results['ratio_stats']['mean']:.6f}")
    print(f"✓ Growth slope (log2 scale): {ratio_results['growth_analysis']['linear_regression']['slope']:.6f}")

    print("\n" + "-" * 80)
    print("TASK 12: MAGNITUDE GROWTH ANALYSIS")
    print("-" * 80)

    print("\nPerforming magnitude analysis...")
    magnitude_results = task_12_magnitude_analysis(adj_dict)

    print(f"✓ Analyzed {len(magnitude_results['magnitude_data'])} adj values")
    if 'slope' in magnitude_results['regression']:
        print(f"✓ Regression slope (log2 scale): {magnitude_results['regression']['slope']:.6f}")
        print(f"✓ R² fit quality: {magnitude_results['regression']['r_squared']:.6f}")
        print(f"✓ Mean absolute deviation: {magnitude_results['deviation_analysis']['mean_abs_deviation']:.4f}")

    print("\n" + "-" * 80)
    print("WRITING REPORT")
    print("-" * 80)

    output_file = '/home/rkh/ladder/ratio_magnitude_analysis.md'
    write_markdown_report(ratio_results, magnitude_results, output_file)

    print(f"\n✓ Report written to: {output_file}")

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)

    # Summary
    print("\nKEY FINDINGS:")
    print(f"  - Average k[n]/k[n-1] ratio: {ratio_results['ratio_stats']['mean']:.4f}")
    print(f"  - k-value growth: 2^{ratio_results['growth_analysis']['linear_regression']['slope']:.4f} per step")
    print(f"  - adj-value growth: 2^{magnitude_results['regression']['slope']:.4f} per step")
    print(f"  - Regression fit (R²): {magnitude_results['regression']['r_squared']:.4f}")
    print()

if __name__ == '__main__':
    main()
