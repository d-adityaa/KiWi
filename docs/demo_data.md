# Demo data

All values are synthetic and deterministic (seeded). Generator:
`src/synthetic/generator.py`.

- Grid: lat 10–30°N, lon 70–88°E, 2.5° step (India-focused)
- 60 daily cycles × 5 lead times (6/12/24/48/72 h) × 3 variables
- Contexts: humidity, CAPE-like instability, regime labels, season
- Source forecasts = truth + source-specific bias/noise growing with lead time,
  modulated by regime, so adaptive weighting has something to learn
- ENS: 8 members per case; member spread drives ensemble probability

No real meteorological data is used, stored, or displayed.
