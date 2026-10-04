"""Shared dashboard shell: styling, navigation chrome, status bar,
scientific section helpers, bars, alert strip, density helpers."""
from __future__ import annotations
import os
import sys
from pathlib import Path
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src import config  # noqa: E402
from api.services import service  # noqa: E402

PALETTE = ["#3e6b8b", "#8a8f94", "#6b7177", "#3f7d53", "#b07d2b", "#a4443c"]
FONT = ("'Public Sans','Source Sans Pro',Roboto,'Open Sans','Noto Sans',"
        "'Lucida Sans',sans-serif")
AGREEMENT_SCALE = ["STRONG", "MODERATE", "WEAK", "DIVERGENT"]

TEMPLATE = dict(layout=dict(
    font=dict(family=FONT, size=12, color="#24282b"),
    paper_bgcolor="white", plot_bgcolor="white",
    margin=dict(l=44, r=20, t=40, b=40),
    xaxis=dict(showgrid=True, gridcolor="#ececea", linecolor="#d8d8d4", zeroline=False),
    yaxis=dict(showgrid=True, gridcolor="#ececea", linecolor="#d8d8d4", zeroline=False),
    colorway=PALETTE, hovermode="x unified",
))

CSS = """
<style>
html, body, [class*="css"], .stApp, button, input, select, textarea {
  font-family: 'Public Sans','Source Sans Pro',Roboto,'Open Sans','Noto Sans','Lucida Sans',sans-serif !important;
}
.stApp { background-color: #ffffff; }
section[data-testid="stSidebar"] { background-color: #f6f6f4; border-right: 1px solid #d8d8d4; }
[data-testid="stMetricValue"] { font-size: 1.45rem; font-weight: 600; color: #24282b; }
[data-testid="stMetricLabel"] { font-size: 0.72rem; color: #6b7177; text-transform: uppercase; letter-spacing: .06em; }
h1 { font-size: 1.5rem !important; font-weight: 650 !important; }
h2 { font-size: 1.15rem !important; font-weight: 620 !important; }
h3 { font-size: 1.0rem !important; font-weight: 620 !important; }
h1, h2, h3 { color: #24282b; }
hr { border-color: #d8d8d4; margin-top: .9rem; margin-bottom: .9rem; }
div[data-testid="stCaption"] p { color: #6b7177; font-size: .78rem; }
.stButton>button, .stDownloadButton>button {
  border-radius: 2px; border: 1px solid #b9bdc2; background: #ffffff;
  color: #24282b; font-weight: 500; padding: .25rem .8rem;
}
.stButton>button:hover, .stDownloadButton>button:hover { border-color: #3e6b8b; color: #3e6b8b; }
thead tr th { background-color: #f1f1ee !important; font-size: .78rem !important;
  text-transform: uppercase; letter-spacing: .04em; color: #6b7177 !important; }
div[data-baseweb="select"] > div { border-radius: 2px; border-color: #c3c8cd; }
div[data-testid="stMetric"] { border: 1px solid #d8d8d4; border-left: 4px solid #3e6b8b; border-radius: 2px;
  padding: 10px 12px; background: #f7f9fb; }
div[data-testid="stMetricValue"] { font-weight: 650; color: #24282b; }
div[data-testid="stMetricLabel"] { color: #6b7177; }
div[data-testid="stDataFrame"] { border: 1px solid #d8d8d4; border-radius: 2px; }
div[data-testid="stDataFrame"] thead tr th { background-color: #e8eef4 !important; color: #3e6b8b !important; }
div[data-testid="stAlert"] { border-radius: 2px; text-align: left; }
div[data-testid="stChart"] { border: 1px solid #e3e3de; border-radius: 2px; padding: 6px; background: #fcfcfb; }
.wk-bar { height: 12px; background: #e9e9e6; width: 100%; border: 1px solid #dcdcd8; border-radius: 2px; }
.wk-fill { height: 100%; background: #3e6b8b; }
.wk-fill.muted { background: #9aa0a6; }
.wk-strip { border:1px solid #d8d8d4; border-left:4px solid #b07d2b; background:#fbfaf7;
  padding:.5rem .8rem; margin:.4rem 0; font-size:.85rem; }
.wk-strip.red { border-left-color:#a4443c; background:#faf3f2; }
.wk-strip.green { border-left-color:#3f7d53; background:#f2f7f3; }
.wk-strip { background:#fdf9f0; }
.wk-kv { display:flex; justify-content:space-between; border-bottom:1px dashed #e4e4e0; padding:.18rem 0; font-size:.85rem;}
.wk-kv b { font-weight:600; }
.wk-dot { display:inline-block; width:8px; height:8px; border-radius:50%; margin-right:6px; vertical-align:middle;}
.wk-chip { font-size:.7rem; letter-spacing:.08em; color:#6b7177; text-transform:uppercase; }
div[data-testid="stSidebarNav"] { display: none; }
section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] { padding-top: 0.15rem !important; }
.wk-brand-top { margin-top: -3.6rem; }
div[data-testid="stMainBlockContainer"] { padding-top: 1.1rem !important; }
.wk-desc-band { margin: .1rem 0 .8rem 0 !important; }
</style>
"""


def bootstrap(title: str, subtitle: str = ""):
    st.set_page_config(page_title=f"KiWi — {title}", layout="wide")
    st.markdown(CSS, unsafe_allow_html=True)
    top_bar()
    sidebar_top_brand()
    sidebar_nav()
    sidebar_brand()
    st.markdown(f"### {title}")
    if subtitle:
        st.caption(subtitle)
    st.markdown(
        "<div class='wk-desc-band' style='border-left:4px solid #3e6b8b;background:#eef3f8;padding:8px 12px;"
        "font-weight:700 !important; font-size:1.2rem !important; color:#24282b;'>"
        "KiWi intelligently blends NWP, AI and ensemble forecasts to deliver adaptive, "
        "explainable and risk-aware weather intelligence.</div>",
        unsafe_allow_html=True)


def top_bar():
    from src.runs.runs import list_runs
    runs = list_runs(limit=1)
    last = runs[0]["run_id"] if runs else "—"
    ts = runs[0].get("timestamp", "—")[:19].replace("T", " ") if runs else "—"
    avail = runs[0].get("available_sources", []) if runs else []
    st.markdown(
        f"<div style='border-bottom:1px solid #d8d8d4;padding:4px 0 6px 0;font-size:11px;"
        f"letter-spacing:.08em;color:#6b7177;text-transform:uppercase;'>"
        f"<b style='color:#24282b'>KIWI</b> &nbsp;·&nbsp; RUN {last} &nbsp;·&nbsp; DEMO / SYNTHETIC &nbsp;·&nbsp; "
        f"PIPELINE READY &nbsp;·&nbsp; SOURCES {len(avail)} / 6 &nbsp;·&nbsp; LAST RUN {ts} UTC</div>",
        unsafe_allow_html=True,
    )


LOGO_NAME = "Kiwi Bird Sensing Ripples.png"


def resolve_logo() -> Path | None:
    try:
        candidates = [
            Path.home() / "Downloads" / LOGO_NAME,
            Path(os.environ.get("USERPROFILE", "")) / "Downloads" / LOGO_NAME,
            Path(os.environ.get("HOMEDRIVE", "")) / os.environ.get("HOMEPATH", "") / "Downloads" / LOGO_NAME,
        ]
        for c in candidates:
            if c and c.exists():
                return c
        # fallback: recursive search of Downloads (handles redirected/localized dirs)
        dl = Path.home() / "Downloads"
        if dl.exists():
            for hit in dl.rglob("Kiwi Bird Sensing Ripples*.png"):
                return hit
    except Exception:
        pass
    return None


def sidebar_top_brand():
    with st.sidebar:
        st.markdown("<div class='wk-brand-top'></div>", unsafe_allow_html=True)
        logo = resolve_logo()
        if logo is not None:
            st.image(str(logo), width=56)
        else:
            st.markdown("**KiWi**")
        st.markdown("**Knowledge Integrated Weather Intelligence**")
        st.markdown("---")


NAV_PAGES = [
    ("dashboard/app.py", "app"),
    ("dashboard/pages/02_Forecast_Desk.py", "Forecast Desk"),
    ("dashboard/pages/03_Model_Comparison.py", "Model Comparison"),
    ("dashboard/pages/04_Trust_Atlas.py", "Trust Atlas"),
    ("dashboard/pages/05_Confidence_Uncertainty.py", "Confidence & Uncertainty"),
    ("dashboard/pages/06_Extremes_Risk.py", "Extreme Weather & Risk"),
    ("dashboard/pages/07_Spatial_Explorer.py", "Spatial Explorer"),
    ("dashboard/pages/08_LeadTime_Performance.py", "Lead-Time Performance"),
    ("dashboard/pages/09_Data_Health.py", "Data Health"),
    ("dashboard/pages/10_Run_History.py", "Run History"),
    ("dashboard/pages/11_Model_Registry.py", "Model Registry"),
    ("dashboard/pages/12_Export_Bulletin.py", "Export / Bulletin"),
]


def sidebar_nav():
    with st.sidebar:
        for rel, label in NAV_PAGES:
            try:
                st.page_link(str(ROOT / rel), label=label)
            except Exception:
                pass
        st.markdown("---")


def sidebar_brand():
    with st.sidebar:
        st.markdown("**KiWi**")
        st.caption("Adaptive Forecast Intelligence")
        st.markdown("<span class='wk-chip' style='color:#b07d2b'>DEMO / SYNTHETIC DATA</span>",
                    unsafe_allow_html=True)
        st.markdown("---")


def footer():
    st.markdown("---")
    st.caption(
        "KiWi — Hybrid AI–NWP Multi-Model Forecast Blending System · SIH 26081 · "
        "Demo / Synthetic Data · Version 1.0 · "
        "Prototype only — synthetic data, not operational weather guidance."
    )


def sidebar_filters() -> dict:
    from src.constants import REGIONS, VARIABLES, LEAD_BUCKETS
    t = t_get()
    with st.sidebar:
        st.markdown("**" + t["controls"] + "**")
        region = st.selectbox(t["region"], REGIONS, index=2)
        variable = st.selectbox(t["variable"], VARIABLES, index=0)
        lead = st.selectbox(t["lead"], LEAD_BUCKETS, index=2)
        regime = st.selectbox(t["regime"], ["All"] + ["Stable", "Normal Rain", "Convective",
                                                       "Heavy Rain", "Heatwave", "High Wind", "Transition"])
        latest = service.latest()
        sources = [c[2:] for c in latest.columns if c.startswith("w_")] if not latest.empty else []
        source = st.selectbox(t["source"], ["All"] + sources) if sources else None
        st.markdown("---")
        return {"region": region, "variable": variable, "lead": lead, "regime": regime, "source": source}


def sidebar_language():
    with st.sidebar:
        st.selectbox("Language / भाषा", ["en", "hi"], key="lang")
        import pandas as _pd  # noqa
        from src.runs.runs import list_runs
        r = list_runs(limit=1)
        if r:
            st.caption(f"Last run: {r[0]['run_id']} · {r[0]['status']}")
    return st.session_state.get("lang", "en")


def t_get() -> dict:
    from dashboard.utils.i18n import T
    return T[st.session_state.get("lang", "en")]


SOURCE_COLORS = {"GFS": "#7c8a99", "ECMWF": "#3e6b8b", "IMD-WRF": "#3f7d53",
                 "GraphCast": "#b07d2b", "Pangu": "#8a6f9e", "ENS": "#5d8a8b", "treegate_kiwi": "#2f4f66"}


def section(title: str, note: str = ""):
    st.markdown(
        f"<div style='background:#eef3f8;border-left:4px solid #3e6b8b;padding:4px 10px;"
        f"margin-top:1rem;font-weight:620;font-size:.95rem;color:#2f4f66;'>{title}</div>",
        unsafe_allow_html=True)
    st.markdown("<hr style='margin:.25rem 0 .6rem 0'/>", unsafe_allow_html=True)
    if note:
        st.caption(note)


def bar_row(label: str, pct: float, note: str = "", muted: bool = False,
            color: str | None = None):
    pct = max(0.0, min(100.0, float(pct)))
    fill = color if color else ("#9aa0a6" if muted else "#3e6b8b")
    st.markdown(
        f"<div class='wk-kv'><span>{label}</span><b>{pct:.1f}%</b></div>"
        f"<div class='wk-bar'><div style='height:100%;width:{pct}%;background:{fill};border-radius:2px;'></div></div>"
        + (f"<div style='font-size:11px;color:#8a8f94'>{note}</div>" if note else ""),
        unsafe_allow_html=True,
    )


def box(md_html: str):
    st.markdown(f"<div style='border:1px solid #d8d8d4; background:#fbfaf7; padding:10px 12px; "
                f"border-radius:2px; margin-bottom:.6rem;'>{md_html}</div>", unsafe_allow_html=True)


def dot(color: str) -> str:
    return f"<span class='wk-dot' style='background:{color}'></span>"


def status_pill(available: bool) -> str:
    c = "#3f7d53" if available else "#a4443c"
    label = "AVAILABLE" if available else "UNAVAILABLE"
    return f"{dot(c)}{label}"


def agreement_word(score: float) -> str:
    if score is None or score != score:
        return "—"
    if score < 20:
        return "STRONG"
    if score < 45:
        return "MODERATE"
    if score < 70:
        return "WEAK"
    return "DIVERGENT"


def alert_strip(kind: str, headline: str, detail: str):
    cls = {"high": "red", "moderate": "", "ok": "green"}.get(kind, "")
    st.markdown(f"<div class='wk-strip {cls}'><b>{headline}</b> &nbsp;·&nbsp; {detail}</div>",
                unsafe_allow_html=True)


def no_data(msg: str = "No forecast data for this selection."):
    st.info(msg)


def weight_change(prev: dict, curr: dict) -> list[dict]:
    out = []
    for k in sorted(set(prev) | set(curr)):
        p = prev.get(k); c = curr.get(k)
        if p is None or c is None:
            continue
        out.append({"source": k, "prev": p, "curr": c, "delta": c - p})
    return sorted(out, key=lambda r: -abs(r["delta"]))
