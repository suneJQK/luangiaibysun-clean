from __future__ import annotations

import json
import uuid
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel, Field

from tuvi_lap_so_engine import lap_la_so
from tu_vi_calculator import calculate_chart
from chart_sanitizer import normalize_engine_chart
from tuvi_engine.data_loader import load_cach_cuc
from tuvi_engine.rules.analysis import analyze_chart
from ai_providers.router import generate as generate_ai, normalize_provider

ROOT = Path(__file__).resolve().parent.parent
BOOKS_FILE = ROOT / "books_cache.json"
ROOT_PROMPT_FILE = ROOT / "system_prompt_tuvi.txt"
PROMPT_DIR = ROOT / "system_prompts"
AI_MODE_DIR = ROOT / "ai_modes"
WEB_INDEX = ROOT / "index.html"
AI_MODE_INDEX = ROOT / "ai_mode.html"
VN_TZ = ZoneInfo("Asia/Ho_Chi_Minh")

app = FastAPI(title="TV AI - Tử Vi Đẩu Số", version="2.9")
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
    nam_xem: int | None = Field(default=None, ge=1800, le=2200)
    thang_xem: int | None = Field(default=None, ge=1, le=12)
    ngay_xem: int | None = Field(default=None, ge=1, le=31)
    gio_xem: int | None = Field(default=None, ge=1, le=12)


class AskRequest(BirthRequest):
    question: str = Field(min_length=1, max_length=8000)
    year: int | None = Field(default=None, ge=1800, le=2200)
    provider: str | None = None


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
    chart = lap_la_so(req.ngay, req.thang, req.nam, req.gio_sinh, req.gioi_tinh, req.ten, req.duong_lich, req.time_zone)
    if len(chart.get("12_cung", {})) != 12:
        raise ValueError("Engine không tạo đủ 12 cung")
    analyzed = analyze_chart(chart)
    analyzed.setdefault("input", {})["lich"] = "Dương lịch" if req.duong_lich else "Âm lịch"
    return normalize_engine_chart(analyzed)


def _view_year(req: BirthRequest, explicit_year: int | None = None) -> int:
    """Năm xem là một lựa chọn độc lập với năm sinh."""
    return int(explicit_year if explicit_year is not None else (req.nam_xem if req.nam_xem is not None else date.today().year))


def _view_args(req: BirthRequest, default_year: int | None = None) -> dict[str, Any]:
    return {
        "year": _view_year(req, default_year),
        "month": req.thang_xem,
        "day": req.ngay_xem,
        "hour": req.gio_xem,
    }


def _save_profile(req: BirthRequest) -> dict[str, Any]:
    try:
        from google_sheets_storage import save_user_profile
        created_at = datetime.now(timezone.utc).astimezone(VN_TZ).isoformat(timespec="seconds")
        return save_user_profile(
            user_id=str(uuid.uuid4()),
            name=req.ten.strip(),
            ngay_sinh=f"{req.ngay:02d}/{req.thang:02d}/{req.nam:04d}",
            gio_sinh=str(req.gio_sinh),
            gioi_tinh=req.gioi_tinh,
            lich="Dương lịch" if req.duong_lich else "Âm lịch",
            time_zone=req.time_zone,
            created_at=created_at,
        )
    except Exception as exc:
        return {"saved": False, "error": f"{type(exc).__name__}: {exc}"}


def _assert_ai_payload_sync(calc: dict[str, Any], ai_context: dict[str, Any]) -> None:
    """Fail closed if AI context and calculated vận layers disagree."""
    van = calc.get("van") or {}
    authoritative = van.get("tieu_van") or {}
    synced = (van.get("sync_contract") or {}).get("tieu_van_cung_so")
    if synced != authoritative.get("cung_so"):
        raise ValueError("Dữ liệu Tiểu vận nội bộ không đồng bộ")

    context_van = ai_context.get("van_han") or {}
    context_tieu = context_van.get("tieu_van") or {}
    if context_tieu != authoritative:
        raise ValueError("AI context và Tiểu vận authoritative không đồng bộ")

    palaces = ai_context.get("palaces") or {}
    palace_items = palaces.values() if isinstance(palaces, dict) else palaces
    forbidden = {"dai_van", "tieu_van", "luu_nien", "luu_dai_van", "luu_nguyet", "luu_nhat", "luu_thoi"}
    for palace in palace_items:
        if isinstance(palace, dict) and forbidden.intersection(palace):
            raise ValueError("AI context còn chứa dynamic vận tĩnh trong từng cung")


def _ai_context_for_request(chart: dict[str, Any], calc: dict[str, Any]) -> dict[str, Any]:
    context = chart.get("ai_context")
    if not isinstance(context, dict):
        raise ValueError("Thiếu AI context authoritative")
    _assert_ai_payload_sync(calc, context)
    return context


@app.post("/api/luan-giai")
def luan_giai(req: AskRequest) -> dict[str, Any]:
    try:
        viewing_year = _view_year(req, req.year)
        req.nam_xem = viewing_year
        chart = _prepare_chart(req)
        calc = calculate_chart(chart, **_view_args(req, viewing_year))
        chart["van"] = calc.get("van", {})
        chart.setdefault("viewing", {})["year"] = viewing_year

        context = _ai_context_for_request(chart, calc)
        mode_text, mode_id = _load_ai_mode(req.provider)
        books = _load_json(BOOKS_FILE, [])
        payload = {
            "question": req.question,
            "year": viewing_year,
            "mode": mode_id,
            "mode_prompt": mode_text,
            "chart_context": context,
            "books": books,
        }
        prompt = _compact(payload)
        system = _system_prompt()
        answer = generate_ai(system_instruction=system, prompt=prompt, provider=normalize_provider(req.provider))[0]
        return {"answer": answer, "year": viewing_year, "mode": mode_id}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Không thể luận giải: {type(exc).__name__}: {exc}") from exc
