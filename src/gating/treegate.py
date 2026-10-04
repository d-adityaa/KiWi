"""Adaptive TreeGate: per variable×source HistGradientBoostingRegressor
predicting expected normalized abs error -> softmax weights (sum to 1)."""
from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor

from src.constants import SOURCES, VARIABLES, TREEGATE_VERSION

TEMPERATURE = 0.5


def _softmax(x, T=TEMPERATURE):
    x = np.asarray(x, dtype=float)
    x = -(x - np.nanmin(x)) / max(T, 1e-6)
    e = np.exp(x - np.max(x))
    return e / e.sum()


def train_treegate(feats: pd.DataFrame, sources: list[str], variable: str) -> dict:
    models = {}
    for s in sources:
        col = f"{s}__abs_err"
        if col not in feats:
            continue
        X = feats[["lead_time", "month", "latitude", "longitude", "humidity", "cape",
                   "obs_climo_anom", "ens_spread", "model_disagreement", "regime_code",
                   "season_code"]].copy()
        # add source-specific recent skill if present
        recent = feats.get(f"{s}__recent_mae")
        if recent is not None:
            X["recent_mae"] = recent
            recent_bias = feats.get(f"{s}__recent_bias")
            X["recent_bias"] = recent_bias if recent_bias is not None else 0.0
        else:
            X["recent_mae"] = 0.0
            X["recent_bias"] = 0.0
        y = feats[col].astype(float)
        ok = y.notna() & X.notna().all(axis=1)
        if ok.sum() < 20:
            continue
        m = HistGradientBoostingRegressor(max_iter=80, max_depth=5, learning_rate=0.08,
                                          l2_regularization=0.1, random_state=0)
        m.fit(X[ok], y[ok])
        models[s] = m
    return models


def predict_weights(models: dict, feats: pd.DataFrame, sources: list[str]) -> pd.DataFrame:
    """Return per-case weight columns w_<source> over provided sources."""
    preds = {}
    for s, m in models.items():
        X = pd.DataFrame({"lead_time": feats["lead_time"], "month": feats["month"],
                          "latitude": feats["latitude"], "longitude": feats["longitude"],
                          "humidity": feats["humidity"], "cape": feats["cape"],
                          "obs_climo_anom": feats["obs_climo_anom"], "ens_spread": feats["ens_spread"],
                          "model_disagreement": feats["model_disagreement"],
                          "regime_code": feats["regime_code"], "season_code": feats["season_code"],
                          "recent_mae": feats.get(f"{s}__recent_mae", pd.Series(0.0, index=feats.index)),
                          "recent_bias": feats.get(f"{s}__recent_bias", pd.Series(0.0, index=feats.index))})
        preds[s] = m.predict(X)
    keys = list(preds.keys())
    M = np.column_stack([preds[s] for s in keys]).astype(float)
    M = -(M - np.nanmin(M, axis=1, keepdims=True)) / max(TEMPERATURE, 1e-6)
    e = np.exp(M - np.max(M, axis=1, keepdims=True))
    W = e / e.sum(axis=1, keepdims=True)
    weights = pd.DataFrame({f"w_{s}": W[:, j] for j, s in enumerate(keys)}, index=feats.index)
    return weights.fillna(0.0)


def smooth_weights(current: pd.DataFrame, previous: pd.DataFrame | None, alpha: float = 0.6) -> pd.DataFrame:
    """alpha in (0,1]: fraction of the new weight; blends with previous smoothed weight."""
    if previous is None or previous.empty:
        return current.copy()
    out = current.copy()
    for c in out.columns:
        if c in previous.columns and len(previous) == len(current):
            out[c] = alpha * current[c].to_numpy() + (1 - alpha) * previous[c].to_numpy()
    # renormalize rows over available weight columns
    wcols = [c for c in out.columns if c.startswith("w_")]
    if wcols:
        s = out[wcols].sum(axis=1).replace(0, np.nan)
        out[wcols] = out[wcols].div(s, axis=0)
    return out
