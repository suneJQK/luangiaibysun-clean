from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from tuvi_engine.engine.chart_builder import lap_la_so
from tuvi_engine.data_loader import load_cach_cuc, load_star_registry
from tuvi_engine.rules.analysis import analyze_chart

app = FastAPI(title="LuanGiaiBySun Tu Vi API", version="2.0")


class ChartRequest(BaseModel):
    ngay: int = Field(ge=1, le=31)
    thang: int = Field(ge=1, le=12)
    nam: int = Field(ge=1800, le=2200)
    gio_sinh: str | int
    gioi_tinh: str | int
    ten: str = ""
    duong_lich: bool = True
    time_zone: float = Field(default=7.0, ge=-12, le=14)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": "2.0"}


@app.get("/stars")
def stars() -> dict[str, Any]:
    return load_star_registry()


@app.get("/cach-cuc")
def cach_cuc() -> list[dict[str, Any]]:
    return load_cach_cuc()


@app.post("/generate-chart")
def generate_chart(request: ChartRequest) -> dict[str, Any]:
    try:
        chart = lap_la_so(**request.model_dump())
        return analyze_chart(chart)
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
