"""Deterministic, metric-based explainability (no LLM)."""
from __future__ import annotations
import pandas as pd


def explain_weights(source_weights: dict, skill: pd.DataFrame, variable: str, region: str,
                    regime: str, lead: int) -> dict:
    """source_weights: {source: weight}. skill: long skill table."""
    out = {}
    sk = skill[(skill["variable"] == variable) & (skill["region"] == region) &
               (skill["lead_time"] == lead) & (skill["regime"] == regime)]
    for src, w in sorted(source_weights.items(), key=lambda kv: -kv[1]):
        row = sk[sk["source_id"] == src]
        reasons = []
        if not row.empty:
            mae = row["mae"].iloc[0]
            if mae == mae:
                reasons.append(f"mean absolute error {mae:.2f} for this regime")
            f1 = row["f1"].iloc[0] if "f1" in row else float("nan")
            if f1 == f1:
                reasons.append(f"extreme-event F1 {f1:.2f}")
            n = int(row["sample_count"].iloc[0])
            reasons.append(f"{n} historical samples")
        else:
            reasons.append("limited historical samples for this context")
        out[src] = {"weight": round(w * 100, 1), "reasons": reasons}
    return out


def explain_confidence(disagreement_score: float, recent_rmse: float, sample_count: int,
                       fallback_active: bool, regime: str, confidence: float) -> list[str]:
    reasons = []
    if disagreement_score < 25:
        reasons.append("Sources are in close agreement (low disagreement).")
    elif disagreement_score < 55:
        reasons.append("Sources show moderate disagreement.")
    else:
        reasons.append("Sources disagree strongly; forecast is less certain.")
    if recent_rmse < 3:
        reasons.append("Blend error over the recent window has been small.")
    else:
        reasons.append("Recent blend error has been elevated.")
    if sample_count >= 50:
        reasons.append("Adequate historical sample count supports the calibration.")
    else:
        reasons.append("Historical sample count is limited; intervals are wider.")
    if fallback_active:
        reasons.append("One or more sources are unavailable (fallback active).")
    if regime in {"Convective", "Heavy Rain", "Heatwave", "High Wind"}:
        reasons.append(f"Current regime ({regime}) historically carries higher uncertainty.")
    return reasons
