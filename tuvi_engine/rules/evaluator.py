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
        if not isinstance(value, list):
            continue
        for star in value:
            if isinstance(star, dict):
                records.append(star)
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
    value = palace.get("cung_so")
    try:
        value = int(value)
    except (TypeError, ValueError):
        return None
    return value if 1 <= value <= 12 else None


def _cung_name(palace: dict[str, Any]) -> str:
    return str(palace.get("cung") or palace.get("cung_ten") or "").strip()


def _cung_chi(palace: dict[str, Any]) -> str:
    value = palace.get("dia_chi") or palace.get("chi")
    if value:
        return str(value).strip()
    text = _cung_name(palace)
    parts = text.split()
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
    return [p for p in _palaces(chart) if _cung_so(p) == ((base - 1 + offset) % 12) + 1]


def get_tam_phuong_tu_chinh(chart: dict[str, Any], cung_so: int) -> list[dict[str, Any]]:
    return (
        ([p] for p in [])
    )


def related_palaces(chart: dict[str, Any], target: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """Return actual palace objects in each positional relationship."""
    dong = [target]
    tam_hop = _offset_palace(chart, target, 4) + _offset_palace(chart, target, 8)
    xung = _offset_palace(chart, target, 6)
    giap = _offset_palace(chart, target, -1) + _offset_palace(chart, target, 1)
    tam_phuong = dong + tam_hop + xung

    luc_hop = []
    chi = _cung_chi(target)
    partner = BRANCH_LUC_HOP.get(chi)
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


def has_star(palace: dict[str, Any] | None, star_name: str, star_attr: str | None = None) -> bool:
    if not palace:
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
    count = 0
    for name in star_names:
        if any(has_star(h, name) for h in houses):
            count += 1
    return count


def _scope_matches(scope: list[dict[str, Any]], condition: dict[str, Any]) -> bool:
    if "stars_all" in condition:
        required = _normalize_names(condition["stars_all"])
        if not required.issubset(_scope_star_names(scope)):
            return False
    if "stars_any" in condition:
        requested = _normalize_names(condition["stars_any"])
        if not (requested & _scope_star_names(scope)):
            return False
    if "stars_none" in condition:
        forbidden = _normalize_names(condition["stars_none"])
        if forbidden & _scope_star_names(scope):
            return False
    if "not_both" in condition:
        pair = _normalize_names(condition["not_both"])
        if pair and pair.issubset(_scope_star_names(scope)):
            return False
    if "stars_required" in condition:
        required = _normalize_names(condition["stars_required"])
        min_count = int(condition.get("min_count", len(required)))
        if len(required & _scope_star_names(scope)) < min_count:
            return False
    return True


def _scope_star_names(houses: list[dict[str, Any]]) -> set[str]:
    result: set[str] = set()
    for house in houses:
        result |= _star_names(house)
    return result


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

    # Explicit relation blocks: each one is independently checked on its actual scope.
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
        if not isinstance(rule, dict):
            return False
        if not _scope_matches(scope, rule):
            return False

    # Explicit Giáp Cung pair predicate: one star on each side.
    if "giap_cung_pairs" in condition:
        relation_present = True
        left, right = relations["giap_cung"][0:1], relations["giap_cung"][1:2]
        if not left or not right:
            return False
        pairs = condition["giap_cung_pairs"]
        matched = False
        for pair in pairs if isinstance(pairs, list) else []:
            if not isinstance(pair, (list, tuple)) or len(pair) != 2:
                continue
            a, b = pair
            if (has_star(left[0], a) and has_star(right[0], b)) or (has_star(left[0], b) and has_star(right[0], a)):
                matched = True
                break
        if not matched:
            return False

    # Existing TuViMCP-style specialized scopes.
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
        scope = relations["nhi_hop"]
        if not scope or not _match_house_condition(scope[0], condition["luc_hop"]):
            return False

    # Direct target-house filters are always about the target itself.
    target_filters = {
        k: condition[k]
        for k in ("branches_in", "stars_all", "stars_any", "stars_none", "not_both")
        if k in condition
    }
    if target_filters and not _match_house_condition(target, target_filters):
        return False

    if "stem_contains" in condition:
        can_nam = str((chart.get("thien_ban") or {}).get("can_nam") or "")
        if str(condition["stem_contains"]) not in can_nam:
            return False

    # A relation-only condition is valid once the relation predicate(s) matched.
    return relation_present or bool(target_filters) or "stem_contains" in condition
