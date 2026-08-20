"""Relationship-aware evaluator for Cách Cục JSON rules.

Rules are evaluated against the actual 12-palace geometry. A condition such as
``tam_phuong_tu_chinh`` means the required stars must be present within the
target palace + its two tam-hợp palaces + its xung-chiếu palace; they are not
assumed to be đồng cung.
"""
from __future__ import annotations

from typing import Any, Iterable


def _palaces(chart: dict[str, Any]) -> list[dict[str, Any]]:
    raw = chart.get("12_cung") or chart.get("dia_ban") or {}
    if isinstance(raw, dict):
        items = list(raw.values())
    elif isinstance(raw, list):
        items = raw
    else:
        items = []
    return [p for p in items if isinstance(p, dict)]


def _star_names(palace: dict[str, Any]) -> set[str]:
    stars: list[Any] = []
    if isinstance(palace.get("sao"), list):
        stars.extend(palace["sao"])
    if isinstance(palace.get("chinh_tinh"), list):
        stars.extend(palace["chinh_tinh"])
    if isinstance(palace.get("phu_tinh"), list):
        stars.extend(palace["phu_tinh"])
    names: set[str] = set()
    for star in stars:
        if isinstance(star, dict):
            value = star.get("ten") or star.get("name") or star.get("saoTen")
            if value:
                names.add(str(value).strip().casefold())
        elif isinstance(star, str):
            names.add(star.strip().casefold())
    return names


def _normalize_names(names: Iterable[str]) -> set[str]:
    return {str(name).strip().casefold() for name in names if str(name).strip()}


def _cung_so(palace: dict[str, Any]) -> int | None:
    value = palace.get("cung_so")
    if isinstance(value, int) and 1 <= value <= 12:
        return value
    try:
        value = int(value)
    except (TypeError, ValueError):
        return None
    return value if 1 <= value <= 12 else None


def _target_palace(chart: dict[str, Any], target: str = "Mệnh") -> dict[str, Any] | None:
    for palace in _palaces(chart):
        if palace.get("cung") == target or palace.get("cung_ten") == target:
            return palace
    raw = chart.get("12_cung") or {}
    if isinstance(raw, dict) and isinstance(raw.get(target), dict):
        return raw[target]
    return None


def _same_cung(chart: dict[str, Any], target: dict[str, Any], offset: int) -> list[dict[str, Any]]:
    target_no = _cung_so(target)
    if target_no is None:
        return []
    wanted = ((target_no - 1 + offset) % 12) + 1
    return [p for p in _palaces(chart) if _cung_so(p) == wanted]


def related_palaces(chart: dict[str, Any], target: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """Return actual palace objects in each positional relationship."""
    result: dict[str, list[dict[str, Any]]] = {
        "dong_cung": [target],
        "tam_hop": _same_cung(chart, target, 4) + _same_cung(chart, target, 8),
        "xung_chieu": _same_cung(chart, target, 6),
        "nhi_hop": [],
        "giap_cung": _same_cung(chart, target, -1) + _same_cung(chart, target, 1),
        "tam_phuong_tu_chinh": [target]
        + _same_cung(chart, target, 4)
        + _same_cung(chart, target, 8)
        + _same_cung(chart, target, 6),
    }

    branch = target.get("dia_chi") or target.get("chi")
    if branch:
        luc_hop = {
            "Tý": "Sửu", "Sửu": "Tý", "Dần": "Hợi", "Hợi": "Dần",
            "Mão": "Tuất", "Tuất": "Mão", "Thìn": "Dậu", "Dậu": "Thìn",
            "Tỵ": "Thân", "Thân": "Tỵ", "Ngọ": "Mùi", "Mùi": "Ngọ",
        }.get(str(branch))
        if luc_hop:
            result["nhi_hop"] = [p for p in _palaces(chart) if (p.get("dia_chi") or p.get("chi")) == luc_hop]
    return result


def has_all(palace: dict[str, Any], names: list[str]) -> bool:
    return _normalize_names(names).issubset(_star_names(palace))


def has_any(palace: dict[str, Any], names: list[str]) -> bool:
    return bool(_normalize_names(names) & _star_names(palace))


def _scope_stars(palaces: list[dict[str, Any]]) -> set[str]:
    result: set[str] = set()
    for palace in palaces:
        result |= _star_names(palace)
    return result


def _evaluate_scope(scope: list[dict[str, Any]], condition: dict[str, Any]) -> bool:
    stars = _scope_stars(scope)
    if "stars_all" in condition and not _normalize_names(condition["stars_all"]).issubset(stars):
        return False
    if "stars_any" in condition and not (_normalize_names(condition["stars_any"]) & stars):
        return False
    if "stars_none" in condition and (_normalize_names(condition["stars_none"]) & stars):
        return False
    if "stars_required" in condition:
        required = _normalize_names(condition["stars_required"])
        min_count = int(condition.get("min_count", len(required)))
        if len(required & stars) < min_count:
            return False
    return True


def evaluate_condition(chart: dict[str, Any], condition: dict[str, Any]) -> bool:
    """Evaluate a Cách Cục condition using explicit palace geometry."""
    if not isinstance(condition, dict):
        return False

    if "any_of" in condition:
        return any(
            evaluate_condition(chart, item)
            for item in condition["any_of"]
            if isinstance(item, dict)
        )
    if "all_of" in condition:
        return all(
            evaluate_condition(chart, item)
            for item in condition["all_of"]
            if isinstance(item, dict)
        )

    target_name = str(condition.get("target", "Mệnh"))
    target = _target_palace(chart, target_name)
    if target is None:
        return False

    # Conditions explicitly attached to the target palace.
    if "cung_menh" in condition:
        return evaluate_condition(chart, {"target": "Mệnh", **condition["cung_menh"]})

    relationships = related_palaces(chart, target)

    # Default scope is đồng cung: stars must actually be in the target palace.
    scope = [target]
    for relationship in (
        "dong_cung",
        "tam_phuong_tu_chinh",
        "tam_hop",
        "xung_chieu",
        "nhi_hop",
        "giap_cung",
    ):
        if relationship in condition:
            relation_rule = condition[relationship]
            if isinstance(relation_rule, dict):
                scope = relationships[relationship]
                if not scope:
                    return False
                if not _evaluate_scope(scope, relation_rule):
                    return False
            elif relation_rule is True:
                scope = relationships[relationship]

    # Direct target filters remain restricted to the target palace.
    if "stars_all" in condition and not has_all(target, condition["stars_all"]):
        # If a broader relationship scope was explicitly selected, allow those
        # requirements to be satisfied there instead of forcing đồng cung.
        if not any(key in condition for key in ("dong_cung", "tam_phuong_tu_chinh", "tam_hop", "xung_chieu", "nhi_hop", "giap_cung")):
            return False
    if "stars_any" in condition and not has_any(target, condition["stars_any"]):
        if not any(key in condition for key in ("dong_cung", "tam_phuong_tu_chinh", "tam_hop", "xung_chieu", "nhi_hop", "giap_cung")):
            return False
    if "stars_none" in condition and has_any(target, condition["stars_none"]):
        return False
    if "branches_in" in condition:
        branch = target.get("dia_chi") or target.get("chi")
        if branch not in set(condition["branches_in"]):
            return False

    return True
