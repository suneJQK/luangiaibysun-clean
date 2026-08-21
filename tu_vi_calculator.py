"""Deterministic chart relations and structured vận context."""
from __future__ import annotations

from copy import deepcopy
from typing import Any

from tuvi_engine.ai_context import build_ai_context
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


def _palace_by_branch(chart: dict[str, Any], branch_name: str) -> dict[str, Any] | None:
    """Tra cung chức năng thực tế của lá số theo Địa Chi cung Tiểu vận."""
    for palace in (chart.get("12_cung") or {}).values():
        if isinstance(palace, dict) and palace.get("dia_chi") == branch_name:
            return palace
    return None


def _sync_tieu_van(chart: dict[str, Any], van: dict[str, Any]) -> None:
    """Tính Tiểu vận động và tra sang đúng cung của từng lá số."""
    thien_ban = chart.get("thien_ban", {}) if isinstance(chart, dict) else {}
    inp = chart.get("input", {}) if isinstance(chart, dict) else {}
    birth_branch = _branch_number(thien_ban.get("chi_nam"))
    year_branch = _branch_number((van.get("year") or {}).get("chi"))
    age = van.get("age")
    gender = str(inp.get("gioi_tinh", "Nam"))
    if birth_branch is None or year_branch is None:
        return

    canonical = build_tieu_van_source_mapping(
        lambda x: (int(x) - 1) % 12 + 1,
        lambda x: BRANCHES[(int(x) - 1) % 12],
        birth_branch,
        year_branch,
        gender,
        age=int(age) if age is not None else None,
    )

    target_branch_name = canonical.get("cung_dia_chi_ten")
    target_palace = _palace_by_branch(chart, str(target_branch_name)) if target_branch_name else None
    if target_palace is None:
        raise ValueError(f"Không tìm thấy cung có Địa Chi {target_branch_name!r} trong 12 cung lá số")

    # Giữ số cung từ lá số thật; không suy ra tên cung bằng một số hard-code.
    canonical["cung_so"] = target_palace.get("cung_so")
    canonical["cung"] = target_palace.get("cung")
    canonical["dia_chi"] = target_palace.get("dia_chi")
    canonical["can_chi"] = target_palace.get("can_chi")
    canonical["cung_chuc_nang"] = target_palace.get("cung")
    van["tieu_van"] = canonical


def _dynamic_sync_contract(van: dict[str, Any]) -> dict[str, Any]:
    tieu = van.get("tieu_van") or {}
    year = van.get("year") or {}
    return {
        "source_of_truth": "calculate_van_layers -> dynamic_tieu_van_rule -> chart.palace_by_branch",
        "year": year.get("nam"),
        "year_chi": year.get("chi_ten"),
        "tieu_van_cung_so": tieu.get("cung_so"),
        "tieu_van_cung": tieu.get("cung"),
        "tieu_van_dia_chi": tieu.get("dia_chi"),
        "tieu_van_chi_nam": tieu.get("chi_ten"),
        "tieu_van_tuoi": tieu.get("tuoi"),
        "static_palace_tieu_van_must_not_be_used": True,
    }


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

    # Một nguồn xác thực duy nhất cho Tiểu vận, tính động theo từng lá số/năm.
    _sync_tieu_van(chart, van)
    van["sync_contract"] = _dynamic_sync_contract(van)
    van["reasoning_context"] = build_reasoning_context(chart, van)

    # AI context được xây sau khi đã có đầy đủ lớp vận của năm xem.
    chart["ai_context"] = build_ai_context(chart, van=deepcopy(van))

    return {
        "calculator_version": "3.4",
        "relations": relations,
        "van": van,
    }
