# KiWi Feature Matrix

Status legend: IMPLEMENTED · PARTIAL · FUTURE

| # | Feature | Status | Notes |
|---|---------|--------|-------|
| 1 | Synthetic data engine (truth, sources, ENS, regimes, seasons) | IMPLEMENTED | seeded, deterministic |
| 2 | QC checks | IMPLEMENTED | per-source report on Data Health |
| 3 | Temporal/spatial alignment | IMPLEMENTED | common case index |
| 4 | Historical skill memory | IMPLEMENTED | MAE/RMSE/bias/corr + extreme P/R/F1 |
| 5 | Bias correction | IMPLEMENTED | rolling contextual mean bias |
| 6 | Prototype regime classifier | IMPLEMENTED | rule-based, labelled demo |
| 7 | TreeGate adaptive weights | IMPLEMENTED | HistGBR per variable×source |
| 8 | Weight smoothing | IMPLEMENTED | configurable alpha |
| 9 | Model disagreement score | IMPLEMENTED | std/range/IQR → 0–100 prototype |
| 10 | Confidence score + reasoning | IMPLEMENTED | deterministic decomposition |
| 11 | Uncertainty intervals 50/80/95 | IMPLEMENTED | residual-quantile calibration |
| 12 | Coverage / width evaluation | IMPLEMENTED | artifact `coverage.parquet` |
| 13 | Extreme detection (rain/heat/wind/uncertainty) | IMPLEMENTED | prototype thresholds |
| 14 | RPI risk priority | IMPLEMENTED | explicit configurable formula |
| 15 | Source fallback simulation | IMPLEMENTED | `--disable` feeds |
| 16 | Why-this-weight explanation | IMPLEMENTED | metric-based, no LLM |
| 17 | Method comparison | IMPLEMENTED | sources, equal avg, best single, skill gate, TreeGate |
| 18 | Cell-level explorer | IMPLEMENTED | sidebar filters + cell select |
| 19 | Trust Atlas (weight maps) | IMPLEMENTED | region bars + dominant source |
| 20 | Lead-time performance | IMPLEMENTED | RMSE heatmap, MAE curves |
| 21 | Data health page | IMPLEMENTED | status/QC/missing/fallback/rows/cells |
| 22 | Run history | IMPLEMENTED | JSONL inspect |
| 23 | Model registry | IMPLEMENTED | sources + component versions |
| 24 | Export CSV/JSON + bulletin | IMPLEMENTED | demo-labelled |
| 25 | English/Hindi UI | IMPLEMENTED | static dictionary |
| 26 | Footer + demo label on all pages | IMPLEMENTED | enforced in common.py |
| 27 | 3D diagnostic chart | PARTIAL | not primary visual |
| 28 | Real GFS/ECMWF/IMD/GraphCast/Pangu/ERA5 adapters | FUTURE | interfaces only |
| 29 | GPU/DL, GNN, downscaling, radar/satellite | FUTURE | out of MVP scope |
| 30 | Official IMD thresholds, operational scheduling | FUTURE | |
