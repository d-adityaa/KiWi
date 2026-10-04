import sys
from pathlib import Path
import pandas as pd
import streamlit as st
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from dashboard.utils.common import *  # noqa

bootstrap("Export & Bulletin", "Final product with full provenance")
sel = sidebar_filters(); sidebar_language()
from api.services import service
from src.export.exporter import to_csv, to_json
latest = service.latest()
sub = latest[(latest["variable"] == sel["variable"]) & (latest["region"] == sel["region"]) & (latest["lead_time"] == sel["lead"])]
if sub.empty:
    no_data(); footer(); st.stop()

section("KIWI WEATHER PRODUCT")
row = sub.iloc[len(sub) // 2]
c1, c2, c3, c4 = st.columns(4)
c1.metric("Region", str(row["region"]))
c2.metric("Variable", str(row["variable"]))
c3.metric("Lead", f"{row['lead_time']}h")
c4.metric("Forecast", f"{row['forecast']:.1f}")
wcols = [c for c in sub.columns if c.startswith("w_")]
mean_w = sub[wcols].mean().sort_values(ascending=False)
st.markdown(f"**Dominant source:** {mean_w.index[0][2:]} ({mean_w.iloc[0]*100:.1f}%) · "
            f"**Confidence:** {row['confidence']:.0f}/100 · "
            f"**80% interval:** {row['lower_80']:.1f}–{row['upper_80']:.1f} · **Regime:** {row.get('regime')}")

section("DOWNLOADS")
c1, c2 = st.columns(2)
c1.download_button("Download CSV", to_csv(sub), file_name="kiwi_product.csv", mime="text/csv")
c2.download_button("Download JSON", to_json(sub.head(500).to_dict("records")),
                   file_name="kiwi_product.json", mime="application/json")

section("BULLETIN")
if st.button("Generate Bulletin"):
    ev = service.events()
    top = ev.sort_values("risk_priority_score", ascending=False).head(1) if not ev.empty and "risk_priority_score" in ev else None
    hazard = top["hazard"].iloc[0] if top is not None and len(top) else "—"
    rpi = f"{top['risk_priority_score'].iloc[0]:.0f}/100" if top is not None and len(top) else "—"
    bulletin = (
        "KIWI WEATHER BULLETIN\n"
        f"Region: {row.get('region')} (demo)\n"
        f"Hazard: {hazard}\n"
        f"Forecast: {row['forecast']:.1f} / lead {row['lead_time']}h\n"
        f"Confidence: {row['confidence']:.0f}/100\n"
        f"Risk (prototype RPI): {rpi}\n"
        "Data: DEMO / SYNTHETIC — not operational weather guidance."
    )
    st.code(bulletin, language=None)
    st.download_button("Download bulletin (txt)", bulletin, file_name="kiwi_bulletin.txt")

footer()
