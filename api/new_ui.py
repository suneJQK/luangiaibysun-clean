from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse

ROOT = Path(__file__).resolve().parent.parent
UI_ROOT = (ROOT / "new-ui").resolve()

app = FastAPI(title="TV AI New UI")

ALLOWED = {
    "index.html": "text/html; charset=utf-8",
    "style.css": "text/css; charset=utf-8",
    "app.js": "application/javascript; charset=utf-8",
}


def _asset_path(path: str) -> tuple[Path, str]:
    clean = (path or "index.html").lstrip("/")
    if clean in {"", "."}:
        clean = "index.html"
    if clean not in ALLOWED:
        raise HTTPException(status_code=404, detail="New UI asset not found")
    target = (UI_ROOT / clean).resolve()
    if target.parent != UI_ROOT or not target.is_file():
        raise HTTPException(status_code=404, detail="New UI asset not found")
    return target, ALLOWED[clean]


@app.get("/")
def index(path: str = Query(default="index.html")) -> FileResponse:
    target, media_type = _asset_path(path)
    return FileResponse(target, media_type=media_type)


@app.get("/{asset:path}")
def asset(asset: str) -> FileResponse:
    target, media_type = _asset_path(asset)
    return FileResponse(target, media_type=media_type)
