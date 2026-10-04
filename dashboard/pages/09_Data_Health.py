import sys
from pathlib import Path
import pandas as pd
import streamlit as st
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from dashboard.utils.common import *  # noqa

bootstrap("Data Health", "Feed status, QC, missingness, fallback")
sidebar_language()
from api.services import service
h = service.health()
if h.empty:
    no_data(); footer(); st.stop()

section("SOURCE STATUS")
for _, r in h.iterrows():
    fb = " · FALLBACK ACTIVE" if r["fallback_active"] else ""
    st.markdown(f"{status_pill(bool(r['available']))} &nbsp; **{r['source_id']}** "
                f"<span style='color:#8a8f94'>· {r['source_type']} · {r['version']} · QC {r['qc_status']} · "
                f"missing {r['missing_pct']}% · {r['rows']} rows · {r['cells']} cells{fb}</span>",
                unsafe_allow_html=True)

section("PIPELINE")
from src.runs.runs import list_runs
runs = list_runs(limit=1)
if runs:
    r = runs[0]
    st.markdown(f"**Last completed run:** `{r['run_id']}` · status {r['status']} · gate {r['gate']} · "
                f"duration {r['duration_s']}s")
    st.markdown(f"**Available sources:** {', '.join(r.get('available_sources', []))}")
    if r.get("fallback_events"):
        alert_strip("moderate", "FALLBACK EVENTS", ", ".join(r["fallback_events"]))
    else:
        alert_strip("ok", "ALL FEEDS NOMINAL", "No fallback events in the last run.")

section("SIMULATE FEED FAILURE (DEMO DIAGNOSTICS)")
disabled = st.multiselect("Disable sources", ["GFS", "ECMWF", "IMD-WRF", "GraphCast", "Pangu", "ENS"])
if st.button("Apply fallback"):
    import requests
    r = requests.post("http://127.0.0.1:8000/fallback", json={"disabled_sources": disabled}, timeout=300)
    if r.ok:
        st.success(f"Fallback applied. Available: {r.json()['available']}")
        st.caption("Restore with scripts/run_pipeline.py (full) or rerun the pipeline.")
    else:
        st.error(f"Fallback request failed: {r.status_code}")
st.caption("Fallback masks disabled sources and renormalizes remaining weights (deterministic, no crash).")

footer()
