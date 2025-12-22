#!/usr/bin/env python3
"""
Interactive convergent formula tester.

Use this to test specific hypotheses about m-sequence construction.
"""

import sys
from fractions import Fraction

# Known m-sequence from database
m_seq = {
    2: 3, 3: 7, 4: 22, 5: 27, 6: 57, 7: 150, 8: 184, 9: 493,
    10: 1444, 11: 1921, 12: 3723, 13: 8342, 14: 16272, 15: 26989,
    16: 67760, 17: 138269, 18: 255121, 19: 564091, 20: 900329
}

def continued_fraction_pi(max_terms=40):
    """π continued fraction."""
    cf = [3, 7, 15, 1, 292, 1, 1, 1, 2, 1, 3, 1, 14, 2, 1, 1, 2, 2, 2, 2,
          1, 84, 2, 1, 1, 15, 3, 13, 1, 4, 2, 6, 6, 1, 1, 1, 8, 1, 1, 3]
    return cf[:max_terms]

def continued_fraction_e(max_terms=50):
    """e continued fraction."""
    cf = [2]
    for k in range(1, max_terms):
        cf.extend([1, 2*k, 1])
        if len(cf) >= max_terms:
            break
    return cf[:max_terms]

def continued_fraction_phi(max_terms=50):
    """φ continued fraction."""
    return [1] * max_terms

def convergents_from_cf(cf):
    """Generate convergents from continued fraction."""
    convergents = []
    p_prev, p_curr = 1, cf[0]
    q_prev, q_curr = 0, 1
    convergents.append((p_curr, q_curr))

    for a in cf[1:]:
        p_next = a * p_curr + p_prev
        q_next = a * q_curr + q_prev
        convergents.append((p_next, q_next))
        p_prev, p_curr = p_curr, p_next
        q_prev, q_curr = q_curr, q_next

    return convergents

# Generate convergents
pi_cf = continued_fraction_pi()
e_cf = continued_fraction_e()
phi_cf = continued_fraction_phi()

pi_conv = convergents_from_cf(pi_cf)
e_conv = convergents_from_cf(e_cf)
phi_conv = convergents_from_cf(phi_cf)

class ConvergentFormulaTester:
    """Test convergent-based formulas."""

    def __init__(self):
        self.pi_conv = pi_conv
        self.e_conv = e_conv
        self.phi_conv = phi_conv
        self.pi_cf = pi_cf
        self.e_cf = e_cf
        self.phi_cf = phi_cf

    def get_convergent(self, system, index):
        """Get convergent by system and index."""
        if system == 'pi':
            if 0 <= index < len(self.pi_conv):
                return self.pi_conv[index]
        elif system == 'e':
            if 0 <= index < len(self.e_conv):
                return self.e_conv[index]
        elif system == 'phi':
            if 0 <= index < len(self.phi_conv):
                return self.phi_conv[index]
        return (None, None)

    def test_formula(self, formula_func, n_range=None):
        """
        Test a formula function against known m-values.

        formula_func should take (n, tester) and return predicted m[n].
        """
        if n_range is None:
            n_range = sorted(m_seq.keys())

        results = []
        for n in n_range:
            if n not in m_seq:
                continue

            try:
                predicted = formula_func(n, self)
                actual = m_seq[n]
                match = (predicted == actual)
                results.append({
                    'n': n,
                    'actual': actual,
                    'predicted': predicted,
                    'match': match,
                    'error': abs(predicted - actual) if predicted else None
                })
            except Exception as e:
                results.append({
                    'n': n,
                    'actual': m_seq[n],
                    'predicted': None,
                    'match': False,
                    'error': None,
                    'exception': str(e)
                })

        return results

    def print_results(self, results):
        """Pretty print test results."""
        print("\n" + "=" * 80)
        print("FORMULA TEST RESULTS")
        print("=" * 80)
        print(f"\nn  | actual   | predicted | match | error")
        print("-" * 60)

        matches = 0
        for r in results:
            match_str = "✓" if r['match'] else "✗"
            pred_str = f"{r['predicted']:9d}" if r['predicted'] is not None else "None     "
            error_str = f"{r['error']:8d}" if r.get('error') is not None else ""

            print(f"{r['n']:2d} | {r['actual']:8d} | {pred_str} | {match_str:5s} | {error_str}")

            if r['match']:
                matches += 1

        print("-" * 60)
        print(f"Matches: {matches}/{len(results)} ({100*matches/len(results):.1f}%)")

        return matches, len(results)

# Example formula functions
def formula_simple_index_map(n, tester):
    """Example: m[n] = π_num[n-2]"""
    num, den = tester.get_convergent('pi', n-2)
    return num if num is not None else 0

def formula_switching_mod2(n, tester):
    """Example: Switch based on n%2"""
    if n % 2 == 0:
        num, den = tester.get_convergent('pi', n-2)
        return num if num is not None else 0
    else:
        num, den = tester.get_convergent('pi', n-2)
        return den if den is not None else 0

def formula_weighted_combination(n, tester):
    """
    Example: Weighted combination.
    Customize this for your hypothesis!
    """
    # This is a TEMPLATE - modify based on your hypothesis
    if n == 2:
        num, den = tester.get_convergent('pi', 0)
        return num  # 3

    if n == 3:
        num, den = tester.get_convergent('pi', 1)
        return den  # 7

    if n == 4:
        num, den = tester.get_convergent('pi', 1)
        return num  # 22

    if n == 5:
        num, den = tester.get_convergent('pi', 0)
        return 9 * num  # 27

    if n == 6:
        num_e, den_e = tester.get_convergent('e', 4)
        return 3 * num_e  # 57

    if n == 7:
        num, den = tester.get_convergent('pi', 1)
        return 10 * (num - den)  # 150

    if n == 8:
        num, den = tester.get_convergent('pi', 1)
        return 8 * num + 8 * den  # 184

    # Add more cases as you discover them
    return 0

# Main execution
if __name__ == "__main__":
    tester = ConvergentFormulaTester()

    print("=" * 80)
    print("CONVERGENT FORMULA TESTER")
    print("=" * 80)

    # Test example formulas
    print("\n1. Testing simple index mapping: m[n] = π_num[n-2]")
    results1 = tester.test_formula(formula_simple_index_map, list(range(2, 12)))
    tester.print_results(results1)

    print("\n2. Testing switching formula: even→num, odd→den")
    results2 = tester.test_formula(formula_switching_mod2, list(range(2, 12)))
    tester.print_results(results2)

    print("\n3. Testing weighted combination formula (manual cases)")
    results3 = tester.test_formula(formula_weighted_combination, list(range(2, 12)))
    tester.print_results(results3)

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("""
To test your own hypothesis:

1. Create a new formula function:
   def my_formula(n, tester):
       # Your logic here
       num, den = tester.get_convergent('pi', some_index)
       return your_combination

2. Test it:
   results = tester.test_formula(my_formula)
   tester.print_results(results)

3. Iterate until you find the pattern!

Available convergent systems:
- tester.get_convergent('pi', index)    → (numerator, denominator)
- tester.get_convergent('e', index)     → (numerator, denominator)
- tester.get_convergent('phi', index)   → (numerator, denominator)

You can also access:
- tester.pi_cf[index]  → π continued fraction term
- tester.e_cf[index]   → e continued fraction term
- tester.phi_cf[index] → φ continued fraction term (always 1)
- m_seq[n]             → Known m-values for verification
""")

    print("\nQuick reference:")
    print("π convergents (first 5):")
    for i in range(min(5, len(pi_conv))):
        num, den = pi_conv[i]
        print(f"  [{i}] {num}/{den}")

    print("\ne convergents (first 5):")
    for i in range(min(5, len(e_conv))):
        num, den = e_conv[i]
        print(f"  [{i}] {num}/{den}")

    print("\nφ convergents (first 5):")
    for i in range(min(5, len(phi_conv))):
        num, den = phi_conv[i]
        print(f"  [{i}] {num}/{den}")
