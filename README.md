# KiWi — Hybrid AI–NWP Multi-Model Forecast Blending System

SIH 26081 · **DEMO / SYNTHETIC DATA** · Version 1.0

KiWi is a forecast **trust, blending, verification, confidence, and risk** layer
over multiple (simulated) forecast sources. It does not predict weather by
itself; it decides *which sources to trust under which context* and produces a
calibrated, explainable blended product.

> Prototype only — synthetic data, not operational weather guidance.

## Core identity

```
Multiple forecasts → contextual skill → adaptive trust (TreeGate)
→ dynamic blending → confidence + uncertainty → extreme risk → verification → learning
```

## Quick start

```bash
pip install -r requirements.txt

python scripts/generate_demo_data.py   # synthetic demo fields
python scripts/run_pipeline.py         # full pipeline (QC→TreeGate→blend→calibration→artifacts)
python scripts/run_api.py              # FastAPI on :8000
python scripts/run_dashboard.py        # Streamlit on :8501

pytest                                 # test suite
python scripts/run_pipeline.py --disable Pangu   # simulate source failure (fallback)
python scripts/run_pipeline.py --quick           # faster run for tests/CI
```

## What is implemented

- Six simulated sources: GFS, ECMWF, IMD-WRF, GraphCast, Pangu, ENS
- Deterministic synthetic gridded India fields (truth, contexts, regimes, seasons)
- QC checks, temporal/spatial alignment to a common case schema
- Historical skill memory: MAE/RMSE/Bias/Correlation + extreme P/R/F1, by
  source × variable × region × lead × regime
- Contextual rolling bias correction
- Prototype regime classifier
- Adaptive TreeGate (HistGradientBoostingRegressor per variable×source)
  → temperature-softmax weights summing to 1
- Temporal weight smoothing
- Model disagreement score (0–100)
- Demo-calibrated confidence + 50/80/95% conformal-style intervals with coverage metrics
- Deterministic explainability ("why this weight", "why this confidence")
- Prototype extreme-event detection from ENS member probability + RPI
- Method comparison: individual sources, equal average, best single, skill gate,
  TreeGate, final KiWi blend
- Deterministic source fallback (disable feeds, renormalize, record events)
- Data health, run history, model registry
- CSV/JSON export + bulletin generator
- English/Hindi static UI translation
- FastAPI backend + 12-page Streamlit dashboard with restrained scientific styling

## What is explicitly NOT implemented

- No live GFS/ECMWF/IMD/GraphCast/Pangu/ERA5/radar/satellite ingestion
- No GPU/deep-learning training, no LLM/chatbot
- No official IMD thresholds, no operational disaster scoring
- Real-data adapter interfaces exist as seams (`ForecastSource`, `ObservationSource`)

See `FEATURE_MATRIX.md` and `docs/` for full details.

