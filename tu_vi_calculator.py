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
    raw = str(value).strip().casefold()
    if raw in {"ty1", "tý", "ty"}:
        return "Tý"
    if raw in {"ty2", "tỵ", "tị", "ti"}:
        return "Tỵ"
    text = unicodedata.normalize("NFD", raw)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = re.sub(r"\d+$", "", text)
    aliases = {
        "suu": "Sửu", "dan": "Dần", "mao": "Mão", "thin": "Thìn",
        "ngo": "Ngọ", "mui": "Mùi", "than": "Thân", "dau": "Dậu",
        "tuat": "Tuất", "hoi": "Hợi",
    }
    return aliases.get(text)


def _branch_number(value: Any) -> int | None:
    normalized = _norm_branch(value)
    return BRANCHES.index(normalized) + 1 if normalized in BRANCHES else None


def _branch_distance(a: str, b: str) -> int:
    return (BRANCHES.index(b) - BRANCHES.index(a)) % 12


def relation(a: dict[str, Any], b: dict[str, Any]) -> str:
    branch_a = _norm_branch(a.get("dia_chi"))
    branch_b = _norm_branch(b.get("dia_chi"))
    if branch_a is None or branch_b is None:
        return "unknown"
    if branch_a == branch_b and a.get("cung_so") == b.get("cung_so"):
        return "dong_cung"

    pos_a = a.get("cung_so")
    pos_b = b.get("cung_so")
    if isinstance(pos_a, int) and isinstance(pos_b, int):
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


def _branch_palace_map(chart: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for palace in (chart.get("12_cung") or {}).values():
        if not isinstance(palace, dict):
            continue
        branch = _norm_branch(palace.get("dia_chi"))
        if branch:
            result[branch] = palace
    return result


def _palace_by_branch(chart: dict[str, Any], branch: Any) -> dict[str, Any] | None:
    branch_name = _norm_branch(branch)
    return _branch_palace_map(chart).get(branch_name) if branch_name else None


def _palace_by_number(chart: dict[str, Any], palace_number: Any) -> dict[str, Any] | None:
    try:
        number = int(palace_number)
    except (TypeError, ValueError):
        return None
    for palace in (chart.get("12_cung") or {}).values():
        if isinstance(palace, dict) and palace.get("cung_so") == number:
            return palace
    return None


def _source_luu_nien_dai_van(age: int, cung_dai_van: int, bat_dau: int, direction: int) -> int | None:
    """Lưu niên trong Đại vận theo đúng chuỗi lndv() nguồn.

    Đây là lớp KHÁC với Lưu niên bản mệnh:
    - Lưu niên bản mệnh: an trực tiếp theo Chi năm xem.
    - Lưu niên Đại vận: dịch từ cung Đại vận hiện hành theo tuổi trong Đại vận.
    """
    step = 1 if direction >= 0 else -1
    khoi = int(age) - int(bat_dau)
    x = int(cung_dai_van)
    if khoi < 0 or khoi > 9:
        return None
    if khoi == 0:
        return x
    if khoi == 1:
        return (x + 6 - 1) % 12 + 1
    if khoi == 2:
        return (x + 6 - step - 1) % 12 + 1
    return (x + 6 + (khoi - 3) * step - 1) % 12 + 1


def _sync_luu_nien_layers(chart: dict[str, Any], van: dict[str, Any]) -> None:
    """Đóng dấu rõ 3 lớp vận để downstream/AI không nhập nhằng."""
    year = van.get("year") or {}
    target_branch = year.get("chi")
    luu_nien_palace = _palace_by_branch(chart, target_branch)
    luu_nien = van.get("luu_nien") or {}

    dv = (van.get("dai_van") or {}).get("dang_xet") or {}
    age = van.get("age")
    direction_text = (van.get("dai_van") or {}).get("huong", "thuận")
    direction = 1 if direction_text == "thuận" else -1

    luu_nien_dv_palace_no = None
    if dv and age is not None:
        luu_nien_dv_palace_no = _source_luu_nien_dai_van(
            int(age),
            int(dv["cung_so"]),
            int(dv["tuoi_bat_dau"]),
            direction,
        )

    dv_palace = _palace_by_number(chart, luu_nien_dv_palace_no)
    if luu_nien_dv_palace_no is not None:
        luu_nien["cung_luu_nien_trong_dai_van"] = luu_nien_dv_palace_no
        luu_nien["cung_luu_nien_trong_dai_van_detail"] = {
            "cung_so": dv_palace.get("cung_so") if dv_palace else luu_nien_dv_palace_no,
            "cung": dv_palace.get("cung") if dv_palace else None,
            "dia_chi": _norm_branch(dv_palace.get("dia_chi")) if dv_palace else None,
        }

    luu_nien["cung_so"] = luu_nien_palace.get("cung_so") if luu_nien_palace else None
    luu_nien["cung_nam"] = luu_nien["cung_so"]
    luu_nien["cung_detail"] = {
        "cung_so": luu_nien_palace.get("cung_so") if luu_nien_palace else None,
        "cung": luu_nien_palace.get("cung") if luu_nien_palace else None,
        "dia_chi": _norm_branch(luu_nien_palace.get("dia_chi")) if luu_nien_palace else None,
        "can_chi": luu_nien_palace.get("can_chi") if luu_nien_palace else None,
    }
    luu_nien["phuong_phap"] = "Lưu niên bản mệnh = cung có Chi năm xem; Lưu niên Đại vận = lndv() trong Đại vận hiện hành."
    van["luu_nien"] = luu_nien
    van["luu_nien_dai_van"] = {
        "cung_so": luu_nien_dv_palace_no,
        "cung": dv_palace.get("cung") if dv_palace else None,
        "dia_chi": _norm_branch(dv_palace.get("dia_chi")) if dv_palace else None,
        "tuoi": age,
        "dai_van_cung_so": dv.get("cung_so") if dv else None,
        "phuong_phap": "lndv(tuoi, cung_dai_van, tuoi_bat_dau, direction)",
    }


def _sync_tieu_van(chart: dict[str, Any], van: dict[str, Any]) -> None:
    """Tính Tiểu vận theo cung khởi + mốc Tý, rồi tra đúng cung thực tế."""
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
    canonical["dia_chi"] = target_palace.get("dia_chi")
    canonical["dia_chi_chuan"] = _norm_branch(target_palace.get("dia_chi"))
    canonical["can_chi"] = target_palace.get("can_chi")
    canonical["cung_chuc_nang"] = target_palace.get("cung")
    canonical["source_of_truth"] = "van_tieu_van_patch.build_tieu_van_source_mapping"
    van["tieu_van"] = canonical


def _dynamic_sync_contract(van: dict[str, Any]) -> dict[str, Any]:
    tieu = van.get("tieu_van") or {}
    year = van.get("year") or {}
    return {
        "source_of_truth": "Lưu niên=Chi năm xem; Lưu niên Đại vận=lndv(); Tiểu vận=cung khởi + mốc Tý",
        "year": year.get("nam"),
        "year_chi": year.get("chi_ten"),
        "luu_nien_cung_so": (van.get("luu_nien") or {}).get("cung_so"),
        "luu_nien_dai_van_cung_so": (van.get("luu_nien_dai_van") or {}).get("cung_so"),
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
    _sync_luu_nien_layers(chart, van)
    _sync_tieu_van(chart, van)
    van["sync_contract"] = _dynamic_sync_contract(van)
    van["reasoning_context"] = build_reasoning_context(chart, van)
    chart["ai_context"] = build_ai_context(chart, van=deepcopy(van))

    return {
        "calculator_version": "3.7",
        "relations": relations,
        "van": van,
    }
