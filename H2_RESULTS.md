# H2 Results: Cryptographic Hash Functions
**Completed**: 2025-12-19
**Runtime**: ~5 minutes
**Hypothesis**: drift[k][lane] = hash(k, lane) mod 256

---

## Summary

**Overall Accuracy**: 0.82% (FAILED)

### Best Results:
| Hash Function | Encoding | Accuracy |
|---------------|----------|----------|
| SHA512 | str_concat | **0.82%** |
| HASH256 (Bitcoin) | packed_little | 0.7% |
| MD5 | str_concat | 0.5% |
| RIPEMD160 | str_concat | 0.5% |
| SHA256 | bytes_concat | 0.3% |

---

## Tests Performed

1. ✅ Standard hashes: SHA256, MD5, SHA1, SHA512, RIPEMD160
2. ✅ Bitcoin-specific: HASH256 (double SHA256), HASH160
3. ✅ Salted/seeded variants
4. ✅ XOR combinations
5. ✅ N-th byte extraction from hashes

All failed with <1% accuracy.

---

## Verdict

❌ **Cryptographic hash functions are NOT the drift generator**

The drift values are NOT produced by:
- Standard cryptographic hashes
- Bitcoin-specific hashes (HASH256, HASH160)
- Salted/keyed hashes
- XOR combinations
- Selective byte extraction

**Recommendation**: Try H3 (PRNG) next

---

## Implications

The low accuracy (<1%) rules out hash functions completely. The drift generator must use a different approach:
- PRNG with specific seed
- Modular arithmetic (already tested in H1, got 69%)
- Recursive/algorithmic pattern
- Lookup table / pre-computed values

Next: Test H3 (PRNG hypothesis)
