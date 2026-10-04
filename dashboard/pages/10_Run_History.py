import sys
from pathlib import Path
import pandas as pd
import streamlit as st
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from dashboard.utils.common import *  # noqa

bootstrap("Run History", "Operational run log")
sidebar_language()
from src.runs.runs import list_runs
runs = list_runs()
if not runs:
    st.info("No runs recorded yet."); footer(); st.stop()

df = pd.DataFrame(runs)
show = [c for c in ["run_id", "timestamp", "region", "selected_variable", "gate", "status",
                    "available_sources", "fallback_events", "duration_s"] if c in df]
section("RUNS")
st.dataframe(df[show], use_container_width=True, hide_index=True)

section("INSPECT RUN")
rid = st.selectbox("Run", [r["run_id"] for r in runs])
r = next(r for r in runs if r["run_id"] == rid)
c1, c2, c3 = st.columns(3)
c1.metric("Status", str(r["status"]))
c2.metric("Gate", str(r["gate"]))
c3.metric("Duration", f"{r['duration_s']}s")
st.markdown(f"**Region:** {r.get('region')} · **Variable:** {r.get('selected_variable')}")
st.markdown(f"**Sources:** {', '.join(r.get('available_sources', []))}")
if r.get("fallback_events"):
    alert_strip("moderate", "FALLBACK", ", ".join(r["fallback_events"]))
st.json({k: v for k, v in r.items() if k not in ("timestamp",)})

footer()
