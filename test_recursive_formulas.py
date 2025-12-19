#!/usr/bin/env python3
"""
Test recursive/self-referential formulas for m-sequence.

Based on discoveries from multi-Claude session:
- m[6] = d[6] × m[5] + m[2] = 2 × 9 + 1 = 19
- m[8] = m[2] + m[4] = 1 + 22 = 23
- m[10] = m[6] = 19 (exact repeat!)
- m[11] = 17 × prime(11 + 19) = 17 × 113
- m[12] = 17 × prime(12 + 9) = 17 × 73
"""

import json
import sympy

# Load verified data
with open('data_for_csolver.json') as f:
    data = json.load(f)
    n_start = data['n_range'][0]  # Should be 2
    # Convert arrays to dictionaries (m_seq[0] = m[2], m_seq[1] = m[3], etc.)
    M_SEQ = {n_start + i: val for i, val in enumerate(data['m_seq'])}
    D_SEQ = {n_start + i: val for i, val in enumerate(data['d_seq'])}

print("=" * 80)
print("RECURSIVE FORMULA TESTER")
print("=" * 80)
print(f"\nLoaded {len(M_SEQ)} m-values and {len(D_SEQ)} d-values")

# Helper functions
def prime(n):
    """Get the nth prime (1-indexed)."""
    return sympy.prime(n)

def is_prime(n):
    """Check if n is prime."""
    return sympy.isprime(n)

def prime_index(p):
    """Get index of prime p (slow for large primes)."""
    if not is_prime(p):
        return None
    return sympy.primepi(p)

# Test formulas
formulas = []

# FORMULA 1: Linear combination of previous m-values
formulas.append({
    'name': 'F1: m[n] = d[n] × m[n-1] + m[n-2]',
    'test': lambda n: D_SEQ.get(n, 0) * M_SEQ.get(n-1, 0) + M_SEQ.get(n-2, 0) if n > 3 else None
})

# FORMULA 2: m[n] = m[n-1] + m[n-d[n]]
formulas.append({
    'name': 'F2: m[n] = m[n-1] + m[n-d[n]]',
    'test': lambda n: M_SEQ.get(n-1, 0) + M_SEQ.get(n-D_SEQ.get(n, 1), 0) if n > 2 else None
})

# FORMULA 3: m[n] = m[n-d[n]] (exact repeat based on d)
formulas.append({
    'name': 'F3: m[n] = m[n-d[n]] (repeat pattern)',
    'test': lambda n: M_SEQ.get(n-D_SEQ.get(n, 1), 0) if n > 2 else None
})

# FORMULA 4: m[n] = d[n] × m[n-d[n]] + constant
formulas.append({
    'name': 'F4: m[n] = d[n] × m[n-d[n]] + m[2]',
    'test': lambda n: D_SEQ.get(n, 0) * M_SEQ.get(n-D_SEQ.get(n, 1), 0) + M_SEQ.get(2, 0) if n > 2 else None
})

# FORMULA 5: Product with prime 17
formulas.append({
    'name': 'F5: m[n] = 17 × f(n)',
    'test': lambda n: None  # Will test separately (requires factorization check)
})

# FORMULA 6: Power of 2 scaling
formulas.append({
    'name': 'F6: m[n] = 2^d[n] × m[n-d[n]]',
    'test': lambda n: (2**D_SEQ.get(n, 1)) * M_SEQ.get(n-D_SEQ.get(n, 1), 0) if n > 2 else None
})

# FORMULA 7: Weighted combination
formulas.append({
    'name': 'F7: m[n] = 2×m[n-1] - m[n-2] + d[n]',
    'test': lambda n: 2*M_SEQ.get(n-1, 0) - M_SEQ.get(n-2, 0) + D_SEQ.get(n, 0) if n > 3 else None
})

# FORMULA 8: Fibonacci-like
formulas.append({
    'name': 'F8: m[n] = m[n-1] + m[n-2]',
    'test': lambda n: M_SEQ.get(n-1, 0) + M_SEQ.get(n-2, 0) if n > 3 else None
})

# FORMULA 9: Modular combination
formulas.append({
    'name': 'F9: m[n] = (m[n-1] × d[n]) mod 256 + offset',
    'test': lambda n: (M_SEQ.get(n-1, 0) * D_SEQ.get(n, 1)) % 256 if n > 2 else None
})

# FORMULA 10: Prime index self-reference (discovered pattern)
def test_prime_index_pattern(n):
    """Test: m[n] = p[7] × p[n + m[k]] for some k."""
    m_n = M_SEQ.get(n)
    if m_n is None or m_n % 17 != 0:
        return None

    quotient = m_n // 17
    if not is_prime(quotient):
        return None

    q_index = prime_index(quotient)

    # Check if q_index = n + m[k] for any k < n
    for k in range(2, n):
        if q_index == n + M_SEQ.get(k, 0):
            return (k, quotient, q_index)

    return None

formulas.append({
    'name': 'F10: m[n] = 17 × p[n + m[k]] (self-ref prime index)',
    'test': test_prime_index_pattern
})

# Test all formulas
print("\n" + "=" * 80)
print("TESTING FORMULAS")
print("=" * 80)

results = {}

for formula in formulas:
    name = formula['name']
    test_fn = formula['test']

    print(f"\n{name}")
    print("-" * 80)

    matches = 0
    total = 0
    examples = []

    for n in sorted(M_SEQ.keys()):
        if n < 4:  # Skip base cases
            continue

        predicted = None
        try:
            predicted = test_fn(n)
        except:
            pass

        actual = M_SEQ[n]

        if predicted is not None:
            total += 1
            if predicted == actual:
                matches += 1
                examples.append(f"n={n}: ✓ {predicted}")
            elif matches < 3 and total < 10:  # Show first few failures
                examples.append(f"n={n}: ✗ pred={predicted}, actual={actual}")

    accuracy = 100 * matches / total if total > 0 else 0

    print(f"  Matches: {matches}/{total} ({accuracy:.1f}%)")
    if examples:
        print(f"  Examples:")
        for ex in examples[:5]:
            print(f"    {ex}")

    results[name] = {
        'matches': matches,
        'total': total,
        'accuracy': accuracy
    }

# Special test for F10 (prime index pattern)
print("\n" + "=" * 80)
print("SPECIAL TEST: Prime Index Self-Reference Pattern")
print("=" * 80)

print("\nDiscovered pattern:")
print("  m[11] = 17 × p[11 + m[6]] = 17 × p[30] = 17 × 113 = 1921")
print("  m[12] = 17 × p[12 + m[5]] = 17 × p[21] = 17 × 73 = 1241")

discoveries = []
for n in sorted(M_SEQ.keys()):
    if n < 4:
        continue

    result = test_prime_index_pattern(n)
    if result:
        k, quotient, q_index = result
        m_n = M_SEQ[n]
        print(f"\n  n={n}: m[{n}] = 17 × p[{n} + m[{k}]] = 17 × p[{q_index}] = 17 × {quotient} = {m_n}")
        discoveries.append({'n': n, 'k': k, 'quotient': quotient, 'index': q_index})

# Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

# Sort by accuracy
sorted_formulas = sorted(results.items(), key=lambda x: x[1]['accuracy'], reverse=True)

print("\nFormulas ranked by accuracy:\n")
for i, (name, res) in enumerate(sorted_formulas, 1):
    acc = res['accuracy']
    matches = res['matches']
    total = res['total']

    status = ""
    if acc == 100:
        status = "🎉 PERFECT!"
    elif acc >= 90:
        status = "🔥 VERY CLOSE!"
    elif acc >= 70:
        status = "👍 PROMISING"
    elif acc >= 50:
        status = "🤔 PARTIAL"
    else:
        status = "❌ POOR"

    print(f"{i}. {name}")
    print(f"   {matches}/{total} = {acc:.1f}% {status}")

# Check for exact repeats (like m[6] = m[10])
print("\n" + "=" * 80)
print("EXACT REPEATS IN SEQUENCE")
print("=" * 80)

seen = {}
for n, m in sorted(M_SEQ.items()):
    if m in seen:
        print(f"  m[{n}] = m[{seen[m]}] = {m}")
    else:
        seen[m] = n

# Save results
output = {
    'formulas_tested': len(formulas),
    'results': results,
    'prime_index_discoveries': discoveries,
    'exact_repeats': [(n, m, seen[m]) for n, m in M_SEQ.items() if m in [v for k, v in M_SEQ.items() if k < n]]
}

with open('recursive_formula_test_results.json', 'w') as f:
    json.dump(output, f, indent=2)

print("\n✅ Results saved to: recursive_formula_test_results.json")
