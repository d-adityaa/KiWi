import sys
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from dashboard.utils.common import *  # noqa

bootstrap("Extreme Weather & Risk", "Prototype thresholds, prototype RPI")
sel = sidebar_filters(); sidebar_language()
from api.services import service
ev = service.events()
if ev.empty:
    no_data(); footer(); st.stop()

cols = [c for c in ["hazard", "probability", "forecast", "event_detected",
                    "risk_priority_score", "risk_category", "time_horizon_h"] if c in ev]
section("RISK EVENTS (CURRENT CYCLE)")
st.dataframe(ev[cols].sort_values("risk_priority_score", ascending=False, na_position="last"),
             use_container_width=True, hide_index=True)

section("TOP HAZARD DETAIL")
top = ev.sort_values("risk_priority_score", ascending=False).iloc[0] if "risk_priority_score" in ev else None
if top is not None:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Hazard", str(top.get("hazard")))
    pr = top.get("probability")
    c2.metric("Probability", f"{float(pr)*100:.0f}%" if pr == pr and pr is not None else "—")
    c3.metric("RPI", f"{top['risk_priority_score']:.0f} / 100")
    c4.metric("Category", str(top.get("risk_category")))
    bar_row("RPI", float(top["risk_priority_score"]))
    st.markdown("**WHY THIS RISK?**")
    fc = top.get("forecast")
    if fc is not None and fc == fc:
        st.markdown(f"- Forecast {fc:.1f} vs prototype threshold {top.get('threshold')}")
    pr = top.get("probability")
    if pr is not None and pr == pr:
        st.markdown(f"- ENS exceedance probability {float(pr)*100:.0f}%")
    st.markdown(f"- High uncertainty flag: {top.get('high_uncertainty')}")
    st.markdown(f"- Time horizon: {top.get('time_horizon_h')}h · data: DEMO / SYNTHETIC")

section("RPI DISTRIBUTION")
if "risk_priority_score" in ev:
    fig = px.histogram(ev, x="risk_priority_score", nbins=20, color_discrete_sequence=["#b07d2b"])
    fig.update_layout(**TEMPLATE["layout"], height=260)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("RPI = Risk Priority Index — prototype decision-support score, not an official disaster score.")

footer()
