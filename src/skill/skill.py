"""Historical skill memory: MAE, RMSE, Bias, Correlation, extreme precision/recall/F1."""
from __future__ import annotations
import numpy as np
import pandas as pd

from src.constants import SOURCES, VARIABLES

EXTREME_THR = {"rainfall": 64.0, "temperature": 40.0, "wind": 12.0}


def _metrics(y_true, y_pred) -> dict:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    err = y_pred - y_true
    mae = float(np.mean(np.abs(err))) if len(err) else np.nan
    rmse = float(np.sqrt(np.mean(err ** 2))) if len(err) else np.nan
    bias = float(np.mean(err)) if len(err) else np.nan
    corr = float(np.corrcoef(y_true, y_pred)[0, 1]) if len(err) > 2 and np.std(y_true) > 0 and np.std(y_pred) > 0 else np.nan
    # extreme event skill
    thr = np.nan
    return {"mae": mae, "rmse": rmse, "bias": bias, "correlation": corr}


def event_skill(y_true, y_pred, thr) -> dict:
    a = np.asarray(y_true) >= thr
    b = np.asarray(y_pred) >= thr
    tp = int((a & b).sum()); fp = int((~a & b).sum()); fn = int((a & ~b).sum())
    prec = tp / (tp + fp) if tp + fp else np.nan
    rec = tp / (tp + fn) if tp + fn else np.nan
    f1 = 2 * prec * rec / (prec + rec) if (prec == prec and rec == rec and (prec + rec) > 0) else np.nan
    return {"precision": prec, "recall": rec, "f1": f1, "tp": tp, "fp": fp, "fn": fn}


def compute_skill(cases: pd.DataFrame, window: str = "long", available=None) -> pd.DataFrame:
    avail = available or list(SOURCES.keys())
    records = []
    for (region, variable, lead, regime), sub in cases.groupby(["region", "variable", "lead_time", "regime"]):
        y = sub["observed_value"].to_numpy()
        for s in avail:
            if s not in sub:
                continue
            p = sub[s].to_numpy()
            m = _metrics(y, p)
            es = event_skill(y, p, EXTREME_THR.get(variable, np.inf))
            records.append({"source_id": s, "variable": variable, "region": region,
                            "lead_time": lead, "regime": regime, "window": window,
                            "sample_count": int(len(sub)), **m, **{k: es[k] for k in ("precision", "recall", "f1")},
                            "version": "skill-1.0", "timestamp": str(pd.Timestamp.now("UTC"))})
    return pd.DataFrame(records)


def recent_skill(cases: pd.DataFrame, source: str, variable: str, lead: int, region: str, days: int = 3) -> dict:
    sub = cases[(cases["variable"] == variable) & (cases["lead_time"] == lead) & (cases["region"] == region)]
    if sub.empty or source not in sub:
        return {"mae": np.nan, "rmse": np.nan, "samples": 0}
    cutoff = sub["valid_time"].max() - pd.Timedelta(days=days)
    sub = sub[sub["valid_time"] >= cutoff]
    y = sub["observed_value"].to_numpy(); p = sub[source].to_numpy()
    return {"mae": float(np.mean(np.abs(p - y))), "rmse": float(np.sqrt(np.mean((p - y) ** 2))), "samples": int(len(sub))}
