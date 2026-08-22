"""Deterministic chart relations and authoritative 10-year vận context."""
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


def _palace_by_number(chart: dict[str, Any], palace_number: Any) -> dict[str, Any] | None:
    try:
        number = int(palace_number)
    except (TypeError, ValueError):
        return None
    for palace in (chart.get("12_cung") or {}).values():
        if isinstance(palace, dict) and int(palace.get("cung_so", 0) or 0) == number:
            return palace
    return None


def _palace_by_branch(chart: dict[str, Any], branch: Any) -> dict[str, Any] | None:
    target = _norm_branch(branch)
    if target is None:
        return None
    for palace in (chart.get("12_cung") or {}).values():
        if isinstance(palace, dict) and _norm_branch(palace.get("dia_chi")) == target:
            return palace
    return None


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
    if (BRANCHES.index(branch_b) - BRANCHES.index(branch_a)) % 12 == 6:
        return "xung_chieu"
    if frozenset((branch_a, branch_b)) in NHI_HOP:
        return "nhi_hop"
    return "other"


def _dv_direction_text(van: dict[str, Any]) -> tuple[int, str]:
    text = str(((van.get("dai_van") or {}).get("huong")) or "thuận").strip().casefold()
    if text == "nghịch":
        return -1, "nghịch"
    return 1, "thuận"


def _luu_nien_dai_van_position(
    nam_thu: int,
    cung_dai_van: int,
    direction: int,
) -> tuple[int, str]:
    """Authoritative 10-year sequence.

    Nam thu 1 = cung Dai van.
    Nam thu 2 = cung xung chieu.
    Nam thu 3 = xung chieu - direction (thuan -> -1, nghich -> +1).
    Nam thu 4 tro di tiep tuc tu nam thu 3 theo direction.
    """
    xung = (int(cung_dai_van) + 6 - 1) % 12 + 1
    if nam_thu == 1:
        return int(cung_dai_van), "Năm 1 = cung Đại vận."
    if nam_thu == 2:
        return xung, "Năm 2 = cung xung chiếu."
    # Year 3 is the special transition step; after that, continue in the
    # same direction as the main vòng vận.
    offset_from_xung = nam_thu - 3
    step = int(direction)
    cung = (xung - step + offset_from_xung * step - 1) % 12 + 1
    if nam_thu == 3:
        detail = "Năm 3 = xung chiếu -1 theo vòng thuận." if direction == 1 else "Năm 3 = xung chiếu +1 theo vòng nghịch."
    else:
        detail = "Từ năm 4 tiếp tục +1 theo vòng thuận." if direction == 1 else "Từ năm 4 tiếp tục -1 theo vòng nghịch."
    return cung, detail


def _current_dai_van(van: dict[str, Any]) -> dict[str, Any] | None:
    dv = (van.get("dai_van") or {}).get("dang_xet") or {}
    if not dv or dv.get("cung_so") is None or dv.get("tuoi_bat_dau") is None:
        return None
    return dv


def _build_luu_nien_dai_van_10_nam(chart: dict[str, Any], van: dict[str, Any]) -> list[dict[str, Any]]:
    dv = _current_dai_van(van)
    year_info = van.get("year") or {}
    if dv is None or year_info.get("nam") is None:
        return []

    direction, direction_name = _dv_direction_text(van)
    start_age = int(dv["tuoi_bat_dau"])
    start_year = int(year_info.get("nam")) - int(van.get("age")) + start_age
    rows: list[dict[str, Any]] = []

    for nam_thu in range(1, 11):
        tuoi = start_age + nam_thu - 1
        nam = start_year + nam_thu - 1
        cung_so, calc = _luu_nien_dai_van_position(nam_thu, int(dv["cung_so"]), direction)
        palace = _palace_by_number(chart, cung_so) or {}
        rows.append({
            "nam": nam,
            "tuoi": tuoi,
            "nam_thu": nam_thu,
            "cung_so": cung_so,
            "cung": palace.get("cung"),
            "dia_chi": palace.get("dia_chi"),
            "can_chi": palace.get("can_chi"),
            "la_nam_dang_xem": nam == int(year_info.get("nam")),
            "huong": direction_name,
            "cung_dai_van": int(dv["cung_so"]),
            "cung_xung_chieu": (int(dv["cung_so"]) + 6 - 1) % 12 + 1,
            "cach_tinh": calc,
        })
    return rows


def _build_tieu_van_for_year(chart: dict[str, Any], birth_branch: int, year: int, gender: str, age: int) -> dict[str, Any]:
    # The dedicated patch is the single source of truth for Tiểu vận.
    _, target_branch = __import__("tuvi_engine.van_calculator", fromlist=["can_chi_year"]).can_chi_year(year)
    canonical = build_tieu_van_source_mapping(
        lambda x: (int(x) - 1) % 12 + 1,
        lambda x: BRANCHES[(int(x) - 1) % 12],
        birth_branch,
        target_branch,
        gender,
        age=age,
    )
    target_palace = _palace_by_number(chart, canonical.get("cung_so")) or {}
    return {
        **canonical,
        "nam": year,
        "tuoi": age,
        "nam_thu": None,
        "cung_so": target_palace.get("cung_so", canonical.get("cung_so")),
        "cung": target_palace.get("cung"),
        "dia_chi": target_palace.get("dia_chi"),
        "dia_chi_chuan": _norm_branch(target_palace.get("dia_chi")),
        "can_chi": target_palace.get("can_chi"),
        "cung_chuc_nang": target_palace.get("cung"),
        "la_nam_dang_xem": False,
        "source_of_truth": "van_tieu_van_patch.build_tieu_van_source_mapping",
        "cach_tinh": "Cung khởi theo Tam hợp Chi năm sinh; đặt cung khởi làm mốc Tý; Nam đếm thuận, Nữ đếm nghịch đến Chi năm xem.",
    }


def _build_tieu_van_10_nam(chart: dict[str, Any], van: dict[str, Any]) -> list[dict[str, Any]]:
    dv = _current_dai_van(van)
    year_info = van.get("year") or {}
    if dv is None or year_info.get("nam") is None:
        return []

    thien_ban = chart.get("thien_ban") or {}
    birth_branch = _branch_number(thien_ban.get("chi_nam"))
    if birth_branch is None:
        return []
    gender = str((chart.get("input") or {}).get("gioi_tinh", "Nam"))

    start_age = int(dv["tuoi_bat_dau"])
    start_year = int(year_info.get("nam")) - int(van.get("age")) + start_age
    rows: list[dict[str, Any]] = []
    direction_name = "thuận" if gender.strip().casefold() in {"nam", "male", "m", "1"} else "nghịch"

    for nam_thu in range(1, 11):
        tuoi = start_age + nam_thu - 1
        nam = start_year + nam_thu - 1
        row = _build_tieu_van_for_year(chart, birth_branch, nam, gender, tuoi)
        row["nam_thu"] = nam_thu
        row["huong"] = direction_name
        row["la_nam_dang_xem"] = nam == int(year_info.get("nam"))
        row["cung_khoi"] = row.get("cung_khoi")
        row["cung_khoi_ten"] = row.get("cung_khoi_ten")
        rows.append(row)
    return rows


def _sync_layers(chart: dict[str, Any], van: dict[str, Any]) -> None:
    luu_rows = _build_luu_nien_dai_van_10_nam(chart, van)
    tieu_rows = _build_tieu_van_10_nam(chart, van)
    year = int((van.get("year") or {}).get("nam"))

    van["luu_nien_dai_van_10_nam"] = luu_rows
    van["tieu_van_10_nam"] = tieu_rows
    van["van_10_nam"] = {
        "source_of_truth": "tu_vi_calculator authoritative 10-year layer",
        "dai_van_cung_so": ((van.get("dai_van") or {}).get("dang_xet") or {}).get("cung_so"),
        "dai_van_tuoi_bat_dau": ((van.get("dai_van") or {}).get("dang_xet") or {}).get("tuoi_bat_dau"),
        "dai_van_tuoi_ket_thuc": ((van.get("dai_van") or {}).get("dang_xet") or {}).get("tuoi_ket_thuc"),
        "huong_vong_van": "thuận" if _dv_direction_text(van)[0] == 1 else "nghịch",
        "luu_nien_dai_van": luu_rows,
        "tieu_van": tieu_rows,
    }

    current_luu = next((r for r in luu_rows if r["nam"] == year), None)
    current_tieu = next((r for r in tieu_rows if r["nam"] == year), None)

    if current_luu:
        van["luu_nien_dai_van"] = {
            "cung_so": current_luu["cung_so"],
            "cung": current_luu["cung"],
            "dia_chi": current_luu["dia_chi"],
            "tuoi": current_luu["tuoi"],
            "nam_thu_trong_dai_van": current_luu["nam_thu"],
            "dai_van_cung_so": current_luu["cung_dai_van"],
            "cung_xung_chieu": current_luu["cung_xung_chieu"],
            "chieu_van": "thuận (+1 cung)" if _dv_direction_text(van)[0] == 1 else "nghịch (-1 cung)",
            "phuong_phap": "Năm 1=Đại vận; năm 2=Xung chiếu; năm 3=xung chiếu đối ứng; từ năm 4 tiếp tục theo chiều vòng vận.",
        }
    if current_tieu:
        van["tieu_van"] = current_tieu

    base_luu = van.get("luu_nien") or {}
    base_luu["cung_luu_nien_trong_dai_van"] = current_luu.get("cung_so") if current_luu else None
    base_luu["cung_luu_nien_trong_dai_van_detail"] = current_luu
    van["luu_nien"] = base_luu

    van["sync_contract"] = {
        "source_of_truth": "Lưu niên=Chi năm xem; Lưu niên Đại vận=chuỗi 10 năm authoritative; Tiểu vận=chuỗi 10 năm authoritative",
        "year": year,
        "year_chi": (van.get("year") or {}).get("chi_ten"),
        "luu_nien_cung_so": (base_luu.get("cung_so") if base_luu else None),
        "luu_nien_dai_van_cung_so": current_luu.get("cung_so") if current_luu else None,
        "tieu_van_cung_so": current_tieu.get("cung_so") if current_tieu else None,
        "tieu_van_cung": current_tieu.get("cung") if current_tieu else None,
        "tieu_van_dia_chi": current_tieu.get("dia_chi") if current_tieu else None,
        "tieu_van_chi_nam": current_tieu.get("chi_ten") if current_tieu else None,
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
    _sync_layers(chart, van)
    van["reasoning_context"] = build_reasoning_context(chart, van)
    chart["ai_context"] = build_ai_context(chart, van=deepcopy(van))

    return {
        "calculator_version": "4.0-authoritative-10y",
        "relations": relations,
        "van": van,
    }
