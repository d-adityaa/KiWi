import numpy as np
import pandas as pd


def test_weight_sums_from_artifact():
    from api.services import service
    w = service.weights()
    if w.empty:
        import pytest; pytest.skip("no artifacts")
    cols = [c for c in w.columns if c.startswith("w_")]
    s = w[cols].sum(axis=1)
    assert (s - 1).abs().max() < 1e-4
    assert (w[cols] >= 0).all().all()
    assert not w[cols].isna().any().any()


def test_uncertainty_ordering():
    from api.services import service
    u = service.uncertainty()
    if u.empty:
        import pytest; pytest.skip("no artifacts")
    assert (u["lower_95"] <= u["upper_95"]).all()
    assert (u["lower_80"] <= u["upper_80"]).all()
    assert (u["lower_50"] <= u["upper_50"]).all()


def test_risk_bounds():
    from api.services import service
    e = service.events()
    if e.empty or "risk_priority_score" not in e:
        import pytest; pytest.skip("no artifacts")
    assert e["risk_priority_score"].between(0, 100).all()
    if "probability" in e:
        p = e["probability"].dropna()
        assert p.between(0, 1).all()


def test_synthetic_label_present():
    from api.services import service
    u = service.uncertainty()
    if u.empty:
        import pytest; pytest.skip("no artifacts")
    assert (u["data_mode"] == "DEMO").all()
