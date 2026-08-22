# -*- coding: utf-8 -*-
"""Chuẩn hóa dữ liệu sao của engine trước khi hiển thị hoặc gửi AI.

Mục tiêu: một sao chỉ xuất hiện một lần trong đúng nhóm; chính tinh không
bao giờ rơi vào cột phụ tinh, kể cả với JSON/chart cũ.
"""
from __future__ import annotations

import re
import unicodedata
from typing import Any

MAIN_STAR_IDS = frozenset(range(1, 15))
TRANG_SINH_IDS = frozenset(range(39, 51))
TRANSFORMATION_IDS = frozenset(range(92, 96))

BRANCHES = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]


def _key(star: dict[str, Any]) -> tuple[str, Any]:
    sid = star.get("id")
    if sid is not None:
        return ("id", sid)
    return ("name", str(star.get("ten", "")).strip().casefold())


def dedupe_stars(stars: Any) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    seen: set[tuple[str, Any]] = set()
    for star in stars or []:
        if not isinstance(star, dict) or not star.get("ten"):
            continue
        item = dict(star)
        key = _key(item)
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def split_engine_stars(stars: Any) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Trả về (chính tinh, phụ tinh, vòng Tràng Sinh) theo ID chuẩn."""
    main: list[dict[str, Any]] = []
    support: list[dict[str, Any]] = []
    trang_sinh: list[dict[str, Any]] = []
    for star in dedupe_stars(stars):
        sid = star.get("id")
        if sid in MAIN_STAR_IDS or star.get("loai") == 1:
            main.append(star)
        elif sid in TRANG_SINH_IDS or star.get("vong_trang_sinh"):
            trang_sinh.append(star)
        else:
            support.append(star)
    return main, support, trang_sinh


def _canonical_branch(value: Any, cung_so: Any = None) -> str | None:
    """Chuẩn hóa địa chi; cung_so 1..12 là fallback authoritative của engine."""
    if value is not None:
        raw = str(value).strip()
        if raw:
            direct = {
                "Tý": "Tý", "Ty": "Tý", "ty": "Tý", "ty1": "Tý",
                "Sửu": "Sửu", "Suu": "Sửu", "suu": "Sửu",
                "Dần": "Dần", "Dan": "Dần", "dan": "Dần",
                "Mão": "Mão", "Mao": "Mão", "mao": "Mão",
                "Thìn": "Thìn", "Thin": "Thìn", "thin": "Thìn",
                "Tỵ": "Tỵ", "Tị": "Tỵ", "Ty2": "Tỵ", "ty2": "Tỵ", "ti": "Tỵ",
                "Ngọ": "Ngọ", "Ngo": "Ngọ", "ngo": "Ngọ",
                "Mùi": "Mùi", "Mui": "Mùi", "mui": "Mùi",
                "Thân": "Thân", "Than": "Thân", "than": "Thân",
                "Dậu": "Dậu", "Dau": "Dậu", "dau": "Dậu",
                "Tuất": "Tuất", "Tuat": "Tuất", "tuat": "Tuất",
                "Hợi": "Hợi", "Hoi": "Hợi", "hoi": "Hợi",
            }
            if raw in direct:
                return direct[raw]
            folded = unicodedata.normalize("NFD", raw.casefold())
            folded = "".join(c for c in folded if unicodedata.category(c) != "Mn")
            folded = re.sub(r"\d+$", "", folded)
            aliases = {
                "ty": "Tý", "suu": "Sửu", "dan": "Dần", "mao": "Mão",
                "thin": "Thìn", "ti": "Tỵ", "ty": "Tý", "ngo": "Ngọ",
                "mui": "Mùi", "than": "Thân", "dau": "Dậu", "tuat": "Tuất", "hoi": "Hợi",
            }
            if folded in aliases:
                return aliases[folded]
    try:
        idx = int(cung_so)
        if 1 <= idx <= 12:
            return BRANCHES[idx - 1]
    except (TypeError, ValueError):
        pass
    return None


def normalize_engine_chart(chart: Any, *, for_ai: bool = False) -> dict[str, Any]:
    """Làm sạch chart engine mà không thay đổi vị trí sao.

    ``branch`` là trường địa chi canonical dành cho frontend; nếu ``dia_chi``
    lỗi/mơ hồ thì dùng ``cung_so`` 1..12 của engine làm nguồn dự phòng.
    """
    if not isinstance(chart, dict):
        return {}
    out = dict(chart)
    cungs = chart.get("12_cung", {})
    normalized: dict[str, Any] = {}
    values = cungs.values() if isinstance(cungs, dict) else cungs
    for name, raw in (cungs.items() if isinstance(cungs, dict) else enumerate(values, 1)):
        if not isinstance(raw, dict):
            continue
        item = dict(raw)
        all_stars = raw.get("sao", [])
        if not all_stars:
            all_stars = list(raw.get("chinh_tinh", [])) + list(raw.get("phu_tinh", [])) + list(raw.get("vong_trang_sinh_data", []))
        main, support, trang_sinh = split_engine_stars(all_stars)
        item["chinh_tinh"] = main
        item["phu_tinh"] = support
        item["vong_trang_sinh_data"] = trang_sinh
        item["tuan_triet"] = ", ".join(x for x, ok in (("Tuần", raw.get("tuan")), ("Triệt", raw.get("triet"))) if ok) or None
        item["branch"] = _canonical_branch(raw.get("dia_chi") or raw.get("chi") or raw.get("branch"), raw.get("cung_so"))
        if for_ai:
            item.pop("sao", None)
            item.pop("tuan", None)
            item.pop("triet", None)
            item.pop("vong_trang_sinh_data", None)
        key = str(name)
        normalized[key] = item
    out["12_cung"] = normalized
    return out
