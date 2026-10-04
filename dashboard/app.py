import sys
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from dashboard.utils.common import *  # noqa

bootstrap("Overview", "Forecast trust desk — DEMO / SYNTHETIC DATA")
sel = sidebar_filters()
sidebar_language()

from api.services import service  # noqa
latest = service.latest()
health = service.health()

if latest.empty:
    no_data("No artifacts found. Run: python scripts/run_pipeline.py")
    footer()
    st.stop()

sub = latest[(latest["variable"] == sel["variable"]) & (latest["region"] == sel["region"]) & (latest["lead_time"] == sel["lead"])]
if sub.empty:
    no_data()
    footer()
    st.stop()

row = sub.iloc[len(sub) // 2]

# context strip
st.markdown(f"<span class='wk-chip'>REGION</span> {row['region']} &nbsp; "
            f"<span class='wk-chip'>VARIABLE</span> {row['variable']} &nbsp; "
            f"<span class='wk-chip'>LEAD</span> {row['lead_time']}h &nbsp; "
            f"<span class='wk-chip'>REGIME</span> {row.get('regime','—')} &nbsp; "
            f"<span class='wk-chip'>CELL</span> {row.get('cell_id','—')}", unsafe_allow_html=True)
st.markdown("")

left, right = st.columns([3, 2], gap="large")
with left:
    section("FINAL FORECAST")
    c1, c2, c3 = st.columns(3)
    c1.metric("Forecast", f"{row['forecast']:.1f}")
    c2.metric("Confidence", f"{row['confidence']:.0f} / 100")
    c3.metric("Regime", str(row.get("regime", "—")))
    st.caption(f"80% interval {row['lower_80']:.1f} – {row['upper_80']:.1f} · "
               f"95% interval {row['lower_95']:.1f} – {row['upper_95']:.1f}")
    st.caption(f"Model agreement: {agreement_word(row.get('disagreement_score'))} · "
               f"Disagreement score {row.get('disagreement_score', float('nan')):.0f}/100")

    ev = service.events()
    if not ev.empty and "risk_priority_score" in ev:
        top = ev.sort_values("risk_priority_score", ascending=False).iloc[0]
        kind = "high" if top["risk_priority_score"] >= 55 else ("moderate" if top["risk_priority_score"] >= 30 else "ok")
        alert_strip(kind, f"{top.get('risk_category','RISK')} RISK",
                    f"{top.get('hazard','—')} · {str(top.get('time_horizon_h','—'))}h horizon · RPI {top['risk_priority_score']}/100")
with right:
    section("SOURCE HEALTH")
    for _, r in health.iterrows():
        st.markdown(f"{status_pill(bool(r['available']))} &nbsp; **{r['source_id']}** "
                    f"<span style='color:#8a8f94'>· QC {r['qc_status']} · {r['rows']} rows"
                    + (" · FALLBACK" if r['fallback_active'] else "") + "</span>",
                    unsafe_allow_html=True)

st.markdown("---")
section("MODEL TRUST", "Mean corrected-source weights for the current selection.")
wcols = [c for c in sub.columns if c.startswith("w_")]
mean_w = sub[wcols].mean().sort_values(ascending=False)
for c, v in mean_w.items():
    src = c[2:]
    emphasis = sel["source"] == src
    bar_row(f"**{src}**" if emphasis else src, v * 100,
            note=f"weight {v*100:.1f}%", color=SOURCE_COLORS.get(src))
    if emphasis:
        bias_col = f"{src}__bias"
        bias = row.get(bias_col)
        if bias is not None and bias == bias:
            st.caption(f"Selected source bias correction: {bias:+.2f}")

# WHY THIS WEIGHT?
st.markdown("---")
section("WHY THIS WEIGHT?")
skill = service.skill()
chosen = st.selectbox("Select a source to explain", [c[2:] for c in wcols])
if chosen:
    w = float(mean_w.get(f"w_{chosen}", float("nan")))
    st.caption(f"{chosen} weight: {w*100:.1f}%")
    ssub = skill[(skill["variable"] == sel["variable"]) & (skill["region"] == sel["region"]) &
                 (skill["lead_time"] == sel["lead"]) & (skill["source_id"] == chosen)]
    if not ssub.empty:
        r0 = ssub.iloc[0]
        st.markdown(f"- Mean absolute error this context: **{r0['mae']:.2f}**")
        st.markdown(f"- RMSE: **{r0['rmse']:.2f}** · Bias: **{r0['bias']:+.2f}** · Correlation: **{r0['correlation']:.2f}**")
        st.markdown(f"- Extreme-event precision/recall/F1: "
                    f"{r0['precision']:.2f} / {r0['recall']:.2f} / {r0['f1']:.2f}")
        st.markdown(f"- Historical samples: **{int(r0['sample_count'])}**")
    else:
        st.caption("Limited historical skill samples for this exact context.")

# WHAT CHANGED SINCE LAST RUN?
st.markdown("---")
section("WHAT CHANGED SINCE LAST RUN?")
wdf = service.weights()
if wdf.empty or "case_id" not in wdf:
    st.caption("No run delta available.")
else:
    # weights do not store timestamps; approximate change via last two valid_times in cases
    cases = service.cases()
    if not cases.empty and "valid_time" in cases:
        times = sorted(cases["valid_time"].unique())[-2:]
        if len(times) == 2:
            prev_rows = cases[cases["valid_time"] == times[0]]
            curr_rows = cases[cases["valid_time"] == times[-1]]
            # use weights artifact joined by case_id
            w_prev = wdf[wdf["case_id"].isin(prev_rows["case_id"])][[c for c in wdf.columns if c.startswith("w_")]].mean()
            w_curr = wdf[wdf["case_id"].isin(curr_rows["case_id"])][[c for c in wdf.columns if c.startswith("w_")]].mean()
            for d in weight_change({c[2:]: float(w_prev[c]) for c in w_prev.index},
                                   {c[2:]: float(w_curr[c]) for c in w_curr.index}):
                arrow = "→"
                st.markdown(f"**{d['source']}** &nbsp; {d['prev']*100:.0f}% {arrow} {d['curr']*100:.0f}% "
                            f"<span style='color:{'#3f7d53' if d['delta']>=0 else '#a4443c'}'>"
                            f"{d['delta']*100:+.0f} pts</span>", unsafe_allow_html=True)

# FORECAST COMPARISON CHART
st.markdown("---")
section("SOURCE FORECASTS vs KIWI vs OBSERVED", "Region mean, last 14 cycles")
cases = service.cases()
if not cases.empty:
    subc = cases[(cases["variable"] == sel["variable"]) & (cases["region"] == sel["region"]) &
                 (cases["lead_time"] == sel["lead"])].copy()
    subc["valid_time"] = pd.to_datetime(subc["valid_time"])
    last_times = sorted(subc["valid_time"].unique())[-14:]
    subc = subc[subc["valid_time"].isin(last_times)]
    src_cols = [s for s in ["GFS", "ECMWF", "IMD-WRF", "GraphCast", "Pangu", "ENS"] if s in subc]
    fig = go.Figure()
    for s in src_cols:
        g = subc.groupby("valid_time")[s].mean()
        fig.add_trace(go.Scatter(x=g.index, y=g.values, mode="lines", name=s,
                                 line=dict(width=1, color="#b9bdc2")))
    if "kiwi_blend" in subc:
        g = subc.groupby("valid_time")["kiwi_blend"].mean()
        fig.add_trace(go.Scatter(x=g.index, y=g.values, mode="lines", name="KiWi blend",
                                 line=dict(width=2.5, color="#3e6b8b")))
    g = subc.groupby("valid_time")["observed_value"].mean()
    fig.add_trace(go.Scatter(x=g.index, y=g.values, mode="lines+markers", name="Observed (demo)",
                             line=dict(width=1.5, color="#24282b", dash="dot")))
    fig.update_layout(**TEMPLATE["layout"], height=340, legend=dict(orientation="h", y=-0.15))
    st.plotly_chart(fig, use_container_width=True)

footer()
