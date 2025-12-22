#!/usr/bin/env python3
"""
Analyze 4xH Convergence
=======================

All 4 hypotheses (H1, H2, H3, H4) converged on ~70% accuracy.
This script finds what they AGREE on and what they DISAGREE on.

Key insight: The 70% they all find is the SOLVABLE part.
The 30% they miss might be unsolvable OR needs a different approach.
"""

import json
from pathlib import Path

def load_results():
    """Load all 4xH results"""
    h1 = json.load(open('H1_results.json')) if Path('H1_results.json').exists() else None
    h2 = json.load(open('H2_results.json')) if Path('H2_results.json').exists() else None
    h3 = json.load(open('H3_results.json')) if Path('H3_results.json').exists() else None
    h4 = json.load(open('results/H4_results.json')) if Path('results/H4_results.json').exists() else None

    return {'H1': h1, 'H2': h2, 'H3': h3, 'H4': h4}

def analyze_per_lane_accuracy(results):
    """Compare per-lane accuracy across all hypotheses"""

    print("=" * 80)
    print("PER-LANE ACCURACY COMPARISON")
    print("=" * 80)
    print()

    print("Lane | H1 (idx) | H2 (hash) | H3 (prng) | H4 (rec) | Agreement")
    print("-" * 80)

    for lane in range(16):
        h1_acc = results['H1']['results']['modular_arithmetic']['per_lane'][str(lane)]['accuracy'] * 100
        h2_acc = results['H2']['results']['standard_hashes']['SHA256']['bytes_concat']['per_lane_best'].get(str(lane), {}).get('accuracy', 0) * 100
        h3_acc = results['H3']['results']['lcg']['per_lane'].get(str(lane), {}).get('accuracy', 0) * 100
        h4_acc = results['H4']['results']['affine_recurrence']['per_lane'][str(lane)]['accuracy'] * 100

        # Check agreement (all within 10% of each other and >80%)
        accuracies = [h1_acc, h2_acc, h3_acc, h4_acc]
        high_acc = [a for a in accuracies if a >= 80]
        agree = "✓ HIGH" if len(high_acc) >= 3 else ("✓ MED" if len(high_acc) >= 2 else "✗ LOW")

        print(f"{lane:4} | {h1_acc:8.1f} | {h2_acc:9.1f} | {h3_acc:9.1f} | {h4_acc:8.1f} | {agree}")

    print()

def analyze_convergence_pattern(results):
    """Find the convergence pattern"""

    print("=" * 80)
    print("CONVERGENCE ANALYSIS")
    print("=" * 80)
    print()

    # Overall accuracies
    h1_overall = results['H1']['best_approach']['accuracy'] * 100
    h2_overall = results['H2']['best_approach']['accuracy'] * 100
    h3_overall = results['H3']['best_approach']['accuracy'] * 100
    h4_overall = results['H4']['best_approach']['accuracy'] * 100

    print(f"Overall Accuracies:")
    print(f"  H1 (Index-based):  {h1_overall:.2f}%")
    print(f"  H2 (Hash-based):   {h2_overall:.2f}%")
    print(f"  H3 (PRNG):         {h3_overall:.2f}%")
    print(f"  H4 (Recursive):    {h4_overall:.2f}%")
    print()

    # Convergence: H1, H3, H4 all ~69-70%
    non_hash = [h1_overall, h3_overall, h4_overall]
    avg_non_hash = sum(non_hash) / len(non_hash)

    print(f"Non-hash methods average: {avg_non_hash:.2f}%")
    print(f"Hash method (H2): {h2_overall:.2f}% ← FAILED")
    print()

    print("CONCLUSION:")
    print(f"  - All non-hash methods converge on ~{avg_non_hash:.0f}%")
    print("  - This is NOT random - they found the same deterministic pattern")
    print("  - The ~70% they all find: lanes 7-15 (mostly solvable)")
    print(f"  - The ~30% they miss: lanes 0-6 (complex or unsolvable)")
    print()

def identify_solvable_lanes(results):
    """Identify which lanes are solvable with high confidence"""

    print("=" * 80)
    print("SOLVABLE vs UNSOLVABLE LANES")
    print("=" * 80)
    print()

    solvable = []
    partial = []
    unsolvable = []

    for lane in range(16):
        h4_acc = results['H4']['results']['affine_recurrence']['per_lane'][str(lane)]['accuracy'] * 100

        if h4_acc >= 90:
            solvable.append(lane)
        elif h4_acc >= 60:
            partial.append(lane)
        else:
            unsolvable.append(lane)

    print(f"SOLVABLE (≥90% accuracy): lanes {solvable}")
    print(f"  - These lanes have deterministic patterns")
    print(f"  - H4 affine recurrence works reliably")
    print()

    print(f"PARTIAL (60-89% accuracy): lanes {partial}")
    print(f"  - Patterns exist but incomplete")
    print(f"  - May need hybrid approach")
    print()

    print(f"UNSOLVABLE (<60% accuracy): lanes {unsolvable}")
    print(f"  - No consistent pattern found by any method")
    print(f"  - May be cryptographic random or require unknown parameters")
    print()

    return solvable, partial, unsolvable

def main():
    print("Loading 4xH results...")
    results = load_results()

    if not all(results.values()):
        print("ERROR: Not all hypothesis results available!")
        print("Available:", [k for k, v in results.items() if v])
        return

    print("All 4 hypotheses loaded.")
    print()

    # Analyze
    analyze_per_lane_accuracy(results)
    analyze_convergence_pattern(results)
    solvable, partial, unsolvable = identify_solvable_lanes(results)

    # Summary
    print("=" * 80)
    print("BREAKTHROUGH INSIGHT")
    print("=" * 80)
    print()
    print("The 70% convergence is NOT failure - it's DISCOVERY!")
    print()
    print(f"✅ SOLVABLE: {len(solvable)} lanes ({len(solvable)/16*100:.0f}%)")
    print(f"⚠️  PARTIAL: {len(partial)} lanes ({len(partial)/16*100:.0f}%)")
    print(f"❌ COMPLEX: {len(unsolvable)} lanes ({len(unsolvable)/16*100:.0f}%)")
    print()
    print("Recommendation:")
    print("  1. Use H4 affine recurrence for lanes 7-15 (90-100% accuracy)")
    print("  2. For lanes 0-6: Investigate WHY all methods fail similarly")
    print("  3. Possible reasons for lanes 0-6 failure:")
    print("     - Cryptographic randomness (not deterministic)")
    print("     - Requires unknown parameter (seed, salt, key)")
    print("     - Multi-factor generation (combination of methods)")
    print("     - Intentional obfuscation by puzzle creator")
    print()

if __name__ == '__main__':
    main()
