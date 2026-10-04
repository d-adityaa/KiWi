# Architecture

KiWi pipeline:

```
Synthetic sources (src/synthetic)
  → Ingestion (src/ingestion) → Schema validation (src/schemas.py)
  → QC (src/qc) → Temporal/Spatial alignment (src/alignment)
  → Features (src/features) → Historical skill (src/skill)
  → Bias correction (src/bias) → Regime engine (src/regime)
  → TreeGate (src/gating) → Weight smoothing → Fallback renormalization
  → Weighted blend (src/blending) → Disagreement
  → Confidence + Uncertainty (src/confidence) → Extremes (src/extremes) → RPI (src/risk)
  → Evaluation (src/evaluation) → Artifacts (data/artifacts)
  → FastAPI (api/) → Streamlit dashboard (dashboard/)
```

All state is artifact-based: `data/artifacts/*.parquet`, `run_history.jsonl`,
`models/metadata/registry.json`. No database is required for the MVP.

Real-data seams: `ForecastSource` / `ObservationSource` in `src/ingestion/ingest.py`.
