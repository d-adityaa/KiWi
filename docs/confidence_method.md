# Confidence method

Confidence is a deterministic 0–100 score built from measurable inputs:

- Model disagreement score (−0..35 points)
- Recent blend RMSE normalized (−0..30 points)
- Sparse historical samples (−20 points below threshold)
- Fallback active (−15 points)
- Severe regime (−8 points)

Reasons are generated from the same quantities by
`src/explain/explain.py`. No randomness, no LLM.
