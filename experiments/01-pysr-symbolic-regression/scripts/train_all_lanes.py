#!/usr/bin/env python3
"""
Phase 3.2: Train PySR on all 16 lanes

Discovers symbolic formulas for all lanes in sequence.
Saves checkpoints after each lane.
"""

import argparse
import json
import time
from pathlib import Path
from train_single_lane import train_lane

def train_all_lanes(iterations=1000, start_lane=0, end_lane=15, verbose=True):
    """Train all lanes from start_lane to end_lane."""
    print("=" * 70)
    print("Phase 3.2: Training All Lanes - Symbolic Regression")
    print("=" * 70)
    print(f"\nConfiguration:")
    print(f"  Lanes to train: {start_lane} to {end_lane} ({end_lane - start_lane + 1} lanes)")
    print(f"  Iterations per lane: {iterations}")
    print(f"  Total estimated time: {(end_lane - start_lane + 1) * 45} - {(end_lane - start_lane + 1) * 60} minutes")
    print()

    results_summary = []
    successful = 0
    failed = 0

    start_time = time.time()

    for lane in range(start_lane, end_lane + 1):
        print(f"\n{'#' * 70}")
        print(f"# Training Lane {lane:02d}/{end_lane} ({lane - start_lane + 1}/{end_lane - start_lane + 1})")
        print(f"{'#' * 70}\n")

        lane_start = time.time()

        try:
            model, results = train_lane(lane, iterations, verbose)

            if results:
                results_summary.append(results)

                if results['accuracy'] >= 95.0:
                    successful += 1
                    print(f"\n✅ Lane {lane} SUCCESS - {results['accuracy']:.2f}% accuracy")
                else:
                    failed += 1
                    print(f"\n⚠️  Lane {lane} LOW ACCURACY - {results['accuracy']:.2f}%")

            lane_elapsed = time.time() - lane_start
            print(f"\n⏱️  Lane {lane} completed in {lane_elapsed/60:.1f} minutes")

        except Exception as e:
            print(f"\n❌ Lane {lane} FAILED with error: {e}")
            failed += 1
            results_summary.append({
                'lane': lane,
                'error': str(e),
                'accuracy': 0.0
            })

        # Progress summary
        total_elapsed = time.time() - start_time
        lanes_done = lane - start_lane + 1
        lanes_remaining = end_lane - lane
        avg_time_per_lane = total_elapsed / lanes_done
        estimated_remaining = avg_time_per_lane * lanes_remaining

        print(f"\n📊 Progress:")
        print(f"   Completed: {lanes_done}/{end_lane - start_lane + 1} lanes")
        print(f"   Successful: {successful} (≥95% accuracy)")
        print(f"   Low accuracy: {failed}")
        print(f"   Time elapsed: {total_elapsed/60:.1f} minutes")
        print(f"   Estimated remaining: {estimated_remaining/60:.1f} minutes")

    # Final summary
    total_time = time.time() - start_time

    print("\n" + "=" * 70)
    print("✅ ALL LANES TRAINING COMPLETE!")
    print("=" * 70)

    print(f"\n📊 Final Summary:")
    print(f"   Total lanes trained: {len(results_summary)}")
    print(f"   Successful (≥95%): {successful}")
    print(f"   Low accuracy (<95%): {failed}")
    print(f"   Total time: {total_time/60:.1f} minutes ({total_time/3600:.2f} hours)")

    # Save summary
    results_dir = Path(__file__).parent.parent / "results"
    summary_file = results_dir / "all_lanes_summary.json"

    summary = {
        'total_lanes': len(results_summary),
        'successful': successful,
        'failed': failed,
        'total_time_minutes': total_time / 60,
        'iterations_per_lane': iterations,
        'lanes': results_summary
    }

    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\n💾 Summary saved to: {summary_file}")

    # Display results table
    print(f"\n📋 Results Table:")
    print(f"{'Lane':<6} {'Equation':<30} {'Accuracy':<10} {'Loss':<12}")
    print("-" * 70)

    for r in results_summary:
        if 'error' not in r:
            eq = r['equation'][:28] + '..' if len(r['equation']) > 30 else r['equation']
            print(f"{r['lane']:<6} {eq:<30} {r['accuracy']:>8.2f}% {r['loss']:>10.6f}")
        else:
            print(f"{r['lane']:<6} {'ERROR':<30} {'0.00%':<10} {'-':<12}")

    # Recommendations
    print(f"\n🎯 Next Steps:")

    if successful == len(results_summary):
        print("   ✅ All lanes achieved ≥95% accuracy!")
        print("   → Proceed to Phase 4: Extract coefficients")
        print("   → Run: python3 scripts/extract_coefficients.py")
    elif successful >= len(results_summary) * 0.8:
        print(f"   ⚠️  {failed} lanes need improvement")
        print("   → Re-train low-accuracy lanes with more iterations")
        print(f"   → Run: python3 scripts/train_all_lanes.py --start-lane X --end-lane Y --iterations 2000")
    else:
        print(f"   ❌ Too many lanes failed ({failed}/{len(results_summary)})")
        print("   → Review approach or try different operators")
        print("   → Check data quality for failing lanes")

    return results_summary

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Train PySR on all 16 lanes")
    parser.add_argument('--iterations', type=int, default=1000,
                        help='Iterations per lane (default: 1000)')
    parser.add_argument('--start-lane', type=int, default=0,
                        help='Starting lane (default: 0)')
    parser.add_argument('--end-lane', type=int, default=15,
                        help='Ending lane (default: 15)')
    parser.add_argument('--quiet', action='store_true',
                        help='Reduce verbosity')

    args = parser.parse_args()

    if args.start_lane < 0 or args.start_lane > 15:
        print(f"❌ Start lane must be 0-15, got {args.start_lane}")
        return

    if args.end_lane < args.start_lane or args.end_lane > 15:
        print(f"❌ End lane must be {args.start_lane}-15, got {args.end_lane}")
        return

    print("\n⚠️  WARNING: This will take approximately 8-12 hours to complete")
    print("   You can safely stop and resume by adjusting --start-lane")
    print()

    response = input("Continue? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("❌ Cancelled")
        return

    results = train_all_lanes(
        iterations=args.iterations,
        start_lane=args.start_lane,
        end_lane=args.end_lane,
        verbose=not args.quiet
    )

    print("\n🎉 Training pipeline complete!")
    print(f"   Results saved to: experiments/01-pysr-symbolic-regression/results/")

if __name__ == "__main__":
    main()
