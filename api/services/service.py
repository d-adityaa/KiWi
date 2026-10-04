"""Artifact loading service shared by API and dashboard."""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd

from src.constants import DATA_ARTIFACTS, MODELS_METADATA


def _pq(name) -> pd.DataFrame:
    p = DATA_ARTIFACTS / name
    if not p.exists():
        return pd.DataFrame()
    return pd.read_parquet(p)


def records(df: pd.DataFrame) -> list[dict]:
    if df.empty:
        return []
    return df.astype(object).where(pd.notna(df), None).to_dict("records")


def latest() -> pd.DataFrame: return _pq("latest.parquet")
def cases() -> pd.DataFrame: return _pq("cases.parquet")
def forecasts() -> pd.DataFrame: return _pq("forecasts.parquet")
def skill() -> pd.DataFrame: return _pq("skill_long.parquet")
def weights() -> pd.DataFrame: return _pq("weights.parquet")
def uncertainty() -> pd.DataFrame: return _pq("uncertainty.parquet")
def evaluation() -> pd.DataFrame: return _pq("evaluation.parquet")
def coverage() -> pd.DataFrame: return _pq("coverage.parquet")
def events() -> pd.DataFrame: return _pq("risk_events.parquet")
def disagreement() -> pd.DataFrame: return _pq("disagreement.parquet")
def health() -> pd.DataFrame: return _pq("data_health.parquet")
def bias_table() -> pd.DataFrame: return _pq("bias_table.parquet")


def registry() -> dict:
    p = MODELS_METADATA / "registry.json"
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def runs() -> list[dict]:
    from src.runs.runs import list_runs
    return list_runs()
