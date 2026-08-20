from __future__ import annotations

import json
import os
from datetime import date
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from tuvi_lap_so_engine import lap_la_so
from tu_vi_calculator import calculate_chart
from chart_sanitizer import normalize_engine_chart
from tuvi_engine.data_loader import load_cach_cuc
from tuvi_engine.rules.analysis import analyze_chart

try:
    from google import genai
    from google.genai import types
except Exception:  # optional until AI endpoint is called
    genai = None
    types = None

ROOT = Path(__file__).resolve().parent.parent
BOOKS_FILE = ROOT / "books_cache.json"
ROOT_PROMPT_FILE = ROOT / "system_prompt_tuvi.txt"
PROMPT_DIR = ROOT / "system_prompts"

app = FastAPI(title="TV AI - Tử Vi Đẩu Số", version="2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class BirthRequest(BaseModel):
    ngay: int = Field(ge=1, le=31)
    thang: int = Field(ge=1, le=12)
    nam: int = Field(ge=1800, le=2200)
    gio_sinh: str | int
    gioi_tinh: str
    ten: str = ""
    duong_lich: bool = True
    time_zone: float = 7.0


class AskRequest(BirthRequest):
    question: str = Field(min_length=1, max_length=8000)
    year: int | None = None


def _load_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default
    except Exception:
        return default


def _system_prompt() -> str:
    parts: list[str] = []
    if ROOT_PROMPT_FILE.exists():
        parts.append(ROOT_PROMPT_FILE.read_text(encoding="utf-8").strip())
    if PROMPT_DIR.exists():
        for path in sorted(PROMPT_DIR.glob("*.txt")):
            text = path.read_text(encoding="utf-8").strip()
            if text:
                parts.append(text)
    return "\n\n".join(x for x in parts if x) or "Bạn là chuyên gia Tử Vi Đẩu Số."


def _compact(value: Any, limit: int = 90000) -> str:
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return text if len(text) <= limit else text[:limit] + "..."


def _prepare_chart(req: BirthRequest) -> dict[str, Any]:
    chart = lap_la_so(
        req.ngay,
        req.thang,
        req.nam,
        req.gio_sinh,
        req.gioi_tinh,
        req.ten,
        req.duong_lich,
        req.time_zone,
    )
    if len(chart.get("12_cung", {})) != 12:
        raise ValueError("Engine không tạo đủ 12 cung")
    analyzed = analyze_chart(chart)
    analyzed.setdefault("input", {})["lich"] = "Dương lịch" if req.duong_lich else "Âm lịch"
    return normalize_engine_chart(analyzed)


@app.get("/")
def root() -> dict[str, Any]:
    return {"name": "TV AI", "status": "ok", "api": "/api/docs", "version": "2.0"}


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "service": "tv-ai", "version": "2.0"}


@app.get("/api/cach-cuc")
def cach_cuc() -> dict[str, Any]:
    return {"count": len(load_cach_cuc()), "items": load_cach_cuc()}


@app.post("/api/lap-so")
def lap_so(req: BirthRequest) -> dict[str, Any]:
    try:
        return _prepare_chart(req)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Không thể lập lá số: {type(exc).__name__}: {exc}") from exc


@app.post("/api/luan-giai")
def luan_giai(req: AskRequest) -> dict[str, Any]:
    try:
        chart = _prepare_chart(req)
        calc = calculate_chart(chart)
        ai_context = chart.get("ai_context", {})
        cach_cuc_analysis = chart.get("cach_cuc_analysis", {})
        books = _load_json(BOOKS_FILE, {})
        prompt = f'''Năm luận: {req.year or date.today().year}\n\nCÂU HỎI:\n{req.question}\n\nDỮ LIỆU LÁ SỐ:\n{_compact(chart)}\n\nBẰNG CHỨNG CÁCH CỤC:\n{_compact(cach_cuc_analysis, 30000)}\n\nQUAN HỆ CUNG:\n{_compact(ai_context.get("relationship_knowledge", {}), 20000)}\n\nCONTEXT AI:\n{_compact(ai_context, 50000)}\n\nTÍNH TOÁN KHÁC:\n{_compact(calc, 30000)}\n\nTÀI LIỆU:\n{_compact(books, 40000)}\n\nQUY TẮC BẮT BUỘC:\n- Chỉ dùng Cách Cục đã match từ engine.\n- Cách Cục lõi và modifier phá/giảm phải được luận riêng rồi tổng hợp.\n- Đối chiếu Đồng cung, Tam Hợp, Xung Chiếu, Nhị Hợp, Giáp Cung và Tuần/Triệt.\n- Không tự an sao, không tự thêm hoặc sửa dữ liệu engine.\n- Nếu không có Cách Cục match, nói rõ là chưa xác định được từ bộ điều kiện hiện tại.'''

        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            return {"chart": chart, "calculation": calc, "answer": None, "ai_status": "missing_GEMINI_API_KEY"}
        if genai is None or types is None:
            raise RuntimeError("google-genai chưa được cài đặt")

        client = genai.Client(api_key=api_key)
        config = types.GenerateContentConfig(
            system_instruction=_system_prompt() + "\nAI chỉ diễn giải dữ liệu từ engine Python local.",
            temperature=0.2,
            max_output_tokens=30000,
        )
        response = client.models.generate_content(
            model=os.environ.get("GEMINI_MODEL", "gemini-3.6-flash"),
            contents=prompt,
            config=config,
        )
        return {
            "chart": chart,
            "calculation": calc,
            "answer": response.text,
            "ai_status": "ok",
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Không thể luận giải: {type(exc).__name__}: {exc}") from exc
