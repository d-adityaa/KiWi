# Uncertainty method

Intervals are residual-quantile (conformal-style) demo calibration:

1. Compute KiWi blend residual = blend − observation across history.
2. Per (variable, lead_time), take absolute residual quantiles at
   50/80/95% on the recent window.
3. Interval = blend ± q. Width and coverage are tracked as metrics.

Evaluated by empirical coverage vs nominal level and average width; shown on
the Confidence page. Deterministic and reproducible; labelled DEMO.
