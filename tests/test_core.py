import pandas as pd
from src.qc.qc import qc_forecasts
from src.schemas import check_schema, FORECAST_REQUIRED
from src.alignment.align import align_cases
from src.skill.skill import compute_skill, _metrics, event_skill
from src.bias.bias import compute_bias_table, apply_bias_correction
from src.regime.regime import classify
from src.gating.treegate import train_treegate, predict_weights, smooth_weights
from src.features.features import build_features
from src.blending.blend import blend, apply_fallback, disagreement, disagreement_score
from src.confidence.confidence import interval_quantiles
from src.extremes.extremes import ens_probability
from src.risk.risk import compute_rpi
from src.export.exporter import to_csv, to_json, product_record


def test_schema(small_fc):
    assert check_schema(small_fc, FORECAST_REQUIRED, "fc")["ok"]


def test_qc(small_fc):
    r = qc_forecasts(small_fc)
    assert r["status"] in ("PASS", "WARN")
    assert r["broken_cycles"] == 0


def test_alignment_and_skill(small_truth, small_fc):
    cases = align_cases(small_fc, small_truth)
    assert {"observed_value", "case_id"} <= set(cases.columns)
    sk = compute_skill(cases)
    assert {"mae", "rmse", "bias", "correlation", "precision", "recall", "f1"} <= set(sk.columns)


def test_bias_correction(small_truth, small_fc):
    cases = align_cases(small_fc, small_truth)
    avail = list({s for s in small_fc["source_id"]})
    bt = compute_bias_table(cases, avail)
    corrected = apply_bias_correction(cases, bt, avail)
    for s in avail:
        assert f"{s}_corrected" in corrected.columns


def test_regime():
    assert classify({"rainfall": 80, "temperature": 28, "wind": 3, "humidity": 85}) == "Heavy Rain"
    assert classify({"rainfall": 0, "temperature": 42, "wind": 3, "humidity": 30}) == "Heatwave"
    assert classify({"rainfall": 0, "temperature": 25, "wind": 2, "humidity": 40}) == "Stable"


def test_treegate_weights_sum(small_truth, small_fc):
    cases = align_cases(small_fc, small_truth)
    avail = ["GFS", "ECMWF", "IMD-WRF", "GraphCast", "Pangu", "ENS"]
    bt = compute_bias_table(cases, avail)
    cases = apply_bias_correction(cases, bt, avail)
    feats = build_features(cases, small_fc, available_sources=avail)
    var = "rainfall"
    idx = feats.index[feats["variable"] == var]
    models = train_treegate(feats.loc[idx], avail, var)
    w = predict_weights(models, feats.loc[idx], avail)
    wcols = [c for c in w.columns if c.startswith("w_")]
    s = w[wcols].sum(axis=1)
    assert ((s - 1).abs() < 1e-6).all()
    assert (w[wcols] >= 0).all().all()
    assert not w[wcols].isna().any().any()


def test_smoothing():
    import pandas as pd, numpy as np
    cur = pd.DataFrame({"w_A": [1.0, 0.0], "w_B": [0.0, 1.0]})
    prev = pd.DataFrame({"w_A": [0.5, 0.5], "w_B": [0.5, 0.5]})
    out = smooth_weights(cur, prev, alpha=0.5)
    assert abs(out["w_A"].iloc[0] - (0.5 * 1.0 + 0.5 * 0.5)) < 1e-6
    assert abs(out.filter(like="w_").sum(axis=1) - 1).max() < 1e-6


def test_fallback():
    import pandas as pd
    w = pd.DataFrame({"w_GFS": [0.4], "w_ECMWF": [0.6], "w_Pangu": [0.0]})
    w2, ev = apply_fallback(w, ["GFS", "Pangu"])
    assert ev["fallback_active"] is True
    assert w2["w_ECMWF"].iloc[0] == 0.0
    assert abs(w2[["w_GFS", "w_Pangu"]].sum(axis=1).iloc[0] - 1.0) < 1e-9


def test_disagreement_nonneg(small_truth, small_fc):
    cases = align_cases(small_fc, small_truth)
    avail = list({s for s in small_fc["source_id"]})
    d = disagreement(cases, avail)
    assert (d["disagreement_std"] >= 0).all()


def test_interval_quantiles_ordered():
    import numpy as np
    r = pd.Series(np.random.default_rng(0).normal(0, 5, 200))
    q = interval_quantiles(r)
    assert q[0.5] <= q[0.8] <= q[0.95]


def test_ens_probability_bounds(small_fc):
    row = small_fc[small_fc["source_id"] == "ENS"].iloc[0]
    p = ens_probability(small_fc, row["valid_time"], row["lead_time"], row["cell_id"], row["variable"], threshold=row["forecast_value"])
    assert 0.0 <= p <= 1.0


def test_rpi_range():
    import pandas as pd
    ev = pd.DataFrame({"case_id": ["a", "b"], "hazard": ["Heavy Rain", "Heatwave"], "probability": [0.9, 0.2],
                       "forecast": [100, 45], "event_detected": [True, True]})
    out = compute_rpi(ev, pd.Series([80.0, 40.0], index=ev.index))
    assert out["risk_priority_score"].between(0, 100).all()
    assert set(out["risk_category"]).issubset({"LOW", "MODERATE", "HIGH", "CRITICAL"})


def test_export_labels_demo():
    rec = product_record({"forecast": 12.3})
    assert rec["data_mode"] == "DEMO"
    assert to_csv(pd.DataFrame([rec])).startswith(b"forecast")
    assert b"DEMO" in to_json([rec])
