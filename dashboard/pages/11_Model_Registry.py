import sys
from pathlib import Path
import pandas as pd
import streamlit as st
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from dashboard.utils.common import *  # noqa

bootstrap("Model Registry", "Simulated sources and KiWi components")
sidebar_language()
from api.services import service
reg = service.registry()
if not reg:
    no_data(); footer(); st.stop()

section("SOURCES")
src = pd.DataFrame(reg["sources"])
health = service.health()
if not health.empty:
    src = src.merge(health[["source_id", "available", "qc_status", "missing_pct"]], on="source_id", how="left")
st.dataframe(src, use_container_width=True, hide_index=True)

section("COMPONENT VERSIONS")
for k, v in reg["components"].items():
    st.markdown(f"- **{k.replace('_', ' ').title()}**: `{v}`")
st.caption(f"Data mode: {reg.get('data_mode', 'DEMO')}")

footer()
