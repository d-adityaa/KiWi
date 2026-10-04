"""Ingestion entry points + real-data adapter seams (interfaces only)."""
from __future__ import annotations
import pandas as pd


def load_forecasts(path) -> pd.DataFrame:
    return pd.read_parquet(path)


def load_observations(path) -> pd.DataFrame:
    return pd.read_parquet(path)


class ForecastSource:
    """Real-data seam. Demo sources do not implement this yet."""
    def fetch(self, variable: str, valid_time, lead_time: int) -> pd.DataFrame:
        raise NotImplementedError("Real source adapters are a future extension.")


class ObservationSource:
    def fetch(self, variable: str, start, end) -> pd.DataFrame:
        raise NotImplementedError("Real observation adapters are a future extension.")
