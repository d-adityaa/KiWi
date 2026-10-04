import sys
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from dashboard.utils.common import *  # noqa

bootstrap("Trust Atlas", "Where each source is trusted")
sel = sidebar_filters(); sidebar_language()
from api.services import service
latest = service.latest()
if latest.empty:
    no_data(); footer(); st.stop()

sub = latest[(latest["variable"] == sel["variable"]) & (latest["lead_time"] == sel["lead"])]
if sel["regime"] != "All":
    sub = sub[sub["regime"] == sel["regime"]]
wcols = [c for c in sub.columns if c.startswith("w_")]
mean_w = sub[wcols].mean().sort_values(ascending=False)
if len(mean_w) >= 2:
    top, second = mean_w.index[0][2:], mean_w.index[1][2:]
    c1, c2, c3 = st.columns(3)
    c1.metric("Dominant source", top)
    c2.metric("Weight", f"{mean_w.iloc[0]*100:.1f}%")
    c3.metric("Trust gap", f"{(mean_w.iloc[0]-mean_w.iloc[1])*100:.1f} pts vs {second}")

section("REGIONAL TRUST MAP (bar stack by region)")
agg = sub.groupby("region")[wcols].mean().reset_index()
long = agg.melt(id_vars="region", var_name="source", value_name="weight")
long["source"] = long["source"].str[2:]
fig = px.bar(long, x="region", y="weight", color="source", barmode="stack")
fig.update_layout(**TEMPLATE["layout"], height=320)
st.plotly_chart(fig, use_container_width=True)

section("WEIGHT RANKING")
for c, v in mean_w.items():
    bar_row(c[2:], v * 100)

section("CELL-LEVEL DOMINANT SOURCE")
dom = sub.copy()
dom["dominant"] = dom[wcols].idxmax(axis=1).str[2:]
fig2 = px.scatter(dom, x="longitude", y="latitude", color="dominant",
                  hover_data=["cell_id", "region", "forecast", "confidence"],
                  color_discrete_sequence=PALETTE)
fig2.update_layout(**TEMPLATE["layout"], height=380)
st.plotly_chart(fig2, use_container_width=True)
st.caption("Each marker is a synthetic grid cell; colour = highest-weight source.")

footer()
