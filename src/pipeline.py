"""KiWi end-to-end demo pipeline orchestration."""
from __future__ import annotations
import time
import uuid
import pandas as pd
import numpy as np

from src import config
from src.constants import (SOURCES, VARIABLES, DATA_ARTIFACTS, MODELS_GATES,
                           MODELS_METADATA, TREEGATE_VERSION, BIAS_VERSION,
                           CAL_VERSION, REGIME_VERSION, DATA_MODE)
from src.synthetic.generator import generate_truth_and_context, generate_source_forecasts
from src.qc.qc import qc_forecasts
from src.alignment.align import align_cases
from src.features.features import build_features, REGIMES, SEASONS
from src.skill.skill import compute_skill, EXTREME_THR
from src.bias.bias import compute_bias_table, apply_bias_correction
from src.gating.treegate import train_treegate, predict_weights, smooth_weights
from src.blending.blend import blend, disagreement as disagreement_df, disagreement_score, apply_fallback
from src.confidence.confidence import compute_intervals, attach_uncertainty
from src.extremes.extremes import detect_events
from src.risk.risk import compute_rpi
from src.evaluation.evaluate import method_forecasts, evaluate_methods, coverage_table
from src.runs.runs import record_run


def _ensure_dirs():
    for p in (DATA_ARTIFACTS, MODELS_GATES, MODELS_METADATA):
        p.mkdir(parents=True, exist_ok=True)


def run_pipeline(available_sources: list[str] | None = None,
                 selected_variable: str = "rainfall",
                 selected_region: str = "Central",
                 seed: int | None = None, quick: bool = False) -> dict:
    t0 = time.time()
    _ensure_dirs()
    pipe = config.pipeline()
    seed = pipe["seed"] if seed is None else seed
    if quick:
        pipe = dict(pipe, cycles_days=24)
    avail = available_sources or list(SOURCES.keys())
    cfg = dict(pipe)

    truth = generate_truth_and_context(cfg, seed=seed)
    sources_cfg = config.sources()
    fc = generate_source_forecasts(truth, sources_cfg, seed=seed + 5)
    qc = qc_forecasts(fc)

    cases = align_cases(fc, truth)

    skill_long = compute_skill(cases, available=avail)
    bias_table = compute_bias_table(cases, avail)
    cases = apply_bias_correction(cases, bias_table, avail)
    feats = build_features(cases, fc, available_sources=avail)

    # TreeGate per variable
    all_weights = pd.DataFrame(index=feats.index)
    for var in VARIABLES:
        sub_idx = feats.index[feats["variable"] == var]
        models = train_treegate(feats.loc[sub_idx], avail, var)
        w = predict_weights(models, feats.loc[sub_idx], avail)
        for c in w.columns:
            all_weights.loc[sub_idx, c] = w[c].to_numpy()
    all_weights = all_weights.fillna(0.0)
    # normalize each row
    wcols = [c for c in all_weights.columns if c.startswith("w_")]
    s = all_weights[wcols].sum(axis=1).replace(0, np.nan)
    all_weights[wcols] = all_weights[wcols].div(s, axis=0).fillna(0.0)
    all_weights = smooth_weights(all_weights, None, alpha=pipe.get("smoothing_alpha", 0.6))
    all_weights, fallback_event = apply_fallback(all_weights, avail)
    disabled_all = [s for s in SOURCES if s not in avail]
    fallback_event = {"disabled": disabled_all, "active": list(avail),
                      "fallback_active": len(disabled_all) > 0}

    dis = disagreement_df(cases, avail)
    for var in VARIABLES:
        m = cases["variable"] == var
        dis.loc[m, "disagreement_score"] = disagreement_score(dis.loc[m, "disagreement_std"], var)

    blend_vals = blend(cases, all_weights, avail)
    cases["kiwi_blend"] = blend_vals

    # calibration from residuals across history
    res = cases.assign(residual=cases["kiwi_blend"] - cases["observed_value"])
    interval_table = compute_intervals(res)
    # recent blend rmse per (variable, lead, region) -> map per row
    recent = (res.sort_values("valid_time")
                .groupby(["variable", "lead_time", "region"])["residual"]
                .transform(lambda x: (x ** 2).rolling(12, min_periods=3).mean().pow(0.5)))
    unc = attach_uncertainty(
        cases, cases["kiwi_blend"], interval_table,
        dis["disagreement_score"].reindex(cases.index).fillna(50),
        recent.reindex(cases.index).fillna(np.nan),
        res.groupby(["variable", "lead_time"])["residual"].transform("count").reindex(cases.index),
        fallback_active=bool(fallback_event["fallback_active"]),
    )

    methods = method_forecasts(cases, all_weights, cases["kiwi_blend"], avail)
    eval_df = evaluate_methods(methods)
    coverage = coverage_table(unc.assign(observed_value=cases["observed_value"].to_numpy()))

    # latest cycle products
    latest_time = cases["valid_time"].max()
    lat_mask = cases["valid_time"] == latest_time
    latest_cases = cases.loc[lat_mask].copy()
    latest_cases["forecast"] = cases.loc[lat_mask, "kiwi_blend"].round(2)
    keep = ["lower_50", "upper_50", "lower_80", "upper_80", "lower_95", "upper_95",
            "interval_width_80", "disagreement_score", "confidence"]
    keep = [c for c in keep if c in unc.columns]
    latest_cases = latest_cases.drop(columns=[c for c in keep if c in latest_cases.columns])
    latest_cases = latest_cases.merge(unc[["case_id"] + keep], on="case_id", how="left")
    w_by_case = all_weights.reset_index(drop=True).assign(case_id=cases["case_id"].to_numpy())
    latest_cases = latest_cases.merge(w_by_case, on="case_id", how="left")
    # events + RPI on latest rows
    lat_unc = unc[unc["case_id"].isin(latest_cases["case_id"])].copy()
    events = detect_events(lat_unc, fc)
    if not events.empty:
        conf_map = lat_unc.set_index("case_id")["confidence"]
        events = compute_rpi(events, conf_map.reindex(events["case_id"]).fillna(50).set_axis(events.index))

    # ---------------- persist artifacts ----------------
    truth.to_parquet(DATA_ARTIFACTS / "truth.parquet", index=False)
    fc.to_parquet(DATA_ARTIFACTS / "forecasts.parquet", index=False)
    cases.to_parquet(DATA_ARTIFACTS / "cases.parquet", index=False)
    skill_long.to_parquet(DATA_ARTIFACTS / "skill_long.parquet", index=False)
    bias_table.to_parquet(DATA_ARTIFACTS / "bias_table.parquet", index=False)
    all_weights.reset_index(drop=True).assign(case_id=cases["case_id"].to_numpy()).to_parquet(
        DATA_ARTIFACTS / "weights.parquet", index=False)
    unc.to_parquet(DATA_ARTIFACTS / "uncertainty.parquet", index=False)
    eval_df.to_parquet(DATA_ARTIFACTS / "evaluation.parquet", index=False)
    coverage.to_parquet(DATA_ARTIFACTS / "coverage.parquet", index=False)
    latest_cases.to_parquet(DATA_ARTIFACTS / "latest.parquet", index=False)
    events.to_parquet(DATA_ARTIFACTS / "risk_events.parquet", index=False)
    dis.reset_index(drop=True).assign(case_id=cases["case_id"].to_numpy()).to_parquet(
        DATA_ARTIFACTS / "disagreement.parquet", index=False)

    # data health
    counts = fc.groupby("source_id").agg(rows=("forecast_value", "count"), cells=("cell_id", "nunique")).reset_index()
    health_rows = []
    for sid, prof in sources_cfg["profiles"].items():
        present = sid in counts["source_id"].values
        row = counts[counts["source_id"] == sid]
        health_rows.append({"source_id": sid, "source_type": prof["source_type"],
                            "version": prof["version"], "available": sid in avail and present,
                            "in_feed": present,
                            "rows": int(row["rows"].iloc[0]) if present else 0,
                            "cells": int(row["cells"].iloc[0]) if present else 0,
                            "missing_pct": round(float(fc[fc["source_id"] == sid]["forecast_value"].isna().mean() * 100), 2) if present else 100.0,
                            "qc_status": qc["status"], "fallback_active": sid not in avail,
                            "last_update": f"demo-run-{pipe.get('cycles_days')}d"})
    health = pd.DataFrame(health_rows)
    health.to_parquet(DATA_ARTIFACTS / "data_health.parquet", index=False)

    registry = {
        "sources": [{"source_id": s, **{k: SOURCES[s][k] for k in ("type", "version")},
                     "available": s in avail} for s in SOURCES],
        "components": {"treegate": TREEGATE_VERSION, "bias_correction": BIAS_VERSION,
                        "confidence_calibration": CAL_VERSION, "regime_engine": REGIME_VERSION},
        "data_mode": DATA_MODE,
    }
    import json
    (MODELS_METADATA / "registry.json").write_text(json.dumps(registry, indent=2), encoding="utf-8")

    run_id = f"run-{uuid.uuid4().hex[:8]}"
    duration = round(time.time() - t0, 2)
    record_run({"run_id": run_id, "selected_variable": selected_variable,
                "region": selected_region, "gate": "treegate",
                "available_sources": avail, "duration_s": duration,
                "forecast_version": f"kiwi-{pipe.get('version')}", "status": "OK",
                "fallback_events": fallback_event["disabled"], "warnings": [],
                "data_mode": DATA_MODE})

    return {"run_id": run_id, "duration_s": duration, "qc": qc,
            "fallback": fallback_event, "coverage": coverage.to_dict("records"),
            "evaluation": eval_df.to_dict("records")}
