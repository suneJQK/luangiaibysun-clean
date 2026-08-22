"""Compatibility wrapper: authoritative 10-year Dai Van / Tieu Van layers."""
from __future__ import annotations

from typing import Any

from .van_calculator_legacy import *  # noqa: F401,F403
from . import van_calculator_legacy as _legacy


def _palace_by_number(chart: dict[str, Any], palace_number: Any) -> dict[str, Any] | None:
    try:
        number = int(palace_number)
    except (TypeError, ValueError):
        return None
    for palace in (chart.get("12_cung") or {}).values():
        if isinstance(palace, dict) and palace.get("cung_so") == number:
            return palace
    return None


def _direction_from_dv(van: dict[str, Any]) -> int:
    return 1 if ((van.get("dai_van") or {}).get("huong") or "thuận") == "thuận" else -1


def _authoritative_luu_nien_dai_van_cung(cung_dai_van: int, year_index: int, direction: int) -> int:
    """0=Đại vận; 1=Xung chiếu; từ năm 3 dịch ngược chiều vòng vận."""
    if year_index == 0:
        return _legacy.check(cung_dai_van)
    if year_index == 1:
        return _legacy.check(cung_dai_van + 6)
    # Thuận => năm 3 bắt đầu -1; nghịch => năm 3 bắt đầu +1.
    movement = -direction
    return _legacy.check(cung_dai_van + 6 + (year_index - 1) * movement)


def _build_luu_nien_dai_van_10_nam(chart: dict[str, Any], van: dict[str, Any]) -> list[dict[str, Any]]:
    dv = (van.get("dai_van") or {}).get("dang_xet") or {}
    if not dv:
        return []
    start_age = int(dv["tuoi_bat_dau"])
    start_year = int(chart.get("input", {}).get("nam")) + start_age - 1
    direction = _direction_from_dv(van)
    rows: list[dict[str, Any]] = []
    for idx in range(10):
        age = start_age + idx
        target_year = start_year + idx
        cung_so = _authoritative_luu_nien_dai_van_cung(int(dv["cung_so"]), idx, direction)
        palace = _palace_by_number(chart, cung_so)
        rows.append({
            "nam": target_year,
            "tuoi": age,
            "nam_thu": idx + 1,
            "cung_so": cung_so,
            "cung": palace.get("cung") if palace else None,
            "dia_chi": palace.get("dia_chi") if palace else None,
            "can_chi": palace.get("can_chi") if palace else None,
            "la_nam_dang_xem": target_year == (van.get("year") or {}).get("nam"),
            "cach_tinh": (
                "Năm 1 = cung Đại vận; Năm 2 = cung xung chiếu; "
                "Năm 3 = xung chiếu ±1 theo chiều đối ứng; từ năm 4 tiếp tục cùng chiều."
            ),
        })
    return rows


def _build_tieu_van_10_nam(chart: dict[str, Any], van: dict[str, Any]) -> list[dict[str, Any]]:
    dv = (van.get("dai_van") or {}).get("dang_xet") or {}
    birth_branch = _legacy._birth_year_branch(chart)
    if not dv or birth_branch is None:
        return []
    start_age = int(dv["tuoi_bat_dau"])
    start_year = int(chart.get("input", {}).get("nam")) + start_age - 1
    gender = str(chart.get("input", {}).get("gioi_tinh", "Nam"))
    rows: list[dict[str, Any]] = []
    for idx in range(10):
        age = start_age + idx
        target_year = start_year + idx
        _can, target_branch = _legacy.can_chi_year(target_year)
        mapping = _legacy._tieu_van_source_mapping(birth_branch, target_branch, gender)
        cung_so = mapping.get("cung_so")
        palace = _palace_by_number(chart, cung_so)
        rows.append({
            "nam": target_year,
            "tuoi": age,
            "nam_thu": idx + 1,
            "chi_nam": target_branch,
            "chi_ten": _legacy.chi_name(target_branch),
            "cung_so": cung_so,
            "cung": palace.get("cung") if palace else None,
            "dia_chi": palace.get("dia_chi") if palace else None,
            "can_chi": palace.get("can_chi") if palace else None,
            "cung_khoi": mapping.get("cung_khoi"),
            "huong": mapping.get("huong"),
            "la_nam_dang_xem": target_year == (van.get("year") or {}).get("nam"),
            "cach_tinh": "Cung khởi làm mốc Tý, dịch theo Chi năm xem theo quy tắc Tiểu vận của engine.",
        })
    return rows


def calculate_van_layers(
    chart: dict[str, Any],
    *,
    year: int | None = None,
    month: int | None = None,
    day: int | None = None,
    hour: int | None = None,
    time_zone: float | None = None,
) -> dict[str, Any]:
    van = _legacy.calculate_van_layers(
        chart, year=year, month=month, day=day, hour=hour, time_zone=time_zone
    )

    direction = _direction_from_dv(van)
    dv10 = _build_luu_nien_dai_van_10_nam(chart, van)
    tv10 = _build_tieu_van_10_nam(chart, van)

    van["luu_nien_dai_van_10_nam"] = dv10
    van["tieu_van_10_nam"] = tv10
    van["van_10_nam"] = {
        "dai_van_cung_so": (van.get("dai_van") or {}).get("dang_xet", {}).get("cung_so"),
        "dai_van_tuoi_bat_dau": (van.get("dai_van") or {}).get("dang_xet", {}).get("tuoi_bat_dau"),
        "dai_van_tuoi_ket_thuc": (van.get("dai_van") or {}).get("dang_xet", {}).get("tuoi_ket_thuc"),
        "huong_vong_van": "thuận" if direction == 1 else "nghịch",
        "luu_nien_dai_van": dv10,
        "tieu_van": tv10,
        "source_of_truth": "tuvi_engine.van_calculator authoritative 10-year layer",
    }

    # Đồng bộ vị trí năm đang xem với bảng 10 năm authoritative.
    current_year = (van.get("year") or {}).get("nam")
    current_dv = next((r for r in dv10 if r["nam"] == current_year), None)
    current_tv = next((r for r in tv10 if r["nam"] == current_year), None)
    if current_dv:
        van.setdefault("luu_nien", {})["cung_luu_nien_trong_dai_van_authoritative"] = current_dv["cung_so"]
        van.setdefault("luu_nien", {})["luu_nien_dai_van_10_nam"] = dv10
    if current_tv:
        van.setdefault("tieu_van", {})["cung_so_authoritative"] = current_tv["cung_so"]
        van.setdefault("tieu_van", {})["tieu_van_10_nam"] = tv10

    van["rules_audit"] = {
        **(van.get("rules_audit") or {}),
        "luu_nien_dai_van_10_nam": (
            "Lấy cung Đại vận thực tế của từng lá số; năm 1 = Đại vận; năm 2 = xung chiếu; "
            "năm 3 dịch 1 cung theo chiều đối ứng; năm 4-10 tiếp tục theo cùng chiều."
        ),
        "tieu_van_10_nam": "Tính độc lập cho từng năm trong toàn bộ 10 năm của Đại vận, không chỉ năm đang chọn.",
    }
    return van
