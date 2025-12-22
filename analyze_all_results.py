#!/usr/bin/env python3
"""
Analyze All Research Results

Collects and compares results from all 4 hypotheses:
- H1: Index-Based Generator
- H2: Cryptographic Hash Function
- H3: PRNG
- H4: Recursive Pattern

Outputs:
- Ranked list of approaches
- Best overall hypothesis
- Recommendations for next steps
"""

import json
from pathlib import Path
from datetime import datetime

def load_result(filepath):
    """Load a result file if it exists"""
    path = Path(filepath)
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return None

def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def analyze_h1(result):
    """Analyze H1 results"""
    if not result:
        return None

    best = result['best_approach']
    return {
        'hypothesis': 'H1: Index-Based',
        'best_method': best['name'],
        'accuracy': best['accuracy'],
        'conclusion': result['conclusion'],
        'details': result['results']
    }

def analyze_h2(result):
    """Analyze H2 results"""
    if not result:
        return None

    best = result['best_approach']
    return {
        'hypothesis': 'H2: Hash Function',
        'best_method': best['name'],
        'accuracy': best['accuracy'],
        'conclusion': result['conclusion'],
        'details': result['results']
    }

def analyze_h3(result):
    """Analyze H3 results"""
    if not result:
        return None

    best = result['best_approach']
    return {
        'hypothesis': 'H3: PRNG',
        'best_method': best['name'],
        'accuracy': best['accuracy'],
        'conclusion': result['conclusion'],
        'details': result['results']
    }

def analyze_h4(result):
    """Analyze H4 results"""
    if not result:
        return None

    best = result['best_approach']
    return {
        'hypothesis': 'H4: Recursive',
        'best_method': best['name'],
        'accuracy': best['accuracy'],
        'conclusion': result['conclusion'],
        'details': result['results']
    }

def rank_hypotheses(analyses):
    """Rank all hypotheses by accuracy"""
    valid = [a for a in analyses if a is not None]
    return sorted(valid, key=lambda x: x['accuracy'], reverse=True)

def print_summary_table(ranked):
    """Print a summary table of all results"""
    print_header("RESEARCH RESULTS SUMMARY")

    print(f"\n{'Rank':<6} {'Hypothesis':<20} {'Best Method':<25} {'Accuracy':<12} {'Status'}")
    print("-" * 70)

    for i, result in enumerate(ranked, 1):
        status_emoji = {
            'SUCCESS': '🎉',
            'PROMISING': '🔥',
            'PARTIAL': '👍',
            'FAILED': '❌'
        }.get(result['conclusion'], '❓')

        print(f"{i:<6} {result['hypothesis']:<20} {result['best_method']:<25} "
              f"{result['accuracy']*100:>6.2f}%    {status_emoji} {result['conclusion']}")

def generate_recommendations(ranked):
    """Generate recommendations based on results"""
    print_header("RECOMMENDATIONS")

    if not ranked:
        print("\n❌ No results available. Run research scripts first.")
        return

    best = ranked[0]

    if best['accuracy'] == 1.0:
        print("\n🎉🎉🎉 SUCCESS! We found the drift generator! 🎉🎉🎉\n")
        print(f"Generator: {best['hypothesis']}")
        print(f"Method:    {best['best_method']}")
        print(f"Accuracy:  100%\n")
        print("NEXT STEPS:")
        print("1. Verify the formula on all 69 transitions")
        print("2. Use the formula to predict puzzles 71-95")
        print("3. Validate predictions against known bridge puzzles")
        print("4. If validated, generate puzzles 96-160")
        print("5. Document the complete generator formula")

    elif best['accuracy'] > 0.9:
        print(f"\n🔥 Very promising result! {best['hypothesis']} achieved {best['accuracy']*100:.1f}%\n")
        print("NEXT STEPS:")
        print("1. Investigate why remaining ~10% don't match")
        print("2. Look for patterns in the mismatches")
        print("3. Try hybrid approaches:")

        # Suggest combinations
        if len(ranked) >= 2:
            second_best = ranked[1]
            print(f"   - Combine {best['hypothesis']} with {second_best['hypothesis']}")
            print(f"   - Use {best['hypothesis']} as primary, {second_best['hypothesis']} for edge cases")

        print("4. Refine the winning hypothesis with more sophisticated analysis")

    elif best['accuracy'] > 0.7:
        print(f"\n👍 Partial success with {best['hypothesis']} ({best['accuracy']*100:.1f}%)\n")
        print("NEXT STEPS:")
        print("1. Analyze which lanes/transitions have lower accuracy")
        print("2. Try combining multiple hypotheses:")

        for i, result in enumerate(ranked[:3], 1):
            print(f"   {i}. {result['hypothesis']} ({result['accuracy']*100:.1f}%)")

        print("3. Consider more complex models:")
        print("   - Hybrid: Different generators for different lanes")
        print("   - Context-dependent: Generator changes based on puzzle number ranges")
        print("   - Multi-factor: Combine (k, lane, X_k) as inputs")

    else:
        print(f"\n🤔 All hypotheses showed limited success (best: {best['accuracy']*100:.1f}%)\n")
        print("NEXT STEPS:")
        print("1. The drift generator may be more complex than tested")
        print("2. Consider advanced approaches:")
        print("   - Machine learning (neural networks, transformers)")
        print("   - Genetic algorithms")
        print("   - Symbolic regression with more features")
        print("   - Manual cryptanalysis of drift patterns")
        print("3. Re-examine the data:")
        print("   - Verify calibration file correctness")
        print("   - Check for data preprocessing needs")
        print("   - Look for hidden dependencies in the data")

def generate_detailed_report(ranked):
    """Generate detailed JSON report"""
    report = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total_hypotheses_tested': len(ranked),
            'best_hypothesis': ranked[0]['hypothesis'] if ranked else None,
            'best_accuracy': ranked[0]['accuracy'] if ranked else 0.0,
            'winner': ranked[0]['conclusion'] if ranked else 'NONE'
        },
        'ranked_results': ranked,
        'recommendations': 'See console output'
    }

    output_path = Path("analysis_report.json")
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n📄 Detailed report saved to: {output_path}")

def main():
    print_header("DRIFT GENERATOR RESEARCH - RESULTS ANALYSIS")
    print(f"\nAnalysis timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Load all results
    print("Loading research results...")
    h1_result = load_result("H1_results.json")
    h2_result = load_result("H2_results.json")
    h3_result = load_result("H3_results.json")
    h4_result = load_result("H4_results.json")

    # Check what's available
    available = []
    if h1_result:
        available.append("H1 ✓")
    if h2_result:
        available.append("H2 ✓")
    if h3_result:
        available.append("H3 ✓")
    if h4_result:
        available.append("H4 ✓")

    if not available:
        print("\n❌ No result files found!")
        print("\nPlease run the research scripts first:")
        print("  python3 research_H1_index_based.py")
        print("  python3 research_H2_hash_function.py")
        print("  python3 research_H3_prng.py")
        print("  python3 research_H4_recursive.py")
        return

    print(f"Available results: {', '.join(available)}\n")

    # Analyze each hypothesis
    analyses = [
        analyze_h1(h1_result),
        analyze_h2(h2_result),
        analyze_h3(h3_result),
        analyze_h4(h4_result)
    ]

    # Rank by accuracy
    ranked = rank_hypotheses(analyses)

    # Print summary table
    print_summary_table(ranked)

    # Generate recommendations
    generate_recommendations(ranked)

    # Save detailed report
    generate_detailed_report(ranked)

    print_header("ANALYSIS COMPLETE")

    if ranked and ranked[0]['accuracy'] == 1.0:
        print("\n🎉 CONGRATULATIONS! The drift generator has been discovered!")
        print(f"\nWinning approach: {ranked[0]['hypothesis']} - {ranked[0]['best_method']}")
        print("\nYou can now generate ALL Bitcoin puzzles 1-160! 🚀\n")
    elif ranked and ranked[0]['accuracy'] > 0.9:
        print("\n🔥 Very close! Keep refining the winning hypothesis.")
    else:
        print("\n📊 Results collected. Review recommendations above.")

if __name__ == '__main__':
    main()
