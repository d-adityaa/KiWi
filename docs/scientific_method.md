# Scientific method

1. Historical skill memory: per source×variable×region×lead×regime metrics
   (MAE, RMSE, bias, correlation; extreme precision/recall/F1).
2. Contextual rolling bias correction: corrected = raw − rolling mean bias
   grouped by source×variable×region×lead. Bias is measurable per cell.
3. Prototype regime classifier buckets each case into Stable / Normal Rain /
   Convective / Heavy Rain / Heatwave / High Wind / Transition.
4. TreeGate: HistGradientBoostingRegressor per (variable, source) predicts
   expected absolute error from inspectable context features; errors feed a
   temperature softmax → dynamic weights (sum to 1). Temporal smoothing
   (configurable alpha) damps jumps. Unavailable sources are masked and
   weights renormalized (fallback).
5. Blend: F = Σ wᵢ fᵢ(corrected). Disagreement score from ensemble of
   source values (std/range/IQR normalized).
6. Confidence + intervals: recent blend residuals provide empirical
   quantiles (50/80/95%). Confidence score combines disagreement, recent
   blend RMSE, sample size, fallback state, regime.
7. Extremes/RPI: ENS member exceedance probability × severity × uncertainty
   × persistence → prototype Risk Priority Index in [0,100].
8. Verification: coverage vs nominal, interval widths, and method-by-method
   MAE/RMSE/bias/correlation (individual sources, equal average, best
   single, skill-only gate, TreeGate/KiWi). KiWi is not claimed to be best.

All explanations are deterministic and derived from computed values.
