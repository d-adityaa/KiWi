"""Canonical dataset schema validation (deterministic, simple)."""
from __future__ import annotations
import pandas as pd

FORECAST_REQUIRED = ["source_id", "source_type", "source_version", "initialization_time",
                     "valid_time", "lead_time", "lead_bucket", "latitude", "longitude",
                     "cell_id", "region", "variable", "forecast_value", "unit",
                     "ensemble_member", "regime", "metadata"]
OBS_REQUIRED = ["observation_time", "latitude", "longitude", "cell_id", "region",
                "variable", "observed_value", "unit", "quality_flag", "source"]


def check_schema(df: pd.DataFrame, required: list[str], name: str = "dataset") -> dict:
    missing = [c for c in required if c not in df.columns]
    return {"name": name, "ok": len(missing) == 0, "missing_columns": missing,
            "rows": int(len(df))}
