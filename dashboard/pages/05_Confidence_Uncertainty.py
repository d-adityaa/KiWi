import sys
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from dashboard.utils.common import *  # noqa

bootstrap("Confidence & Uncertainty", "Calibrated, measurable, labelled DEMO")
sel = sidebar_filters(); sidebar_language()
from api.services import service
from src.explain.explain import explain_confidence
latest = service.latest()
sub = latest[(latest["variable"] == sel["variable"]) & (latest["region"] == sel["region"]) & (latest["lead_time"] == sel["lead"])]
if sub.empty:
    no_data(); footer(); st.stop()
row = sub.iloc[len(sub) // 2]

section("CURRENT PRODUCT")
c1, c2, c3 = st.columns(3)
c1.metric("Forecast", f"{row['forecast']:.2f}")
c2.metric("Confidence", f"{row['confidence']:.0f} / 100")
c3.metric("Agreement", agreement_word(row.get("disagreement_score")))

section("INTERVALS")
for lv, lo, hi in (("50%", row["lower_50"], row["upper_50"]),
                   ("80%", row["lower_80"], row["upper_80"]),
                   ("95%", row["lower_95"], row["upper_95"])):
    bar_row(f"{lv} interval  {lo:.1f} – {hi:.1f}", min(100, (hi - lo) / max(1e-6, abs(row['forecast']) + 1) * 100), muted=True)
bar_row("Model disagreement", float(row.get("disagreement_score", 0)))

section("WHY IS CONFIDENCE WHAT IT IS?")
reasons = explain_confidence(float(row.get('disagreement_score', 50)), 5.0, int(len(sub)), False,
                             str(row.get('regime')), float(row['confidence']))
for r in reasons:
    st.markdown(f"- {r}")

section("COVERAGE vs NOMINAL")
cov = service.coverage()
if not cov.empty:
    st.dataframe(cov, use_container_width=True, hide_index=True)

section("HISTORICAL CONFIDENCE DISTRIBUTION")
unc = service.uncertainty()
if not unc.empty and "confidence" in unc:
    fig = px.histogram(unc, x="confidence", nbins=24, color_discrete_sequence=["#3e6b8b"])
    fig.update_layout(**TEMPLATE["layout"], height=260)
    st.plotly_chart(fig, use_container_width=True)

section("INTERVAL WIDTH BY LEAD TIME")
if not unc.empty and {"interval_width_80", "lead_time"} <= set(unc.columns):
    g = unc.groupby("lead_time")["interval_width_80"].mean().reset_index()
    fig2 = px.line(g, x="lead_time", y="interval_width_80", markers=True)
    fig2.update_layout(**TEMPLATE["layout"], height=260)
    st.plotly_chart(fig2, use_container_width=True)

footer()
