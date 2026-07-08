"""FastAPI service encapsulating astrology calculations."""

from fastapi import FastAPI

from todayflow_astro.core import models
from todayflow_astro.services.engine import AstroEngine

app = FastAPI(title="TodayFlow Astrology Service")
engine = AstroEngine()


@app.get("/health", tags=["ops"])
def health() -> dict:
    return {"status": "ok"}


@app.post("/chart", response_model=models.ChartResponse, tags=["charts"])
def compute_chart(payload: models.ChartRequest) -> models.ChartResponse:
    """
    Accept normalized birth data (optionally pre-resolved coordinates) and return
    a chart snapshot that the backend will map onto the Internal Model.
    """
    return engine.compute_chart(payload)
