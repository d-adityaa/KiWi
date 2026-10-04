import sys
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from dashboard.utils.common import *  # noqa

bootstrap("Model Comparison", "All methods on identical synthetic cases")
sel = sidebar_filters(); sidebar_language()
from api.services import service
ev = service.evaluation()
if ev.empty:
    no_data(); footer(); st.stop()

section("EVALUATION TABLE")
order = ["GFS", "ECMWF", "IMD-WRF", "GraphCast", "Pangu", "ENS", "equal_avg", "best_single", "skill_gate", "treegate_kiwi"]
ev = ev.set_index("method")
ev = ev.loc[[m for m in order if m in ev.index]]
st.dataframe(ev.round(3), use_container_width=True)
st.caption("KiWi blend is labelled treegate_kiwi. Not declared superior by default.")

section("RMSE BY METHOD")
fig = px.bar(ev.reset_index(), x="method", y="rmse", color_discrete_sequence=["#3e6b8b"])
fig.update_traces(marker_line_color="#24282b", marker_line_width=0.5)
fig.update_layout(**TEMPLATE["layout"], height=300)
st.plotly_chart(fig, use_container_width=True)

section("UNCERTAINTY COVERAGE vs NOMINAL")
cov = service.coverage()
if not cov.empty:
    c = cov.copy()
    c["nominal"] = c["interval"].str.replace("%", "").astype(float) / 100
    c["coverage_pct"] = (c["coverage"] * 100).round(1)
    c["nominal_pct"] = (c["nominal"] * 100).round(0)
    st.dataframe(c[["interval", "coverage_pct", "nominal_pct", "avg_width"]], use_container_width=True, hide_index=True)

section("RECENT SKILL BY SOURCE (MAE)")
skill = service.skill()
if not skill.empty:
    agg = skill.groupby("source_id")[["mae", "rmse", "bias", "correlation"]].mean().round(3)
    st.dataframe(agg, use_container_width=True)

footer()
