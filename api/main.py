from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.api import router

app = FastAPI(title="KiWi API", version="1.0",
              description="Hybrid AI–NWP Multi-Model Forecast Blending — DEMO / SYNTHETIC DATA")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(router)


@app.get("/")
def root():
    return {"product": "KiWi", "data_mode": "DEMO", "docs": "/docs"}
