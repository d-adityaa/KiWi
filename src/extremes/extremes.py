"""Prototype extreme-event detection + probability from ENS member spread."""
from __future__ import annotations
import numpy as np
import pandas as pd

from src import config


def _thresholds():
    return config.thresholds().get("extremes", {})


def ens_probability(fc: pd.DataFrame, valid_time, lead: int, cell_id: str,
                    variable: str, threshold: float) -> float:
    sub = fc[(fc["source_id"] == "ENS") & (fc["valid_time"] == valid_time) &
             (fc["lead_time"] == lead) & (fc["cell_id"] == cell_id) & (fc["variable"] == variable)]
    if sub.empty:
        return float("nan")
    return float((sub["forecast_value"] >= threshold).mean())


def detect_events(blend_rows: pd.DataFrame, fc: pd.DataFrame) -> pd.DataFrame:
    th = _thresholds()
    rows = []
    for _, r in blend_rows.iterrows():
        var = r["variable"]
        if var == "rainfall":
            thr = th["rainfall"]["heavy_rain_mm"]; hazard = "Heavy Rain"
            prob = ens_probability(fc, r["valid_time"], r["lead_time"], r["cell_id"], var, thr)
            hit = r["forecast"] >= thr
        elif var == "temperature":
            thr = th["temperature"]["heatwave_degC"]; hazard = "Heatwave"
            prob = ens_probability(fc, r["valid_time"], r["lead_time"], r["cell_id"], var, thr)
            hit = r["forecast"] >= thr
        elif var == "wind":
            thr = th["wind"]["high_wind_ms"]; hazard = "High Wind"
            prob = ens_probability(fc, r["valid_time"], r["lead_time"], r["cell_id"], var, thr)
            hit = r["forecast"] >= thr
        else:
            continue
        unc_hit = r["interval_width_80"] > max(1e-6, abs(r["forecast"])) * 0.5 if pd.notna(r.get("interval_width_80")) else False
        rows.append({"case_id": r["case_id"], "hazard": hazard, "variable": var,
                     "threshold": thr, "forecast": r["forecast"], "event_detected": bool(hit),
                     "probability": round(prob, 3) if prob == prob else None,
                     "high_uncertainty": bool(unc_hit),
                     "time_horizon_h": int(r["lead_time"]),
                     "data_mode": "DEMO"})
    return pd.DataFrame(rows)
