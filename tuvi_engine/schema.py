"""Canonical V2 chart schema helpers."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "2.0"
ENGINE_NAME = "luangiaibysun-v2"
SCHEMA_PATH = Path(__file__).with_name("schema_v2.json")


def build_meta(*, source: str = "local_tuvi_engine") -> dict[str, str]:
    return {
        "schema_version": SCHEMA_VERSION,
        "engine": ENGINE_NAME,
        "source": source,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def to_v2_chart(chart: Any, *, source: str = "local_tuvi_engine") -> dict[str, Any]:
    if not isinstance(chart, dict):
        raise TypeError("chart phải là dict")
    out = deepcopy(chart)
    input_data = out.get("input")
    if not isinstance(input_data, dict):
        raise ValueError("chart thiếu trường input")
    out.pop("schema_version", None)
    out["meta"] = build_meta(source=source)
    out.setdefault("cach_cuc", [])
    out.setdefault("luan_giai", {})
    out["input"] = dict(input_data)
    return out


def validate_v2_chart(chart: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(chart, dict):
        return ["chart phải là object"]
    meta = chart.get("meta")
    if not isinstance(meta, dict):
        errors.append("meta phải là object")
    elif meta.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"meta.schema_version phải là {SCHEMA_VERSION}")
    required = ("input", "thien_ban", "12_cung")
    for key in required:
        if key not in chart:
            errors.append(f"thiếu trường {key}")
    input_data = chart.get("input")
    if isinstance(input_data, dict):
        for key in ("ngay", "thang", "nam", "gio_sinh", "gioi_tinh", "duong_lich", "time_zone"):
            if key not in input_data:
                errors.append(f"input thiếu {key}")
        if not isinstance(input_data.get("gioi_tinh"), str) or input_data.get("gioi_tinh") not in {"Nam", "Nữ"}:
            errors.append("input.gioi_tinh phải là Nam hoặc Nữ")
        if not isinstance(input_data.get("12_cung", chart.get("12_cung")), dict):
            errors.append("12_cung phải là object")
    cungs = chart.get("12_cung")
    if not isinstance(cungs, dict):
        errors.append("12_cung phải là object")
    elif len(cungs) != 12:
        errors.append(f"12_cung phải có đúng 12 cung, hiện có {len(cungs)}")
    return errors


def require_valid_v2_chart(chart: Any) -> dict[str, Any]:
    errors = validate_v2_chart(chart)
    if errors:
        raise ValueError("; ".join(errors))
    return chart
