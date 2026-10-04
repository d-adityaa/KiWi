"""Weighted blend + disagreement + fallback handling."""
from __future__ import annotations
import numpy as np
import pandas as pd

from src.constants import SOURCES


def blend(cases: pd.DataFrame, weights: pd.DataFrame, sources: list[str], use_corrected: bool = True) -> pd.Series:
    total = pd.Series(0.0, index=cases.index)
    wsum = pd.Series(0.0, index=cases.index)
    for s in sources:
        col = f"{s}_corrected" if use_corrected and f"{s}_corrected" in cases else s
        if col not in cases or f"w_{s}" not in weights:
            continue
        w = weights[f"w_{s}"].reindex(cases.index).fillna(0.0)
        total = total + w * cases[col].astype(float)
        wsum = wsum + w
    total = total / wsum.replace(0, np.nan)
    return total


def disagreement(cases: pd.DataFrame, sources: list[str], use_corrected: bool = True) -> pd.DataFrame:
    cols = [(s + "_corrected") if use_corrected and (s + "_corrected") in cases else s for s in sources]
    cols = [c for c in cols if c in cases]
    mat = cases[cols].astype(float)
    std = mat.std(axis=1)
    rng = mat.max(axis=1) - mat.min(axis=1)
    q75 = mat.quantile(0.75, axis=1); q25 = mat.quantile(0.25, axis=1)
    iqr = q75 - q25
    return pd.DataFrame({"disagreement_std": std, "disagreement_range": rng, "disagreement_iqr": iqr})


def disagreement_score(std: pd.Series, variable: str) -> pd.Series:
    """Prototype 0-100 score, scaled by a variable-dependent denominator."""
    denom = {"rainfall": 25.0, "temperature": 4.0, "wind": 3.0}.get(variable, 10.0)
    return (std / denom * 100).clip(0, 100)


def apply_fallback(weights: pd.DataFrame, available: list[str]) -> tuple[pd.DataFrame, dict]:
    """Zero-out unavailable sources and renormalize (deterministic, no crash)."""
    out = weights.copy()
    dropped = []
    for c in list(out.columns):
        if c.startswith("w_"):
            sid = c[2:]
            if sid not in available:
                out[c] = 0.0
                dropped.append(sid)
    wcols = [c for c in out.columns if c.startswith("w_")]
    if wcols:
        s = out[wcols].sum(axis=1).replace(0, np.nan)
        out[wcols] = out[wcols].div(s, axis=0).fillna(0.0)
    event = {"disabled": dropped, "active": [s for s in available], "fallback_active": len(dropped) > 0}
    return out, event
