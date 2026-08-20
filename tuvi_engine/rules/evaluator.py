"""Generic condition evaluator for Cách Cục JSON rules."""
from __future__ import annotations

from typing import Any


def _star_names(palace: dict[str, Any]) -> set[str]:
    stars = palace.get("sao") or palace.get("chinh_tinh", []) + palace.get("phu_tinh", [])
    return {str(x.get("ten", "")).strip().casefold() for x in stars if isinstance(x, dict)}


def has_all(palace: dict[str, Any], names: list[str]) -> bool:
    stars = _star_names(palace)
    return all(str(name).strip().casefold() in stars for name in names)


def has_any(palace: dict[str, Any], names: list[str]) -> bool:
    stars = _star_names(palace)
    return any(str(name).strip().casefold() in stars for name in names)


def evaluate_condition(chart: dict[str, Any], condition: dict[str, Any]) -> bool:
    cung_menh = chart.get("12_cung", {}).get("Mệnh", {})
    if not isinstance(cung_menh, dict):
        return False
    if "any_of" in condition:
        return any(evaluate_condition(chart, item) for item in condition["any_of"] if isinstance(item, dict))
    if "cung_menh" in condition:
        return evaluate_condition(chart, {"target": "Mệnh", **condition["cung_menh"]})
    target_name = condition.get("target", "Mệnh")
    palace = chart.get("12_cung", {}).get(target_name, cung_menh)
    if not isinstance(palace, dict):
        return False
    if "stars_all" in condition and not has_all(palace, condition["stars_all"]):
        return False
    if "stars_any" in condition and not has_any(palace, condition["stars_any"]):
        return False
    if "stars_none" in condition and has_any(palace, condition["stars_none"]):
        return False
    if "branches_in" in condition and palace.get("dia_chi") not in set(condition["branches_in"]):
        return False
    if "tam_phuong_tu_chinh" in condition:
        return True
    return True
