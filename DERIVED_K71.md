# DERIVED: k[71] - ESTIMATE FAILED VERIFICATION

**Date**: 2025-12-20
**Status**: ❌ CRYPTOGRAPHIC VERIFICATION FAILED

---

## Summary

Using constraint analysis and the verified formula, we estimated k[71]:

```
Estimated k[71] = 1,602,101,676,614,237,534,489
Estimated k[71] = 0x56d9a08a95095fb919 (hex)
```

**However, cryptographic verification FAILED:**
```
Target Address:  1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU
Derived Address: 1KEqStQnjYJnEWyqYhwdAup53JCDnTm7va  ← MISMATCH!
```

---

## Why the Estimate Failed

The constraint analysis used an **approximated offset growth ratio** (~1.67). This was based on averaging historical ratios, but:

1. The offset sequence does NOT follow a simple geometric progression
2. The ratios vary significantly: -13.18, -7.63, -6.43, +5.64, +11.99
3. A small error in the ratio compounds across the chain (71→74→77→80)

---

## What We Know (VERIFIED)

1. **Formula works** (67/67 verified for n=4 to n=70):
   ```
   k[n] = 2*k[n-1] + 2^n - m_seq[n-2] * k[d_seq[n-2]]
   ```

2. **d[n] minimizes m[n]** (100% verified)

3. **m-values derive from mathematical constants**:
   - π, e, √2, φ, ln(2) convergents
   - Products, sums, differences of convergents

---

## What We Don't Know

1. **Exact m[71]**: The construction rule for m[n > 70] is not fully determined
2. **Exact d[71]**: Without m[71], we can't verify which d minimizes it

---

## The Real Problem

The m-sequence generation algorithm beyond n=70 is unknown. We have:
- Patterns (17-network, e-factor patterns)
- Construction types (DIRECT, PRODUCT, SUM, DIFF, etc.)
- Selection rules (based on n mod 3, d value)

But we don't have a closed-form algorithm that produces m[71] exactly.

---

## Lesson Learned

**Mathematical constraint analysis is NOT sufficient for cryptographic verification.**

The only way to confirm a private key is correct:
1. Derive the public key (EC point multiplication)
2. Hash it (SHA256 → RIPEMD160)
3. Base58Check encode
4. **Match the address**

Until the address matches, the key is NOT solved.

---

## Next Steps

To solve k[71], we need to:

1. **Find the exact m[71] construction rule** - not approximate, but exact
2. **Test candidates against the target address** - cryptographic verification
3. **Consider brute force within constraints** - if k[71] is in a narrow range

---

## Files

- `verify_key_pure.py` - Pure Python address verification tool
- `search_m71_constrained.py` - Constraint analysis (gave wrong estimate)
