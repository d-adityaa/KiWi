from __future__ import annotations
import pandas as pd
from fastapi import APIRouter, Query

from api.services import service
from api.schemas import RunRequest, FallbackRequest, ForecastQuery, ExportRequest
from src import pipeline
from src.constants import SOURCES
from src.export.exporter import to_csv, to_json
from src.runs.runs import list_runs

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok", "data_mode": "DEMO"}


@router.get("/models")
def models():
    return {"sources": list(SOURCES.keys()), "registry": service.registry()}


@router.get("/regions")
def regions():
    from src.constants import REGIONS
    return {"regions": REGIONS}


@router.get("/skill")
def skill(variable: str | None = None, region: str | None = None):
    df = service.skill()
    if variable:
        df = df[df["variable"] == variable]
    if region:
        df = df[df["region"] == region]
    return service.records(df.head(2000))


@router.get("/weights")
def weights(variable: str | None = None, region: str | None = None, limit: int = 500):
    df = service.weights()
    if df.empty:
        return []
    if variable and "case_id" in df:
        df = df[df["case_id"].str.contains(f"_{variable}$")]
    return service.records(df.head(limit))


@router.get("/weights/summary")
def weights_summary(variable: str | None = None):
    df = service.weights()
    cols = [c for c in df.columns if c.startswith("w_")]
    if df.empty or not cols:
        return {"columns": cols}
    if variable:
        df = df[df["case_id"].str.endswith(f"_{variable}")]
    return {c: round(float(df[c].mean()), 4) for c in cols}


@router.get("/forecast")
def forecast(variable: str = "rainfall", region: str = "Central", lead_time: int = 24):
    df = service.latest()
    if df.empty:
        return {"rows": []}
    sub = df[(df["variable"] == variable) & (df["region"] == region) & (df["lead_time"] == lead_time)]
    return {"rows": service.records(sub.head(500))}


@router.get("/confidence")
def confidence(variable: str = "rainfall", region: str = "Central", lead_time: int = 24):
    df = service.uncertainty()
    sub = df[(df["variable"] == variable) & (df["region"] == region) & (df["lead_time"] == lead_time)]
    cols = [c for c in ["case_id", "region", "cell_id", "forecast", "confidence",
                        "lower_80", "upper_80", "lower_95", "upper_95", "disagreement_score"] if c in sub]
    return service.records(sub[cols].head(500))


@router.get("/uncertainty")
def uncertainty():
    return service.records(service.coverage())


@router.get("/extremes")
def extremes():
    return service.records(service.events())


@router.get("/risk")
def risk():
    df = service.events()
    if df.empty:
        return []
    return service.records(df.sort_values("risk_priority_score", ascending=False).head(200))


@router.get("/data-health")
def data_health():
    return service.records(service.health())


@router.get("/runs")
def runs(limit: int = 50):
    return list_runs(limit)


@router.get("/registry")
def registry():
    return service.registry()


@router.get("/explain")
def explain(variable: str = "rainfall", region: str = "Central", lead_time: int = 24):
    from src.explain.explain import explain_weights
    df = service.latest()
    sub = df[(df["variable"] == variable) & (df["region"] == region) & (df["lead_time"] == lead_time)]
    if sub.empty:
        return {"weights": {}, "reasons": []}
    row = sub.iloc[0]
    sw = {c[2:]: float(row[c]) for c in sub.columns if c.startswith("w_")}
    regime = row["regime"] if "regime" in row else "Transition"
    return {"case": row.get("case_id"), "weights": explain_weights(sw, service.skill(), variable, region, regime, lead_time)}


@router.get("/evaluate")
def evaluate():
    return {"methods": service.records(service.evaluation()),
            "coverage": service.records(service.coverage())}


@router.post("/run")
def run(req: RunRequest):
    avail = req.available_sources or list(SOURCES.keys())
    result = pipeline.run_pipeline(available_sources=avail,
                                   selected_variable=req.selected_variable,
                                   selected_region=req.selected_region,
                                   quick=req.quick)
    return result


@router.post("/fallback")
def fallback(req: FallbackRequest):
    avail = [s for s in SOURCES if s not in req.disabled_sources]
    result = pipeline.run_pipeline(available_sources=avail, quick=True)
    return {"available": avail, "disabled": req.disabled_sources,
            "fallback_active": bool(req.disabled_sources), "run": result}


@router.post("/forecast/query")
def forecast_query(req: ForecastQuery):
    df = service.latest()
    sub = df[(df["variable"] == req.variable) & (df["region"] == req.region) & (df["lead_time"] == req.lead_time)]
    if req.cell_id:
        sub = sub[sub["cell_id"] == req.cell_id]
    cols = [c for c in sub.columns if c in ["case_id", "cell_id", "region", "variable", "lead_time",
            "forecast", "observed_value", "confidence", "lower_80", "upper_80", "regime"]] + \
           [c for c in sub.columns if c.startswith("w_") or c in SOURCES or c.endswith("_corrected")]
    return {"rows": service.records(sub[cols].head(300))}


@router.post("/export")
def export(req: ExportRequest):
    df = service.latest()
    sub = df[(df["variable"] == req.variable) & (df["region"] == req.region) & (df["lead_time"] == req.lead_time)]
    if req.format == "json":
        return to_json(service.records(sub.head(500)))
    return to_csv(sub.head(500))
