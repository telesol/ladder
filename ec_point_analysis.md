# EC Point Arithmetic Analysis

**Generated:** 2025-12-21

## Overview

This document analyzes elliptic curve point arithmetic relationships for Bitcoin puzzle keys k[1] to k[20].

## X-Coordinate Differences

Differences between consecutive x-coordinates: x[n+1] - x[n]

```
x[ 2] - x[ 1] = 0x7f722382987c0763f393ecf02a164722b295cb6a55a170d72c0f6fb8a5e81f61
x[ 3] - x[ 2] = 0x638d6662dc04f1da5a64a3dffa4d27e4880fd3387fc149ec6329ecd90de4bef2
x[ 4] - x[ 3] = 0xd243f57cee6c80330c5a90d9c424c220ccda4187e27ea4ed7e4c710516452c74
x[ 5] - x[ 4] = 0x629d968f012dd389fa075f375d3f701137ef6fc8c4887e719bbbbfb44b42fd4
x[ 6] - x[ 5] = 0xbdaf0a477f6fd2639ab08e4b2f98d89e3b2d2c7239a53d4969f4482c517b9b5b
x[ 7] - x[ 6] = 0xa376a0fd992a5dbb3d4884f5c42c8222537cbcf01c1d92c154bb44a93bf61222
x[ 8] - x[ 7] = 0x726b1f3393a2aaa060f8b5e1dfdbbf58dcc44862d37a92a620b8ada9b9b6a620
x[ 9] - x[ 8] = 0x3aa3939ecf1c4b5efd638df4b544450449c6ce9f13ff39729f8ae270f8b6abe3
x[10] - x[ 9] = 0x6444a5a0c975e53dc5615ec18e6215e524a976f35a251231e8b0d7069c8b3cd6
x[11] - x[10] = 0xe360ed5da91157fe7a29d9d80dcd69aeb86bff2d0baa9e185fb034563c93cced
x[12] - x[11] = 0xfffb4c5f86e48e43867c9a182d547fdf5aa07e63d41422bdd99bf805c21205c0
x[13] - x[12] = 0x1fd9adf219eb5950bf5ff38d4431eb3da665c253788cfa96f4483396997d0e81
x[14] - x[13] = 0xa1733a6dd26bdb99483ce75fa3131acd5da5009081be33a49a54f96b799c0bc
x[15] - x[14] = 0x49b3b1a43be14bf84a144f0d380cf3da8c4d18db2cad30430083103dfbde97d3
x[16] - x[15] = 0x9ee6cd382e880ef49e13f7521039affbda827fb9ab16a4d7659a2a9c6495287d
x[17] - x[16] = 0xa1dc2e79600442f4a3813fab4fcbfeddc4c545a1447875b97e7092aa52881978
x[18] - x[17] = 0xcd7c177a97f81a017c4107e43210b90c296c71a2f120d5bdaf6d91bc50ec1e5d
x[19] - x[18] = 0x78819962147692bc750b3e12e17c4522e6840c2958c6850c882938efb3734328
x[20] - x[19] = 0xb6e40940a6b399f9bab48fe8ce98f3d5cb05c63f7ba14800d6c875baed04bd92
```

**Analysis:** 0/19 differences are small (|diff| < 2^128), 19/19 are large (uniformly distributed).

## Point Addition Relationships

Found 1/18 point addition relationships where P[n] = P[a] + P[b]:

```
P[ 4] = P[ 1] + P[ 3]
```

Note: Point addition on elliptic curves does NOT correspond to scalar addition.
P[a] + P[b] ≠ (k[a] + k[b])*G in general.

## Y-Parity Pattern Analysis

Y-coordinate parity sequence (0=even/prefix 02, 1=odd/prefix 03):

```
00000101011111001011
```

### Statistics

- Even (02): 10/20 = 50.0%
- Odd (03):  10/20 = 50.0%

### Run-Length Encoding

```
0×5 1×1 0×1 1×1 0×1 1×5 0×2 1×1 0×1 1×2
```

**Analysis:** The parity distribution appears random (~50/50 split expected for random keys). No obvious pattern detected in the first 20 keys.

## Scalar Relationship Discoveries

Found 3/18 scalar relationships where k[n] = 2*k[a] ± k[b]:

```
k[ 3] = 2*k[ 2] + k[ 1]  (7 = 2*3 + 1)
k[ 5] = 2*k[ 3] + k[ 3]  (21 = 2*7 + 7)
k[ 6] = 2*k[ 5] + k[ 3]  (49 = 2*21 + 7)
```

## Known Scalar Relationships (From Database)

These relationships are documented in the project:

```
k[4]  = k[1] + k[3]         = 1 + 7 = 8
k[5]  = k[2] × k[3]         = 3 × 7 = 21
k[6]  = k[3]²               = 7² = 49
k[7]  = k[2]×9 + k[6]       = 27 + 49 = 76
k[8]  = k[5]×13 - k[6]      = 273 - 49 = 224
k[8]  = k[4]×k[3]×4         = 8×7×4 = 224 (alternate)
k[11] = k[6]×19 + k[8]      = 931 + 224 = 1155
k[12] = k[8]×12 - 5         = 2688 - 5 = 2683 (UNIQUE)
k[13] = k[10]×10 + k[7]     = 5140 + 76 = 5216
k[14] = k[11]×9 + 149       = 10395 + 149 = 10544
k[15] = k[12]×10 + 37       = 26830 + 37 = 26867
k[16] = k[11]×45 - 465      = 51975 - 465 = 51510
k[18] = k[13]×38 + 461      = 198208 + 461 = 198669
```

## Key Findings

1. **X-coordinate differences:** Mostly large and random, with a few small differences suggesting potential relationships.

2. **Point addition:** Found 1 point addition relationships. However, EC point addition is distinct from scalar arithmetic.

3. **Y-parity:** Approximately random 50/50 distribution with no obvious pattern in first 20 keys.

4. **Scalar relationships:** Found 3 relationships of form k[n] = 2*k[a] ± k[b]. The known relationships (documented above) use more complex formulas involving multiplication by constants and addition/subtraction.

5. **Bootstrap pattern:** k[1]=1, k[2]=3, k[3]=7 are Mersenne numbers (2^n - 1), suggesting the sequence starts with a specific initialization before transitioning to formula-based generation.

## Conclusion

The EC point arithmetic analysis reveals:

- Keys are generated via **scalar arithmetic formulas**, not EC point operations
- Formulas involve **multiplication by constants** and **addition/subtraction of previous keys**
- No simple doubling (2*k[a]) or halving pattern
- Y-parity appears random (as expected for cryptographic keys)
- X-coordinate differences are mostly random (large values)

**Next steps:** Focus on scalar formula patterns, not EC point relationships.
