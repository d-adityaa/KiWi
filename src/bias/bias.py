"""Contextual rolling bias correction (deterministic).

b_corr = mean(forecast - obs) over history grouped by
(source, variable, region, lead_bucket). corrected = raw - b_corr.
"""
from __future__ import annotations
import numpy as np
import pandas as pd

BIAS_VERSION = "bias-1.0"


def compute_bias_table(cases: pd.DataFrame, sources: list[str]) -> pd.DataFrame:
    rows = []
    for s in sources:
        if s not in cases:
            continue
        agg = pd.DataFrame({"err": cases[s] - cases["observed_value"], "variable": cases["variable"], "region": cases["region"], "lead_time": cases["lead_time"]})
        for (var, region, lead), v in agg.groupby(["variable", "region", "lead_time"])["err"]:
            rows.append({"source_id": s, "variable": var, "region": region,
                         "lead_time": lead, "bias": float(v.mean()), "n": int(v.count())})
    return pd.DataFrame(rows)


def apply_bias_correction(cases: pd.DataFrame, bias_table: pd.DataFrame, sources: list[str]) -> pd.DataFrame:
    df = cases.copy()
    for s in sources:
        if s not in df:
            continue
        df[f"{s}__bias"] = 0.0
        key = bias_table[bias_table["source_id"] == s].set_index(["variable", "region", "lead_time"])["bias"]
        idx = list(zip(df["variable"], df["region"], df["lead_time"]))
        df[f"{s}__bias"] = pd.Series(idx, index=df.index).map(key).fillna(0.0).astype(float)
        df[f"{s}_corrected"] = df[s] - df[f"{s}__bias"]
    return df
