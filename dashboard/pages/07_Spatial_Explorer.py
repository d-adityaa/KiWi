import sys
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from dashboard.utils.common import *  # noqa

bootstrap("Spatial Explorer", "Inspect individual synthetic grid cells")
sel = sidebar_filters(); sidebar_language()
from api.services import service
latest = service.latest()
sub = latest[(latest["variable"] == sel["variable"]) & (latest["region"] == sel["region"]) & (latest["lead_time"] == sel["lead"])]
if sub.empty:
    no_data(); footer(); st.stop()

section("GRID MAP")
fig = px.scatter(sub, x="longitude", y="latitude", color="forecast", hover_data=["cell_id", "region", "confidence"],
                 color_continuous_scale="Blues", size_max=8)
fig.update_traces(marker=dict(size=9, line=dict(width=0.5, color="#6b7177")))
fig.update_layout(**TEMPLATE["layout"], height=380)
st.plotly_chart(fig, use_container_width=True)

section("CELL DETAILS")
cell = st.selectbox("Cell", sorted(sub["cell_id"].unique()))
row = sub[sub["cell_id"] == cell].iloc[0]
left, right = st.columns(2)
with left:
    st.markdown(f"**Cell** `{row['cell_id']}` · Lat {row['latitude']} · Lon {row['longitude']} · Regime {row.get('regime')}")
    st.metric("Forecast", f"{row['forecast']:.2f}")
    st.caption(f"80% interval {row['lower_80']:.1f} – {row['upper_80']:.1f} · Confidence {row['confidence']:.0f}/100")
    if "observed_value" in row and row["observed_value"] == row["observed_value"]:
        st.caption(f"Observed (demo): {row['observed_value']:.2f}")
with right:
    wcols = [c for c in sub.columns if c.startswith("w_")]
    for c in sorted(wcols, key=lambda c: -float(row[c])):
        bar_row(c[2:], float(row[c]) * 100, color=SOURCE_COLORS.get(c[2:]))

section("RECENT SKILL AT THIS CONTEXT")
skill = service.skill()
if not skill.empty:
    s = skill[(skill["region"] == row["region"]) & (skill["variable"] == sel["variable"]) & (skill["lead_time"] == sel["lead"])]
    st.dataframe(s.groupby("source_id")[["mae", "rmse", "bias", "correlation"]].mean().round(3),
                 use_container_width=True)

footer()
