#!/usr/bin/env python3
"""
Puzzle CLI - Command line tool for Bitcoin Puzzle analysis
Puzzle-agnostic: works with ANY target puzzle number

Usage:
    python puzzle_cli.py status          # Show current target and status
    python puzzle_cli.py target 72       # Set target to puzzle 72
    python puzzle_cli.py analyze         # Analyze current target
    python puzzle_cli.py solved N KEY   # Mark puzzle N as solved with KEY
    python puzzle_cli.py predict         # Show search predictions
"""
import sys
import json
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.puzzle_utils import PuzzleConfig, get_puzzle_summary


def cmd_status(args):
    """Show current status"""
    config = PuzzleConfig()
    target = config.get_target_puzzle()
    last_n, last_key = config.get_last_solved_key()

    print("=" * 60)
    print("BITCOIN PUZZLE STATUS")
    print("=" * 60)
    print(f"Current target:  Puzzle {target}")
    print(f"Last solved:     Puzzle {last_n}")
    print(f"k{last_n} =          {last_key}")
    print(f"k{last_n} position:  {config.get_position(last_n):.2f}%")
    print()

    low, high = config.get_range(target)
    print(f"Puzzle {target} range:")
    print(f"  Min: {low}")
    print(f"  Max: {high}")
    print(f"  Bits: {target}")
    print("=" * 60)


def cmd_target(args):
    """Set target puzzle"""
    config = PuzzleConfig()
    n = int(args.puzzle)

    if n in config.solved_puzzles:
        print(f"Warning: Puzzle {n} is already solved!")
        print(f"Key: {config.get_key(n)}")
        confirm = input("Set as target anyway? (y/n): ")
        if confirm.lower() != 'y':
            return

    config.set_target_puzzle(n)
    print(f"Target set to puzzle {n}")

    low, high = config.get_range(n)
    print(f"\nPuzzle {n} range: [{low}, {high}]")


def cmd_solved(args):
    """Mark puzzle as solved"""
    config = PuzzleConfig()
    n = int(args.puzzle)
    key = int(args.key)

    # Validate key is in range
    low, high = config.get_range(n)
    if not (low <= key <= high):
        print(f"ERROR: Key {key} is NOT in valid range [{low}, {high}]")
        return

    config.mark_solved(n, key)
    pos = config.get_position(n, key)

    print(f"Puzzle {n} marked as SOLVED!")
    print(f"Key: {key}")
    print(f"Position: {pos:.4f}%")
    print(f"\nNext target: Puzzle {config.get_target_puzzle()}")


def cmd_analyze(args):
    """Analyze target puzzle"""
    print(get_puzzle_summary(args.puzzle if hasattr(args, 'puzzle') and args.puzzle else None))


def cmd_predict(args):
    """Show search predictions"""
    config = PuzzleConfig()
    n = args.puzzle if hasattr(args, 'puzzle') and args.puzzle else config.get_target_puzzle()

    pred = config.predict_search_region(n)

    print("=" * 60)
    print(f"SEARCH PREDICTIONS - PUZZLE {n}")
    print("=" * 60)
    print(f"Range: {n}-bit keys")
    print(f"  Min: {pred['range']['low']}")
    print(f"  Max: {pred['range']['high']}")
    print()

    for i, s in enumerate(pred["strategies"], 1):
        print(f"Strategy {i}: {s['name']}")
        print(f"  Priority: {s['priority']}")
        if 'range_start' in s:
            print(f"  Range: [{s['range_start']}, {s.get('range_end', '...')}]")
        if 'first_candidate' in s:
            print(f"  First candidate: {s['first_candidate']}")
        print(f"  Rationale: {s['rationale']}")
        print()


def cmd_keys(args):
    """List known keys"""
    config = PuzzleConfig()
    start = args.start if hasattr(args, 'start') and args.start else 1
    end = args.end if hasattr(args, 'end') and args.end else 70

    print(f"Known keys (puzzles {start}-{end}):")
    print("-" * 50)
    for n in range(start, end + 1):
        key = config.get_key(n)
        if key:
            pos = config.get_position(n, key)
            status = "B" if n in config.bridge_keys else " "
            print(f"k{n:3} = {key:>25} ({pos:6.2f}%) {status}")


def main():
    parser = argparse.ArgumentParser(description="Bitcoin Puzzle CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # status
    subparsers.add_parser("status", help="Show current status")

    # target
    p_target = subparsers.add_parser("target", help="Set target puzzle")
    p_target.add_argument("puzzle", type=int, help="Puzzle number")

    # solved
    p_solved = subparsers.add_parser("solved", help="Mark puzzle as solved")
    p_solved.add_argument("puzzle", type=int, help="Puzzle number")
    p_solved.add_argument("key", type=int, help="Private key value")

    # analyze
    p_analyze = subparsers.add_parser("analyze", help="Analyze puzzle")
    p_analyze.add_argument("puzzle", type=int, nargs="?", help="Puzzle number (default: current target)")

    # predict
    p_predict = subparsers.add_parser("predict", help="Show search predictions")
    p_predict.add_argument("puzzle", type=int, nargs="?", help="Puzzle number (default: current target)")

    # keys
    p_keys = subparsers.add_parser("keys", help="List known keys")
    p_keys.add_argument("--start", type=int, default=1, help="Start puzzle")
    p_keys.add_argument("--end", type=int, default=70, help="End puzzle")

    args = parser.parse_args()

    if args.command == "status":
        cmd_status(args)
    elif args.command == "target":
        cmd_target(args)
    elif args.command == "solved":
        cmd_solved(args)
    elif args.command == "analyze":
        cmd_analyze(args)
    elif args.command == "predict":
        cmd_predict(args)
    elif args.command == "keys":
        cmd_keys(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
