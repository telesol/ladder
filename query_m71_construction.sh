#!/bin/bash
# Query Nemotron for m[71] construction analysis

CONTEXT=$(cat NEMOTRON_CONTEXT.md)

# Create the prompt
PROMPT="You are a mathematical analyst. NO PREDICTIONS - ONLY DERIVATIONS.

$CONTEXT

---

## SPECIFIC TASK

Analyze the m-value construction for n ≡ 2 (mod 3) cases.

### Data for n ≡ 2 (mod 3):
- n=50: m=1332997220739910, d=1
- n=53: m=10676506562464268, d=1
- n=56: m=87929632728990281, d=1
- n=59: m=451343703997841395, d=1
- n=62: m=1184962853718958602, d=2
- n=65: m=1996402169071970173, d=5
- n=68: m=340563526170809298635, d=1

### Question 1: Factor Analysis
For each m-value above, find its prime factorization or connection to convergents.
Check for factors: 17, 19, 22, 3, 7, 11, 13.

### Question 2: Pattern in d-sequence
For n ≡ 2 (mod 3): d = [1, 1, 1, 1, 2, 5, 1, ...]
What determines when d changes from 1 to 2 or 5?

### Question 3: Predict d[71]
Based on the pattern [1, 1, 1, 1, 2, 5, 1], what is d[71]?
Show your reasoning.

SHOW ALL WORK. NO GUESSING."

# Create JSON payload
PAYLOAD=$(jq -n \
  --arg model "nemotron-3-nano:30b-cloud" \
  --arg prompt "$PROMPT" \
  '{model: $model, prompt: $prompt, stream: false, options: {temperature: 0.1, num_predict: 2000}}')

echo "Querying Nemotron..."
echo "=========================================="

# Query Nemotron
curl -s http://localhost:11434/api/generate \
  -d "$PAYLOAD" \
  --max-time 120 \
  | jq -r '.response // "No response"'

echo "=========================================="
