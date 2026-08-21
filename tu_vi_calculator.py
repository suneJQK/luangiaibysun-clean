"""Deterministic chart relations and structured vận context."""
from __future__ import annotations

from typing import Any

from tuvi_engine.van_calculator import calculate_van_layers
from tuvi_engine.van_reasoning import build_reasoning_context
from tuvi_engine.van_tieu_van_patch import build_tieu_van_source_mapping

BRANCHES = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]
NHI_HOP = {
    frozenset(("Tý", "Sửu")),
    frozenset(("Dần", "Hợi")),
    frozenset(("Mão", "Tuất")),
    frozenset(("Thìn", "Dậu")),
    frozenset(("Tỵ", "Thân")),
    frozenset(("Ngọ", "Mùi")),
}


def _branch_distance(a: str, b: str) -> int:
    return (BRANCHES.index(b) - BRANCHES.index(a)) % 12


def relation(a: dict[str, Any], b: dict[str, Any]) -> str:
    branch_a = a.get("dia_chi")
    branch_b = b.get("dia_chi")
    if branch_a not in BRANCHES or branch_b not in BRANCHES:
        return "unknown"

    # Giáp cung là quan hệ theo VỊ TRÍ 12 CUNG, không phải khoảng cách Địa Chi.
    pos_a = a.get("cung_so")
    pos_b = b.get("cung_so")
    if isinstance(pos_a, int) and isinstance(pos_b, int):
        palace_distance = abs(pos_a - pos_b) % 12
        if palace_distance in (1, 11):
            return "giap_cung"

    d = _branch_distance(branch_a, branch_b)
    if d in (4, 8):
        return "tam_hop"
    if d == 6:
        return "xung_chieu"
    if frozenset((branch_a, branch_b)) in NHI_HOP:
        return "nhi_hop"
    return "other"


def _branch_number(value: Any) -> int | None:
    if isinstance(value, int) and 1 <= value <= 12:
        return value
    text = str(value or "").strip()
    try:
        return BRANCHES.index(text) + 1
    except ValueError:
        return None


def _repair_tieu_van(chart: dict[str, Any], van: dict[str, Any]) -> None:
    """Ghi đè lớp Tiểu vận bằng công thức tuổi năm đã kiểm chứng.

    Đây là lớp bảo vệ tại điểm xuất dữ liệu cho app, để bản tính cũ trong
    ``van_calculator.py`` không thể làm sai vị trí Tiểu vận hiển thị.
    """
    thien_ban = chart.get("thien_ban", {}) if isinstance(chart, dict) else {}
    inp = chart.get("input", {}) if isinstance(chart, dict) else {}

    birth_branch = _branch_number(thien_ban.get("chi_nam"))
    year_branch = _branch_number((van.get("year") or {}).get("chi"))
    age = van.get("age")
    gender = str(inp.get("gioi_tinh", "Nam"))

    if birth_branch is None or year_branch is None:
        return

    corrected = build_tieu_van_source_mapping(
        lambda x: (int(x) - 1) % 12 + 1,
        lambda x: BRANCHES[(int(x) - 1) % 12],
        birth_branch,
        year_branch,
        gender,
        age=int(age) if age is not None else None,
    )
    van["tieu_van"] = corrected


def calculate_chart(
    chart: dict[str, Any],
    *,
    year: int | None = None,
    month: int | None = None,
    day: int | None = None,
    hour: int | None = None,
) -> dict[str, Any]:
    cungs = chart.get("12_cung", {}) if isinstance(chart, dict) else {}
    palaces = [v for v in cungs.values() if isinstance(v, dict)]
    relations: list[dict[str, Any]] = []
    for i, a in enumerate(palaces):
        for b in palaces[i + 1:]:
            r = relation(a, b)
            if r in {"tam_hop", "xung_chieu", "nhi_hop", "giap_cung"}:
                relations.append({
                    "a": a.get("cung"),
                    "b": b.get("cung"),
                    "cung_a": a.get("cung_so"),
                    "cung_b": b.get("cung_so"),
                    "quan_he": r,
                })

    van = calculate_van_layers(
        chart,
        year=year,
        month=month,
        day=day,
        hour=hour,
    )

    # Sửa lớp Tiểu vận ngay trước khi xây reasoning_context và trước khi
    # trả dữ liệu cho API/UI.
    _repair_tieu_van(chart, van)

    van["reasoning_context"] = build_reasoning_context(chart, van)

    return {
        "calculator_version": "3.2",
        "relations": relations,
        "van": van,
    }
