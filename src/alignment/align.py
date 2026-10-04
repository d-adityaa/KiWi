"""Temporal + spatial alignment: build the per-case wide table.

A case is (valid_time, lead_time, cell_id, region, variable). For each case we
pivot each source's (mean over ensemble members) forecast into a column.
"""
from __future__ import annotations
import pandas as pd


def align_cases(fc: pd.DataFrame, truth: pd.DataFrame) -> pd.DataFrame:
    # source mean forecast per case
    src = (fc.groupby(["valid_time", "lead_time", "cell_id", "region", "variable", "source_id"],
                      as_index=False)["forecast_value"].mean())
    wide = src.pivot_table(index=["valid_time", "lead_time", "cell_id", "region", "variable"],
                           columns="source_id", values="forecast_value").reset_index()
    wide.columns.name = None
    t = truth.rename(columns={
        "time": "valid_time",
        "rainfall": "obs_rainfall", "temperature": "obs_temperature", "wind": "obs_wind",
        "humidity": "humidity", "cape": "cape", "season": "season",
    })
    obs_long = t.melt(id_vars=["valid_time", "cell_id", "region", "latitude", "longitude", "humidity", "cape", "season"],
                      value_vars=["obs_rainfall", "obs_temperature", "obs_wind"],
                      var_name="v", value_name="observed_value")
    obs_long["variable"] = obs_long["v"].str.replace("obs_", "")
    obs_long = obs_long.drop(columns=["v"])
    cases = wide.merge(obs_long, on=["valid_time", "cell_id", "region", "variable"], how="left")
    cases = cases.merge(
        truth[["time", "cell_id", "regime"] if "regime" in truth.columns else ["time", "cell_id"]].rename(
            columns={"time": "valid_time"}),
        on=["valid_time", "cell_id"], how="left")
    cases["lead_bucket"] = cases["lead_time"]
    cases["month"] = cases["valid_time"].dt.month
    cases["case_id"] = (cases["valid_time"].dt.strftime("%Y%m%d") + "_" +
                        cases["lead_time"].astype(str) + "_" + cases["cell_id"] + "_" + cases["variable"])
    return cases
