import sys
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from dashboard.utils.common import *  # noqa

bootstrap("Lead-Time Performance", "Skill degradation with forecast lead")
sel = sidebar_filters(); sidebar_language()
from api.services import service
skill = service.skill()
if skill.empty:
    no_data(); footer(); st.stop()

section("RMSE — SOURCE × LEAD (HEATMAP)")
tab = skill.pivot_table(index="source_id", columns="lead_time", values="rmse", aggfunc="mean")
fig = px.imshow(tab, aspect="auto", color_continuous_scale="Blues")
fig.update_layout(**TEMPLATE["layout"], height=300)
st.plotly_chart(fig, use_container_width=True)

section("MAE vs LEAD TIME")
mae = skill.pivot_table(index="lead_time", columns="source_id", values="mae", aggfunc="mean")
fig2 = px.line(mae, markers=True)
fig2.update_layout(**TEMPLATE["layout"], height=300, legend=dict(orientation="h", y=-0.2))
st.plotly_chart(fig2, use_container_width=True)

section("KIWI BLEND vs SOURCES (RMSE by lead)")
ev = service.evaluation()
st.caption("Aggregate across leads in evaluation artifact; see Model Comparison for the metric table.")
if not ev.empty:
    fig3 = px.bar(ev, x="method", y="mae", color_discrete_sequence=["#3e6b8b"])
    fig3.update_layout(**TEMPLATE["layout"], height=280)
    st.plotly_chart(fig3, use_container_width=True)

footer()
