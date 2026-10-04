import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    from api.main import app
    return TestClient(app)


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["data_mode"] == "DEMO"


def test_endpoints_get(client):
    for path in ["/models", "/regions", "/skill", "/weights", "/weights/summary",
                 "/forecast", "/confidence", "/uncertainty", "/extremes", "/risk",
                 "/data-health", "/runs", "/registry", "/explain", "/evaluate"]:
        r = client.get(path)
        assert r.status_code == 200, path


def test_forecast_query_and_export(client):
    r = client.post("/forecast/query", json={"variable": "rainfall", "region": "Central", "lead_time": 24})
    assert r.status_code == 200
    r = client.post("/export", json={"variable": "rainfall", "region": "Central", "lead_time": 24, "format": "json"})
    assert r.status_code == 200
    assert b"DEMO" in r.content
