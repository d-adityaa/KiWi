"""Deterministic data-quality checks."""
from __future__ import annotations
import pandas as pd

VALID_RANGES = {
    "rainfall": (0, 500),
    "temperature": (-20, 60),
    "wind": (0, 60),
}


def qc_forecasts(df: pd.DataFrame) -> dict:
    report = {"missing_values": int(df["forecast_value"].isna().sum()) if "forecast_value" in df else len(df),
              "duplicates": int(df.duplicated().sum()),
              "invalid_ranges": 0,
              "invalid_timestamps": 0,
              "unit_mismatch": 0,
              "missing_source": int(df["source_id"].isna().sum()) if "source_id" in df else len(df),
              "missing_coordinates": int(df[["latitude", "longitude"]].isna().any(axis=1).sum()),
              "broken_cycles": 0,
              "insufficient_ensemble": 0}
    if "variable" in df and "forecast_value" in df:
        for var, (lo, hi) in VALID_RANGES.items():
            sub = df[df["variable"] == var]["forecast_value"]
            report["invalid_ranges"] += int(((sub < lo) | (sub > hi)).sum())
    if "initialization_time" in df and "valid_time" in df:
        dt = (pd.to_datetime(df["valid_time"]) - pd.to_datetime(df["initialization_time"])).dt.total_seconds() / 3600
        report["invalid_timestamps"] = int((pd.to_datetime(df["valid_time"]) <= pd.to_datetime(df["initialization_time"])).sum())
        report["broken_cycles"] = int((dt != df["lead_time"]).sum())
    unit_map = {"rainfall": "mm", "temperature": "degC", "wind": "m/s"}
    if "variable" in df and "unit" in df:
        exp = df["variable"].map(unit_map)
        report["unit_mismatch"] = int((df["unit"] != exp).sum())
    if "ensemble_member" in df and "source_id" in df:
        ens = df[df["source_id"] == "ENS"]
        counts = ens.groupby(["valid_time", "lead_time", "cell_id", "variable"])["ensemble_member"].nunique()
        report["insufficient_ensemble"] = int((counts < 4).sum())
    fails = {k: v for k, v in report.items() if isinstance(v, int) and v > 0}
    report["status"] = "PASS" if sum(fails.values()) == 0 else "WARN"
    report["issues"] = fails
    return report
