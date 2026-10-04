"""Model comparison metrics across sources and KiWi blend."""
from __future__ import annotations
import numpy as np
import pandas as pd

from src.skill.skill import _metrics, event_skill, EXTREME_THR


def method_forecasts(cases: pd.DataFrame, weights: pd.DataFrame, blend: pd.Series, sources: list[str]) -> pd.DataFrame:
    out = cases[["case_id", "valid_time", "variable", "region", "lead_time", "regime", "observed_value"]].copy()
    for s in sources:
        col = s + "_corrected" if s + "_corrected" in cases else s
        if col in cases:
            out[s] = cases[col].to_numpy()
    avail = [s for s in sources if s in out]
    if avail:
        out["equal_avg"] = out[avail].mean(axis=1)
        mae = {s: float(np.mean(np.abs(out[s] - out["observed_value"]))) for s in avail}
        out["best_single"] = out[min(mae, key=mae.get)]
        # skill-only softmax gate: weight by inverse long-term MAE
        inv = {s: 1.0 / (mae[s] + 1e-6) for s in avail}
        tot = sum(inv.values())
        out["skill_gate"] = sum(out[s] * (inv[s] / tot) for s in avail)
    out["treegate_kiwi"] = blend.to_numpy()
    return out


def evaluate_methods(method_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    methods = [c for c in method_df.columns if c in
               ["equal_avg", "best_single", "skill_gate", "treegate_kiwi"] or c in method_df.columns]
    skip = {"case_id", "valid_time", "variable", "region", "lead_time", "regime", "observed_value"}
    for m in method_df.columns:
        if m in skip:
            continue
        met = _metrics(method_df["observed_value"], method_df[m])
        rows.append({"method": m, **met})
    return pd.DataFrame(rows)


def coverage_table(uncertainty: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col, lv in ((50, 50), (80, 80), (95, 95)):
        if f"lower_{col}" not in uncertainty:
            continue
        inside = ((uncertainty["observed_value"] >= uncertainty[f"lower_{col}"]) &
                  (uncertainty["observed_value"] <= uncertainty[f"upper_{col}"]))
        rows.append({"interval": f"{lv}%", "coverage": float(inside.mean()),
                     "avg_width": float((uncertainty[f"upper_{col}"] - uncertainty[f"lower_{col}"]).mean())})
    return pd.DataFrame(rows)
