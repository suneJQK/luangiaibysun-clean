from __future__ import annotations

import json
import os
from typing import Any

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
HEADERS = ["ID", "Họ tên", "Ngày sinh", "Giờ sinh", "Giới tính", "Lịch", "Múi giờ", "Thời gian tạo"]


def _google_modules():
    try:
        from google.oauth2.service_account import Credentials
        from googleapiclient.discovery import build
        return Credentials, build
    except Exception as exc:
        raise RuntimeError(f"Thiếu thư viện Google Sheets: {type(exc).__name__}: {exc}") from exc


def _credentials():
    Credentials, _ = _google_modules()
    raw = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "").strip()
    if not raw:
        raise RuntimeError("Thiếu GOOGLE_SERVICE_ACCOUNT_JSON")
    try:
        info = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError("GOOGLE_SERVICE_ACCOUNT_JSON không phải JSON hợp lệ") from exc
    if not isinstance(info, dict) or not info.get("client_email") or not info.get("private_key"):
        raise RuntimeError("GOOGLE_SERVICE_ACCOUNT_JSON thiếu client_email hoặc private_key")
    return Credentials.from_service_account_info(info, scopes=SCOPES)


def _sheet_id() -> str:
    value = os.environ.get("GOOGLE_SHEET_ID", "").strip()
    if not value:
        raise RuntimeError("Thiếu GOOGLE_SHEET_ID")
    return value


def _service():
    _, build = _google_modules()
    return build("sheets", "v4", credentials=_credentials(), cache_discovery=False)


def save_user_profile(*, user_id: str, name: str, ngay_sinh: str, gio_sinh: str, gioi_tinh: str, lich: str, time_zone: float, created_at: str) -> dict[str, Any]:
    service = _service()
    spreadsheet_id = _sheet_id()
    values_api = service.spreadsheets().values()

    first = values_api.get(spreadsheetId=spreadsheet_id, range="A1:H1").execute()
    if not first.get("values"):
        values_api.update(
            spreadsheetId=spreadsheet_id,
            range="A1:H1",
            valueInputOption="RAW",
            body={"values": [HEADERS]},
        ).execute()

    row = [user_id, name, ngay_sinh, gio_sinh, gioi_tinh, lich, str(time_zone), created_at]
    result = values_api.append(
        spreadsheetId=spreadsheet_id,
        range="A:H",
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body={"values": [row]},
    ).execute()
    return {"saved": True, "updated_range": result.get("updates", {}).get("updatedRange")}
