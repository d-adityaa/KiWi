"""Deterministic, demo-calibrated confidence + conformal-style intervals.

Intervals: for each (variable, lead_bucket), compute recent residual
absolute values of the KiWi blend vs observations over a rolling window,
then take empirical quantiles -> 50/80/95 intervals. This is measurable
(coverage) and deterministic. Confidence is derived from disagreement,
recent blend error, sample count, and fallback state — not random.
"""
from __future__ import annotations
import numpy as np
import pandas as pd

CAL_VERSION = "calibration-1.0"


def interval_quantiles(residuals: pd.Series, levels=(0.50, 0.80, 0.95)) -> dict:
    r = residuals.dropna().abs()
    if len(r) < 5:
        return {lv: np.nan for lv in levels}
    return {lv: float(np.quantile(r, lv)) for lv in levels}


def compute_intervals(eval_rows: pd.DataFrame) -> pd.DataFrame:
    """eval_rows: case_id, variable, lead_time, residual_kiwi rows."""
    rows = []
    for (var, lead), sub in eval_rows.groupby(["variable", "lead_time"]):
        qs = interval_quantiles(sub["residual"])
        rows.append({"variable": var, "lead_time": lead,
                     **{f"q{int(lv*100)}": qs[lv] for lv in qs}})
    return pd.DataFrame(rows)


def confidence_score(disagreement_score: pd.Series, recent_blend_rmse: pd.Series,
                     sample_count: pd.Series, fallback_active: bool,
                     regime: pd.Series | None = None) -> pd.Series:
    s = pd.Series(100.0, index=disagreement_score.index)
    s = s - disagreement_score.clip(0, 100) * 0.35
    s = s - (recent_blend_rmse.fillna(recent_blend_rmse.median()).clip(0, 30) / 30 * 100) * 0.30
    sparse = (sample_count.fillna(0) < 20).astype(float) * 100 * 0.20
    s = s - sparse
    if fallback_active:
        s = s - 100 * 0.15
    if regime is not None:
        s = s - regime.isin(["Convective", "Heavy Rain", "Heatwave", "High Wind"]).astype(float) * 8
    return s.clip(0, 100).round(1)


def attach_uncertainty(cases: pd.DataFrame, blend: pd.Series, interval_table: pd.DataFrame,
                       disagreement_score: pd.Series, recent_rmse: pd.Series,
                       sample_count: pd.Series, fallback_active: bool) -> pd.DataFrame:
    out = cases[["case_id", "variable", "lead_time", "region", "cell_id", "valid_time",
                 "observed_value", "regime"]].copy()
    out["forecast"] = blend.round(2)
    for lv, col in ((50, "q50"), (80, "q80"), (95, "q95")):
        wdt = interval_table.set_index(["variable", "lead_time"])[col] if not interval_table.empty else pd.Series(dtype=float)
        w = out.set_index(["variable", "lead_time"]).index.map(wdt) if len(wdt) else np.nan
        out[f"half_{col}"] = pd.Series(w, index=out.index).fillna(out["forecast"].abs().median() * 0.1 + 1.0)
    out["lower_50"] = (out["forecast"] - out["half_q50"]).round(2)
    out["upper_50"] = (out["forecast"] + out["half_q50"]).round(2)
    out["lower_80"] = (out["forecast"] - out["half_q80"]).round(2)
    out["upper_80"] = (out["forecast"] + out["half_q80"]).round(2)
    out["lower_95"] = (out["forecast"] - out["half_q95"]).round(2)
    out["upper_95"] = (out["forecast"] + out["half_q95"]).round(2)
    out["disagreement_score"] = disagreement_score.round(1)
    out["confidence"] = confidence_score(disagreement_score, recent_rmse, sample_count,
                                         fallback_active, out["regime"])
    out["interval_width_80"] = (out["upper_80"] - out["lower_80"]).round(2)
    out["calibration_version"] = CAL_VERSION
    out["data_mode"] = "DEMO"
    return out
