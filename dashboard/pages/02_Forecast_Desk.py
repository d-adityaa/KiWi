import sys
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from dashboard.utils.common import *  # noqa

bootstrap("Forecast Desk", "Per-case blend composition and corrections")
sel = sidebar_filters(); sidebar_language()
from api.services import service
latest = service.latest()
sub = latest[(latest["variable"] == sel["variable"]) & (latest["region"] == sel["region"]) & (latest["lead_time"] == sel["lead"])]
if sub.empty:
    no_data(); footer(); st.stop()
row = sub.iloc[len(sub) // 2]

section("CURRENT PRODUCT")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Forecast", f"{row['forecast']:.2f}")
c2.metric("Confidence", f"{row['confidence']:.0f} / 100")
c3.metric("80% interval", f"{row['lower_80']:.0f} – {row['upper_80']:.0f}")
c4.metric("Agreement", agreement_word(row.get("disagreement_score")))
st.caption(f"Regime: {row.get('regime')} · Disagreement {row.get('disagreement_score', float('nan')):.0f}/100 · "
           f"Interval width {row.get('interval_width_80', float('nan')):.1f}")

section("SOURCE COMPOSITION")
wcols = [c for c in sub.columns if c.startswith("w_")]
rows = []
for w in wcols:
    sid = w[2:]
    raw = row.get(sid); corr = row.get(f"{sid}_corrected")
    weight = float(row[w])
    rows.append({"Source": sid, "Raw": raw, "Corrected": corr,
                 "Weight %": round(weight * 100, 1),
                 "Contribution": round(weight * corr, 2) if corr == corr else None})
comp = pd.DataFrame(rows)
st.dataframe(comp, use_container_width=True, hide_index=True)
total = sum(r["Contribution"] or 0 for r in rows)
st.caption(f"Weighted sum of corrected contributions: {total:.2f}  vs  KiWi forecast: {row['forecast']:.2f}")

section("UNCERTAINTY")
for lv, lo, hi in (("50%", row["lower_50"], row["upper_50"]),
                   ("80%", row["lower_80"], row["upper_80"]),
                   ("95%", row["lower_95"], row["upper_95"])):
    st.markdown(f"**{lv} interval** &nbsp; {lo:.1f} – {hi:.1f}")
    bar_row(f"Width ({lv})", min(100, (hi - lo) / max(1e-6, abs(row['forecast']) + 1) * 100), muted=True)

section("MODEL DISAGREEMENT")
bar_row("Disagreement score", float(row.get("disagreement_score", 0)))
st.caption(f"Interpretation: {agreement_word(row.get('disagreement_score'))} source agreement")

footer()
