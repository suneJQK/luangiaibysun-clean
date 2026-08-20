"""Stable serialization helpers for low-level Tu Vi engine objects."""
from __future__ import annotations
from typing import Any, Iterable

MAIN_STAR_IDS = frozenset(range(1, 15))
TRANG_SINH_IDS = frozenset(range(39, 51))


def serialize_star(star: Any) -> dict[str, Any]:
    """Convert a low-level ``Sao`` object or star dict into stable JSON data."""
    if isinstance(star, dict):
        get = star.get
    else:
        get = lambda key, default=None: getattr(star, key, default)
    return {
        "id": get("saoID", get("id")),
        "ten": get("saoTen", get("ten")),
        "ngu_hanh": get("saoNguHanh", get("ngu_hanh")),
        "loai": get("saoLoai", get("loai")),
        "phuong_vi": get("saoPhuongVi", get("phuong_vi")),
        "am_duong": get("saoAmDuong", get("am_duong")),
        "dac_tinh": get("saoDacTinh", get("dac_tinh")),
        "vong_trang_sinh": bool(get("vongTrangSinh", get("vong_trang_sinh", False))),
    }


def dedupe_stars(stars: Iterable[Any]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    seen: set[tuple[str, Any]] = set()
    for raw in stars:
        star = serialize_star(raw)
        name = star.get("ten")
        if not name:
            continue
        key = ("id", star["id"]) if star.get("id") is not None else ("name", str(name).casefold())
        if key in seen:
            continue
        seen.add(key)
        result.append(star)
    return result


def serialize_palace(cung: Any) -> dict[str, Any]:
    stars = dedupe_stars(getattr(cung, "cungSao", []))
    main = [s for s in stars if s.get("id") in MAIN_STAR_IDS or s.get("loai") == 1]
    trang_sinh = [
        s for s in stars
        if s.get("id") in TRANG_SINH_IDS or s.get("vong_trang_sinh")
    ]
    main_ids = {s.get("id") for s in main}
    trang_ids = {s.get("id") for s in trang_sinh}
    support = [
        s for s in stars
        if s.get("id") not in main_ids
        and s.get("id") not in trang_ids
        and s.get("loai") != 1
    ]
    return {
        "cung": getattr(cung, "cungChu", ""),
        "can_chi": getattr(cung, "cungTen", "").strip(),
        "dia_chi": getattr(cung, "cungDiaChi", ""),
        "ngu_hanh": getattr(cung, "cungHanh", getattr(cung, "hanhCung", "")),
        "am_duong": "Dương" if getattr(cung, "cungAmDuong", 0) == 1 else "Âm",
        "than_cu": bool(getattr(cung, "cungThan", False)),
        "tuan": bool(getattr(cung, "tuanTrung", False)),
        "triet": bool(getattr(cung, "trietLo", False)),
        "dai_van": {"tuoi_bat_dau": getattr(cung, "cungDaiHan", None)},
        "tieu_van": {"chi": getattr(cung, "cungTieuHan", None)},
        "chinh_tinh": main,
        "phu_tinh": support,
        "vong_trang_sinh": next((s["ten"] for s in trang_sinh), None),
        "sao": stars,
    }
