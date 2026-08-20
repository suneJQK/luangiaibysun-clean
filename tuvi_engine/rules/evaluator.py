"""Relationship-aware evaluator for declarative Tử Vi Cách Cục rules.

The rule data describes *what* must be true; this evaluator determines *where*
the required stars are located using the actual 12-palace geometry.

Reference architecture: TuViMCP/tuvi_mcp/_rules.py.
"""
from __future__ import annotations

from typing import Any, Iterable

BRANCH_LUC_HOP = {
    "Tý": "Sửu", "Sửu": "Tý", "Dần": "Hợi", "Hợi": "Dần",
    "Mão": "Tuất", "Tuất": "Mão", "Thìn": "Dậu", "Dậu": "Thìn",
    "Tỵ": "Thân", "Thân": "Tỵ", "Ngọ": "Mùi", "Mùi": "Ngọ",
}

RELATION_KEYS = (
    "dong_cung",
    "tam_phuong_tu_chinh",
    "tam_hop",
    "xung_chieu",
    "nhi_hop",
    "giap_cung",
)


def _palaces(chart: dict[str, Any]) -> list[dict[str, Any]]:
    raw = chart.get("12_cung") or chart.get("dia_ban") or {}
    if isinstance(raw, dict):
        items = list(raw.values())
    elif isinstance(raw, list):
        items = raw
    else:
        items = []
    return [p for p in items if isinstance(p, dict)]


def _normalize_names(names: Iterable[str]) -> set[str]:
    return {str(name).strip().casefold() for name in names if str(name).strip()}


def _star_records(palace: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for key in ("sao", "chinh_tinh", "phu_tinh"):
        value = palace.get(key)
        if isinstance(value, list):
            records.extend(star for star in value if isinstance(star, dict))
    return records


def _star_names(palace: dict[str, Any]) -> set[str]:
    names: set[str] = set()
    for star in _star_records(palace):
        value = star.get("ten") or star.get("name") or star.get("saoTen")
        if value:
            names.add(str(value).strip().casefold())
    return names


def _star_attribute_matches(star: dict[str, Any], attr: str) -> bool:
    requested = str(attr).strip().casefold()
    actual = star.get("attribute") or star.get("dac_tinh") or star.get("saoDacTinh") or ""
    return requested in str(actual).casefold()


def _cung_so(palace: dict[str, Any]) -> int | None:
    try:
        value = int(palace.get("cung_so"))
    except (TypeError, ValueError):
        return None
    return value if 1 <= value <= 12 else None


def _cung_name(palace: dict[str, Any]) -> str:
    return str(palace.get("cung") or palace.get("cung_ten") or "").strip()


def _cung_chi(palace: dict[str, Any]) -> str:
    value = palace.get("dia_chi") or palace.get("chi")
    if value:
        return str(value).strip()
    parts = _cung_name(palace).split()
    return parts[-1] if parts else ""


def get_cung_by_chu(chart: dict[str, Any], name: str) -> dict[str, Any] | None:
    target = str(name).strip().casefold()
    for palace in _palaces(chart):
        if _cung_name(palace).casefold() == target:
            return palace
        if str(palace.get("cung_chu") or "").strip().casefold() == target:
            return palace
    return None


def get_cung_by_so(chart: dict[str, Any], cung_so: int) -> dict[str, Any] | None:
    wanted = ((int(cung_so) - 1) % 12) + 1
    return next((p for p in _palaces(chart) if _cung_so(p) == wanted), None)


def get_cung_by_chi(chart: dict[str, Any], chi: str) -> dict[str, Any] | None:
    target = str(chi).strip().casefold()
    return next((p for p in _palaces(chart) if _cung_chi(p).casefold() == target), None)


def _offset_palace(chart: dict[str, Any], target: dict[str, Any], offset: int) -> list[dict[str, Any]]:
    base = _cung_so(target)
    if base is None:
        return []
    wanted = ((base - 1 + offset) % 12) + 1
    return [p for p in _palaces(chart) if _cung_so(p) == wanted]


def related_palaces(chart: dict[str, Any], target: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """Return actual palace objects in each positional relationship."""
    dong = [target]
    tam_hop = _offset_palace(chart, target, 4) + _offset_palace(chart, target, 8)
    xung = _offset_palace(chart, target, 6)
    giap = _offset_palace(chart, target, -1) + _offset_palace(chart, target, 1)
    tam_phuong = dong + tam_hop + xung
    luc_hop = []
    partner = BRANCH_LUC_HOP.get(_cung_chi(target))
    if partner:
        found = get_cung_by_chi(chart, partner)
        if found is not None:
            luc_hop = [found]
    return {
        "dong_cung": dong,
        "tam_hop": tam_hop,
        "xung_chieu": xung,
        "nhi_hop": luc_hop,
        "giap_cung": giap,
        "tam_phuong_tu_chinh": tam_phuong,
    }


def get_tam_phuong_tu_chinh(chart: dict[str, Any], cung_so: int) -> list[dict[str, Any]]:
    target = get_cung_by_so(chart, cung_so)
    return related_palaces(chart, target)["tam_phuong_tu_chinh"] if target else []


def get_giap_cung(chart: dict[str, Any], cung_so: int) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    target = get_cung_by_so(chart, cung_so)
    if target is None:
        return None, None
    rel = related_palaces(chart, target)["giap_cung"]
    return (rel[0] if len(rel) > 0 else None, rel[1] if len(rel) > 1 else None)


def get_luc_hop_cung(chart: dict[str, Any], cung_so: int) -> dict[str, Any] | None:
    target = get_cung_by_so(chart, cung_so)
    if target is None:
        return None
    rel = related_palaces(chart, target)["nhi_hop"]
    return rel[0] if rel else None


def has_star(palace: dict[str, Any] | None, star_name: str, star_attr: str | None = None) -> bool:
    if palace is None:
        return False
    target = str(star_name).strip().casefold()
    for star in _star_records(palace):
        value = star.get("ten") or star.get("name") or star.get("saoTen")
        if str(value or "").strip().casefold() != target:
            continue
        if star_attr is None or _star_attribute_matches(star, star_attr):
            return True
    return False


def count_stars_in_houses(houses: list[dict[str, Any]], star_names: list[str]) -> int:
    return sum(1 for name in star_names if any(has_star(house, name) for house in houses))


def _scope_star_names(houses: list[dict[str, Any]]) -> set[str]:
    result: set[str] = set()
    for house in houses:
        result |= _star_names(house)
    return result


def _scope_matches(scope: list[dict[str, Any]], condition: dict[str, Any]) -> bool:
    stars = _scope_star_names(scope)
    if "stars_all" in condition and not _normalize_names(condition["stars_all"]).issubset(stars):
        return False
    if "stars_any" in condition and not (_normalize_names(condition["stars_any"]) & stars):
        return False
    if "stars_none" in condition and (_normalize_names(condition["stars_none"]) & stars):
        return False
    if "not_both" in condition and _normalize_names(condition["not_both"]).issubset(stars):
        return False
    if "stars_required" in condition:
        required = _normalize_names(condition["stars_required"])
        min_count = int(condition.get("min_count", len(required)))
        if len(required & stars) < min_count:
            return False
    return True


def _match_house_condition(palace: dict[str, Any] | None, condition: dict[str, Any]) -> bool:
    if palace is None:
        return False
    if "branches_in" in condition and _cung_chi(palace) not in set(condition["branches_in"]):
        return False
    if "stars_all" in condition and not all(has_star(palace, s) for s in condition["stars_all"]):
        return False
    if "stars_any" in condition and not any(has_star(palace, s) for s in condition["stars_any"]):
        return False
    if "stars_none" in condition and any(has_star(palace, s) for s in condition["stars_none"]):
        return False
    if "not_both" in condition and all(has_star(palace, s) for s in condition["not_both"]):
        return False
    return True


def evaluate_condition(chart: dict[str, Any], condition: dict[str, Any]) -> bool:
    """Evaluate one declarative condition against real palace geometry."""
    if not isinstance(condition, dict):
        return False
    if "any_of" in condition:
        branches = [x for x in condition["any_of"] if isinstance(x, dict)]
        return any(evaluate_condition(chart, x) for x in branches)
    if "all_of" in condition:
        branches = [x for x in condition["all_of"] if isinstance(x, dict)]
        return bool(branches) and all(evaluate_condition(chart, x) for x in branches)
    if "cung_menh" in condition:
        return evaluate_condition(chart, {"target": "Mệnh", **condition["cung_menh"]})

    target = get_cung_by_chu(chart, str(condition.get("target", "Mệnh")))
    if target is None:
        return False
    relations = related_palaces(chart, target)
    relation_present = False

    for relation_name in RELATION_KEYS:
        rule = condition.get(relation_name)
        if rule is None:
            continue
        relation_present = True
        scope = relations[relation_name]
        if not scope:
            return False
        if rule is True:
            continue
        if not isinstance(rule, dict) or not _scope_matches(scope, rule):
            return False

    if "giap_cung_pairs" in condition:
        relation_present = True
        pair_houses = relations["giap_cung"]
        if len(pair_houses) != 2:
            return False
        matched = False
        for pair in condition["giap_cung_pairs"] if isinstance(condition["giap_cung_pairs"], list) else []:
            if not isinstance(pair, (list, tuple)) or len(pair) != 2:
                continue
            a, b = pair
            if (has_star(pair_houses[0], a) and has_star(pair_houses[1], b)) or (has_star(pair_houses[0], b) and has_star(pair_houses[1], a)):
                matched = True
                break
        if not matched:
            return False

    for key, house_name in (("cung_quan", "Quan Lộc"), ("cung_tai", "Tài Bạch"), ("cung_dien", "Điền Trạch")):
        if key in condition:
            relation_present = True
            if not _match_house_condition(get_cung_by_chu(chart, house_name), condition[key]):
                return False

    for key, chi in (("cung_ty", "Tỵ"), ("cung_dau", "Dậu")):
        if key in condition:
            relation_present = True
            if not _match_house_condition(get_cung_by_chi(chart, chi), condition[key]):
                return False

    if "luc_hop" in condition:
        relation_present = True
        partner = relations["nhi_hop"]
        if not partner or not _match_house_condition(partner[0], condition["luc_hop"]):
            return False

    target_filters = {k: condition[k] for k in ("branches_in", "stars_all", "stars_any", "stars_none", "not_both") if k in condition}
    if target_filters and not _match_house_condition(target, target_filters):
        return False

    if "stem_contains" in condition:
        relation_present = True
        can_nam = str((chart.get("thien_ban") or {}).get("can_nam") or "")
        if str(condition["stem_contains"]) not in can_nam:
            return False

    return relation_present or bool(target_filters)
