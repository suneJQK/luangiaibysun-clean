from __future__ import annotations

import json
import uuid
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
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

app = FastAPI(title="TV AI - Tử Vi Đẩu Số", version="2.5")
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


def _available_ai_modes() -> list[dict[str, str]]:
    modes: list[dict[str, str]] = []
    if not AI_MODE_DIR.exists():
        return modes
    for path in sorted(AI_MODE_DIR.glob("*.txt")):
        text = path.read_text(encoding="utf-8").strip()
        first_line = next((x.strip() for x in text.splitlines() if x.strip()), "")
        name = first_line.split(":", 1)[1].strip() if ":" in first_line else path.stem
        modes.append({"id": path.stem, "name": name, "file": path.name})
    return modes


def _load_ai_mode(mode_id: str | None) -> tuple[str, str]:
    modes = _available_ai_modes()
    if not modes:
        return "", "standard"
    wanted = (mode_id or "standard").strip().lower()
    path = AI_MODE_DIR / f"{wanted}.txt"
    if not path.exists():
        path = AI_MODE_DIR / f"{modes[0]['id']}.txt"
        wanted = modes[0]["id"]
    return path.read_text(encoding="utf-8").strip(), wanted


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


@app.get("/", response_class=FileResponse)
def root() -> FileResponse:
    if not WEB_INDEX.exists():
        raise HTTPException(status_code=500, detail="Thiếu index.html")
    return FileResponse(WEB_INDEX, media_type="text/html")


@app.get("/ai-mode", response_class=FileResponse)
def ai_mode_page() -> FileResponse:
    if not AI_MODE_INDEX.exists():
        raise HTTPException(status_code=500, detail="Thiếu ai_mode.html")
    return FileResponse(AI_MODE_INDEX, media_type="text/html")


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "service": "tv-ai", "version": "2.5"}


@app.get("/api/ai-modes")
def ai_modes() -> dict[str, Any]:
    return {"modes": _available_ai_modes()}


@app.get("/api/ai-providers")
def ai_providers() -> dict[str, Any]:
    return {
        "providers": [
            {"id": "gemini", "name": "Gemini", "env_key": "GEMINI_API_KEY", "model_env": "GEMINI_MODEL"},
            {"id": "openai", "name": "ChatGPT / OpenAI", "env_key": "OPENAI_API_KEY", "model_env": "OPENAI_MODEL"},
        ]
    }


@app.get("/api/google-sheets-test")
def google_sheets_test() -> dict[str, Any]:
    try:
        import google_sheets_storage as storage
        result = storage.save_user_profile(
            user_id="diagnostic",
            name="_TEST_",
            ngay_sinh="01/01/2000",
            gio_sinh="Tý",
            gioi_tinh="Nam",
            lich="Dương lịch",
            time_zone=7,
            created_at=datetime.now(timezone.utc).astimezone(VN_TZ).isoformat(timespec="seconds"),
        )
        return {"ok": True, "result": result}
    except Exception as exc:
        return {"ok": False, "error_type": type(exc).__name__, "error": str(exc)}


@app.get("/api/cach-cuc")
def cach_cuc() -> dict[str, Any]:
    return {"count": len(load_cach_cuc()), "items": load_cach_cuc()}


@app.post("/api/lap-so")
def lap_so(req: BirthRequest) -> dict[str, Any]:
    try:
        chart = _prepare_chart(req)
        save_status = _save_profile(req)
        chart.setdefault("storage", {})["user_profile"] = save_status
        return chart
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Không thể lập lá số: {type(exc).__name__}: {exc}") from exc


@app.post("/api/luan-giai")
def luan_giai(req: AskRequest, request: Request) -> dict[str, Any]:
    try:
        chart = _prepare_chart(req)
        calc = calculate_chart(chart)
        ai_context = chart.get("ai_context", {})
        cach_cuc_analysis = chart.get("cach_cuc_analysis", {})
        books = _load_json(BOOKS_FILE, {})
        mode_text, mode_id = _load_ai_mode(request.cookies.get("tv_ai_mode", "standard"))
        provider_id = normalize_provider(req.provider or request.cookies.get("tv_ai_provider", "gemini"))
        prompt = f'''Năm luận: {req.year or date.today().year}\n\nCHẾ ĐỘ LUẬN GIẢI ĐƯỢC CHỌN:\n{mode_text}\n\nCÂU HỎI:\n{req.question}\n\nDỮ LIỆU LÁ SỐ:\n{_compact(chart)}\n\nBẰNG CHỨNG CÁCH CỤC:\n{_compact(cach_cuc_analysis, 30000)}\n\nQUAN HỆ CUNG:\n{_compact(ai_context.get("relationship_knowledge", {}), 20000)}\n\nCONTEXT AI:\n{_compact(ai_context, 50000)}\n\nTÍNH TOÁN KHÁC:\n{_compact(calc, 30000)}\n\nTÀI LIỆU:\n{_compact(books, 40000)}\n\nQUY TẮC BẮT BUỘC:\n- Chỉ dùng Cách Cục đã match từ engine.\n- Cách Cục lõi và modifier phá/giảm phải được luận riêng rồi tổng hợp.\n- Đối chiếu Đồng cung, Tam Hợp, Xung Chiếu, Nhị Hợp, Giáp Cung và Tuần/Triệt.\n- Không tự an sao, không tự thêm hoặc sửa dữ liệu engine.\n- Nếu không có Cách Cục match, nói rõ là chưa xác định được từ bộ điều kiện hiện tại.'''
        answer, selected_provider = generate_ai(
            provider=provider_id,
            system_instruction=_system_prompt() + "\nAI chỉ diễn giải dữ liệu từ engine Python local.",
            prompt=prompt,
        )
        return {
            "chart": chart,
            "calculation": calc,
            "answer": answer,
            "ai_status": "ok",
            "ai_mode": mode_id,
            "ai_provider": selected_provider,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Không thể luận giải: {type(exc).__name__}: {exc}") from exc
