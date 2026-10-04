"""Contextual feature builder for the TreeGate error models."""
from __future__ import annotations
import numpy as np
import pandas as pd

from src.constants import SOURCES, VARIABLES

FEATURE_COLS = [
    "lead_time", "month", "latitude", "longitude", "humidity", "cape",
    "obs_climo_anom", "ens_spread", "model_disagreement", "recent_bias",
    "recent_mae", "regime_code", "season_code", "source_index_err",
]
REGIMES = ["Stable", "Normal Rain", "Convective", "Heavy Rain", "Heatwave", "High Wind", "Transition"]
SEASONS = ["winter", "pre_monsoon", "monsoon", "post_monsoon"]


def build_features(cases: pd.DataFrame, fc: pd.DataFrame, available_sources=None) -> pd.DataFrame:
    df = cases.copy()
    avail = available_sources or list(SOURCES.keys())
    src_cols = [s for s in avail if s in df.columns]
    # ensemble spread per case
    ens = (fc[fc["source_id"] == "ENS"]
           .groupby(["valid_time", "lead_time", "cell_id", "variable"])["forecast_value"]
           .std().rename("ens_spread").reset_index())
    df = df.merge(ens, on=["valid_time", "lead_time", "cell_id", "variable"], how="left")
    df["ens_spread"] = df["ens_spread"].fillna(df["ens_spread"].median() if df["ens_spread"].notna().any() else 1.0)
    mat = df[src_cols]
    df["model_disagreement"] = mat.std(axis=1).fillna(0.0)
    climo = df.groupby(["region", "month", "variable"])["observed_value"].transform("mean")
    df["obs_climo_anom"] = df["observed_value"] - climo
    for s in src_cols:
        df[f"{s}__abs_err"] = (df[s] - df["observed_value"]).abs()
    # recent error per source: mean abs err over previous 5 valid_times within same region/variable/lead
    for s in src_cols:
        g = df.sort_values("valid_time").groupby(["region", "variable", "lead_time", "source_id"] if False else ["region", "variable", "lead_time"])[f"{s}__abs_err"]
        df[f"{s}__recent_mae"] = g.transform(lambda x: x.shift().rolling(5, min_periods=1).mean())
        df[f"{s}__recent_bias"] = (df[s] - df["observed_value"]).groupby(
            [df["region"], df["variable"], df["lead_time"]]).transform(
                lambda x: x.shift().rolling(5, min_periods=1).mean())
    df["regime_code"] = df["regime"].map({r: i for i, r in enumerate(REGIMES)}).fillna(len(REGIMES) - 1)
    df["season_code"] = df["season"].map({s: i for i, s in enumerate(SEASONS)}).fillna(0)
    return df
