# -*- coding: utf-8 -*-
"""Chuẩn hóa dữ liệu sao của engine trước khi hiển thị hoặc gửi AI."""
from __future__ import annotations

import re
import unicodedata
from typing import Any

MAIN_STAR_IDS = frozenset(range(1, 15))
TRANG_SINH_IDS = frozenset(range(39, 51))
TRANSFORMATION_IDS = frozenset(range(92, 96))
BRANCHES = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]


def _normalize_star(raw: Any) -> dict[str, Any] | None:
    if not isinstance(raw, dict):
        return None
    item = dict(raw)
    if not item.get("ten"):
        item["ten"] = item.get("name") or item.get("saoTen") or item.get("sao")
    if item.get("id") is None:
        item["id"] = item.get("saoID")
    if item.get("loai") is None:
        item["loai"] = item.get("saoLoai")
    if item.get("vong_trang_sinh") is None:
        item["vong_trang_sinh"] = bool(item.get("vongTrangSinh"))
    if not item.get("ten"):
        return None
    return item


def _key(star: dict[str, Any]) -> tuple[str, Any]:
    sid = star.get("id")
    if sid is not None:
        return ("id", str(sid))
    return ("name", str(star.get("ten", "")).strip().casefold())


def dedupe_stars(stars: Any) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    seen: set[tuple[str, Any]] = set()
    for raw in stars or []:
        star = _normalize_star(raw)
        if not star:
            continue
        key = _key(star)
        if key in seen:
            continue
        seen.add(key)
        out.append(star)
    return out


def split_engine_stars(stars: Any) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Trả về (chính tinh, phụ tinh, vòng Tràng Sinh)."""
    main: list[dict[str, Any]] = []
    support: list[dict[str, Any]] = []
    trang_sinh: list[dict[str, Any]] = []
    for star in dedupe_stars(stars):
        sid = star.get("id")
        try:
            sid_int = int(sid) if sid is not None else None
        except (TypeError, ValueError):
            sid_int = None
        loai = star.get("loai")
        try:
            loai_int = int(loai) if loai is not None else None
        except (TypeError, ValueError):
            loai_int = None
        if sid_int in MAIN_STAR_IDS or loai_int == 1:
            main.append(star)
        elif sid_int in TRANG_SINH_IDS or bool(star.get("vong_trang_sinh")):
            trang_sinh.append(star)
        else:
            support.append(star)
    return main, support, trang_sinh


def _canonical_branch(value: Any, cung_so: Any = None) -> str | None:
    if value is not None:
        raw = str(value).strip()
        direct = {
            "Tý": "Tý", "Ty": "Tý", "ty": "Tý", "ty1": "Tý",
            "Sửu": "Sửu", "Suu": "Sửu", "suu": "Sửu",
            "Dần": "Dần", "Dan": "Dần", "dan": "Dần",
            "Mão": "Mão", "Mao": "Mão", "mao": "Mão",
            "Thìn": "Thìn", "Thin": "Thìn", "thin": "Thìn",
            "Tỵ": "Tỵ", "Tị": "Tỵ", "ti": "Tỵ", "ty2": "Tỵ",
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
        aliases = {"ty": "Tý", "suu": "Sửu", "dan": "Dần", "mao": "Mão", "thin": "Thìn", "ti": "Tỵ", "ngo": "Ngọ", "mui": "Mùi", "than": "Thân", "dau": "Dậu", "tuat": "Tuất", "hoi": "Hợi"}
        if folded in aliases:
            return aliases[folded]
    try:
        idx = int(cung_so)
        if 1 <= idx <= 12:
            return BRANCHES[idx - 1]
    except (TypeError, ValueError):
        pass
    return None


def _list_alias(raw: dict[str, Any], *keys: str) -> list[Any]:
    for key in keys:
        value = raw.get(key)
        if isinstance(value, list) and value:
            return value
    return []


def normalize_engine_chart(chart: Any, *, for_ai: bool = False) -> dict[str, Any]:
    """Chuẩn hóa chart mà không làm mất chính tinh/phụ tinh từ engine."""
    if not isinstance(chart, dict):
        return {}
    out = dict(chart)
    cungs = chart.get("12_cung", {})
    normalized: dict[str, Any] = {}
    iterable = cungs.items() if isinstance(cungs, dict) else enumerate(cungs, 1)
    for name, raw in iterable:
        if not isinstance(raw, dict):
            continue
        item = dict(raw)
        explicit_main = _list_alias(raw, "chinh_tinh", "chinhTinh", "chinhTinhData")
        explicit_support = _list_alias(raw, "phu_tinh", "phuTinh", "phuTinhData")
        explicit_trang = _list_alias(raw, "vong_trang_sinh_data", "vongTrangSinhData")
        raw_all = _list_alias(raw, "sao", "stars", "all_stars")

        if explicit_main or explicit_support or explicit_trang:
            main = dedupe_stars(explicit_main)
            support = dedupe_stars(explicit_support)
            trang_sinh = dedupe_stars(explicit_trang)
            if raw_all:
                raw_main, raw_support, raw_trang = split_engine_stars(raw_all)
                if not main:
                    main = raw_main
                if not support:
                    support = raw_support
                if not trang_sinh:
                    trang_sinh = raw_trang
        else:
            main, support, trang_sinh = split_engine_stars(raw_all)

        item["chinh_tinh"] = main
        item["phu_tinh"] = support
        item["vong_trang_sinh_data"] = trang_sinh
        item["tuan_triet"] = ", ".join(x for x, ok in (("Tuần", raw.get("tuan")), ("Triệt", raw.get("triet"))) if ok) or None
        item["branch"] = _canonical_branch(raw.get("dia_chi") or raw.get("chi") or raw.get("branch"), raw.get("cung_so"))
        if for_ai:
            item.pop("sao", None)
            item.pop("stars", None)
            item.pop("tuan", None)
            item.pop("triet", None)
            item.pop("vong_trang_sinh_data", None)
        normalized[str(name)] = item
    out["12_cung"] = normalized
    return out
