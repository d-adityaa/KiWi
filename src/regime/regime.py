"""Deterministic prototype regime classifier (DEMO rules)."""
from __future__ import annotations
import pandas as pd

REGIME_VERSION = "regime-1.0"


def classify(row) -> str:
    rain = float(row.get("rainfall", 0))
    temp = float(row.get("temperature", 25))
    wind = float(row.get("wind", 0))
    humid = float(row.get("humidity", 60))
    if rain >= 64:
        return "Heavy Rain"
    if wind >= 12:
        return "High Wind"
    if temp >= 40:
        return "Heatwave"
    if rain >= 15 and humid >= 70:
        return "Convective"
    if rain >= 1:
        return "Normal Rain"
    if temp >= 38 and rain < 1:
        return "Heatwave"
    if rain < 1 and temp < 38:
        return "Stable"
    return "Transition"


def classify_frame(df: pd.DataFrame) -> pd.Series:
    return df.apply(classify, axis=1)
