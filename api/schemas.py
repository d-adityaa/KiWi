from pydantic import BaseModel, Field
from typing import Optional


class RunRequest(BaseModel):
    available_sources: Optional[list[str]] = None
    selected_variable: str = "rainfall"
    selected_region: str = "Central"
    quick: bool = False


class FallbackRequest(BaseModel):
    disabled_sources: list[str] = Field(default_factory=list)


class ForecastQuery(BaseModel):
    variable: str = "rainfall"
    region: str = "Central"
    lead_time: int = 24
    cell_id: Optional[str] = None


class ExportRequest(BaseModel):
    variable: str = "rainfall"
    region: str = "Central"
    lead_time: int = 24
    format: str = "csv"
