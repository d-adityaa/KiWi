def test_truth_has_spatial_temporal_structure(small_truth):
    assert small_truth["cell_id"].nunique() > 10
    assert small_truth["time"].nunique() >= 6
    assert {"rainfall", "temperature", "wind", "regime"} <= set(small_truth.columns)
    assert small_truth["rainfall"].between(0, 400).all()


def test_forecast_schema_and_sources(small_fc):
    for col in ["source_id", "initialization_time", "valid_time", "lead_time",
                "latitude", "longitude", "cell_id", "region", "variable",
                "forecast_value", "unit", "ensemble_member", "regime", "metadata"]:
        assert col in small_fc.columns
    assert set(small_fc["source_id"].unique()) == {"GFS", "ECMWF", "IMD-WRF", "GraphCast", "Pangu", "ENS"}
    assert (small_fc["metadata"] == "DEMO/SYNTHETIC").all()


def test_ens_members(small_fc):
    ens = small_fc[small_fc["source_id"] == "ENS"]
    assert ens.groupby(["valid_time", "lead_time", "cell_id", "variable"])["ensemble_member"].nunique().min() >= 8
