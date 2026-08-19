# -*- coding: utf-8 -*-
"""Chuẩn hóa dữ liệu sao của engine trước khi hiển thị hoặc gửi AI.

Mục tiêu: một sao chỉ xuất hiện một lần trong đúng nhóm; chính tinh không
bao giờ rơi vào cột phụ tinh, kể cả với JSON/chart cũ.
"""
from __future__ import annotations
from typing import Any

MAIN_STAR_IDS = frozenset(range(1, 15))
TRANG_SINH_IDS = frozenset(range(39, 51))
TRANSFORMATION_IDS = frozenset(range(92, 96))


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


def normalize_engine_chart(chart: Any, *, for_ai: bool = False) -> dict[str, Any]:
    """Làm sạch chart engine mà không thay đổi vị trí sao.

    `for_ai=True` loại trường raw `sao` và boolean Tuần/Triệt để AI chỉ nhận
    cấu trúc đã chuẩn hóa, tránh lặp chính tinh và tránh trả dữ liệu engine thô.
    """
    if not isinstance(chart, dict):
        return {}
    out = dict(chart)
    cungs = chart.get("12_cung", {})
    normalized: dict[str, Any] = {}
    for name, raw in cungs.items():
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
        if for_ai:
            item.pop("sao", None)
            item.pop("tuan", None)
            item.pop("triet", None)
            item.pop("vong_trang_sinh_data", None)
        normalized[name] = item
    out["12_cung"] = normalized
    return out
