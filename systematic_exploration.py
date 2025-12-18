#!/usr/bin/env python3
"""
Systematic Formula Exploration for Bitcoin Puzzle Keys
======================================================
This script mathematically tests ~175K formula combinations and saves valid ones.
The actual computation is fast (pure math) - AI is only used to analyze interesting patterns.
Uses ALL 74 known keys from database.
"""

import sqlite3
import json
import time
import itertools
from datetime import datetime
from pathlib import Path
import puzzle_config  # Central config - all data from DB

# Database path
DB_PATH = "/home/solo/LA/formula_theories.db"

# Known keys - loaded from DB
KEYS = puzzle_config.KEYS  # All 74 known keys

# Parameters
BASE_KEYS = [2, 3, 4, 5, 6, 7, 8, 9]  # Keys to use as bases
MULTIPLIERS = list(range(1, 26))      # 1 to 25
CONSTANTS = list(range(-50, 101))      # -50 to 100

# Work assignments
ASSIGNMENTS = {
    'b-solver': [9, 10],   # k9=467, k10=514
    'c-solver': [12, 14]   # k12=2683, k14=10544
}

def get_db():
    """Get database connection"""
    return sqlite3.connect(DB_PATH)

def generate_type_a_formulas(target_n, target_value):
    """Type A: k_a × M + C"""
    formulas = []
    for k_idx in BASE_KEYS:
        if k_idx >= target_n:
            continue
        k_val = KEYS[k_idx]
        for m in MULTIPLIERS:
            for c in CONSTANTS:
                computed = k_val * m + c
                if computed == target_value:
                    formulas.append({
                        'type': 'A',
                        'formula': f'k{k_idx} × {m} + {c}',
                        'base_key': f'k{k_idx}',
                        'base_value': k_val,
                        'multiplier': m,
                        'constant': c,
                        'computed': computed,
                        'is_valid': True
                    })
    return formulas

def generate_type_b_formulas(target_n, target_value):
    """Type B: k_a × M + k_b"""
    formulas = []
    for k_a in BASE_KEYS:
        if k_a >= target_n:
            continue
        for k_b in BASE_KEYS:
            if k_b >= target_n or k_b == k_a:
                continue
            val_a = KEYS[k_a]
            val_b = KEYS[k_b]
            for m in MULTIPLIERS:
                computed = val_a * m + val_b
                if computed == target_value:
                    formulas.append({
                        'type': 'B',
                        'formula': f'k{k_a} × {m} + k{k_b}',
                        'base_key': f'k{k_a}',
                        'base_value': val_a,
                        'multiplier': m,
                        'second_key': f'k{k_b}',
                        'second_value': val_b,
                        'computed': computed,
                        'is_valid': True
                    })
    return formulas

def generate_type_c_formulas(target_n, target_value):
    """Type C: k_a × M - k_b"""
    formulas = []
    for k_a in BASE_KEYS:
        if k_a >= target_n:
            continue
        for k_b in BASE_KEYS:
            if k_b >= target_n or k_b == k_a:
                continue
            val_a = KEYS[k_a]
            val_b = KEYS[k_b]
            for m in MULTIPLIERS:
                computed = val_a * m - val_b
                if computed == target_value:
                    formulas.append({
                        'type': 'C',
                        'formula': f'k{k_a} × {m} - k{k_b}',
                        'base_key': f'k{k_a}',
                        'base_value': val_a,
                        'multiplier': m,
                        'second_key': f'k{k_b}',
                        'second_value': val_b,
                        'computed': computed,
                        'is_valid': True
                    })
    return formulas

def generate_type_d_formulas(target_n, target_value):
    """Type D: k_a² ± C"""
    formulas = []
    for k_idx in BASE_KEYS:
        if k_idx >= target_n:
            continue
        k_val = KEYS[k_idx]
        k_squared = k_val ** 2
        for c in CONSTANTS:
            # k_a² + C
            if k_squared + c == target_value:
                formulas.append({
                    'type': 'D',
                    'formula': f'k{k_idx}² + {c}',
                    'base_key': f'k{k_idx}',
                    'base_value': k_val,
                    'constant': c,
                    'computed': k_squared + c,
                    'is_valid': True
                })
            # k_a² - C
            if k_squared - c == target_value:
                formulas.append({
                    'type': 'D',
                    'formula': f'k{k_idx}² - {c}',
                    'base_key': f'k{k_idx}',
                    'base_value': k_val,
                    'constant': -c,
                    'computed': k_squared - c,
                    'is_valid': True
                })
    return formulas

def generate_type_e_formulas(target_n, target_value):
    """Type E: k_a × k_b ± C"""
    formulas = []
    key_pairs = list(itertools.combinations(BASE_KEYS, 2))
    for k_a, k_b in key_pairs:
        if k_a >= target_n or k_b >= target_n:
            continue
        val_a = KEYS[k_a]
        val_b = KEYS[k_b]
        product = val_a * val_b
        for c in CONSTANTS:
            # k_a × k_b + C
            if product + c == target_value:
                formulas.append({
                    'type': 'E',
                    'formula': f'k{k_a} × k{k_b} + {c}',
                    'base_key': f'k{k_a}',
                    'base_value': val_a,
                    'second_key': f'k{k_b}',
                    'second_value': val_b,
                    'constant': c,
                    'computed': product + c,
                    'is_valid': True
                })
            # k_a × k_b - C
            if product - c == target_value:
                formulas.append({
                    'type': 'E',
                    'formula': f'k{k_a} × k{k_b} - {c}',
                    'base_key': f'k{k_a}',
                    'base_value': val_a,
                    'second_key': f'k{k_b}',
                    'second_value': val_b,
                    'constant': -c,
                    'computed': product - c,
                    'is_valid': True
                })
    return formulas

def explore_target(target_n, explorer):
    """Explore all formula types for a target key"""
    target_value = KEYS[target_n]
    all_formulas = []

    print(f"\n{'='*60}")
    print(f"Exploring k{target_n} = {target_value}")
    print(f"Explorer: {explorer}")
    print(f"{'='*60}")

    # Type A
    t0 = time.time()
    formulas_a = generate_type_a_formulas(target_n, target_value)
    print(f"Type A (k×M+C): {len(formulas_a)} valid formulas found ({time.time()-t0:.2f}s)")
    all_formulas.extend(formulas_a)

    # Type B
    t0 = time.time()
    formulas_b = generate_type_b_formulas(target_n, target_value)
    print(f"Type B (k×M+k): {len(formulas_b)} valid formulas found ({time.time()-t0:.2f}s)")
    all_formulas.extend(formulas_b)

    # Type C
    t0 = time.time()
    formulas_c = generate_type_c_formulas(target_n, target_value)
    print(f"Type C (k×M-k): {len(formulas_c)} valid formulas found ({time.time()-t0:.2f}s)")
    all_formulas.extend(formulas_c)

    # Type D
    t0 = time.time()
    formulas_d = generate_type_d_formulas(target_n, target_value)
    print(f"Type D (k²±C): {len(formulas_d)} valid formulas found ({time.time()-t0:.2f}s)")
    all_formulas.extend(formulas_d)

    # Type E
    t0 = time.time()
    formulas_e = generate_type_e_formulas(target_n, target_value)
    print(f"Type E (k×k±C): {len(formulas_e)} valid formulas found ({time.time()-t0:.2f}s)")
    all_formulas.extend(formulas_e)

    print(f"\nTOTAL: {len(all_formulas)} valid formulas for k{target_n}")

    # Save to database
    save_to_db(target_n, target_value, all_formulas, explorer)

    return all_formulas

def save_to_db(target_n, target_value, formulas, explorer):
    """Save valid formulas to database"""
    conn = get_db()
    cursor = conn.cursor()

    batch_id = int(time.time())

    for f in formulas:
        cursor.execute("""
            INSERT INTO formula_theories
            (target_key, target_value, formula_type, formula_string,
             base_key, base_value, multiplier, second_key, second_value,
             constant, computed_value, is_valid, explored_by, batch_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            f'k{target_n}',
            target_value,
            f['type'],
            f['formula'],
            f.get('base_key'),
            f.get('base_value'),
            f.get('multiplier'),
            f.get('second_key'),
            f.get('second_value'),
            f.get('constant'),
            f['computed'],
            f['is_valid'],
            explorer,
            batch_id
        ))

    conn.commit()
    conn.close()
    print(f"Saved {len(formulas)} formulas to database (batch {batch_id})")

def run_exploration(explorer):
    """Run exploration for assigned targets"""
    if explorer not in ASSIGNMENTS:
        print(f"Unknown explorer: {explorer}")
        return

    targets = ASSIGNMENTS[explorer]
    all_results = {}

    print(f"\n{'#'*70}")
    print(f"# SYSTEMATIC FORMULA EXPLORATION")
    print(f"# Explorer: {explorer}")
    print(f"# Targets: {', '.join(f'k{t}={KEYS[t]}' for t in targets)}")
    print(f"# Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'#'*70}")

    start_time = time.time()

    for target_n in targets:
        formulas = explore_target(target_n, explorer)
        all_results[f'k{target_n}'] = {
            'value': KEYS[target_n],
            'formulas': formulas,
            'count': len(formulas)
        }

    elapsed = time.time() - start_time

    # Summary
    print(f"\n{'='*70}")
    print("EXPLORATION COMPLETE")
    print(f"{'='*70}")
    total_formulas = sum(r['count'] for r in all_results.values())
    print(f"Total valid formulas found: {total_formulas}")
    print(f"Time elapsed: {elapsed:.2f}s")

    for key, data in all_results.items():
        print(f"\n{key} = {data['value']}:")
        # Show top formulas by pattern quality
        if data['formulas']:
            # Prioritize formulas with small constants and multipliers
            sorted_formulas = sorted(data['formulas'],
                key=lambda x: (abs(x.get('constant', 0) or 0) + (x.get('multiplier', 0) or 0)))
            print(f"  Best formulas (smallest constants/multipliers):")
            for f in sorted_formulas[:5]:
                print(f"    {f['formula']} = {f['computed']}")

    # Save results
    results_file = f"/home/solo/LA/{explorer.replace('-', '_')}_exploration_results.json"
    with open(results_file, 'w') as f:
        # Convert formulas to serializable format
        serializable = {}
        for key, data in all_results.items():
            serializable[key] = {
                'value': data['value'],
                'count': data['count'],
                'formulas': data['formulas']
            }
        json.dump({
            'explorer': explorer,
            'timestamp': datetime.now().isoformat(),
            'elapsed_seconds': elapsed,
            'results': serializable
        }, f, indent=2)
    print(f"\nResults saved to: {results_file}")

    return all_results

def show_interesting_patterns():
    """Query database for interesting patterns across all targets"""
    conn = get_db()
    cursor = conn.cursor()

    print(f"\n{'='*70}")
    print("INTERESTING PATTERNS FROM DATABASE")
    print(f"{'='*70}")

    # Formulas using prime constants
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23]
    print("\n1. Formulas with prime constants:")
    cursor.execute("""
        SELECT target_key, formula_string, constant
        FROM formula_theories
        WHERE is_valid = 1 AND constant IN (2,3,5,7,11,13,17,19,23,-2,-3,-5,-7,-11,-13,-17,-19,-23)
        ORDER BY target_key
    """)
    for row in cursor.fetchall():
        print(f"   {row[0]}: {row[1]} (constant={row[2]})")

    # Formulas using known multipliers (9, 13, 19)
    print("\n2. Formulas with known multipliers (9, 13, 19):")
    cursor.execute("""
        SELECT target_key, formula_string, multiplier
        FROM formula_theories
        WHERE is_valid = 1 AND multiplier IN (9, 13, 19)
        ORDER BY target_key
    """)
    for row in cursor.fetchall():
        print(f"   {row[0]}: {row[1]} (multiplier={row[2]})")

    # Type E (product) formulas - often most meaningful
    print("\n3. Product formulas (Type E):")
    cursor.execute("""
        SELECT target_key, formula_string, base_key, second_key, constant
        FROM formula_theories
        WHERE is_valid = 1 AND formula_type = 'E'
        ORDER BY target_key
    """)
    for row in cursor.fetchall():
        print(f"   {row[0]}: {row[1]}")

    conn.close()

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        explorer = sys.argv[1]
        run_exploration(explorer)
    else:
        # Run both explorations
        print("Running full exploration for both solvers...")
        run_exploration('b-solver')
        run_exploration('c-solver')
        show_interesting_patterns()
