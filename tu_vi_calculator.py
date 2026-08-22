"""Deterministic chart relations and structured vận context."""
from __future__ import annotations

from copy import deepcopy
from typing import Any
import re
import unicodedata

from tuvi_engine.ai_context import build_ai_context
from tuvi_engine.van_calculator import calculate_van_layers
from tuvi_engine.van_reasoning import build_reasoning_context
from tuvi_engine.van_tieu_van_patch import build_tieu_van_source_mapping

BRANCHES = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]

# Tam phương: 4 tổ hợp cố định, mỗi tổ hợp gồm 3 Địa Chi.
TAM_PHUONG_GROUPS = (
    frozenset(("Thân", "Tý", "Thìn")),
    frozenset(("Dần", "Ngọ", "Tuất")),
    frozenset(("Tỵ", "Dậu", "Sửu")),
    frozenset(("Hợi", "Mão", "Mùi")),
)

NHI_HOP = {
    frozenset(("Tý", "Sửu")),
    frozenset(("Dần", "Hợi")),
    frozenset(("Mão", "Tuất")),
    frozenset(("Thìn", "Dậu")),
    frozenset(("Tỵ", "Thân")),
    frozenset(("Ngọ", "Mùi")),
}


def _norm_branch(value: Any) -> str | None:
    """Chuẩn hóa Địa Chi dạng Tý/Ty/ty1/ty2... về tên chuẩn."""
    if value is None:
        return None
    text = unicodedata.normalize("NFD", str(value)).strip().casefold()
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = re.sub(r"\d+$", "", text)
    aliases = {
        "ty": "Tý",
        "su u": "Sửu",
        "suu": "Sửu",
        "dan": "Dần",
        "mao": "Mão",
        "thin": "Thìn",
        "ti": "Tỵ",
        "ty": "Tý",
        "ngo": "Ngọ",
        "mui": "Mùi",
        "than": "Thân",
        "dau": "Dậu",
        "tuat": "Tuất",
        "hoi": "Hợi",
    }
    return aliases.get(text)


def _branch_distance(a: str, b: str) -> int:
    return (BRANCHES.index(b) - BRANCHES.index(a)) % 12


def relation(a: dict[str, Any], b: dict[str, Any]) -> str:
    """Quan hệ cung theo đúng hình học Tử Vi đã quy định.

    - Tam phương: cùng một trong 4 nhóm Thân-Tý-Thìn / Dần-Ngọ-Tuất /
      Tỵ-Dậu-Sửu / Hợi-Mão-Mùi.
    - Xung chiếu: Địa Chi đối nhau, ví dụ Tý-Ngọ, Sửu-Mùi, Dần-Thân...
    - Nhị hợp: các cặp ngang hàng Tý-Sửu, Hợi-Dần, Tuất-Mão, Thìn-Dậu,
      Tỵ-Thân, Ngọ-Mùi.
    - Giáp cung: đúng cung_so -1 và +1 trong vòng 12 cung.
    """
    branch_a = _norm_branch(a.get("dia_chi"))
    branch_b = _norm_branch(b.get("dia_chi"))
    if branch_a is None or branch_b is None:
        return "unknown"
    if branch_a == branch_b and a.get("cung_so") == b.get("cung_so"):
        return "dong_cung"

    pos_a = a.get("cung_so")
    pos_b = b.get("cung_so")
    if isinstance(pos_a, int) and isinstance(pos_b, int):
        # Cung trước và cung sau của cung gốc: +1 / -1, vòng 12 cung.
        palace_distance = (pos_b - pos_a) % 12
        if palace_distance in (1, 11):
            return "giap_cung"

    if any({branch_a, branch_b}.issubset(group) for group in TAM_PHUONG_GROUPS):
        return "tam_hop"

    if _branch_distance(branch_a, branch_b) == 6:
        return "xung_chieu"

    if frozenset((branch_a, branch_b)) in NHI_HOP:
        return "nhi_hop"
    return "other"


def _branch_number(value: Any) -> int | None:
    if isinstance(value, int) and 1 <= value <= 12:
        return value
    normalized = _norm_branch(value)
    if normalized in BRANCHES:
        return BRANCHES.index(normalized) + 1
    return None


def _palace_by_number(chart: dict[str, Any], palace_number: Any) -> dict[str, Any] | None:
    """Tra đúng ô cung của lá số theo cung số canonical 1..12."""
    try:
        number = int(palace_number)
    except (TypeError, ValueError):
        return None
    for palace in (chart.get("12_cung") or {}).values():
        if isinstance(palace, dict) and palace.get("cung_so") == number:
            return palace
    return None


def _sync_tieu_van(chart: dict[str, Any], van: dict[str, Any]) -> None:
    """Tính Tiểu vận động và tra sang đúng cung của từng lá số.

    Quy tắc Tiểu vận trả về ``cung_so`` theo bàn 12 vị trí. Không tra ngược
    một lần nữa bằng tên Địa Chi, vì làm vậy sẽ tạo double-mapping.
    """
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

    target_palace = _palace_by_number(chart, canonical.get("cung_so"))
    if target_palace is None:
        raise ValueError(f"Không tìm thấy cung số {canonical.get('cung_so')!r} trong 12 cung lá số")

    canonical["cung_so"] = target_palace.get("cung_so")
    canonical["cung"] = target_palace.get("cung")
    canonical["dia_chi"] = target_palace.get("dia_chi") or canonical.get("cung_dia_chi_ten")
    canonical["dia_chi_chuan"] = _norm_branch(target_palace.get("dia_chi"))
    canonical["can_chi"] = target_palace.get("can_chi")
    canonical["cung_chuc_nang"] = target_palace.get("cung")
    van["tieu_van"] = canonical


def _dynamic_sync_contract(van: dict[str, Any]) -> dict[str, Any]:
    tieu = van.get("tieu_van") or {}
    year = van.get("year") or {}
    return {
        "source_of_truth": "calculate_van_layers -> dynamic_tieu_van_rule -> chart.palace_by_cung_so",
        "year": year.get("nam"),
        "year_chi": year.get("chi_ten"),
        "tieu_van_cung_so": tieu.get("cung_so"),
        "tieu_van_cung": tieu.get("cung"),
        "tieu_van_dia_chi": tieu.get("dia_chi"),
        "tieu_van_dia_chi_chuan": tieu.get("dia_chi_chuan"),
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
                    "dia_chi_a": _norm_branch(a.get("dia_chi")),
                    "dia_chi_b": _norm_branch(b.get("dia_chi")),
                    "quan_he": r,
                })

    van = calculate_van_layers(chart, year=year, month=month, day=day, hour=hour)
    _sync_tieu_van(chart, van)
    van["sync_contract"] = _dynamic_sync_contract(van)
    van["reasoning_context"] = build_reasoning_context(chart, van)
    chart["ai_context"] = build_ai_context(chart, van=deepcopy(van))

    return {
        "calculator_version": "3.6",
        "relations": relations,
        "van": van,
    }
