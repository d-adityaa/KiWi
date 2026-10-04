"""Prototype Risk Priority Index (RPI), explicit and explainable."""
from __future__ import annotations
import pandas as pd

from src import config


def _cat(v):
    c = config.thresholds()["rpi"]["categories"]
    if v <= c["low_max"]:
        return "LOW"
    if v <= c["moderate_max"]:
        return "MODERATE"
    if v <= c["high_max"]:
        return "HIGH"
    return "CRITICAL"


def compute_rpi(events: pd.DataFrame, confidence: pd.Series, persistence: pd.Series | None = None) -> pd.DataFrame:
    w = config.thresholds()["rpi"]["weights"]
    out = events.copy()
    prob = out["probability"].fillna(0.0) if "probability" in out else pd.Series(0.0, index=out.index)
    conf = confidence.reindex(out.index).fillna(50.0)
    if persistence is None:
        persistence = pd.Series(50.0, index=out.index)
    severity = out["forecast"].clip(lower=0)
    sev_scaled = (severity / severity.max() * 100) if severity.max() > 0 else severity * 0
    rpi = (w["probability"] * prob * 100 +
           w["severity"] * sev_scaled +
           w["confidence_inverse"] * (100 - conf) +
           w["persistence"] * persistence.reindex(out.index).fillna(50.0))
    out["risk_priority_score"] = rpi.clip(0, 100).round(1)
    out["risk_category"] = out["risk_priority_score"].map(_cat)
    out["label"] = "PROTOTYPE RPI — not an official disaster score"
    return out
