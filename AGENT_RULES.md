# AGENT STRICT RULES - MUST READ BEFORE ANY TASK

## ABSOLUTE PROHIBITIONS

1. **NO PREDICTIONS** - Do not predict, guess, or estimate unknown key values
2. **NO HALLUCINATIONS** - Never invent or fabricate data
3. **NO ASSUMPTIONS** - If you don't have data, say "UNKNOWN"
4. **NO POSITION GUESSING** - Do not estimate where in a range a key might be

## MANDATORY REQUIREMENTS

1. **USE THE DATABASE** - All key values must come from `db/kh.db`
2. **VERIFY EVERYTHING** - Every formula must be verified against actual DB values
3. **SHOW YOUR MATH** - Every step must be explicit and reproducible
4. **CITE YOUR SOURCE** - State which puzzle IDs you're using from the DB

## DATABASE SCHEMA

```sql
-- Keys table (the source of truth)
SELECT puzzle_id, priv_hex FROM keys WHERE puzzle_id = N;

-- Known puzzles: 1-70, 75, 80, 85, 90 (74 total)
-- Unknown: 71-74, 76-79, 81-84, 86-89, 91-160
```

## WHAT WE WANT

**FORMULA DERIVATION** - Find the mathematical relationship the creator used.

Given: k1=1, k2=3, k3=7, k4=8, k5=21, k6=49, k7=76, k8=224...

Find: f(n) such that k_n = f(k_1, k_2, ..., k_{n-1})

## VALID OPERATIONS

- Arithmetic on KNOWN values from DB
- Testing formulas against KNOWN values
- Identifying patterns in KNOWN sequences
- Proving or disproving relationships

## INVALID OPERATIONS

- Predicting k71 or any unknown key
- Estimating search positions
- Guessing algorithm parameters
- Claiming to have "solved" anything

## EXAMPLE: GOOD vs BAD

**BAD**: "k71 is probably near the minimum because k69 was at 0.72%"
**GOOD**: "k5 = k2 × k3 = 3 × 7 = 21 (verified against DB)"

**BAD**: "The key is likely 0x..."
**GOOD**: "Testing formula f(n) = k_{n-1}² against k1-k14: [results]"

## THE GOAL

Reverse-engineer the KEY GENERATION METHOD, not predict specific keys.

If we find the formula, we can derive ALL 160 keys mathematically.
Without the formula, guessing is useless.

## BEFORE ANY RESPONSE, ASK:

1. Am I using actual DB values?
2. Am I making any predictions?
3. Can I verify this mathematically?
4. Am I showing all steps?

If any answer is NO, stop and reformulate.
