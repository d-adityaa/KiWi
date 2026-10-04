"""Forecast product export (CSV / JSON)."""
from __future__ import annotations
import io
import json
import pandas as pd

from src.constants import DATA_MODE


def product_record(row: dict) -> dict:
    row = dict(row)
    row["data_mode"] = DATA_MODE
    return row


def to_csv(df: pd.DataFrame) -> bytes:
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    return buf.getvalue().encode("utf-8")


def to_json(records: list[dict]) -> bytes:
    return json.dumps([product_record(r) for r in records], default=str, indent=2).encode("utf-8")
