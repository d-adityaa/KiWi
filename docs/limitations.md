# Limitations

- All data is synthetic; numbers do not measure real model skill.
- Regime engine and RPI are prototype/demo classifiers, not official IMD criteria.
- Confidence/RPI are heuristic decision-support scores, not validated
  operational metrics.
- Single-node, file-artifact storage; no streaming, no real-time scheduling.
- TreeGate trains per variable×source on all history — deterministic but not
  a research-grade retraining regime.
- Uncertainty intervals are residual-quantile based, not full Bayesian
  posterior samples.
